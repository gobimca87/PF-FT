from __future__ import annotations

import asyncio
from typing import Protocol

from pff_fa_ai.integration.execution.states import IdempotencyStatus


def build_idempotency_key(*, workflow_instance_id: str, operation_id: str) -> str:
    """doc 10 §46: key_source = workflow_instance_id + operation_id."""
    return f"{workflow_instance_id}:{operation_id}"


class IdempotencyStore(Protocol):
    async def get_status(self, key: str) -> IdempotencyStatus | None: ...

    async def mark_in_progress(self, key: str) -> None: ...

    async def mark_completed(self, key: str) -> None: ...

    async def mark_failed(self, key: str) -> None: ...


class InMemoryIdempotencyStore:
    def __init__(self) -> None:
        self._entries: dict[str, IdempotencyStatus] = {}
        self._lock = asyncio.Lock()

    async def get_status(self, key: str) -> IdempotencyStatus | None:
        return self._entries.get(key)

    async def mark_in_progress(self, key: str) -> None:
        async with self._lock:
            self._entries[key] = IdempotencyStatus.IN_PROGRESS

    async def mark_completed(self, key: str) -> None:
        async with self._lock:
            self._entries[key] = IdempotencyStatus.COMPLETED

    async def mark_failed(self, key: str) -> None:
        async with self._lock:
            self._entries[key] = IdempotencyStatus.FAILED
