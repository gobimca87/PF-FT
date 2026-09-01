from __future__ import annotations

import hashlib

from pff_fa_ai.common.exceptions import ValidationError
from pff_fa_ai.rag.models import Chunk


def chunk_text(
    *,
    document_id: str,
    document_version: int,
    source_id: str,
    title: str,
    text: str,
    target_tokens: int,
    overlap_tokens: int,
    tenant_id: str,
    organization_id: str | None = None,
) -> list[Chunk]:
    """Doc 13 §41-42 — approximate chunking (1 token ~= 1 word), deterministic and testable.

    A true tokenizer-aware/semantic chunker (doc 13 §40, §43) is a later evaluation-driven
    refinement; this gives the pipeline a genuine, working default in the meantime.
    """
    if overlap_tokens >= target_tokens:
        raise ValidationError(
            "overlap_tokens must be smaller than target_tokens to guarantee progress",
            details={"target_tokens": target_tokens, "overlap_tokens": overlap_tokens},
        )

    words = text.split()
    if not words:
        return []

    chunks: list[Chunk] = []
    start = 0
    index = 0
    while start < len(words):
        end = min(start + target_tokens, len(words))
        content = " ".join(words[start:end])
        chunks.append(
            Chunk(
                chunk_id=f"{document_id}-chunk-{index}",
                document_id=document_id,
                document_version=document_version,
                source_id=source_id,
                chunk_index=index,
                content=content,
                content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
                title=title,
                tenant_id=tenant_id,
                organization_id=organization_id,
            )
        )
        if end == len(words):
            break
        start = end - overlap_tokens
        index += 1
    return chunks
