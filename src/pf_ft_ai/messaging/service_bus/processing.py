from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict

from pf_ft_ai.common.exceptions import ValidationError
from pf_ft_ai.messaging.events.models import EventEnvelope
from pf_ft_ai.messaging.events.registry import HandlerKind
from pf_ft_ai.messaging.events.states import EventProcessingStatus
from pf_ft_ai.messaging.events.validator import validate_envelope
from pf_ft_ai.messaging.handlers.base import EventHandler
from pf_ft_ai.messaging.reliability.dead_letter import DeadLetterRecord, DeadLetterStore
from pf_ft_ai.messaging.reliability.idempotency import (
    EventIdempotencyStore,
    build_event_idempotency_key,
)
from pf_ft_ai.messaging.routing.router import EventRouter


class EventProcessingOutcome(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: EventProcessingStatus
    reason_code: str | None = None


class EventProcessingService:
    """doc 11 §133 — the central orchestrator: validate → deduplicate → route → execute
    → record outcome (doc 11 §33 consumer responsibilities)."""

    def __init__(
        self,
        *,
        router: EventRouter,
        idempotency: EventIdempotencyStore,
        consumer_id: str,
        known_sources: frozenset[str],
        handlers: dict[HandlerKind, EventHandler],
        dead_letter: DeadLetterStore,
        subscription_name: str,
    ) -> None:
        self._router = router
        self._idempotency = idempotency
        self._consumer_id = consumer_id
        self._known_sources = known_sources
        self._handlers = handlers
        self._dead_letter = dead_letter
        self._subscription_name = subscription_name

    async def process(self, envelope: EventEnvelope) -> EventProcessingOutcome:
        try:
            validate_envelope(envelope, known_sources=self._known_sources)
        except ValidationError as exc:
            return EventProcessingOutcome(
                status=EventProcessingStatus.FAILED, reason_code=exc.message
            )

        key = build_event_idempotency_key(event_id=envelope.event_id, consumer_id=self._consumer_id)
        claimed = await self._idempotency.try_claim(key)
        if not claimed:
            return EventProcessingOutcome(status=EventProcessingStatus.DUPLICATE)

        route = self._router.resolve_handler(envelope)
        if route is None:
            # doc 11 §39: unknown/unsupported event types are safely ignored, no retry.
            await self._idempotency.mark_completed(key)
            return EventProcessingOutcome(
                status=EventProcessingStatus.PROCESSED, reason_code="UNSUPPORTED_EVENT_TYPE"
            )

        handler = self._handlers.get(route.handler)
        if handler is None:
            await self._idempotency.mark_failed(key)
            return EventProcessingOutcome(
                status=EventProcessingStatus.FAILED, reason_code="HANDLER_NOT_CONFIGURED"
            )

        try:
            outcome = await handler.handle(envelope, route=route)
        except Exception as exc:
            await self._idempotency.mark_failed(key)
            await self._dead_letter.put(
                DeadLetterRecord(
                    event_id=envelope.event_id,
                    event_type=envelope.event_type,
                    event_version=envelope.event_version,
                    source=envelope.source,
                    subscription=self._subscription_name,
                    first_received_at=envelope.occurred_at,
                    last_attempt_at=datetime.now(UTC),
                    attempt_count=1,
                    failure_code="HANDLER_EXCEPTION",
                    failure_reason=str(exc),
                    correlation_id=envelope.correlation_id,
                    payload=envelope.payload,
                )
            )
            return EventProcessingOutcome(
                status=EventProcessingStatus.DEAD_LETTERED, reason_code="HANDLER_EXCEPTION"
            )

        if outcome.succeeded:
            await self._idempotency.mark_completed(key)
            return EventProcessingOutcome(
                status=EventProcessingStatus.PROCESSED, reason_code=outcome.reason_code
            )
        await self._idempotency.mark_failed(key)
        return EventProcessingOutcome(
            status=EventProcessingStatus.FAILED, reason_code=outcome.reason_code
        )
