from datetime import UTC, datetime

from pff_fa_ai.domain.conversation.value_objects import Message, MessageRole
from pff_fa_ai.infrastructure.persistence.in_memory_message_repository import (
    InMemoryMessageRepository,
)


def _message(conversation_id: str, sequence_number: int) -> Message:
    return Message(
        message_id=f"msg-{sequence_number}",
        conversation_id=conversation_id,
        session_id="sess-1",
        role=MessageRole.USER,
        content=f"message {sequence_number}",
        created_at=datetime.now(UTC),
        sequence_number=sequence_number,
    )


async def test_should_append_and_list_messages_in_order() -> None:
    repository = InMemoryMessageRepository()
    for sequence_number in range(1, 4):
        await repository.append(_message("conv-1", sequence_number))

    messages = await repository.list("conv-1")

    assert [message.sequence_number for message in messages] == [1, 2, 3]


async def test_should_respect_the_limit_when_listing() -> None:
    repository = InMemoryMessageRepository()
    for sequence_number in range(1, 6):
        await repository.append(_message("conv-1", sequence_number))

    messages = await repository.list("conv-1", limit=2)

    assert [message.sequence_number for message in messages] == [4, 5]


async def test_should_return_empty_list_for_unknown_conversation() -> None:
    repository = InMemoryMessageRepository()

    assert await repository.list("missing") == []


async def test_should_find_message_by_sequence_number() -> None:
    repository = InMemoryMessageRepository()
    await repository.append(_message("conv-1", 1))
    await repository.append(_message("conv-1", 2))

    found = await repository.get_by_sequence("conv-1", 2)

    assert found is not None
    assert found.message_id == "msg-2"


async def test_should_return_none_when_sequence_number_not_found() -> None:
    repository = InMemoryMessageRepository()
    await repository.append(_message("conv-1", 1))

    assert await repository.get_by_sequence("conv-1", 99) is None
