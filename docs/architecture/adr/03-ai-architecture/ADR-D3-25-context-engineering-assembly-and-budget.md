---
id: ADR-D3-25
title: Context engineering — assembly order, precedence and token-budget allocation
domain: 3 AI
ws_ref: [WS-18]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [ML Engineer, Prompt Engineer, Principal Architect]
reviewers: [Principal Architect, Security Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-09, ADR-D3-12, ADR-D3-22, ADR-D2-12, ADR-D4-11, ADR-D1-03]
source_docs:
  - "MD files/4 AI/16.PF-FT-AI-PROMPT-ENGINEERING.md §20, §73, §123, §124, §125, §127, §128, §129, §130, §131, §138"
  - "MD files/4 AI/15.PF-FT-AI-SLM.md §28, §29, §30, §31, §32"
build_phases: [6, 8]
impacted_paths:
  - src/pf_ft_ai/prompt/
  - src/pf_ft_ai/context/
classification: Internal
review_due: 2027-08-22
---

# ADR-D3-25 — Context engineering — assembly order, precedence and token-budget allocation

## 1. Summary

PFF AI will assemble the model context by a **deterministic, precedence-ordered
pipeline** with an explicit **token budget allocated per source** — enterprise/ERC
context and instructions first and protected, then memory, then retrieved knowledge,
each trimmed to its budget by defined rules, with ERC summarisation/overflow handling
when large (16.PF-FT-AI-PROMPT-ENGINEERING.md §123–§131; 15.PF-FT-AI-SLM.md §28–§32). Assembly order encodes the
authoritative-truth precedence chain so that under token pressure the platform drops
the *lowest*-authority content first, never enterprise truth or safety instructions.

## 2. Context and Problem Statement

16.PF-FT-AI-PROMPT-ENGINEERING.md §123–§124 define prompt context budget and budget strategy; §125–§131 define
composition with ERC batching, RAG, memory, API/tool results and authorization;
§138 covers source authority. 15.PF-FT-AI-SLM.md §28–§32 define context budget, dynamic budget,
large-ERC handling, summarisation and overflow. The model window is finite; when
inputs exceed it, *what gets dropped* is a correctness and safety decision. Without a
policy, naive truncation could cut authoritative ERC data or a safety instruction
while keeping a low-value retrieved chunk — inverting the precedence chain. This ADR
fixes the assembly order and budget allocation.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Deterministic assembly order | 16.PF-FT-AI-PROMPT-ENGINEERING.md §20, §22 |
| DR-F-02 | Per-source token budget | 16.PF-FT-AI-PROMPT-ENGINEERING.md §123–§124; 15.PF-FT-AI-SLM.md §28–§29 |
| DR-C-01 | Assembly honours precedence (drop lowest authority first) | CLAUDE.md; 16.PF-FT-AI-PROMPT-ENGINEERING.md §138; ADR-D1-03 |
| DR-C-02 | ERC large → summarise/overflow safely | 15.PF-FT-AI-SLM.md §30–§32 |
| DR-C-03 | Trust tiers preserved (untrusted delimited) | ADR-D3-12; 16.PF-FT-AI-PROMPT-ENGINEERING.md §57 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Summarising ERC preserves decision-relevant facts | Prefer paginate/omit-with-note over lossy summary | ERC summary eval |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Precedence fidelity under pressure | 30 | Safety/correctness | Drop-order tests |
| EC-02 | Determinism & reproducibility | 20 | Auditable prompts | Same inputs→same context |
| EC-03 | Answer quality within budget | 18 | Useful context | Eval score |
| EC-04 | Safety (instructions/trust preserved) | 16 | Never drop guardrails | Instruction-retention tests |
| EC-05 | Cost (token efficiency) | 10 | Spend | tokens/turn |
| EC-06 | Simplicity | 6 | Maintainability | Concepts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Precedence-ordered assembly with per-source budgets + graceful degradation

**Description.** Fixed order: system+safety instructions → persona → task →
authorization/ERC (protected) → memory → retrieved knowledge → user turn (delimited).
Each source has a token budget; when total exceeds the window, trim from the
*lowest-authority* end (retrieved first, then memory), summarise large ERC (15.PF-FT-AI-SLM.md
§31), never drop instructions or authoritative ERC facts.
**Strengths.** Precedence-faithful; deterministic; safe; tunable budgets.
**Weaknesses.** Requires budget bookkeeping + ERC summarisation.
**Cost / effort.** Medium.

### 5.2 Option B — Naive truncation (cut from the end / oldest)

**Description.** Concatenate and truncate to fit.
**Strengths.** Trivial.
**Weaknesses.** Can cut authoritative ERC or safety instructions; non-deterministic
quality; unsafe.
**Cost / effort.** Low; unsafe.

### 5.3 Option C — Relevance-ranked packing (fit highest-similarity content regardless of source)

**Description.** Rank all candidate content by relevance score, pack greedily.
**Strengths.** Maximises topical relevance.
**Weaknesses.** Ignores authority — a high-similarity retrieved chunk could crowd out
lower-similarity but authoritative ERC; inverts precedence.
**Cost / effort.** Medium; unsafe for precedence.

### 5.4 Option D — Summarise-everything to fit

**Description.** Summarise all sources aggressively.
**Strengths.** Fits large inputs.
**Weaknesses.** Lossy on authoritative facts/IDs; summarisation errors on business
data are dangerous; slow (extra model calls).
**Cost / effort.** High; risky.

### 5.5 Option E — Model-managed context (let the model request what it needs — tool-augmented context)

**Description.** Give the model tools to fetch context on demand rather than
pre-assembling.
**Strengths.** Fetches only what's needed; scales to huge corpora.
**Weaknesses.** Non-deterministic; more round-trips/latency; harder to guarantee
precedence and budget; better as a *later* pattern for very large contexts.
**Cost / effort.** High; premature.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No budget (rely on window being big enough) | Overflow inevitable at large ERC (15.PF-FT-AI-SLM.md §30) |
| Drop instructions to fit data | DR-C-01/EC-04 — safety violation |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 16.PF-FT-AI-PROMPT-ENGINEERING.md §123–§131/§138 and 15.PF-FT-AI-SLM.md
§28–§32, and the precedence chain (ADR-D1-03).

| Criterion | Weight | A: Precedence+budgets | B: Naive trunc | C: Relevance packing | D: Summarise-all | E: Model-managed |
|---|---|---|---|---|---|---|
| EC-01 Precedence fidelity | 30 | 5 | 1 | 2 | 3 | 3 |
| EC-02 Determinism | 20 | 5 | 3 | 3 | 3 | 2 |
| EC-03 Answer quality | 18 | 4 | 2 | 5 | 3 | 4 |
| EC-04 Safety | 16 | 5 | 1 | 2 | 3 | 3 |
| EC-05 Cost | 10 | 4 | 5 | 4 | 2 | 3 |
| EC-06 Simplicity | 6 | 3 | 5 | 3 | 2 | 2 |
| **Weighted total** | **100** | **458** | **222** | **306** | **288** | **300** |

Totals (×20): **A = 458**, **C = 306**, **E = 300**, **D = 288**, **B = 222**.

**Sensitivity.** A dominates on the two highest-weighted criteria (precedence,
safety). C scores best on raw quality but fails precedence — unacceptable. E is a
future option for very large contexts (RT-02). A can *incorporate* relevance ranking
*within* each source's budget, capturing C's benefit without inverting authority.

## 7. Decision

**PFF AI will assemble context via a deterministic, precedence-ordered pipeline with
per-source token budgets and graceful degradation (Option A).** Instructions,
persona, task and authorization/ERC context are assembled first and protected;
memory and retrieved knowledge follow within their budgets; under token pressure the
platform trims from the lowest-authority end and summarises large ERC per 15.PF-FT-AI-SLM.md §31,
never dropping instructions or authoritative facts. Relevance ranking is applied
*within* each source's budget. Naive truncation (B), authority-blind packing (C) and
summarise-everything (D) are rejected; model-managed context (E) is a future option
for very large contexts.

**Status rationale.** `Accepted` — 16.PF-FT-AI-PROMPT-ENGINEERING.md §123–§131 and 15.PF-FT-AI-SLM.md §28–§32 govern this;
ADR records the rationale.

## 8. Architecture Detail

- **Pipeline** `src/pf_ft_ai/context/` + prompt composer (ADR-D3-09): ordered stages
  each with a `token_budget`; a tokenizer-aware counter (15.PF-FT-AI-SLM.md §27; 16.PF-FT-AI-PROMPT-ENGINEERING.md §122)
  enforces budgets.
- **Order** (highest→lowest authority): system/safety instructions → persona → task →
  authorization + ERC (protected, ADR-D2-12) → memory (ADR-D4-11) → retrieved
  knowledge (ADR-D3-22, delimited per ADR-D3-12) → user turn.
- **ERC handling** (15.PF-FT-AI-SLM.md §30–§32): large ERC is paginated/batched (MAX_ERC_BATCH_SIZE
  = 20) and summarised only with a lossless-for-decisions strategy; overflow raises a
  handled condition, never silent truncation of facts.
- **Degradation**: when trimming, emit a trace note of what was omitted; if
  authoritative content cannot fit, prefer a follow-up turn / clarification over
  dropping it.
- **Trust**: untrusted segments carry nonce delimiters (ADR-D3-12).

## 9. Consequences

### 9.1 Positive
- Under pressure the platform degrades knowledge, never authority or safety.
- Deterministic, auditable, reproducible prompts.
### 9.2 Negative
- Budget bookkeeping + ERC summarisation complexity.
### 9.3 Neutral
- Ties together ERC (D2-12), memory (D4-11) and RAG (D3-22) into one assembly.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Max topical relevance packing (C) | Precedence fidelity & safety | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Authoritative ERC is protected in assembly |
| Precedence chain | Assembly order *is* the precedence chain; lowest authority dropped first |
| Four-state separation | Each state source has its own budgeted slot |
| Versioned artefacts | Assembly config/budgets versioned |
| Adam persona governs *how*, not *what* | Persona slot fixed; never displaces facts |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Authoritative fact trimmed to fit | Low | High | M | Protected slots + follow-up over drop | AI Arch Lead | Low |
| RSK-02 | ERC summary loses a decision-relevant fact | Med | High | H | Lossless-for-decisions summary + eval (DR-A-01) | ML Eng | Med |
| RSK-03 | Non-deterministic assembly | Low | Med | M | Deterministic pipeline + tests | AI Arch Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Authoritative content retained under pressure | 100% | < 100% | Drop-order tests | Per release |
| QM-02 | Assembly determinism (same in→same out) | 100% | < 100% | Test | Per release |
| QM-03 | Token budget adherence | 100% | overflow | Tokenizer counter | Continuous |
| QM-04 | ERC-summary factual retention | ≥ target | below | ERC summary eval | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Trust tiers + delimiters preserved in assembly |
| Data classification touched | Mixed; ERC may be Confidential/Personal — minimised per ADR-D6-07 |
| Personal data / PII | Only necessary ERC fields assembled |
| Children's data and safeguarding | Safeguarding context handled within protected ERC slot |
| UK GDPR lawful basis and rights impact | Data minimisation in assembly |
| Audit and evidential requirements | Assembly recorded (prompt snapshot, 16.PF-FT-AI-PROMPT-ENGINEERING.md §89) |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 (composition), 8 (RAG integration) |
| Repository paths | `src/pf_ft_ai/context/`, `src/pf_ft_ai/prompt/` |
| Configuration | Per-source budgets; order config; summary strategy |
| Contracts / schemas | Context assembly contract; token counts |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-09, ADR-D2-12, ADR-D4-11, ADR-D3-22, ADR-D3-12 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Under overflow, retrieved knowledge dropped before ERC/instructions | Drop-order test |
| AC-02 | Same inputs produce identical assembled context | Determinism test |
| AC-03 | Budgets never exceeded (tokenizer-aware) | Unit test |
| AC-04 | ERC summary preserves decision-relevant facts | Summary eval |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Token usage per source; trims/summaries; omitted-content notes |
| Alerting | Frequent authoritative-content pressure; overflow errors |
| Runbook | `docs/runbooks/context.md` |
| Failure mode and degradation | Overflow → summarise/paginate/follow-up, never silent fact loss |
| Rollback | Revert budgets/order config |
| Support model impact | AI platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Assembly pipeline + counter | M | negligible | Build |
| ERC summarisation calls | — | small | Only on large ERC |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Frequent authoritative-content pressure | QM-01/traces | Increase window/model or restructure ERC |
| RT-02 | Contexts routinely exceed window | Token metrics | Evaluate model-managed context (Option E) |
| RT-03 | ERC-summary factual loss incident | Incident | CAR; tighten summary strategy |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-18 Context Engineering |
| Specification sections | 16.PF-FT-AI-PROMPT-ENGINEERING.md §20, §73, §123–§131, §138; 15.PF-FT-AI-SLM.md §28–§32 |
| Requirement IDs | CTX-* |
| Build phases | 6, 8 |
| Code paths | `src/pf_ft_ai/context/`, `src/pf_ft_ai/prompt/` |
| Configuration | budgets/order/summary config |
| Tests | drop-order + determinism + summary suites |
| Upstream ADRs | ADR-D3-09, ADR-D2-12, ADR-D4-11, ADR-D3-22 |
| Downstream ADRs | — |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
