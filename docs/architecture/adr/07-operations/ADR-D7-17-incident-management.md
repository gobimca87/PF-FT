---
id: ADR-D7-17
title: Incident management and AI-specific incident classification
domain: 7 Operations
ws_ref: [WS-33]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: SRE
contributors: [AI Governance Lead, Security Architect, Product Owner]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-08, ADR-D7-16, ADR-D6-17, ADR-D6-13, ADR-D7-18]
source_docs:
  - "MD files/6 Production/28.PF-FT-AI-OPERATIONS-RUNBOOK.md §8, §9, §10, §11, §12, §13, §14, §15, §105, §106"
  - "MD files/5 QualityGovernance/20.PF-FT-AI-GOVERNANCE.md §105, §106"
build_phases: [10]
impacted_paths:
  - docs/runbooks/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-17 — Incident management and AI-specific incident classification

## 1. Summary

PFF AI will run a **standard incident lifecycle (detect → triage → mitigate → resolve →
review) with P1–P4 severity and evidence capture**, extended with **AI-specific incident
classes** — hallucination/wrong-answer, guardrail bypass/injection, model/prompt
regression, RAG/ACL leak, persona/RAI breach — each with defined handling and a blameless
post-incident review feeding causal analysis (doc 28 §8–§15, §105–§106; doc 20 §105–§106).
AI incidents are first-class, not shoehorned into infra categories.

## 2. Context and Problem Statement

Doc 28 §8–§12 severity (P1–P4), §13 incident lifecycle, §14 first-response checklist, §15
incident evidence, §105–§106 governance incident/process; doc 20 §105–§106 AI governance
incident/process. A hallucinated affiliation status or a guardrail bypass is a real
incident type that classic infra incident management misses. This ADR fixes incident
management and AI-specific classification.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Standard lifecycle + P1–P4 + evidence | doc 28 §8–§15 |
| DR-F-02 | AI-specific incident classes | doc 20 §105–§106; doc 28 §105–§106 |
| DR-F-03 | Blameless review → causal analysis | doc 28 §13; ADR-D6-13 (CAR) |
| DR-C-01 | Evidence capture (audit) | doc 28 §15; ADR-D6-17 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | AI incidents are detectable | Improve detection (evals/guardrails) | ADR-D7-13 |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | AI-incident coverage | 28 | The gap | AI classes handled |
| EC-02 | Response effectiveness (MTTR) | 22 | Limit harm | MTTR |
| EC-03 | Evidence + learning (CAR) | 20 | Prevent recurrence | Reviews→actions |
| EC-04 | Severity/escalation clarity | 18 | Right response | P1–P4 |
| EC-05 | Simplicity | 12 | Usable | Process weight |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Standard lifecycle + P1–P4 + AI-specific classes + evidence + blameless review/CAR

**Description.** The doc 28 lifecycle with P1–P4; add AI incident classes (hallucination,
guardrail bypass, regression, RAG/ACL leak, RAI breach) each with handling; evidence
captured (§15; ADR-D6-17); blameless post-incident review feeds causal analysis
(ADR-D6-13/CAR) and superseding ADRs.
**Strengths.** Covers AI incidents, effective, learning-oriented.
**Weaknesses.** More classes/process.
**Cost / effort.** Medium.

### 5.2 Option B — Generic IT incident management only

**Description.** Classic infra incident process.
**Strengths.** Familiar.
**Weaknesses.** No AI-incident classes; mis-triages hallucination/guardrail issues.
**Cost / effort.** Low; gaps.

### 5.3 Option C — Ad-hoc incident handling

**Description.** Handle incidents case by case.
**Strengths.** Flexible.
**Weaknesses.** Inconsistent; poor evidence/learning.
**Cost / effort.** Low; weak.

### 5.4 Option D — Severity + lifecycle but no blameless review/CAR

**Description.** Handle + resolve, skip structured review.
**Strengths.** Faster close.
**Weaknesses.** Recurrence; no causal learning (doc 20 §106).
**Cost / effort.** Low; repeats incidents.

### 5.5 Option E — A + automated AI-incident detection hooks (from evals/guardrails/SLOs)

**Description.** Option A with automated detection: guardrail hits, eval regressions, SLO
burn, ACL-leak signals auto-open incidents with severity.
**Strengths.** Faster detection of AI incidents; less reliance on user reports.
**Weaknesses.** Detection tuning.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No incident process | doc 28 §13 |
| No evidence capture | doc 28 §15 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 28 §8–§15/§105–§106 and doc 20
§105–§106.

| Criterion | Weight | A: Lifecycle+AI classes | B: Generic IT | C: Ad-hoc | D: No review | E: A+auto-detect |
|---|---|---|---|---|---|---|
| EC-01 AI coverage | 28 | 5 | 2 | 2 | 4 | 5 |
| EC-02 MTTR | 22 | 5 | 4 | 2 | 4 | 5 |
| EC-03 Evidence/learning | 20 | 5 | 3 | 1 | 2 | 5 |
| EC-04 Severity clarity | 18 | 5 | 4 | 2 | 5 | 5 |
| EC-05 Simplicity | 12 | 4 | 5 | 4 | 5 | 3 |
| **Weighted total** | **100** | **488** | **336** | **214** | **384** | **484** |

Totals (×20): **A = 488**, **E = 484**, **D = 384**, **B = 336**, **C = 214**.

**Sensitivity.** A leads; automated AI-incident detection (E) is adopted as an enhancement
once evals/guardrails/SLOs are live, cutting detection time. Generic-IT-only (B) misses AI
incidents; skipping review (D) breeds recurrence.

## 7. Decision

**PFF AI will run the standard incident lifecycle with P1–P4 severity and evidence
capture, extended with AI-specific incident classes (hallucination/wrong-answer, guardrail
bypass/injection, model/prompt regression, RAG/ACL leak, persona/RAI breach), each with
defined handling, and a blameless post-incident review feeding causal analysis and
superseding ADRs; automated AI-incident detection from guardrails/evals/SLOs opens
incidents (Option E, on top of A).** Generic-IT-only (B), ad-hoc (C) and no-review (D) are
rejected.

## 8. Architecture Detail

- Lifecycle (doc 28 §13): detect→triage→mitigate→resolve→review; first-response checklist
  (§14); P1–P4 (§9–§12); evidence captured to the audit store (§15; ADR-D6-17).
- AI incident classes with handling: hallucination (roll back prompt/model, ADR-D7-12;
  strengthen eval), guardrail bypass/injection (patch guardrail ADR-D6-08, add case),
  RAG/ACL leak (sev-1, ADR-D6-12), RAI/persona breach (ADR-D6-13). Detection hooks from
  guardrails/evals/SLOs auto-open incidents (ADR-D7-08/13/07).
- Blameless review → causal analysis (ADR-D6-13 CAR) → superseding ADR where a decision is
  implicated (per template §18).

## 9. Consequences

### 9.1 Positive
- AI incidents handled as first-class; faster detection; learning prevents recurrence.
### 9.2 Negative
- More incident classes/process + detection tuning.
### 9.3 Neutral
- Ties alerting (D7-08), audit (D6-17), CAR (D6-13), DR (D7-18).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Process simplicity | AI-incident coverage + learning | SRE |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | AI incidents (e.g. wrong "truth") treated seriously |
| Precedence chain | RAG/ACL-leak + hallucination incidents protect authoritative truth |
| Four-state separation | Incident evidence redacted per classification |
| Versioned artefacts | Fixes ship as versioned artefacts (ADR-D7-12) |
| Adam persona governs *how*, not *what* | Persona/RAI breach is an incident class |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | AI incident mis-triaged as infra | Med | Med | M | AI-specific classes + training | SRE | Low |
| RSK-02 | Recurrence (no learning) | Low | High | M | Blameless review + CAR (ADR-D6-13) | AI Governance Lead | Low |
| RSK-03 | Slow AI-incident detection | Med | Med | M | Auto-detection hooks (E) | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | AI incidents with correct class + review | 100% | < 100% | Incident data | Monthly |
| QM-02 | Repeat incidents (same cause) | ≈ 0 | rising | Incident data | Monthly |
| QM-03 | Time-to-detect AI incidents | ≤ target | rising | Detection hooks | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Faster response to security/AI incidents |
| Data classification touched | Incident evidence (redacted) |
| Personal data / PII | Redacted in evidence |
| Children's data and safeguarding | Safeguarding incidents P1; regulatory notification if needed |
| UK GDPR lawful basis and rights impact | Breach process supports 72h notification |
| Audit and evidential requirements | Incident evidence retained (ADR-D6-17) |
| Standards touched | ISO/IEC 27001, 42001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 10 |
| Repository paths | `docs/runbooks/` (incident) |
| Configuration | Incident classes; detection hooks |
| Contracts / schemas | Incident record |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-08, D6-17, D6-13, D7-13 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | AI incident classes defined + handled | Runbook review |
| AC-02 | Evidence captured to audit | Incident drill |
| AC-03 | Blameless review feeds CAR | Process check |
| AC-04 | Auto-detection opens incidents | Detection test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Incident metrics; detection hooks |
| Alerting | Auto-open on AI signals (ADR-D7-08) |
| Runbook | `docs/runbooks/incident.md` |
| Failure mode and degradation | Defined per class + severity |
| Rollback | AI rollback (ADR-D7-12; doc 28 §44–§47) |
| Support model impact | On-call (ADR-D7-16) |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Incident tooling + detection | M | small | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | New AI incident type | Post-incident | Add class + handling |
| RT-02 | Repeat incidents | QM-02 | Deeper CAR; superseding ADR |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-33 |
| Specification sections | doc 28 §8–§15, §105–§106; doc 20 §105–§106 |
| Requirement IDs | INC-* |
| Build phases | 10 |
| Code paths | `docs/runbooks/` |
| Configuration | incident classes/hooks |
| Tests | incident drills |
| Upstream ADRs | ADR-D7-08, D6-17 |
| Downstream ADRs | ADR-D6-13, D7-18 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | SRE | Initial decision recorded. |
