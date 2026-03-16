# ACR Framework Glossary

This glossary defines key terminology used within the ACR Framework and related governance models.

---

# ACR Control Plane

The runtime governance layer responsible for mediating interactions between autonomous AI systems and enterprise infrastructure.

The control plane enforces governance policies, monitors system behavior, and enables intervention when necessary.

---

# Autonomous AI System

An AI system capable of performing actions, executing workflows, or interacting with enterprise resources without direct human instruction at each step.

Examples include:

- AI agents
- autonomous workflow systems
- enterprise copilots
- multi-agent orchestration systems

---

# Behavioral Policy Enforcement

The process of translating organizational AI governance policies into machine-enforceable runtime controls that restrict AI system actions.

---

# Execution Observability

The capability to monitor and record AI system inputs, actions, and outputs during runtime.

Observability enables auditing, investigation, and governance oversight.

---

# Identity & Purpose Binding

A governance mechanism that assigns an AI system a defined identity and operational purpose.

This prevents AI systems from operating outside their authorized scope.

---

# Autonomy Drift

The gradual divergence of an AI system's behavior from its intended operational boundaries.

Drift may occur as systems interact with new inputs, tools, or workflows.

---

# Drift Detection

A monitoring capability that identifies abnormal AI system behavior or deviations from expected execution patterns.

---

# Tool Access Gateway

A governance mechanism that mediates AI interactions with enterprise tools, APIs, and services.

This ensures that AI systems only access authorized resources.

---

# Containment Controls

Automated mechanisms used to limit the impact of abnormal or unsafe AI behavior.

Examples include:

- capability restriction
- workflow interruption
- system isolation

---

# Human Authority

The principle that human operators retain ultimate decision authority over autonomous AI systems.

Human oversight mechanisms allow operators to intervene, override, or terminate AI system execution.

---

# STRIKE Framework

A threat model describing security risks associated with autonomous AI systems.

STRIKE identifies six threat categories:

- Scope Escalation
- Tool Misuse
- Role Drift
- Information Leakage
- Kill Chain Expansion
- Execution Manipulation

---

# Runtime Governance

Governance mechanisms that remain active while AI systems operate in production environments.

Runtime governance enables organizations to enforce policies, monitor behavior, and intervene in system activity.

---

# Autonomous Control & Resilience (ACR)

A governance framework designed to manage the behavior of autonomous AI systems operating in enterprise environments.

ACR introduces runtime control architecture that enforces governance policies while AI systems are actively executing.
