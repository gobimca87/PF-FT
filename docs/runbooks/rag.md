# RAG Runbook

**Owner:** AI Platform / Data Team (doc 28 §4) · **Severity:** P2 (doc 28 §10).

## Symptoms (doc 28 §57)

No results, retrieval timeout, vector unavailable, embedding failure, ACL failure,
incorrect citations.

## Diagnostic steps

1. Check whether this is a legitimate empty result rather than an infrastructure
   failure (doc 28 §59) — `src/pff_fa_ai/rag/pipeline.py`'s `IngestionPipeline` and
   the retrieval path in `rag/service.py` don't currently enforce
   `SourceAuthorityLevel` before ingesting (documented gap,
   `docs/security/0001-phase-15-security-hardening-pass.md` §3), so an unexpectedly
   present/absent document may trace back to that, not a runtime outage.
2. Confirm `config/base/rag.yaml` — no real RAG source/corpus has been approved yet
   (Phase 8 shipped behind interfaces only); an "empty results" report in a
   non-production environment is very likely expected, not a bug.
3. Check ACL enforcement — `tests/security/` and `rag/models.py`'s ACL fields; a
   cross-organization or expired-access retrieval must return zero results, not an
   error (doc 22 §41 mandatory ACL scenarios).
4. Check embedding/reranking stages independently (`rag/fusion.py`, `rag/reranking.py`)
   — doc 28 §52's latency breakdown (query → embedding → vector → keyword → hybrid →
   reranker → context assembly) tells you which stage to inspect first.

## Recovery

- Retrieval timeout / vector unavailable: see [`vector.md`](vector.md).
- Embedding failure: check the configured provider in `config/base/rag.yaml` —
  `embedding_vector/providers.py` — never silently fall back to a different embedding
  model without re-indexing compatibility (doc 26 §110, doc 20 §57).
- ACL failure: never disable ACL filtering to "make retrieval work" — treat as a P1
  security incident instead (doc 28 §90).

## Escalation

AI Platform / Data Team. Escalate to Security if an ACL failure allowed retrieval of
data outside the requester's authorization scope.
