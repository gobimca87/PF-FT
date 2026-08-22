---
id: ADR-D8-01
title: Cost model and unit economics per conversation / workflow completion
domain: 8 Business Value
ws_ref: [WS-34]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: FinOps
contributors: [AI Architecture Lead, Product Owner, SRE]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-07, ADR-D3-13, ADR-D5-10, ADR-D8-03, ADR-D8-05]
source_docs:
  - "MD files/6 Production/26.PF-FT-AI-PERFORMANCE-COST.md §74, §75, §76, §77, §78, §79, §80, §88, §89, §90, §91, §92, §93, §95"
build_phases: [20]
impacted_paths:
  - src/pf_ft_ai/observability/
classification: Internal
review_due: 2027-08-22
---

# ADR-D8-01 — Cost model and unit economics per conversation / workflow completion

## 1. Summary

PFF AI will measure cost as **unit economics — cost per request, per workflow, and per
successful outcome — with cost attribution/tagging, budgets, alerts and anomaly detection**
(doc 26 §74–§93, §95). The headline metric is **cost per successful workflow completion**
(e.g. per completed affiliation), because that ties spend to delivered value; token/GPU/
infra costs roll up into it.

## 2. Context and Problem Statement

Doc 26 §74–§75 cost model/categories, §76–§79 cost per request/workflow/outcome/user,
§80–§87 token/GPU/RAG/eval/agent/observability cost, §88–§93 allocation/tags/budgets/
alerts/anomaly/guardrails. Without a unit-cost model, AI spend is opaque and can't be tied
to value or controlled. This ADR fixes the cost model and its headline unit.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Cost per request/workflow/outcome | doc 26 §76–§78 |
| DR-F-02 | Cost attribution + tags | doc 26 §88–§89 |
| DR-F-03 | Budgets + alerts + anomaly detection | doc 26 §90–§92 |
| DR-F-04 | Tie cost to value (successful outcome) | doc 26 §78; ADR-D8-03 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Cost per step is attributable via traces | Improve cost instrumentation | ADR-D7-02 |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Value-linkage (cost per outcome) | 28 | Spend↔value | Metric present |
| EC-02 | Attribution granularity | 22 | Find cost drivers | Per-step cost |
| EC-03 | Controllability (budgets/alerts) | 20 | Prevent overrun | Controls |
| EC-04 | Accuracy | 16 | Trustworthy | Reconciliation |
| EC-05 | Overhead | 14 | Measurement cost | Instrumentation |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Unit economics (request/workflow/outcome) + attribution/tags + budgets/alerts/anomaly

**Description.** Compute cost per request, per workflow and per successful outcome; attribute
via cost tags (doc 26 §89) and Langfuse token/cost traces (ADR-D7-02); budgets + alerts
(§90–§91) + anomaly detection (§92); headline = cost per successful workflow completion.
**Strengths.** Value-linked, granular, controllable.
**Weaknesses.** Instrumentation upkeep.
**Cost / effort.** Low-medium.

### 5.2 Option B — Total spend only (monthly bill)

**Description.** Track the aggregate cloud/AI bill.
**Strengths.** Trivial.
**Weaknesses.** No unit economics; can't tie to value or find drivers.
**Cost / effort.** Low; opaque.

### 5.3 Option C — Cost per request only

**Description.** Track per-request cost.
**Strengths.** Simple unit.
**Weaknesses.** Misses multi-turn workflow cost and outcome linkage.
**Cost / effort.** Low; partial.

### 5.4 Option D — Infra cost allocation only (by service/tag, no AI token attribution)

**Description.** Cloud cost tags per service.
**Strengths.** Cloud-native.
**Weaknesses.** Misses AI token/GPU cost per interaction — the AI cost driver.
**Cost / effort.** Low; gaps.

### 5.5 Option E — Unit economics + FinOps dashboard + cost gates in CI (cost regression) + showback

**Description.** Option A plus a FinOps dashboard, a cost-regression gate in CI (doc 26
§132/§135) and showback per workflow/county.
**Strengths.** A + prevents cost regressions + accountability.
**Weaknesses.** Dashboard/gate upkeep.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No cost tracking | doc 26 §74 |
| Estimate-only (no measurement) | Not actionable |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 26 §74–§95/§132/§135.

| Criterion | Weight | A: Unit econ | B: Total only | C: Per-request | D: Infra-only | E: A+dashboard+gate |
|---|---|---|---|---|---|---|
| EC-01 Value-linkage | 28 | 5 | 1 | 3 | 2 | 5 |
| EC-02 Attribution | 22 | 5 | 1 | 3 | 3 | 5 |
| EC-03 Controllability | 20 | 5 | 2 | 3 | 3 | 5 |
| EC-04 Accuracy | 16 | 4 | 4 | 4 | 4 | 4 |
| EC-05 Overhead | 14 | 4 | 5 | 4 | 4 | 3 |
| **Weighted total** | **100** | **468** | **228** | **336** | **312** | **472** |

Totals (×20): **E = 472**, **A = 468**, **C = 336**, **D = 312**, **B = 228**.

**Sensitivity.** E (A + FinOps dashboard + cost-regression gate + showback) edges A by
preventing cost regressions and enabling per-county showback. Adopted. Total-only (B) is
opaque; per-request (C) and infra-only (D) miss workflow/outcome and AI-token attribution.

## 7. Decision

**PFF AI will measure unit economics — cost per request, per workflow and (headline) per
successful workflow completion — with cost attribution/tags, budgets, alerts, anomaly
detection, a FinOps dashboard, a CI cost-regression gate and per-workflow/county showback
(Option E).** Total-spend-only (B), per-request-only (C) and infra-only (D) are rejected.

## 8. Architecture Detail

- Cost computed from Langfuse token/cost traces (ADR-D7-02) + cloud cost tags (doc 26 §89);
  rolled up to per-request/workflow/outcome (§76–§78); headline = £/completed affiliation.
- Budgets + alerts (§90–§91), anomaly detection (§92) and cost guardrails (§93–§94, e.g.
  model routing §95–§98 to cheaper models where adequate); cost-regression gate in CI
  (§132/§135; ADR-D7-09). Feeds ROI (ADR-D8-03) and SLO cost dimension (ADR-D7-07).

## 9. Consequences

### 9.1 Positive
- Spend tied to value; drivers visible; overruns prevented.
### 9.2 Negative
- Instrumentation + dashboard upkeep.
### 9.3 Neutral
- Feeds ROI and quality-KPI ADRs.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of total-spend | Value-linked unit economics | FinOps |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Cost measures the AI layer |
| Precedence chain | Cost guardrails never trade correctness for savings (routing safety §97) |
| Four-state separation | N/A |
| Versioned artefacts | Cost model/config versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Cost overrun undetected | Med | High | H | Budgets + alerts + anomaly (§90–§92) | FinOps | Low |
| RSK-02 | Cost guardrail harms quality | Low | Med | M | Routing safety (§97); quality gates | AI Arch Lead | Low |
| RSK-03 | Inaccurate attribution | Med | Med | M | Reconcile traces vs cloud bill | FinOps | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Cost per successful workflow | ≤ model target | over | FinOps dashboard | Monthly |
| QM-02 | Budget adherence | within | breach | Budget alerts | Continuous |
| QM-03 | Cost regressions caught in CI | 100% | < 100% | Cost gate | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None |
| Data classification touched | Internal cost data |
| Personal data / PII | None |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Cost reports retained |
| Standards touched | ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 20 |
| Repository paths | `src/pf_ft_ai/observability/` (cost) + dashboards |
| Configuration | Cost tags; budgets; gates |
| Contracts / schemas | Cost record |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-02, D7-07, D8-03 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Cost per request/workflow/outcome computed | Dashboard review |
| AC-02 | Budgets + anomaly alerts active | Config test |
| AC-03 | Cost-regression gate in CI | CI config |
| AC-04 | Attribution reconciles with cloud bill | FinOps reconciliation |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Cost dashboards; anomaly detection |
| Alerting | Budget breach; anomaly |
| Runbook | `docs/runbooks/finops.md` |
| Failure mode and degradation | Cost guardrails throttle/route (§93–§95) |
| Rollback | Config revert |
| Support model impact | FinOps + AI platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Cost instrumentation + dashboard | M | small | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Unit cost exceeds target | QM-01 | Optimise (routing/self-host/context) |
| RT-02 | Cost anomaly | §92 | Investigate driver |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-34 Business Value |
| Specification sections | doc 26 §74–§98, §132, §135 |
| Requirement IDs | COST-* |
| Build phases | 20 |
| Code paths | observability/cost |
| Configuration | tags/budgets/gates |
| Tests | cost gate |
| Upstream ADRs | ADR-D7-02, D7-07 |
| Downstream ADRs | ADR-D8-03, D8-05 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | FinOps | Initial decision recorded. |
