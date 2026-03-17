# STRIKE Threat Model for Autonomous AI Systems

The **STRIKE** framework defines a threat model for autonomous AI systems at runtime. It complements the ACR Framework: **STRIKE** identifies the threats; **ACR** provides the control architecture to mitigate them.

Use STRIKE for risk assessment, architecture review, and mapping controls to threats. Use ACR for implementation patterns and specifications.

---

# STRIKE Threat Categories

STRIKE identifies six classes of risk that increase as AI systems gain autonomy and access to enterprise systems and data.

---

## S — Scope Escalation

**Definition:** An AI system gains access to capabilities, tools, or data outside its approved operational scope—whether through misconfiguration, abuse, or gradual expansion.

### Attack Scenarios

| Scenario | Description | Likelihood | Impact |
|---------|-------------|------------|--------|
| **Tool creep** | Agent is granted broad tool access "for convenience"; it later uses a low-privilege tool to reach high-value data (e.g. read from a shared drive it was not intended to use). | Medium | High |
| **API scope abuse** | Agent has access to "customer API"; it discovers and calls internal admin or billing endpoints on the same host. | Medium | Critical |
| **Purpose drift** | Agent approved for "customer_support" begins performing "data_analysis" tasks because the boundary was not enforced at runtime. | Medium | High |

### Detection Techniques

- **Identity & purpose checks:** Every request validated against bound purpose and allowlist of tools/data.
- **Telemetry analysis:** Alert on first-use of a tool or data source not in baseline for that agent.
- **Periodic attestation:** Re-validate agent identity and scope; flag if scope has been changed without approval.

### ACR Controls (Detailed)

| Control | How It Mitigates |
|---------|------------------|
| [Identity & Purpose Binding](../pillars/01-identity-purpose-binding.md) | Cryptographically bound identity and purpose; tool and resource allowlists per purpose. |
| [Behavioral Policy Enforcement](../pillars/02-behavioral-policy-enforcement.md) | Runtime allowlist/denylist for tools and APIs; deny-by-default for unknown resources. |
| [Execution Observability](../pillars/04-execution-observability.md) | Every tool/resource access logged with agent_id and purpose; anomalies (new tools, new endpoints) detectable. |
| [Autonomy Drift Detection](../pillars/03-autonomy-drift-detection.md) | Baseline of "normal" tool and data access; alert when pattern expands beyond baseline. |

### References

- Pillar 1: Control objectives for scope and capability authorization
- Pillar 2: Tool allowlists and action authorization

---

## T — Tool Misuse

**Definition:** The agent uses approved tools in unintended or harmful ways—correct tool, wrong action, wrong context, or wrong frequency.

### Attack Scenarios

| Scenario | Description | Likelihood | Impact |
|---------|-------------|------------|--------|
| **Unintended action** | Agent is allowed to "send_email"; it sends bulk marketing or sensitive content to the wrong recipients. | High | High |
| **Privilege chaining** | Agent uses read-only DB access plus email to exfiltrate data by encoding it in outbound messages. | Medium | Critical |
| **Financial misuse** | Agent with "create_refund" capability issues excessive or fraudulent refunds. | Medium | Critical |

### Detection Techniques

- **Output and action policy:** Validate parameters and outcomes (e.g. refund amount, recipient list) before execution.
- **Rate and volume:** Detect abnormal frequency or volume of tool calls.
- **Human-in-the-loop:** Gate high-impact actions (refunds, bulk operations) on approval.

### ACR Controls (Detailed)

| Control | How It Mitigates |
|---------|------------------|
| [Behavioral Policy Enforcement](../pillars/02-behavioral-policy-enforcement.md) | Input/output validation; parameter constraints; action authorization with context. |
| [Human Authority](../pillars/06-human-authority.md) | Approval workflows for high-risk actions; override and revocation. |
| [Execution Observability](../pillars/04-execution-observability.md) | Full logging of tool invocations and parameters for audit and anomaly detection. |
| [Self-Healing & Containment](../pillars/05-self-healing-containment.md) | Automatic throttle or restriction when misuse patterns are detected. |

### References

- Pillar 2: Action authorization, output filtering
- Pillar 6: Approval tiers and escalation

---

## R — Role Drift

**Definition:** The AI system’s behavior gradually diverges from its intended role—taking on tasks, making decisions, or interacting with systems outside its designed authority.

### Attack Scenarios

| Scenario | Description | Likelihood | Impact |
|---------|-------------|------------|--------|
| **Task expansion** | Support agent starts answering legal or compliance questions because users ask; no guardrail limits "type of question." | High | Medium |
| **Authority creep** | Agent begins making commitments (e.g. "we will ship by Friday") that only humans are authorized to make. | Medium | High |
| **Domain crossover** | Data-analysis agent starts modifying data or triggering workflows (write vs read). | Medium | High |

### Detection Techniques

- **Behavioral baselines:** Establish normal distributions for actions, tools, and topics; alert on deviation.
- **Semantic / intent signals:** Monitor prompts and outputs for topics or intent outside role (e.g. legal, financial commitments).
- **Periodic role review:** Compare recent behavior to stated purpose and approved use cases.

### ACR Controls (Detailed)

| Control | How It Mitigates |
|---------|------------------|
| [Autonomy Drift Detection](../pillars/03-autonomy-drift-detection.md) | Statistical and behavioral baselines; drift scores; alerts when behavior leaves expected envelope. |
| [Identity & Purpose Binding](../pillars/01-identity-purpose-binding.md) | Purpose as hard boundary; re-attestation and scope review. |
| [Behavioral Policy Enforcement](../pillars/02-behavioral-policy-enforcement.md) | Policies that encode "allowed task types" or domains; block out-of-scope actions. |
| [Human Authority](../pillars/06-human-authority.md) | Escalation when drift is detected; human confirmation before expanding scope. |

### References

- Pillar 3: Baselines, metrics, and evaluation criteria
- Pillar 1: Purpose and operational scope

---

## I — Information Leakage

**Definition:** Sensitive data is exposed through AI outputs, logs, or system interactions—whether from training data, context injection, or inappropriate inclusion in responses.

### Attack Scenarios

| Scenario | Description | Likelihood | Impact |
|---------|-------------|------------|--------|
| **PII in output** | Agent includes customer SSN, email, or health data in a response or log. | High | High |
| **Context leakage** | Long context window includes internal docs; agent echoes confidential content in reply. | High | Critical |
| **Inference attacks** | Repeated queries allow inferring sensitive attributes from model behavior. | Low | Medium |

### Detection Techniques

- **Output filtering and redaction:** PII patterns and confidential markers stripped or redacted before emission.
- **Data classification:** Tag inputs and outputs; block or redact when classification exceeds allowed level.
- **Audit and monitoring:** Log all outputs and access; alert on sensitive patterns or unusual data access.

### ACR Controls (Detailed)

| Control | How It Mitigates |
|---------|------------------|
| [Behavioral Policy Enforcement](../pillars/02-behavioral-policy-enforcement.md) | Output filters, PII redaction, data-handling rules, and content policies. |
| [Execution Observability](../pillars/04-execution-observability.md) | Full audit trail; redacted/sanitized logging; evidence for compliance. |
| [Identity & Purpose Binding](../pillars/01-identity-purpose-binding.md) | Data access limited by purpose and allowlist (e.g. only certain DBs or columns). |

### References

- Pillar 2: Output filtering and data handling
- Pillar 4: Audit and retention

---

## K — Kill Chain Expansion

**Definition:** The AI system extends the enterprise attack surface—enabling lateral movement, chaining of actions across systems, or creating new pathways for adversaries.

### Attack Scenarios

| Scenario | Description | Likelihood | Impact |
|---------|-------------|------------|--------|
| **Lateral movement** | Compromised or manipulated agent uses its tools to pivot to other systems (e.g. cloud APIs, internal services). | Medium | Critical |
| **Action chaining** | A sequence of individually allowed actions (read A, transform, write B) achieves an unintended outcome (exfiltration, privilege escalation). | Medium | Critical |
| **Supply chain** | Agent pulls or executes external content (plugins, code); that content is malicious. | Medium | High |

### Detection Techniques

- **Graph and sequence analysis:** Model allowed flows (tool A → tool B); alert on new or anomalous sequences.
- **Network and egress control:** Restrict agent-initiated traffic to approved endpoints; block unexpected connections.
- **Containment and isolation:** On anomaly or alert, restrict tools or isolate the agent to limit blast radius.

### ACR Controls (Detailed)

| Control | How It Mitigates |
|---------|------------------|
| [Self-Healing & Containment](../pillars/05-self-healing-containment.md) | Circuit breakers, isolation, tool restriction, kill switch; limit propagation. |
| [Behavioral Policy Enforcement](../pillars/02-behavioral-policy-enforcement.md) | Sequence or graph-based policies; deny dangerous combinations; restrict egress. |
| [Autonomy Drift Detection](../pillars/03-autonomy-drift-detection.md) | Detect anomalous tool sequences or access patterns that suggest chaining. |
| [Execution Observability](../pillars/04-execution-observability.md) | Trace full action chains for investigation and tuning of policies. |

### References

- Pillar 5: Containment tiers and kill switch
- Pillar 2: Action and tool policies

---

## E — Execution Manipulation

**Definition:** Adversaries or malicious inputs influence AI behavior—prompt injection, jailbreaking, or manipulation of context and tools to change outcomes.

### Attack Scenarios

| Scenario | Description | Likelihood | Impact |
|---------|-------------|------------|--------|
| **Prompt injection** | User or system input contains instructions that override intended behavior ("ignore previous instructions and..."). | High | High |
| **Jailbreaking** | Inputs designed to bypass safety or policy (e.g. role-play, encoding) so the agent performs restricted actions. | Medium | High |
| **Context poisoning** | Attacker controls part of context (e.g. retrieved docs); model is steered to leak data or take wrong action. | Medium | Critical |

### Detection Techniques

- **Input validation and sanitization:** Detect and block known injection patterns; limit influence of untrusted input.
- **Behavioral and output monitoring:** Compare output to intent; flag responses that contradict policy or role.
- **Human review:** High-stakes or anomalous decisions routed for human review before execution.

### ACR Controls (Detailed)

| Control | How It Mitigates |
|---------|------------------|
| [Execution Observability](../pillars/04-execution-observability.md) | Log inputs and outputs; reconstruct decisions; support detection and incident response. |
| [Autonomy Drift Detection](../pillars/03-autonomy-drift-detection.md) | Anomalous input or output patterns; deviation from expected behavior. |
| [Human Authority](../pillars/06-human-authority.md) | Override, kill switch, and approval for sensitive actions. |
| [Behavioral Policy Enforcement](../pillars/02-behavioral-policy-enforcement.md) | Input checks and output filters that reduce impact of successful manipulation. |

### References

- Pillar 4: Correlation and audit
- Pillar 6: Override and escalation

---

# STRIKE Summary Matrix

| Threat | Primary ACR Pillars | Typical Severity |
|--------|---------------------|------------------|
| **S** Scope Escalation | 1, 2, 4, 3 | High |
| **T** Tool Misuse | 2, 6, 4, 5 | High–Critical |
| **R** Role Drift | 3, 1, 2, 6 | Medium–High |
| **I** Information Leakage | 2, 4, 1 | High–Critical |
| **K** Kill Chain Expansion | 5, 2, 3, 4 | Critical |
| **E** Execution Manipulation | 4, 3, 6, 2 | High–Critical |

---

# Using STRIKE in Risk Assessment

1. **Map assets and agents:** List autonomous agents, their purposes, and the systems/data they touch.
2. **Apply STRIKE:** For each agent, consider each of S–T–R–I–K–E; note likelihood and impact.
3. **Map to ACR:** For each relevant threat, identify which ACR pillars you will implement and how (see [Implementation Guide](../guides/acr-implementation-guide.md)).
4. **Prioritize:** Address high-likelihood and high-impact threats first; use the [maturity model](../../ADOPTION.md#acr-maturity-levels) to stage controls.
5. **Review periodically:** Re-run as new agents, tools, or threats emerge.

---

**ACR Framework v1.0** | [Home](../../README.md) | [Pillars](../pillars/README.md) | [Glossary](./acr-glossary.md)
