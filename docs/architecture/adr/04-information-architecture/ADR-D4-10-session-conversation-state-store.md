---
id: ADR-D4-10
title: Session / conversation / memory / cache state store — Azure Managed Redis
domain: 4 Information
ws_ref: [WS-22]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Principal Architect
contributors: [Platform Engineer, Backend Lead, FinOps, Security Architect]
reviewers: [AI Architecture Lead, Security Architect]
approver: Architecture Review Board
supersedes:
  - "docs/adr/0004-memory-cache-store-azure-managed-redis.md"
superseded_by: []
related_adrs: [ADR-D4-11, ADR-D4-12, ADR-D4-01, ADR-D5-08, ADR-D5-07, ADR-D6-04]
source_docs:
  - "MD files/3 Context & Integration/9 PFF-FA-AI-MEMORY-CACHE.md §21, §22, §37, §54, §55, §77, §78"
  - "MD files/2 Agent Runtime/6 PFF-FA-AI-CONVERSATION-SESSION.md §15, §68, §69, §70, §71"
  - "MD files/1 Foundation/5. PFF-FA-AI-STATE-MODEL.md §53, §54, §55"
build_phases: [7]
impacted_paths:
  - src/pff_fa_ai/memory/
  - src/pff_fa_ai/cache/
  - config/base/redis.yaml
classification: Internal
review_due: 2027-08-22
---

# ADR-D4-10 — Session / conversation / memory / cache state store — Azure Managed Redis

> **Supersedes** `docs/adr/0004-memory-cache-store-azure-managed-redis.md`. That
> lightweight Nygard ADR recorded the same choice; this ADR provides the full
> CMMI DAR evaluation behind it. The decision is unchanged (Azure Managed Redis);
> `docs/adr/0004` is left in place as required by ADR-D0-01.

## 1. Summary

PFF AI will use **Azure Managed Redis** as the backing store for conversation,
session, memory and cache state, behind the `MemoryStore`/`CacheStore` abstractions
(9 PFF-FA-AI-MEMORY-CACHE.md §22), with memory and cache logically separated by key namespace on the same
instance (9 PFF-FA-AI-MEMORY-CACHE.md §37, §77–§78). Redis's low-latency key/value + TTL model fits
short-lived conversational/session state and cache; Azure-managed operation, private
networking and Entra integration meet the enterprise bar (6 PFF-FA-AI-CONVERSATION-SESSION.md §68–§71; 5. PFF-FA-AI-STATE-MODEL.md
§53–§55).

## 2. Context and Problem Statement

The memory/session/cache store was deliberately left open (DEVELOPMENT-GUIDE §2, 9 PFF-FA-AI-MEMORY-CACHE.md §21) to be resolved by ADR. 6 PFF-FA-AI-CONVERSATION-SESSION.md §68–§71 require a stateless API with session
affinity backed by an external store; 5. PFF-FA-AI-STATE-MODEL.md §53–§55 require state persistence with
store separation; 9 PFF-FA-AI-MEMORY-CACHE.md §22 requires provider-independent `MemoryStore`/`CacheStore`
interfaces. The state to hold is mostly **ephemeral, key-addressable and TTL-bound**
(conversations, sessions, working memory, caches) — not relational analytics. The
choice must be Azure-native, private-networkable, low-latency and operationally light.
Legacy `docs/adr/0004` already selected Azure Managed Redis; this ADR records the
alternatives and evaluation that justify it to enterprise-review standard.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Low-latency key/value with TTL for session/cache | 9 PFF-FA-AI-MEMORY-CACHE.md §37–§38; 6 PFF-FA-AI-CONVERSATION-SESSION.md §15 |
| DR-F-02 | Provider-independent behind MemoryStore/CacheStore | 9 PFF-FA-AI-MEMORY-CACHE.md §22 |
| DR-F-03 | Session recovery / affinity support | 6 PFF-FA-AI-CONVERSATION-SESSION.md §55, §69 |
| DR-N-01 | Azure-native, private endpoint, Entra/Key Vault | ADR-D5-08, D5-07, D6-04 |
| DR-N-02 | Managed operation (small team) | operational |
| DR-C-01 | Memory/cache logically separated | 9 PFF-FA-AI-MEMORY-CACHE.md §77–§78; ADR-D4-01 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | State is mostly ephemeral/TTL-bound, not relational | Add a durable store for long-term memory | ADR-D4-11 |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Fit for ephemeral TTL key/value state | 24 | Matches the workload | Data-model fit |
| EC-02 | Latency | 20 | On the conversational hot path | p99 read/write |
| EC-03 | Azure-native + security (PE/Entra/CMK) | 20 | Enterprise bar | Feature audit |
| EC-04 | Operational burden | 16 | Small team | Managed? |
| EC-05 | Cost | 10 | Spend | £/month |
| EC-06 | Durability options (for long-term memory) | 10 | Some memory persists | Persistence/backup |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Azure Managed Redis (RESP), memory+cache namespaced

**Description.** Managed Redis; `redis.asyncio` client; memory and cache separated by
key namespace on one instance; TTL per key; private endpoint + Entra + Key Vault.
**Strengths.** Ideal for ephemeral TTL key/value; lowest latency; Azure-native;
managed; standard RESP (no lock-in to a proprietary SDK).
**Weaknesses.** Durability is cache-grade; long-term memory needs care (ADR-D4-11).
**Cost / effort.** Moderate tier cost; low ops.

### 5.2 Option B — Azure Cosmos DB

**Description.** Managed multi-model DB for state.
**Strengths.** Durable; global distribution; rich queries; TTL supported.
**Weaknesses.** Higher latency than Redis for hot session reads; higher cost;
over-featured for ephemeral state; RU cost model complex.
**Cost / effort.** Higher; managed.

### 5.3 Option C — Azure Database for PostgreSQL

**Description.** Relational store for state.
**Strengths.** Durable; transactional; already considered for pgvector (ADR-D3-24).
**Weaknesses.** Relational overkill for key/value TTL churn; higher latency; TTL/
expiry is DIY; connection-pool pressure under chatty session access.
**Cost / effort.** Low-moderate; more app logic.

### 5.4 Option D — Self-hosted Redis/KeyDB on AKS

**Description.** Run Redis in-cluster.
**Strengths.** Control; lowest licence cost; in-tenancy.
**Weaknesses.** The platform now operates a stateful store (HA, persistence, patching,
backup) — disproportionate for a small team.
**Cost / effort.** Low licence, high ops.

### 5.5 Option E — Split stores: Redis for cache/session + a durable store for long-term memory

**Description.** Redis (Option A) for ephemeral cache/session/working memory, plus a
durable store (Cosmos/Postgres) specifically for long-term/user-preference memory.
**Strengths.** Best fit per data lifetime; durability where it matters.
**Weaknesses.** Two stores to run; more complexity now, when long-term memory volume
is small.
**Cost / effort.** Medium; premature split.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| In-process memory only | 6 PFF-FA-AI-CONVERSATION-SESSION.md §68 — stateless API needs external store |
| Blob storage for state | Wrong access pattern; no TTL/low-latency reads |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 9 PFF-FA-AI-MEMORY-CACHE.md §21–§22/§37/§77–§78, 6 PFF-FA-AI-CONVERSATION-SESSION.md
§68–§71 and Azure service characteristics.

| Criterion | Weight | A: Managed Redis | B: Cosmos DB | C: Postgres | D: Self-host Redis | E: Split stores |
|---|---|---|---|---|---|---|
| EC-01 Ephemeral KV fit | 24 | 5 | 3 | 2 | 5 | 5 |
| EC-02 Latency | 20 | 5 | 3 | 3 | 5 | 5 |
| EC-03 Azure-native/security | 20 | 5 | 5 | 5 | 3 | 5 |
| EC-04 Ops burden | 16 | 5 | 4 | 4 | 2 | 3 |
| EC-05 Cost | 10 | 4 | 2 | 4 | 4 | 3 |
| EC-06 Durability for long-term | 10 | 3 | 5 | 5 | 3 | 5 |
| **Weighted total** | **100** | **468** | **372** | **366** | **384** | **452** |

Totals (×20): **A = 468**, **E = 452**, **D = 384**, **B = 372**, **C = 366**.

**Sensitivity.** A leads E by 16 — the only close contender. E's durable long-term
store is deferred: while long-term memory volume is small, Redis with persistence +
backup suffices, and ADR-D4-11 keeps the memory abstraction store-agnostic so the
split (E) can be adopted later (RT-01) without a rewrite. A honours the "one physical
store, namespaced" model of `docs/adr/0004` and 9 PFF-FA-AI-MEMORY-CACHE.md §37.

## 7. Decision

**PFF AI will use Azure Managed Redis as the backing store for conversation, session,
memory and cache state, behind `MemoryStore`/`CacheStore` abstractions, with memory
and cache logically separated by key namespace on one instance (Option A),** with
private endpoint, Entra auth and Key Vault secret refs. If long-term memory grows to
need stronger durability/query, the split-store model (Option E) is adopted behind the
same abstraction (RT-01). Cosmos (B) and Postgres (C) are over-featured/higher-latency
for ephemeral state; self-host (D) imposes undue ops. This confirms and supersedes
`docs/adr/0004`.

**Status rationale.** `Accepted` — resolves an open decision; unchanged from
`docs/adr/0004`, now with full evaluation.

## 8. Architecture Detail

- `MemoryStore`/`CacheStore` protocols (9 PFF-FA-AI-MEMORY-CACHE.md §22) with a `RedisMemoryStore` /
  `RedisCacheStore` using `redis.asyncio`; no Azure-specific SDK at app layer.
- Namespaces (9 PFF-FA-AI-MEMORY-CACHE.md §37, §77–§78): `pff-fa:<env>:memory:...` and
  `pff-fa:<env>:cache:...`; cross-user/club isolation enforced in key design.
- TTLs per state class (5. PFF-FA-AI-STATE-MODEL.md §55; 6 PFF-FA-AI-CONVERSATION-SESSION.md §15 session TTL; ADR-D4-12 cache TTL).
- Config `config/base/redis.yaml` with `*_secret_ref` (ADR-D5-07); private endpoint
  (ADR-D6-04); persistence + backup enabled for memory namespace.
- Session recovery/affinity (6 PFF-FA-AI-CONVERSATION-SESSION.md §55, §69) via session keys; stateless API
  (6 PFF-FA-AI-CONVERSATION-SESSION.md §68).

## 9. Consequences

### 9.1 Positive
- Low-latency, Azure-native, managed store fitting the ephemeral workload; one store to run.
### 9.2 Negative
- Durability is cache-grade; long-term memory needs persistence config / later split.
### 9.3 Neutral
- Same physical store, namespaced — memory/cache stay logically separate (D4-11/12).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Rich query/strong durability of a DB | Latency + fit + low ops | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Store holds AI-owned state only; never enterprise truth (ADR-D4-01) |
| Precedence chain | Cache ranks below ERC/enterprise; TTL enforces freshness |
| Four-state separation | Namespaces keep conversation/session/memory/cache separate |
| Versioned artefacts | Store config versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Long-term memory lost on eviction | Med | Med | M | Persistence+backup for memory ns; split later (E) | Platform Eng | Low |
| RSK-02 | Cross-user/club key leakage | Low | High | M | Namespace + isolation tests (9 PFF-FA-AI-MEMORY-CACHE.md §77–§78) | Security Architect | Low |
| RSK-03 | Redis outage drops sessions | Low | Med | M | HA tier; graceful re-auth/recovery (6 PFF-FA-AI-CONVERSATION-SESSION.md §55) | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | p99 read/write latency | ≤ 10 ms | > 30 ms | Redis metrics | Continuous |
| QM-02 | Availability | ≥ 99.9% | < 99.5% | Azure Monitor | Monthly |
| QM-03 | Cross-namespace isolation tests | 100% | < 100% | CI | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Managed store, private endpoint only |
| Data classification touched | Conversation/session/memory may be Personal |
| Personal data / PII | TTL + retention per ADR-D4-07; encrypted |
| Children's data and safeguarding | Safeguarding context not persisted as truth; TTL-bound |
| UK GDPR lawful basis and rights impact | Retention/erasure via TTL + deletion (9 PFF-FA-AI-MEMORY-CACHE.md §75) |
| Audit and evidential requirements | Access via Entra logged |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 7 |
| Repository paths | `src/pff_fa_ai/memory/`, `src/pff_fa_ai/cache/`, `config/base/redis.yaml` |
| Configuration | Redis connection, namespaces, TTLs, secret refs |
| Contracts / schemas | MemoryStore/CacheStore protocols |
| Migration | Supersedes docs/adr/0004 (no behaviour change) |
| Dependencies on other ADRs | ADR-D5-08, D5-07, D6-04, D4-11, D4-12 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | No Azure-specific SDK at app layer (RESP client only) | Code review |
| AC-02 | Memory/cache separated by namespace | Key-design test |
| AC-03 | Private endpoint + Entra + Key Vault used | Config/security review |
| AC-04 | Session recovery works after reconnect | Integration test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Latency, memory, evictions, hit rate |
| Alerting | Latency/availability/eviction spikes |
| Runbook | `docs/runbooks/redis.md` |
| Failure mode and degradation | Store down → session recovery / degrade (6 PFF-FA-AI-CONVERSATION-SESSION.md §55) |
| Rollback | Config revert |
| Support model impact | Managed → low on-call |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Azure Managed Redis tier | setup | £X/mo (tier-dependent) | Managed Redis pricing |
| Private endpoint | small | small | Azure PE |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Long-term memory needs durability/query | ADR-D4-11 volume | Adopt split-store (Option E) behind abstraction |
| RT-02 | Latency/eviction issues at scale | QM-01 | Resize tier / shard |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-22 Memory/Cache/Store |
| Specification sections | 9 PFF-FA-AI-MEMORY-CACHE.md §21–§22, §37, §54–§55, §77–§78; 6 PFF-FA-AI-CONVERSATION-SESSION.md §15, §68–§71; 5. PFF-FA-AI-STATE-MODEL.md §53–§55 |
| Requirement IDs | STORE-* |
| Build phases | 7 |
| Code paths | `src/pff_fa_ai/memory/`, `src/pff_fa_ai/cache/` |
| Configuration | `config/base/redis.yaml` |
| Tests | store + isolation suites |
| Upstream ADRs | ADR-D5-08, ADR-D4-01 |
| Downstream ADRs | ADR-D4-11, ADR-D4-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Principal Architect | Initial decision recorded; supersedes docs/adr/0004 with full DAR evaluation. |
