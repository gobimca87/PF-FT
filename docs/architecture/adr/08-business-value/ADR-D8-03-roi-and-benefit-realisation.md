---
id: ADR-D8-03
title: ROI model and benefit-realisation tracking
domain: 8 Business Value
ws_ref: [WS-34]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Product Owner
contributors: [FinOps, AI Architecture Lead, Principal Architect]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D8-01, ADR-D8-04, ADR-D8-05, ADR-D1-04, ADR-D1-05]
source_docs:
  - "MD files/6 Production/26.PF-FT-AI-PERFORMANCE-COST.md §78"
  - "MD files/5 QualityGovernance/20.PF-FT-AI-GOVERNANCE.md §15"
  - "MD files/1 Foundation/1 PF-FT-AI-ARCHITECTURE.md §1"
build_phases: [20]
impacted_paths:
  - docs/governance/
classification: Internal
review_due: 2027-08-22
---

# ADR-D8-03 — ROI model and benefit-realisation tracking

## 1. Summary

PFF AI will track ROI as **benefit (cost/time saved, capacity freed, error reduction,
experience uplift) minus cost (unit economics, ADR-D8-01), measured against a pre-launch
baseline per workflow**, with **benefit-realisation reviews** rather than a one-off business
case (doc 26 §78; doc 20 §15; doc 1 §1). The first ROI subject is Club Affiliation
(ADR-D1-05): cost per completed affiliation vs the manual/portal baseline.

## 2. Context and Problem Statement

Doc 26 §78 cost per successful outcome; doc 20 §15 AI suitability/benefit; doc 1 §1 the
problem/value framing. Without a measured ROI model tied to a baseline, the platform's value
is asserted, not demonstrated, and investment decisions lack evidence. This ADR fixes the
ROI model and benefit-realisation tracking (D8-01 = cost; D8-04/05 = KPIs feeding benefit).

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Benefit − cost vs baseline per workflow | doc 26 §78; doc 20 §15 |
| DR-F-02 | Ongoing benefit-realisation reviews | benefit-realisation practice |
| DR-F-03 | Baseline captured pre-launch | measurement practice |
| DR-C-01 | Benefit not overstated (evidence-based) | governance |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Baseline metrics obtainable | Estimate + refine | Baseline study |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Evidence-based benefit | 28 | Credible ROI | Baseline vs actual |
| EC-02 | Ongoing realisation (not one-off) | 22 | Sustained value | Review cadence |
| EC-03 | Ties to unit cost | 18 | Net ROI | Cost linkage (D8-01) |
| EC-04 | Attribution honesty | 18 | No overstatement | Causal attribution |
| EC-05 | Simplicity | 14 | Usable | Model weight |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Baseline-anchored benefit − cost, per workflow, with periodic realisation reviews

**Description.** Capture pre-launch baseline per workflow (time/cost/error/experience);
measure post-launch; ROI = benefit − unit cost (ADR-D8-01); periodic benefit-realisation
reviews adjust and re-baseline.
**Strengths.** Evidence-based, ongoing, cost-linked, honest.
**Weaknesses.** Baseline capture effort.
**Cost / effort.** Low-medium.

### 5.2 Option B — One-off upfront business case only

**Description.** Build the case pre-project; don't track after.
**Strengths.** Simple approval artefact.
**Weaknesses.** No realisation tracking; benefits unverified.
**Cost / effort.** Low; unverified.

### 5.3 Option C — Cost-savings-only ROI

**Description.** Track only cost/time saved.
**Strengths.** Concrete.
**Weaknesses.** Ignores experience/capacity/error benefits and quality.
**Cost / effort.** Low; narrow.

### 5.4 Option D — Vanity-metric ROI (usage/volume as value)

**Description.** Treat usage as value.
**Strengths.** Easy.
**Weaknesses.** Usage ≠ value; can mislead investment.
**Cost / effort.** Low; misleading.

### 5.5 Option E — Baseline-anchored ROI + benefit-realisation reviews + A/B or control comparison for attribution

**Description.** Option A with control/A-B comparison (where feasible) to attribute benefit
causally, not just correlationally.
**Strengths.** Strongest attribution honesty.
**Weaknesses.** Control-group setup may be impractical for some flows.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No ROI tracking | doc 20 §15 |
| Overstated benefit | Governance/honesty |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 26 §78, doc 20 §15, doc 1 §1.

| Criterion | Weight | A: Baseline+reviews | B: One-off case | C: Savings-only | D: Vanity | E: A+control comparison |
|---|---|---|---|---|---|---|
| EC-01 Evidence | 28 | 5 | 2 | 4 | 1 | 5 |
| EC-02 Ongoing | 22 | 5 | 1 | 4 | 3 | 5 |
| EC-03 Cost linkage | 18 | 5 | 3 | 4 | 2 | 5 |
| EC-04 Attribution | 18 | 4 | 2 | 3 | 1 | 5 |
| EC-05 Simplicity | 14 | 4 | 5 | 4 | 5 | 3 |
| **Weighted total** | **100** | **462** | **248** | **384** | **220** | **482** |

Totals (×20): **E = 482**, **A = 462**, **C = 384**, **B = 248**, **D = 220**.

**Sensitivity.** E (A + control/A-B comparison) edges A on attribution honesty where a
control is feasible; where it isn't, A applies. One-off case (B) and vanity (D) don't track
realised value.

## 7. Decision

**PFF AI will track ROI as baseline-anchored benefit minus unit cost, per workflow, with
periodic benefit-realisation reviews and control/A-B comparison for causal attribution
where feasible (Option E).** The first subject is Club Affiliation (ADR-D1-05). One-off
business case (B), savings-only (C) and vanity metrics (D) are rejected.

## 8. Architecture Detail

- Baseline captured pre-launch per workflow (time/cost/error/experience); post-launch
  metrics from KPIs (ADR-D8-04/05) and unit cost (ADR-D8-01); ROI computed and reviewed on
  a cadence; re-baseline as processes change.
- Control/A-B where feasible (e.g. cohort still on the portal) for attribution; results feed
  investment/prioritisation (ADR-D1-10) and governance (doc 20 §15).

## 9. Consequences

### 9.1 Positive
- Demonstrated, ongoing, honestly-attributed value.
### 9.2 Negative
- Baseline + review + (optional) control effort.
### 9.3 Neutral
- Consumes cost (D8-01) + KPI (D8-04/05) data.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of one-off case | Evidence-based realised ROI | Product Owner |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | ROI measures orchestration value; enterprise executes |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | ROI model versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Benefit overstated | Med | Med | M | Control comparison; honest attribution | Product Owner | Low |
| RSK-02 | No baseline captured | Med | High | H | Mandate pre-launch baseline | Product Owner | Low |
| RSK-03 | ROI below expectation | Med | Med | M | Realisation reviews → adjust/optimise | Principal Architect | Med |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | ROI per workflow (benefit − cost) | positive & rising | negative | ROI model | Quarterly |
| QM-02 | Workflows with captured baseline | 100% | < 100% | ROI register | Per launch |
| QM-03 | Benefit-realisation reviews held | on schedule | missed | Governance | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None |
| Data classification touched | Aggregated business metrics |
| Personal data / PII | Aggregated/anonymised |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | ROI evidence retained |
| Standards touched | ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 20 |
| Repository paths | `docs/governance/` (ROI model) |
| Configuration | Baseline/metric definitions |
| Contracts / schemas | ROI record |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D8-01, D8-04, D8-05, D1-05 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Baseline captured pre-launch | ROI register |
| AC-02 | ROI = benefit − unit cost | Model review |
| AC-03 | Realisation reviews held | Governance record |
| AC-04 | Attribution method stated | Model review |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | ROI dashboard |
| Alerting | ROI below threshold |
| Runbook | `docs/runbooks/roi.md` |
| Failure mode and degradation | Low ROI → optimise/reprioritise |
| Rollback | N/A |
| Support model impact | Product + FinOps |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| ROI model + reviews | M | periodic | Product/FinOps effort |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | ROI negative sustained | QM-01 | Optimise or reprioritise workflow |
| RT-02 | Process change invalidates baseline | Review | Re-baseline |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-34 |
| Specification sections | doc 26 §78; doc 20 §15; doc 1 §1 |
| Requirement IDs | ROI-* |
| Build phases | 20 |
| Code paths | governance/ROI |
| Configuration | baseline/metrics |
| Tests | N/A |
| Upstream ADRs | ADR-D8-01, D1-05 |
| Downstream ADRs | ADR-D8-04, D8-05 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Product Owner | Initial decision recorded. |
