from __future__ import annotations

import asyncio

from pf_ft_ai.common.exceptions import WorkflowError
from pf_ft_ai.domain.conversation.entities import Conversation
from pf_ft_ai.domain.conversation.states import ConversationStatus
from pf_ft_ai.domain.versioning import assert_expected_version


class InMemoryConversationRepository:
    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._lock = asyncio.Lock()

    async def create(self, conversation: Conversation) -> Conversation:
        async with self._lock:
            if conversation.conversation_id in self._conversations:
                raise WorkflowError(f"Conversation already exists: {conversation.conversation_id}")
            self._conversations[conversation.conversation_id] = conversation
            return conversation

    async def get(self, conversation_id: str) -> Conversation | None:
        return self._conversations.get(conversation_id)

    async def update(self, conversation: Conversation, *, expected_version: int) -> Conversation:
        async with self._lock:
            existing = self._conversations.get(conversation.conversation_id)
            if existing is None:
                raise WorkflowError(f"Conversation not found: {conversation.conversation_id}")
            assert_expected_version(
                current_version=existing.version, expected_version=expected_version
            )
            self._conversations[conversation.conversation_id] = conversation
            return conversation

    async def close(self, conversation_id: str, *, expected_version: int) -> Conversation:
        async with self._lock:
            existing = self._conversations.get(conversation_id)
            if existing is None:
                raise WorkflowError(f"Conversation not found: {conversation_id}")
            assert_expected_version(
                current_version=existing.version, expected_version=expected_version
            )
            closed = existing.model_copy(
                update={"status": ConversationStatus.CLOSED, "version": existing.version + 1}
            )
            self._conversations[conversation_id] = closed
            return closed
