from datetime import UTC, datetime, timedelta

import pytest
from fakeredis import FakeAsyncRedis

from pff_fa_ai.cache.models import CacheEntry, CacheMetadata
from pff_fa_ai.cache.states import CacheCategory
from pff_fa_ai.cache.store import RedisCacheStore


def _entry(
    *,
    key_hash: str,
    tenant_id: str = "tenant-1",
    organization_id: str | None = "club-123",
    category: CacheCategory = CacheCategory.ENTERPRISE_API_RESPONSE,
) -> CacheEntry:
    now = datetime.now(UTC)
    return CacheEntry(
        key_hash=key_hash,
        category=category,
        schema_version="1.0.0",
        source="enterprise.club.get",
        metadata=CacheMetadata(tenant_id=tenant_id, organization_id=organization_id),
        value={"club_id": "club-123", "name": "Example FC"},
        created_at=now,
        expires_at=now + timedelta(seconds=300),
    )


@pytest.fixture
def store() -> RedisCacheStore:
    return RedisCacheStore(FakeAsyncRedis(), environment="test")


async def test_should_round_trip_a_cache_entry(store: RedisCacheStore) -> None:
    entry = _entry(key_hash="abc123")

    await store.set(entry, ttl_seconds=300)
    fetched = await store.get(
        CacheCategory.ENTERPRISE_API_RESPONSE,
        "abc123",
        tenant_id="tenant-1",
        organization_id="club-123",
    )

    assert fetched is not None
    assert fetched.value == {"club_id": "club-123", "name": "Example FC"}


async def test_should_return_none_on_cache_miss(store: RedisCacheStore) -> None:
    fetched = await store.get(
        CacheCategory.ENTERPRISE_API_RESPONSE,
        "missing",
        tenant_id="tenant-1",
        organization_id=None,
    )

    assert fetched is None


async def test_should_isolate_cache_entries_by_tenant(store: RedisCacheStore) -> None:
    await store.set(_entry(key_hash="abc123", tenant_id="tenant-a"), ttl_seconds=300)

    fetched_for_other_tenant = await store.get(
        CacheCategory.ENTERPRISE_API_RESPONSE,
        "abc123",
        tenant_id="tenant-b",
        organization_id="club-123",
    )

    assert fetched_for_other_tenant is None


async def test_should_delete_a_cache_entry(store: RedisCacheStore) -> None:
    await store.set(_entry(key_hash="abc123"), ttl_seconds=300)

    await store.delete(
        CacheCategory.ENTERPRISE_API_RESPONSE,
        "abc123",
        tenant_id="tenant-1",
        organization_id="club-123",
    )

    assert (
        await store.get(
            CacheCategory.ENTERPRISE_API_RESPONSE,
            "abc123",
            tenant_id="tenant-1",
            organization_id="club-123",
        )
        is None
    )


async def test_should_invalidate_matching_entries_only(store: RedisCacheStore) -> None:
    await store.set(_entry(key_hash="official:123"), ttl_seconds=300)
    await store.set(_entry(key_hash="official:456"), ttl_seconds=300)
    await store.set(_entry(key_hash="club:789"), ttl_seconds=300)

    deleted = await store.invalidate(
        CacheCategory.ENTERPRISE_API_RESPONSE, tenant_id="tenant-1", key_prefix="official"
    )

    assert deleted == 2
    assert (
        await store.get(
            CacheCategory.ENTERPRISE_API_RESPONSE,
            "club:789",
            tenant_id="tenant-1",
            organization_id="club-123",
        )
        is not None
    )
