# Vector Runbook

**Owner:** Data / AI Platform (doc 28 §4) · **Severity:** P2 (doc 28 §10).

## Status note

The vector store is still an open ADR decision (`docs/adr/0003-deferred-decisions-log.md`)
— `src/pf_ft_ai/embedding_vector/vector_store.py` is an interface only, with no
production backend selected among the candidates (Azure AI Search, Pinecone, Qdrant,
Weaviate, Milvus, pgvector, OpenSearch, Elasticsearch, Redis Vector Search, Chroma).
This runbook documents the *interface-level* diagnostic steps that apply regardless of
which backend is eventually chosen; add backend-specific steps once the ADR closes.

## Symptoms (doc 28 §60)

Index unavailable, capacity, connection failure, latency, storage, version mismatch.

## Diagnostic steps

1. Confirm which `VectorStore` implementation is actually wired for the environment —
   check `embedding_vector/registry.py` and the relevant `config/base/*.yaml` entry.
2. Check embedding/vector compatibility (doc 20 §58, doc 26 §109) — a vector index
   built with one embedding model version is not compatible with a different one;
   `embedding_vector/models.py` carries the version metadata needed to confirm this.
3. Check query latency/error rate against the interface's own contract
   (`embedding_vector/vector_store.py`) rather than backend-specific tooling, until a
   backend is selected.

## Recovery

- Retry / failover only if the selected backend supports it and the failover target is
  approved (doc 28 §60).
- Index restore/rebuild: never attempted casually — requires the embedding version and
  compatibility to be revalidated first (doc 20 §58, doc 26 §109).

## Escalation

Data / AI Platform team. If this incident reveals the vector store ADR is now urgent
(e.g. a production incident with no real backend to recover from), escalate the ADR
decision itself, not just the incident.
