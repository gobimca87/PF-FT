from __future__ import annotations

import asyncio
from collections import defaultdict

from pff_fa_ai.domain.conversation.value_objects import Message


class InMemoryMessageRepository:
    def __init__(self) -> None:
        self._messages: dict[str, list[Message]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def append(self, message: Message) -> Message:
        async with self._lock:
            self._messages[message.conversation_id].append(message)
            return message

    async def list(self, conversation_id: str, *, limit: int = 50) -> list[Message]:
        return self._messages.get(conversation_id, [])[-limit:]

    async def get_by_sequence(self, conversation_id: str, sequence_number: int) -> Message | None:
        for message in self._messages.get(conversation_id, []):
            if message.sequence_number == sequence_number:
                return message
        return None
