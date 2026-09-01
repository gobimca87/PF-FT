from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Protocol

from pff_fa_ai.embedding_vector.models import VectorRecord, VectorSearchFilter, VectorSearchResult


class VectorStore(Protocol):
    """Doc 14 §31 — vector store technology is an open ADR (docs/adr/0003); build strictly
    behind this interface (DEVELOPMENT-GUIDE Phase 8)."""

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
