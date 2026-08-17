from __future__ import annotations

from pf_ft_ai.messaging.events.models import EventEnvelope
from pf_ft_ai.messaging.events.registry import EventRoute, EventRouteRegistry


class EventRouter:
    """doc 11 §134 — resolves a route only; execution is the caller's responsibility."""

    def __init__(self, registry: EventRouteRegistry) -> None:
        self._registry = registry

    def resolve_handler(self, event: EventEnvelope) -> EventRoute | None:
        return self._registry.resolve(event.event_type)
