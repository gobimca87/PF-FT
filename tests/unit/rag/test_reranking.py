from pff_fa_ai.rag.models import Chunk, RetrievedChunk
from pff_fa_ai.rag.reranking import ScoreTruncationReranker


def _candidate(chunk_id: str, score: float) -> RetrievedChunk:
    chunk = Chunk(
        chunk_id=chunk_id,
        document_id="doc-1",
        document_version=1,
        source_id="affiliation-policy",
        chunk_index=0,
        content="A club must submit its documents.",
        content_hash="hash",
        title="Affiliation Policy",
        tenant_id="tenant-1",
    )
    return RetrievedChunk(chunk=chunk, score=score)


async def test_should_order_by_score_descending() -> None:
    reranker = ScoreTruncationReranker()
    candidates = [_candidate("low", 0.1), _candidate("high", 0.9), _candidate("mid", 0.5)]

    ranked = await reranker.rerank("query", candidates, top_n=3)

    assert [c.chunk.chunk_id for c in ranked] == ["high", "mid", "low"]


async def test_should_truncate_to_top_n() -> None:
    reranker = ScoreTruncationReranker()
    candidates = [_candidate(f"chunk-{i}", float(i)) for i in range(10)]

    ranked = await reranker.rerank("query", candidates, top_n=3)

    assert len(ranked) == 3
    assert ranked[0].chunk.chunk_id == "chunk-9"
