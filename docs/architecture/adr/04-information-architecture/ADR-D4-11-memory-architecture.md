---
id: ADR-D4-11
title: Memory architecture — short/long-term, ranking, summarisation, retention
domain: 4 Information
ws_ref: [WS-22]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [Backend Lead, Conversation Designer, Data Protection Officer]
reviewers: [Principal Architect, Security Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D4-10, ADR-D4-12, ADR-D4-01, ADR-D3-25, ADR-D4-07, ADR-D6-06]
source_docs:
  - "MD files/3 Context & Integration/9 PF-FT-AI-MEMORY-CACHE.md §5, §6, §10, §11, §12, §16, §17, §20, §22, §24, §25, §26, §27, §28, §29, §30, §32, §62, §64, §67, §68, §69, §72, §73, §74, §75, §76, §77, §78, §79"
build_phases: [7]
impacted_paths:
  - src/pf_ft_ai/memory/
classification: Internal
review_due: 2027-08-22
---

# ADR-D4-11 — Memory architecture — short/long-term, ranking, summarisation, retention

## 1. Summary

PFF AI will implement memory as **typed categories** (conversation, session, working,
workflow, agent-run, user-preference, organizational, ERC-reference, decision,
summary — doc 9 §5–§19) behind a provider-independent `MemoryStore`, with
**relevance+recency+confidence ranking** for retrieval (doc 9 §24–§28),
**summarisation** for long conversations (doc 9 §19, §64–§66), and **category-specific
retention** (doc 9 §32, §74–§75). Crucially, memory **never stores enterprise business
truth** — ERC is *referenced*, not copied (doc 9 §16–§17). Memory carries provenance
and trust and is isolated per user/club (doc 9 §69, §77–§79).

## 2. Context and Problem Statement

Doc 9 §5–§19 enumerate memory categories; §16–§17 forbid copying ERC into memory as
truth; §20–§32 cover lifecycle, storage, retrieval, ranking, confidence, trust,
write policy and retention; §62–§79 cover selection, compression, conflict,
staleness, provenance, versioning, deletion, security and isolation. Without a memory
architecture, conversations lose useful context or, worse, memory becomes a
back-door copy of enterprise data that goes stale and violates precedence. This ADR
fixes what memory is, how it is ranked and summarised, and how long it lives.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Typed memory categories behind MemoryStore | doc 9 §5–§19, §22 |
| DR-F-02 | Relevance+recency+confidence ranked retrieval | doc 9 §24–§28 |
| DR-F-03 | Summarisation for long context | doc 9 §19, §64–§66 |
| DR-C-01 | No enterprise truth in memory (ERC referenced) | doc 9 §16–§17; ADR-D4-01 |
| DR-C-02 | Category retention + per-user/club isolation | doc 9 §32, §74–§79 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Ranked retrieval improves answers without leaking stale data | Tighten trust/staleness rules | Memory eval |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Precedence safety (no stale enterprise truth) | 28 | Golden Rule | ERC-not-copied tests |
| EC-02 | Retrieval usefulness | 22 | Better continuity | Memory eval |
| EC-03 | Context-budget efficiency (summarisation) | 16 | Token cost | Tokens saved |
| EC-04 | Privacy/retention/isolation | 18 | UK GDPR/safeguarding | Retention + isolation |
| EC-05 | Simplicity/provider-independence | 16 | Maintainability + swap | Abstraction |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Typed categories + ranked retrieval + summarisation + category retention (ERC referenced, not copied)

**Description.** The full doc 9 model: categories, `MemoryStore` abstraction,
relevance/recency/confidence ranking, summary memory for long conversations,
per-category TTL/retention, provenance+trust, per-user/club isolation; ERC held as
*reference* memory (id + pointer), never copied values.
**Strengths.** Useful, safe, private, efficient, swappable.
**Weaknesses.** Most components.
**Cost / effort.** Medium.

### 5.2 Option B — Raw full-history memory (store everything, no ranking/summarisation)

**Description.** Keep the whole transcript; feed as much as fits.
**Strengths.** Simple; nothing lost.
**Weaknesses.** Token blowout; no relevance; retention/privacy risk; no trust model.
**Cost / effort.** Low; poor.

### 5.3 Option C — Summary-only memory (keep rolling summary, drop detail)

**Description.** Maintain one evolving summary.
**Strengths.** Compact.
**Weaknesses.** Lossy; can drop facts needed later; no category nuance; summary errors
propagate.
**Cost / effort.** Low; lossy.

### 5.4 Option D — Vector/semantic memory (embed and retrieve all memories by similarity)

**Description.** Treat memory like a mini-RAG over past turns.
**Strengths.** Strong relevance retrieval.
**Weaknesses.** Adds embedding/index infra for small per-conversation memory; blurs
memory/RAG separation; overkill now — but a useful *component* of A's relevance
ranking later.
**Cost / effort.** Medium-high.

### 5.5 Option E — Copy ERC into memory for fast reuse

**Description.** Cache enterprise data in memory for the conversation.
**Strengths.** Fewer ERC reads.
**Weaknesses.** Stale enterprise truth in memory — violates doc 9 §16–§17 and
precedence. The exact anti-pattern the spec forbids.
**Cost / effort.** Low; unacceptable.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No memory (stateless turns) | DR-F-02 — loses continuity |
| Cross-user shared memory | doc 9 §77–§79 — isolation |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 9 §5–§32/§62–§79.

| Criterion | Weight | A: Typed+ranked+summary | B: Raw history | C: Summary-only | D: Vector memory | E: Copy ERC |
|---|---|---|---|---|---|---|
| EC-01 Precedence safety | 28 | 5 | 3 | 3 | 4 | 1 |
| EC-02 Retrieval usefulness | 22 | 5 | 3 | 3 | 5 | 4 |
| EC-03 Budget efficiency | 16 | 5 | 1 | 5 | 4 | 3 |
| EC-04 Privacy/retention | 18 | 5 | 2 | 3 | 3 | 2 |
| EC-05 Simplicity/independence | 16 | 4 | 4 | 4 | 2 | 3 |
| **Weighted total** | **100** | **484** | **266** | **352** | **376** | **250** |

Totals (×20): **A = 484**, **D = 376**, **C = 352**, **B = 266**, **E = 250**.

**Sensitivity.** A leads by > 100. D (vector memory) is the strongest single technique
and is folded into A's relevance ranking as a *later* enhancement (RT-01). E is
rejected outright — it is the forbidden ERC-copy anti-pattern.

## 7. Decision

**PFF AI will implement typed memory categories behind a provider-independent
`MemoryStore`, with relevance+recency+confidence ranked retrieval, summarisation for
long conversations, per-category retention and per-user/club isolation; ERC is
referenced, never copied as truth (Option A).** Memory carries provenance and a trust
level; conflicting/stale memories are resolved by trust+recency (doc 9 §67–§68).
Vector/semantic retrieval (D) may later enhance ranking behind the same abstraction.
Raw-history (B), summary-only (C) and ERC-copy (E) are rejected.

**Status rationale.** `Accepted` — doc 9 governs this.

## 8. Architecture Detail

- `src/pf_ft_ai/memory/`: `MemoryStore` protocol (doc 9 §22) over Redis (ADR-D4-10);
  category models (§5–§19) including `ERCReferenceMemory` holding pointers, not values
  (§16).
- Retrieval policy (§23–§27): candidate memories ranked by relevance × recency ×
  confidence (§28), filtered by trust (§29) and staleness (§68).
- Summarisation (§19, §64): rolling summary with summary versioning (§65) and
  integrity checks (§66); feeds context assembly (ADR-D3-25) within its budget (§63).
- Retention (§32, §74–§75): per-category TTL; explicit deletion path (§75) for rights
  requests; isolation by user/club key (§77–§79).
- Write policy (§30–§31): explicit vs implicit memory; provenance stamped (§69).

## 9. Consequences

### 9.1 Positive
- Useful continuity without stale enterprise truth; privacy-respecting and efficient.
### 9.2 Negative
- Several components (ranking, summarisation, retention) to build.
### 9.3 Neutral
- Sets up context assembly (D3-25) and store (D4-10).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of raw history | Safety, privacy, efficiency | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Memory never holds enterprise truth (ERC referenced) |
| Precedence chain | Memory ranks below ERC/enterprise; trust/staleness enforced |
| Four-state separation | Memory distinct from ERC/cache/session (doc 9 §3) |
| Versioned artefacts | Summary versioning (§65) |
| Adam persona governs *how*, not *what* | Memory informs wording, not business truth |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | ERC values copied into memory | Med | High | H | ERC-reference-only model + fitness test | AI Arch Lead | Low |
| RSK-02 | Stale memory used as fact | Med | Med | M | Trust+staleness filter (§29, §68) | Backend Lead | Low |
| RSK-03 | Cross-user memory leak | Low | High | M | Isolation keys + tests (§77–§79) | Security Architect | Low |
| RSK-04 | Summary drops needed fact | Med | Med | M | Summary integrity checks (§66) | Conversation Designer | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | ERC-copied-into-memory violations | 0 | > 0 | Fitness test | Per build |
| QM-02 | Memory retrieval helpfulness | ≥ target | below | Memory eval | Per release |
| QM-03 | Retention policy coverage | 100% | < 100% | Config audit | Quarterly |
| QM-04 | Cross-user isolation tests | 100% | < 100% | CI | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Memory access authorized (doc 9 §79) |
| Data classification touched | Conversation/preference memory may be Personal |
| Personal data / PII | Retention/TTL; deletion path (§75); minimised |
| Children's data and safeguarding | No safeguarding records in memory; ERC referenced |
| UK GDPR lawful basis and rights impact | Erasure + retention supported |
| Audit and evidential requirements | Memory provenance (§69) |
| Standards touched | ISO/IEC 27001, 42001, UK GDPR |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 7 |
| Repository paths | `src/pf_ft_ai/memory/` |
| Configuration | Category retention/TTL; ranking weights |
| Contracts / schemas | Memory category models; MemoryStore protocol |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D4-10, ADR-D3-25, ADR-D4-07 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | ERC held as reference, never copied values | Fitness test |
| AC-02 | Retrieval ranks by relevance×recency×confidence | Unit test |
| AC-03 | Per-category retention enforced | Config + test |
| AC-04 | Cross-user/club isolation holds | Security test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Memory size, retrieval hit usefulness, evictions |
| Alerting | Isolation violations; retention breaches |
| Runbook | `docs/runbooks/memory.md` |
| Failure mode and degradation | Store issue → degrade to session-only context |
| Rollback | Config/version revert |
| Support model impact | Platform + DPO |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Memory subsystem | M | small | Build + storage (shares Redis, D4-10) |
| Summarisation calls | — | small | SLM cost on long convos |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Long-term memory volume/quality needs | Metrics | Add vector memory (D) + durable store (D4-10 Option E) |
| RT-02 | Memory-caused stale-fact incident | Incident | CAR; tighten trust/staleness |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-22 |
| Specification sections | doc 9 §5–§32, §62–§79 |
| Requirement IDs | MEM-* |
| Build phases | 7 |
| Code paths | `src/pf_ft_ai/memory/` |
| Configuration | retention/ranking config |
| Tests | memory eval + isolation suites |
| Upstream ADRs | ADR-D4-10, ADR-D4-01 |
| Downstream ADRs | ADR-D3-25, ADR-D4-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
