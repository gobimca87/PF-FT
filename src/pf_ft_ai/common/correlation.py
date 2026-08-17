from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


class CorrelationContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    request_id: str
    correlation_id: str
    conversation_id: str | None = None
    session_id: str | None = None
    workflow_instance_id: str | None = None
