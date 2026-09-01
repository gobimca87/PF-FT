import pytest

from pff_fa_ai.common.exceptions import ValidationError
from pff_fa_ai.rag.chunking import chunk_text
from pff_fa_ai.rag.models import Chunk


def test_should_return_a_single_chunk_for_short_text() -> None:
    chunks = chunk_text(
        document_id="doc-1",
        document_version=1,
        source_id="affiliation-policy",
        title="Affiliation Policy",
        text="A club must submit its affiliation documents annually.",
        target_tokens=400,
        overlap_tokens=50,
        tenant_id="tenant-1",
    )

    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].tenant_id == "tenant-1"


def test_should_split_long_text_into_overlapping_chunks() -> None:
    words = [f"word{i}" for i in range(1000)]
    text = " ".join(words)

    chunks = chunk_text(
        document_id="doc-1",
        document_version=1,
        source_id="affiliation-policy",
        title="Affiliation Policy",
        text=text,
        target_tokens=400,
        overlap_tokens=50,
        tenant_id="tenant-1",
    )

    assert len(chunks) > 1
    # Doc 13 §42: overlap should preserve context across chunk boundaries.
    first_chunk_words = chunks[0].content.split()
    second_chunk_words = chunks[1].content.split()
    assert first_chunk_words[-50:] == second_chunk_words[:50]


def test_should_produce_deterministic_chunk_ids_and_hashes() -> None:
    def build() -> list[Chunk]:
        return chunk_text(
            document_id="doc-1",
            document_version=1,
            source_id="affiliation-policy",
            title="Affiliation Policy",
            text="A club must submit its affiliation documents annually.",
            target_tokens=400,
            overlap_tokens=50,
            tenant_id="tenant-1",
        )

    first = build()
    second = build()

    assert first[0].chunk_id == second[0].chunk_id
    assert first[0].content_hash == second[0].content_hash


def test_should_return_empty_list_for_empty_text() -> None:
    chunks = chunk_text(
        document_id="doc-1",
        document_version=1,
        source_id="affiliation-policy",
        title="Affiliation Policy",
        text="   ",
        target_tokens=400,
        overlap_tokens=50,
        tenant_id="tenant-1",
    )

    assert chunks == []


def test_should_reject_overlap_greater_than_or_equal_to_target() -> None:
    with pytest.raises(ValidationError, match="overlap_tokens"):
        chunk_text(
            document_id="doc-1",
            document_version=1,
            source_id="affiliation-policy",
            title="Affiliation Policy",
            text="some text here",
            target_tokens=10,
            overlap_tokens=10,
            tenant_id="tenant-1",
        )
