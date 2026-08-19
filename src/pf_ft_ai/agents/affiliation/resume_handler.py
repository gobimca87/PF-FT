from __future__ import annotations

from pf_ft_ai.agents.affiliation.agent import AffiliationAgent
from pf_ft_ai.agents.context import AgentExecutionContext
from pf_ft_ai.agents.states import AgentRunStatus
from pf_ft_ai.common.claims import ClaimsContext
from pf_ft_ai.common.correlation import CorrelationContext, new_id
from pf_ft_ai.messaging.events.models import EventEnvelope
from pf_ft_ai.messaging.events.registry import EventRoute
from pf_ft_ai.messaging.handlers.base import HandlerOutcome
from pf_ft_ai.messaging.handlers.workflow_resume import WorkflowResumeService


def _synthetic_resume_context(
    workflow_instance_id: str, organization_id: str
) -> AgentExecutionContext:
    """`AffiliationAgent._resume()` reads `context.workflow_instance_id` to look up the
    persisted workflow and the earlier-saved `AffiliationResumeContext` (real claims,
    real conversation) — every other field here is a placeholder the resume path
    never reads, since resuming isn't triggered by a new user message."""
    return AgentExecutionContext(
        conversation_id="",
        session_id="",
        workflow_instance_id=workflow_instance_id,
        agent_run_id=new_id("run"),
        claims=ClaimsContext(subject="system.event-consumer", organization=organization_id),
        user_message="",
        correlation=CorrelationContext(
            request_id=new_id("req"),
            correlation_id=new_id("corr"),
            workflow_instance_id=workflow_instance_id,
        ),
    )


class AffiliationWorkflowResumeHandler:
    """doc 7 §134 "Affiliation Agent — Async Path": adapts `WorkflowResumeService`
    (Phase 12's generic resume validation) to also re-invoke `AffiliationAgent` once
    the workflow is confirmed resumable — the generic handler
    (`messaging.handlers.workflow_resume.WorkflowResumeEventHandler`) only transitions
    the `WorkflowInstance`; nothing else was wired to continue the agent afterward
    until this phase."""

    def __init__(self, resume_service: WorkflowResumeService, agent: AffiliationAgent) -> None:
        self._resume_service = resume_service
        self._agent = agent

    async def handle(self, event: EventEnvelope, *, route: EventRoute) -> HandlerOutcome:
        if event.workflow_instance_id is None:
            return HandlerOutcome(succeeded=False, reason_code="MISSING_WORKFLOW_INSTANCE_ID")

        outcome = await self._resume_service.resume(
            workflow_instance_id=event.workflow_instance_id, event=event
        )
        if not outcome.resumed or outcome.workflow is None:
            return HandlerOutcome(succeeded=False, reason_code=outcome.reason_code)

        context = _synthetic_resume_context(
            event.workflow_instance_id, outcome.workflow.organization_id
        )
        result = await self._agent.execute(context)
        if result.status is AgentRunStatus.FAILED:
            # `AffiliationAgent` always populates `errors` whenever it returns FAILED
            # (`_error_result()`/`_result_from_failed_state()` in `agent.py`) — no
            # fallback placeholder code is needed here.
            return HandlerOutcome(succeeded=False, reason_code=result.errors[0].code)
        return HandlerOutcome(succeeded=True)
