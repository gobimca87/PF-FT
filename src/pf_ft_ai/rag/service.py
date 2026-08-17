from __future__ import annotations

from pf_ft_ai.configuration.models import RerankingSettings, RetrievalSettings
from pf_ft_ai.embedding_vector.models import VectorSearchFilter
from pf_ft_ai.embedding_vector.providers import EmbeddingProvider
from pf_ft_ai.embedding_vector.registry import EmbeddingModelRegistry
from pf_ft_ai.embedding_vector.vector_store import VectorStore
from pf_ft_ai.rag.chunk_store import ChunkStore
from pf_ft_ai.rag.citations import build_citation
from pf_ft_ai.rag.fusion import reciprocal_rank_fusion
from pf_ft_ai.rag.keyword_search import TermOverlapKeywordSearch
from pf_ft_ai.rag.models import RagQuery, RagResult, RetrievedChunk
from pf_ft_ai.rag.reranking import Reranker
from pf_ft_ai.rag.states import RagStatus


class RagService:
    """Doc 13 §6 query pipeline: Query Analysis → Transformation → Metadata/ACL Filter
    (before search) → Candidate Retrieval (vector + keyword hybrid) → Reranker → Context
    Selection → Citations (DEVELOPMENT-GUIDE Phase 8).

    Query rewriting/expansion (doc 13 §57-58) needs the SLM and is deliberately not built
    here — the query is used as given.
    """

    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        embedding_model_id: str,
        model_registry: EmbeddingModelRegistry,
        vector_store: VectorStore,
        chunk_store: ChunkStore,
        keyword_search: TermOverlapKeywordSearch,
        reranker: Reranker,
        retrieval: RetrievalSettings,
        reranking: RerankingSettings,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._embedding_model_id = embedding_model_id
        self._model_registry = model_registry
        self._vector_store = vector_store
        self._chunk_store = chunk_store
        self._keyword_search = keyword_search
        self._reranker = reranker
        self._retrieval = retrieval
        self._reranking = reranking

    async def query(self, query: RagQuery) -> RagResult:
        query_text = query.query_text.strip()
        if not query_text:
            return RagResult(status=RagStatus.NO_RESULTS)

        # Security filters applied before search, not after (doc 13 §33-34, §62).
        query_vector = await self._embedding_provider.embed_query(query_text)
        self._model_registry.assert_dimension(self._embedding_model_id, query_vector)
        vector_filters = VectorSearchFilter(
            tenant_id=query.tenant_id,
            organization_ids=query.organization_ids,
            domain=query.domain,
        )

        vector_results = await self._vector_store.search(
            query_vector, filters=vector_filters, top_k=self._retrieval.vector_top_k
        )
        keyword_results = await self._keyword_search.search(
            query_text, tenant_id=query.tenant_id, top_k=self._retrieval.keyword_top_k
        )

        fused_scores = reciprocal_rank_fusion(
            [result.chunk_id for result in vector_results],
            [chunk.chunk_id for chunk, _score in keyword_results],
        )
        if not fused_scores:
            return RagResult(status=RagStatus.NO_RESULTS)

        candidates: list[RetrievedChunk] = []
        for chunk_id, score in fused_scores.items():
            chunk = await self._chunk_store.get(chunk_id)
            if chunk is None or chunk.tenant_id != query.tenant_id:
                continue
            candidates.append(RetrievedChunk(chunk=chunk, score=score))
        if not candidates:
            return RagResult(status=RagStatus.NO_RESULTS)

        reranked = await self._reranker.rerank(query_text, candidates, top_n=self._reranking.top_n)
        citations = tuple(build_citation(candidate.chunk) for candidate in reranked)
        return RagResult(status=RagStatus.COMPLETED, chunks=tuple(reranked), citations=citations)
