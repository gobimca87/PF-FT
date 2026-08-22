---
id: ADR-D8-08
title: Platform extensibility — how a new agent/workflow is added
domain: 8 Business Value
ws_ref: [WS-37]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [Principal Architect, Backend Lead]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-03, ADR-D2-05, ADR-D1-10, ADR-D1-11, ADR-D6-15]
source_docs:
  - "MD files/2 Agent Runtime/7 PF-FT-AI-AGENTIC-ORCHESTRATION.md"
  - "MD files/5 QualityGovernance/20.PF-FT-AI-GOVERNANCE.md §45, §46, §49"
build_phases: [23]
impacted_paths:
  - src/pf_ft_ai/agents/
classification: Internal
review_due: 2027-08-22
---

# ADR-D8-08 — Platform extensibility — how a new agent/workflow is added

## 1. Summary

PFF AI will make adding a new workflow/agent a **declarative, contract-driven, governed
extension** — implement the agent contract (ADR-D3-03), register it with the supervisor
(ADR-D2-05), declare its tools/ERC needs/prompts as versioned artefacts, pass evaluation
(ADR-D7-13) and change governance (ADR-D6-15) — with **no changes to core orchestration
required** (doc 7 orchestration; doc 20 §45–§46, §49). Extensibility is by declaration +
registration, not core edits.

## 2. Context and Problem Statement

Doc 7 defines the agentic orchestration; doc 20 §45–§46 agent governance/capability
boundaries, §49 workflow change. The platform starts with AffiliationAgent (ADR-D1-11) but a
catalogue of workflows is planned (ADR-D1-10). If adding an agent required core changes, growth
would be slow and risky. This ADR fixes the extension model.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Add agent via contract + registration, no core edit | ADR-D3-03, D2-05 |
| DR-F-02 | Declarative tools/ERC/prompts as artefacts | doc 20 §45 |
| DR-F-03 | Gated by eval + governance | ADR-D7-13, D6-15 |
| DR-C-01 | Capability boundaries respected | doc 20 §46 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Contract is expressive enough for new workflows | Extend contract | Design review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | No core changes to add an agent | 30 | Safe growth | Core diff on add |
| EC-02 | Declarativeness/contract-driven | 22 | Consistency | Declaration model |
| EC-03 | Governance + eval gating | 20 | Quality/safety | Gates applied |
| EC-04 | Speed to add a workflow | 16 | Growth velocity | Lead time |
| EC-05 | Boundary safety | 12 | No scope creep | Capability limits |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Contract + registration + declarative artefacts, no core edits, gated

**Description.** A new agent implements the agent contract (ADR-D3-03), declares tools/ERC
requirements/prompts as versioned artefacts, and registers with the supervisor (ADR-D2-05);
the core (harness, ERC, guardrails, graph engine) is unchanged; eval (ADR-D7-13) + governance
(ADR-D6-15) gate it; capability boundaries enforced (doc 20 §46).
**Strengths.** Safe, consistent, governed, fast.
**Weaknesses.** Contract must be expressive.
**Cost / effort.** Low per agent (after core exists).

### 5.2 Option B — Core edits per new agent

**Description.** Modify orchestration for each agent.
**Strengths.** Max flexibility per agent.
**Weaknesses.** Slow, risky, regression-prone; doesn't scale.
**Cost / effort.** High per agent.

### 5.3 Option C — Fully config-driven agents (no code, pure config/DSL)

**Description.** Define agents entirely in config/DSL.
**Strengths.** Fastest add; non-devs could author.
**Weaknesses.** Complex workflows exceed a DSL; a powerful DSL becomes a language to
maintain; harder to test.
**Cost / effort.** High DSL build; ceiling.

### 5.4 Option D — Plugin/microservice per agent (separate deployable)

**Description.** Each agent a separate service.
**Strengths.** Isolation.
**Weaknesses.** Violates single-runtime principle (ADR-D2-02); ops sprawl.
**Cost / effort.** High ops.

### 5.5 Option E — Contract + registration + declarative artefacts + scaffolding generator + capability boundaries

**Description.** Option A with a scaffolding generator (creates the agent skeleton, contract
stub, prompt/tool declarations, tests) to standardise and speed new agents.
**Strengths.** A + faster, more consistent onboarding.
**Weaknesses.** Maintain the generator.
**Cost / effort.** Low-medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Ungoverned agent addition | doc 20 §45–§46 |
| One microservice per agent | ADR-D2-02 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 7 and doc 20 §45–§49.

| Criterion | Weight | A: Contract+register | B: Core edits | C: Config-DSL | D: Microservice/agent | E: A+scaffolding |
|---|---|---|---|---|---|---|
| EC-01 No core edits | 30 | 5 | 1 | 5 | 4 | 5 |
| EC-02 Declarative | 22 | 5 | 2 | 5 | 3 | 5 |
| EC-03 Governance/eval | 20 | 5 | 4 | 3 | 4 | 5 |
| EC-04 Speed | 16 | 4 | 1 | 5 | 2 | 5 |
| EC-05 Boundary safety | 12 | 5 | 3 | 3 | 4 | 5 |
| **Weighted total** | **100** | **480** | **220** | **436** | **340** | **500** |

Totals (×20): **E = 500**, **A = 480**, **C = 436**, **B = 220**, **D = 220... (340)**.

_(D = 340.)_ **Sensitivity.** E (A + scaffolding generator) wins by speeding consistent
onboarding without loosening governance. Config-DSL (C) is fast but hits a complexity ceiling;
core-edits (B) and microservice-per-agent (D) are rejected (slow/risky; violates single
runtime).

## 7. Decision

**PFF AI will add new workflows/agents by implementing the agent contract, declaring tools/
ERC needs/prompts as versioned artefacts, and registering with the supervisor — with no core
orchestration changes, gated by evaluation and change governance, within capability
boundaries, and aided by a scaffolding generator (Option E).** Core-edits-per-agent (B),
pure-config-DSL (C) and microservice-per-agent (D) are rejected.

## 8. Architecture Detail

- A new agent: implements the contract (ADR-D3-03) in `src/pf_ft_ai/agents/<name>/`; declares
  its intents (ADR-D3-06), tools (allowlisted, ADR-D6-10), ERC requirements (ADR-D4-04),
  prompts (ADR-D3-11); registers with the supervisor (ADR-D2-05); reuses harness/guardrails/
  ERC/persona unchanged.
- A scaffolding generator produces the skeleton + declarations + test stubs; eval (ADR-D7-13)
  + governance (ADR-D6-15) gate go-live; capability boundaries (doc 20 §46) enforced. Fits the
  workflow catalogue/phasing (ADR-D1-10) — one agent (AffiliationAgent) first (ADR-D1-11).

## 9. Consequences

### 9.1 Positive
- Safe, fast, consistent, governed workflow growth with no core churn.
### 9.2 Negative
- Contract expressiveness + generator upkeep.
### 9.3 Neutral
- Realises the workflow catalogue (D1-10).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Per-agent core flexibility | Safe, scalable extension | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | New agents inherit the Golden-Rule boundary |
| Precedence chain | New agents use ERC/precedence unchanged |
| Four-state separation | Inherited from core |
| Versioned artefacts | Agent + its artefacts versioned |
| Adam persona governs *how*, not *what* | New agents reuse the persona layer (ADR-D3-10) |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Agent bypasses boundaries | Low | High | M | Harness + capability limits + eval | Security Architect | Low |
| RSK-02 | Contract too rigid | Med | Med | M | Extend contract via ADR | AI Arch Lead | Low |
| RSK-03 | Ungoverned agent go-live | Low | High | M | Eval + governance gates | AI Governance Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Core diff to add an agent | ≈ 0 | > 0 | PR review | Per new agent |
| QM-02 | New agents passing eval+governance | 100% | < 100% | Gates | Per new agent |
| QM-03 | Time to add a workflow | ≤ target | rising | Delivery metrics | Per agent |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | New agents inherit guardrails/boundaries |
| Data classification touched | Per new workflow's data |
| Personal data / PII | Inherits data controls (D6-06) |
| Children's data and safeguarding | New agents inherit ADR-D6-16 controls |
| UK GDPR lawful basis and rights impact | Per-workflow DPIA if new data |
| Audit and evidential requirements | Agent registration audited |
| Standards touched | ISO/IEC 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 23 (first agent) → ongoing |
| Repository paths | `src/pf_ft_ai/agents/` |
| Configuration | Agent registration; declarations |
| Contracts / schemas | Agent contract (ADR-D3-03) |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-03, D2-05, D1-10, D6-15 |
| Effort estimate | Low per agent (post-core) |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | New agent added with no core edits | PR diff |
| AC-02 | Declares tools/ERC/prompts as artefacts | Registration review |
| AC-03 | Passes eval + governance | Gates |
| AC-04 | Respects capability boundaries | Boundary test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Per-agent metrics (inherited) |
| Alerting | Per-agent (inherited) |
| Runbook | `docs/runbooks/add-agent.md` |
| Failure mode and degradation | New agent failure isolated |
| Rollback | Deregister/disable agent |
| Support model impact | AI platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Scaffolding generator | M | negligible | Build once |
| Per-agent addition | low | usage | Reuses core |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Contract can't express a workflow | Design | Extend contract (ADR) |
| RT-02 | Adding agents still slow | QM-03 | Improve scaffolding |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-37 Evolution |
| Specification sections | doc 7; doc 20 §45–§46, §49 |
| Requirement IDs | EXT-AGENT-* |
| Build phases | 23 → ongoing |
| Code paths | `src/pf_ft_ai/agents/` |
| Configuration | agent registration |
| Tests | contract + boundary suites |
| Upstream ADRs | ADR-D3-03, D2-05, D1-10 |
| Downstream ADRs | ADR-D8-09 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
