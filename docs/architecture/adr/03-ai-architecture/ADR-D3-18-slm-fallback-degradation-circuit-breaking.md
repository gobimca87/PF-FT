---
id: ADR-D3-18
title: SLM fallback, degradation and circuit-breaking
domain: 3 AI
ws_ref: [WS-16]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [ML Engineer, SRE, Platform Engineer]
reviewers: [Principal Architect, Security Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-13, ADR-D3-14, ADR-D3-15, ADR-D7-06, ADR-D2-11]
source_docs:
  - "MD files/4 AI/15.PF-FT-AI-SLM.md §61, §62, §63, §64, §65, §66, §67, §68, §69, §163, §168"
build_phases: [6]
impacted_paths:
  - src/pf_ft_ai/slm/
classification: Internal
review_due: 2027-08-22
---

# ADR-D3-18 — SLM fallback, degradation and circuit-breaking

## 1. Summary

PFF AI will make SLM resilience explicit and **never silent**: ordered fallback
across compatible models/providers, per-provider circuit breakers, layered timeouts,
bounded retries with backoff, and a defined degraded mode when no model is available
(doc 15 §61–§69, §163, §168). A fallback or degradation is always logged and, where
it affects the user, communicated honestly by Adam — the platform never pretends a
degraded answer is a normal one.

## 2. Context and Problem Statement

Doc 15 §62–§64 require fallback that is compatible and **not silent**; §65–§69 define
retry, backoff, circuit breaker, timeout layers and cancellation; §163/§168 define
degraded mode and the failure principle. Model endpoints fail, throttle and slow
down. Without an explicit policy, a provider outage becomes a user-facing hang or a
silently worse answer, and retries can amplify an incident. This ADR fixes the
resilience behaviour of the SLM path.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Fallback across compatible models/providers | doc 15 §62–§63 |
| DR-F-02 | Fallback/degradation never silent | doc 15 §64; CLAUDE.md §Adam 7 |
| DR-F-03 | Circuit-break failing providers | doc 15 §67 |
| DR-N-01 | Bounded latency via layered timeouts | doc 15 §68 |
| DR-N-02 | Retries must not amplify incidents | doc 15 §65–§66; ADR-D2-11 |
| DR-C-01 | Degraded answers communicated honestly | CLAUDE.md §Adam 7 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | A compatible fallback model exists | Degrade to non-generative response | Registry check |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Availability under provider failure | 26 | Core goal | Success rate during outage |
| EC-02 | Incident-safety (no amplification) | 20 | Retries/breakers must protect | Load during failure |
| EC-03 | Honesty of degradation | 18 | Golden rule / persona | Degraded flagged? |
| EC-04 | Latency bound | 14 | No hangs | p99 under failure |
| EC-05 | Correctness preservation | 12 | Fallback must be compatible | Output validity on fallback |
| EC-06 | Complexity/ops | 10 | Maintainability | Concepts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Ordered compatible fallback + circuit breaker + bounded retry/backoff + layered timeouts + honest degraded mode

**Description.** The full pattern from doc 15 §61–§69: try primary; on failure/timeout
fall back to next compatible model (per registry capabilities, ADR-D3-15); breakers
trip per provider; retries are bounded with jittered backoff; layered timeouts
(per-call, per-attempt, overall); if all fail, enter degraded mode and tell the user.
**Strengths.** Highest availability with incident-safety and honesty.
**Weaknesses.** Most moving parts.
**Cost / effort.** Medium.

### 5.2 Option B — Retry-only (no fallback, no breaker)

**Description.** Retry the same provider on failure.
**Strengths.** Simplest.
**Weaknesses.** No help in a sustained outage; retries amplify load; hangs.
**Cost / effort.** Low, inadequate.

### 5.3 Option C — Fallback without circuit breaker

**Description.** Fall back but keep hammering failing providers.
**Strengths.** Some availability.
**Weaknesses.** No incident-safety; keeps calling a down provider; slow.
**Cost / effort.** Low-medium; risky.

### 5.4 Option D — Fail-fast, no fallback, surface error

**Description.** On any failure, return an error immediately.
**Strengths.** Simple; honest; incident-safe.
**Weaknesses.** Poor availability; every blip is user-visible; no graceful path.
**Cost / effort.** Low; poor UX.

### 5.5 Option E — Cache/last-known-good fallback for repeatable outputs

**Description.** For idempotent, cacheable generations, serve a cached response when
live inference fails.
**Strengths.** Availability for repeatable prompts; cheap.
**Weaknesses.** Only applies to cacheable, non-personalised outputs; stale risk;
must be flagged. A complement, not a whole strategy.
**Cost / effort.** Low; narrow applicability.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Silent fallback to a weaker model | DR-F-02 / CLAUDE.md §Adam 7 |
| Unbounded retries | ADR-D2-11 — incident amplification |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 15 §61–§69/§163/§168 and
the resilience patterns of ADR-D7-06.

| Criterion | Weight | A: Full pattern | B: Retry-only | C: Fallback no breaker | D: Fail-fast | E: Cache fallback |
|---|---|---|---|---|---|---|
| EC-01 Availability | 26 | 5 | 2 | 4 | 1 | 3 |
| EC-02 Incident-safety | 20 | 5 | 2 | 2 | 5 | 4 |
| EC-03 Honesty | 18 | 5 | 3 | 3 | 5 | 4 |
| EC-04 Latency bound | 14 | 5 | 2 | 3 | 5 | 4 |
| EC-05 Correctness | 12 | 4 | 4 | 4 | 5 | 3 |
| EC-06 Complexity | 10 | 3 | 5 | 4 | 5 | 4 |
| **Weighted total** | **100** | **466** | **272** | **322** | **388** | **362** |

Totals (×20): **A = 466**, **D = 388**, **E = 362**, **C = 322**, **B = 272**.

**Sensitivity.** A leads by a wide margin. D scores well on safety/honesty but poorly
on availability — acceptable only as A's *final* stage. E is adopted as a
*complement* for cacheable outputs. B/C rejected.

## 7. Decision

**PFF AI will implement the full resilience pattern (Option A):** ordered fallback
across compatible models/providers (capabilities from ADR-D3-15), per-provider
circuit breakers, bounded retries with jittered backoff, layered timeouts and
cancellation, terminating in an honest degraded mode when no model is available.
Cache/last-known-good fallback (E) is used only for cacheable, non-personalised
outputs and is flagged as such. Every fallback and degradation is logged and, when
user-affecting, communicated plainly by Adam (never celebrated, never disguised).
B/C/D rejected as standalone strategies.

**Status rationale.** `Accepted` — doc 15 §61–§69 mandate this behaviour.

## 8. Architecture Detail

- Implemented in the SLM abstraction (ADR-D3-14): a resilience wrapper around
  provider adapters using the shared HTTP client's retry/timeout (ADR-D5-16) and a
  circuit-breaker per provider (doc 15 §67).
- Fallback order and compatibility from the model registry (ADR-D3-15); only
  capability-compatible models are fallback targets (§63).
- Timeout layers (§68): per-attempt, per-call, and an overall budget aligned to the
  latency budget (ADR-D5-18); cancellation on client disconnect (§69).
- Degraded mode (§163, §168): return a safe, honest message; for HIL/critical flows,
  suspend rather than fabricate (ADR-D2-10). Degradation events emit metrics/alerts.

## 9. Consequences

### 9.1 Positive
- High availability with incident-safety and user honesty.
### 9.2 Negative
- More components (breakers, timeouts, fallback order) to configure and test.
### 9.3 Neutral
- Shares breaker/retry infrastructure with other integrations (ADR-D7-06).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity | Availability + incident-safety + honesty | AI Arch Lead, SRE |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Degradation never fabricates a business outcome |
| Precedence chain | Fallback/cached output still ranks below authoritative sources |
| Four-state separation | Resilience is compute behaviour; state preserved (suspend on critical) |
| Versioned artefacts | Fallback config versioned |
| Adam persona governs *how*, not *what* | Degraded state told honestly; no "GOAL!" on failure |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Fallback model changes output shape | Med | Med | M | Compatibility check + validation (ADR-D3-17) | ML Eng | Low |
| RSK-02 | Retry storm during outage | Med | High | H | Breakers + bounded backoff (ADR-D2-11) | SRE | Low |
| RSK-03 | Silent degradation slips through | Low | High | M | Mandatory degradation flag + tests | Security Architect | Low |
| RSK-04 | Stale cache served as fresh | Low | Med | M | Flag + TTL; only cacheable outputs | ML Eng | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | SLM success rate incl. fallback | ≥ 99.5% | < 99% | Langfuse/App Insights | Continuous |
| QM-02 | p99 latency under single-provider failure | within budget | breach | App Insights | Continuous |
| QM-03 | Degradations flagged to user | 100% | < 100% | Traces | Continuous |
| QM-04 | Breaker trips per provider | tracked | rising trend | Metrics | Weekly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None new; breakers reduce cascade risk |
| Data classification touched | Internal |
| Personal data / PII | Fallback stays within same data-boundary policy (ADR-D6-07) |
| Children's data and safeguarding | Critical flows suspend rather than fabricate |
| UK GDPR lawful basis and rights impact | None |
| Audit and evidential requirements | Fallback/degradation events audited |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 |
| Repository paths | `src/pf_ft_ai/slm/` |
| Configuration | Fallback order, breaker/timeout/retry settings |
| Contracts / schemas | Degradation flag in `SLMResponse` |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-14, ADR-D3-15, ADR-D5-16, ADR-D7-06 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Primary failure → compatible fallback used | Fault-injection test |
| AC-02 | Failing provider trips breaker | Breaker unit test |
| AC-03 | No compatible model → honest degraded response/suspend | Test |
| AC-04 | Every degradation logged + flagged | Trace assertion |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Success rate, breaker state, fallback rate, degradation count |
| Alerting | Sustained breaker open; degradation spike |
| Runbook | `docs/runbooks/slm.md` — provider outage |
| Failure mode and degradation | Defined degraded mode (§163, §168) |
| Rollback | Config revert of fallback settings |
| Support model impact | SRE + ML platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Resilience wrapper | M | negligible | Build |
| Fallback calls | — | small | Only during failures |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Success rate < 99% sustained | QM-01 | Add provider/model or capacity |
| RT-02 | Retry storm observed | QM-04 | Tighten breaker/backoff |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-16 |
| Specification sections | doc 15 §61–§69, §163, §168 |
| Requirement IDs | SLM-RESIL-* |
| Build phases | 6 |
| Code paths | `src/pf_ft_ai/slm/` |
| Configuration | fallback/breaker/timeout config |
| Tests | fault-injection + breaker suites |
| Upstream ADRs | ADR-D3-14, ADR-D3-15 |
| Downstream ADRs | ADR-D7-06 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
