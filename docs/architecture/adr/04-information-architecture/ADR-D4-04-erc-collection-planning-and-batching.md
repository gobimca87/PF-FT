---
id: ADR-D4-04
title: ERC collection planning, batching and pagination safety
domain: 4 Information
ws_ref: [WS-19]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [Backend Lead, Integration Engineer]
reviewers: [Principal Architect, SRE]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D4-02, ADR-D4-05, ADR-D2-08, ADR-D2-13, ADR-D2-12]
source_docs:
  - "MD files/3 Context & Integration/8 PFF-FA-AI-ERC-CONTEXT.md §22, §23, §24, §25, §26, §27, §28, §29, §30, §35, §36, §37, §38, §39, §42, §43, §53, §54, §55, §56, §57, §58"
build_phases: [4]
impacted_paths:
  - src/pff_fa_ai/erc/collection/
classification: Internal
review_due: 2027-08-22
---

# ADR-D4-04 — ERC collection planning, batching and pagination safety

## 1. Summary

PFF AI will build ERC through a **declarative collection planner** that resolves the
context-requirement dependency graph and executes enterprise reads with **bounded
parallelism**, agreed **batch sizes** (`MAX_ERC_BATCH_SIZE = 20`), and
**pagination-safety** guards (max pages, duplicate/missing-record detection) — never
an unbounded fan-out (8 PFF-FA-AI-ERC-CONTEXT.md §22–§30, §35–§43, §53–§58). Batch processing gathers
*data*; it does not mean per-item SLM calls (§40).

## 2. Context and Problem Statement

8 PFF-FA-AI-ERC-CONTEXT.md §22–§29 define context-requirement identification, dependency graphs and a
collection planner; §26–§28 define sequential vs parallel collection and the
parallel-execution rule; §35–§43 define large-data batching, agreed batch size, team/
official batching and bounded parallelism; §53–§58 define pagination safety,
duplicate/missing detection and aggregation. CLAUDE.md fixes `MAX_ERC_BATCH_SIZE = 20`.
Without a planned, bounded approach, ERC construction either serialises everything
(slow) or fans out unbounded (overloads enterprise APIs, risks throttling/incidents),
and large collections (many teams/officials) page unsafely. This ADR fixes how ERC is
collected.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Resolve dependencies before/around parallel reads | 8 PFF-FA-AI-ERC-CONTEXT.md §25–§28 |
| DR-F-02 | Batch large collections at agreed size (20) | 8 PFF-FA-AI-ERC-CONTEXT.md §36; CLAUDE.md |
| DR-F-03 | Pagination safety: max pages, dup/missing detection | 8 PFF-FA-AI-ERC-CONTEXT.md §53–§56 |
| DR-N-01 | Bounded parallelism (don't overload enterprise) | 8 PFF-FA-AI-ERC-CONTEXT.md §28, §43; ADR-D2-08 |
| DR-C-01 | Batch collection ≠ per-item SLM calls | 8 PFF-FA-AI-ERC-CONTEXT.md §40 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Batch size 20 balances latency vs load | Tune via config | Load tests |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Enterprise-API safety (no overload) | 26 | Protect systems of record | Concurrency bound |
| EC-02 | Latency of ERC build | 22 | UX | p95 build time |
| EC-03 | Correctness/completeness | 20 | Dup/missing handling | Completeness rate |
| EC-04 | Dependency correctness | 16 | Ordered where needed | Ordering respected |
| EC-05 | Simplicity/observability | 16 | Debuggable | Traceability |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Declarative planner: dependency graph + bounded-parallel batched reads + pagination safety

**Description.** A planner computes the requirement dependency graph (§25), executes
independent reads in parallel up to a concurrency bound (§28, §43), batches large
collections at size 20 (§36), and guards pagination (§54) with dup (§55) and missing
(§56) detection; aggregation ordered (§58).
**Strengths.** Fast within safe bounds; correct; observable.
**Weaknesses.** Planner complexity.
**Cost / effort.** Medium.

### 5.2 Option B — Fully sequential collection

**Description.** Fetch everything one after another.
**Strengths.** Simple; gentle on APIs.
**Weaknesses.** Slow for multi-section/large ERC; poor UX.
**Cost / effort.** Low; slow.

### 5.3 Option C — Unbounded parallel fan-out

**Description.** Fire all reads concurrently.
**Strengths.** Fastest in isolation.
**Weaknesses.** Overloads enterprise APIs; throttling/incidents; violates §28/§43.
**Cost / effort.** Low; dangerous.

### 5.4 Option D — Fixed thread pool, no dependency graph

**Description.** Bounded parallel but ignores dependencies.
**Strengths.** Bounded load; simpler than A.
**Weaknesses.** Breaks when section B needs A's output; retries/errors from ordering.
**Cost / effort.** Low-medium; incorrect for dependent reads.

### 5.5 Option E — Planner + adaptive concurrency (dynamic based on API health)

**Description.** Option A with concurrency that adapts to observed latency/throttle
signals.
**Strengths.** Best safety+latency balance under varying load.
**Weaknesses.** More complex control loop; premature before baseline load is known.
**Cost / effort.** Medium-high; a later optimisation over A.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Per-item SLM enrichment during collection | 8 PFF-FA-AI-ERC-CONTEXT.md §40 — batch ≠ SLM calls |
| Unlimited pagination | 8 PFF-FA-AI-ERC-CONTEXT.md §54 — pagination safety |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 8 PFF-FA-AI-ERC-CONTEXT.md §22–§58 and ADR-D2-08.

| Criterion | Weight | A: Planner bounded | B: Sequential | C: Unbounded | D: Pool no-graph | E: Adaptive |
|---|---|---|---|---|---|---|
| EC-01 API safety | 26 | 5 | 5 | 1 | 4 | 5 |
| EC-02 Latency | 22 | 5 | 2 | 5 | 4 | 5 |
| EC-03 Correctness | 20 | 5 | 5 | 3 | 3 | 5 |
| EC-04 Dependency correctness | 16 | 5 | 5 | 2 | 2 | 5 |
| EC-05 Simplicity/observability | 16 | 4 | 5 | 3 | 4 | 3 |
| **Weighted total** | **100** | **488** | **432** | **288** | **346** | **476** |

Totals (×20): **A = 488**, **E = 476**, **B = 432**, **D = 346**, **C = 288**.

**Sensitivity.** A edges E by 12; E's adaptive concurrency is a clear *future*
enhancement (RT-01) once baseline API behaviour is measured. B is safe but slow; C/D
fail safety or dependency correctness.

## 7. Decision

**PFF AI will build ERC via a declarative collection planner that resolves the
requirement dependency graph and executes reads with bounded parallelism, batching
large collections at `MAX_ERC_BATCH_SIZE = 20`, with pagination-safety and
duplicate/missing-record detection (Option A).** Concurrency is bounded and
configurable; adaptive concurrency (E) is a documented future optimisation. Batch
collection gathers data only — never per-item SLM calls (§40). Sequential (B) is too
slow; unbounded (C) unsafe; pool-without-graph (D) mishandles dependencies.

**Status rationale.** `Accepted` — 8 PFF-FA-AI-ERC-CONTEXT.md §22–§58 and CLAUDE.md govern this.

## 8. Architecture Detail

- `src/pff_fa_ai/erc/collection/`: a `ContextCollectionPlanner` builds the dependency
  graph (§25), schedules independent nodes in parallel within a semaphore-bounded pool
  (§28, §43), and batches collections (teams §37, officials §38) at 20 (§36).
- Pagination (§53–§54): each paged read has a max-page guard; duplicates detected by
  record id (§55); missing records tracked for completeness (§56, ADR-D4-05).
- Aggregation ordered deterministically (§58); results feed ERC sections (ADR-D4-02).
- Uses the shared HTTP client (ADR-D5-16) via the integration layer (ADR-D2-13).

## 9. Consequences

### 9.1 Positive
- Fast, safe, correct ERC construction with clear observability.
### 9.2 Negative
- Planner and batching logic to build/maintain.
### 9.3 Neutral
- Sets up partial-failure semantics (ADR-D4-05).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of sequential | Latency within API-safe bounds | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Reads only; bounded to protect systems of record |
| Precedence chain | Collects authoritative ERC data faithfully |
| Four-state separation | Builds the enterprise-reference view (ERC) |
| Versioned artefacts | Collection config versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Concurrency overloads enterprise API | Low | High | M | Bounded pool; retry/backoff (§46); adaptive later | SRE | Low |
| RSK-02 | Pagination misses/duplicates records | Low | High | M | Max-page guard + dup/missing detection | Backend Lead | Low |
| RSK-03 | Dependency mis-ordering | Low | Med | M | Dependency graph + tests | AI Arch Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | ERC build p95 latency | within budget (ADR-D5-18) | breach | App Insights | Continuous |
| QM-02 | Collection completeness | 100% mandatory sections | < 100% | Completeness tracker | Continuous |
| QM-03 | Enterprise API throttle events during collection | ≈ 0 | rising | Integration metrics | Weekly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Bounded reads; no new surface |
| Data classification touched | As per collected sections |
| Personal data / PII | Collect only required sections (ADR-D6-07) |
| Children's data and safeguarding | Officials/safeguarding collected under authorization |
| UK GDPR lawful basis and rights impact | Minimised collection |
| Audit and evidential requirements | Collection traced per requirement |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 4 |
| Repository paths | `src/pff_fa_ai/erc/collection/` |
| Configuration | Concurrency bound, batch size (20), max pages |
| Contracts / schemas | Context requirement model (§23) |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D4-02, ADR-D2-08, ADR-D2-13, ADR-D5-16 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Parallel reads bounded by configured concurrency | Load test |
| AC-02 | Large collections batched at 20 | Unit test |
| AC-03 | Pagination guarded; dups/missing detected | Tests (§54–§56) |
| AC-04 | Dependencies respected | Integration test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Build latency, batch states (§45), throttle events |
| Alerting | Throttle spikes; completeness < target |
| Runbook | `docs/runbooks/erc.md` |
| Failure mode and degradation | Partial failure per ADR-D4-05 |
| Rollback | Concurrency/batch config revert |
| Support model impact | Integration + SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Planner + batching | M | negligible | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Variable API load hurts latency/safety | QM-01/QM-03 | Adopt adaptive concurrency (Option E) |
| RT-02 | Batch size 20 suboptimal | Load tests | Tune via config |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-19 |
| Specification sections | 8 PFF-FA-AI-ERC-CONTEXT.md §22–§30, §35–§43, §53–§58 |
| Requirement IDs | ERC-COLL-* |
| Build phases | 4 |
| Code paths | `src/pff_fa_ai/erc/collection/` |
| Configuration | concurrency/batch/page config |
| Tests | collection + pagination suites |
| Upstream ADRs | ADR-D4-02, ADR-D2-08 |
| Downstream ADRs | ADR-D4-05 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
