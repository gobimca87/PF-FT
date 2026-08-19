from datetime import UTC, datetime

from pf_ft_ai.agents.affiliation.agent import AffiliationAgent
from pf_ft_ai.agents.affiliation.resume_handler import AffiliationWorkflowResumeHandler
from pf_ft_ai.common.correlation import new_id
from pf_ft_ai.infrastructure.persistence import InMemoryWorkflowRepository
from pf_ft_ai.messaging.events.models import EventEnvelope
from pf_ft_ai.messaging.events.registry import EventRoute
from pf_ft_ai.messaging.handlers.workflow_resume import WorkflowResumeService
from tests.unit.agents.affiliation.support import (
    build_test_dependencies,
    enterprise_response_handler,
)

_ROUTE = EventRoute(event_type="affiliation.application.status_changed", handler="workflow.resume")


def _event(**overrides: object) -> EventEnvelope:
    defaults: dict[str, object] = {
        "event_id": new_id("evt"),
        "event_type": "affiliation.application.status_changed",
        "event_version": "1.0",
        "source": "enterprise",
        "subject": "app-1",
        "occurred_at": datetime.now(UTC),
        "published_at": datetime.now(UTC),
        "correlation_id": new_id("corr"),
        "tenant_id": "pff",
        "organization_id": "club-1",
        "workflow_instance_id": "wf-1",
    }
    defaults.update(overrides)
    return EventEnvelope.model_validate(defaults)


async def test_should_reject_an_event_with_no_workflow_instance_id() -> None:
    workflow_repository = InMemoryWorkflowRepository()
    deps = build_test_dependencies(
        enterprise_response_handler(), workflow_repository=workflow_repository
    )
    agent = AffiliationAgent(deps)
    handler = AffiliationWorkflowResumeHandler(WorkflowResumeService(workflow_repository), agent)

    outcome = await handler.handle(_event(workflow_instance_id=None), route=_ROUTE)

    assert outcome.succeeded is False
    assert outcome.reason_code == "MISSING_WORKFLOW_INSTANCE_ID"


async def test_should_reject_an_event_for_an_unknown_workflow() -> None:
    workflow_repository = InMemoryWorkflowRepository()
    deps = build_test_dependencies(
        enterprise_response_handler(), workflow_repository=workflow_repository
    )
    agent = AffiliationAgent(deps)
    handler = AffiliationWorkflowResumeHandler(WorkflowResumeService(workflow_repository), agent)

    outcome = await handler.handle(_event(workflow_instance_id="does-not-exist"), route=_ROUTE)

    assert outcome.succeeded is False
    assert outcome.reason_code == "WORKFLOW_NOT_FOUND"
