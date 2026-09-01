---
id: ADR-D6-14
title: Human oversight and HIL governance model
domain: 6 Security & Governance
ws_ref: [WS-28]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Governance Lead
contributors: [Principal Architect, Product Owner, Domain SME]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D1-08, ADR-D2-10, ADR-D3-07, ADR-D6-13, ADR-D1-02]
source_docs:
  - "MD files/5 QualityGovernance/20.PF-FT-AI-GOVERNANCE.md §68, §69, §70, §71"
build_phases: [4, 12]
impacted_paths:
  - src/pf_ft_ai/orchestration/
classification: Internal
review_due: 2027-08-22
---

# ADR-D6-14 — Human oversight and HIL governance model

## 1. Summary

PFF AI will keep **humans in authority over consequential decisions**: a defined
human-in-the-loop (HIL) boundary means the platform pauses for human decision/approval
on defined actions (e.g. CFA review of affiliation, irreversible/high-impact steps),
humans hold decision authority, and **HIL decisions are captured as evidence** (20.PF-FT-AI-GOVERNANCE.md
§68–§71). HIL is a governed workflow state (ADR-D2-10), not an afterthought.

## 2. Context and Problem Statement

20.PF-FT-AI-GOVERNANCE.md §68 human oversight, §69 HIL boundary, §70 human decision authority, §71 HIL
evidence. The Golden Rule (ADR-D1-02) makes the enterprise/humans the deciders; the
platform must therefore know *when* to defer to a human, *who* decides, and *record*
the decision. Without a governance model, HIL is inconsistent and un-evidenced. This ADR
fixes the HIL boundary, authority and evidence model (D2-10 provides the mechanics;
D3-07 the conversational trigger).

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Defined HIL boundary (when to pause) | 20.PF-FT-AI-GOVERNANCE.md §69; ADR-D3-07 |
| DR-C-01 | Humans hold decision authority | 20.PF-FT-AI-GOVERNANCE.md §70; ADR-D1-02 |
| DR-F-02 | HIL decisions captured as evidence | 20.PF-FT-AI-GOVERNANCE.md §71; ADR-D6-17 |
| DR-F-03 | HIL as a durable workflow state | ADR-D2-10 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | HIL actions are enumerable | Default high-impact to HIL | Workflow review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Human authority on consequential actions | 30 | Golden Rule | Boundary coverage |
| EC-02 | Evidence capture | 22 | Accountability/audit | HIL records |
| EC-03 | Clear boundary (when to pause) | 20 | Consistency | Boundary defined |
| EC-04 | UX (not over-pausing) | 16 | Flow | Pause rate |
| EC-05 | Durability (resume) | 12 | Long-running HIL | Resume works |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Defined HIL boundary + human authority + evidence capture + durable resume

**Description.** Enumerate HIL-required actions (high-impact/irreversible/CFA-review);
pause as a durable workflow state (ADR-D2-10); human decides; capture who/what/when as
evidence (20.PF-FT-AI-GOVERNANCE.md §71; ADR-D6-17); resume on decision.
**Strengths.** Human authority, evidenced, consistent, durable.
**Weaknesses.** Boundary maintenance.
**Cost / effort.** Medium.

### 5.2 Option B — No HIL (full automation)

**Description.** Platform acts autonomously.
**Strengths.** Fastest.
**Weaknesses.** Violates Golden Rule for consequential actions; unacceptable.
**Cost / effort.** Low; forbidden.

### 5.3 Option C — HIL on everything (human approves each step)

**Description.** Human confirms every action.
**Strengths.** Maximum oversight.
**Weaknesses.** Destroys UX/throughput; oversight fatigue.
**Cost / effort.** Low; impractical.

### 5.4 Option D — HIL by confidence threshold only (pause when model unsure)

**Description.** Pause based on model confidence.
**Strengths.** Adaptive.
**Weaknesses.** Confidence is unreliable; misses confident-but-wrong high-impact actions;
must be by consequence, not confidence (ADR-D3-07).
**Cost / effort.** Low; unsafe basis.

### 5.5 Option E — Consequence-based HIL boundary + confidence as a secondary trigger + evidence

**Description.** Option A (consequence-based) with low confidence as an *additional*
trigger to pause even on lower-impact actions.
**Strengths.** Consequence-first with a safety net for uncertainty.
**Weaknesses.** Slightly more triggers to tune.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Autonomous consequential decisions | ADR-D1-02 |
| HIL without evidence | 20.PF-FT-AI-GOVERNANCE.md §71 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 20.PF-FT-AI-GOVERNANCE.md §68–§71 and ADR-D3-07/D2-10.

| Criterion | Weight | A: Consequence HIL | B: No HIL | C: HIL all | D: Confidence-only | E: Consequence+confidence |
|---|---|---|---|---|---|---|
| EC-01 Human authority | 30 | 5 | 1 | 5 | 3 | 5 |
| EC-02 Evidence | 22 | 5 | 1 | 5 | 4 | 5 |
| EC-03 Clear boundary | 20 | 5 | 2 | 3 | 2 | 5 |
| EC-04 UX | 16 | 4 | 5 | 1 | 4 | 4 |
| EC-05 Durability | 12 | 5 | 3 | 4 | 4 | 5 |
| **Weighted total** | **100** | **482** | **214** | **384** | **316** | **492** |

Totals (×20): **E = 492**, **A = 482**, **C = 384**, **D = 316**, **B = 214**.

**Sensitivity.** E (consequence-based + confidence safety net) edges A by catching
uncertain lower-impact cases without HIL-on-everything. Consequence remains primary
(confidence alone, D, is unsafe). No-HIL (B) is forbidden.

## 7. Decision

**PFF AI will define a consequence-based HIL boundary (high-impact/irreversible/CFA-review
actions require human decision), with low model confidence as a secondary trigger, hold
human decision authority, implement HIL as a durable workflow state (ADR-D2-10), and
capture every HIL decision as evidence (Option E).** Full automation of consequential
actions (B) is forbidden; HIL-on-everything (C) and confidence-only (D) are rejected.

## 8. Architecture Detail

- HIL-required actions enumerated per workflow (e.g. affiliation CFA review); the
  conversational trigger and confirmation are ADR-D3-07; the durable pause/resume is
  ADR-D2-10 (WAITING_FOR_HUMAN state).
- HIL evidence (who/role, decision, timestamp, context) recorded per 20.PF-FT-AI-GOVERNANCE.md §71 and
  audited (ADR-D6-17); humans hold authority (§70) — the model never overrides a human
  decision.
- Confidence-based secondary trigger uses the uncertainty record (ADR-D3-08).

## 9. Consequences

### 9.1 Positive
- Human authority on consequential actions, evidenced and durable.
### 9.2 Negative
- Boundary + evidence maintenance; some pauses.
### 9.3 Neutral
- Uses D2-10 mechanics + D3-07 triggers.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Full automation speed | Human authority + accountability | AI Governance Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Humans/enterprise decide consequential actions |
| Precedence chain | Human decision is authoritative |
| Four-state separation | HIL is a workflow state (ADR-D2-10) |
| Versioned artefacts | HIL boundary config versioned |
| Adam persona governs *how*, not *what* | Persona explains the wait; never decides |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Consequential action taken without HIL | Low | Critical | H | Enumerated boundary + confirmation gate | AI Governance Lead | Low |
| RSK-02 | Over-pausing harms UX | Med | Med | M | Consequence-based scoping | Product Owner | Low |
| RSK-03 | HIL decision not evidenced | Low | High | M | Mandatory evidence capture (§71) | Governance | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Consequential actions with HIL | 100% | < 100% | Workflow audit | Per release |
| QM-02 | HIL decisions with evidence | 100% | < 100% | Audit | Continuous |
| QM-03 | HIL pause rate (over-pausing) | reasonable | rising | Metrics | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Human gate on high-impact actions |
| Data classification touched | HIL context (per classification) |
| Personal data / PII | HIL evidence may include identities (minimised) |
| Children's data and safeguarding | Safeguarding decisions kept with humans |
| UK GDPR lawful basis and rights impact | Human oversight of significant decisions (Art. 22 adjacent) |
| Audit and evidential requirements | HIL evidence retained (ADR-D6-17) |
| Standards touched | ISO/IEC 42001, EU AI Act (human oversight) |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 4, 12 |
| Repository paths | `src/pf_ft_ai/orchestration/` |
| Configuration | HIL boundary per workflow |
| Contracts / schemas | HIL evidence record |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D2-10, D3-07, D6-17 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Consequential actions require HIL | Workflow test |
| AC-02 | HIL decision recorded as evidence | Audit test |
| AC-03 | Model never overrides human decision | Test |
| AC-04 | Durable resume after HIL | Integration test (ADR-D2-10) |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | HIL pause/resume; decision latency |
| Alerting | Stuck HIL; missing evidence |
| Runbook | `docs/runbooks/hil.md` |
| Failure mode and degradation | If HIL unavailable, action stays paused (safe) |
| Rollback | Boundary config revert |
| Support model impact | Governance + ops |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| HIL governance + evidence | M | small | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | New consequential action type | Workflow change | Add to HIL boundary |
| RT-02 | Autonomous consequential action incident | Incident | CAR; widen HIL |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-28 |
| Specification sections | 20.PF-FT-AI-GOVERNANCE.md §68–§71 |
| Requirement IDs | GOV-HIL-* |
| Build phases | 4, 12 |
| Code paths | `src/pf_ft_ai/orchestration/` |
| Configuration | HIL boundary |
| Tests | HIL + evidence suites |
| Upstream ADRs | ADR-D2-10, D3-07, D1-02 |
| Downstream ADRs | ADR-D6-17 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Governance Lead | Initial decision recorded. |
