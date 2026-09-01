---
id: ADR-D7-07
title: SLI/SLO definition and error-budget policy
domain: 7 Operations
ws_ref: [WS-31]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: SRE
contributors: [Principal Architect, Product Owner, AI Architecture Lead]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-01, ADR-D5-18, ADR-D7-08, ADR-D8-05, ADR-D7-10]
source_docs:
  - "MD files/6 Production/24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §5, §6, §49, §50"
  - "MD files/6 Production/26.PF-FT-AI-PERFORMANCE-COST.md §5, §8"
build_phases: [10]
impacted_paths:
  - docs/runbooks/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-07 — SLI/SLO definition and error-budget policy

## 1. Summary

PFF AI will define **SLIs** (availability, latency per ADR-D5-18, correctness/answer
success, cost) and **SLOs** with an **error-budget policy** that governs the balance
between shipping and reliability: when the budget is healthy the team ships; when it is
exhausted, change slows and reliability work takes priority (24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §5–§6, §49–§50; 26.PF-FT-AI-PERFORMANCE-COST.md §5, §8). SLOs are measured from the observability stack (ADR-D7-01) and drive alerting
(ADR-D7-08).

## 2. Context and Problem Statement

24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §5–§6 pillars/four-questions, §49–§50 metrics/AI-quality-metrics; 26.PF-FT-AI-PERFORMANCE-COST.md §5/§8
performance objectives/latency budget. Without SLOs and an error-budget policy, there's
no shared definition of "reliable enough" and no principled way to decide when to slow
change. This ADR fixes SLIs/SLOs and the error-budget policy.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Define SLIs (avail/latency/correctness/cost) | 24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §49–§50; 26.PF-FT-AI-PERFORMANCE-COST.md §5 |
| DR-F-02 | SLO targets + error budget | 26.PF-FT-AI-PERFORMANCE-COST.md §8 |
| DR-F-03 | Budget policy governs ship vs reliability | SRE practice |
| DR-F-04 | SLOs drive alerting | ADR-D7-08 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | AI correctness measurable as an SLI | Use proxy metrics (eval) | ADR-D7-13 |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | User-relevance of SLIs | 28 | Measure what matters | SLI fit |
| EC-02 | Actionability (budget policy) | 24 | Drives decisions | Policy defined |
| EC-03 | Measurability from telemetry | 20 | Real signals | Data source |
| EC-04 | Includes AI-quality + cost | 16 | Beyond uptime | AI/cost SLIs |
| EC-05 | Simplicity | 12 | Usable | # SLOs |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — SLIs (avail/latency/correctness/cost) + SLOs + error-budget policy

**Description.** Define user-centric SLIs; set SLO targets; an error-budget policy that
governs change velocity vs reliability; measured from ADR-D7-01; alerts on burn (D7-08).
**Strengths.** Principled, actionable, user-centric, includes AI-quality + cost.
**Weaknesses.** Correctness SLI needs eval proxies.
**Cost / effort.** Medium.

### 5.2 Option B — Availability + latency SLOs only

**Description.** Classic uptime/latency SLOs.
**Strengths.** Simple, standard.
**Weaknesses.** Ignores AI correctness + cost — core to this platform.
**Cost / effort.** Low; incomplete.

### 5.3 Option C — Uptime monitoring only (no SLOs/budget)

**Description.** Just alert on down.
**Strengths.** Minimal.
**Weaknesses.** No reliability targets or ship/slow policy.
**Cost / effort.** Low; weak.

### 5.4 Option D — Business-KPI-only targets (containment/CSAT)

**Description.** Track only business outcomes.
**Strengths.** Business-aligned.
**Weaknesses.** Not operational; can't drive engineering reliability decisions. (Business
KPIs live in ADR-D8-05.)
**Cost / effort.** Low; wrong layer.

### 5.5 Option E — SLIs/SLOs + error budget + multi-window burn-rate alerting

**Description.** Option A with multi-window, multi-burn-rate alerting (fast + slow burn)
for precise, low-noise alerts.
**Strengths.** Best alert signal-to-noise; catches fast + slow degradation.
**Weaknesses.** More alert config.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No reliability targets | 26.PF-FT-AI-PERFORMANCE-COST.md §5 |
| Vanity metrics as SLIs | Not user-relevant |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §49–§50, 26.PF-FT-AI-PERFORMANCE-COST.md §5/§8 and SRE
error-budget practice.

| Criterion | Weight | A: SLIs+SLO+budget | B: Avail+latency | C: Uptime-only | D: Business-KPI-only | E: A+burn-rate alerts |
|---|---|---|---|---|---|---|
| EC-01 SLI relevance | 28 | 5 | 3 | 2 | 3 | 5 |
| EC-02 Actionability | 24 | 5 | 3 | 1 | 2 | 5 |
| EC-03 Measurability | 20 | 4 | 5 | 5 | 3 | 4 |
| EC-04 AI-quality+cost | 16 | 5 | 2 | 1 | 3 | 5 |
| EC-05 Simplicity | 12 | 4 | 5 | 5 | 4 | 3 |
| **Weighted total** | **100** | **464** | **352** | **288** | **288** | **468** |

Totals (×20): **E = 468**, **A = 464**, **B = 352**, **C = 288**, **D = 288**.

**Sensitivity.** E (A + multi-window burn-rate alerting) edges A on alert precision.
Adopted. Availability+latency-only (B) omits the AI-correctness and cost dimensions
central to this platform.

## 7. Decision

**PFF AI will define user-centric SLIs (availability, latency per ADR-D5-18, answer
correctness/success, cost per interaction) with SLO targets, an error-budget policy
governing change velocity vs reliability work, and multi-window burn-rate alerting
(Option E).** Correctness SLIs use eval proxies (ADR-D7-13). Availability+latency-only
(B), uptime-only (C) and business-KPI-only (D, which belongs to ADR-D8-05) are rejected.

## 8. Architecture Detail

- SLIs computed from ADR-D7-01 telemetry + eval (ADR-D7-13); SLOs documented per service;
  error-budget tracked; burn-rate alerts (fast + slow windows) route via ADR-D7-08.
- Budget policy: healthy budget → normal shipping; exhausted → change freeze on the
  affected area + reliability focus (ties to change governance ADR-D6-15 and CD D7-10).
- Cost SLI ties to ADR-D8-01 unit economics.

## 9. Consequences

### 9.1 Positive
- Shared reliability definition; principled ship/slow decisions; AI + cost covered.
### 9.2 Negative
- SLO/budget/alert maintenance.
### 9.3 Neutral
- Bridges ops (D7) and business value (D8-05).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of uptime-only | Actionable, complete reliability | SRE |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | SLIs measure the AI layer; no business authority |
| Precedence chain | Correctness SLI reflects authoritative-truth fidelity |
| Four-state separation | N/A |
| Versioned artefacts | SLO/budget config versioned |
| Adam persona governs *how*, not *what* | Persona-adherence is a quality signal (D8-05) |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Correctness SLI unmeasurable | Med | Med | M | Eval proxies (ADR-D7-13) | AI Arch Lead | Low |
| RSK-02 | Budget policy ignored | Med | Med | M | Tie to change governance (ADR-D6-15) | SRE | Low |
| RSK-03 | Alert noise | Med | Med | M | Multi-window burn-rate (E) | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | SLOs met | ≥ target | breach | Telemetry/eval | Continuous |
| QM-02 | Error budget burn | within | fast/slow burn | Burn-rate alerts | Continuous |
| QM-03 | SLIs defined per service | 100% | < 100% | SLO catalogue | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None |
| Data classification touched | Internal metrics |
| Personal data / PII | None |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | SLO reports retained |
| Standards touched | ISO 9001, ISO/IEC 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 10 |
| Repository paths | `docs/runbooks/` (SLO catalogue) + alert config |
| Configuration | SLIs/SLOs/budget/burn-rate alerts |
| Contracts / schemas | SLO definitions |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-01, D5-18, D7-13, D7-08 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | SLIs/SLOs defined per service | SLO catalogue review |
| AC-02 | Error-budget policy documented + applied | Governance check |
| AC-03 | Burn-rate alerts fire correctly | Alert test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | SLO dashboards; budget burn |
| Alerting | Burn-rate alerts (ADR-D7-08) |
| Runbook | `docs/runbooks/slo.md` |
| Failure mode and degradation | Budget exhausted → slow change |
| Rollback | N/A |
| Support model impact | SRE + product |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| SLO tooling/dashboards | S | small | Reuses ADR-D7-01 |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | SLOs chronically breached | QM-01 | Reliability investment / re-set targets |
| RT-02 | Alert noise high | QM/feedback | Tune burn-rate windows |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-31 |
| Specification sections | 24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §5–§6, §49–§50; 26.PF-FT-AI-PERFORMANCE-COST.md §5, §8 |
| Requirement IDs | SLO-* |
| Build phases | 10 |
| Code paths | SLO catalogue + alerts |
| Configuration | SLIs/SLOs/budget |
| Tests | alert tests |
| Upstream ADRs | ADR-D7-01, D5-18 |
| Downstream ADRs | ADR-D7-08, D8-05 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | SRE | Initial decision recorded. |
