from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from pff_fa_ai.domain.workflow.entities import WorkflowInstance
from pff_fa_ai.domain.workflow.repository import WorkflowRepository
from pff_fa_ai.domain.workflow.states import WorkflowStatus
from pff_fa_ai.messaging.events.models import EventEnvelope
from pff_fa_ai.messaging.events.registry import EventRoute
from pff_fa_ai.messaging.handlers.base import HandlerOutcome

# doc 11 §55-56: only a workflow actually waiting for something may resume.
_RESUMABLE_STATUSES = frozenset(
    {
        WorkflowStatus.WAITING_FOR_USER,
        WorkflowStatus.WAITING_FOR_HUMAN,
        WorkflowStatus.WAITING_FOR_EXTERNAL_EVENT,
    }
)


class WorkflowResumeOutcome(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    resumed: bool
    reason_code: str | None = None
    workflow: WorkflowInstance | None = None


class WorkflowResumeService:
    """doc 11 §55-57/§70: never resumes solely because an event of the right type
    arrived. Duplicate-delivery protection is the caller's job (the idempotency claim
    happens once per event, upstream of routing) — this validates workflow state and
    event correlation, doc 11 §56's other five checks.
    """

    def __init__(self, repository: WorkflowRepository) -> None:
        self._repository = repository

    async def resume(
        self, *, workflow_instance_id: str, event: EventEnvelope
    ) -> WorkflowResumeOutcome:
        workflow = await self._repository.get(workflow_instance_id)
        if workflow is None:
            return WorkflowResumeOutcome(resumed=False, reason_code="WORKFLOW_NOT_FOUND")

        if event.organization_id is not None and workflow.organization_id != event.organization_id:
            return WorkflowResumeOutcome(resumed=False, reason_code="ORGANIZATION_MISMATCH")

        if workflow.status not in _RESUMABLE_STATUSES:
            return WorkflowResumeOutcome(resumed=False, reason_code="WORKFLOW_NOT_WAITING")

        waiting = workflow.waiting
        if waiting is None:
            return WorkflowResumeOutcome(resumed=False, reason_code="NO_PENDING_TASK")

        expected_event_type = waiting.expected_event_type
        if expected_event_type is not None and expected_event_type != event.event_type:
            return WorkflowResumeOutcome(resumed=False, reason_code="EVENT_TASK_MISMATCH")

        resumed_workflow = await self._repository.transition(
            workflow_instance_id,
            status=WorkflowStatus.RESUMING,
            current_state=waiting.resume_node,
            expected_version=workflow.version,
        )
        return WorkflowResumeOutcome(resumed=True, workflow=resumed_workflow)


class WorkflowResumeEventHandler:
    """Adapts `WorkflowResumeService` to the generic `EventHandler` protocol (doc 11
    §68) so `EventProcessingService` can dispatch to it by route without knowing about
    workflow-specific concerns."""

    def __init__(self, service: WorkflowResumeService) -> None:
        self._service = service

    async def handle(self, event: EventEnvelope, *, route: EventRoute) -> HandlerOutcome:
        if event.workflow_instance_id is None:
            return HandlerOutcome(succeeded=False, reason_code="MISSING_WORKFLOW_INSTANCE_ID")
        outcome = await self._service.resume(
            workflow_instance_id=event.workflow_instance_id, event=event
        )
        return HandlerOutcome(succeeded=outcome.resumed, reason_code=outcome.reason_code)
