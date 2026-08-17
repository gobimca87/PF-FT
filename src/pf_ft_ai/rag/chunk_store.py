from __future__ import annotations

from typing import Protocol

from pf_ft_ai.rag.models import Chunk


class ChunkStore(Protocol):
    """Doc 14 §23-24 — the vector index stores vector + metadata + chunk_id only; chunk
    content is owned by RAG's content store, looked up by chunk_id after search."""

    async def put(self, chunk: Chunk) -> None: ...

    async def get(self, chunk_id: str) -> Chunk | None: ...


class InMemoryChunkStore:
    def __init__(self) -> None:
        self._chunks: dict[str, Chunk] = {}

    async def put(self, chunk: Chunk) -> None:
        self._chunks[chunk.chunk_id] = chunk

    async def get(self, chunk_id: str) -> Chunk | None:
        return self._chunks.get(chunk_id)
