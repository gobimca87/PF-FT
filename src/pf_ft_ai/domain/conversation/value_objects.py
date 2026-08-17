from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(StrEnum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"
    TOOL = "TOOL"


class Message(BaseModel):
    model_config = ConfigDict(frozen=True)

    message_id: str
    conversation_id: str
    session_id: str
    role: MessageRole
    content: str
    created_at: datetime
    sequence_number: int = Field(ge=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
