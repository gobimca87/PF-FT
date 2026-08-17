from pf_ft_ai.agents.context import AgentExecutionContext
from pf_ft_ai.agents.result import AgentError, AgentExecutionResult
from pf_ft_ai.agents.states import AgentRunStatus
from pf_ft_ai.common.claims import ClaimsContext
from pf_ft_ai.common.correlation import CorrelationContext
from pf_ft_ai.common.error_category import ErrorCategory


def test_should_build_an_agent_execution_context() -> None:
    context = AgentExecutionContext(
        conversation_id="conv-1",
        session_id="sess-1",
        workflow_instance_id="wf-1",
        agent_run_id="run-1",
        claims=ClaimsContext(subject="user-1", organization="club-1"),
        user_message="hello",
        correlation=CorrelationContext(request_id="req-1", correlation_id="corr-1"),
    )

    assert context.conversation_id == "conv-1"
    assert context.claims.subject == "user-1"


def test_should_default_result_fields() -> None:
    result = AgentExecutionResult(status=AgentRunStatus.COMPLETED)

    assert result.response is None
    assert result.errors == []


def test_should_carry_agent_errors() -> None:
    result = AgentExecutionResult(
        status=AgentRunStatus.FAILED,
        errors=[
            AgentError(
                category=ErrorCategory.DEPENDENCY,
                code="ENTERPRISE_API_TIMEOUT",
                message_safe="The information is temporarily unavailable.",
                retryable=True,
            )
        ],
    )

    assert result.errors[0].category is ErrorCategory.DEPENDENCY
    assert result.errors[0].retryable is True
