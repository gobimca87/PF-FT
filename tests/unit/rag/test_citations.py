from pf_ft_ai.rag.citations import build_citation
from pf_ft_ai.rag.models import Chunk


def test_should_build_a_citation_strictly_from_the_retrieved_chunk() -> None:
    chunk = Chunk(
        chunk_id="doc-1-chunk-0",
        document_id="doc-1",
        document_version=3,
        source_id="affiliation-policy",
        chunk_index=0,
        content="A club must submit its documents.",
        content_hash="hash",
        title="Affiliation Policy",
        tenant_id="tenant-1",
        page=12,
        section="Eligibility",
    )

    citation = build_citation(chunk)

    assert citation.document_id == "doc-1"
    assert citation.document_version == 3
    assert citation.title == "Affiliation Policy"
    assert citation.chunk_id == "doc-1-chunk-0"
    assert citation.page == 12
    assert citation.section == "Eligibility"
