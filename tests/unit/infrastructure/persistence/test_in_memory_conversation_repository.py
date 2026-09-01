from datetime import UTC, datetime

import pytest

from pff_fa_ai.common.exceptions import WorkflowError
from pff_fa_ai.domain.conversation.entities import Conversation
from pff_fa_ai.domain.conversation.states import ConversationStatus
from pff_fa_ai.infrastructure.persistence.in_memory_conversation_repository import (
    InMemoryConversationRepository,
)


def _new_conversation(conversation_id: str = "conv-1") -> Conversation:
    now = datetime.now(UTC)
    return Conversation(
        conversation_id=conversation_id,
        user_reference="user-1",
        session_id="sess-1",
        status=ConversationStatus.NEW,
        created_at=now,
        updated_at=now,
    )


async def test_should_create_and_get_a_conversation() -> None:
    repository = InMemoryConversationRepository()
    conversation = _new_conversation()

    await repository.create(conversation)
    loaded = await repository.get(conversation.conversation_id)

    assert loaded == conversation


async def test_should_return_none_for_unknown_conversation() -> None:
    repository = InMemoryConversationRepository()

    assert await repository.get("missing") is None


async def test_should_reject_creating_a_duplicate_conversation_id() -> None:
    repository = InMemoryConversationRepository()
    conversation = _new_conversation()
    await repository.create(conversation)

    with pytest.raises(WorkflowError, match="already exists"):
        await repository.create(conversation)


async def test_should_update_with_matching_expected_version() -> None:
    repository = InMemoryConversationRepository()
    conversation = _new_conversation()
    await repository.create(conversation)
    updated = conversation.model_copy(update={"status": ConversationStatus.ACTIVE, "version": 2})

    result = await repository.update(updated, expected_version=1)

    assert result.status is ConversationStatus.ACTIVE


async def test_should_reject_update_with_stale_expected_version() -> None:
    repository = InMemoryConversationRepository()
    conversation = _new_conversation()
    await repository.create(conversation)
    updated = conversation.model_copy(update={"version": 2})

    with pytest.raises(WorkflowError, match="Concurrency conflict"):
        await repository.update(updated, expected_version=99)


async def test_should_reject_update_of_missing_conversation() -> None:
    repository = InMemoryConversationRepository()

    with pytest.raises(WorkflowError, match="not found"):
        await repository.update(_new_conversation(), expected_version=1)


async def test_should_close_a_conversation() -> None:
    repository = InMemoryConversationRepository()
    conversation = _new_conversation()
    await repository.create(conversation)

    closed = await repository.close(conversation.conversation_id, expected_version=1)

    assert closed.status is ConversationStatus.CLOSED
    assert closed.version == 2


async def test_should_reject_closing_missing_conversation() -> None:
    repository = InMemoryConversationRepository()

    with pytest.raises(WorkflowError, match="not found"):
        await repository.close("missing", expected_version=1)
