---
id: ADR-D3-26
title: RAG retrieval invocation — tool contract, execution model, agentic loop bound
domain: 3 AI
ws_ref: [WS-17]
status: Accepted
version: 1.0.0
date: 2026-08-23
decision_owner: AI Architecture Lead
contributors: [Backend Lead, Security Architect]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-22, ADR-D3-04, ADR-D3-05, ADR-D2-09, ADR-D4-12, ADR-D5-18]
source_docs:
  - "MD files/4 AI/13.PFF-FA-AI-RAG.md §105, §106, §107, §108, §109, §110, §111, §112, §113, §114, §115"
build_phases: [8]
impacted_paths:
  - src/pff_fa_ai/rag/retrieval/
  - src/pff_fa_ai/harness/
classification: Internal
review_due: 2027-08-23
---

# ADR-D3-26 — RAG retrieval invocation — tool contract, execution model, agentic loop bound

## 1. Summary

PFF AI will expose RAG retrieval as a **harness-gated tool (`rag.search`)** with an
explicit input contract and limits, invoked either by deterministic supervisor routing
or by the agent within its declared scope (never by free-form model text) — and once
invoked, retrieval **executes deterministically** inside the RAG service (13.PFF-FA-AI-RAG.md
§106, §110). Iterative "agentic" retrieval is supported but **bounded to a fixed
`max_iterations`** (13.PFF-FA-AI-RAG.md §108–§109) to prevent retrieval loops and uncontrolled
cost. This closes a gap in [ADR-D3-22](ADR-D3-22-retrieval-reranking-and-citation.md),
which fixes what happens *once* retrieval runs but not how it is *called*.

## 2. Context and Problem Statement

ADR-D3-22 fixes the retrieval pipeline (ACL filter → hybrid search → fusion → rerank →
threshold → context selection) but leaves open exactly how that pipeline is triggered
within a conversation turn. 13.PFF-FA-AI-RAG.md §106 defines a `rag.search` tool contract; §107 sets
tool limits (max query length, max `top_k`, max filters, max query expansions, max
retrieval rounds, max context tokens); §108–§109 describe optional agentic (iterative)
RAG bounded by `max_iterations`; §110 states that the *decision* to retrieve may be
made by the Supervisor/LangGraph or the agent, but the *retrieval execution itself
remains deterministic* within the RAG service — it is never something the model
improvises turn by turn. Without this ADR, retrieval could be invoked inconsistently
(sometimes a tool call, sometimes an ungated pre-fetch), agentic RAG could loop
unboundedly, and the tool-calling security boundary (ADR-D3-04) would have no RAG-
specific contract to gate against.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | RAG exposed as a formal, harness-gated tool contract | 13.PFF-FA-AI-RAG.md §106 |
| DR-F-02 | Tool limits enforced (query length, top_k, filters, expansions, rounds, tokens) | 13.PFF-FA-AI-RAG.md §107 |
| DR-C-01 | Retrieval execution deterministic once invoked | 13.PFF-FA-AI-RAG.md §110 |
| DR-F-03 | Agentic/iterative retrieval bounded by max_iterations | 13.PFF-FA-AI-RAG.md §108–§109 |
| DR-C-02 | No arbitrary/free-form retrieval invocation by the model | ADR-D3-04 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Most turns need at most one retrieval round | Raise default max_iterations | Retrieval analytics |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Determinism & security (no ungated invocation) | 30 | Core risk this ADR closes | Gate coverage |
| EC-02 | Cost/loop control (bounded iteration) | 22 | Prevent runaway retrieval cost | Loop-limit enforcement |
| EC-03 | Flexibility (handles multi-part questions) | 18 | UX quality | Coverage of complex queries |
| EC-04 | Latency | 16 | Within budget (ADR-D5-18) | p95 retrieval-call latency |
| EC-05 | Simplicity | 14 | Maintainability | Concepts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Harness-gated `rag.search` tool, deterministic execution, bounded agentic loop (max_iterations = 2)

**Description.** RAG is registered as a tool (13.PFF-FA-AI-RAG.md §106) callable either by
deterministic supervisor routing (ADR-D3-05, for clear knowledge-intents) or by the
agent within its declared tool scope (ADR-D3-03/D3-04); every call passes through the
harness gate (ADR-D2-09) which enforces the tool limits (§107); once invoked, the
pipeline (ADR-D3-22) runs deterministically; an optional evidence-sufficiency check
after the first round may trigger one further round, capped at `max_iterations = 2`
(§108–§109).
**Strengths.** Secure (harness-gated, ADR-D3-04-consistent); deterministic; cost-bounded;
handles the common multi-part question without unbounded looping.
**Weaknesses.** Two-round cap may occasionally under-serve very complex questions.
**Cost / effort.** Low — reuses the existing harness and tool-gate machinery.

### 5.2 Option B — Deterministic pre-fetch (RAG always runs before the SLM call for knowledge-classified intents, not modelled as a callable tool)

**Description.** The workflow graph pre-fetches RAG context deterministically for any
intent classified as knowledge-seeking (ADR-D3-06), before the SLM is ever called; no
tool-call surface at all.
**Strengths.** Simplest; fully deterministic; no agentic-loop risk.
**Weaknesses.** Cannot adapt mid-turn if the first retrieval is insufficient (no
evidence-sufficiency check); wastes a retrieval call on turns where the model
determines context isn't actually needed; doesn't match 13.PFF-FA-AI-RAG.md §110's framing of RAG
as something the Supervisor/agent *may* invoke.
**Cost / effort.** Low; less capable.

### 5.3 Option C — Model-initiated free-form retrieval (no formal tool contract; the SLM emits a search query in text, parsed downstream)

**Description.** The model writes a "search for: ..." instruction in its output, parsed
by a downstream regex/heuristic into a retrieval call.
**Strengths.** No tool-schema plumbing.
**Weaknesses.** Not deterministic; not gated (ADR-D3-04 requires structured tool calls,
not parsed text); injection-prone; violates 13.PFF-FA-AI-RAG.md §110's determinism requirement.
**Cost / effort.** Low; unsafe — the exact anti-pattern ADR-D3-04 exists to prevent.

### 5.4 Option D — Always-on RAG for every turn (unconditional retrieval, no invocation decision)

**Description.** Every turn retrieves, regardless of whether the intent needs
knowledge.
**Strengths.** Never "misses" a case where knowledge would have helped.
**Weaknesses.** Wastes latency/cost on the majority of turns that don't need RAG
(business-state questions, ADR-D3-20, or pure chit-chat); no routing intelligence.
**Cost / effort.** Low build, high runtime cost.

### 5.5 Option E — Harness-gated tool + bounded agentic loop (as A) + semantic result caching for repeated queries

**Description.** Option A plus a semantic cache (ADR-D4-12) keyed on normalised
query+filter, serving repeated/near-duplicate queries without re-running the full
pipeline.
**Strengths.** A's safety and cost-bound properties plus reduced latency/cost on
repeated queries.
**Weaknesses.** Cache-staleness and cache-key-normalisation complexity; given the
small, low-churn corpus (ADR-D3-21), the win is modest.
**Cost / effort.** Medium; a worthwhile later optimisation, not a day-one requirement.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Unbounded agentic RAG (no iteration cap) | 13.PFF-FA-AI-RAG.md §109 — explicit loop-limit requirement |
| RAG invoked directly by any node without harness gating | ADR-D3-04 — mandatory tool-validation boundary |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 13.PFF-FA-AI-RAG.md §105–§115 and the tool-gate
model of ADR-D3-04.

| Criterion | Weight | A: Gated tool + bounded loop | B: Deterministic pre-fetch | C: Free-form model invocation | D: Always-on | E: A + semantic cache |
|---|---|---|---|---|---|---|
| EC-01 Determinism/security | 30 | 5 | 4 | 1 | 4 | 5 |
| EC-02 Loop/cost control | 22 | 5 | 5 | 1 | 2 | 5 |
| EC-03 Flexibility | 18 | 5 | 2 | 4 | 3 | 5 |
| EC-04 Latency | 16 | 4 | 4 | 3 | 2 | 5 |
| EC-05 Simplicity | 14 | 4 | 5 | 3 | 5 | 3 |
| **Weighted total** | **100** | **462** | **372** | **220** | **298** | **476** |

Totals (×20): **E = 476**, **A = 462**, **B = 372**, **D = 298**, **C = 220**.

**Sensitivity.** E (A + semantic cache) edges A on latency, but the win is small given
the low-churn, small corpus (ADR-D3-21) — most queries are not literal repeats. **A is
adopted as the baseline; the semantic-cache layer (E) is a documented future
optimisation** rather than a day-one requirement, revisited if repeated-query volume
proves material (RT-01). Free-form invocation (C) is decisively rejected — it is the
precise anti-pattern the tool-validation boundary (ADR-D3-04) exists to close.

## 7. Decision

**PFF AI will expose RAG retrieval as a harness-gated tool (`rag.search`) with the
input contract and limits of 13.PFF-FA-AI-RAG.md §106–§107, invocable by deterministic supervisor
routing or by the agent within its declared scope, executing deterministically once
invoked, with agentic (iterative) retrieval bounded to `max_iterations = 2` (Option
A).** A semantic result cache (Option E) is a documented future optimisation, not
required at launch. Deterministic pre-fetch (B), free-form model invocation (C) and
always-on retrieval (D) are rejected.

**Status rationale.** `Accepted` — 13.PFF-FA-AI-RAG.md §106–§110 fix the tool-contract and
determinism requirements directly; this ADR records the alternatives and the chosen
iteration bound.

## 8. Architecture Detail

- `src/pff_fa_ai/rag/retrieval/tool.py`: registers `rag.search(query: str, filters:
  dict, top_k: int) -> RetrievalResult` with the tool registry (ADR-D3-03); limits
  (13.PFF-FA-AI-RAG.md §107) enforced at the harness gate (ADR-D2-09, ADR-D3-04 gate 3 — semantic
  parameter validation) before the call reaches the retrieval pipeline (ADR-D3-22).
- **Invocation path**: for intents the intent classifier (ADR-D3-06) resolves
  deterministically to "needs knowledge", the supervisor calls `rag.search` directly
  (ADR-D3-05's deterministic-routing branch); for intents where the agent must decide
  whether knowledge is needed mid-reasoning, the agent calls the same tool through the
  harness (model-decided branch) — both paths converge on one gated tool, never a
  bespoke code path.
- **Agentic loop** (13.PFF-FA-AI-RAG.md §108–§109): after a retrieval round, an evidence-
  sufficiency check (grounded in the citation/threshold logic of ADR-D3-22 §69–§71)
  may trigger exactly one further round if evidence is insufficient; a hard counter
  enforces `max_iterations = 2`; on exhaustion, the platform answers with what it has
  or declines honestly (ADR-D3-22 §7) — it never loops silently.
- Config: `max_iterations`, per-limit values (query length, top_k, filters,
  expansions, context tokens) live in versioned config (ADR-D5-06), not hard-coded.

## 9. Consequences

### 9.1 Positive
- One deterministic, gated, auditable retrieval-invocation path regardless of whether
  routing or the agent decided to retrieve.
- Retrieval cost and latency are bounded and predictable.

### 9.2 Negative
- Two-round cap may occasionally leave a genuinely complex multi-part question
  under-served (mitigated: honest "no confident answer" rather than fabrication).

### 9.3 Neutral
- Establishes the tool-contract pattern that a future semantic cache (E) or richer
  query-planning (ADR-D3-22 §5.5 Option E) would layer onto.

### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Unbounded iterative refinement | Predictable cost, no retrieval loops | AI Architecture Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Retrieval invocation gathers knowledge only; never a business decision |
| Precedence chain | Retrieved content still ranks below ERC/enterprise regardless of how it was fetched |
| Four-state separation | Tool invocation touches no enterprise/session state directly |
| Versioned artefacts | Tool limits and iteration bound are versioned config |
| Adam persona governs *how*, not *what* | Persona narrates retrieved, cited content; invocation mechanics are invisible to it |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Agentic loop runs away despite cap (bug) | Low | Med | M | Hard counter + tests; alert on cap-hit rate | Backend Lead | Low |
| RSK-02 | Model bypasses the tool gate | Low | High | M | Harness enforces tool-only invocation (ADR-D3-04) | Security Architect | Low |
| RSK-03 | Two-round cap under-serves complex queries | Med | Low | L | Honest decline; revisit cap if pattern recurs | AI Architecture Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Retrieval calls outside the gated tool path | 0 | > 0 | Harness audit | Continuous |
| QM-02 | Agentic-loop cap-hit rate | tracked | > 20% of retrievals | Langfuse | Weekly |
| QM-03 | p95 retrieval-call latency | ≤ 120 ms/round | > 250 ms | App Insights | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Closes an ungated-retrieval path; all calls harness-validated |
| Data classification touched | Internal knowledge (per ADR-D3-20 scope) |
| Personal data / PII | None — RAG remains knowledge-only |
| Children's data and safeguarding | ACL enforcement (ADR-D6-12) applies identically regardless of invocation path |
| UK GDPR lawful basis and rights impact | Not applicable — no personal data in this path |
| Audit and evidential requirements | Every retrieval call traced (ADR-D7-02) with iteration count |
| Standards touched | ISO/IEC 42001, OWASP LLM Top 10 (excessive agency) |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 8 |
| Repository paths | `src/pff_fa_ai/rag/retrieval/`, `src/pff_fa_ai/harness/` |
| Configuration | Tool limits, `max_iterations` |
| Contracts / schemas | `rag.search` tool schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-22, D3-04, D3-05, D2-09 |
| Effort estimate | S — thin wrapper over existing harness + pipeline |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | RAG is only reachable via the gated `rag.search` tool | Code/harness audit |
| AC-02 | Tool limits enforced (reject over-limit calls) | Unit test |
| AC-03 | Agentic loop never exceeds `max_iterations` | Fault-injection test |
| AC-04 | Both deterministic-routing and agent-decided paths converge on one tool | Integration test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Retrieval-call volume, iteration counts, cap-hit rate |
| Alerting | Cap-hit rate spike; ungated-call detection |
| Runbook | `docs/runbooks/rag.md` |
| Failure mode and degradation | Retrieval failure mid-loop → honest decline (ADR-D3-22 §7) |
| Rollback | Config revert (limits/iteration bound) |
| Support model impact | AI platform team |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Tool wrapper + gate integration | S | negligible | Build |
| Bounded agentic second round | — | small | ≤1 extra retrieval round on a minority of turns |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Repeated-query volume becomes material | Query analytics | Adopt semantic cache (Option E) |
| RT-02 | Cap-hit rate consistently high | QM-02 | Raise `max_iterations` or add query decomposition |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-17 RAG & Retrieval |
| Specification sections | 13.PFF-FA-AI-RAG.md §105–§115 |
| Requirement IDs | RAG-INVOKE-* |
| Build phases | 8 |
| Code paths | `src/pff_fa_ai/rag/retrieval/`, `src/pff_fa_ai/harness/` |
| Configuration | tool limits, iteration bound |
| Tests | harness-gate + loop-bound suites |
| Upstream ADRs | ADR-D3-22, D3-04, D3-05 |
| Downstream ADRs | — |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-23 | AI Architecture Lead | Initial decision recorded — closes the retrieval-invocation gap identified after the initial 136-ADR pass. |
