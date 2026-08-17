import pytest

from pf_ft_ai.configuration.models import ChunkingSettings, RerankingSettings, RetrievalSettings
from pf_ft_ai.embedding_vector.models import EmbeddingModelDescriptor
from pf_ft_ai.embedding_vector.providers import MockEmbeddingProvider
from pf_ft_ai.embedding_vector.registry import EmbeddingModelRegistry
from pf_ft_ai.embedding_vector.states import EmbeddingModelStatus
from pf_ft_ai.embedding_vector.vector_store import InMemoryVectorStore
from pf_ft_ai.rag.chunk_store import InMemoryChunkStore
from pf_ft_ai.rag.keyword_search import TermOverlapKeywordSearch
from pf_ft_ai.rag.models import DocumentRecord, RagQuery
from pf_ft_ai.rag.pipeline import IngestionPipeline
from pf_ft_ai.rag.reranking import ScoreTruncationReranker
from pf_ft_ai.rag.service import RagService
from pf_ft_ai.rag.states import DocumentLifecycleStatus, RagStatus

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


@pytest.fixture
def rag_stack() -> tuple[IngestionPipeline, RagService]:
    embedding_provider = MockEmbeddingProvider(dimension=16)
    model_registry = _registry()
    vector_store = InMemoryVectorStore()
    chunk_store = InMemoryChunkStore()
    keyword_search = TermOverlapKeywordSearch()

    pipeline = IngestionPipeline(
        embedding_provider=embedding_provider,
        embedding_model_id=_MODEL_ID,
        model_registry=model_registry,
        vector_store=vector_store,
        chunk_store=chunk_store,
        keyword_search=keyword_search,
    )
    service = RagService(
        embedding_provider=embedding_provider,
        embedding_model_id=_MODEL_ID,
        model_registry=model_registry,
        vector_store=vector_store,
        chunk_store=chunk_store,
        keyword_search=keyword_search,
        reranker=ScoreTruncationReranker(),
        retrieval=RetrievalSettings(vector_top_k=20, keyword_top_k=20),
        reranking=RerankingSettings(top_n=8),
    )
    return pipeline, service


async def test_should_ingest_and_retrieve_a_document(
    rag_stack: tuple[IngestionPipeline, RagService],
) -> None:
    pipeline, service = rag_stack
    document = DocumentRecord(
        document_id="doc-1",
        source_id="affiliation-policy",
        title="Affiliation Policy",
        document_version=1,
        content_hash="hash",
        status=DocumentLifecycleStatus.ACTIVE,
    )
    await pipeline.ingest(
        document=document,
        text="A club must submit its affiliation documents to the county each season.",
        tenant_id="tenant-1",
        organization_id="club-123",
        domain="affiliation",
        chunking=ChunkingSettings(target_tokens=400, overlap_tokens=50),
    )

    result = await service.query(RagQuery(query_text="affiliation documents", tenant_id="tenant-1"))

    assert result.status is RagStatus.COMPLETED
    assert len(result.chunks) >= 1
    assert result.citations[0].document_id == "doc-1"
    assert result.citations[0].title == "Affiliation Policy"


async def test_should_isolate_retrieval_by_tenant(
    rag_stack: tuple[IngestionPipeline, RagService],
) -> None:
    pipeline, service = rag_stack
    document = DocumentRecord(
        document_id="doc-1",
        source_id="affiliation-policy",
        title="Affiliation Policy",
        document_version=1,
        content_hash="hash",
        status=DocumentLifecycleStatus.ACTIVE,
    )
    await pipeline.ingest(
        document=document,
        text="A club must submit its affiliation documents to the county each season.",
        tenant_id="tenant-a",
        organization_id=None,
        domain=None,
        chunking=ChunkingSettings(target_tokens=400, overlap_tokens=50),
    )

    result = await service.query(RagQuery(query_text="affiliation documents", tenant_id="tenant-b"))

    assert result.status is RagStatus.NO_RESULTS
    assert result.chunks == ()


async def test_should_report_no_results_for_an_empty_index(
    rag_stack: tuple[IngestionPipeline, RagService],
) -> None:
    _pipeline, service = rag_stack

    result = await service.query(RagQuery(query_text="anything", tenant_id="tenant-1"))

    assert result.status is RagStatus.NO_RESULTS


async def test_should_report_no_results_for_blank_query(
    rag_stack: tuple[IngestionPipeline, RagService],
) -> None:
    _pipeline, service = rag_stack

    result = await service.query(RagQuery(query_text="   ", tenant_id="tenant-1"))

    assert result.status is RagStatus.NO_RESULTS


async def test_should_ingest_nothing_for_blank_document_text(
    rag_stack: tuple[IngestionPipeline, RagService],
) -> None:
    pipeline, _service = rag_stack
    document = DocumentRecord(
        document_id="doc-1",
        source_id="affiliation-policy",
        title="Affiliation Policy",
        document_version=1,
        content_hash="hash",
        status=DocumentLifecycleStatus.ACTIVE,
    )

    chunks = await pipeline.ingest(
        document=document,
        text="   ",
        tenant_id="tenant-1",
        organization_id=None,
        domain=None,
        chunking=ChunkingSettings(target_tokens=400, overlap_tokens=50),
    )

    assert chunks == []
