# Threat Model

This threat model is focused on the runtime control plane implementation, not only the abstract standard.

## Protected Assets

- agent manifests and registered boundaries
- agent JWTs
- operator API keys and signed sessions
- policy bundles and active release aliases
- approval records and override decisions
- telemetry events and evidence bundles
- execution authorization tokens and brokered downstream credentials
- Postgres and Redis runtime state

## Trust Boundaries

1. Agent runtime to gateway
2. Operator to gateway and console
3. Gateway to OPA
4. Gateway to PostgreSQL and Redis
5. Gateway to kill-switch service
6. Gateway to protected executors and downstream enterprise systems
7. Release pipeline to container registry and release assets

## Primary Threats

### Direct Tool Bypass

Scenario:
An agent or compromised service calls a protected downstream tool directly without passing through the control plane.

Relevant controls:

- gateway-issued execution authorization tokens
- payload-bound execution verification
- brokered downstream credentials
- network segmentation expectations in deployment guidance

Residual risk:
If downstream services are reachable directly and do not verify gateway-issued credentials, bypass remains possible.

### Stolen Agent Identity

Scenario:
An attacker obtains an agent JWT and replays or abuses it.

Relevant controls:

- short-lived JWTs
- agent registration and lifecycle validation
- kill-switch containment
- server-side rate and spend controls

Residual risk:
Token theft remains impactful until expiration or containment unless deployers add stronger issuer controls and network restrictions.

### Operator Credential Misuse

Scenario:
An attacker obtains operator API keys or session material and attempts approvals, policy changes, or containment actions.

Relevant controls:

- operator RBAC
- OIDC support
- signed operator sessions
- operator key rotation and audit trails

Residual risk:
Bootstrap API keys remain powerful and should be limited to break-glass and automation scenarios.

### Policy Tampering

Scenario:
An attacker or unauthorized insider changes policy content or activation state.

Relevant controls:

- versioned drafts and releases
- activation and rollback history
- operator-authenticated policy management
- release provenance and container signing for shipped artifacts

Residual risk:
Bundle hosting and operator access control remain deployment responsibilities.

### Evidence Tampering

Scenario:
An attacker attempts to alter telemetry or exported evidence after the fact.

Relevant controls:

- chained telemetry integrity metadata
- bundle signatures
- exported checksums

Residual risk:
Retention immutability and long-term custody controls still depend on the operator’s storage and retention model.

### Dependency Failure as an Availability Attack

Scenario:
OPA, Redis, PostgreSQL, or the kill-switch service become unavailable due to outage or hostile interference.

Relevant controls:

- fail-secure policy behavior
- Redis-backed hot-path kill checks
- readiness endpoints
- documented failure/load/DR validation

Residual risk:
The current validation showed two open items:

- PostgreSQL loss currently surfaces as generic `500 INTERNAL_ERROR` on evaluate
- readiness does not currently include kill-switch service availability

### Supply-Chain Compromise

Scenario:
Release artifacts are modified, replaced, or built from untrusted workflow state.

Relevant controls:

- GitHub Actions release workflow identity
- container image signing
- build provenance attestations
- signed compliance-package blob

Residual risk:
Deployers still need to verify signatures and attestations before promotion.

## Assumptions

- downstream systems enforce gateway-issued credentials or are otherwise network-isolated
- production deployments replace development secrets and use a real secret-management flow
- operator roles are assigned through an approved identity process
- release consumers verify signatures and provenance rather than trusting tags alone

## Recommended Review Focus

For enterprise review, pay special attention to:

- downstream bypass resistance
- bootstrap key governance
- policy release authorization
- retention and evidence custody
- dependency failure semantics under production load
