from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from pff_fa_ai.common.exceptions import ConfigurationError

HandlerKind = Literal["workflow.resume", "erc.refresh", "external"]


class EventRoute(BaseModel):
    """doc 11 §65-66/§127 — routing is deterministic runtime configuration; the SLM
    never decides which handler processes a production event (doc 11 §67, §102)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_type: str
    handler: HandlerKind
    target_section: str | None = None
    enabled: bool = True


class EventRouteRegistry:
    """doc 11 §131 — must reject duplicate/conflicting registrations."""

    def __init__(self) -> None:
        self._routes: dict[str, EventRoute] = {}

    def register(self, route: EventRoute) -> None:
        if route.event_type in self._routes:
            raise ConfigurationError(f"Duplicate route registered for: {route.event_type}")
        self._routes[route.event_type] = route

    def resolve(self, event_type: str) -> EventRoute | None:
        route = self._routes.get(event_type)
        if route is None or not route.enabled:
            return None
        return route
