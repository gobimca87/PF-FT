from datetime import UTC, datetime

from pf_ft_ai.messaging.events.models import EventEnvelope
from pf_ft_ai.messaging.events.registry import EventRoute, EventRouteRegistry
from pf_ft_ai.messaging.routing.router import EventRouter


def _envelope(event_type: str) -> EventEnvelope:
    now = datetime.now(UTC)
    return EventEnvelope(
        event_id="evt-1",
        event_type=event_type,
        event_version="1.0.0",
        source="affiliation-service",
        subject="official/official-123",
        occurred_at=now,
        published_at=now,
        correlation_id="corr-1",
        tenant_id="tenant-1",
    )


def test_should_resolve_the_registered_handler_for_an_event() -> None:
    registry = EventRouteRegistry()
    registry.register(EventRoute(event_type="HIL_TASK_COMPLETED", handler="workflow.resume"))
    router = EventRouter(registry)

    route = router.resolve_handler(_envelope("HIL_TASK_COMPLETED"))

    assert route is not None
    assert route.handler == "workflow.resume"


def test_should_return_none_for_an_unrouted_event() -> None:
    router = EventRouter(EventRouteRegistry())

    assert router.resolve_handler(_envelope("UNKNOWN_EVENT")) is None
