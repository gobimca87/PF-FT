from datetime import UTC, datetime

from pf_ft_ai.messaging.events.models import EventEnvelope
from pf_ft_ai.messaging.events.registry import EventRoute
from pf_ft_ai.messaging.handlers.external import ExternalEventHandler


async def test_should_acknowledge_an_external_event() -> None:
    handler = ExternalEventHandler()
    now = datetime.now(UTC)
    event = EventEnvelope(
        event_id="evt-1",
        event_type="PARTNER_SYSTEM_NOTIFIED",
        event_version="1.0.0",
        source="partner-system",
        subject="partner/notification-1",
        occurred_at=now,
        published_at=now,
        correlation_id="corr-1",
        tenant_id="tenant-1",
    )
    route = EventRoute(event_type="PARTNER_SYSTEM_NOTIFIED", handler="external")

    outcome = await handler.handle(event, route=route)

    assert outcome.succeeded is True
    assert outcome.reason_code == "EXTERNAL_EVENT_ACKNOWLEDGED"
