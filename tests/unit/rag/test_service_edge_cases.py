from collections.abc import Sequence

from pf_ft_ai.configuration.models import RerankingSettings, RetrievalSettings
from pf_ft_ai.embedding_vector.models import (
    EmbeddingModelDescriptor,
    VectorMetadata,
    VectorRecord,
    VectorSearchFilter,
    VectorSearchResult,
)
from pf_ft_ai.embedding_vector.providers import MockEmbeddingProvider
from pf_ft_ai.embedding_vector.registry import EmbeddingModelRegistry
from pf_ft_ai.embedding_vector.states import EmbeddingModelStatus
from pf_ft_ai.rag.chunk_store import InMemoryChunkStore
from pf_ft_ai.rag.keyword_search import TermOverlapKeywordSearch
from pf_ft_ai.rag.models import Chunk, RagQuery
from pf_ft_ai.rag.reranking import ScoreTruncationReranker
from pf_ft_ai.rag.service import RagService
from pf_ft_ai.rag.states import RagStatus

_MODEL_ID = "mock-embedding-v1"


def _registry() -> EmbeddingModelRegistry:
    registry = EmbeddingModelRegistry()
    registry.register(
        EmbeddingModelDescriptor(
            model_id=_MODEL_ID,
            provider="mock",
            version="1.0.0",
            dimension=16,
            max_input_tokens=512,
            status=EmbeddingModelStatus.ACTIVE,
        )
    )
    return registry


class _StubVectorStore:
    def __init__(self, results: list[VectorSearchResult]) -> None:
        self._results = results

    async def upsert(self, records: list[VectorRecord]) -> None:
        raise NotImplementedError

    async def update(self, records: list[VectorRecord]) -> None:
        raise NotImplementedError

    async def delete(self, vector_ids: list[str]) -> None:
        raise NotImplementedError

    async def search(
        self, vector: Sequence[float], *, filters: VectorSearchFilter, top_k: int
    ) -> list[VectorSearchResult]:
        return self._results[:top_k]


def _vector_hit(chunk_id: str) -> VectorSearchResult:
    return VectorSearchResult(
        vector_id=f"{chunk_id}-vec",
        chunk_id=chunk_id,
        score=0.9,
        metadata=VectorMetadata(
            document_id="doc-1",
            document_version=1,
            source_id="affiliation-policy",
            chunk_index=0,
            tenant_id="tenant-1",
        ),
    )


async def test_should_skip_a_vector_hit_whose_content_is_no_longer_in_the_chunk_store() -> None:
    service = RagService(
        embedding_provider=MockEmbeddingProvider(dimension=16),
        embedding_model_id=_MODEL_ID,
        model_registry=_registry(),
        vector_store=_StubVectorStore([_vector_hit("missing-chunk")]),
        chunk_store=InMemoryChunkStore(),
        keyword_search=TermOverlapKeywordSearch(),
        reranker=ScoreTruncationReranker(),
        retrieval=RetrievalSettings(vector_top_k=20, keyword_top_k=20),
        reranking=RerankingSettings(top_n=8),
    )

    result = await service.query(RagQuery(query_text="affiliation", tenant_id="tenant-1"))

    assert result.status is RagStatus.NO_RESULTS


async def test_should_reject_a_chunk_whose_tenant_does_not_match_the_query() -> None:
    chunk_store = InMemoryChunkStore()
    await chunk_store.put(
        Chunk(
            chunk_id="foreign-chunk",
            document_id="doc-1",
            document_version=1,
            source_id="affiliation-policy",
            chunk_index=0,
            content="affiliation documents",
            content_hash="hash",
            title="Affiliation Policy",
            tenant_id="tenant-OTHER",
        )
    )
    service = RagService(
        embedding_provider=MockEmbeddingProvider(dimension=16),
        embedding_model_id=_MODEL_ID,
        model_registry=_registry(),
        vector_store=_StubVectorStore([_vector_hit("foreign-chunk")]),
        chunk_store=chunk_store,
        keyword_search=TermOverlapKeywordSearch(),
        reranker=ScoreTruncationReranker(),
        retrieval=RetrievalSettings(vector_top_k=20, keyword_top_k=20),
        reranking=RerankingSettings(top_n=8),
    )

    result = await service.query(RagQuery(query_text="affiliation", tenant_id="tenant-1"))

    assert result.status is RagStatus.NO_RESULTS
