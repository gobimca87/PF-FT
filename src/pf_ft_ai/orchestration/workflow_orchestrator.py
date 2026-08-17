from __future__ import annotations

from pf_ft_ai.agents.context import AgentExecutionContext
from pf_ft_ai.agents.states import AgentRunStatus
from pf_ft_ai.application.workflows.orchestrator import OrchestrationRequest, OrchestrationResult
from pf_ft_ai.application.workflows.states import OrchestrationStatus
from pf_ft_ai.common.correlation import new_id
from pf_ft_ai.orchestration.harness import AgentHarness
from pf_ft_ai.orchestration.supervisor import AgentRegistry, Supervisor, SupervisorStatus

NO_CAPABILITY_MESSAGE = "I don't have a capability registered for that request yet."
CLARIFICATION_MESSAGE = "Could you tell me a bit more about what you'd like help with?"

_AGENT_STATUS_TO_ORCHESTRATION_STATUS: dict[AgentRunStatus, OrchestrationStatus] = {
    AgentRunStatus.CREATED: OrchestrationStatus.IN_PROGRESS,
    AgentRunStatus.INITIALIZING: OrchestrationStatus.IN_PROGRESS,
    AgentRunStatus.EXECUTING: OrchestrationStatus.IN_PROGRESS,
    AgentRunStatus.WAITING_FOR_TOOL: OrchestrationStatus.IN_PROGRESS,
    AgentRunStatus.WAITING_FOR_RAG: OrchestrationStatus.IN_PROGRESS,
    AgentRunStatus.WAITING_FOR_SLM: OrchestrationStatus.IN_PROGRESS,
    AgentRunStatus.WAITING_FOR_USER: OrchestrationStatus.WAITING_FOR_USER,
    AgentRunStatus.WAITING_FOR_HUMAN: OrchestrationStatus.WAITING_FOR_HUMAN,
    AgentRunStatus.WAITING_FOR_EVENT: OrchestrationStatus.WAITING_FOR_EXTERNAL_EVENT,
    AgentRunStatus.COMPLETED: OrchestrationStatus.COMPLETED,
    AgentRunStatus.PARTIAL: OrchestrationStatus.IN_PROGRESS,
    AgentRunStatus.FAILED: OrchestrationStatus.FAILED,
    AgentRunStatus.CANCELLED: OrchestrationStatus.FAILED,
}


class SupervisorWorkflowOrchestrator:
    def __init__(
        self, supervisor: Supervisor, harness: AgentHarness, registry: AgentRegistry
    ) -> None:
        self._supervisor = supervisor
        self._harness = harness
        self._registry = registry

    async def handle_message(self, request: OrchestrationRequest) -> OrchestrationResult:
        decision = await self._supervisor.route(
            user_message=request.user_message, claims=request.claims
        )

        if decision.status is SupervisorStatus.CLARIFICATION_REQUIRED:
            return OrchestrationResult(
                status=OrchestrationStatus.NEEDS_CLARIFICATION,
                response_message=CLARIFICATION_MESSAGE,
            )

        if decision.status is not SupervisorStatus.ROUTED or decision.agent_id is None:
            return OrchestrationResult(
                status=OrchestrationStatus.FAILED, response_message=NO_CAPABILITY_MESSAGE
            )

        executor = self._registry.get_executor(decision.agent_id)
        if executor is None:
            return OrchestrationResult(
                status=OrchestrationStatus.FAILED,
                response_message=(
                    f"Agent '{decision.agent_id}' is registered but has no executor wired yet."
                ),
            )

        workflow_instance_id = request.correlation.workflow_instance_id or new_id("wf")
        context = AgentExecutionContext(
            conversation_id=request.conversation.conversation_id,
            session_id=request.correlation.session_id or request.conversation.session_id,
            workflow_instance_id=workflow_instance_id,
            agent_run_id=new_id("run"),
            claims=request.claims,
            user_message=request.user_message,
            correlation=request.correlation,
        )

        result = await self._harness.execute(executor, context)
        return OrchestrationResult(
            status=_AGENT_STATUS_TO_ORCHESTRATION_STATUS.get(
                result.status, OrchestrationStatus.FAILED
            ),
            response_message=result.response or "",
            workflow_instance_id=workflow_instance_id,
        )
