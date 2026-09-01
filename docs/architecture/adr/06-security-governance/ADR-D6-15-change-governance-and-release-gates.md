---
id: ADR-D6-15
title: Model/prompt/index change governance and release approval gates
domain: 6 Security & Governance
ws_ref: [WS-28]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Governance Lead
contributors: [Release Manager, AI Architecture Lead, Security Architect]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-06, ADR-D3-11, ADR-D3-15, ADR-D7-12, ADR-D7-13]
source_docs:
  - "MD files/5 QualityGovernance/20.PFF-FA-AI-GOVERNANCE.md §34, §36, §37, §42, §44, §49, §75, §76, §77, §78, §79, §80, §81, §86"
build_phases: [12]
impacted_paths:
  - .github/
classification: Internal
review_due: 2027-08-22
---

# ADR-D6-15 — Model/prompt/index change governance and release approval gates

## 1. Summary

Changes to versioned AI artefacts — models, prompts, RAG indexes, guardrails, agents,
workflows — will pass **classified change-governance gates**: risk-classified changes,
required approvals by role, evaluation release gates (golden datasets/regression), and
approval evidence, before promotion via the release manifest (20.PFF-FA-AI-GOVERNANCE.md §34–§49, §75–§81,
§86; ADR-D5-06). High-risk changes need explicit sign-off; emergency changes have a
defined expedited-but-evidenced path.

## 2. Context and Problem Statement

20.PFF-FA-AI-GOVERNANCE.md §34/§36–§37 model governance/approval/change, §42/§44 prompt governance/change,
§49 workflow change, §75–§81 release/change management/classification/high-risk/emergency/
approval workflow/evidence, §86 evaluation release gate. Ungoverned changes to
model/prompt/index are the top cause of AI regressions and safety incidents. This ADR
fixes the change-governance gates (D5-06 provides the manifest; D7-13 the eval gates).

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Risk-classify changes | 20.PFF-FA-AI-GOVERNANCE.md §77 |
| DR-F-02 | Role-based approvals + evidence | 20.PFF-FA-AI-GOVERNANCE.md §80–§81 |
| DR-F-03 | Evaluation release gate | 20.PFF-FA-AI-GOVERNANCE.md §86; ADR-D7-13 |
| DR-F-04 | Emergency-change path | 20.PFF-FA-AI-GOVERNANCE.md §79 |
| DR-C-01 | Promote via immutable manifest | ADR-D5-06 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Changes are classifiable by risk | Default high-risk | Governance review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Regression/safety prevention | 30 | Core purpose | Escaped regressions |
| EC-02 | Proportionality (risk-based) | 22 | Not over-gating | Gate by risk |
| EC-03 | Evidence/auditability | 18 | Accountability | Approval records |
| EC-04 | Emergency responsiveness | 16 | Incident fixes | Expedited path |
| EC-05 | Velocity impact | 14 | Ship speed | Lead time |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Risk-classified gates + role approvals + eval gate + evidence + emergency path

**Description.** Each artefact change is risk-classified (§77); required approvals scale
with risk (§78, §80); the eval release gate (§86; ADR-D7-13) must pass; approval evidence
retained (§81); emergency path (§79) is expedited but still evidenced; promotion via
manifest (ADR-D5-06).
**Strengths.** Prevents regressions proportionately; auditable; responsive.
**Weaknesses.** Process to maintain.
**Cost / effort.** Medium.

### 5.2 Option B — Uniform heavy approval for all changes

**Description.** Every change gets full review.
**Strengths.** Thorough.
**Weaknesses.** Over-gates low-risk changes; slows velocity; approval fatigue.
**Cost / effort.** Medium; slow.

### 5.3 Option C — CI checks only (no human approval)

**Description.** Automated eval gates, no sign-off.
**Strengths.** Fast.
**Weaknesses.** No human accountability for high-risk model/safety changes; misses
judgement calls.
**Cost / effort.** Low; gaps.

### 5.4 Option D — Human approval only (no eval gate)

**Description.** Reviewers approve; no automated eval.
**Strengths.** Judgement.
**Weaknesses.** Misses measurable regressions; subjective; 20.PFF-FA-AI-GOVERNANCE.md §86 wants eval gate.
**Cost / effort.** Medium; gaps.

### 5.5 Option E — Risk-classified gates + automated eval + change-impact analysis + rollback readiness

**Description.** Option A plus mandatory change-impact analysis (16.PFF-FA-AI-PROMPT-ENGINEERING.md §105/§158 for
prompts; dependency graph) and verified rollback readiness before promotion.
**Strengths.** Understands blast radius; safe to revert.
**Weaknesses.** More upfront analysis.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Ad-hoc changes to prod artefacts | 20.PFF-FA-AI-GOVERNANCE.md §76; CLAUDE.md immutability |
| No emergency path | 20.PFF-FA-AI-GOVERNANCE.md §79 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 20.PFF-FA-AI-GOVERNANCE.md §75–§86.

| Criterion | Weight | A: Risk gates | B: Uniform heavy | C: CI-only | D: Human-only | E: A+impact+rollback |
|---|---|---|---|---|---|---|
| EC-01 Regression prevention | 30 | 5 | 5 | 3 | 3 | 5 |
| EC-02 Proportionality | 22 | 5 | 2 | 4 | 3 | 5 |
| EC-03 Evidence | 18 | 5 | 5 | 3 | 4 | 5 |
| EC-04 Emergency response | 16 | 5 | 2 | 4 | 3 | 5 |
| EC-05 Velocity | 14 | 4 | 2 | 5 | 3 | 4 |
| **Weighted total** | **100** | **484** | **340** | **372** | **324** | **496** |

Totals (×20): **E = 496**, **A = 484**, **C = 372**, **B = 340**, **D = 324**.

**Sensitivity.** E (A + change-impact analysis + rollback readiness) edges A by ensuring
blast radius is understood and reverts are safe — high value for model/prompt/index
changes. Uniform-heavy (B) over-gates; CI-only (C) and human-only (D) each miss half the
assurance.

## 7. Decision

**Changes to models, prompts, RAG indexes, guardrails, agents and workflows will pass
risk-classified governance gates: proportionate role-based approvals, a mandatory
evaluation release gate, change-impact analysis, verified rollback readiness, and
retained approval evidence, with a defined expedited-but-evidenced emergency path;
promotion is via the immutable release manifest (Option E).** Uniform-heavy (B),
CI-only (C) and human-only (D) are rejected.

## 8. Architecture Detail

- Change classification (§77) → required approvals (§78/§80) encoded in CI/CD (branch
  protection, required reviewers) + governance record; eval gate (ADR-D7-13; 20.PFF-FA-AI-GOVERNANCE.md §86)
  blocks promotion on regression.
- Change-impact analysis (prompt dependency graph 16.PFF-FA-AI-PROMPT-ENGINEERING.md §105–§106; model/index deps
  ADR-D3-15/D3-24); rollback readiness verified (prior manifest available, ADR-D5-06).
- Emergency path (§79): expedited approval with mandatory post-hoc evidence + review.
- Approval evidence retained (§81; ADR-D6-17).

## 9. Consequences

### 9.1 Positive
- Proportionate, auditable change control preventing AI regressions; safe reverts.
### 9.2 Negative
- Governance process + impact analysis overhead.
### 9.3 Neutral
- Builds on manifest (D5-06) and eval gates (D7-13).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Some velocity on high-risk changes | Regression/safety prevention | AI Governance Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Governance keeps changes within approved scope |
| Precedence chain | Index/model changes can't undermine authoritative data |
| Four-state separation | N/A |
| Versioned artefacts | Enforces immutable versioned promotion |
| Adam persona governs *how*, not *what* | Persona changes are governed prompt changes |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Regression reaches prod | Med | High | H | Eval gate + impact analysis (E) | AI Governance Lead | Low |
| RSK-02 | Emergency path abused | Low | High | M | Post-hoc evidence + review (§79) | Governance | Low |
| RSK-03 | Over-gating slows fixes | Med | Med | M | Risk-proportionate gates | Release Manager | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Artefact changes passing required gates | 100% | < 100% | CI/CD audit | Per release |
| QM-02 | Regressions escaping to prod | ≈ 0 | rising | Incident tracking | Monthly |
| QM-03 | Emergency changes with post-hoc evidence | 100% | < 100% | Audit | Per incident |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Governed changes reduce unsafe deploys |
| Data classification touched | Internal |
| Personal data / PII | Eval datasets governed for privacy (20.PFF-FA-AI-GOVERNANCE.md §84) |
| Children's data and safeguarding | Safeguarding-affecting changes high-risk |
| UK GDPR lawful basis and rights impact | Change control supports accountability |
| Audit and evidential requirements | Approval evidence retained |
| Standards touched | ISO/IEC 42001, 27001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 12 |
| Repository paths | `.github/` (branch protection, workflows) + governance records |
| Configuration | Change-classification + approval matrix |
| Contracts / schemas | Approval evidence record |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-06, D3-11, D3-15, D7-13 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Changes risk-classified + approved per matrix | CI/CD + audit |
| AC-02 | Eval gate blocks regressions | Gate test |
| AC-03 | Rollback readiness verified pre-promotion | Release drill |
| AC-04 | Emergency changes evidenced post-hoc | Audit |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Change/approval flow; gate outcomes |
| Alerting | Gate bypass attempts; regressions |
| Runbook | `docs/runbooks/change-governance.md` |
| Failure mode and degradation | Gate fail → block promotion |
| Rollback | Re-promote prior manifest |
| Support model impact | Governance + release mgmt |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Governance workflow + eval gates | M | small | CI + process |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Regressions persist despite gates | QM-02 | Strengthen eval/impact analysis |
| RT-02 | Gates block velocity excessively | QM/feedback | Re-tune risk thresholds |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-28 |
| Specification sections | 20.PFF-FA-AI-GOVERNANCE.md §34–§49, §75–§86 |
| Requirement IDs | GOV-CHG-* |
| Build phases | 12 |
| Code paths | `.github/`, governance |
| Configuration | approval matrix |
| Tests | gate + rollback drills |
| Upstream ADRs | ADR-D5-06, D3-11, D3-15 |
| Downstream ADRs | ADR-D7-12, D7-13 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Governance Lead | Initial decision recorded. |
