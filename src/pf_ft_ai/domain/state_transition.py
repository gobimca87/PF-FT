from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class StateActor(StrEnum):
    USER = "USER"
    SUPERVISOR = "SUPERVISOR"
    AGENT = "AGENT"
    LANGGRAPH = "LANGGRAPH"
    TOOL = "TOOL"
    ENTERPRISE_EVENT = "ENTERPRISE_EVENT"
    HUMAN = "HUMAN"
    SYSTEM = "SYSTEM"
    ADMIN = "ADMIN"
    RECOVERY = "RECOVERY"


class StateTransition(BaseModel):
    model_config = ConfigDict(frozen=True)

    entity_id: str
    from_state: str
    to_state: str
    reason: str
    actor: StateActor
    version: int
    occurred_at: datetime
