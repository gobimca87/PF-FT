---
id: ADR-D7-13
title: Evaluation and regression gates in CI — golden datasets, LLM-as-judge
domain: 7 Operations
ws_ref: [WS-32]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [ML Engineer, QA Lead]
reviewers: [Principal Architect, AI Governance Lead]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-09, ADR-D7-12, ADR-D7-14, ADR-D6-15, ADR-D8-05]
source_docs:
  - "MD files/5 QualityGovernance/21.PF-FT-AI-EVALUATION.md §6, §7, §8, §10, §12, §16, §17, §21, §22, §23, §24, §26, §56, §57, §58, §59"
build_phases: [12]
impacted_paths:
  - tests/eval/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-13 — Evaluation and regression gates in CI — golden datasets, LLM-as-judge

## 1. Summary

PFF AI will gate AI changes on **automated evaluation against versioned golden datasets**,
combining **deterministic checks** (exact/functional correctness) with **LLM-as-judge**
for subjective qualities (relevance, groundedness, faithfulness, persona), plus adversarial
and security evals — with **regression thresholds** blocking promotion (21.PF-FT-AI-EVALUATION.md §6–§26,
§56–§59). Deterministic-first; LLM-judge only where determinism can't measure the quality,
and always validated against human ratings.

## 2. Context and Problem Statement

21.PF-FT-AI-EVALUATION.md §6–§8 evaluation levels/types/offline, §10–§13 golden dataset/versioning/categories,
§16–§17 functional/deterministic correctness, §21–§24 groundedness/faithfulness/
hallucination/citation, §26 prompt regression, §56–§59 guardrail/security/adversarial/human
eval. AI quality can regress invisibly on a prompt/model/index change. This ADR fixes the
evaluation-gate approach used by CI (ADR-D7-09) and LLMOps (ADR-D7-12).

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Versioned golden datasets | 21.PF-FT-AI-EVALUATION.md §10, §12 |
| DR-F-02 | Deterministic + subjective (judge) eval | 21.PF-FT-AI-EVALUATION.md §16–§17, §18–§24 |
| DR-F-03 | Regression thresholds block promotion | 21.PF-FT-AI-EVALUATION.md §26; 20.PF-FT-AI-GOVERNANCE.md §86 |
| DR-F-04 | Adversarial + security eval | 21.PF-FT-AI-EVALUATION.md §56–§58 |
| DR-C-01 | Judge validated vs human ratings | 21.PF-FT-AI-EVALUATION.md §59 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | LLM-judge correlates with human ratings | Fall back to human eval for that dimension | 21.PF-FT-AI-EVALUATION.md §59 |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Regression detection power | 30 | Core purpose | Caught regressions |
| EC-02 | Deterministic reliability | 22 | Trustworthy gate | Determinism |
| EC-03 | Coverage (quality dims + adversarial) | 20 | Completeness | Dimensions covered |
| EC-04 | CI-fit (speed/cost) | 16 | Usable in gate | Runtime/cost |
| EC-05 | Judge validity | 12 | Judge trust | Human correlation |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Golden datasets + deterministic-first + validated LLM-judge + adversarial/security + regression thresholds

**Description.** Versioned golden datasets per category (21.PF-FT-AI-EVALUATION.md §13); deterministic checks
where possible (§17); LLM-as-judge for subjective dims (§18–§24), calibrated to human
ratings (§59); adversarial + security evals (§56–§58); thresholds gate promotion (§26).
**Strengths.** Strong detection, reliable, broad, calibrated.
**Weaknesses.** Dataset + judge maintenance.
**Cost / effort.** Medium.

### 5.2 Option B — Deterministic-only evaluation

**Description.** Exact/functional checks only.
**Strengths.** Fully reliable, cheap.
**Weaknesses.** Can't measure relevance/groundedness/persona; misses subjective regressions.
**Cost / effort.** Low; incomplete.

### 5.3 Option C — LLM-judge-only

**Description.** Judge everything.
**Strengths.** Flexible; measures subjective.
**Weaknesses.** Non-deterministic; judge bias; costly; needs calibration; weak on exact
correctness.
**Cost / effort.** Medium; less reliable alone.

### 5.4 Option D — Human evaluation only

**Description.** Manual review of samples.
**Strengths.** Gold-standard judgement.
**Weaknesses.** Slow; can't gate every change; not scalable in CI.
**Cost / effort.** High per cycle.

### 5.5 Option E — A + online evaluation (production monitoring) feeding datasets

**Description.** Option A plus online eval (21.PF-FT-AI-EVALUATION.md §9) on production traffic feeding new
golden cases and drift detection.
**Strengths.** Offline gate + online drift catch; datasets stay representative.
**Weaknesses.** Online eval pipeline + privacy handling.
**Cost / effort.** Medium-high.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No eval gate | 20.PF-FT-AI-GOVERNANCE.md §86 |
| Unversioned datasets | 21.PF-FT-AI-EVALUATION.md §12 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 21.PF-FT-AI-EVALUATION.md §6–§26/§56–§59.

| Criterion | Weight | A: Golden+det+judge | B: Deterministic-only | C: Judge-only | D: Human-only | E: A+online |
|---|---|---|---|---|---|---|
| EC-01 Detection | 30 | 5 | 3 | 4 | 4 | 5 |
| EC-02 Determinism | 22 | 5 | 5 | 2 | 3 | 5 |
| EC-03 Coverage | 20 | 5 | 2 | 4 | 4 | 5 |
| EC-04 CI-fit | 16 | 4 | 5 | 3 | 1 | 4 |
| EC-05 Judge validity | 12 | 4 | 5 | 2 | 5 | 4 |
| **Weighted total** | **100** | **468** | **372** | **312** | **352** | **476** |

Totals (×20): **E = 476**, **A = 468**, **B = 372**, **D = 352**, **C = 312**.

**Sensitivity.** E (A + online eval feeding datasets) edges A by keeping golden sets
representative and catching drift. Adopted; online eval added once production traffic
exists. Deterministic-only (B) can't measure subjective quality; judge-only (C) is
unreliable alone.

## 7. Decision

**PFF AI will gate AI changes on evaluation against versioned golden datasets, using
deterministic checks first and validated LLM-as-judge for subjective dimensions, plus
adversarial and security evals, with regression thresholds blocking promotion; online
evaluation on production traffic feeds the golden datasets and drift detection (Option
E).** The judge is calibrated against human ratings (21.PF-FT-AI-EVALUATION.md §59). Deterministic-only (B),
judge-only (C) and human-only (D) are rejected as sole approaches.

## 8. Architecture Detail

- `tests/eval/`: golden datasets per category (21.PF-FT-AI-EVALUATION.md §13), versioned (§12); deterministic
  scorers (§17); an LLM-judge harness (calibrated, §59) for relevance/completeness/
  groundedness/faithfulness/citation/persona (§19–§24; persona ties to ADR-D8-05);
  adversarial + security datasets (§56–§58).
- Regression thresholds (§26) gate promotion in CI (ADR-D7-09) and LLMOps (ADR-D7-12);
  online eval (§9) samples production (privacy-safe, 20.PF-FT-AI-GOVERNANCE.md §84) to grow datasets + detect
  drift.

## 9. Consequences

### 9.1 Positive
- Objective, broad, calibrated regression detection gating AI changes.
### 9.2 Negative
- Dataset + judge calibration + online pipeline upkeep.
### 9.3 Neutral
- Powers CI gates (D7-09) and LLMOps (D7-12) and SLO correctness (D7-07).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of deterministic-only | Coverage of subjective quality | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Eval measures the AI layer; no business authority |
| Precedence chain | Groundedness/faithfulness evals protect authoritative-truth fidelity |
| Four-state separation | Eval data governed; no real PII (synthetic) |
| Versioned artefacts | Datasets versioned |
| Adam persona governs *how*, not *what* | Persona adherence evaluated separately (ADR-D8-05) |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Judge unreliable/biased | Med | Med | M | Calibrate vs human (§59); deterministic-first | ML Eng | Low |
| RSK-02 | Dataset drift (stale) | Med | Med | M | Online eval feeds datasets (E) | AI Arch Lead | Low |
| RSK-03 | Eval too slow for CI | Med | Med | M | Tiered eval (fast subset PR, full pre-merge) | QA Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | AI regressions caught pre-prod | ≥ target | falling | Eval/incident | Monthly |
| QM-02 | Judge-human correlation | ≥ target | below | Calibration | Quarterly |
| QM-03 | Golden dataset freshness | current | stale | Online eval | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Adversarial eval strengthens guardrails |
| Data classification touched | Eval datasets governed (20.PF-FT-AI-GOVERNANCE.md §84) |
| Personal data / PII | Synthetic/anonymised eval data; online eval privacy-safe |
| Children's data and safeguarding | No real children's data in eval |
| UK GDPR lawful basis and rights impact | Online eval minimised/anonymised |
| Audit and evidential requirements | Eval results retained (evidence) |
| Standards touched | ISO/IEC 42001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 12 |
| Repository paths | `tests/eval/` |
| Configuration | Datasets; thresholds; judge config |
| Contracts / schemas | Eval case schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-09, D7-12, D6-15, D8-05 |
| Effort estimate | M–L |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Golden datasets versioned per category | Repo review |
| AC-02 | Deterministic + judge scorers run | Eval run |
| AC-03 | Thresholds block promotion on regression | Gate test |
| AC-04 | Judge calibrated vs human | Calibration report |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Eval scores; drift; judge correlation |
| Alerting | Regression; drift |
| Runbook | `docs/runbooks/evaluation.md` |
| Failure mode and degradation | Regression → block promotion / auto-rollback (D7-12) |
| Rollback | Revert artefact bundle |
| Support model impact | AI platform + QA |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Eval harness + datasets | M | per-run judge cost | Build + inference |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Regressions slip past eval | Incident | Add cases/dimensions |
| RT-02 | Judge drift | QM-02 | Recalibrate/replace judge |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-32 |
| Specification sections | 21.PF-FT-AI-EVALUATION.md §6–§26, §56–§59 |
| Requirement IDs | EVAL-* |
| Build phases | 12 |
| Code paths | `tests/eval/` |
| Configuration | datasets/thresholds |
| Tests | eval harness itself |
| Upstream ADRs | ADR-D7-09 |
| Downstream ADRs | ADR-D7-12, D8-05 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
