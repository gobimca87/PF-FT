from __future__ import annotations

from datetime import datetime

from pydantic import Field

from pff_fa_ai.domain.conversation.states import ConversationStatus
from pff_fa_ai.domain.versioning import Versioned


class Conversation(Versioned):
    conversation_id: str
    user_reference: str
    session_id: str
    status: ConversationStatus
    created_at: datetime
    updated_at: datetime
    active_workflow_instance_id: str | None = None
    message_count: int = Field(ge=0, default=0)
