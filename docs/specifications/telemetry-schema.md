# ACR Telemetry Schema Specification

**Version:** 1.0  
**Status:** Stable  
**Last Updated:** March 2026

This document defines the canonical schema for telemetry events emitted by ACR-aligned control planes. It supports [Pillar 4: Execution Observability](../pillars/04-execution-observability.md), audit trails, drift detection input, and compliance evidence generation.

## Purpose and Scope

- **Purpose:** Provide a consistent, machine-readable structure for all runtime events related to AI system actions, policy decisions, drift alerts, containment actions, and human interventions.
- **Scope:** Events emitted by the ACR control plane (or equivalent governance layer) during request processing. Out of scope: model training telemetry, pre-deployment validation logs, and non-ACR application logs.
- **Consumers:** Observability pipelines, audit stores, drift detection services, compliance reporting, and incident response tooling.

## Event Types

Every event MUST include an `event_type` from the following set:

| event_type | Description |
|------------|-------------|
| `ai_inference` | Standard model invocation (request → policy checks → model/tools → response) |
| `policy_decision` | Policy evaluation without inference (e.g. pre-flight check, re-validation) |
| `drift_alert` | Anomaly or drift detection event (behavioral baseline deviation) |
| `containment_action` | Automated or manual containment response (throttle, restrict, isolate, kill) |
| `human_intervention` | Manual override, approval, or break-glass action |

## Schema Overview

Events are JSON objects. Field names use `snake_case`. Timestamps use ISO 8601 with timezone (e.g. `2026-03-16T14:22:01Z`). All UUIDs are RFC 4122 version 4 where applicable.

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `acr_version` | string | Yes | ACR schema version (e.g. `"1.0"`). Semantic versioning for backward compatibility. |
| `event_id` | string | Yes | Unique event identifier (UUID v4 recommended). |
| `event_type` | string | Yes | One of: `ai_inference`, `policy_decision`, `drift_alert`, `containment_action`, `human_intervention`. |
| `timestamp` | string | Yes | ISO 8601 timestamp with timezone. |
| `correlation_id` | string | No | Links this event to a request or trace; should be consistent across spans of the same action. |
| `agent` | object | Yes* | Identity and purpose binding. *Optional only for non-agent events (e.g. system health). |
| `request` | object | No | Request context; required for `ai_inference` and often for `policy_decision`. |
| `execution` | object | No | Execution details (duration, tool calls); typical for `ai_inference`. |
| `policies` | array | No | Policy evaluation results; present when policy checks were performed. |
| `output` | object | No | Output metadata (tokens, cost); for inference events. |
| `metadata` | object | No | Environment, drift score, and other extensible attributes. |

### Object: `agent`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_id` | string | Yes | Stable identifier for the AI system or agent instance. |
| `purpose` | string | Yes | Operational purpose or scope (e.g. `customer_support`, `data_analysis`). |
| `model` | object | No | Model identifier and optional version/vendor. |
| `risk_tier` | string | No | Risk classification if defined (e.g. `low`, `medium`, `high`). |

### Object: `request`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | string | No | Client or gateway request ID for correlation. |
| `input` | object | No | Sanitized or summarized input (avoid logging full PII); size limits apply. |

### Object: `execution`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `duration_ms` | number | No | End-to-end duration in milliseconds. |
| `tool_calls` | array | No | List of tool invocations (name, params summary, result summary). |
| `error` | string | No | Error message or code if the execution failed. |

### Object: `policies[]`

Each element represents one policy evaluation:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `policy_id` | string | Yes | Policy or rule identifier. |
| `decision` | string | Yes | `allow` or `deny`. |
| `rule_id` | string | No | Specific rule that fired. |
| `transformations` | number | No | Count of transformations applied (e.g. redactions). |

### Object: `output`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tokens` | object | No | Input/output token counts if available. |
| `cost` | object | No | Cost or usage metadata if available. |
| `redacted` | boolean | No | Whether output was redacted or truncated for logging. |

### Object: `metadata`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `environment` | string | No | Deployment or environment label (e.g. `production`, `staging`). |
| `drift_score` | number | No | Current or latest drift score in [0.0, 1.0] when applicable. |
| `containment_tier` | string | No | For containment events: e.g. `throttle`, `restrict`, `isolate`, `kill`. |
| `approver_id` | string | No | For human_intervention: identifier of the approver (opaque or hashed). |

Additional custom fields MAY be added under `metadata` or as top-level extensions; implementers SHOULD namespace custom keys (e.g. `vendor_*`) to avoid clashes with future ACR schema versions.

## Validation Rules

1. **Schema version:** `acr_version` MUST be present and parseable. Consumers MAY reject unknown major versions.
2. **Event size:** Events SHOULD stay under 10 KB to avoid pipeline and storage bloat. Redact or truncate large payloads (e.g. `request.input`, tool call payloads) and document redaction policy.
3. **Timestamps:** `timestamp` MUST be ISO 8601 with timezone. Prefer UTC.
4. **Async emission:** Telemetry MUST NOT block the action pipeline; emit asynchronously where possible.
5. **Integrity:** For audit logs, use append-only storage and optional hash-chaining as described in [Pillar 4](../pillars/04-execution-observability.md).

## Versioning

- **Major** (e.g. 1.0 → 2.0): Breaking changes (removed or renamed required fields, changed types).
- **Minor** (e.g. 1.0 → 1.1): New optional fields or event types; backward compatible.
- **Patch:** Clarifications and non-structural edits only.

Implementations SHOULD include `acr_version` in every event so consumers can route or transform by version.

## Examples

### Minimal `ai_inference` event

```json
{
  "acr_version": "1.0",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "ai_inference",
  "timestamp": "2026-03-16T14:22:01Z",
  "agent": {
    "agent_id": "customer-support-01",
    "purpose": "customer_support"
  },
  "request": {
    "request_id": "req-abc-123"
  },
  "execution": {
    "duration_ms": 385
  },
  "policies": [
    { "policy_id": "pii_redaction", "decision": "allow" }
  ],
  "metadata": {
    "environment": "production",
    "drift_score": 0.12
  }
}
```

### `containment_action` event

```json
{
  "acr_version": "1.0",
  "event_id": "660e8400-e29b-41d4-a716-446655440001",
  "event_type": "containment_action",
  "timestamp": "2026-03-16T14:25:00Z",
  "correlation_id": "trace-xyz-789",
  "agent": {
    "agent_id": "customer-support-01",
    "purpose": "customer_support"
  },
  "metadata": {
    "environment": "production",
    "drift_score": 0.72,
    "containment_tier": "restrict"
  }
}
```

## References

- [Pillar 4: Execution Observability](../pillars/04-execution-observability.md) — Architectural patterns and integration points
- [Implementation Guide: Telemetry & Observability](../guides/acr-implementation-guide.md#telemetry--observability-setup) — OpenTelemetry and dashboard guidance
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/) — For trace and attribute conventions

---

**ACR Framework v1.0** | [Home](../../README.md) | [Pillars](../pillars/README.md) | [Implementation Guide](../guides/acr-implementation-guide.md)
