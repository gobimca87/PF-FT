from __future__ import annotations

from datetime import UTC, datetime

from pf_ft_ai.common.claims import ClaimsContext
from pf_ft_ai.common.correlation import new_id
from pf_ft_ai.common.exceptions import ValidationError, WorkflowError
from pf_ft_ai.configuration.models import ConversationSecuritySettings, ConversationSettings
from pf_ft_ai.domain.conversation.entities import Conversation
from pf_ft_ai.domain.conversation.repository import ConversationRepository, MessageRepository
from pf_ft_ai.domain.conversation.states import ConversationStatus
from pf_ft_ai.domain.conversation.value_objects import Message, MessageRole


class ConversationService:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
        settings: ConversationSettings,
        security: ConversationSecuritySettings,
    ) -> None:
        self._conversations = conversation_repository
        self._messages = message_repository
        self._settings = settings
        self._security = security

    async def start_conversation(
        self, *, conversation_id: str, session_id: str, claims: ClaimsContext
    ) -> Conversation:
        now = datetime.now(UTC)
        conversation = Conversation(
            conversation_id=conversation_id,
            user_reference=claims.subject,
            session_id=session_id,
            status=ConversationStatus.NEW,
            created_at=now,
            updated_at=now,
        )
        return await self._conversations.create(conversation)

    async def resolve_conversation(
        self, conversation_id: str, *, claims: ClaimsContext
    ) -> Conversation:
        conversation = await self._conversations.get(conversation_id)
        if conversation is None:
            raise WorkflowError(f"Conversation not found: {conversation_id}")
        self._assert_ownership(conversation, claims)
        return conversation

    async def list_messages(self, conversation_id: str) -> list[Message]:
        return await self._messages.list(conversation_id, limit=self._settings.max_history_messages)

    async def append_user_message(
        self, conversation: Conversation, *, content: str
    ) -> tuple[Conversation, Message]:
        return await self._append_message(conversation, role=MessageRole.USER, content=content)

    async def append_assistant_message(
        self, conversation: Conversation, *, content: str
    ) -> tuple[Conversation, Message]:
        return await self._append_message(conversation, role=MessageRole.ASSISTANT, content=content)

    async def close_conversation(self, conversation: Conversation) -> Conversation:
        return await self._conversations.close(
            conversation.conversation_id, expected_version=conversation.version
        )

    def _assert_ownership(self, conversation: Conversation, claims: ClaimsContext) -> None:
        if self._security.enforce_ownership and conversation.user_reference != claims.subject:
            raise ValidationError("Conversation does not belong to the authenticated subject")

    async def _append_message(
        self, conversation: Conversation, *, role: MessageRole, content: str
    ) -> tuple[Conversation, Message]:
        if len(content) > self._settings.max_message_size:
            raise ValidationError(
                f"Message exceeds max_message_size ({self._settings.max_message_size})"
            )

        next_sequence = conversation.message_count + 1
        message = Message(
            message_id=new_id("msg"),
            conversation_id=conversation.conversation_id,
            session_id=conversation.session_id,
            role=role,
            content=content,
            created_at=datetime.now(UTC),
            sequence_number=next_sequence,
        )
        await self._messages.append(message)

        resumable_statuses = (ConversationStatus.NEW, ConversationStatus.WAITING_FOR_USER)
        new_status = (
            ConversationStatus.ACTIVE
            if conversation.status in resumable_statuses
            else conversation.status
        )
        updated = conversation.model_copy(
            update={
                "status": new_status,
                "updated_at": message.created_at,
                "message_count": next_sequence,
                "version": conversation.version + 1,
            }
        )
        await self._conversations.update(updated, expected_version=conversation.version)
        return updated, message
