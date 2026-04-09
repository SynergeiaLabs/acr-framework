# External Assessment Scope

This document is a scoping package for independent review. It is not a substitute for an actual assessment report.

## Recommended Assessment Types

- application penetration test of operator and runtime APIs
- authenticated architecture review of runtime control boundaries
- cloud and Kubernetes configuration review for the target deployment
- release integrity and provenance verification review

## In Scope

- `POST /acr/evaluate` decision path
- operator authentication and authorization paths
- policy draft, release, and activation APIs
- approval and containment APIs
- telemetry and evidence export paths
- downstream authorization token and brokered credential patterns
- release workflow provenance and signature verification

## Explicit Questions for Assessors

- Can an agent bypass the gateway and still reach protected systems?
- Can operator roles be escalated through session or API-key misuse?
- Can policy or evidence records be tampered with undetected?
- What happens if Redis, OPA, PostgreSQL, or the kill-switch service are attacked or degraded?
- Do release artifacts provide enough provenance to support admission or promotion policies?

## Deployment Preconditions

The following should be available to the assessor:

- deployment diagram and trust boundaries
- sample operator roles
- policy bundle source and active release id
- staging environment with representative downstream integrations
- digest-pinned deployed images
- recent validation report and release verification output

## Expected Deliverables

- executive summary
- findings with severity and evidence
- exploit or reproduction notes where appropriate
- architectural observations and compensating controls
- retest notes after remediation

## Current Known Focus Areas

Based on the latest validation pass, assessors should pay special attention to:

- generic `500` behavior during PostgreSQL outage
- readiness blind spot for kill-switch service loss
- full compose deployment startup behavior around OPA health gating
- hot-path latency under higher concurrency and more realistic policy/data load
