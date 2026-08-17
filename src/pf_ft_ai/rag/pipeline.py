from __future__ import annotations

from pf_ft_ai.configuration.models import ChunkingSettings
from pf_ft_ai.embedding_vector.models import VectorMetadata, VectorRecord
from pf_ft_ai.embedding_vector.providers import EmbeddingProvider
from pf_ft_ai.embedding_vector.registry import EmbeddingModelRegistry
from pf_ft_ai.embedding_vector.vector_store import VectorStore
from pf_ft_ai.rag.chunk_store import ChunkStore
from pf_ft_ai.rag.chunking import chunk_text
from pf_ft_ai.rag.keyword_search import TermOverlapKeywordSearch
from pf_ft_ai.rag.models import Chunk, DocumentRecord


class IngestionPipeline:
    """Doc 13 §15: Source Registration → Extraction → Normalization → Chunking →
    Metadata Enrichment → Embedding → Vector/Search Index (DEVELOPMENT-GUIDE Phase 8).

    Extraction/normalization are trivial passthroughs here — no real Word/PDF/Excel
    parsers exist yet (doc 13 §19-27); the caller supplies already-extracted plain text.
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
    ) -> None:
        self._embedding_provider = embedding_provider
        self._embedding_model_id = embedding_model_id
        self._model_registry = model_registry
        self._vector_store = vector_store
        self._chunk_store = chunk_store
        self._keyword_search = keyword_search

    async def ingest(
        self,
        *,
        document: DocumentRecord,
        text: str,
        tenant_id: str,
        organization_id: str | None,
        domain: str | None,
        chunking: ChunkingSettings,
    ) -> list[Chunk]:
        chunks = chunk_text(
            document_id=document.document_id,
            document_version=document.document_version,
            source_id=document.source_id,
            title=document.title,
            text=text,
            target_tokens=chunking.target_tokens,
            overlap_tokens=chunking.overlap_tokens,
            tenant_id=tenant_id,
            organization_id=organization_id,
        )
        if not chunks:
            return []

        vectors = await self._embedding_provider.embed_documents(
            [chunk.content for chunk in chunks]
        )
        model = self._model_registry.get(self._embedding_model_id)

        records = []
        for chunk, vector in zip(chunks, vectors, strict=True):
            self._model_registry.assert_dimension(self._embedding_model_id, vector)
            await self._chunk_store.put(chunk)
            await self._keyword_search.index(chunk)
            records.append(
                VectorRecord(
                    vector_id=f"{chunk.chunk_id}:{model.version}",
                    chunk_id=chunk.chunk_id,
                    embedding=vector,
                    embedding_model=model.model_id,
                    embedding_version=model.version,
                    dimension=model.dimension,
                    metadata=VectorMetadata(
                        document_id=document.document_id,
                        document_version=document.document_version,
                        source_id=document.source_id,
                        chunk_index=chunk.chunk_index,
                        tenant_id=tenant_id,
                        organization_id=organization_id,
                        domain=domain,
                    ),
                )
            )
        await self._vector_store.upsert(records)
        return chunks
