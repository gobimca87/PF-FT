---
id: ADR-D6-13
title: Responsible AI principles and prohibited-use boundary
domain: 6 Security & Governance
ws_ref: [WS-28]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Governance Lead
contributors: [Principal Architect, Data Protection Officer, Security Architect]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D1-02, ADR-D6-14, ADR-D6-16, ADR-D6-18, ADR-D3-06]
source_docs:
  - "MD files/5 QualityGovernance/20.PF-FT-AI-GOVERNANCE.md §21, §22, §23, §24, §25, §26, §27, §28, §29, §30, §13, §14, §15"
build_phases: [9, 12]
impacted_paths:
  - docs/governance/
classification: Internal
review_due: 2027-08-22
---

# ADR-D6-13 — Responsible AI principles and prohibited-use boundary

## 1. Summary

PFF AI will adopt an explicit **Responsible AI framework** — fairness, reliability,
safety, privacy, transparency, explainability, traceability, auditability (20.PF-FT-AI-GOVERNANCE.md
§21–§30) — and a **prohibited-use boundary** defining what the platform must not do
(no autonomous business decisions, no unsupported claims, no profiling of children
beyond legitimate football administration, no use outside its stated scope). These
principles are made **enforceable** through the existing controls (Golden Rule ADR-D1-02,
guardrails, HIL) rather than left as a poster.

## 2. Context and Problem Statement

20.PF-FT-AI-GOVERNANCE.md §21–§30 define Responsible AI principles and their scope; §13–§15 AI suitability
and risk classification. Without an explicit, enforceable RAI framework and a
prohibited-use boundary, "responsible AI" is aspirational and the platform has no clear
line for what it will refuse to do. This ADR fixes the RAI principles and the
prohibited-use boundary, mapped to concrete controls.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Adopt the 8 RAI principles | 20.PF-FT-AI-GOVERNANCE.md §21–§30 |
| DR-F-02 | Define a prohibited-use boundary | 20.PF-FT-AI-GOVERNANCE.md §22, §14 |
| DR-C-01 | Principles enforced via controls, not text | ADR-D1-02, D6-09, D6-14 |
| DR-F-03 | Risk-classify AI uses | 20.PF-FT-AI-GOVERNANCE.md §15–§17 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Existing controls can enforce RAI | Add controls | Governance review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Enforceability (controls, not text) | 30 | Real RAI | Principle→control map |
| EC-02 | Coverage of RAI principles | 22 | Completeness | 8 principles |
| EC-03 | Clarity of prohibited-use boundary | 20 | Refusal line | Boundary defined |
| EC-04 | Auditability/traceability | 16 | Evidence | Traceable |
| EC-05 | Practicality | 12 | Usable | Overhead |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — RAI principles mapped to enforcing controls + explicit prohibited-use boundary + risk classification

**Description.** Each principle mapped to a concrete control (e.g. traceability→Langfuse,
safety→guardrails, privacy→ADR-D6-06, decision-authority→Golden Rule); a documented
prohibited-use list; AI uses risk-classified (§15) before build.
**Strengths.** Enforceable, complete, auditable.
**Weaknesses.** Mapping upkeep.
**Cost / effort.** Low-medium.

### 5.2 Option B — RAI policy document only (principles, no control mapping)

**Description.** A statement of principles.
**Strengths.** Quick.
**Weaknesses.** Not enforceable; "poster RAI".
**Cost / effort.** Low; weak.

### 5.3 Option C — Adopt an external RAI standard verbatim (e.g. NIST AI RMF) as the framework

**Description.** Use NIST AI RMF as the RAI framework directly.
**Strengths.** Rigorous, recognised.
**Weaknesses.** Needs mapping to PFF controls anyway; heavy if adopted wholesale now.
Better as the conformance target (ADR-D6-18).
**Cost / effort.** Medium.

### 5.4 Option D — Principles enforced purely by human review (no automated controls)

**Description.** Rely on governance board review for RAI.
**Strengths.** Human judgement.
**Weaknesses.** Doesn't scale to runtime; misses per-interaction issues.
**Cost / effort.** Medium; gaps.

### 5.5 Option E — RAI controls + continuous RAI metrics/dashboards + periodic review

**Description.** Option A plus RAI metrics (fairness/quality/persona) monitored on a
dashboard (20.PF-FT-AI-GOVERNANCE.md §87–§89) with periodic governance review.
**Strengths.** Ongoing assurance, not point-in-time.
**Weaknesses.** Metric definition/upkeep.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No RAI framework | 20.PF-FT-AI-GOVERNANCE.md §21 |
| RAI as marketing only | Not enforceable |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 20.PF-FT-AI-GOVERNANCE.md §13–§30/§87–§89.

| Criterion | Weight | A: Mapped controls | B: Policy doc | C: NIST verbatim | D: Human-only | E: A+metrics |
|---|---|---|---|---|---|---|
| EC-01 Enforceability | 30 | 5 | 1 | 3 | 2 | 5 |
| EC-02 Coverage | 22 | 5 | 4 | 5 | 3 | 5 |
| EC-03 Prohibited-use clarity | 20 | 5 | 4 | 3 | 4 | 5 |
| EC-04 Auditability | 16 | 5 | 2 | 4 | 3 | 5 |
| EC-05 Practicality | 12 | 4 | 5 | 2 | 3 | 4 |
| **Weighted total** | **100** | **488** | **300** | **360** | **290** | **496** |

Totals (×20): **E = 496**, **A = 488**, **C = 360**, **B = 300**, **D = 290**.

**Sensitivity.** E (A + continuous RAI metrics) edges A by making RAI ongoing rather than
point-in-time. NIST AI RMF (C) is adopted as a *conformance target* (ADR-D6-18), not the
day-to-day framework. Policy-only (B) and human-only (D) are not enforceable at runtime.

## 7. Decision

**PFF AI will adopt the eight Responsible AI principles mapped to concrete enforcing
controls, an explicit prohibited-use boundary, risk classification of AI uses, and
continuous RAI metrics with periodic governance review (Option E).** NIST AI RMF and
ISO/IEC 42001 are conformance targets (ADR-D6-18). Policy-only (B) and human-review-only
(D) are rejected as unenforceable at runtime.

## 8. Architecture Detail

- Principle→control map: safety→guardrails (ADR-D6-09); privacy→ADR-D6-06/16;
  decision-authority→Golden Rule (ADR-D1-02); transparency/explainability→cited answers
  (ADR-D3-22) + persona honesty (ADR-D1-09); traceability/auditability→Langfuse +
  audit (ADR-D6-17, D7-02).
- Prohibited-use list maintained in `docs/governance/`; out-of-scope intents refused
  (ADR-D3-06 closed intent set); risk classification (20.PF-FT-AI-GOVERNANCE.md §15–§17) gates new AI uses.
- RAI metrics (fairness proxies, quality, persona adherence, refusal correctness) on a
  governance dashboard (20.PF-FT-AI-GOVERNANCE.md §87–§89); periodic review (§90).

## 9. Consequences

### 9.1 Positive
- Enforceable, monitored RAI with a clear refusal boundary.
### 9.2 Negative
- Metric/mapping maintenance.
### 9.3 Neutral
- Frames HIL (D6-14) and compliance (D6-18).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Lightweight policy statement | Enforceable, auditable RAI | AI Governance Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Decision-authority principle = Golden Rule |
| Precedence chain | Reliability/transparency uphold authoritative truth |
| Four-state separation | Privacy principle respects state boundaries |
| Versioned artefacts | RAI controls versioned |
| Adam persona governs *how*, not *what* | Transparency: persona never misrepresents truth |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | RAI stays aspirational | Med | High | H | Control mapping + metrics (E) | AI Governance Lead | Low |
| RSK-02 | Prohibited-use boundary unclear | Low | High | M | Documented list + refusal tests | Principal Architect | Low |
| RSK-03 | Fairness issues in outputs | Low | Med | M | RAI metrics + review | AI Governance Lead | Med |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | RAI principles with mapped controls | 8/8 | < 8 | Governance audit | Quarterly |
| QM-02 | Out-of-scope/prohibited requests refused | 100% | < 100% | Refusal tests | Per release |
| QM-03 | RAI metrics tracked | all defined | gaps | Dashboard | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Prohibited-use refusals reduce misuse |
| Data classification touched | Internal |
| Personal data / PII | Privacy principle → ADR-D6-06/16 |
| Children's data and safeguarding | RAI safety + privacy for children (ADR-D6-16) |
| UK GDPR lawful basis and rights impact | Transparency/fairness support rights |
| Audit and evidential requirements | RAI evidence retained |
| Standards touched | ISO/IEC 42001, 23894, NIST AI RMF, EU AI Act |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 9, 12 |
| Repository paths | `docs/governance/` + control links |
| Configuration | RAI metrics; prohibited-use list |
| Contracts / schemas | Risk-classification record |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D1-02, D6-09, D6-16, D3-06 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Each RAI principle maps to a control | Governance audit |
| AC-02 | Prohibited-use requests refused | Refusal tests |
| AC-03 | New AI uses risk-classified | Intake review |
| AC-04 | RAI metrics on dashboard | Dashboard check |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | RAI metrics dashboard |
| Alerting | RAI metric regressions |
| Runbook | `docs/runbooks/rai.md` |
| Failure mode and degradation | Uncertain use → refuse/escalate |
| Rollback | Policy revert |
| Support model impact | Governance board |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| RAI framework + metrics | M | small | Governance effort |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Regulation changes (EU AI Act) | Compliance | Update RAI + prohibited-use |
| RT-02 | RAI incident | Incident | CAR; add control |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-28 Governance |
| Specification sections | 20.PF-FT-AI-GOVERNANCE.md §13–§17, §21–§30, §87–§90 |
| Requirement IDs | GOV-RAI-* |
| Build phases | 9, 12 |
| Code paths | governance + controls |
| Configuration | RAI metrics/prohibited-use |
| Tests | refusal + RAI eval |
| Upstream ADRs | ADR-D1-02 |
| Downstream ADRs | ADR-D6-14, D6-16, D6-18 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Governance Lead | Initial decision recorded. |
