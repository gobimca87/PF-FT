from __future__ import annotations

from pf_ft_ai.messaging.events.models import EventEnvelope
from pf_ft_ai.messaging.events.registry import EventRoute
from pf_ft_ai.messaging.handlers.base import HandlerOutcome


class ExternalEventHandler:
    """doc 11 §72: source/schema validation and routing already ran upstream
    (`EventProcessingService`); no approved external-source-specific business handler
    exists yet, so this acknowledges receipt without executing anything further —
    the same honest-placeholder pattern as the empty `config/enterprise/` catalogs."""

    async def handle(self, event: EventEnvelope, *, route: EventRoute) -> HandlerOutcome:
        return HandlerOutcome(succeeded=True, reason_code="EXTERNAL_EVENT_ACKNOWLEDGED")
