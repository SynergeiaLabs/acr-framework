# ACR Framework Mapping to NIST AI Risk Management Framework

The ACR Framework complements the NIST AI Risk Management Framework (AI RMF) by providing runtime governance mechanisms that enforce AI governance policies during system operation.

While the NIST AI RMF focuses on organizational governance processes and risk management structures, ACR focuses on **runtime control architecture for autonomous AI systems**.

Together, these approaches provide both governance policy and operational enforcement.

---

# NIST AI RMF Functions

The NIST AI Risk Management Framework defines four core functions:

- Govern
- Map
- Measure
- Manage

The ACR Framework introduces technical control layers that support these functions during runtime.

---

# Mapping of ACR Control Layers to NIST AI RMF

| ACR Control Layer | NIST AI RMF Function | Governance Capability |
|---|---|---|
| Identity & Purpose Binding | Govern | Establishes defined operational roles and system accountability |
| Behavioral Policy Enforcement | Govern / Manage | Enforces governance policies through runtime system constraints |
| Autonomy Drift Detection | Measure | Detects deviations from expected system behavior |
| Execution Observability | Measure | Provides runtime visibility into AI decision processes |
| Self-Healing & Containment | Manage | Enables defensive responses to abnormal or unsafe behavior |
| Human Authority | Govern | Preserves human oversight and decision authority |

---

# Subcategory-Level Mapping

The following table maps NIST AI RMF 1.0 subcategories to ACR controls that support them at runtime. Authoritative subcategory text and IDs are in [NIST AI RMF 1.0](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf).

## Govern

| NIST AI RMF Subcategory | ACR Control(s) | How ACR Supports It |
|-------------------------|----------------|---------------------|
| Governance structures (roles, accountability) | Identity & Purpose Binding, Human Authority | Bound identity and purpose; human override and approval workflows |
| Policies and processes for AI risk | Behavioral Policy Enforcement | Runtime policy enforcement (input/output/action rules) |
| Organizational culture and communication | Human Authority, Execution Observability | Escalation paths, audit trails for accountability |

## Map

| NIST AI RMF Subcategory | ACR Control(s) | How ACR Supports It |
|-------------------------|----------------|---------------------|
| Context (stakeholders, use case) | Identity & Purpose Binding | Purpose-scoped agents; operational context in telemetry |
| Categorize (risks, benefits) | Behavioral Policy Enforcement, Human Authority | Risk-tiered policies; high-risk actions gated by human approval |
| Risks (identification) | STRIKE threat model, Drift Detection | Threat categories; drift signals as risk indicators |

## Measure

| NIST AI RMF Subcategory | ACR Control(s) | How ACR Supports It |
|-------------------------|----------------|---------------------|
| Methods (metrics, testing) | Execution Observability, Autonomy Drift Detection | Telemetry schema; drift scores and baselines as measurable outcomes |
| Data (quality, relevance) | Behavioral Policy Enforcement, Execution Observability | Input validation; logged inputs/outputs for analysis |
| Testing and evaluation | Execution Observability, Self-Healing & Containment | Audit trail for post-incident review; containment as testable response |
| Impact (positive/negative) | Execution Observability, Human Authority | Decision lineage; human intervention events as impact controls |

## Manage

| NIST AI RMF Subcategory | ACR Control(s) | How ACR Supports It |
|-------------------------|----------------|---------------------|
| Risks and responses | Self-Healing & Containment, Behavioral Policy Enforcement | Automated containment tiers; policy denials as response |
| Allocation (resources, responsibility) | Identity & Purpose Binding, Human Authority | Scoped capabilities; approver attribution in telemetry |
| Oversight and review | Human Authority, Execution Observability | Approval workflows; full observability for oversight |

---

# Complementary Governance Roles

The NIST AI RMF provides guidance for:

- governance structures
- risk assessment processes
- organizational AI oversight

The ACR Framework provides mechanisms for:

- runtime AI governance enforcement
- monitoring autonomous AI system behavior
- containing abnormal AI activity
- maintaining human authority over automated systems

Together, these frameworks help organizations move from **AI governance policy to operational governance control**.

---

# Operational Alignment

Organizations implementing NIST AI RMF governance processes may adopt ACR as the runtime control architecture supporting those policies.

Example alignment:

| Governance Layer | Responsibility |
|---|---|
| NIST AI RMF | Policy, risk management, and governance processes |
| ACR Framework | Runtime enforcement and operational control |

---

# References

- [NIST AI RMF 1.0](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf) — Full framework (Govern, Map, Measure, Manage)
- [NIST AI RMF Playbook](https://airc.nist.gov/airmf-resources/playbook/) — Suggested actions by subcategory
- [ACR STRIKE Threat Model](../security/acr-strike-threat-model.md) — Runtime threat categories aligned to ACR controls

---

# Summary

The ACR Framework extends the NIST AI Risk Management Framework by introducing a runtime governance architecture capable of controlling autonomous AI systems in production environments.

By combining governance policy frameworks such as NIST AI RMF with runtime control architectures such as ACR, organizations can achieve both **governance definition and governance enforcement** for AI systems.
