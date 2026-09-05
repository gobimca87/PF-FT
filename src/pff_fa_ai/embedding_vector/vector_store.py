from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any, Protocol

from pff_fa_ai.common.exceptions import ConfigurationError, IntegrationError
from pff_fa_ai.configuration.models import VectorStoreSettings
from pff_fa_ai.configuration.secrets import SpnCredentials
from pff_fa_ai.embedding_vector.models import (
    VectorMetadata,
    VectorRecord,
    VectorSearchFilter,
    VectorSearchResult,
)


class VectorStore(Protocol):
    """Doc 14 §31 — vector store technology is resolved by ADR-D3-24 (Azure AI Search,
    Proposed build default; pgvector fallback). Build strictly behind this interface
    (DEVELOPMENT-GUIDE Phase 8) so the store can be swapped without touching callers."""

    async def upsert(self, records: list[VectorRecord]) -> None: ...

    async def search(
        self, vector: Sequence[float], *, filters: VectorSearchFilter, top_k: int
    ) -> list[VectorSearchResult]: ...

    async def delete(self, vector_ids: list[str]) -> None: ...

    async def update(self, records: list[VectorRecord]) -> None: ...


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return dot / (magnitude_a * magnitude_b)


def _matches(record: VectorRecord, filters: VectorSearchFilter) -> bool:
    if record.metadata.tenant_id != filters.tenant_id:
        return False
    if filters.organization_ids and record.metadata.organization_id not in filters.organization_ids:
        return False
    return filters.domain is None or record.metadata.domain == filters.domain


class InMemoryVectorStore:
    """Doc 14 §125 tenant isolation, enforced before results ever leave the store."""

    def __init__(self) -> None:
        self._records: dict[str, VectorRecord] = {}

    async def upsert(self, records: list[VectorRecord]) -> None:
        for record in records:
            self._records[record.vector_id] = record

    async def update(self, records: list[VectorRecord]) -> None:
        await self.upsert(records)

    async def delete(self, vector_ids: list[str]) -> None:
        for vector_id in vector_ids:
            self._records.pop(vector_id, None)

    async def search(
        self, vector: Sequence[float], *, filters: VectorSearchFilter, top_k: int
    ) -> list[VectorSearchResult]:
        candidates = [record for record in self._records.values() if _matches(record, filters)]
        scored = sorted(
            ((cosine_similarity(vector, record.embedding), record) for record in candidates),
            key=lambda pair: pair[0],
            reverse=True,
        )
        return [
            VectorSearchResult(
                vector_id=record.vector_id,
                chunk_id=record.chunk_id,
                score=score,
                metadata=record.metadata,
            )
            for score, record in scored[:top_k]
        ]


# --- Azure AI Search adapter (ADR-D3-24) ---------------------------------------------------

_VECTOR_FIELD = "embedding"


def _odata_escape(value: str) -> str:
    """ADR-D6-12 / doc 14 §51: ACL filters are built parametrically from validated claims,
    never from model output. Single quotes are doubled so a value can never break out of its
    OData string literal (filter-injection resistance)."""
    return value.replace("'", "''")


def build_acl_filter(filters: VectorSearchFilter) -> str:
    """Tenant/organization/domain ACL as an OData filter enforced at query time (ADR-D6-12).
    Tenant isolation is always applied; org and domain narrow further when present."""
    clauses = [f"tenant_id eq '{_odata_escape(filters.tenant_id)}'"]
    if filters.organization_ids:
        org_clause = " or ".join(
            f"organization_id eq '{_odata_escape(org)}'" for org in filters.organization_ids
        )
        clauses.append(f"({org_clause})")
    if filters.domain is not None:
        clauses.append(f"domain eq '{_odata_escape(filters.domain)}'")
    return " and ".join(clauses)


def _record_to_document(record: VectorRecord) -> dict[str, Any]:
    metadata = record.metadata
    return {
        "vector_id": record.vector_id,
        "chunk_id": record.chunk_id,
        _VECTOR_FIELD: list(record.embedding),
        "embedding_model": record.embedding_model,
        "embedding_version": record.embedding_version,
        "dimension": record.dimension,
        "document_id": metadata.document_id,
        "document_version": metadata.document_version,
        "source_id": metadata.source_id,
        "chunk_index": metadata.chunk_index,
        "tenant_id": metadata.tenant_id,
        "organization_id": metadata.organization_id,
        "domain": metadata.domain,
    }


def _document_to_result(document: dict[str, Any], score: float) -> VectorSearchResult:
    return VectorSearchResult(
        vector_id=document["vector_id"],
        chunk_id=document["chunk_id"],
        score=score,
        metadata=VectorMetadata(
            document_id=document["document_id"],
            document_version=document["document_version"],
            source_id=document["source_id"],
            chunk_index=document["chunk_index"],
            tenant_id=document["tenant_id"],
            organization_id=document.get("organization_id"),
            domain=document.get("domain"),
        ),
    )


class AzureSearchClient(Protocol):
    """Seam over the Azure AI Search documents client so the adapter is unit-testable
    without a live index; production uses `AzureSearchDocumentsClient`. `search_vector`
    returns `(score, document)` pairs, highest score first."""

    async def upload_documents(self, documents: list[dict[str, Any]]) -> None: ...

    async def merge_or_upload_documents(self, documents: list[dict[str, Any]]) -> None: ...

    async def delete_documents(self, keys: list[str]) -> None: ...

    async def search_vector(
        self, *, vector: Sequence[float], top_k: int, odata_filter: str
    ) -> list[tuple[float, dict[str, Any]]]: ...


class AzureAiSearchVectorStore:
    """ADR-D3-24 — the Azure AI Search realization of `VectorStore`. Records map to search
    documents keyed by `vector_id`; retrieval is a vector query narrowed by an OData ACL
    filter built from validated claims (ADR-D6-12). Authentication is via the enterprise SPN
    / Entra ID RBAC (ADR-D5-07); the index is addressed through its blue/green alias
    (ADR-D3-24 §8), resolved by the caller."""

    def __init__(self, client: AzureSearchClient) -> None:
        self._client = client

    async def upsert(self, records: list[VectorRecord]) -> None:
        await self._client.upload_documents([_record_to_document(record) for record in records])

    async def update(self, records: list[VectorRecord]) -> None:
        await self._client.merge_or_upload_documents(
            [_record_to_document(record) for record in records]
        )

    async def delete(self, vector_ids: list[str]) -> None:
        await self._client.delete_documents(vector_ids)

    async def search(
        self, vector: Sequence[float], *, filters: VectorSearchFilter, top_k: int
    ) -> list[VectorSearchResult]:
        hits = await self._client.search_vector(
            vector=vector, top_k=top_k, odata_filter=build_acl_filter(filters)
        )
        return [_document_to_result(document, score) for score, document in hits]


class AzureSearchDocumentsClient:
    """The production `AzureSearchClient`. The Azure SDK is imported lazily so the module
    stays importable — and unit-testable through the seam — without the SDK installed, and so
    no live endpoint is required until Azure AI Search is provisioned (ADR-D3-24, Phase 8)."""

    def __init__(
        self,
        *,
        endpoint: str,
        index_name: str,
        credentials: SpnCredentials,
        api_version: str,
    ) -> None:
        from azure.identity.aio import ClientSecretCredential
        from azure.search.documents.aio import SearchClient

        self._vector_field = _VECTOR_FIELD
        credential = ClientSecretCredential(
            tenant_id=credentials.tenant_id,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
        )
        self._client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=credential,
            api_version=api_version,
        )

    async def upload_documents(self, documents: list[dict[str, Any]]) -> None:
        await self._client.upload_documents(documents=documents)

    async def merge_or_upload_documents(self, documents: list[dict[str, Any]]) -> None:
        await self._client.merge_or_upload_documents(documents=documents)

    async def delete_documents(self, keys: list[str]) -> None:
        await self._client.delete_documents(documents=[{"vector_id": key} for key in keys])

    async def search_vector(
        self, *, vector: Sequence[float], top_k: int, odata_filter: str
    ) -> list[tuple[float, dict[str, Any]]]:
        from azure.search.documents.models import VectorizedQuery

        query = VectorizedQuery(
            vector=list(vector), k_nearest_neighbors=top_k, fields=self._vector_field
        )
        results = await self._client.search(
            search_text=None, vector_queries=[query], filter=odata_filter, top=top_k
        )
        hits: list[tuple[float, dict[str, Any]]] = []
        async for document in results:
            hits.append((float(document["@search.score"]), dict(document)))
        return hits


def build_vector_store(
    settings: VectorStoreSettings,
    *,
    credentials: SpnCredentials | None = None,
    client: AzureSearchClient | None = None,
) -> VectorStore:
    """Select the vector store from config (ADR-D3-24). `inmemory` is the default until Azure
    AI Search is provisioned; `azure_ai_search` requires a configured endpoint and the
    enterprise SPN (or an injected client for tests), and fails closed otherwise."""
    if settings.provider == "inmemory":
        return InMemoryVectorStore()

    if client is not None:
        return AzureAiSearchVectorStore(client)

    azure = settings.azure_ai_search
    if not azure.endpoint:
        raise ConfigurationError(
            "Azure AI Search is selected but no endpoint is configured; set "
            "vector_store.azure_ai_search.endpoint for this environment (ADR-D3-24)"
        )
    if credentials is None:
        raise IntegrationError(
            "Azure AI Search requires the enterprise service-principal credentials "
            "(ADR-D5-07); none were provided"
        )
    return AzureAiSearchVectorStore(
        AzureSearchDocumentsClient(
            endpoint=azure.endpoint,
            index_name=azure.index_name,
            credentials=credentials,
            api_version=azure.api_version,
        )
    )
