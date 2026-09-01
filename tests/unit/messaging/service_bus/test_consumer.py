from datetime import UTC, datetime
from typing import Any

from pff_fa_ai.domain.workflow.entities import WaitingInfo, WorkflowInstance
from pff_fa_ai.domain.workflow.states import WaitingType, WorkflowStatus
from pff_fa_ai.infrastructure.persistence.in_memory_workflow_repository import (
    InMemoryWorkflowRepository,
)
from pff_fa_ai.messaging.events.models import EventEnvelope
from pff_fa_ai.messaging.events.registry import EventRoute, EventRouteRegistry
from pff_fa_ai.messaging.events.states import EventProcessingStatus
from pff_fa_ai.messaging.handlers.base import HandlerOutcome
from pff_fa_ai.messaging.handlers.workflow_resume import (
    WorkflowResumeEventHandler,
    WorkflowResumeService,
)
from pff_fa_ai.messaging.reliability.dead_letter import InMemoryDeadLetterStore
from pff_fa_ai.messaging.reliability.idempotency import InMemoryEventIdempotencyStore
from pff_fa_ai.messaging.routing.router import EventRouter
from pff_fa_ai.messaging.service_bus.consumer import EventConsumer
from pff_fa_ai.messaging.service_bus.processing import EventProcessingService


class _ExplodingHandler:
    async def handle(self, event: EventEnvelope, *, route: EventRoute) -> HandlerOutcome:
        raise RuntimeError("boom")


class _FakeMessage:
    def __init__(self, body: dict[str, Any]) -> None:
        self.body = body


class _FakeReceiver:
    def __init__(self, messages: list[_FakeMessage]) -> None:
        self._messages = messages
        self.completed: list[_FakeMessage] = []
        self.abandoned: list[_FakeMessage] = []
        self.dead_lettered: list[tuple[_FakeMessage, str, str]] = []

    async def receive_messages(
        self, *, max_message_count: int, max_wait_time: float
    ) -> list[_FakeMessage]:
        batch, self._messages = (
            self._messages[:max_message_count],
            self._messages[max_message_count:],
        )
        return batch

    async def complete_message(self, message: _FakeMessage) -> None:
        self.completed.append(message)

    async def abandon_message(self, message: _FakeMessage) -> None:
        self.abandoned.append(message)

    async def dead_letter_message(
        self, message: _FakeMessage, *, reason: str, error_description: str
    ) -> None:
        self.dead_lettered.append((message, reason, error_description))

    def decode_body(self, message: _FakeMessage) -> dict[str, Any]:
        return message.body


def _event_body(**overrides: object) -> dict[str, Any]:
    now = datetime.now(UTC).isoformat()
    body: dict[str, Any] = {
        "event_id": "evt-1",
        "event_type": "HIL_TASK_COMPLETED",
        "event_version": "1.0.0",
        "source": "hil-service",
        "subject": "hil-task/task-1",
        "occurred_at": now,
        "published_at": now,
        "correlation_id": "corr-1",
        "tenant_id": "tenant-1",
        "organization_id": "club-123",
        "workflow_instance_id": "wf-1",
    }
    body.update(overrides)
    return body


async def _build_service() -> tuple[EventProcessingService, InMemoryWorkflowRepository]:
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
    registry = EventRouteRegistry()
    registry.register(EventRoute(event_type="HIL_TASK_COMPLETED", handler="workflow.resume"))
    handler = WorkflowResumeEventHandler(WorkflowResumeService(repository))
    service = EventProcessingService(
        router=EventRouter(registry),
        idempotency=InMemoryEventIdempotencyStore(),
        consumer_id="ai-workflow",
        known_sources=frozenset({"hil-service"}),
        handlers={"workflow.resume": handler},
        dead_letter=InMemoryDeadLetterStore(),
        subscription_name="pff-fa-ai-runtime-dev",
    )
    return service, repository


async def test_should_complete_a_successfully_processed_message() -> None:
    service, repository = await _build_service()
    receiver = _FakeReceiver([_FakeMessage(_event_body())])
    consumer = EventConsumer(receiver=receiver, processing=service)

    outcomes = await consumer.consume_once()

    assert outcomes[0].status is EventProcessingStatus.PROCESSED
    assert len(receiver.completed) == 1
    assert len(receiver.abandoned) == 0
    resumed = await repository.get("wf-1")
    assert resumed is not None
    assert resumed.status is WorkflowStatus.RESUMING


async def test_should_dead_letter_a_message_whose_handler_raises() -> None:
    registry = EventRouteRegistry()
    registry.register(EventRoute(event_type="HIL_TASK_COMPLETED", handler="workflow.resume"))
    service = EventProcessingService(
        router=EventRouter(registry),
        idempotency=InMemoryEventIdempotencyStore(),
        consumer_id="ai-workflow",
        known_sources=frozenset({"hil-service"}),
        handlers={"workflow.resume": _ExplodingHandler()},
        dead_letter=InMemoryDeadLetterStore(),
        subscription_name="pff-fa-ai-runtime-dev",
    )
    receiver = _FakeReceiver([_FakeMessage(_event_body())])
    consumer = EventConsumer(receiver=receiver, processing=service)

    outcomes = await consumer.consume_once()

    assert outcomes[0].status is EventProcessingStatus.DEAD_LETTERED
    assert len(receiver.dead_lettered) == 1
    assert receiver.dead_lettered[0][1] == "HANDLER_EXCEPTION"
    assert len(receiver.completed) == 0
    assert len(receiver.abandoned) == 0


async def test_should_dead_letter_a_message_with_an_invalid_schema() -> None:
    service, _repository = await _build_service()
    receiver = _FakeReceiver([_FakeMessage({"not": "a valid envelope"})])
    consumer = EventConsumer(receiver=receiver, processing=service)

    outcomes = await consumer.consume_once()

    assert outcomes[0].status is EventProcessingStatus.DEAD_LETTERED
    assert len(receiver.dead_lettered) == 1
    assert receiver.dead_lettered[0][1] == "INVALID_SCHEMA"


async def test_should_abandon_a_message_that_fails_processing() -> None:
    service, _repository = await _build_service()
    # Wrong organization -> WorkflowResumeService rejects -> handler outcome FAILED.
    receiver = _FakeReceiver([_FakeMessage(_event_body(organization_id="club-999"))])
    consumer = EventConsumer(receiver=receiver, processing=service)

    outcomes = await consumer.consume_once()

    assert outcomes[0].status is EventProcessingStatus.FAILED
    assert len(receiver.abandoned) == 1
    assert len(receiver.completed) == 0


async def test_should_complete_a_duplicate_message_without_reprocessing() -> None:
    service, _repository = await _build_service()
    receiver = _FakeReceiver([_FakeMessage(_event_body()), _FakeMessage(_event_body())])
    consumer = EventConsumer(receiver=receiver, processing=service)

    outcomes = await consumer.consume_once()

    assert outcomes[0].status is EventProcessingStatus.PROCESSED
    assert outcomes[1].status is EventProcessingStatus.DUPLICATE
    assert len(receiver.completed) == 2


async def test_should_process_messages_in_batches_up_to_max_message_count() -> None:
    service, _repository = await _build_service()
    receiver = _FakeReceiver([_FakeMessage(_event_body()) for _ in range(3)])
    consumer = EventConsumer(receiver=receiver, processing=service, max_message_count=2)

    first_batch = await consumer.consume_once()
    second_batch = await consumer.consume_once()

    assert len(first_batch) == 2
    assert len(second_batch) == 1
