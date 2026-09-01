---
id: ADR-D8-04
title: Business KPI framework and dashboard definition
domain: 8 Business Value
ws_ref: [WS-35]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Product Owner
contributors: [FinOps, AI Architecture Lead, SRE]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D8-05, ADR-D8-03, ADR-D8-01, ADR-D7-01, ADR-D1-04]
source_docs:
  - "MD files/5 QualityGovernance/20.PFF-FA-AI-GOVERNANCE.md §15, §87, §88"
  - "MD files/6 Production/26.PFF-FA-AI-PERFORMANCE-COST.md §78"
build_phases: [20]
impacted_paths:
  - docs/governance/
classification: Internal
review_due: 2027-08-22
---

# ADR-D8-04 — Business KPI framework and dashboard definition

## 1. Summary

PFF AI will define a **business KPI framework** — workflow completion rate, containment/
deflection, time-to-completion, user satisfaction, cost per outcome — presented on a
**business dashboard**, distinct from AI-quality KPIs (ADR-D8-05) and operational SLIs
(ADR-D7-07) (20.PFF-FA-AI-GOVERNANCE.md §15, §87–§88; 26.PFF-FA-AI-PERFORMANCE-COST.md §78). KPIs are outcome-focused and tied to the ROI
model (ADR-D8-03).

## 2. Context and Problem Statement

20.PFF-FA-AI-GOVERNANCE.md §15 AI suitability/benefit, §87–§88 governance metrics/dashboard; 26.PFF-FA-AI-PERFORMANCE-COST.md §78 cost per
outcome. Without an agreed business-KPI set, stakeholders judge success by anecdote. This
ADR fixes the business KPI framework and dashboard (D8-05 = AI-quality KPIs; D7-07 =
operational SLIs — kept separate).

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Outcome-focused business KPIs | 20.PFF-FA-AI-GOVERNANCE.md §15; 26.PFF-FA-AI-PERFORMANCE-COST.md §78 |
| DR-F-02 | Business dashboard | 20.PFF-FA-AI-GOVERNANCE.md §88 |
| DR-C-01 | Distinct from AI-quality/ops metrics | ADR-D8-05, D7-07 |
| DR-F-03 | Tied to ROI | ADR-D8-03 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Outcomes measurable from platform + enterprise | Add instrumentation | Metric review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Outcome relevance | 30 | Measure value | KPI fit |
| EC-02 | Measurability | 22 | Real data | Data source |
| EC-03 | Separation from quality/ops | 18 | No conflation | Distinct set |
| EC-04 | Actionability | 16 | Drives decisions | Decision use |
| EC-05 | Simplicity | 14 | Focus | # KPIs |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Outcome-focused business KPI set + dashboard, tied to ROI, separate from quality/ops

**Description.** KPIs: completion rate, containment/deflection, time-to-completion, CSAT,
cost per outcome (ADR-D8-01); on a business dashboard (20.PFF-FA-AI-GOVERNANCE.md §88); feeding ROI (ADR-D8-03);
kept distinct from AI-quality (D8-05) and SLIs (D7-07).
**Strengths.** Relevant, measurable, actionable, uncluttered.
**Weaknesses.** Instrumentation for some KPIs.
**Cost / effort.** Low-medium.

### 5.2 Option B — Merge business + AI-quality + ops into one metric set

**Description.** One combined dashboard.
**Strengths.** Single view.
**Weaknesses.** Conflates audiences/purposes; noise; harder to act.
**Cost / effort.** Low; muddled.

### 5.3 Option C — Usage/volume KPIs (sessions, messages)

**Description.** Track activity.
**Strengths.** Easy.
**Weaknesses.** Activity ≠ outcomes/value.
**Cost / effort.** Low; low value.

### 5.4 Option D — Financial KPIs only (cost/ROI)

**Description.** Money metrics only.
**Strengths.** Clear to finance.
**Weaknesses.** Misses experience/completion; incomplete picture.
**Cost / effort.** Low; narrow.

### 5.5 Option E — Outcome KPIs + dashboard + per-county/segment breakdown + targets & trends

**Description.** Option A with per-county/segment slicing and explicit targets/trend lines.
**Strengths.** Actionable per segment; target-driven.
**Weaknesses.** More dashboard work.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No business KPIs | 20.PFF-FA-AI-GOVERNANCE.md §15/§87 |
| Vanity-only KPIs | Not outcome-focused |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 20.PFF-FA-AI-GOVERNANCE.md §15/§87–§88 and 26.PFF-FA-AI-PERFORMANCE-COST.md §78.

| Criterion | Weight | A: Outcome set | B: Merged | C: Usage | D: Financial-only | E: A+segments+targets |
|---|---|---|---|---|---|---|
| EC-01 Relevance | 30 | 5 | 3 | 2 | 3 | 5 |
| EC-02 Measurability | 22 | 4 | 4 | 5 | 4 | 4 |
| EC-03 Separation | 18 | 5 | 1 | 3 | 4 | 5 |
| EC-04 Actionability | 16 | 5 | 3 | 2 | 3 | 5 |
| EC-05 Simplicity | 14 | 4 | 3 | 5 | 4 | 3 |
| **Weighted total** | **100** | **458** | **294** | **314** | **352** | **454** |

Totals (×20): **A = 458**, **E = 454**, **D = 352**, **C = 314**, **B = 294**.

**Sensitivity.** A and E near-tied; per-county/segment slicing + targets (E) add
actionability for a multi-county context (ADR-D8-09) at modest cost — adopted where segments
matter. Merged (B) conflates audiences.

## 7. Decision

**PFF AI will define an outcome-focused business KPI set (workflow completion rate,
containment/deflection, time-to-completion, CSAT, cost per outcome) on a business dashboard
with per-county/segment breakdown and explicit targets/trends, tied to ROI (ADR-D8-03) and
kept distinct from AI-quality KPIs (ADR-D8-05) and operational SLIs (ADR-D7-07) (Option
E-with-A base).** Merged (B), usage-only (C) and financial-only (D) are rejected.

## 8. Architecture Detail

- KPIs computed from platform telemetry (ADR-D7-01), enterprise outcomes (completion), and
  cost (ADR-D8-01); business dashboard (20.PFF-FA-AI-GOVERNANCE.md §88) with targets/trends and county/segment
  slices; feeds ROI (ADR-D8-03) and governance review (20.PFF-FA-AI-GOVERNANCE.md §90).
- Separation: AI-quality (D8-05) and SLIs (D7-07) live on their own dashboards for their
  audiences.

## 9. Consequences

### 9.1 Positive
- Shared, outcome-focused view of business value; actionable per segment.
### 9.2 Negative
- Instrumentation + dashboard upkeep.
### 9.3 Neutral
- Feeds ROI; complements quality/ops KPIs.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| One combined dashboard | Audience-appropriate, actionable KPIs | Product Owner |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | KPIs measure orchestration outcomes; enterprise executes |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | KPI definitions versioned |
| Adam persona governs *how*, not *what* | Persona adherence is a quality KPI (D8-05), not business KPI |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | KPIs not measurable | Med | Med | M | Add instrumentation; proxies | Product Owner | Low |
| RSK-02 | Metric conflation/noise | Low | Med | M | Keep sets separate (D8-05/D7-07) | Product Owner | Low |
| RSK-03 | Vanity focus | Low | Med | M | Outcome-focused definitions | Product Owner | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Workflow completion rate | ≥ target | falling | Dashboard | Monthly |
| QM-02 | Containment/deflection | ≥ target | falling | Dashboard | Monthly |
| QM-03 | Cost per outcome (from D8-01) | ≤ target | rising | FinOps | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None |
| Data classification touched | Aggregated business metrics |
| Personal data / PII | Aggregated/anonymised |
| Children's data and safeguarding | No child-level KPIs exposed |
| UK GDPR lawful basis and rights impact | Aggregation minimises |
| Audit and evidential requirements | KPI reports retained |
| Standards touched | ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 20 |
| Repository paths | `docs/governance/` (KPI defs) + dashboards |
| Configuration | KPI/target definitions |
| Contracts / schemas | KPI record |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D8-01, D8-03, D8-05, D7-01 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Outcome KPIs defined + on dashboard | Dashboard review |
| AC-02 | Distinct from quality/ops metrics | Metric review |
| AC-03 | Tied to ROI | ROI linkage |
| AC-04 | Per-segment breakdown available | Dashboard |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Business dashboard |
| Alerting | KPI target breach |
| Runbook | `docs/runbooks/kpi.md` |
| Failure mode and degradation | Missing data → flagged, not guessed |
| Rollback | KPI def revert |
| Support model impact | Product + FinOps |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| KPI instrumentation + dashboard | M | small | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | KPIs not driving decisions | Review | Refine KPI set |
| RT-02 | New workflow launched | Launch | Extend KPIs |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-35 KPIs |
| Specification sections | 20.PFF-FA-AI-GOVERNANCE.md §15, §87–§88; 26.PFF-FA-AI-PERFORMANCE-COST.md §78 |
| Requirement IDs | KPI-BIZ-* |
| Build phases | 20 |
| Code paths | governance/KPI |
| Configuration | KPI defs |
| Tests | N/A |
| Upstream ADRs | ADR-D8-01, D1-04 |
| Downstream ADRs | ADR-D8-03, D8-05 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Product Owner | Initial decision recorded. |
