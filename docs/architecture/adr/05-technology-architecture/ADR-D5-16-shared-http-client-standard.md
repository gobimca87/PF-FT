---
id: ADR-D5-16
title: Shared HTTP client standard — pooling, timeout, retry, tracing
domain: 5 Technology
ws_ref: [WS-25]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Backend Lead
contributors: [Platform Engineer, SRE, AI Architecture Lead]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D2-13, ADR-D3-18, ADR-D7-06, ADR-D7-03, ADR-D4-04]
source_docs:
  - "MD files/6 Production/25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §63"
  - "MD files/6 Production/27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §24, §25, §26"
  - "MD files/6 Production/26.PF-FT-AI-PERFORMANCE-COST.md §15"
build_phases: [2]
impacted_paths:
  - src/pf_ft_ai/infrastructure/http/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-16 — Shared HTTP client standard — pooling, timeout, retry, tracing

## 1. Summary

PFF AI will route all outbound HTTP through a **single shared async client** (httpx
`AsyncClient`) with **connection pooling, mandatory timeouts, bounded retries with
backoff, circuit-breaking, correlation-ID propagation and tracing** — no ad-hoc clients
or blocking calls in async paths (CLAUDE.md; 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §24–§26; 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §63; 26.PF-FT-AI-PERFORMANCE-COST.md §15).
Enterprise API, SLM, embedding, MCP and RAG calls all use it.

## 2. Context and Problem Statement

CLAUDE.md mandates "a shared HTTP client with pooling/timeout/retry/tracing" and "never
a blocking call inside an async path"; 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §24–§26 async/blocking/HTTP-client
standards; 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §63 HTTP client infrastructure; 26.PF-FT-AI-PERFORMANCE-COST.md §15 HTTP client performance.
Scattered, unconfigured clients cause connection exhaustion, hung requests (no
timeout), retry storms and missing traces. This ADR fixes the shared client standard.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | One shared pooled async client | CLAUDE.md; 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §63 |
| DR-F-02 | Mandatory timeouts; no blocking calls | CLAUDE.md; 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §25 |
| DR-F-03 | Bounded retry + circuit breaker | ADR-D7-06; ADR-D3-18 |
| DR-F-04 | Correlation-ID propagation + tracing | ADR-D7-03 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | httpx meets all needs | Evaluate aiohttp | Perf/feature test |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Reliability (timeout/retry/breaker) | 28 | No hangs/storms | Behaviour under fault |
| EC-02 | Resource efficiency (pooling) | 20 | No exhaustion | Connection reuse |
| EC-03 | Async correctness | 18 | No blocking | Event-loop safety |
| EC-04 | Tracing/correlation | 16 | Observability | Trace propagation |
| EC-05 | Consistency (single standard) | 18 | No ad-hoc clients | One client |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Shared httpx AsyncClient wrapper (pool + timeout + retry + breaker + tracing)

**Description.** One configured `AsyncClient` behind a small wrapper providing default
timeouts, retry/backoff, circuit breaker (shared with ADR-D3-18/D7-06), correlation-ID
injection and OpenTelemetry/Langfuse tracing; injected via DI.
**Strengths.** Reliable, efficient, consistent, observable; async-native.
**Weaknesses.** Wrapper to maintain.
**Cost / effort.** Low.

### 5.2 Option B — Per-call httpx clients (no shared instance)

**Description.** Create clients ad hoc.
**Strengths.** Simple locally.
**Weaknesses.** No pooling reuse; inconsistent timeouts/retries; connection churn.
**Cost / effort.** Low; inefficient/inconsistent.

### 5.3 Option C — aiohttp shared client

**Description.** Use aiohttp instead of httpx.
**Strengths.** Mature async client.
**Weaknesses.** httpx integrates better with the sync/async + testing story and is the
common FastAPI-era choice; no compelling edge here.
**Cost / effort.** Low; lateral.

### 5.4 Option D — requests (sync) with threadpool offload

**Description.** Sync requests offloaded to threads.
**Strengths.** Familiar.
**Weaknesses.** Blocking in an async app; thread overhead; violates 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §25.
**Cost / effort.** Low; wrong model.

### 5.5 Option E — Service-mesh-handled resilience (client stays naive)

**Description.** Let a mesh (e.g. Istio/Linkerd) do retry/timeout/mTLS.
**Strengths.** Cross-cutting resilience; mTLS.
**Weaknesses.** Mesh only covers in-cluster hops, not external enterprise/SLM APIs;
adds platform complexity; app still needs client config. Complement, not replacement.
**Cost / effort.** High platform.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No timeouts (default infinite) | CLAUDE.md — mandatory timeouts |
| Unbounded retries | ADR-D7-06 — retry amplification |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by CLAUDE.md, 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §24–§26, 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md
§63, 26.PF-FT-AI-PERFORMANCE-COST.md §15.

| Criterion | Weight | A: Shared httpx | B: Per-call httpx | C: aiohttp | D: requests+threads | E: mesh-only |
|---|---|---|---|---|---|---|
| EC-01 Reliability | 28 | 5 | 2 | 5 | 3 | 3 |
| EC-02 Pooling | 20 | 5 | 2 | 5 | 2 | 4 |
| EC-03 Async correctness | 18 | 5 | 4 | 5 | 1 | 4 |
| EC-04 Tracing/correlation | 16 | 5 | 3 | 4 | 3 | 3 |
| EC-05 Consistency | 18 | 5 | 2 | 4 | 3 | 3 |
| **Weighted total** | **100** | **500** | **256** | **464** | **246** | **340** |

Totals (×20): **A = 500**, **C = 464**, **E = 340**, **B = 256**, **D = 246**.

**Sensitivity.** A leads C by 36; both are viable async clients — httpx is chosen for
FastAPI-era fit and testing ergonomics. A mesh (E) may later add in-cluster mTLS/
resilience as a *complement*, not a replacement for the client config external calls
need.

## 7. Decision

**PFF AI will route all outbound HTTP through a single shared, DI-injected httpx
AsyncClient wrapper providing connection pooling, mandatory timeouts, bounded
retry/backoff, circuit-breaking, correlation-ID propagation and tracing (Option A);**
no ad-hoc clients or blocking HTTP in async paths. A service mesh may later add
in-cluster mTLS/resilience. aiohttp (C) is a viable alternative not chosen;
per-call (B), sync requests (D) and mesh-only (E) are rejected.

**Status rationale.** `Accepted` — CLAUDE.md and 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md / 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md / 26.PF-FT-AI-PERFORMANCE-COST.md mandate this.

## 8. Architecture Detail

- `src/pf_ft_ai/infrastructure/http/`: a `SharedHttpClient` wrapping one `AsyncClient`
  with pool limits, default + per-call timeouts (27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §26), retry/backoff and a
  circuit breaker (shared policy with ADR-D3-18/D7-06), correlation-ID header injection
  (ADR-D7-03) and tracing spans.
- Integration layer (ADR-D2-13), SLM/embedding providers (ADR-D3-14/23), MCP and RAG
  all consume it; ERC collection (ADR-D4-04) uses it under bounded concurrency.
- Lint/architecture check forbids importing `requests` or creating ad-hoc clients in
  async code.

## 9. Consequences

### 9.1 Positive
- Reliable, efficient, observable outbound HTTP everywhere; one place to tune.
### 9.2 Negative
- Wrapper maintenance.
### 9.3 Neutral
- Shares resilience config with ADR-D3-18/D7-06.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Per-call flexibility | Consistency + reliability + tracing | Backend Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Client calls enterprise APIs; doesn't decide business |
| Precedence chain | Faithfully carries enterprise responses |
| Four-state separation | Infra concern; no state conflation |
| Versioned artefacts | Client config versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Ad-hoc client bypasses standard | Med | Med | M | Lint/architecture check | Backend Lead | Low |
| RSK-02 | Retry storm | Low | High | M | Bounded retry + breaker (ADR-D7-06) | SRE | Low |
| RSK-03 | Missing timeout hangs request | Low | High | M | Mandatory default timeout | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Outbound calls via shared client | 100% | < 100% | Lint/audit | Per build |
| QM-02 | Calls without timeout | 0 | > 0 | Lint | Per build |
| QM-03 | Correlation-ID propagation | 100% | < 100% | Traces | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Central TLS/timeout config; egress-controlled (ADR-D6-04) |
| Data classification touched | Carries request/response data (per call classification) |
| Personal data / PII | TLS in transit; redaction in logs (ADR-D7-04) |
| Children's data and safeguarding | N/A at client layer |
| UK GDPR lawful basis and rights impact | Encryption in transit |
| Audit and evidential requirements | Traced calls with correlation id |
| Standards touched | ISO/IEC 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 2 |
| Repository paths | `src/pf_ft_ai/infrastructure/http/` |
| Configuration | Pool limits, timeouts, retry/breaker |
| Contracts / schemas | Client interface |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D2-13, D3-18, D7-06, D7-03 |
| Effort estimate | S–M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | All outbound HTTP uses shared client | Lint/audit |
| AC-02 | Every call has a timeout | Lint |
| AC-03 | Retry bounded + breaker present | Unit test |
| AC-04 | Correlation id propagated | Trace test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Latency, error, retry, breaker metrics per dependency |
| Alerting | Breaker open; latency/error spikes |
| Runbook | `docs/runbooks/http-client.md` |
| Failure mode and degradation | Breaker/fallback (ADR-D3-18/D7-06) |
| Rollback | Config revert |
| Support model impact | Backend + SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Client wrapper | S | negligible | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | In-cluster mTLS/resilience needed | Security | Add service mesh (complement) |
| RT-02 | httpx limitation hit | Perf/feature | Evaluate aiohttp |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-25 |
| Specification sections | 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §63; 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §24–§26; 26.PF-FT-AI-PERFORMANCE-COST.md §15 |
| Requirement IDs | HTTP-* |
| Build phases | 2 |
| Code paths | `src/pf_ft_ai/infrastructure/http/` |
| Configuration | client config |
| Tests | client reliability suite |
| Upstream ADRs | ADR-D2-13 |
| Downstream ADRs | ADR-D3-18, D7-06 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Backend Lead | Initial decision recorded. |
