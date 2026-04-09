# Shared Responsibility Matrix

The control plane provides a strong enforcement core, but enterprise readiness depends on clear operator responsibilities.

| Control Area | ACR Implementation Responsibility | Deployer / Operator Responsibility |
|---|---|---|
| Agent identity validation | Validate registered agents, lifecycle state, and runtime tokens | Establish who may register agents and how agent ownership is approved |
| Runtime policy enforcement | Evaluate policy, enforce allow/deny/escalate or modify, persist decision traces | Author policy, approve releases, and govern activation rights |
| Operator authentication | Provide API key, OIDC session, and RBAC surfaces | Integrate OIDC, manage break-glass keys, and review role assignments |
| Secret handling | Reject weak production secrets and provide generation templates | Store secrets in a real secret manager and rotate them on schedule |
| Kill-switch containment | Enforce Redis-backed kill checks and operator containment APIs | Protect access to containment roles and monitor containment events |
| Downstream authorization | Mint payload-bound execution tokens and brokered credentials | Ensure downstream systems verify those credentials and cannot be reached directly |
| Observability and evidence | Capture telemetry, export evidence bundles, and sign records | Define retention, immutability, access control, and long-term storage policy |
| Data persistence | Persist policy, approval, telemetry, and drift records | Operate backups, restore tests, partition lifecycle, and database hardening |
| Release integrity | Publish signed images, provenance attestations, and signed compliance package artifacts | Verify signatures, pin by digest, and block unverified promotions |
| Network isolation | Provide reference K8s manifests and deployment guidance | Enforce ingress, egress, and service-to-service restrictions in the target environment |
| Compliance narrative | Provide control mappings, threat model, and evidence checklist | Map ACR into the organization’s own control framework and evidence program |
| External assessment support | Provide a scoping package and technical review artifacts | Commission penetration testing, architecture review, and remediation tracking |

## Practical Reading

If a control depends on external identity, storage, networking, or change management, it is almost certainly shared.

Governance is strongest when:

- ACR owns decision enforcement and evidence generation
- the operator owns environment trust, identity, storage, and release promotion
