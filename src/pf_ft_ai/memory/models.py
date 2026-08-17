from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pf_ft_ai.domain.versioning import Versioned
from pf_ft_ai.memory.states import (
    MemoryCategory,
    MemoryConfidence,
    MemoryLifecycleStatus,
    MemorySourceType,
)


class MemoryScope(BaseModel):
    """Doc 9 §101 namespace + §76-78 isolation boundary — every query/write is scoped by this."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tenant_id: str
    user_id: str
    organization_id: str | None = None
    conversation_id: str | None = None
    workflow_instance_id: str | None = None


class MemorySource(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    type: MemorySourceType
    reference: str | None = None


class MemoryRecord(Versioned):
    """Doc 9 §142 memory object."""

    memory_id: str
    category: MemoryCategory
    status: MemoryLifecycleStatus
    schema_version: str
    scope: MemoryScope
    source: MemorySource
    confidence: MemoryConfidence
    content: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None = None


class MemoryQuery(BaseModel):
    """Doc 9 §144 memory retrieval contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tenant_id: str
    user_id: str
    organization_id: str | None = None
    conversation_id: str | None = None
    workflow_instance_id: str | None = None
    categories: tuple[MemoryCategory, ...] = Field(default_factory=tuple)
    limit: int = Field(gt=0, default=20)


class MemoryWriteRequest(BaseModel):
    """Doc 9 §146 memory write contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: MemoryCategory
    scope: MemoryScope
    content: dict[str, Any]
    source: MemorySource
    confidence: MemoryConfidence
    schema_version: str = "1.0.0"
    ttl_seconds: int | None = None
