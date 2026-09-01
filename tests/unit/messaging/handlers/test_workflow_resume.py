from datetime import UTC, datetime

from pff_fa_ai.domain.workflow.entities import WaitingInfo, WorkflowInstance
from pff_fa_ai.domain.workflow.states import WaitingType, WorkflowStatus
from pff_fa_ai.infrastructure.persistence.in_memory_workflow_repository import (
    InMemoryWorkflowRepository,
)
from pff_fa_ai.messaging.events.models import EventEnvelope
from pff_fa_ai.messaging.events.registry import EventRoute
from pff_fa_ai.messaging.handlers.workflow_resume import (
    WorkflowResumeEventHandler,
    WorkflowResumeService,
)


def _workflow(
    *,
    workflow_instance_id: str = "wf-1",
    organization_id: str = "club-123",
    status: WorkflowStatus = WorkflowStatus.WAITING_FOR_EXTERNAL_EVENT,
    expected_event_type: str | None = "HIL_TASK_COMPLETED",
) -> WorkflowInstance:
    now = datetime.now(UTC)
    waiting = (
        WaitingInfo(
            type=WaitingType.WAITING_FOR_EXTERNAL_EVENT,
            reason="hil_pending",
            created_at=now,
            resume_node="refresh_erc",
            expected_event_type=expected_event_type,
        )
        if status is WorkflowStatus.WAITING_FOR_EXTERNAL_EVENT
        else None
    )
    return WorkflowInstance(
        workflow_instance_id=workflow_instance_id,
        workflow_type="affiliation",
        workflow_version="1.0.0",
        status=status,
        current_state=status.value,
        organization_id=organization_id,
        started_at=now,
        updated_at=now,
        waiting=waiting,
    )


def _event(
    *,
    event_type: str = "HIL_TASK_COMPLETED",
    organization_id: str | None = "club-123",
    workflow_instance_id: str | None = "wf-1",
) -> EventEnvelope:
    now = datetime.now(UTC)
    return EventEnvelope(
        event_id="evt-1",
        event_type=event_type,
        event_version="1.0.0",
        source="hil-service",
        subject="hil-task/task-1",
        occurred_at=now,
        published_at=now,
        correlation_id="corr-1",
        tenant_id="tenant-1",
        organization_id=organization_id,
        workflow_instance_id=workflow_instance_id,
    )


async def test_should_resume_a_waiting_workflow_on_a_matching_event() -> None:
    repository = InMemoryWorkflowRepository()
    await repository.create(_workflow())
    service = WorkflowResumeService(repository)

    outcome = await service.resume(workflow_instance_id="wf-1", event=_event())

    assert outcome.resumed is True
    assert outcome.workflow is not None
    assert outcome.workflow.status is WorkflowStatus.RESUMING
    assert outcome.workflow.current_state == "refresh_erc"


async def test_should_reject_resuming_an_unknown_workflow() -> None:
    repository = InMemoryWorkflowRepository()
    service = WorkflowResumeService(repository)

    outcome = await service.resume(workflow_instance_id="does-not-exist", event=_event())

    assert outcome.resumed is False
    assert outcome.reason_code == "WORKFLOW_NOT_FOUND"


async def test_should_reject_resuming_a_workflow_from_a_different_organization() -> None:
    repository = InMemoryWorkflowRepository()
    await repository.create(_workflow(organization_id="club-999"))
    service = WorkflowResumeService(repository)

    outcome = await service.resume(
        workflow_instance_id="wf-1", event=_event(organization_id="club-123")
    )

    assert outcome.resumed is False
    assert outcome.reason_code == "ORGANIZATION_MISMATCH"


async def test_should_reject_resuming_a_workflow_that_is_not_waiting() -> None:
    repository = InMemoryWorkflowRepository()
    await repository.create(_workflow(status=WorkflowStatus.REASONING))
    service = WorkflowResumeService(repository)

    outcome = await service.resume(workflow_instance_id="wf-1", event=_event())

    assert outcome.resumed is False
    assert outcome.reason_code == "WORKFLOW_NOT_WAITING"


async def test_should_reject_resuming_a_waiting_workflow_with_no_pending_task() -> None:
    repository = InMemoryWorkflowRepository()
    await repository.create(_workflow(status=WorkflowStatus.WAITING_FOR_USER))
    service = WorkflowResumeService(repository)

    outcome = await service.resume(workflow_instance_id="wf-1", event=_event())

    assert outcome.resumed is False
    assert outcome.reason_code == "NO_PENDING_TASK"


async def test_should_reject_an_event_that_does_not_match_the_pending_task() -> None:
    repository = InMemoryWorkflowRepository()
    await repository.create(_workflow(expected_event_type="HIL_TASK_COMPLETED"))
    service = WorkflowResumeService(repository)

    outcome = await service.resume(
        workflow_instance_id="wf-1", event=_event(event_type="APPLICATION_UPDATED")
    )

    assert outcome.resumed is False
    assert outcome.reason_code == "EVENT_TASK_MISMATCH"


async def test_should_not_resume_twice_for_the_same_workflow_state() -> None:
    """Doc 11 §142: after resuming once, the workflow is no longer in a waiting state,
    so a second delivery of the same event cannot trigger a second resume."""
    repository = InMemoryWorkflowRepository()
    await repository.create(_workflow())
    service = WorkflowResumeService(repository)

    first = await service.resume(workflow_instance_id="wf-1", event=_event())
    second = await service.resume(workflow_instance_id="wf-1", event=_event())

    assert first.resumed is True
    assert second.resumed is False
    assert second.reason_code == "WORKFLOW_NOT_WAITING"


async def test_event_handler_adapter_should_delegate_to_the_service() -> None:
    repository = InMemoryWorkflowRepository()
    await repository.create(_workflow())
    handler = WorkflowResumeEventHandler(WorkflowResumeService(repository))
    route = EventRoute(event_type="HIL_TASK_COMPLETED", handler="workflow.resume")

    outcome = await handler.handle(_event(), route=route)

    assert outcome.succeeded is True


async def test_event_handler_adapter_should_reject_an_event_with_no_workflow_instance_id() -> None:
    handler = WorkflowResumeEventHandler(WorkflowResumeService(InMemoryWorkflowRepository()))
    route = EventRoute(event_type="HIL_TASK_COMPLETED", handler="workflow.resume")

    outcome = await handler.handle(_event(workflow_instance_id=None), route=route)

    assert outcome.succeeded is False
    assert outcome.reason_code == "MISSING_WORKFLOW_INSTANCE_ID"
