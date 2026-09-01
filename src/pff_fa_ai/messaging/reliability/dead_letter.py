from __future__ import annotations

from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict


class DeadLetterRecord(BaseModel):
    """doc 11 §80 DLQ metadata — the original event is preserved via `payload` (doc 11
    §81), not discarded."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: str
    event_type: str
    event_version: str
    source: str
    subscription: str
    first_received_at: datetime
    last_attempt_at: datetime
    attempt_count: int
    failure_code: str
    failure_reason: str
    correlation_id: str
    trace_id: str | None = None
    payload: dict[str, object]


class DeadLetterStore(Protocol):
    async def put(self, record: DeadLetterRecord) -> None: ...

    async def get(self, event_id: str) -> DeadLetterRecord | None: ...

    async def list_all(self) -> tuple[DeadLetterRecord, ...]: ...


class InMemoryDeadLetterStore:
    def __init__(self) -> None:
        self._records: dict[str, DeadLetterRecord] = {}

    async def put(self, record: DeadLetterRecord) -> None:
        self._records[record.event_id] = record

    async def get(self, event_id: str) -> DeadLetterRecord | None:
        return self._records.get(event_id)

    async def list_all(self) -> tuple[DeadLetterRecord, ...]:
        return tuple(self._records.values())
