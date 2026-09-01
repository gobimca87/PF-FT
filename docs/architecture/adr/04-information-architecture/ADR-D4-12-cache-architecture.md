---
id: ADR-D4-12
title: Cache architecture — namespaces, TTL, invalidation, stampede protection
domain: 4 Information
ws_ref: [WS-22]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [Backend Lead, SRE, Security Architect]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D4-10, ADR-D4-06, ADR-D4-03, ADR-D4-01, ADR-D1-03, ADR-D2-18]
source_docs:
  - "MD files/3 Context & Integration/9 PFF-FA-AI-MEMORY-CACHE.md §33, §34, §35, §36, §37, §38, §39, §40, §41, §42, §43, §44, §45, §46, §47, §57, §58"
build_phases: [7]
impacted_paths:
  - src/pff_fa_ai/cache/
classification: Internal
review_due: 2027-08-22
---

# ADR-D4-12 — Cache architecture — namespaces, TTL, invalidation, stampede protection

## 1. Summary

PFF AI will cache enterprise-API responses and derived data using **cache-aside** with
**namespaced, isolation-safe keys**, **volatility-aware TTLs**, **event-driven +
TTL invalidation**, and protection against **stampede, penetration and poisoning**
(9 PFF-FA-AI-MEMORY-CACHE.md §33–§47). A hard rule: **transaction/command responses are never cached** as
truth (9 PFF-FA-AI-MEMORY-CACHE.md §35); the cache sits below ERC/enterprise in precedence and never serves
stale data as authoritative.

## 2. Context and Problem Statement

9 PFF-FA-AI-MEMORY-CACHE.md §33–§34 define cache categories and the enterprise-API response cache; §35 sets
the transaction-cache rule; §36–§40 define key design, isolation, TTL and freshness;
§41–§47 define cache-aside, invalidation, and stampede/penetration/poisoning
protection; §57–§58 give cache-vs-memory and cache-vs-ERC matrices. Caching is
essential for latency/cost but is the classic place stale enterprise data leaks in as
"truth". Without an explicit policy, TTLs are guessed, transaction results get cached,
and a cold-cache burst stampedes the enterprise APIs. This ADR fixes the cache design.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Cache-aside for enterprise reads | 9 PFF-FA-AI-MEMORY-CACHE.md §41 |
| DR-C-01 | Never cache transaction/command results as truth | 9 PFF-FA-AI-MEMORY-CACHE.md §35 |
| DR-F-02 | Volatility-aware TTL + event invalidation | 9 PFF-FA-AI-MEMORY-CACHE.md §38–§39, §44 |
| DR-F-03 | Stampede/penetration/poisoning protection | 9 PFF-FA-AI-MEMORY-CACHE.md §45–§47 |
| DR-C-02 | Namespaced, isolation-safe keys | 9 PFF-FA-AI-MEMORY-CACHE.md §36–§37 |
| DR-C-03 | Cache ranks below ERC/enterprise | ADR-D1-03; 9 PFF-FA-AI-MEMORY-CACHE.md §58 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Read volumes justify caching | Reduce cache scope | Hit-rate metrics |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Freshness/precedence safety | 30 | No stale-as-truth | Staleness tests |
| EC-02 | Latency/cost reduction | 22 | Why cache | Hit rate; latency |
| EC-03 | Resilience (stampede/penetration) | 18 | Protect enterprise APIs | Load under cold cache |
| EC-04 | Isolation/security | 16 | No cross-tenant leak | Key isolation tests |
| EC-05 | Simplicity | 14 | Maintainability | Concepts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Cache-aside + volatility-aware TTL + event invalidation + stampede/penetration/poisoning protection

**Description.** Read-through-on-miss cache-aside (§41); per-datatype TTL keyed to
volatility (§38–§39); invalidate on enterprise events (§44, ADR-D4-06) and on TTL;
stampede protection via locks/single-flight (§45); penetration protection via
negative caching (§46); poisoning protection via validation (§47); namespaced
isolation-safe keys (§36–§37); transactions never cached (§35).
**Strengths.** Fresh, fast, resilient, isolated, precedence-safe.
**Weaknesses.** Several protections to implement.
**Cost / effort.** Medium.

### 5.2 Option B — Simple TTL cache (no events, no stampede protection)

**Description.** Cache with fixed TTL only.
**Strengths.** Simple.
**Weaknesses.** Stale until TTL; cold-cache stampede; no penetration/poisoning
defence.
**Cost / effort.** Low; fragile.

### 5.3 Option C — Write-through / write-behind cache

**Description.** Cache updated on writes.
**Strengths.** Cache always warm for written data.
**Weaknesses.** The platform doesn't own enterprise writes (Golden Rule); write-behind
risks presenting unconfirmed data as cached truth (§35 violation).
**Cost / effort.** Medium; wrong ownership model.

### 5.4 Option D — No cache (always read enterprise)

**Description.** Skip caching.
**Strengths.** Always fresh; simplest correctness.
**Weaknesses.** Higher latency + enterprise API load/cost; misses easy wins for stable
reference data (ADR-D4-08).
**Cost / effort.** Low; costly at runtime.

### 5.5 Option E — Tiered cache (in-process L1 + Redis L2)

**Description.** Add a small in-process cache before Redis.
**Strengths.** Lowest latency for hot keys.
**Weaknesses.** L1 coherence across instances is hard; risk of per-instance staleness;
premature for current scale. A useful *later* optimisation on top of A.
**Cost / effort.** Medium; coherence complexity.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Cache transaction/command results | 9 PFF-FA-AI-MEMORY-CACHE.md §35 |
| Global (non-namespaced) cache keys | 9 PFF-FA-AI-MEMORY-CACHE.md §36–§37 — isolation |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 9 PFF-FA-AI-MEMORY-CACHE.md §33–§47/§57–§58 and the
precedence chain.

| Criterion | Weight | A: Cache-aside full | B: Simple TTL | C: Write-through | D: No cache | E: Tiered L1+L2 |
|---|---|---|---|---|---|---|
| EC-01 Freshness/precedence | 30 | 5 | 3 | 2 | 5 | 4 |
| EC-02 Latency/cost | 22 | 5 | 4 | 5 | 1 | 5 |
| EC-03 Resilience | 18 | 5 | 2 | 3 | 3 | 4 |
| EC-04 Isolation/security | 16 | 5 | 4 | 3 | 5 | 4 |
| EC-05 Simplicity | 14 | 3 | 5 | 3 | 5 | 2 |
| **Weighted total** | **100** | **470** | **352** | **328** | **358** | **404** |

Totals (×20): **A = 470**, **E = 404**, **D = 358**, **B = 352**, **C = 328**.

**Sensitivity.** A leads E by 66. E (tiered) is a clear *later* latency optimisation
once hot-key patterns are known (RT-01), layered on A. D is safe but costly; B fragile;
C violates the ownership/transaction rules.

## 7. Decision

**PFF AI will use cache-aside with namespaced isolation-safe keys, volatility-aware
TTLs, event-driven plus TTL invalidation, and stampede/penetration/poisoning
protection (Option A); transaction and command responses are never cached as truth,
and the cache always ranks below ERC/enterprise in precedence.** A tiered in-process
L1 (Option E) may be added later for hot keys. Simple-TTL (B) is too fragile;
write-through (C) mismodels ownership; no-cache (D) is needlessly costly for stable
reads.

**Status rationale.** `Accepted` — 9 PFF-FA-AI-MEMORY-CACHE.md §33–§47 govern this.

## 8. Architecture Detail

- `src/pff_fa_ai/cache/`: `CacheStore` over Redis (ADR-D4-10), `pff-fa:<env>:cache:...`
  namespace with tenant/user/club isolation in the key (§36–§37).
- TTL policy per datatype keyed to volatility (§38–§39); stable reference data (leagues)
  longer TTL, volatile data short/none (ADR-D4-08).
- Invalidation: enterprise events (ADR-D4-06/D2-18) invalidate affected keys; TTL as
  backstop (§43–§44).
- Protections: single-flight lock for stampede (§45); negative caching with short TTL
  for penetration (§46); response validation before caching for poisoning (§47).
- Rule: never cache transaction/command outcomes (§35); UNKNOWN outcomes are re-read,
  not cached (ties to ADR-D2-11).

## 9. Consequences

### 9.1 Positive
- Fast, cheap reads for stable data; resilient cold-cache behaviour; precedence-safe.
### 9.2 Negative
- Multiple protections to build and tune.
### 9.3 Neutral
- Cache invalidation coupled to eventing (D4-06/D2-18).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of plain TTL | Freshness + resilience + isolation | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Cache reads only; transactions never cached (§35) |
| Precedence chain | Cache below ERC/enterprise; TTL/events enforce freshness |
| Four-state separation | Cache namespace distinct from memory (D4-10) |
| Versioned artefacts | Cache policy versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Stale cached value served as truth | Med | High | H | Volatility TTL + event invalidation + precedence | AI Arch Lead | Low |
| RSK-02 | Cold-cache stampede hits enterprise API | Med | High | H | Single-flight lock (§45) | SRE | Low |
| RSK-03 | Cross-tenant cache leak | Low | High | M | Namespaced isolation keys + tests | Security Architect | Low |
| RSK-04 | Cache poisoning | Low | High | M | Validate before cache (§47) | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Transaction responses cached | 0 | > 0 | Tests/audit | Continuous |
| QM-02 | Cache hit rate (cacheable reads) | ≥ target | falling | Cache metrics | Weekly |
| QM-03 | Stampede events | ≈ 0 | rising | Metrics | Weekly |
| QM-04 | Cross-tenant isolation tests | 100% | < 100% | CI | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Poisoning/penetration defences reduce risk |
| Data classification touched | Cached enterprise reads may be Personal — short TTL, encrypted |
| Personal data / PII | TTL-bound; namespaced; minimised |
| Children's data and safeguarding | Safeguarding reads short/no TTL; never as truth |
| UK GDPR lawful basis and rights impact | TTL supports minimisation |
| Audit and evidential requirements | Cache invalidations logged |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 7 |
| Repository paths | `src/pff_fa_ai/cache/` |
| Configuration | TTL-by-volatility map; protection settings |
| Contracts / schemas | CacheStore protocol; key schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D4-10, ADR-D4-06, ADR-D2-18 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Transaction/command results never cached | Code + test (§35) |
| AC-02 | TTL varies by data volatility | Config test |
| AC-03 | Stampede lock prevents thundering herd | Load test (§45) |
| AC-04 | Namespaced isolation holds | Security test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Hit rate, TTL efficacy, stampede/negative-cache metrics |
| Alerting | Hit-rate drop; stampede; poisoning attempts |
| Runbook | `docs/runbooks/cache.md` |
| Failure mode and degradation | Cache down → read enterprise directly (bounded, D4-04) |
| Rollback | Cache policy revert |
| Support model impact | Platform + SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Cache subsystem + protections | M | small | Build; shares Redis (D4-10) |
| Reduced enterprise-API calls | — | saving | Fewer reads |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Hot-key latency needs sub-ms | QM-02/latency | Add tiered L1 (Option E) |
| RT-02 | Stale-as-truth incident | Incident | CAR; tighten TTL/invalidation |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-22 |
| Specification sections | 9 PFF-FA-AI-MEMORY-CACHE.md §33–§47, §57–§58 |
| Requirement IDs | CACHE-* |
| Build phases | 7 |
| Code paths | `src/pff_fa_ai/cache/` |
| Configuration | TTL/protection config |
| Tests | cache + isolation + stampede suites |
| Upstream ADRs | ADR-D4-10, ADR-D4-06 |
| Downstream ADRs | ADR-D4-08 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
