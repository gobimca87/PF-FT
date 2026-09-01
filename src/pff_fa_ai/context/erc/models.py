from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.context.erc.provenance import Provenance
from pff_fa_ai.context.erc.states import (
    ErcLifecycleStatus,
    ErcSectionStatus,
    ErcValidationStatus,
    FreshnessStatus,
)
from pff_fa_ai.domain.versioning import Versioned


class Freshness(BaseModel):
    model_config = ConfigDict(frozen=True)

    retrieved_at: datetime
    expires_at: datetime
    ttl_seconds: int = Field(gt=0)
    status: FreshnessStatus


def compute_freshness(*, retrieved_at: datetime, ttl_seconds: int, now: datetime) -> Freshness:
    expires_at = retrieved_at + timedelta(seconds=ttl_seconds)
    status = FreshnessStatus.EXPIRED if now >= expires_at else FreshnessStatus.FRESH
    return Freshness(
        retrieved_at=retrieved_at, expires_at=expires_at, ttl_seconds=ttl_seconds, status=status
    )


class ErcSection(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    status: ErcSectionStatus
    section_version: int = Field(ge=1, default=1)
    data: dict[str, Any] = Field(default_factory=dict)
    provenance: Provenance | None = None
    freshness: Freshness | None = None
    expected_count: int | None = None
    received_count: int | None = None


class ErcCompleteness(BaseModel):
    model_config = ConfigDict(frozen=True)

    required_sections: int = Field(ge=0)
    completed_sections: int = Field(ge=0)
    missing_sections: tuple[str, ...] = Field(default_factory=tuple)


class ErcValidationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: ErcValidationStatus
    checked_at: datetime
    errors: tuple[str, ...] = Field(default_factory=tuple)
    warnings: tuple[str, ...] = Field(default_factory=tuple)


class Erc(Versioned):
    erc_id: str
    schema_version: str
    status: ErcLifecycleStatus
    workflow_instance_id: str
    conversation_id: str
    created_at: datetime
    updated_at: datetime
    sections: dict[str, ErcSection] = Field(default_factory=dict)
    completeness: ErcCompleteness | None = None
    validation: ErcValidationResult | None = None
