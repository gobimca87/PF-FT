---
id: ADR-D3-22
title: Retrieval, reranking and mandatory-citation policy
domain: 3 AI
ws_ref: [WS-17]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [ML Engineer, Security Architect, Domain SME]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-20, ADR-D3-21, ADR-D3-23, ADR-D3-24, ADR-D3-25, ADR-D6-12]
source_docs:
  - "MD files/4 AI/13.FP-FT-AI-RAG.md §51, §52, §53, §54, §63, §64, §65, §66, §67, §68, §69, §70, §71, §81, §82, §83, §88, §89, §90, §91, §92"
build_phases: [8]
impacted_paths:
  - src/pf_ft_ai/rag/retrieval/
classification: Internal
review_due: 2027-08-22
---

# ADR-D3-22 — Retrieval, reranking and mandatory-citation policy

## 1. Summary

PFF AI will retrieve with **hybrid search (vector + lexical) → fusion → reranking →
score-threshold filtering**, and will enforce **mandatory citation**: every knowledge
claim in an answer must map to a retrieved, cited chunk, or the claim is not made
(13.FP-FT-AI-RAG.md §51–§71, §81–§92). Below the score threshold, the platform says it doesn't
have a confident answer rather than fabricating. This turns retrieval quality and
citation integrity into enforceable, measured properties.

## 2. Context and Problem Statement

13.FP-FT-AI-RAG.md §51–§54 define vector/keyword/hybrid retrieval and why hybrid; §63–§71 cover
candidate fusion, reranking, score thresholds and no-/low-result handling; §81–§92
define the citation architecture, integrity and validation. The two failure modes to
prevent are (a) missing the right passage (retrieval quality) and (b) asserting
unsupported claims (citation/hallucination). Exact identifiers (club IDs, WGS IDs)
retrieve poorly on dense vectors alone, motivating hybrid. Without a decision,
retrieval is dense-only and citations are optional, producing confident but
unsupported answers.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | High recall + precision on knowledge queries | 13.FP-FT-AI-RAG.md §53–§54, §65 |
| DR-F-02 | Exact-identifier retrieval | 13.FP-FT-AI-RAG.md §52 (keyword); ADR-D3-23 |
| DR-F-03 | Every claim cited or not made | 13.FP-FT-AI-RAG.md §81, §82, §88, §91 |
| DR-F-04 | Low-confidence/no-result handled honestly | 13.FP-FT-AI-RAG.md §69–§71 |
| DR-C-01 | ACL filtering before/at retrieval | 13.FP-FT-AI-RAG.md §61–§62; ADR-D6-12 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Reranking materially improves precision at this corpus | Drop reranker to cut latency | Retrieval eval with/without |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Retrieval quality (recall+precision) | 28 | Core | Recall@5, nDCG on golden set |
| EC-02 | Citation integrity | 24 | Anti-hallucination | Cited-claim rate; citation validity |
| EC-03 | Exact-identifier handling | 14 | FA IDs common | Exact-ID eval slice |
| EC-04 | Honest low-confidence behaviour | 12 | No fabrication | Ungrounded rate |
| EC-05 | Latency | 12 | Within budget (13.FP-FT-AI-RAG.md §88) | p95 retrieval |
| EC-06 | Cost/complexity | 10 | Keep lean | Added components |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Hybrid retrieval + fusion + reranker + threshold + mandatory citation

**Description.** Vector + BM25 candidates, fused (13.FP-FT-AI-RAG.md §64), reranked (§65–§67),
score-thresholded (§69); answers cite mapped chunks (§83) and validate citations
(§91); below threshold → "no confident answer" (§70–§71).
**Strengths.** Best quality + exact-ID handling + strong anti-hallucination.
**Weaknesses.** Reranker adds a step/latency.
**Cost / effort.** Medium.

### 5.2 Option B — Vector-only retrieval, mandatory citation

**Description.** Dense retrieval only; still cite.
**Strengths.** Simpler; lower latency.
**Weaknesses.** Weak on exact identifiers; lower precision without rerank.
**Cost / effort.** Low; lower quality.

### 5.3 Option C — Hybrid retrieval, no reranker, mandatory citation

**Description.** Vector+BM25 fused, no rerank.
**Strengths.** Good recall; less latency than A.
**Weaknesses.** Precision@k lower than with a reranker; more marginal chunks in
context (harms ADR-D3-25 budget).
**Cost / effort.** Low-medium.

### 5.4 Option D — Retrieval with optional/soft citation

**Description.** Cite where convenient; allow uncited claims.
**Strengths.** Simpler prompts.
**Weaknesses.** Permits unsupported claims — violates 13.FP-FT-AI-RAG.md §82; the core risk.
**Cost / effort.** Low; unsafe.

### 5.5 Option E — Agentic multi-hop retrieval (query planning + iterative retrieval)

**Description.** Decompose queries, retrieve iteratively (13.FP-FT-AI-RAG.md §108–§113).
**Strengths.** Handles complex multi-part questions.
**Weaknesses.** Higher latency/cost; loop-limit governance (§109); overkill for the
current FAQ/knowledge scope. A worthwhile *later* enhancement layered on A.
**Cost / effort.** High; premature.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Keyword-only retrieval | Misses paraphrase/semantic matches (DR-F-01) |
| No score threshold (always answer top-k) | DR-F-04 — fabrication risk |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 13.FP-FT-AI-RAG.md §51–§92 and the corpus
profile (ADR-D3-21). Reranker value assessed against the small, high-quality corpus.

| Criterion | Weight | A: Hybrid+rerank+cite | B: Vector+cite | C: Hybrid no-rerank | D: Soft citation | E: Agentic multi-hop |
|---|---|---|---|---|---|---|
| EC-01 Retrieval quality | 28 | 5 | 3 | 4 | 4 | 5 |
| EC-02 Citation integrity | 24 | 5 | 5 | 5 | 2 | 5 |
| EC-03 Exact-ID | 14 | 5 | 2 | 5 | 4 | 5 |
| EC-04 Low-confidence honesty | 12 | 5 | 4 | 4 | 2 | 5 |
| EC-05 Latency | 12 | 3 | 5 | 4 | 5 | 2 |
| EC-06 Cost/complexity | 10 | 3 | 5 | 4 | 5 | 2 |
| **Weighted total** | **100** | **456** | **384** | **436** | **336** | **436** |

Totals (×20): **A = 456**, **C = 436**, **E = 436**, **B = 384**, **D = 336**.

**Sensitivity.** A leads C by 20, entirely on precision (reranker). If retrieval eval
shows the reranker adds little at this corpus size, C is the fallback (drop reranker
to cut latency, RT-01). E ties C but its latency/cost make it a future enhancement,
not the baseline. D is rejected outright (unsupported claims).

## 7. Decision

**PFF AI will use hybrid retrieval (vector + BM25) with fusion, a reranker, and a
score threshold, and will enforce mandatory citation (Option A).** Every knowledge
claim maps to a cited chunk (13.FP-FT-AI-RAG.md §83) and citations are validated (§91); below the
confidence threshold the platform states it has no confident answer (§70–§71). Exact
identifiers are served by the lexical leg (§52). Reranking is retained unless
retrieval eval shows it adds little at this corpus size (fallback to Option C).
Agentic multi-hop (E) is a documented future enhancement; soft citation (D) is
forbidden.

**Status rationale.** `Accepted` — 13.FP-FT-AI-RAG.md §51–§92 govern this; ADR records rationale.

## 8. Architecture Detail

- **Pipeline** `src/pf_ft_ai/rag/retrieval/`: ACL filter (ADR-D6-12) → hybrid search
  in the vector store (ADR-D3-24) → candidate fusion (§64) → reranker (§65–§67) →
  threshold (§69) → context selection (§72, feeding ADR-D3-25).
- **Query handling**: optional query rewrite/expansion (§57–§58) within loop limits;
  no decomposition in the baseline (that is Option E).
- **Citation** (§81–§92): each selected chunk carries citation metadata; the prompt
  requires claims to reference chunk citations; a post-generation citation validator
  (§91) checks that cited chunks support the claims; citation failure → repair or
  decline (§92).
- **No/low result** (§70–§71): honest "no confident answer" response; never
  fabricate.

## 9. Consequences

### 9.1 Positive
- High-quality, exact-ID-capable retrieval with enforceable anti-hallucination.
### 9.2 Negative
- Reranker latency; citation validation adds a step.
### 9.3 Neutral
- Selected chunks flow into context engineering (ADR-D3-25).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Some latency (reranker + citation check) | Precision + citation integrity | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | RAG informs with cited knowledge only (ADR-D3-20) |
| Precedence chain | Retrieved content ranks below ERC/enterprise |
| Four-state separation | Knowledge plane only |
| Versioned artefacts | Retrieval config + reranker version pinned |
| Adam persona governs *how*, not *what* | Persona narrates cited facts; never uncited claims |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Unsupported claim slips through | Low | High | M | Mandatory citation + validator (§91) | AI Arch Lead | Low |
| RSK-02 | Exact-ID query misses | Med | Med | M | Lexical leg + eval slice | ML Eng | Low |
| RSK-03 | Reranker latency over budget | Med | Med | M | Fallback to Option C; tune top-k | ML Eng | Low |
| RSK-04 | ACL bypass in retrieval | Low | High | M | Filter before retrieval + tests (ADR-D6-12) | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Recall@5 | ≥ 0.90 | < 0.85 | Eval (§129–§130) | Per index build |
| QM-02 | Cited-claim rate | 100% | < 98% | Citation eval (§135) | Per release |
| QM-03 | Ungrounded-answer rate | ≈ 0 | rising | Eval (§117) | Per release |
| QM-04 | p95 retrieval latency | ≤ 120 ms | > 250 ms | Langfuse | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | ACL filtering + citation reduce leakage/hallucination |
| Data classification touched | Internal; ACL-restricted subsets |
| Personal data / PII | Knowledge only (ADR-D3-20) |
| Children's data and safeguarding | ACL restricts sensitive safeguarding knowledge (ADR-D6-12) |
| UK GDPR lawful basis and rights impact | Minimal |
| Audit and evidential requirements | Citations = provenance (§176–§178) |
| Standards touched | ISO/IEC 42001, 27001, NIST AI RMF |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 8 |
| Repository paths | `src/pf_ft_ai/rag/retrieval/` |
| Configuration | Fusion weights, reranker model/version, threshold |
| Contracts / schemas | Retrieval request/response; citation metadata |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-23, ADR-D3-24, ADR-D6-12, ADR-D3-25 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Recall@5 ≥ 0.90 on golden set | Eval gate |
| AC-02 | Every claim cited or answer declined | Citation eval |
| AC-03 | Below threshold → honest no-answer | Unit/eval test (§70) |
| AC-04 | ACL filter applied before retrieval | Security test (ADR-D6-12) |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Recall/precision, citation rate, latency (§127–§128) |
| Alerting | Quality/citation regression; latency breach |
| Runbook | `docs/runbooks/rag.md` |
| Failure mode and degradation | Retrieval timeout/partial → honest degraded answer (§122–§124) |
| Rollback | Revert retrieval config/reranker version |
| Support model impact | AI platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Retrieval pipeline + reranker | M | low | Build; reranker compute small at scale |
| Citation validation | S | small | Per answer |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Reranker adds little quality | Eval A vs C | Drop reranker (Option C) |
| RT-02 | Complex multi-part questions common | Query analytics | Add agentic multi-hop (Option E) |
| RT-03 | Citation rate < 98% | QM-02 | Strengthen citation validation |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-17 |
| Specification sections | 13.FP-FT-AI-RAG.md §51–§71, §81–§92, §127–§135 |
| Requirement IDs | RAG-RET-* |
| Build phases | 8 |
| Code paths | `src/pf_ft_ai/rag/retrieval/` |
| Configuration | fusion/reranker/threshold config |
| Tests | retrieval + citation + ACL suites |
| Upstream ADRs | ADR-D3-20, ADR-D3-23, ADR-D3-24 |
| Downstream ADRs | ADR-D3-25, ADR-D6-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
