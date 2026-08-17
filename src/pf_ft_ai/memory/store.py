from __future__ import annotations

from typing import Protocol

from redis.asyncio import Redis

from pf_ft_ai.memory.models import MemoryQuery, MemoryRecord, MemoryScope
from pf_ft_ai.memory.states import MemoryCategory

_EMPTY_SEGMENT = "-"  # keeps the key layout fixed-width so scan patterns stay predictable


class MemoryStore(Protocol):
    """Doc 9 §137 — agents/services must depend on this, never on Redis directly (§138)."""

    async def put(self, record: MemoryRecord) -> MemoryRecord: ...

    async def get(
        self, scope: MemoryScope, category: MemoryCategory, memory_id: str
    ) -> MemoryRecord | None: ...

    async def query(self, query: MemoryQuery) -> list[MemoryRecord]: ...

    async def delete(
        self, scope: MemoryScope, category: MemoryCategory, memory_id: str
    ) -> None: ...


def _scope_segments(scope: MemoryScope) -> tuple[str, str, str, str, str]:
    return (
        scope.tenant_id,
        scope.user_id,
        scope.organization_id or _EMPTY_SEGMENT,
        scope.conversation_id or _EMPTY_SEGMENT,
        scope.workflow_instance_id or _EMPTY_SEGMENT,
    )


def _build_key(*, environment: str, category: str, scope: MemoryScope, memory_id: str) -> str:
    tenant, user, org, conversation, workflow = _scope_segments(scope)
    return (
        f"pf-ft:{environment}:memory:{category}:{tenant}:{user}:"
        f"{org}:{conversation}:{workflow}:{memory_id}"
    )


def _build_scan_pattern(*, environment: str, query: MemoryQuery, category: str) -> str:
    # An unset scope dimension means "any value" here, not "must be absent" — a query
    # scoped only to tenant+user should still surface workflow-scoped memory (doc 9 §23).
    org = query.organization_id or "*"
    conversation = query.conversation_id or "*"
    workflow = query.workflow_instance_id or "*"
    return (
        f"pf-ft:{environment}:memory:{category}:{query.tenant_id}:{query.user_id}:"
        f"{org}:{conversation}:{workflow}:*"
    )


class RedisMemoryStore:
    """Doc 9 §137-138 + docs/adr/0004 — Azure Managed Redis behind the MemoryStore interface."""

    def __init__(self, client: Redis, *, environment: str) -> None:
        self._client = client
        self._environment = environment

    async def put(self, record: MemoryRecord) -> MemoryRecord:
        key = _build_key(
            environment=self._environment,
            category=record.category.value,
            scope=record.scope,
            memory_id=record.memory_id,
        )
        payload = record.model_dump_json()
        if record.expires_at is None:
            await self._client.set(key, payload)
        else:
            ttl_seconds = max(1, int((record.expires_at - record.updated_at).total_seconds()))
            await self._client.set(key, payload, ex=ttl_seconds)
        return record

    async def get(
        self, scope: MemoryScope, category: MemoryCategory, memory_id: str
    ) -> MemoryRecord | None:
        key = _build_key(
            environment=self._environment, category=category.value, scope=scope, memory_id=memory_id
        )
        payload = await self._client.get(key)
        if payload is None:
            return None
        return MemoryRecord.model_validate_json(payload)

    async def query(self, query: MemoryQuery) -> list[MemoryRecord]:
        categories = query.categories or tuple(MemoryCategory)
        records: list[MemoryRecord] = []
        for category in categories:
            pattern = _build_scan_pattern(
                environment=self._environment, query=query, category=category.value
            )
            async for key in self._client.scan_iter(match=pattern):
                payload = await self._client.get(key)
                if payload is not None:
                    records.append(MemoryRecord.model_validate_json(payload))
                if len(records) >= query.limit:
                    return records
        return records

    async def delete(self, scope: MemoryScope, category: MemoryCategory, memory_id: str) -> None:
        key = _build_key(
            environment=self._environment, category=category.value, scope=scope, memory_id=memory_id
        )
        await self._client.delete(key)
