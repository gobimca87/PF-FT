---
id: ADR-D5-17
title: Scalability and autoscaling model
domain: 5 Technology
ws_ref: [WS-26]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: SRE
contributors: [Platform Engineer, AI Architecture Lead, FinOps]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-08, ADR-D5-11, ADR-D2-16, ADR-D5-18, ADR-D7-06]
source_docs:
  - "MD files/6 Production/25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §51, §52, §53"
  - "MD files/6 Production/26.PFF-FA-AI-PERFORMANCE-COST.md §60, §61, §62, §63, §64, §65, §66, §67, §68, §69"
build_phases: [7, 20]
impacted_paths:
  - deploy/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-17 — Scalability and autoscaling model

## 1. Summary

PFF AI will scale **horizontally** with **workload-appropriate autoscaling signals**:
HPA on request concurrency/CPU for the API tier, queue-depth-based scaling for Service
Bus workers, and inference-utilisation-based scaling for the GPU tier — all with
**failure-mode-aware capacity** to avoid retry-amplification collapse (25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §51–§53;
26.PFF-FA-AI-PERFORMANCE-COST.md §60–§69). No single global signal; each tier scales on what actually drives its
load.

## 2. Context and Problem Statement

25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §51–§53 define horizontal scaling, autoscaling and Service-Bus worker scaling;
26.PFF-FA-AI-PERFORMANCE-COST.md §60–§69 define throughput, concurrency, capacity planning, peak/failure-mode
capacity, retry amplification and autoscaling safety. Scaling on the wrong signal
(e.g. CPU for an I/O-bound API, or ignoring queue depth for workers) under- or
over-provisions; ignoring failure-mode capacity lets a dependency outage trigger a
retry storm that autoscaling amplifies. This ADR fixes the scaling model per tier.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Horizontal autoscaling per tier | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §51–§52 |
| DR-F-02 | Queue-depth scaling for SB workers | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §53; 26.PFF-FA-AI-PERFORMANCE-COST.md §59 |
| DR-F-03 | GPU scaling on inference utilisation | ADR-D5-11; 15.PFF-FA-AI-SLM.md §79 |
| DR-C-01 | Failure-mode capacity; no retry amplification | 26.PFF-FA-AI-PERFORMANCE-COST.md §66–§67, §69 |
| DR-N-01 | Cost efficiency | 26.PFF-FA-AI-PERFORMANCE-COST.md §63–§65 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Workload is horizontally scalable (stateless API) | Address stateful bottlenecks | Load test |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Signal appropriateness per tier | 26 | Right scaling driver | Signal fit |
| EC-02 | Failure-mode safety (no amplification) | 22 | Avoid collapse | Behaviour under fault |
| EC-03 | Responsiveness to load | 18 | Meet SLOs | Scale-up lag |
| EC-04 | Cost efficiency | 18 | Spend | £ vs load |
| EC-05 | Simplicity/operability | 16 | Tune/run | Config complexity |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Per-tier horizontal autoscaling on workload-appropriate signals + failure-mode capacity

**Description.** API: HPA on concurrency/CPU/RPS; workers: KEDA on Service Bus queue
depth; GPU: scale on inference utilisation/queue; headroom + breakers for failure-mode
capacity (26.PFF-FA-AI-PERFORMANCE-COST.md §66–§69).
**Strengths.** Right signal per tier; safe under fault; cost-efficient.
**Weaknesses.** Multiple autoscalers to tune.
**Cost / effort.** Medium.

### 5.2 Option B — CPU-only HPA everywhere

**Description.** Scale all tiers on CPU.
**Strengths.** Simplest.
**Weaknesses.** CPU is a poor signal for I/O-bound API and queue-driven workers; GPU
mis-scaled; over/under-provision.
**Cost / effort.** Low; ineffective.

### 5.3 Option C — Fixed capacity (no autoscaling)

**Description.** Statically sized.
**Strengths.** Predictable cost; simple.
**Weaknesses.** Wastes money off-peak; can't absorb peaks; poor for variable
conversational load.
**Cost / effort.** Low; inflexible.

### 5.4 Option D — Vertical scaling (bigger pods/nodes)

**Description.** Scale up, not out.
**Strengths.** Simple for some bottlenecks.
**Weaknesses.** Ceiling per node; no HA benefit; restarts on resize; not for stateless
horizontal workloads.
**Cost / effort.** Low; limited.

### 5.5 Option E — Predictive/scheduled autoscaling

**Description.** Scale on forecast/schedule (e.g. known peaks).
**Strengths.** Pre-warms for predictable peaks; avoids cold-start lag.
**Weaknesses.** Needs reliable forecasts; complements reactive scaling rather than
replacing it.
**Cost / effort.** Medium; layer on A later.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Autoscale on error rate | Amplifies incidents (26.PFF-FA-AI-PERFORMANCE-COST.md §67) |
| Scale-to-zero for the API | Cold-start hurts conversational latency |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §51–§53 and 26.PFF-FA-AI-PERFORMANCE-COST.md
§60–§69.

| Criterion | Weight | A: Per-tier signals | B: CPU-only | C: Fixed | D: Vertical | E: Predictive |
|---|---|---|---|---|---|---|
| EC-01 Signal fit | 26 | 5 | 2 | 1 | 2 | 4 |
| EC-02 Failure-mode safety | 22 | 5 | 3 | 4 | 3 | 4 |
| EC-03 Responsiveness | 18 | 5 | 3 | 1 | 2 | 5 |
| EC-04 Cost efficiency | 18 | 5 | 3 | 2 | 3 | 4 |
| EC-05 Simplicity | 16 | 3 | 5 | 5 | 4 | 3 |
| **Weighted total** | **100** | **468** | **312** | **252** | **278** | **408** |

Totals (×20): **A = 468**, **E = 408**, **B = 312**, **D = 278**, **C = 252**.

**Sensitivity.** A leads; predictive/scheduled (E) is a strong *complement* to add for
known peaks (RT-01), layered on A's reactive scaling. CPU-only (B) and fixed (C) are
too blunt for variable conversational + queue + GPU workloads.

## 7. Decision

**PFF AI will scale horizontally with per-tier, workload-appropriate autoscaling — HPA
on concurrency/CPU for the API, queue-depth (KEDA) for Service Bus workers, and
inference-utilisation for the GPU tier — with failure-mode capacity headroom and
circuit breakers to prevent retry amplification (Option A).** Predictive/scheduled
scaling (E) may be layered on for known peaks. CPU-only (B), fixed (C) and vertical (D)
are rejected as primary strategies.

**Status rationale.** `Accepted` — 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §51–§53 and 26.PFF-FA-AI-PERFORMANCE-COST.md §60–§69 govern this.

## 8. Architecture Detail

- API HPA on RPS/concurrency (and CPU as guard); workers scaled by KEDA on Service Bus
  queue length (25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §53; ADR-D2-16); GPU pool scaled on utilisation/queue (ADR-D5-11;
  15.PFF-FA-AI-SLM.md §79) with warm-up (15.PFF-FA-AI-SLM.md §80).
- Failure-mode capacity (26.PFF-FA-AI-PERFORMANCE-COST.md §66): headroom sized for a dependency slowdown; breakers
  (ADR-D7-06/D3-18) stop retry storms; autoscaling safety limits (26.PFF-FA-AI-PERFORMANCE-COST.md §69) cap
  scale velocity/max replicas.
- Latency budget (ADR-D5-18) informs target concurrency per replica.

## 9. Consequences

### 9.1 Positive
- Right-sized, responsive, cost-efficient scaling that stays safe under fault.
### 9.2 Negative
- Multiple autoscalers to tune.
### 9.3 Neutral
- Interlocks with GPU pool (D5-11) and resilience (D7-06).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Single-signal simplicity | Correct per-tier scaling + safety | SRE |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Scaling is infra; no business authority |
| Precedence chain | N/A |
| Four-state separation | Stateless horizontal scaling preserves state stores |
| Versioned artefacts | Autoscaler config versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Retry storm amplified by autoscaling | Med | High | H | Breakers + error-rate excluded as signal (§67, §69) | SRE | Low |
| RSK-02 | Scale-up lag misses peak | Med | Med | M | Headroom + predictive scaling (E) | SRE | Low |
| RSK-03 | GPU over-scale cost | Med | Med | M | Utilisation targets + max replicas | FinOps | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | SLO adherence under peak | met | breach | App Insights | Continuous |
| QM-02 | Scale-up lag | within budget | slow | HPA/KEDA metrics | Weekly |
| QM-03 | Retry-amplification events | 0 | > 0 | Metrics | Continuous |
| QM-04 | Cost per peak-hour | ≤ model | over | FinOps | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Autoscaling can absorb some load spikes (not a DDoS control) |
| Data classification touched | Internal |
| Personal data / PII | N/A |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Scaling events logged |
| Standards touched | ISO/IEC 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 7 (API/workers), 20 (GPU) |
| Repository paths | `deploy/` (HPA/KEDA) |
| Configuration | Autoscaler signals/limits |
| Contracts / schemas | N/A |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-08, D5-11, D2-16, D5-18, D7-06 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Each tier scales on its appropriate signal | Config review |
| AC-02 | No autoscaling on error rate | Config check |
| AC-03 | Failure-mode headroom sized | Load/chaos test |
| AC-04 | Max replicas/velocity capped | Config |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | HPA/KEDA/GPU scaling metrics; queue depth |
| Alerting | SLO breach; scale limits hit |
| Runbook | `docs/runbooks/scaling.md` |
| Failure mode and degradation | Breakers + capped scaling prevent collapse |
| Rollback | Autoscaler config revert |
| Support model impact | SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Autoscaling infra (KEDA etc.) | setup | none | OSS |
| Elastic compute | — | load-based | Azure pricing |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Predictable peaks cause cold-start lag | QM-02 | Add predictive/scheduled scaling (E) |
| RT-02 | Retry-amplification incident | Incident | CAR; tighten breakers/limits |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-26 Performance |
| Specification sections | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §51–§53; 26.PFF-FA-AI-PERFORMANCE-COST.md §60–§69 |
| Requirement IDs | SCALE-* |
| Build phases | 7, 20 |
| Code paths | `deploy/` |
| Configuration | HPA/KEDA/GPU autoscaler |
| Tests | load/chaos suites |
| Upstream ADRs | ADR-D5-08, D5-11, D2-16 |
| Downstream ADRs | ADR-D5-18, D7-06 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | SRE | Initial decision recorded. |
