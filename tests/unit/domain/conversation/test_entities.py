from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from pf_ft_ai.domain.conversation.entities import Conversation
from pf_ft_ai.domain.conversation.states import ConversationStatus
from pf_ft_ai.domain.conversation.value_objects import Message, MessageRole


def test_should_create_a_new_conversation_at_version_one() -> None:
    now = datetime.now(UTC)

    conversation = Conversation(
        conversation_id="conv-123",
        user_reference="user-123",
        session_id="sess-123",
        status=ConversationStatus.NEW,
        created_at=now,
        updated_at=now,
    )

    assert conversation.version == 1
    assert conversation.active_workflow_instance_id is None


def test_should_transition_via_immutable_copy_with_incremented_version() -> None:
    now = datetime.now(UTC)
    conversation = Conversation(
        conversation_id="conv-123",
        user_reference="user-123",
        session_id="sess-123",
        status=ConversationStatus.NEW,
        created_at=now,
        updated_at=now,
    )

    activated = conversation.model_copy(
        update={"status": ConversationStatus.ACTIVE, "version": conversation.version + 1}
    )

    assert conversation.status is ConversationStatus.NEW  # original untouched
    assert activated.status is ConversationStatus.ACTIVE
    assert activated.version == 2


def test_should_reject_mutation_of_a_frozen_conversation() -> None:
    now = datetime.now(UTC)
    conversation = Conversation(
        conversation_id="conv-123",
        user_reference="user-123",
        session_id="sess-123",
        status=ConversationStatus.NEW,
        created_at=now,
        updated_at=now,
    )

    with pytest.raises(ValidationError):
        conversation.status = ConversationStatus.ACTIVE  # type: ignore[misc]


def test_should_create_a_message_with_a_role_and_sequence_number() -> None:
    message = Message(
        message_id="msg-1",
        conversation_id="conv-123",
        session_id="sess-123",
        role=MessageRole.USER,
        content="What is the affiliation status?",
        created_at=datetime.now(UTC),
        sequence_number=1,
    )

    assert message.role is MessageRole.USER
    assert message.metadata == {}
