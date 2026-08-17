from __future__ import annotations

from typing import Any

from pydantic import ValidationError as PydanticValidationError

from pf_ft_ai.messaging.events.models import EventEnvelope
from pf_ft_ai.messaging.events.states import EventProcessingStatus
from pf_ft_ai.messaging.service_bus.client import ServiceBusReceiverPort
from pf_ft_ai.messaging.service_bus.processing import EventProcessingOutcome, EventProcessingService


class EventConsumer:
    """doc 11 §132: delegates all processing logic to `EventProcessingService`; this
    class only owns Service Bus message lifecycle (complete/abandon/dead-letter)."""

    def __init__(
        self,
        *,
        receiver: ServiceBusReceiverPort,
        processing: EventProcessingService,
        max_message_count: int = 10,
        max_wait_time: float = 5.0,
    ) -> None:
        self._receiver = receiver
        self._processing = processing
        self._max_message_count = max_message_count
        self._max_wait_time = max_wait_time

    async def consume_once(self) -> list[EventProcessingOutcome]:
        """Pull and process one batch; returns per-message outcomes (observability/tests)."""
        messages = await self._receiver.receive_messages(
            max_message_count=self._max_message_count, max_wait_time=self._max_wait_time
        )
        return [await self._handle_message(message) for message in messages]

    async def _handle_message(self, message: Any) -> EventProcessingOutcome:
        try:
            body = self._receiver.decode_body(message)
            envelope = EventEnvelope.model_validate(body)
        except (PydanticValidationError, ValueError) as exc:
            await self._receiver.dead_letter_message(
                message, reason="INVALID_SCHEMA", error_description=str(exc)
            )
            return EventProcessingOutcome(
                status=EventProcessingStatus.DEAD_LETTERED, reason_code="INVALID_SCHEMA"
            )

        outcome = await self._processing.process(envelope)

        if outcome.status in (EventProcessingStatus.PROCESSED, EventProcessingStatus.DUPLICATE):
            await self._receiver.complete_message(message)
        elif outcome.status is EventProcessingStatus.DEAD_LETTERED:
            await self._receiver.dead_letter_message(
                message,
                reason=outcome.reason_code or "PROCESSING_FAILED",
                error_description=outcome.reason_code or "",
            )
        else:
            # doc 11 §35/§74: FAILED (retryable) — abandon so Service Bus redelivers up
            # to the subscription's own max_delivery_count; this consumer never loops
            # indefinitely on a single lock.
            await self._receiver.abandon_message(message)

        return outcome
