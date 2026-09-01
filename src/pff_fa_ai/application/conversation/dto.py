from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from pff_fa_ai.domain.conversation.entities import Conversation
from pff_fa_ai.domain.conversation.states import ConversationStatus
from pff_fa_ai.domain.conversation.value_objects import Message, MessageRole


class ConversationView(BaseModel):
    model_config = ConfigDict(frozen=True)

    conversation_id: str
    session_id: str
    status: ConversationStatus
    created_at: datetime
    updated_at: datetime
    message_count: int

    @classmethod
    def from_conversation(cls, conversation: Conversation) -> ConversationView:
        return cls(
            conversation_id=conversation.conversation_id,
            session_id=conversation.session_id,
            status=conversation.status,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=conversation.message_count,
        )


class MessageView(BaseModel):
    model_config = ConfigDict(frozen=True)

    message_id: str
    role: MessageRole
    content: str
    created_at: datetime
    sequence_number: int

    @classmethod
    def from_message(cls, message: Message) -> MessageView:
        return cls(
            message_id=message.message_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
            sequence_number=message.sequence_number,
        )
