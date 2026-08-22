---
id: ADR-D7-06
title: Resilience patterns — retry, circuit breaker, bulkhead, fallback
domain: 7 Operations
ws_ref: [WS-31]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: SRE
contributors: [Backend Lead, AI Architecture Lead]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-05, ADR-D3-18, ADR-D2-11, ADR-D5-16, ADR-D5-17]
source_docs:
  - "MD files/6 Production/24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §54, §55, §56, §57, §58, §59"
build_phases: [2]
impacted_paths:
  - src/pf_ft_ai/infrastructure/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-06 — Resilience patterns — retry, circuit breaker, bulkhead, fallback

## 1. Summary

PFF AI will apply a **standard resilience toolkit — bounded retry with backoff (only for
retryable errors), circuit breakers per dependency, bulkhead isolation, timeouts and
fallback** — uniformly across all external dependencies (enterprise APIs, SLM, RAG, MCP,
Service Bus), driven by the error taxonomy (ADR-D7-05) and shared HTTP client (ADR-D5-16)
(doc 24 §54–§59). Retries never amplify incidents; a failing dependency is isolated, not
propagated.

## 2. Context and Problem Statement

Doc 24 §54–§58 retry classification/strategy/retryable/non-retryable/anti-pattern, §59
timeout strategy. Distributed dependencies fail; without disciplined resilience, failures
cascade (retry storms, thread exhaustion, timeouts stacking). This ADR fixes the
resilience patterns applied consistently (SLM-specific resilience is ADR-D3-18; workflow
idempotency/retry is ADR-D2-11 — this ADR is the shared toolkit).

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Bounded retry only on retryable errors | doc 24 §54–§57; ADR-D7-05 |
| DR-F-02 | Circuit breakers per dependency | doc 24 (breaker); ADR-D3-18 |
| DR-F-03 | Bulkhead isolation + timeouts | doc 24 §59 |
| DR-C-01 | No retry amplification | doc 24 §58; ADR-D5-17 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Dependencies fail independently | Shared-failure handling | Dependency review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Failure isolation (no cascade) | 30 | Availability | Blast radius |
| EC-02 | Incident-safety (no amplification) | 24 | Stability | Load under fault |
| EC-03 | Availability under partial failure | 18 | Keep serving | Success rate |
| EC-04 | Consistency (one toolkit) | 16 | Maintainability | Reuse |
| EC-05 | Overhead/latency | 12 | Cost | Added latency |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Full toolkit: bounded retry + backoff + breaker + bulkhead + timeout + fallback, taxonomy-driven

**Description.** A shared resilience layer (in ADR-D5-16 client + wrappers) applying all
patterns per dependency, using `retryable`/severity from ADR-D7-05; jittered backoff;
breakers; bulkheads (isolated pools/semaphores); layered timeouts; fallbacks.
**Strengths.** Isolates failures; incident-safe; available; consistent.
**Weaknesses.** Configuration per dependency.
**Cost / effort.** Medium.

### 5.2 Option B — Retry-only

**Description.** Just retries.
**Strengths.** Simple.
**Weaknesses.** No isolation/breaker → cascades + storms.
**Cost / effort.** Low; unsafe.

### 5.3 Option C — Timeouts + breakers (no bulkhead)

**Description.** Breakers + timeouts, shared pools.
**Strengths.** Good failure detection.
**Weaknesses.** One slow dependency exhausts shared resources (no bulkhead).
**Cost / effort.** Low-medium; partial.

### 5.4 Option D — Service-mesh resilience (mesh does retry/timeout/breaker)

**Description.** Delegate to a mesh.
**Strengths.** Cross-cutting; no app code.
**Weaknesses.** In-cluster only; external deps (SLM/enterprise) need app-level; mesh
retries can conflict with app retries.
**Cost / effort.** High platform; partial.

### 5.5 Option E — Full toolkit + adaptive (load-shedding / adaptive concurrency)

**Description.** Option A plus load-shedding and adaptive concurrency under stress.
**Strengths.** Best behaviour under overload.
**Weaknesses.** More complexity; tune carefully.
**Cost / effort.** Medium-high.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No resilience patterns | doc 24 §54–§59 |
| Unbounded retries | doc 24 §58 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 24 §54–§59 and ADR-D3-18/D5-16.

| Criterion | Weight | A: Full toolkit | B: Retry-only | C: Timeout+breaker | D: Mesh | E: Full+adaptive |
|---|---|---|---|---|---|---|
| EC-01 Isolation | 30 | 5 | 1 | 3 | 3 | 5 |
| EC-02 Incident-safety | 24 | 5 | 1 | 4 | 3 | 5 |
| EC-03 Availability | 18 | 5 | 3 | 4 | 3 | 5 |
| EC-04 Consistency | 16 | 5 | 4 | 4 | 3 | 5 |
| EC-05 Overhead | 12 | 4 | 5 | 4 | 3 | 3 |
| **Weighted total** | **100** | **488** | **236** | **374** | **306** | **486** |

Totals (×20): **A = 488**, **E = 486**, **C = 374**, **D = 306**, **B = 236**.

**Sensitivity.** A and E near-tied; adaptive load-shedding (E) is adopted where overload
is a real risk, layered on A. Mesh (D) helps in-cluster only. Retry-only (B) is unsafe.

## 7. Decision

**PFF AI will apply the full resilience toolkit — bounded jittered retry on retryable
errors, per-dependency circuit breakers, bulkhead isolation, layered timeouts and
fallback — uniformly, driven by the error taxonomy (ADR-D7-05) via the shared client
(ADR-D5-16) (Option A), adding adaptive load-shedding where overload risk warrants
(Option E enhancement).** SLM-specific resilience (ADR-D3-18) and workflow retry/
idempotency (ADR-D2-11) build on this toolkit. Retry-only (B) is rejected; mesh (D)
complements in-cluster only.

## 8. Architecture Detail

- Shared resilience wrappers in `src/pf_ft_ai/infrastructure/`: retry (retryable-only,
  jittered backoff, §55–§57), breakers per dependency, bulkheads (bounded pools/
  semaphores per dependency), timeouts (§59), fallbacks.
- Retryable/severity from ADR-D7-05; breakers/metrics feed alerting (ADR-D7-08) and
  autoscaling safety (ADR-D5-17); the retry anti-pattern (§58) is prevented (no retry on
  non-retryable/no nested retry storms).

## 9. Consequences

### 9.1 Positive
- Failures isolated, incident-safe, available under partial failure, consistent.
### 9.2 Negative
- Per-dependency configuration/tuning.
### 9.3 Neutral
- Foundation for D3-18 and D2-11.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity | Isolation + incident-safety | SRE |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Resilience never fabricates outcomes on failure |
| Precedence chain | Fallbacks stay below authoritative sources (ADR-D3-18) |
| Four-state separation | Resilience preserves state (suspend on critical) |
| Versioned artefacts | Resilience config versioned |
| Adam persona governs *how*, not *what* | Failures communicated honestly |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Retry storm | Med | High | H | Breakers + bounded backoff + no nested retries | SRE | Low |
| RSK-02 | One slow dep exhausts resources | Med | High | H | Bulkhead isolation | SRE | Low |
| RSK-03 | Stacked timeouts | Low | Med | M | Layered timeout budget | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Cascade failures in drills | 0 | > 0 | Chaos tests | Quarterly |
| QM-02 | Retry-amplification events | 0 | > 0 | Metrics | Continuous |
| QM-03 | Breaker trips per dependency | tracked | trend up | Metrics | Weekly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Bulkheads limit blast radius incl. some abuse |
| Data classification touched | Internal |
| Personal data / PII | N/A |
| Children's data and safeguarding | Critical flows suspend, not fabricate |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Failure/fallback events logged |
| Standards touched | ISO/IEC 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 2 |
| Repository paths | `src/pf_ft_ai/infrastructure/` |
| Configuration | Per-dependency retry/breaker/bulkhead/timeout |
| Contracts / schemas | Resilience config |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-05, D5-16, D3-18, D2-11 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Only retryable errors retried | Retry tests |
| AC-02 | Breakers trip + recover | Breaker tests |
| AC-03 | Bulkhead isolates a slow dependency | Chaos test |
| AC-04 | Timeouts layered, bounded | Timeout tests |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Breaker state, retry/timeout rates, bulkhead saturation |
| Alerting | Sustained breaker open; saturation |
| Runbook | `docs/runbooks/resilience.md` |
| Failure mode and degradation | Isolated dep failure → fallback/degrade |
| Rollback | Config revert |
| Support model impact | SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Resilience toolkit | M | negligible | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Overload incidents | Metrics | Add adaptive load-shedding (E) |
| RT-02 | Cascade in production | Incident | CAR; add bulkhead/breaker |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-31 |
| Specification sections | doc 24 §54–§59 |
| Requirement IDs | RESIL-* |
| Build phases | 2 |
| Code paths | `src/pf_ft_ai/infrastructure/` |
| Configuration | resilience config |
| Tests | chaos + resilience suites |
| Upstream ADRs | ADR-D7-05, D5-16 |
| Downstream ADRs | ADR-D3-18, D2-11, D5-17 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | SRE | Initial decision recorded. |
