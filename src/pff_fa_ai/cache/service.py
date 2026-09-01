from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from pff_fa_ai.cache.models import CacheEntry, CacheMetadata, CacheWriteRequest
from pff_fa_ai.cache.states import CacheCategory
from pff_fa_ai.cache.store import CacheStore
from pff_fa_ai.configuration.models import CacheSettings


def _resolve_ttl_seconds(request: CacheWriteRequest, settings: CacheSettings) -> int:
    if request.ttl_seconds is not None:
        return request.ttl_seconds
    return settings.category_ttl_seconds.get(request.category.value, settings.default_ttl_seconds)


class CacheService:
    """Doc 9 §41 cache-aside pattern, built on top of the CacheStore abstraction (§137-138)."""

    def __init__(self, store: CacheStore, settings: CacheSettings) -> None:
        self._store = store
        self._settings = settings

    async def set(self, request: CacheWriteRequest) -> CacheEntry:
        ttl_seconds = _resolve_ttl_seconds(request, self._settings)
        now = datetime.now(UTC)
        entry = CacheEntry(
            key_hash=request.key,
            category=request.category,
            schema_version=request.schema_version,
            source=request.source,
            metadata=CacheMetadata(
                tenant_id=request.tenant_id, organization_id=request.organization_id
            ),
            value=request.value,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
        )
        await self._store.set(entry, ttl_seconds=ttl_seconds)
        return entry

    async def get(
        self, category: CacheCategory, key: str, *, tenant_id: str, organization_id: str | None
    ) -> CacheEntry | None:
        return await self._store.get(
            category, key, tenant_id=tenant_id, organization_id=organization_id
        )

    async def get_or_set(
        self,
        request: CacheWriteRequest,
        loader: Callable[[], Awaitable[dict[str, Any]]],
    ) -> CacheEntry:
        """Doc 9 §41: HIT -> return; MISS -> load from source -> SET -> return."""
        existing = await self.get(
            request.category,
            request.key,
            tenant_id=request.tenant_id,
            organization_id=request.organization_id,
        )
        if existing is not None:
            return existing
        value = await loader()
        return await self.set(request.model_copy(update={"value": value}))
