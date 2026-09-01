from __future__ import annotations

from pff_fa_ai.common.exceptions import GuardrailError
from pff_fa_ai.configuration.models import MemorySettings
from pff_fa_ai.memory.models import MemoryWriteRequest
from pff_fa_ai.memory.states import MemorySourceType

# Doc 9 §71: "AI inference should not automatically become permanent memory."
_DISALLOWED_WRITE_SOURCES = frozenset({MemorySourceType.AI_INFERENCE})


def authorize_write(request: MemoryWriteRequest) -> None:
    if request.source.type in _DISALLOWED_WRITE_SOURCES:
        raise GuardrailError(
            f"Memory writes from source '{request.source.type}' are not permitted "
            "(doc 9 §71 — AI inference must not become permanent memory)",
            details={"category": request.category, "source_type": request.source.type},
        )


def resolve_ttl_seconds(request: MemoryWriteRequest, settings: MemorySettings) -> int:
    if request.ttl_seconds is not None:
        return request.ttl_seconds
    return settings.category_ttl_seconds.get(request.category.value, settings.default_ttl_seconds)
