from typing import Any

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError, IntegrationError
from pff_fa_ai.configuration.models import AzureAiSearchSettings, VectorStoreSettings
from pff_fa_ai.configuration.secrets import SpnCredentials
from pff_fa_ai.embedding_vector.models import VectorMetadata, VectorRecord, VectorSearchFilter
from pff_fa_ai.embedding_vector.vector_store import (
    AzureAiSearchVectorStore,
    InMemoryVectorStore,
    build_acl_filter,
    build_vector_store,
)


def _record(vector_id: str = "vec-1") -> VectorRecord:
    return VectorRecord(
        vector_id=vector_id,
        chunk_id=f"{vector_id}-chunk",
        embedding=(0.1, 0.2, 0.3),
        embedding_model="mock-embedding-v1",
        embedding_version="1.0.0",
        dimension=3,
        metadata=VectorMetadata(
            document_id="doc-1",
            document_version=2,
            source_id="affiliation-policy",
            chunk_index=0,
            tenant_id="tenant-1",
            organization_id="club-123",
            domain="affiliation",
        ),
    )


class _FakeAzureSearchClient:
    def __init__(self, hits: list[tuple[float, dict[str, Any]]] | None = None) -> None:
        self.uploaded: list[dict[str, Any]] = []
        self.merged: list[dict[str, Any]] = []
        self.deleted: list[str] = []
        self.last_filter: str | None = None
        self._hits = hits or []

    async def upload_documents(self, documents: list[dict[str, Any]]) -> None:
        self.uploaded.extend(documents)

    async def merge_or_upload_documents(self, documents: list[dict[str, Any]]) -> None:
        self.merged.extend(documents)

    async def delete_documents(self, keys: list[str]) -> None:
        self.deleted.extend(keys)

    async def search_vector(
        self, *, vector: Any, top_k: int, odata_filter: str
    ) -> list[tuple[float, dict[str, Any]]]:
        self.last_filter = odata_filter
        return self._hits


def _spn() -> SpnCredentials:
    return SpnCredentials(tenant_id="t", client_id="c", client_secret="s")  # noqa: S106


def _settings(
    provider: str = "azure_ai_search", *, endpoint: str = "https://s.search"
) -> VectorStoreSettings:
    return VectorStoreSettings(
        provider=provider,  # type: ignore[arg-type]
        dimension=768,
        index_alias="pff-fa-knowledge",
        azure_ai_search=AzureAiSearchSettings(
            endpoint=endpoint, index_name="pff-fa-knowledge-v1", api_version="2024-07-01"
        ),
    )


def test_acl_filter_applies_tenant_org_and_domain() -> None:
    f = VectorSearchFilter(tenant_id="tenant-1", organization_ids=("a", "b"), domain="affiliation")

    assert build_acl_filter(f) == (
        "tenant_id eq 'tenant-1' and "
        "(organization_id eq 'a' or organization_id eq 'b') and domain eq 'affiliation'"
    )


def test_acl_filter_escapes_single_quotes_to_resist_injection() -> None:
    f = VectorSearchFilter(tenant_id="t' or '1'='1")

    assert build_acl_filter(f) == "tenant_id eq 't'' or ''1''=''1'"


def test_acl_filter_tenant_only_when_no_org_or_domain() -> None:
    f = VectorSearchFilter(tenant_id="tenant-1", domain=None)

    assert build_acl_filter(f) == "tenant_id eq 'tenant-1'"


async def test_upsert_maps_records_to_search_documents() -> None:
    client = _FakeAzureSearchClient()
    store = AzureAiSearchVectorStore(client)

    await store.upsert([_record("vec-9")])

    doc = client.uploaded[0]
    assert doc["vector_id"] == "vec-9"
    assert doc["embedding"] == [0.1, 0.2, 0.3]
    assert doc["tenant_id"] == "tenant-1"
    assert doc["document_version"] == 2


async def test_update_uses_merge_or_upload() -> None:
    client = _FakeAzureSearchClient()
    store = AzureAiSearchVectorStore(client)

    await store.update([_record()])

    assert client.merged and not client.uploaded


async def test_delete_passes_keys_through() -> None:
    client = _FakeAzureSearchClient()
    store = AzureAiSearchVectorStore(client)

    await store.delete(["vec-1", "vec-2"])

    assert client.deleted == ["vec-1", "vec-2"]


async def test_search_applies_acl_filter_and_maps_results() -> None:
    document = {
        "vector_id": "vec-1",
        "chunk_id": "vec-1-chunk",
        "document_id": "doc-1",
        "document_version": 2,
        "source_id": "affiliation-policy",
        "chunk_index": 0,
        "tenant_id": "tenant-1",
        "organization_id": "club-123",
        "domain": "affiliation",
    }
    client = _FakeAzureSearchClient(hits=[(0.87, document)])
    store = AzureAiSearchVectorStore(client)

    results = await store.search(
        [0.1, 0.2, 0.3], filters=VectorSearchFilter(tenant_id="tenant-1"), top_k=5
    )

    assert client.last_filter == "tenant_id eq 'tenant-1'"
    assert results[0].vector_id == "vec-1"
    assert results[0].score == pytest.approx(0.87)
    assert results[0].metadata.organization_id == "club-123"


def test_build_vector_store_defaults_to_inmemory() -> None:
    assert isinstance(build_vector_store(_settings(provider="inmemory")), InMemoryVectorStore)


def test_build_vector_store_uses_injected_client_for_azure() -> None:
    store = build_vector_store(_settings(), client=_FakeAzureSearchClient())

    assert isinstance(store, AzureAiSearchVectorStore)


def test_build_vector_store_fails_closed_without_endpoint() -> None:
    with pytest.raises(ConfigurationError, match="no endpoint is configured"):
        build_vector_store(_settings(endpoint=""), credentials=_spn())


def test_build_vector_store_fails_closed_without_credentials() -> None:
    with pytest.raises(IntegrationError, match="service-principal credentials"):
        build_vector_store(_settings())
