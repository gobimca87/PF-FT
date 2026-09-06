from __future__ import annotations

import asyncio

from pff_fa_ai.memory.models import MemoryQuery, MemoryRecord, MemoryScope
from pff_fa_ai.memory.states import MemoryCategory


def _matches(record: MemoryRecord, query: MemoryQuery) -> bool:
    scope = record.scope
    if query.tenant_id is not None and scope.tenant_id != query.tenant_id:
        return False
    if query.user_id is not None and scope.user_id != query.user_id:
        return False
    if query.organization_id is not None and scope.organization_id != query.organization_id:
        return False
    if query.conversation_id is not None and scope.conversation_id != query.conversation_id:
        return False
    return not (
        query.workflow_instance_id is not None
        and scope.workflow_instance_id != query.workflow_instance_id
    )


class InMemoryMemoryStore:
    """Dev/test adapter for `MemoryStore` (`memory/store.py`), mirroring
    `InMemoryWorkflowRepository`'s "interface now, concrete adapter later" pattern. The
    real backing store is Azure Managed Redis (`RedisMemoryStore`, ADR-D4-10) — wiring
    that in for a deployed environment is a separate infrastructure step, not needed for
    every environment `AppState` currently supports (every other repository in
    `AppState` is in-memory today for the same reason)."""

    def __init__(self) -> None:
        self._records: dict[tuple[str, str], MemoryRecord] = {}
        self._lock = asyncio.Lock()

    async def put(self, record: MemoryRecord) -> MemoryRecord:
        async with self._lock:
            self._records[(record.category.value, record.memory_id)] = record
            return record

    async def get(
        self, scope: MemoryScope, category: MemoryCategory, memory_id: str
    ) -> MemoryRecord | None:
        record = self._records.get((category.value, memory_id))
        if record is None or record.scope != scope:
            return None
        return record

    async def query(self, query: MemoryQuery) -> list[MemoryRecord]:
        categories = query.categories or tuple(MemoryCategory)
        matches = [
            record
            for record in self._records.values()
            if record.category in categories and _matches(record, query)
        ]
        matches.sort(key=lambda record: record.created_at, reverse=True)
        return matches[: query.limit]

    async def delete(self, scope: MemoryScope, category: MemoryCategory, memory_id: str) -> None:
        async with self._lock:
            self._records.pop((category.value, memory_id), None)
