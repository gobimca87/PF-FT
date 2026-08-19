# 3. Deferred decisions log

Date: 2026-08-16

## Status

Tracking (living document — update as each decision is made, don't pre-resolve)

## Context

`DEVELOPMENT-GUIDE.md` §2 intentionally leaves several choices open rather than have the
spec docs silently pick one. Per project direction, these are resolved as development
reaches the phase that needs them, not upfront.

## Open decisions

| Decision | Needed by | Candidates | Status |
|---|---|---|---|
| Vector store | Phase 8 (RAG + Embedding/Vector) | Azure AI Search, Pinecone, Qdrant, Weaviate, Milvus, pgvector, OpenSearch, Elasticsearch, Redis Vector Search, Chroma | **Open** — building behind `VectorStore` interface in the meantime |
| IaC tool | Phase 19 (Infrastructure) | Terraform, Bicep | **Open — explicitly deferred by the user at Phase 19** ("will decide later"). `infra/` is not scaffolded; nothing in Phase 19 assumes either tool. |
| Kubernetes manifest tool | Phase 19 (Infrastructure) | Kustomize, Helm | **Open — explicitly deferred by the user at Phase 19** ("will decide later; skip the phase content that needs it"). `deploy/` is not scaffolded. |

## Decisions already accepted (recommended defaults from the guide)

| Decision | Resolution | ADR |
|---|---|---|
| Environment stage model | 5 stages: `DEV → TEST → UAT → STAGE → PROD` | (recorded here; no dedicated ADR needed — direct adoption of `DEVELOPMENT-GUIDE.md` §2 recommendation) |
| First/only agent build scope | `AffiliationAgent` only; rest of the agent catalog deferred to a real product decision | (recorded here; same as above) |
| Memory / session / cache store | Azure Managed Redis | [`0004-memory-cache-store-azure-managed-redis.md`](0004-memory-cache-store-azure-managed-redis.md) |
| Deployment strategy | Rolling — Kubernetes/AKS's default update strategy, accepted 2026-08-19 by user decision at Phase 19 | (recorded here; no dedicated ADR needed — the CI/CD placeholder deploy job in `.github/workflows/ci.yml` documents this) |

## How to close an open row

When a phase above is reached: write a new numbered ADR deciding it, update this table's
`Status` column to point at that ADR, and update the concrete adapter/module — the
interface boundary should mean no calling code changes.
