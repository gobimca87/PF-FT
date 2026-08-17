from datetime import UTC, datetime

from pf_ft_ai.domain.workflow.entities import WaitingInfo, WorkflowInstance
from pf_ft_ai.domain.workflow.states import WaitingType, WorkflowStatus
from pf_ft_ai.infrastructure.persistence.in_memory_workflow_repository import (
    InMemoryWorkflowRepository,
)
from pf_ft_ai.messaging.events.models import EventEnvelope
from pf_ft_ai.messaging.events.registry import EventRoute, EventRouteRegistry
from pf_ft_ai.messaging.events.states import EventProcessingStatus
from pf_ft_ai.messaging.handlers.base import HandlerOutcome
from pf_ft_ai.messaging.handlers.external import ExternalEventHandler
from pf_ft_ai.messaging.handlers.workflow_resume import (
    WorkflowResumeEventHandler,
    WorkflowResumeService,
)
from pf_ft_ai.messaging.reliability.dead_letter import InMemoryDeadLetterStore
from pf_ft_ai.messaging.reliability.idempotency import InMemoryEventIdempotencyStore
from pf_ft_ai.messaging.routing.router import EventRouter
from pf_ft_ai.messaging.service_bus.processing import EventProcessingService

_KNOWN_SOURCES = frozenset({"hil-service"})


class _ExplodingHandler:
    async def handle(self, event: EventEnvelope, *, route: EventRoute) -> HandlerOutcome:
        raise RuntimeError("boom")


def _event(
    *,
    event_id: str = "evt-1",
    event_type: str = "HIL_TASK_COMPLETED",
    source: str = "hil-service",
    workflow_instance_id: str | None = "wf-1",
) -> EventEnvelope:
    now = datetime.now(UTC)
    return EventEnvelope(
        event_id=event_id,
        event_type=event_type,
        event_version="1.0.0",
        source=source,
        subject="hil-task/task-1",
        occurred_at=now,
        published_at=now,
        correlation_id="corr-1",
        tenant_id="tenant-1",
        organization_id="club-123",
        workflow_instance_id=workflow_instance_id,
    )


async def _resumable_workflow() -> InMemoryWorkflowRepository:
    repository = InMemoryWorkflowRepository()
    now = datetime.now(UTC)
    await repository.create(
        WorkflowInstance(
            workflow_instance_id="wf-1",
            workflow_type="affiliation",
            workflow_version="1.0.0",
            status=WorkflowStatus.WAITING_FOR_EXTERNAL_EVENT,
            current_state="WAITING_FOR_EXTERNAL_EVENT",
            organization_id="club-123",
            started_at=now,
            updated_at=now,
            waiting=WaitingInfo(
                type=WaitingType.WAITING_FOR_EXTERNAL_EVENT,
                reason="hil_pending",
                created_at=now,
                resume_node="refresh_erc",
                expected_event_type="HIL_TASK_COMPLETED",
            ),
        )
    )
    return repository


def _service(
    *,
    registry: EventRouteRegistry,
    handlers: dict[str, object],
    subscription: str = "pf-ft-ai-runtime-dev",
) -> tuple[EventProcessingService, InMemoryDeadLetterStore]:
    dead_letter = InMemoryDeadLetterStore()
    service = EventProcessingService(
        router=EventRouter(registry),
        idempotency=InMemoryEventIdempotencyStore(),
        consumer_id="ai-workflow",
        known_sources=_KNOWN_SOURCES,
        handlers=handlers,  # type: ignore[arg-type]
        dead_letter=dead_letter,
        subscription_name=subscription,
    )
    return service, dead_letter


async def test_should_process_a_workflow_resume_event_end_to_end() -> None:
    repository = await _resumable_workflow()
    registry = EventRouteRegistry()
    registry.register(EventRoute(event_type="HIL_TASK_COMPLETED", handler="workflow.resume"))
    handler = WorkflowResumeEventHandler(WorkflowResumeService(repository))
    service, _dead_letter = _service(registry=registry, handlers={"workflow.resume": handler})

    outcome = await service.process(_event())

    assert outcome.status is EventProcessingStatus.PROCESSED
    resumed = await repository.get("wf-1")
    assert resumed is not None
    assert resumed.status is WorkflowStatus.RESUMING


async def test_should_reject_an_event_from_an_unknown_source() -> None:
    registry = EventRouteRegistry()
    service, _dead_letter = _service(registry=registry, handlers={})

    outcome = await service.process(_event(source="rogue-service"))

    assert outcome.status is EventProcessingStatus.FAILED


async def test_should_report_duplicate_for_a_second_delivery_of_the_same_event() -> None:
    repository = await _resumable_workflow()
    registry = EventRouteRegistry()
    registry.register(EventRoute(event_type="HIL_TASK_COMPLETED", handler="workflow.resume"))
    handler = WorkflowResumeEventHandler(WorkflowResumeService(repository))
    service, _dead_letter = _service(registry=registry, handlers={"workflow.resume": handler})

    first = await service.process(_event())
    second = await service.process(_event())

    assert first.status is EventProcessingStatus.PROCESSED
    assert second.status is EventProcessingStatus.DUPLICATE


async def test_should_mark_unsupported_event_types_processed_without_retry() -> None:
    registry = EventRouteRegistry()
    service, _dead_letter = _service(registry=registry, handlers={})

    outcome = await service.process(_event(event_type="SOME_UNROUTED_EVENT"))

    assert outcome.status is EventProcessingStatus.PROCESSED
    assert outcome.reason_code == "UNSUPPORTED_EVENT_TYPE"


async def test_should_fail_when_the_resolved_handler_is_not_configured() -> None:
    registry = EventRouteRegistry()
    registry.register(EventRoute(event_type="OFFICIAL_UPDATED", handler="erc.refresh"))
    service, _dead_letter = _service(registry=registry, handlers={})

    outcome = await service.process(_event(event_type="OFFICIAL_UPDATED"))

    assert outcome.status is EventProcessingStatus.FAILED
    assert outcome.reason_code == "HANDLER_NOT_CONFIGURED"


async def test_should_dead_letter_when_a_handler_raises() -> None:
    registry = EventRouteRegistry()
    registry.register(EventRoute(event_type="HIL_TASK_COMPLETED", handler="workflow.resume"))
    service, dead_letter = _service(
        registry=registry, handlers={"workflow.resume": _ExplodingHandler()}
    )

    outcome = await service.process(_event())

    assert outcome.status is EventProcessingStatus.DEAD_LETTERED
    records = await dead_letter.list_all()
    assert len(records) == 1
    assert records[0].failure_code == "HANDLER_EXCEPTION"


async def test_should_process_an_external_event() -> None:
    registry = EventRouteRegistry()
    registry.register(EventRoute(event_type="PARTNER_NOTIFIED", handler="external"))
    service, _dead_letter = _service(
        registry=registry, handlers={"external": ExternalEventHandler()}
    )

    outcome = await service.process(
        _event(event_type="PARTNER_NOTIFIED", workflow_instance_id=None)
    )

    assert outcome.status is EventProcessingStatus.PROCESSED
