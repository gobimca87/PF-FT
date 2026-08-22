---
id: ADR-D8-05
title: AI quality KPIs — containment, deflection, accuracy, persona adherence
domain: 8 Business Value
ws_ref: [WS-35]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [Product Owner, ML Engineer, Conversation Designer]
reviewers: [Principal Architect, AI Governance Lead]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D8-04, ADR-D7-13, ADR-D1-09, ADR-D3-22, ADR-D7-07]
source_docs:
  - "MD files/6 Production/24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §50"
  - "MD files/5 QualityGovernance/21.PF-FT-AI-EVALUATION.md §14, §15, §19, §21, §22, §23, §24"
build_phases: [16, 20]
impacted_paths:
  - docs/governance/
classification: Internal
review_due: 2027-08-22
---

# ADR-D8-05 — AI quality KPIs — containment, deflection, accuracy, persona adherence

## 1. Summary

PFF AI will track **AI-quality KPIs distinct from business KPIs** — answer accuracy/
groundedness, retrieval quality, hallucination rate, clarification appropriateness,
containment/deflection, and **persona adherence evaluated separately** (per CLAUDE.md and
ADR-D1-09) — sourced from the evaluation framework (ADR-D7-13) and observability (doc 24
§50; doc 21 §14–§24). Persona adherence is measured independently of workflow/tool/security
correctness, as CLAUDE.md requires.

## 2. Context and Problem Statement

Doc 24 §50 AI quality metrics; doc 21 §14–§15 business/outcome metrics, §19–§24 relevance/
completeness/groundedness/faithfulness/hallucination/citation. CLAUDE.md §Persona Quality
mandates evaluating persona adherence **separately** from workflow, tool, security and model
quality. Without a defined AI-quality KPI set, quality regressions and persona drift are
invisible. This ADR fixes the AI-quality KPIs and the separate persona-adherence measure.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Accuracy/groundedness/hallucination/retrieval KPIs | doc 21 §19–§24; doc 24 §50 |
| DR-F-02 | Containment/deflection quality | doc 21 §14–§15 |
| DR-C-01 | Persona adherence measured separately | CLAUDE.md §Persona Quality; ADR-D1-09 |
| DR-F-03 | Sourced from eval framework | ADR-D7-13 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Quality dims measurable via eval + online signals | Add human eval | ADR-D7-13 |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Coverage of quality dimensions | 28 | Catch regressions | Dims tracked |
| EC-02 | Persona measured separately | 22 | CLAUDE.md mandate | Separate metric |
| EC-03 | Measurability (eval+online) | 20 | Real signals | Data source |
| EC-04 | Actionability | 16 | Drives fixes | Decision use |
| EC-05 | Separation from business/ops | 14 | No conflation | Distinct set |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Full AI-quality KPI set + separate persona-adherence, from eval + online

**Description.** KPIs: accuracy/groundedness/faithfulness, hallucination rate, retrieval
quality (Recall@k, ADR-D3-22), citation validity, clarification appropriateness,
containment/deflection; persona adherence as a **separate** KPI (CLAUDE.md); sourced from
eval (ADR-D7-13) + online signals (doc 21 §9).
**Strengths.** Comprehensive, mandate-compliant, actionable.
**Weaknesses.** Eval/measurement upkeep.
**Cost / effort.** Medium.

### 5.2 Option B — Single blended "quality score"

**Description.** One composite quality number.
**Strengths.** Simple headline.
**Weaknesses.** Hides which dimension regressed; conflates persona with correctness
(violates CLAUDE.md separation).
**Cost / effort.** Low; opaque.

### 5.3 Option C — Accuracy-only

**Description.** Track correctness only.
**Strengths.** Focused.
**Weaknesses.** Ignores persona, hallucination, retrieval, containment.
**Cost / effort.** Low; narrow.

### 5.4 Option D — Persona folded into business KPIs

**Description.** Put persona under business KPIs (D8-04).
**Strengths.** Fewer dashboards.
**Weaknesses.** CLAUDE.md requires persona evaluated separately; conflation.
**Cost / effort.** Low; non-compliant.

### 5.5 Option E — Full quality set + separate persona + online drift detection + human-eval sampling

**Description.** Option A with online drift detection and periodic human-eval sampling to
validate automated scores (doc 21 §59).
**Strengths.** A + drift catch + human-validated.
**Weaknesses.** Human-eval effort.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No AI-quality KPIs | doc 24 §50 |
| Persona blended with correctness | CLAUDE.md §Persona Quality |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 24 §50, doc 21 §14–§24/§59 and
CLAUDE.md persona-quality rules.

| Criterion | Weight | A: Full+separate persona | B: Blended score | C: Accuracy-only | D: Persona in business | E: A+drift+human |
|---|---|---|---|---|---|---|
| EC-01 Coverage | 28 | 5 | 3 | 2 | 4 | 5 |
| EC-02 Persona separate | 22 | 5 | 1 | 1 | 1 | 5 |
| EC-03 Measurability | 20 | 4 | 4 | 5 | 4 | 5 |
| EC-04 Actionability | 16 | 5 | 2 | 3 | 3 | 5 |
| EC-05 Separation | 14 | 5 | 2 | 4 | 2 | 5 |
| **Weighted total** | **100** | **478** | **252** | **282** | **288** | **500** |

Totals (×20): **E = 500**, **A = 478**, **D = 288**, **C = 282**, **B = 252**.

**Sensitivity.** E (A + online drift + human-eval sampling) wins by validating automated
scores and catching drift. Blended-score (B) and persona-in-business (D) violate the
CLAUDE.md separation mandate decisively.

## 7. Decision

**PFF AI will track a full AI-quality KPI set (accuracy/groundedness/faithfulness,
hallucination rate, retrieval quality, citation validity, clarification appropriateness,
containment/deflection) with persona adherence measured as a separate KPI, sourced from the
evaluation framework plus online drift detection and periodic human-eval sampling (Option
E).** Blended single-score (B), accuracy-only (C) and persona-in-business-KPIs (D) are
rejected — the last violates CLAUDE.md's separation requirement.

## 8. Architecture Detail

- KPIs computed by the eval framework (ADR-D7-13) on golden + online data; retrieval KPIs
  from ADR-D3-22; persona adherence scored by a dedicated persona eval (ADR-D1-09; CLAUDE.md
  Persona Quality) on its own axis, never blended with correctness.
- Online drift detection flags regressions; human-eval sampling calibrates (doc 21 §59); an
  AI-quality dashboard (distinct from business D8-04 and SLIs D7-07); correctness KPI feeds
  the SLO (ADR-D7-07).

## 9. Consequences

### 9.1 Positive
- Regression + persona-drift visibility; mandate-compliant separation; actionable.
### 9.2 Negative
- Eval + human-sampling upkeep.
### 9.3 Neutral
- Feeds SLOs (D7-07) and change decisions (D6-15).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Single headline score | Dimension-level + persona-separate insight | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Quality of orchestration measured |
| Precedence chain | Groundedness/hallucination KPIs protect authoritative-truth fidelity |
| Four-state separation | N/A |
| Versioned artefacts | KPI/eval definitions versioned |
| Adam persona governs *how*, not *what* | Persona adherence measured separately, per CLAUDE.md |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Persona conflated with correctness | Low | Med | M | Separate persona eval (CLAUDE.md) | AI Arch Lead | Low |
| RSK-02 | Quality regression unseen | Med | High | H | Eval gates + online drift (E) | ML Eng | Low |
| RSK-03 | Automated scores unreliable | Med | Med | M | Human-eval sampling (§59) | ML Eng | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Answer accuracy/groundedness | ≥ target | falling | Eval | Per release + online |
| QM-02 | Hallucination rate | ≈ 0 | rising | Eval | Continuous |
| QM-03 | Persona adherence (separate) | ≥ 0.9 | < 0.8 | Persona eval | Per release |
| QM-04 | Containment/deflection | ≥ target | falling | Online | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None |
| Data classification touched | Eval data governed (doc 20 §84) |
| Personal data / PII | Synthetic/anonymised eval; online privacy-safe |
| Children's data and safeguarding | No real children's data in eval |
| UK GDPR lawful basis and rights impact | Minimised online eval |
| Audit and evidential requirements | Quality reports retained |
| Standards touched | ISO/IEC 42001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 16 (eval), 20 (dashboards) |
| Repository paths | `docs/governance/` + `tests/eval/` |
| Configuration | KPI/eval definitions |
| Contracts / schemas | Quality-KPI record |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-13, D1-09, D3-22, D8-04 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Quality dims tracked | Dashboard review |
| AC-02 | Persona adherence a separate metric | Metric review |
| AC-03 | Sourced from eval + online | Pipeline check |
| AC-04 | Human-eval calibration run | Calibration report |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | AI-quality dashboard; drift |
| Alerting | Quality/persona regression |
| Runbook | `docs/runbooks/ai-quality.md` |
| Failure mode and degradation | Regression → block promotion (D7-13) |
| Rollback | Artefact rollback (D7-12) |
| Support model impact | AI platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Quality KPIs + human sampling | M | periodic | Eval + human effort |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Persona drift | QM-03 | Revise persona (ADR-D3-10) |
| RT-02 | Quality regression | QM-01/02 | Root-cause + fix (D7-12/13) |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-35 |
| Specification sections | doc 24 §50; doc 21 §14–§24, §59; CLAUDE.md §Persona Quality |
| Requirement IDs | KPI-AI-* |
| Build phases | 16, 20 |
| Code paths | `tests/eval/`, governance |
| Configuration | KPI/eval defs |
| Tests | eval suites |
| Upstream ADRs | ADR-D7-13, D1-09 |
| Downstream ADRs | ADR-D8-04, D7-07 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
