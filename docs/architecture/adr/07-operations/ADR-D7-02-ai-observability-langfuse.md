---
id: ADR-D7-02
title: AI-specific observability — Langfuse
domain: 7 Operations
ws_ref: [WS-31]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [ML Engineer, SRE, Security Architect]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-01, ADR-D7-03, ADR-D3-11, ADR-D6-17, ADR-D7-04]
source_docs:
  - "MD files/6 Production/24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §15, §23, §24, §25, §27, §42, §43, §44, §45, §46, §47, §48, §50"
build_phases: [10]
impacted_paths:
  - src/pff_fa_ai/observability/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D7-02 — AI-specific observability — Langfuse

## 1. Summary

PFF AI will use **Langfuse** as the AI-specific observability layer — tracing LLM/agent
executions, prompt versions, token usage and cost, and AI-quality signals — complementing
the platform stack (ADR-D7-01) (24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §15, §23–§27, §42–§48, §50; CLAUDE.md). Langfuse
is for AI observability, **not** the tamper-evident audit record (ADR-D6-17), and its
traces are redacted of sensitive data.

## 2. Context and Problem Statement

24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §15 AI observability, §23–§24 prompt observability/version traceability, §25–§27
model/provider/token observability, §42–§48 Langfuse integration/trace-structure/config/
sampling/retention/failure, §50 AI quality metrics; CLAUDE.md names Langfuse. Generic APM
can't see prompt versions, token cost per step, or agent-graph reasoning. This ADR fixes
Langfuse as the AI-observability layer and its boundaries.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Trace LLM/agent/prompt/token/cost | 24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §15, §23–§27 |
| DR-F-02 | Prompt-version traceability | 24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §24; ADR-D3-11 |
| DR-C-01 | Redact sensitive data in traces | 24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §14; ADR-D7-04 |
| DR-C-02 | Not the audit record | ADR-D6-17 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Langfuse deployable in-tenancy | Use hosted with data controls | Deployment review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | AI trace fidelity (prompt/token/agent) | 28 | Core purpose | Trace richness |
| EC-02 | Cost/quality visibility | 22 | FinOps + quality | Cost/quality metrics |
| EC-03 | Data control (in-tenancy/redaction) | 20 | Sensitive prompts | Data residency |
| EC-04 | Integration effort | 14 | Adoption | Wiring |
| EC-05 | Reliability (failure isolation) | 16 | Not on critical path | Failure mode |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Langfuse (self-hosted in-tenancy), redacted traces, failure-isolated

**Description.** Self-host Langfuse in Azure; SDK traces LLM/agent/prompt/token/cost;
redaction before send (ADR-D7-04); tracing failures never break serving (§48); sampling/
retention configured (§46–§47).
**Strengths.** Rich AI observability; in-tenancy data control; prompt-version linkage.
**Weaknesses.** Operate Langfuse.
**Cost / effort.** Medium.

### 5.2 Option B — Langfuse Cloud (hosted)

**Description.** Managed Langfuse SaaS.
**Strengths.** No ops.
**Weaknesses.** Prompt/trace data off-tenancy (sensitive); data-residency concern.
**Cost / effort.** Low ops; data-boundary cost.

### 5.3 Option C — App Insights only (no AI-specific tool)

**Description.** Use platform APM for everything.
**Strengths.** One stack.
**Weaknesses.** No prompt-version/token/agent-graph semantics; weak AI quality view.
**Cost / effort.** Low; insufficient for AI.

### 5.4 Option D — Build a bespoke AI-tracing layer

**Description.** Home-grown tracing.
**Strengths.** Tailored.
**Weaknesses.** Reinvents Langfuse; high build/maintenance.
**Cost / effort.** High.

### 5.5 Option E — Other LLM-observability tool (e.g. Phoenix/Arize/OpenLLMetry)

**Description.** An alternative LLM-observability product.
**Strengths.** Comparable features.
**Weaknesses.** CLAUDE.md standardises on Langfuse; switching loses that alignment; no
compelling edge for this stack.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No AI observability | 24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §15 |
| Langfuse as the audit record | ADR-D6-17 (separate concern) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §15/§42–§48 and CLAUDE.md.

| Criterion | Weight | A: Langfuse self-host | B: Langfuse Cloud | C: App Insights only | D: Bespoke | E: Other tool |
|---|---|---|---|---|---|---|
| EC-01 Trace fidelity | 28 | 5 | 5 | 2 | 3 | 5 |
| EC-02 Cost/quality | 22 | 5 | 5 | 2 | 3 | 5 |
| EC-03 Data control | 20 | 5 | 2 | 5 | 5 | 4 |
| EC-04 Integration | 14 | 4 | 5 | 4 | 2 | 3 |
| EC-05 Reliability | 16 | 4 | 4 | 5 | 3 | 4 |
| **Weighted total** | **100** | **466** | **418** | **332** | **328** | **444** |

Totals (×20): **A = 466**, **E = 444**, **B = 418**, **C = 332**, **D = 328**.

**Sensitivity.** A leads; Langfuse Cloud (B) is close but loses on data control for
sensitive prompts. Other tools (E) are viable but CLAUDE.md standardises on Langfuse.
App-Insights-only (C) can't provide AI semantics.

## 7. Decision

**PFF AI will use self-hosted Langfuse (in-tenancy) as the AI-specific observability
layer, with redacted traces and failure isolation so tracing never breaks serving
(Option A).** It complements the platform stack (ADR-D7-01) and links prompt versions
(ADR-D3-11); it is not the audit record (ADR-D6-17). Langfuse Cloud (B) is a fallback if
self-hosting is impractical, subject to data-boundary controls. App-Insights-only (C),
bespoke (D) and other tools (E) are rejected.

## 8. Architecture Detail

- Langfuse SDK wraps SLM/agent/graph calls; traces carry correlation id (ADR-D7-03),
  prompt version (ADR-D3-11), model+version, token counts, cost, and AI-quality signals
  (§50); redaction before send (ADR-D7-04).
- Config per environment (§44–§45); sampling (§46) and retention (§47) tuned; tracing
  failures degrade gracefully (§48) — never block a user turn.
- Distinct from audit (ADR-D6-17) and platform logs (ADR-D7-04).

## 9. Consequences

### 9.1 Positive
- Deep AI observability (prompt/token/cost/agent) with in-tenancy data control.
### 9.2 Negative
- Operate self-hosted Langfuse.
### 9.3 Neutral
- Complements platform stack + audit.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Zero-ops (Cloud) | In-tenancy data control | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Observability only; no business authority |
| Precedence chain | N/A |
| Four-state separation | Traces redacted; not a state store |
| Versioned artefacts | Prompt/model versions traced |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Sensitive prompt data in traces | Med | High | H | Redaction before send (ADR-D7-04) | Security Architect | Low |
| RSK-02 | Tracing failure impacts serving | Low | Med | M | Failure isolation (§48) | SRE | Low |
| RSK-03 | Langfuse ops burden | Med | Low | L | Managed/self-host sizing | Platform Eng | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | LLM/agent calls traced | ≥ sampling target | below | Langfuse | Continuous |
| QM-02 | Prompt version present on traces | 100% | < 100% | Traces | Continuous |
| QM-03 | Sensitive data in traces | 0 | > 0 | Redaction tests | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | In-tenancy trace store |
| Data classification touched | Prompts may be Confidential — redacted |
| Personal data / PII | Redacted before trace |
| Children's data and safeguarding | No safeguarding content in traces |
| UK GDPR lawful basis and rights impact | Minimised trace data |
| Audit and evidential requirements | Separate from audit (ADR-D6-17) |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 10 |
| Repository paths | `src/pff_fa_ai/observability/` |
| Configuration | Langfuse env config; sampling/retention |
| Contracts / schemas | Trace structure (§43) |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-01, D7-03, D3-11, D7-04 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | AI calls traced with prompt/model/token/cost | Trace review |
| AC-02 | Traces redacted | Redaction test |
| AC-03 | Tracing failure doesn't break serving | Fault test (§48) |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Langfuse health (28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §39); trace volume |
| Alerting | Langfuse down; trace loss |
| Runbook | `docs/runbooks/langfuse.md` |
| Failure mode and degradation | Degrade tracing, keep serving (§48) |
| Rollback | Config revert |
| Support model impact | AI platform + SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Langfuse (self-host) | setup | infra | AKS resources |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Self-host ops too costly | Ops | Move to Langfuse Cloud with data controls (B) |
| RT-02 | Trace data-leak incident | Incident | CAR; tighten redaction |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-31 |
| Specification sections | 24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §15, §23–§27, §42–§48, §50 |
| Requirement IDs | OBS-AI-* |
| Build phases | 10 |
| Code paths | `src/pff_fa_ai/observability/` |
| Configuration | Langfuse config |
| Tests | trace + redaction suites |
| Upstream ADRs | ADR-D7-01, D3-11 |
| Downstream ADRs | ADR-D6-17 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
