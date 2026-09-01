from datetime import UTC, datetime

from pff_fa_ai.agents.context import AgentExecutionContext
from pff_fa_ai.agents.result import AgentExecutionResult
from pff_fa_ai.agents.states import AgentRunStatus
from pff_fa_ai.application.workflows.orchestrator import OrchestrationRequest
from pff_fa_ai.application.workflows.states import OrchestrationStatus
from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.common.correlation import CorrelationContext
from pff_fa_ai.configuration.models import HarnessLimits
from pff_fa_ai.domain.conversation.entities import Conversation
from pff_fa_ai.domain.conversation.states import ConversationStatus
from pff_fa_ai.orchestration.harness.harness import AgentHarness
from pff_fa_ai.orchestration.supervisor.models import AgentCapability, IntentClassification
from pff_fa_ai.orchestration.supervisor.registry import AgentRegistry
from pff_fa_ai.orchestration.supervisor.service import Supervisor
from pff_fa_ai.orchestration.workflow_orchestrator import (
    CLARIFICATION_MESSAGE,
    NO_CAPABILITY_MESSAGE,
    SupervisorWorkflowOrchestrator,
)

CLAIMS = ClaimsContext(subject="user-1", organization="club-1")
LIMITS = HarnessLimits(
    max_graph_steps=10,
    max_agent_loops=5,
    max_tool_calls=5,
    max_parallel_calls=2,
    max_context_tokens=1000,
    max_output_tokens=200,
    max_execution_time_seconds=5,
    max_retry_count=1,
    max_batch_size=20,
)


class _FixedClassifier:
    def __init__(self, intent: str, confidence: float) -> None:
        self._intent = intent
        self._confidence = confidence

    async def classify(self, message: str) -> IntentClassification:
        return IntentClassification(intent=self._intent, confidence=self._confidence)


class _EchoAgent:
    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        return AgentExecutionResult(
            status=AgentRunStatus.COMPLETED, response=f"handled: {context.user_message}"
        )


def _capability() -> AgentCapability:
    return AgentCapability(
        agent_id="affiliation_agent",
        agent_version="1.0.0",
        workflow="affiliation",
        supported_intents=("club_affiliation",),
    )


def _request(message: str = "help with affiliation") -> OrchestrationRequest:
    now = datetime.now(UTC)
    return OrchestrationRequest(
        conversation=Conversation(
            conversation_id="conv-1",
            user_reference="user-1",
            session_id="sess-1",
            status=ConversationStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        ),
        user_message=message,
        claims=CLAIMS,
        correlation=CorrelationContext(
            request_id="req-1",
            correlation_id="corr-1",
            conversation_id="conv-1",
            session_id="sess-1",
        ),
    )


async def test_should_report_no_capability_when_registry_is_empty() -> None:
    orchestrator = SupervisorWorkflowOrchestrator(
        Supervisor(AgentRegistry(), _FixedClassifier("club_affiliation", 0.95)),
        AgentHarness(LIMITS),
        AgentRegistry(),
    )

    result = await orchestrator.handle_message(_request())

    assert result.status is OrchestrationStatus.FAILED
    assert result.response_message == NO_CAPABILITY_MESSAGE


async def test_should_request_clarification_when_confidence_is_low() -> None:
    registry = AgentRegistry()
    registry.register(_capability())
    orchestrator = SupervisorWorkflowOrchestrator(
        Supervisor(registry, _FixedClassifier("club_affiliation", 0.2)),
        AgentHarness(LIMITS),
        registry,
    )

    result = await orchestrator.handle_message(_request())

    assert result.status is OrchestrationStatus.NEEDS_CLARIFICATION
    assert result.response_message == CLARIFICATION_MESSAGE


async def test_should_fail_when_routed_agent_has_no_executor() -> None:
    registry = AgentRegistry()
    registry.register(_capability())  # no executor wired
    orchestrator = SupervisorWorkflowOrchestrator(
        Supervisor(registry, _FixedClassifier("club_affiliation", 0.95)),
        AgentHarness(LIMITS),
        registry,
    )

    result = await orchestrator.handle_message(_request())

    assert result.status is OrchestrationStatus.FAILED
    assert "no executor wired yet" in result.response_message


async def test_should_execute_the_registered_agent_and_map_completed_status() -> None:
    registry = AgentRegistry()
    registry.register(_capability(), executor=_EchoAgent())
    orchestrator = SupervisorWorkflowOrchestrator(
        Supervisor(registry, _FixedClassifier("club_affiliation", 0.95)),
        AgentHarness(LIMITS),
        registry,
    )

    result = await orchestrator.handle_message(_request("help with affiliation"))

    assert result.status is OrchestrationStatus.COMPLETED
    assert result.response_message == "handled: help with affiliation"
    assert result.workflow_instance_id is not None
