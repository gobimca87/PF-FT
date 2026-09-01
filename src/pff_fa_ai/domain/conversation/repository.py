from __future__ import annotations

from typing import Protocol

from pff_fa_ai.domain.conversation.entities import Conversation
from pff_fa_ai.domain.conversation.value_objects import Message


class ConversationRepository(Protocol):
    async def create(self, conversation: Conversation) -> Conversation: ...

    async def get(self, conversation_id: str) -> Conversation | None: ...

    async def update(
        self, conversation: Conversation, *, expected_version: int
    ) -> Conversation: ...

    async def close(self, conversation_id: str, *, expected_version: int) -> Conversation: ...


class MessageRepository(Protocol):
    async def append(self, message: Message) -> Message: ...

    async def list(self, conversation_id: str, *, limit: int = 50) -> list[Message]: ...

    async def get_by_sequence(
        self, conversation_id: str, sequence_number: int
    ) -> Message | None: ...
