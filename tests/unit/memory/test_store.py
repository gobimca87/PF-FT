from datetime import UTC, datetime, timedelta

import pytest
from fakeredis import FakeAsyncRedis

from pf_ft_ai.memory.models import MemoryQuery, MemoryRecord, MemoryScope, MemorySource
from pf_ft_ai.memory.states import (
    MemoryCategory,
    MemoryConfidence,
    MemoryLifecycleStatus,
    MemorySourceType,
)
from pf_ft_ai.memory.store import RedisMemoryStore


def _record(
    *,
    memory_id: str,
    scope: MemoryScope,
    category: MemoryCategory = MemoryCategory.WORKFLOW,
    expires_in_seconds: int = 3600,
) -> MemoryRecord:
    now = datetime.now(UTC)
    return MemoryRecord(
        memory_id=memory_id,
        category=category,
        status=MemoryLifecycleStatus.CREATED,
        schema_version="1.0.0",
        scope=scope,
        source=MemorySource(type=MemorySourceType.WORKFLOW, reference="wf-agent"),
        confidence=MemoryConfidence.HIGH,
        content={"last_completed_step": "validate_erc"},
        created_at=now,
        updated_at=now,
        expires_at=now + timedelta(seconds=expires_in_seconds),
    )


@pytest.fixture
def store() -> RedisMemoryStore:
    return RedisMemoryStore(FakeAsyncRedis(), environment="test")


async def test_should_round_trip_a_memory_record(store: RedisMemoryStore) -> None:
    scope = MemoryScope(tenant_id="tenant-1", user_id="user-1", workflow_instance_id="wf-123")
    record = _record(memory_id="mem-1", scope=scope)

    await store.put(record)
    fetched = await store.get(scope, MemoryCategory.WORKFLOW, "mem-1")

    assert fetched is not None
    assert fetched.content == {"last_completed_step": "validate_erc"}
    assert fetched.memory_id == "mem-1"


async def test_should_store_a_record_with_no_expiry(store: RedisMemoryStore) -> None:
    scope = MemoryScope(tenant_id="tenant-1", user_id="user-1")
    now = datetime.now(UTC)
    record = MemoryRecord(
        memory_id="mem-no-ttl",
        category=MemoryCategory.USER_PREFERENCE,
        status=MemoryLifecycleStatus.ACTIVE,
        schema_version="1.0.0",
        scope=scope,
        source=MemorySource(type=MemorySourceType.USER),
        confidence=MemoryConfidence.HIGH,
        content={"preferred_language": "en"},
        created_at=now,
        updated_at=now,
        expires_at=None,
    )

    await store.put(record)
    fetched = await store.get(scope, MemoryCategory.USER_PREFERENCE, "mem-no-ttl")

    assert fetched is not None
    assert fetched.expires_at is None


async def test_should_return_none_for_a_missing_record(store: RedisMemoryStore) -> None:
    scope = MemoryScope(tenant_id="tenant-1", user_id="user-1")

    fetched = await store.get(scope, MemoryCategory.WORKFLOW, "does-not-exist")

    assert fetched is None


async def test_should_delete_a_record(store: RedisMemoryStore) -> None:
    scope = MemoryScope(tenant_id="tenant-1", user_id="user-1")
    record = _record(memory_id="mem-2", scope=scope)
    await store.put(record)

    await store.delete(scope, MemoryCategory.WORKFLOW, "mem-2")

    assert await store.get(scope, MemoryCategory.WORKFLOW, "mem-2") is None


async def test_should_isolate_records_by_tenant(store: RedisMemoryStore) -> None:
    scope_a = MemoryScope(tenant_id="tenant-a", user_id="user-1")
    scope_b = MemoryScope(tenant_id="tenant-b", user_id="user-1")
    await store.put(_record(memory_id="mem-1", scope=scope_a))
    await store.put(_record(memory_id="mem-1", scope=scope_b))

    results_a = await store.query(MemoryQuery(tenant_id="tenant-a", user_id="user-1"))

    assert len(results_a) == 1
    assert results_a[0].scope.tenant_id == "tenant-a"


async def test_should_isolate_records_across_users_within_the_same_tenant(
    store: RedisMemoryStore,
) -> None:
    scope_a = MemoryScope(tenant_id="tenant-1", user_id="user-a")
    scope_b = MemoryScope(tenant_id="tenant-1", user_id="user-b")
    await store.put(_record(memory_id="mem-1", scope=scope_a))
    await store.put(_record(memory_id="mem-1", scope=scope_b))

    results = await store.query(MemoryQuery(tenant_id="tenant-1", user_id="user-a"))

    assert len(results) == 1
    assert results[0].scope.user_id == "user-a"


async def test_should_filter_query_by_category(store: RedisMemoryStore) -> None:
    scope = MemoryScope(tenant_id="tenant-1", user_id="user-1")
    await store.put(_record(memory_id="mem-1", scope=scope, category=MemoryCategory.WORKFLOW))
    await store.put(_record(memory_id="mem-2", scope=scope, category=MemoryCategory.DECISION))

    results = await store.query(
        MemoryQuery(tenant_id="tenant-1", user_id="user-1", categories=(MemoryCategory.DECISION,))
    )

    assert len(results) == 1
    assert results[0].category == MemoryCategory.DECISION


async def test_should_respect_the_query_limit(store: RedisMemoryStore) -> None:
    scope = MemoryScope(tenant_id="tenant-1", user_id="user-1")
    for index in range(5):
        await store.put(_record(memory_id=f"mem-{index}", scope=scope))

    results = await store.query(MemoryQuery(tenant_id="tenant-1", user_id="user-1", limit=2))

    assert len(results) == 2
