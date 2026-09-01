from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.cache.states import CacheCategory


class CacheMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    tenant_id: str
    organization_id: str | None = None


class CacheEntry(BaseModel):
    """Doc 9 §143 cache object."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key_hash: str
    category: CacheCategory
    schema_version: str
    source: str
    metadata: CacheMetadata
    value: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    expires_at: datetime


class CacheQuery(BaseModel):
    """Doc 9 §145 cache retrieval contract — the store enforces scope, not the caller."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: CacheCategory
    key: str
    tenant_id: str
    organization_id: str | None = None


class CacheWriteRequest(BaseModel):
    """Doc 9 §147 cache write contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: CacheCategory
    key: str
    tenant_id: str
    organization_id: str | None = None
    source: str
    value: dict[str, Any]
    ttl_seconds: int | None = None
    schema_version: str = "1.0.0"
