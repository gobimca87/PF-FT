from __future__ import annotations

from typing import Protocol

from redis.asyncio import Redis

from pff_fa_ai.cache.models import CacheEntry
from pff_fa_ai.cache.states import CacheCategory

_EMPTY_SEGMENT = "-"


class CacheStore(Protocol):
    """Doc 9 §137-138 — the harness/agents depend on this, never on Redis directly."""

    async def get(
        self, category: CacheCategory, key: str, *, tenant_id: str, organization_id: str | None
    ) -> CacheEntry | None: ...

    async def set(self, entry: CacheEntry, *, ttl_seconds: int) -> None: ...

    async def delete(
        self, category: CacheCategory, key: str, *, tenant_id: str, organization_id: str | None
    ) -> None: ...

    async def invalidate(
        self, category: CacheCategory, *, tenant_id: str, key_prefix: str = ""
    ) -> int: ...


def _build_key(
    *, environment: str, category: str, tenant_id: str, organization_id: str | None, key: str
) -> str:
    organization_segment = organization_id or _EMPTY_SEGMENT
    return f"pff-fa:{environment}:cache:{category}:{tenant_id}:{organization_segment}:{key}"


class RedisCacheStore:
    """Doc 9 §41 cache-aside pattern + docs/adr/0004 — Azure Managed Redis backend."""

    def __init__(self, client: Redis, *, environment: str) -> None:
        self._client = client
        self._environment = environment

    async def get(
        self, category: CacheCategory, key: str, *, tenant_id: str, organization_id: str | None
    ) -> CacheEntry | None:
        redis_key = _build_key(
            environment=self._environment,
            category=category.value,
            tenant_id=tenant_id,
            organization_id=organization_id,
            key=key,
        )
        payload = await self._client.get(redis_key)
        if payload is None:
            return None
        return CacheEntry.model_validate_json(payload)

    async def set(self, entry: CacheEntry, *, ttl_seconds: int) -> None:
        redis_key = _build_key(
            environment=self._environment,
            category=entry.category.value,
            tenant_id=entry.metadata.tenant_id,
            organization_id=entry.metadata.organization_id,
            key=entry.key_hash,
        )
        await self._client.set(redis_key, entry.model_dump_json(), ex=max(1, ttl_seconds))

    async def delete(
        self, category: CacheCategory, key: str, *, tenant_id: str, organization_id: str | None
    ) -> None:
        redis_key = _build_key(
            environment=self._environment,
            category=category.value,
            tenant_id=tenant_id,
            organization_id=organization_id,
            key=key,
        )
        await self._client.delete(redis_key)

    async def invalidate(
        self, category: CacheCategory, *, tenant_id: str, key_prefix: str = ""
    ) -> int:
        # Doc 9 §115: prefer targeted invalidation over flushing the entire cache.
        pattern = f"pff-fa:{self._environment}:cache:{category.value}:{tenant_id}:*{key_prefix}*"
        deleted = 0
        async for redis_key in self._client.scan_iter(match=pattern):
            await self._client.delete(redis_key)
            deleted += 1
        return deleted
