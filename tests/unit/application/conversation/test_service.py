import pytest

from pf_ft_ai.application.conversation.service import ConversationService
from pf_ft_ai.common.claims import ClaimsContext
from pf_ft_ai.common.exceptions import ValidationError, WorkflowError
from pf_ft_ai.configuration.models import ConversationSecuritySettings, ConversationSettings
from pf_ft_ai.domain.conversation.states import ConversationStatus
from pf_ft_ai.infrastructure.persistence.in_memory_conversation_repository import (
    InMemoryConversationRepository,
)
from pf_ft_ai.infrastructure.persistence.in_memory_message_repository import (
    InMemoryMessageRepository,
)

SETTINGS = ConversationSettings(
    max_history_messages=50,
    max_history_tokens=12000,
    summary_threshold_tokens=10000,
    max_message_size=20,
)
SECURITY = ConversationSecuritySettings(enforce_ownership=True, enforce_tenant_isolation=True)
CLAIMS = ClaimsContext(subject="user-1", organization="club-1")
OTHER_CLAIMS = ClaimsContext(subject="user-2", organization="club-1")


def _service() -> ConversationService:
    return ConversationService(
        InMemoryConversationRepository(), InMemoryMessageRepository(), SETTINGS, SECURITY
    )


async def test_should_start_a_new_conversation_owned_by_the_caller() -> None:
    service = _service()

    conversation = await service.start_conversation(
        conversation_id="conv-1", session_id="sess-1", claims=CLAIMS
    )

    assert conversation.status is ConversationStatus.NEW
    assert conversation.user_reference == CLAIMS.subject


async def test_should_resolve_an_owned_conversation() -> None:
    service = _service()
    await service.start_conversation(conversation_id="conv-1", session_id="sess-1", claims=CLAIMS)

    resolved = await service.resolve_conversation("conv-1", claims=CLAIMS)

    assert resolved.conversation_id == "conv-1"


async def test_should_reject_resolving_someone_elses_conversation() -> None:
    service = _service()
    await service.start_conversation(conversation_id="conv-1", session_id="sess-1", claims=CLAIMS)

    with pytest.raises(ValidationError, match="does not belong"):
        await service.resolve_conversation("conv-1", claims=OTHER_CLAIMS)


async def test_should_raise_when_conversation_not_found() -> None:
    service = _service()

    with pytest.raises(WorkflowError, match="not found"):
        await service.resolve_conversation("missing", claims=CLAIMS)


async def test_should_append_a_user_message_and_activate_the_conversation() -> None:
    service = _service()
    conversation = await service.start_conversation(
        conversation_id="conv-1", session_id="sess-1", claims=CLAIMS
    )

    updated, message = await service.append_user_message(conversation, content="hello")

    assert updated.status is ConversationStatus.ACTIVE
    assert updated.message_count == 1
    assert message.sequence_number == 1


async def test_should_keep_sequence_numbers_monotonic_across_messages() -> None:
    service = _service()
    conversation = await service.start_conversation(
        conversation_id="conv-1", session_id="sess-1", claims=CLAIMS
    )

    conversation, first = await service.append_user_message(conversation, content="one")
    conversation, second = await service.append_assistant_message(conversation, content="two")

    assert (first.sequence_number, second.sequence_number) == (1, 2)
    assert conversation.message_count == 2


async def test_should_reject_a_message_over_the_configured_size_limit() -> None:
    service = _service()
    conversation = await service.start_conversation(
        conversation_id="conv-1", session_id="sess-1", claims=CLAIMS
    )

    with pytest.raises(ValidationError, match="max_message_size"):
        await service.append_user_message(conversation, content="x" * 21)


async def test_should_close_a_conversation() -> None:
    service = _service()
    conversation = await service.start_conversation(
        conversation_id="conv-1", session_id="sess-1", claims=CLAIMS
    )

    closed = await service.close_conversation(conversation)

    assert closed.status is ConversationStatus.CLOSED


async def test_should_list_appended_messages() -> None:
    service = _service()
    conversation = await service.start_conversation(
        conversation_id="conv-1", session_id="sess-1", claims=CLAIMS
    )
    await service.append_user_message(conversation, content="hi")

    messages = await service.list_messages("conv-1")

    assert [message.content for message in messages] == ["hi"]
