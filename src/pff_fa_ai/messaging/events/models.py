from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventEnvelope(BaseModel):
    """doc 11 §13, DEVELOPMENT-GUIDE Phase 12's canonical event envelope.

    `workflow_instance_id` is not in DEVELOPMENT-GUIDE's minimum field list but doc 11
    §21 treats it as a first-class correlation field ("where available, events should
    carry workflow_instance_id") distinct from payload — included here for that reason.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: str
    event_type: str
    event_version: str
    source: str
    subject: str
    occurred_at: datetime
    published_at: datetime
    correlation_id: str
    causation_id: str | None = None
    tenant_id: str
    organization_id: str | None = None
    workflow_instance_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
