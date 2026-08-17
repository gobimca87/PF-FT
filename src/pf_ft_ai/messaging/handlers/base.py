from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict

from pf_ft_ai.messaging.events.models import EventEnvelope
from pf_ft_ai.messaging.events.registry import EventRoute


class HandlerOutcome(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    succeeded: bool
    reason_code: str | None = None


class EventHandler(Protocol):
    """doc 11 §68."""

    async def handle(self, event: EventEnvelope, *, route: EventRoute) -> HandlerOutcome: ...
