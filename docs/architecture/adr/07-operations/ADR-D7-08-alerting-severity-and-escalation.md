---
id: ADR-D7-08
title: Alerting, severity model and on-call escalation
domain: 7 Operations
ws_ref: [WS-31]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: SRE
contributors: [Platform Engineer, Security Architect]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-07, ADR-D7-05, ADR-D7-17, ADR-D7-01, ADR-D7-16]
source_docs:
  - "MD files/6 Production/24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §49, §53"
  - "MD files/6 Production/28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §8, §9, §10, §11, §12, §13"
build_phases: [10]
impacted_paths:
  - docs/runbooks/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-08 — Alerting, severity model and on-call escalation

## 1. Summary

PFF AI will alert on **symptoms (SLO burn) and defined error severities**, mapped to a
**P1–P4 severity model** with an **on-call escalation path** (24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §49, §53; 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md
§8–§13). Alerts are actionable and tied to runbooks (ADR-D7-16); severity comes from the
error taxonomy (ADR-D7-05) and SLO burn (ADR-D7-07); noisy/non-actionable alerts are
prohibited.

## 2. Context and Problem Statement

24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §49 metrics, §53 error severity; 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §8–§13 operational severity (P1–P4) and
incident lifecycle. Alert fatigue from noisy, non-actionable alerts is a top operational
failure. This ADR fixes the alerting philosophy, severity model and escalation.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Alert on symptoms/SLO burn + severities | 24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §49, §53; ADR-D7-07 |
| DR-F-02 | P1–P4 severity + escalation | 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §8–§13 |
| DR-C-01 | Actionable alerts only (no noise) | SRE practice |
| DR-F-03 | Alerts link to runbooks | ADR-D7-16 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | On-call rota exists | Define support model (ADR-D7-16) | Ops setup |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Actionability (no noise) | 28 | Avoid fatigue | Alert precision |
| EC-02 | Coverage of real failures | 24 | Catch incidents | Detection rate |
| EC-03 | Severity/escalation clarity | 20 | Right response | P1–P4 mapping |
| EC-04 | Time-to-detect/respond | 16 | MTTR | Detect/ack time |
| EC-05 | Maintainability | 12 | Sustainable | Alert count |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Symptom/SLO-burn alerting + P1–P4 severity + on-call escalation + runbook links

**Description.** Alert primarily on SLO burn (ADR-D7-07) and defined error severities
(ADR-D7-05); map to P1–P4 (28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §9–§12); escalation path per severity; every alert
links a runbook (ADR-D7-16).
**Strengths.** Actionable, well-covered, clear response.
**Weaknesses.** SLO/alert tuning.
**Cost / effort.** Medium.

### 5.2 Option B — Threshold alerts on raw metrics (CPU/mem/etc.)

**Description.** Alert on resource thresholds.
**Strengths.** Simple.
**Weaknesses.** Cause-based, noisy; doesn't reflect user impact; fatigue.
**Cost / effort.** Low; noisy.

### 5.3 Option C — Log-error alerts (alert on ERROR logs)

**Description.** Page on error logs.
**Strengths.** Easy.
**Weaknesses.** Very noisy; many errors are handled; poor severity signal.
**Cost / effort.** Low; noisy.

### 5.4 Option D — Manual monitoring (dashboards, no automated alerts)

**Description.** Humans watch dashboards.
**Strengths.** No false pages.
**Weaknesses.** Misses off-hours; slow detection.
**Cost / effort.** Low; unreliable.

### 5.5 Option E — Symptom/SLO alerting + severity + escalation + alert deduplication/correlation

**Description.** Option A plus alert correlation/dedup (group related alerts, suppress
downstream) to cut noise during incidents.
**Strengths.** Best signal-to-noise during storms.
**Weaknesses.** Correlation config.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Alert on everything | Fatigue; non-actionable |
| No severity model | 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §8 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §49/§53 and 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §8–§13.

| Criterion | Weight | A: Symptom+severity | B: Raw thresholds | C: Log-error | D: Manual | E: A+correlation |
|---|---|---|---|---|---|---|
| EC-01 Actionability | 28 | 5 | 2 | 2 | 3 | 5 |
| EC-02 Coverage | 24 | 5 | 3 | 3 | 2 | 5 |
| EC-03 Severity clarity | 20 | 5 | 3 | 2 | 3 | 5 |
| EC-04 Time-to-detect | 16 | 5 | 4 | 4 | 1 | 5 |
| EC-05 Maintainability | 12 | 4 | 3 | 3 | 4 | 4 |
| **Weighted total** | **100** | **488** | **300** | **280** | **244** | **496** |

Totals (×20): **E = 496**, **A = 488**, **B = 300**, **C = 280**, **D = 244**.

**Sensitivity.** E (A + alert correlation/dedup) edges A by taming alert storms during
incidents. Adopted. Raw-threshold (B) and log-error (C) alerting are noisy; manual (D)
misses off-hours.

## 7. Decision

**PFF AI will alert primarily on SLO burn and defined error severities, mapped to a
P1–P4 severity model with a per-severity on-call escalation path, every alert linking a
runbook, and alert correlation/deduplication to cut incident noise (Option E).** Raw
resource thresholds are secondary (capacity) signals only; log-error paging (C) and
manual-only (D) are rejected.

## 8. Architecture Detail

- Alert rules in Azure Monitor (ADR-D7-01) on SLO burn (ADR-D7-07) + severity from the
  error catalogue (ADR-D7-05); P1–P4 mapping (28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §9–§12); escalation to on-call per
  severity (ADR-D7-16); each alert carries a runbook link.
- Correlation/dedup groups related alerts; security alerts (e.g. ADR-D6-08/D6-12) route
  to security on-call; incident lifecycle per 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §13 and ADR-D7-17.

## 9. Consequences

### 9.1 Positive
- Actionable, well-covered, low-noise alerting with clear escalation.
### 9.2 Negative
- Alert/correlation tuning.
### 9.3 Neutral
- Feeds incident management (D7-17).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Alert-on-everything coverage feel | Actionability + low fatigue | SRE |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Ops alerting; no business authority |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | Alert rules as code |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Alert fatigue | Med | Med | M | Symptom-based + correlation (E) | SRE | Low |
| RSK-02 | Missed real incident | Low | High | M | SLO-burn + severity coverage | SRE | Low |
| RSK-03 | Slow escalation | Low | High | M | Defined escalation + on-call (ADR-D7-16) | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Alert actionability (acted-on rate) | high | falling | Alert reviews | Monthly |
| QM-02 | Incidents caught by alert (not user) | ≥ target | falling | Incident data | Monthly |
| QM-03 | Time-to-detect / time-to-ack | within target | breach | Alerting | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Security alerts routed to security on-call |
| Data classification touched | Internal |
| Personal data / PII | Alerts carry no PII |
| Children's data and safeguarding | Safeguarding-relevant incidents escalated |
| UK GDPR lawful basis and rights impact | Breach-alert supports 72h notification |
| Audit and evidential requirements | Alert/incident records |
| Standards touched | ISO/IEC 27001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 10 |
| Repository paths | `docs/runbooks/` + alert config |
| Configuration | Alert rules; severity map; escalation; correlation |
| Contracts / schemas | Alert→runbook links |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-07, D7-05, D7-16, D7-17 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Alerts are symptom/severity-based | Alert review |
| AC-02 | P1–P4 mapping + escalation defined | Config review |
| AC-03 | Every alert links a runbook | Alert audit |
| AC-04 | Correlation reduces storm noise | Incident drill |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Alert volume/actionability |
| Alerting | This ADR defines it |
| Runbook | `docs/runbooks/alerting.md` |
| Failure mode and degradation | Alerting-system failure has a heartbeat check |
| Rollback | Alert config revert |
| Support model impact | On-call (ADR-D7-16) |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Alerting/paging tooling | S | small | Azure Monitor + paging |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Fatigue/false pages high | QM-01 | Tune/correlate/remove alerts |
| RT-02 | Missed incident | Post-incident | Add coverage |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-31 |
| Specification sections | 24.PFF-FA-AI-OBSERVABILITY-RESILIENCE.md §49, §53; 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §8–§13 |
| Requirement IDs | ALERT-* |
| Build phases | 10 |
| Code paths | alert config + runbooks |
| Configuration | alert rules/severity |
| Tests | alert + escalation drills |
| Upstream ADRs | ADR-D7-07, D7-05 |
| Downstream ADRs | ADR-D7-16, D7-17 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | SRE | Initial decision recorded. |
