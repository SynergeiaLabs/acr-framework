# Failure / Load / DR Validation — 2026-04-08

Version under test: `v1.0.1`

## Scope

This validation pass exercised the control plane in `production` mode with:

- PostgreSQL, Redis, OPA, and the independent kill-switch service running locally
- Alembic migrations applied to an empty database
- the main gateway running locally with `STRICT_DEPENDENCY_STARTUP=true`
- authorization-only execution (`EXECUTE_ALLOWED_ACTIONS=false`) to isolate control-plane behavior

The validation covered:

- baseline runtime behavior
- hot-path load on `POST /acr/evaluate`
- dependency failure behavior for OPA, Redis, PostgreSQL, and the kill-switch service
- disaster recovery via `pg_dump` backup, full dependency teardown, restore, and post-restore verification

## Environment

- Date: `2026-04-08`
- Gateway mode: `production`
- Dependency topology: local Docker services for PostgreSQL, Redis, OPA, and kill-switch
- Gateway startup path used for runtime validation:
  - `docker compose up -d postgres redis opa acr-killswitch`
  - `alembic -c alembic.ini upgrade head`
  - `python3 -m uvicorn acr.main:app --host 127.0.0.1 --port 8000`

Note:
The full `docker compose` startup path that includes `acr-gateway` and `acr-migrate` was also attempted, but the compose-gated path did not become runnable because the OPA service never reached a healthy state in that startup flow on this machine. That is tracked as a deployment finding below.

## Baseline Validation

- Gateway health: `200 healthy`
- Gateway readiness: `200 ready` with `database=ok`, `redis=ok`, `opa=ok`
- Baseline allow path:
  - tool: `query_customer_db`
  - result: `200 allow`
  - observed server latency: `89ms`
- Baseline escalation path:
  - tool: `issue_refund`
  - amount: `$250`
  - result: `202 escalate`
  - approval created successfully in queue `finance-approvals`
  - approval request id: `apr-0b7c6d35-c136-40f9-af0d-217e74d3edf9`

## Load Validation

Workload:

- endpoint: `POST /acr/evaluate`
- action: `query_customer_db`
- total requests: `1000`
- concurrency: `25`

Results:

- success rate: `1000 / 1000` (`100%`)
- decision mix: `1000 allow`
- throughput: `102.54 requests/sec`

Client-observed latency:

- mean: `241.90ms`
- p50: `210.05ms`
- p95: `405.99ms`
- p99: `848.24ms`
- max: `926.63ms`

Gateway-reported latency:

- mean: `204.89ms`
- p50: `176.5ms`
- p95: `366.0ms`
- p99: `809.13ms`
- max: `861.0ms`

Assessment:

- The gateway stayed stable under sustained concurrent load and returned correct decisions.
- The current hot-path latency is functional but not yet at an enterprise-grade p99 target if the expectation is sub-100ms policy gating under pressure.

## Failure Validation

### OPA Outage

Observed behavior:

- readiness: `503 not_ready`
- checks: `database=ok`, `redis=ok`, `opa=error`
- evaluate result: `503 deny`
- error code: `POLICY_ENGINE_ERROR`
- reason: `OPA unreachable after 3 attempts`

Recovery:

- after OPA restart, readiness returned to `200 ready`
- next evaluation returned `200 allow`

Assessment:

- Pass. This is the expected fail-secure behavior.

### Redis Outage

Observed behavior:

- readiness: `503 not_ready`
- checks: `database=ok`, `redis=error`, `opa=ok`
- evaluate result: `503 deny`
- error code: `KILLSWITCH_ERROR`
- reason: `Kill switch state unavailable: Redis read failed`

Recovery:

- after Redis restart, readiness returned to `200 ready`
- next evaluation returned `200 allow`

Assessment:

- Pass. The hot path failed secure when Redis-backed runtime control state was unavailable.

### PostgreSQL Outage

Observed behavior:

- readiness: `503 not_ready`
- checks: `database=error`, `redis=ok`, `opa=ok`
- evaluate result: `500 deny`
- error code: `INTERNAL_ERROR`

Recovery:

- after PostgreSQL restart, readiness returned to `200 ready`
- next evaluation returned `200 allow`

Assessment:

- Partial pass. The system denied execution during database loss, which is safe, but it surfaced as a generic `500 INTERNAL_ERROR` instead of an explicit dependency failure code such as `503`.

### Kill-Switch Service Outage

Observed behavior:

- readiness: `200 ready`
- evaluate result: `200 allow`
- containment status call: `503`

Recovery:

- after kill-switch service restart, evaluate remained `200 allow`
- containment status returned `200`

Assessment:

- Mixed result:
  - runtime evaluation stayed available because hot-path kill checks read Redis directly
  - operator containment writes/reads through the independent service were unavailable
  - readiness did not report this dependency loss

This is an enterprise gap: the current readiness contract does not reflect independent kill-switch service availability.

## Disaster Recovery Validation

Backup artifact:

- method: `pg_dump --clean --if-exists --no-owner --no-privileges`
- artifact size: `2,351,336 bytes`

Recovery flow:

1. created baseline agent, telemetry, and one pending approval
2. took a PostgreSQL backup
3. tore down the dependency stack and removed volumes
4. brought PostgreSQL, Redis, OPA, and kill-switch back up
5. restored the SQL backup into a fresh database
6. verified that the running gateway returned to `ready`
7. verified persisted entities and a fresh evaluation

Post-restore verification:

- readiness: `200 ready`
- agent fetch: `200`
- approval fetch: `200`
- telemetry events returned: `50`
- post-restore evaluation: `200 allow`
- gateway readiness after restore completion: `0.10s`

Assessment:

- Pass. Data needed for runtime governance survived backup and restore, and the live gateway resumed normal decisioning after dependencies were restored.

## Deployment Finding

The full compose startup path is currently not reliable in this environment:

- `docker compose up -d --build postgres redis opa acr-killswitch acr-migrate acr-gateway`
- observed result: the gateway never became startable because compose blocked on an unhealthy OPA service

This appears to be a compose/dependency-gating problem rather than a runtime policy-engine problem, because:

- OPA answered `GET /health` successfully when started on its own
- runtime validation worked once dependencies were started and the gateway was launched outside that compose-gated path

## Summary

What passed:

- baseline allow and escalate paths
- load stability at `1000` requests / `25` concurrency
- fail-secure behavior for OPA outage
- fail-secure behavior for Redis outage
- recovery after OPA, Redis, and PostgreSQL restart
- PostgreSQL backup / restore with persisted governance data

What still blocks a stronger enterprise-ready claim:

- PostgreSQL outage returns a generic `500 INTERNAL_ERROR` instead of an explicit dependency failure contract
- readiness does not include kill-switch service availability
- the compose full-stack deployment path is not currently dependable
- load latency, especially p95/p99, is still higher than a hardened control-plane target would ideally be

## Recommended Next Actions

1. Add explicit database dependency failure handling so PostgreSQL loss returns a controlled `503` contract instead of `500 INTERNAL_ERROR`.
2. Extend `/acr/ready` to include the independent kill-switch service, not just Redis.
3. Fix the compose OPA health / dependency gating path so `acr-gateway` can be started through the documented full-stack deployment flow.
4. Repeat the load test after deployment-path fixes and capture a second run with higher concurrency and a published latency budget.
