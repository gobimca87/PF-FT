import pytest
from fakeredis import FakeAsyncRedis

from pf_ft_ai.common.exceptions import GuardrailError
from pf_ft_ai.configuration.models import MemorySettings
from pf_ft_ai.memory.models import MemoryQuery, MemoryScope, MemorySource, MemoryWriteRequest
from pf_ft_ai.memory.service import MemoryService
from pf_ft_ai.memory.states import MemoryCategory, MemoryConfidence, MemorySourceType
from pf_ft_ai.memory.store import RedisMemoryStore


@pytest.fixture
def service() -> MemoryService:
    store = RedisMemoryStore(FakeAsyncRedis(), environment="test")
    settings = MemorySettings(default_ttl_seconds=3600, category_ttl_seconds={})
    return MemoryService(store, settings)


async def test_should_write_and_retrieve_a_memory_record(service: MemoryService) -> None:
    scope = MemoryScope(tenant_id="tenant-1", user_id="user-1", workflow_instance_id="wf-1")
    request = MemoryWriteRequest(
        category=MemoryCategory.WORKFLOW,
        scope=scope,
        content={"current_state": "WAITING_FOR_HIL"},
        source=MemorySource(type=MemorySourceType.WORKFLOW, reference="affiliation"),
        confidence=MemoryConfidence.HIGH,
    )

    written = await service.write(request)
    results = await service.retrieve(MemoryQuery(tenant_id="tenant-1", user_id="user-1"))

    assert written.content == {"current_state": "WAITING_FOR_HIL"}
    assert written.expires_at is not None
    assert len(results) == 1
    assert results[0].memory_id == written.memory_id


async def test_should_reject_ai_inference_writes_end_to_end(service: MemoryService) -> None:
    scope = MemoryScope(tenant_id="tenant-1", user_id="user-1")
    request = MemoryWriteRequest(
        category=MemoryCategory.SUMMARY,
        scope=scope,
        content={"guess": "probably approved"},
        source=MemorySource(type=MemorySourceType.AI_INFERENCE),
        confidence=MemoryConfidence.LOW,
    )

    with pytest.raises(GuardrailError):
        await service.write(request)
