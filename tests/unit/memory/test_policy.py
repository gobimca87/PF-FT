import pytest

from pff_fa_ai.common.exceptions import GuardrailError
from pff_fa_ai.configuration.models import MemorySettings
from pff_fa_ai.memory.models import MemoryScope, MemorySource, MemoryWriteRequest
from pff_fa_ai.memory.policy import authorize_write, resolve_ttl_seconds
from pff_fa_ai.memory.states import MemoryCategory, MemoryConfidence, MemorySourceType

_SCOPE = MemoryScope(tenant_id="tenant-1", user_id="user-1")


def _request(
    *, source_type: MemorySourceType, ttl_seconds: int | None = None
) -> MemoryWriteRequest:
    return MemoryWriteRequest(
        category=MemoryCategory.DECISION,
        scope=_SCOPE,
        content={"selected": "officials"},
        source=MemorySource(type=source_type),
        confidence=MemoryConfidence.HIGH,
        ttl_seconds=ttl_seconds,
    )


def test_should_reject_ai_inference_as_a_write_source() -> None:
    with pytest.raises(GuardrailError, match="AI inference"):
        authorize_write(_request(source_type=MemorySourceType.AI_INFERENCE))


@pytest.mark.parametrize(
    "source_type",
    [
        MemorySourceType.USER,
        MemorySourceType.ENTERPRISE_API,
        MemorySourceType.ENTERPRISE_EVENT,
        MemorySourceType.WORKFLOW,
        MemorySourceType.AI_SUMMARY,
        MemorySourceType.SYSTEM,
    ],
)
def test_should_allow_all_other_write_sources(source_type: MemorySourceType) -> None:
    authorize_write(_request(source_type=source_type))


def test_should_use_explicit_ttl_when_provided() -> None:
    settings = MemorySettings(default_ttl_seconds=100, category_ttl_seconds={"DECISION": 200})

    ttl = resolve_ttl_seconds(_request(source_type=MemorySourceType.USER, ttl_seconds=42), settings)

    assert ttl == 42


def test_should_fall_back_to_category_ttl() -> None:
    settings = MemorySettings(default_ttl_seconds=100, category_ttl_seconds={"DECISION": 200})

    ttl = resolve_ttl_seconds(_request(source_type=MemorySourceType.USER), settings)

    assert ttl == 200


def test_should_fall_back_to_default_ttl_when_category_not_configured() -> None:
    settings = MemorySettings(default_ttl_seconds=100, category_ttl_seconds={})

    ttl = resolve_ttl_seconds(_request(source_type=MemorySourceType.USER), settings)

    assert ttl == 100
