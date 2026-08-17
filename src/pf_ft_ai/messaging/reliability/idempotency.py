from __future__ import annotations

import asyncio
from typing import Protocol

from pf_ft_ai.integration.execution.states import IdempotencyStatus

_CLAIMED_STATUSES = frozenset({IdempotencyStatus.IN_PROGRESS, IdempotencyStatus.COMPLETED})


def build_event_idempotency_key(*, event_id: str, consumer_id: str) -> str:
    """doc 11 §41 — event_id + consumer_id composite key."""
    return f"{event_id}:{consumer_id}"


class EventIdempotencyStore(Protocol):
    async def try_claim(self, key: str) -> bool: ...

    async def mark_completed(self, key: str) -> None: ...

    async def mark_failed(self, key: str) -> None: ...

    async def get_status(self, key: str) -> IdempotencyStatus | None: ...


class InMemoryEventIdempotencyStore:
    """doc 11 §44: concurrent duplicate deliveries must use an atomic check+claim, not a
    separate check-then-write — `try_claim` holds the lock across both."""

    def __init__(self) -> None:
        self._entries: dict[str, IdempotencyStatus] = {}
        self._lock = asyncio.Lock()

    async def try_claim(self, key: str) -> bool:
        async with self._lock:
            if self._entries.get(key) in _CLAIMED_STATUSES:
                return False
            self._entries[key] = IdempotencyStatus.IN_PROGRESS
            return True

    async def mark_completed(self, key: str) -> None:
        async with self._lock:
            self._entries[key] = IdempotencyStatus.COMPLETED

    async def mark_failed(self, key: str) -> None:
        async with self._lock:
            self._entries[key] = IdempotencyStatus.FAILED

    async def get_status(self, key: str) -> IdempotencyStatus | None:
        return self._entries.get(key)
