from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pf_ft_ai.common.correlation import new_id
from pf_ft_ai.configuration.models import MemorySettings
from pf_ft_ai.memory.models import MemoryQuery, MemoryRecord, MemoryWriteRequest
from pf_ft_ai.memory.policy import authorize_write, resolve_ttl_seconds
from pf_ft_ai.memory.states import MemoryLifecycleStatus
from pf_ft_ai.memory.store import MemoryStore


class MemoryService:
    """Doc 9 §22 provider abstraction — the only path agents/harness should use (§106)."""

    def __init__(self, store: MemoryStore, settings: MemorySettings) -> None:
        self._store = store
        self._settings = settings

    async def write(self, request: MemoryWriteRequest) -> MemoryRecord:
        authorize_write(request)
        ttl_seconds = resolve_ttl_seconds(request, self._settings)
        now = datetime.now(UTC)
        record = MemoryRecord(
            memory_id=new_id("mem"),
            category=request.category,
            status=MemoryLifecycleStatus.CREATED,
            schema_version=request.schema_version,
            scope=request.scope,
            source=request.source,
            confidence=request.confidence,
            content=request.content,
            created_at=now,
            updated_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
        )
        return await self._store.put(record)

    async def retrieve(self, query: MemoryQuery) -> list[MemoryRecord]:
        return await self._store.query(query)
