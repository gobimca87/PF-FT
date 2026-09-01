import pytest
from fakeredis import FakeAsyncRedis

from pff_fa_ai.cache.models import CacheWriteRequest
from pff_fa_ai.cache.service import CacheService
from pff_fa_ai.cache.states import CacheCategory
from pff_fa_ai.cache.store import RedisCacheStore
from pff_fa_ai.configuration.models import CacheSettings


@pytest.fixture
def service() -> CacheService:
    store = RedisCacheStore(FakeAsyncRedis(), environment="test")
    settings = CacheSettings(default_ttl_seconds=300, category_ttl_seconds={"REFERENCE_DATA": 3600})
    return CacheService(store, settings)


def _write_request(**overrides: object) -> CacheWriteRequest:
    defaults: dict[str, object] = {
        "category": CacheCategory.ENTERPRISE_API_RESPONSE,
        "key": "abc123",
        "tenant_id": "tenant-1",
        "organization_id": "club-123",
        "source": "enterprise.club.get",
        "value": {"name": "Example FC"},
    }
    defaults.update(overrides)
    return CacheWriteRequest(**defaults)  # type: ignore[arg-type]


async def test_should_set_and_get_a_cache_entry(service: CacheService) -> None:
    await service.set(_write_request())

    fetched = await service.get(
        CacheCategory.ENTERPRISE_API_RESPONSE,
        "abc123",
        tenant_id="tenant-1",
        organization_id="club-123",
    )

    assert fetched is not None
    assert fetched.value == {"name": "Example FC"}


async def test_should_use_category_ttl_when_no_explicit_ttl_given(service: CacheService) -> None:
    entry = await service.set(_write_request(category=CacheCategory.REFERENCE_DATA, key="ref-1"))

    ttl_seconds = (entry.expires_at - entry.created_at).total_seconds()
    assert ttl_seconds == pytest.approx(3600, abs=1)


async def test_get_or_set_should_return_the_cached_value_on_hit(service: CacheService) -> None:
    await service.set(_write_request())
    calls = 0

    async def loader() -> dict[str, object]:
        nonlocal calls
        calls += 1
        return {"name": "should-not-be-used"}

    entry = await service.get_or_set(_write_request(), loader)

    assert calls == 0
    assert entry.value == {"name": "Example FC"}


async def test_get_or_set_should_populate_the_cache_on_miss(service: CacheService) -> None:
    calls = 0

    async def loader() -> dict[str, object]:
        nonlocal calls
        calls += 1
        return {"name": "Loaded FC"}

    entry = await service.get_or_set(_write_request(key="miss-key"), loader)
    fetched = await service.get(
        CacheCategory.ENTERPRISE_API_RESPONSE,
        "miss-key",
        tenant_id="tenant-1",
        organization_id="club-123",
    )

    assert calls == 1
    assert entry.value == {"name": "Loaded FC"}
    assert fetched is not None
    assert fetched.value == {"name": "Loaded FC"}
