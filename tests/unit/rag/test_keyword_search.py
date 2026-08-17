from pf_ft_ai.rag.keyword_search import TermOverlapKeywordSearch
from pf_ft_ai.rag.models import Chunk


def _chunk(chunk_id: str, content: str, *, tenant_id: str = "tenant-1") -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        document_id="doc-1",
        document_version=1,
        source_id="affiliation-policy",
        chunk_index=0,
        content=content,
        content_hash="hash",
        title="Affiliation Policy",
        tenant_id=tenant_id,
    )


async def test_should_find_chunks_with_overlapping_terms() -> None:
    search = TermOverlapKeywordSearch()
    await search.index(_chunk("chunk-1", "A club must submit affiliation documents"))
    await search.index(_chunk("chunk-2", "Officials require safeguarding accreditation"))

    results = await search.search("affiliation documents", tenant_id="tenant-1", top_k=5)

    assert results[0][0].chunk_id == "chunk-1"


async def test_should_isolate_results_by_tenant() -> None:
    search = TermOverlapKeywordSearch()
    await search.index(_chunk("chunk-1", "affiliation documents", tenant_id="tenant-a"))
    await search.index(_chunk("chunk-2", "affiliation documents", tenant_id="tenant-b"))

    results = await search.search("affiliation documents", tenant_id="tenant-a", top_k=5)

    assert [chunk.chunk_id for chunk, _score in results] == ["chunk-1"]


async def test_should_return_empty_for_no_overlap() -> None:
    search = TermOverlapKeywordSearch()
    await search.index(_chunk("chunk-1", "completely unrelated content"))

    results = await search.search("affiliation documents", tenant_id="tenant-1", top_k=5)

    assert results == []


async def test_should_return_empty_for_a_query_with_no_word_characters() -> None:
    search = TermOverlapKeywordSearch()
    await search.index(_chunk("chunk-1", "affiliation documents"))

    results = await search.search("!!!", tenant_id="tenant-1", top_k=5)

    assert results == []
