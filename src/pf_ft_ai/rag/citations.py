from __future__ import annotations

from pf_ft_ai.rag.models import Chunk, Citation


def build_citation(chunk: Chunk) -> Citation:
    """Doc 13 §82, §88 — built strictly from a chunk that was actually retrieved; there
    is no path here for inventing a document/page/section that wasn't retrieved."""
    return Citation(
        document_id=chunk.document_id,
        document_version=chunk.document_version,
        title=chunk.title,
        chunk_id=chunk.chunk_id,
        page=chunk.page,
        section=chunk.section,
    )
