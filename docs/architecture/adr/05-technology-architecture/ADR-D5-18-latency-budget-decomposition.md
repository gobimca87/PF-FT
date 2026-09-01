---
id: ADR-D5-18
title: Latency budget decomposition and per-hop SLO allocation
domain: 5 Technology
ws_ref: [WS-26]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [SRE, Backend Lead, Performance Engineer]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-16, ADR-D5-17, ADR-D3-25, ADR-D3-19, ADR-D7-07]
source_docs:
  - "MD files/6 Production/26.PF-FT-AI-PERFORMANCE-COST.md §5, §6, §7, §8, §9, §10, §11, §16, §39, §52"
build_phases: [2, 8]
impacted_paths:
  - src/pf_ft_ai/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-18 — Latency budget decomposition and per-hop SLO allocation

## 1. Summary

PFF AI will define an **end-to-end latency budget** measured in **percentiles (p50/
p95/p99)** and **decompose it into per-hop sub-budgets** — gateway, orchestration, ERC
collection, retrieval, SLM generation, tool calls — each with an **owner** and an SLO,
so latency regressions are attributable and enforceable (26.PF-FT-AI-PERFORMANCE-COST.md §5–§11, §16, §39,
§52). Time-to-first-token and time-to-complete are tracked separately for streamed
responses.

## 2. Context and Problem Statement

26.PF-FT-AI-PERFORMANCE-COST.md §5–§9 define performance objectives, end-to-end latency, percentiles and the
latency budget; §9 latency-budget ownership; §10–§11 TTFT/time-to-complete; §16 API
latency; §39 model latency; §52 RAG latency breakdown. Without a decomposed,
owned budget, a slow end-to-end response has no attributable cause and no team is
accountable for a hop. This ADR fixes the budget model and per-hop allocation.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | End-to-end budget in percentiles | 26.PF-FT-AI-PERFORMANCE-COST.md §6–§8 |
| DR-F-02 | Per-hop sub-budgets with owners | 26.PF-FT-AI-PERFORMANCE-COST.md §8–§9 |
| DR-F-03 | TTFT vs time-to-complete for streaming | 26.PF-FT-AI-PERFORMANCE-COST.md §10–§11; ADR-D3-19 |
| DR-N-01 | Attributable regressions | 26.PF-FT-AI-PERFORMANCE-COST.md §52 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Hops are individually measurable (tracing) | Improve instrumentation | ADR-D7-02 |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Attributability (per-hop) | 28 | Find the slow hop | Hop-level SLIs |
| EC-02 | Accountability (owners) | 20 | Someone owns each budget | Owner per hop |
| EC-03 | User-perceived fidelity (percentiles, TTFT) | 20 | Real UX | p95/TTFT tracked |
| EC-04 | Enforceability (gates/alerts) | 18 | Prevent regressions | CI/alert gates |
| EC-05 | Simplicity | 14 | Maintainable | Concepts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Decomposed per-hop budget in percentiles, owned, with TTFT/complete split

**Description.** Total p95 target split into gateway/orchestration/ERC/retrieval/SLM/
tool sub-budgets, each owned and alerted; TTFT and time-to-complete tracked for streams
(ADR-D3-19); regression gates in CI perf tests.
**Strengths.** Attributable, accountable, UX-faithful, enforceable.
**Weaknesses.** Requires per-hop tracing + budget upkeep.
**Cost / effort.** Medium.

### 5.2 Option B — End-to-end target only (no decomposition)

**Description.** One overall latency SLO.
**Strengths.** Simple.
**Weaknesses.** A breach has no attributable cause; no hop ownership.
**Cost / effort.** Low; unactionable.

### 5.3 Option C — Average-latency targets (means, not percentiles)

**Description.** Track/target mean latency.
**Strengths.** Simple metric.
**Weaknesses.** Means hide tail latency users feel; 26.PF-FT-AI-PERFORMANCE-COST.md §7 wants percentiles.
**Cost / effort.** Low; misleading.

### 5.4 Option D — Per-hop budgets but no owners/gates (informational)

**Description.** Measure hops but don't assign owners or gate CI.
**Strengths.** Visibility.
**Weaknesses.** No accountability/enforcement; regressions slip.
**Cost / effort.** Low; weak.

### 5.5 Option E — Adaptive budgets per workflow class (different SLOs per workflow)

**Description.** Option A but budgets vary by workflow complexity (e.g. simple query vs
multi-step affiliation).
**Strengths.** Realistic per-workflow targets.
**Weaknesses.** More budgets to manage; valuable once workflows diversify — layer on A.
**Cost / effort.** Medium; later refinement.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No latency targets | 26.PF-FT-AI-PERFORMANCE-COST.md §5–§6 |
| Max-latency-only (no percentiles) | Hides typical UX |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 26.PF-FT-AI-PERFORMANCE-COST.md §5–§11/§16/§39/§52.

| Criterion | Weight | A: Per-hop owned percentile | B: E2E only | C: Averages | D: Hops no-owner | E: Per-workflow |
|---|---|---|---|---|---|---|
| EC-01 Attributability | 28 | 5 | 1 | 2 | 4 | 5 |
| EC-02 Accountability | 20 | 5 | 2 | 2 | 2 | 5 |
| EC-03 UX fidelity | 20 | 5 | 4 | 2 | 4 | 5 |
| EC-04 Enforceability | 18 | 5 | 3 | 2 | 2 | 5 |
| EC-05 Simplicity | 14 | 3 | 5 | 5 | 4 | 2 |
| **Weighted total** | **100** | **472** | **282** | **248** | **316** | **468** |

Totals (×20): **A = 472**, **E = 468**, **D = 316**, **B = 282**, **C = 248**.

**Sensitivity.** A edges E by 4; per-workflow budgets (E) are a clear refinement once
multiple workflows exist (RT-01), layered on A's per-hop model. Averages (C) and
E2E-only (B) are decisively worse on attributability/UX.

## 7. Decision

**PFF AI will define an end-to-end latency budget in percentiles and decompose it into
owned per-hop sub-budgets (gateway, orchestration, ERC, retrieval, SLM, tools), with
TTFT and time-to-complete tracked separately for streamed responses and regression
gates in CI perf tests (Option A).** Per-workflow-class budgets (E) will be layered on
as workflows diversify. E2E-only (B), averages (C) and owner-less hops (D) are
rejected.

**Status rationale.** `Accepted` — 26.PF-FT-AI-PERFORMANCE-COST.md §5–§11 govern this.

## 8. Architecture Detail

- Budget table maps each hop to a p95 sub-budget + owner (26.PF-FT-AI-PERFORMANCE-COST.md §9); the sum + overhead
  ≤ the end-to-end p95 target.
- Tracing (ADR-D7-02) tags spans per hop so SLIs are computed per hop; TTFT/complete
  (ADR-D3-19) tracked for streams; RAG breakdown (26.PF-FT-AI-PERFORMANCE-COST.md §52) sub-decomposed
  (embed/search/rerank).
- CI perf tests assert hop budgets on representative flows; alerts fire on per-hop
  breach (ADR-D7-07/08). Context assembly (ADR-D3-25) and autoscaling (ADR-D5-17) use
  the budget as a target.

## 9. Consequences

### 9.1 Positive
- Latency regressions are attributable and owned; UX-faithful percentiles.
### 9.2 Negative
- Per-hop tracing + budget maintenance.
### 9.3 Neutral
- Feeds autoscaling (D5-17) and SLOs (D7-07).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Single-number simplicity | Attributability + accountability | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Budget covers AI hops; enterprise-API latency owned at that hop |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | Budget config versioned |
| Adam persona governs *how*, not *what* | Latency never traded for false speed on unconfirmed data |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | A hop lacks instrumentation → blind spot | Med | Med | M | Enforce per-hop tracing (ADR-D7-02) | SRE | Low |
| RSK-02 | SLM hop dominates budget | Med | Med | M | Streaming TTFT + model/serving tuning (D5-10) | AI Arch Lead | Low |
| RSK-03 | Budgets unrealistic per workflow | Med | Low | L | Per-workflow budgets (Option E) | Perf Eng | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | End-to-end p95 | within budget | breach | App Insights | Continuous |
| QM-02 | Per-hop p95 vs sub-budget | within | breach | Tracing | Continuous |
| QM-03 | TTFT p95 (streamed) | ≤ target | breach | Langfuse | Continuous |
| QM-04 | Perf-regression gate pass | 100% | fail | CI perf tests | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None |
| Data classification touched | Internal (metrics) |
| Personal data / PII | Traces redacted (ADR-D7-04) |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | SLIs retained |
| Standards touched | ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 2 (base hops), 8 (RAG hops) |
| Repository paths | Platform-wide instrumentation |
| Configuration | Budget table; alert thresholds |
| Contracts / schemas | Span/hop tags |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-02, D3-19, D3-25, D5-17 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Every hop has a sub-budget + owner | Budget table review |
| AC-02 | Per-hop SLIs computed from traces | Tracing check |
| AC-03 | TTFT tracked for streams | Metric check |
| AC-04 | CI perf gate enforces budgets | CI config |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Per-hop latency dashboards |
| Alerting | Per-hop breach (ADR-D7-08) |
| Runbook | `docs/runbooks/latency.md` |
| Failure mode and degradation | Slow hop identified and owned |
| Rollback | Revert regressing change |
| Support model impact | SRE + owning teams |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Instrumentation + perf tests | M | small | Build + CI |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Workflows diversify | Product | Per-workflow budgets (Option E) |
| RT-02 | Persistent end-to-end breach | QM-01 | Re-decompose; tune slow hop |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-26 |
| Specification sections | 26.PF-FT-AI-PERFORMANCE-COST.md §5–§11, §16, §39, §52 |
| Requirement IDs | LAT-* |
| Build phases | 2, 8 |
| Code paths | platform-wide |
| Configuration | budget table |
| Tests | perf-regression suite |
| Upstream ADRs | ADR-D7-02, D3-19 |
| Downstream ADRs | ADR-D5-17, D7-07 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
