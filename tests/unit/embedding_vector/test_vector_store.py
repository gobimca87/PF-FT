from pff_fa_ai.embedding_vector.models import VectorMetadata, VectorRecord, VectorSearchFilter
from pff_fa_ai.embedding_vector.vector_store import InMemoryVectorStore, cosine_similarity


def _record(
    vector_id: str,
    embedding: tuple[float, ...],
    *,
    tenant_id: str = "tenant-1",
    organization_id: str | None = "club-123",
    domain: str | None = "affiliation",
) -> VectorRecord:
    return VectorRecord(
        vector_id=vector_id,
        chunk_id=f"{vector_id}-chunk",
        embedding=embedding,
        embedding_model="mock-embedding-v1",
        embedding_version="1.0.0",
        dimension=len(embedding),
        metadata=VectorMetadata(
            document_id="doc-1",
            document_version=1,
            source_id="affiliation-policy",
            chunk_index=0,
            tenant_id=tenant_id,
            organization_id=organization_id,
            domain=domain,
        ),
    )


def test_cosine_similarity_should_be_one_for_identical_vectors() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0


def test_cosine_similarity_should_be_zero_for_orthogonal_vectors() -> None:
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_cosine_similarity_should_handle_zero_vector() -> None:
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0


async def test_should_return_the_most_similar_vector_first() -> None:
    store = InMemoryVectorStore()
    await store.upsert(
        [
            _record("close", (1.0, 0.0)),
            _record("far", (0.0, 1.0)),
        ]
    )

    results = await store.search(
        (1.0, 0.0), filters=VectorSearchFilter(tenant_id="tenant-1"), top_k=2
    )

    assert [r.vector_id for r in results] == ["close", "far"]


async def test_should_isolate_search_results_by_tenant() -> None:
    store = InMemoryVectorStore()
    await store.upsert(
        [
            _record("tenant-a-vec", (1.0, 0.0), tenant_id="tenant-a"),
            _record("tenant-b-vec", (1.0, 0.0), tenant_id="tenant-b"),
        ]
    )

    results = await store.search(
        (1.0, 0.0), filters=VectorSearchFilter(tenant_id="tenant-a"), top_k=10
    )

    assert [r.vector_id for r in results] == ["tenant-a-vec"]


async def test_should_filter_by_organization() -> None:
    store = InMemoryVectorStore()
    await store.upsert(
        [
            _record("club-a-vec", (1.0, 0.0), organization_id="club-a"),
            _record("club-b-vec", (1.0, 0.0), organization_id="club-b"),
        ]
    )

    results = await store.search(
        (1.0, 0.0),
        filters=VectorSearchFilter(tenant_id="tenant-1", organization_ids=("club-b",)),
        top_k=10,
    )

    assert [r.vector_id for r in results] == ["club-b-vec"]


async def test_should_filter_by_domain() -> None:
    store = InMemoryVectorStore()
    await store.upsert(
        [
            _record("affiliation-vec", (1.0, 0.0), domain="affiliation"),
            _record("discipline-vec", (1.0, 0.0), domain="discipline"),
        ]
    )

    results = await store.search(
        (1.0, 0.0),
        filters=VectorSearchFilter(tenant_id="tenant-1", domain="discipline"),
        top_k=10,
    )

    assert [r.vector_id for r in results] == ["discipline-vec"]


async def test_should_delete_a_vector() -> None:
    store = InMemoryVectorStore()
    await store.upsert([_record("to-delete", (1.0, 0.0))])

    await store.delete(["to-delete"])

    results = await store.search(
        (1.0, 0.0), filters=VectorSearchFilter(tenant_id="tenant-1"), top_k=10
    )
    assert results == []


async def test_update_should_behave_like_upsert() -> None:
    store = InMemoryVectorStore()
    await store.upsert([_record("vec-1", (1.0, 0.0))])

    await store.update([_record("vec-1", (0.0, 1.0))])

    results = await store.search(
        (0.0, 1.0), filters=VectorSearchFilter(tenant_id="tenant-1"), top_k=10
    )
    assert results[0].score == 1.0


async def test_should_respect_top_k() -> None:
    store = InMemoryVectorStore()
    await store.upsert([_record(f"vec-{i}", (1.0, 0.0)) for i in range(5)])

    results = await store.search(
        (1.0, 0.0), filters=VectorSearchFilter(tenant_id="tenant-1"), top_k=2
    )

    assert len(results) == 2
