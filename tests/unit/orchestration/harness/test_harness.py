import asyncio

import pytest

from pff_fa_ai.agents.context import AgentExecutionContext
from pff_fa_ai.agents.result import AgentExecutionResult
from pff_fa_ai.agents.states import AgentRunStatus
from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.common.correlation import CorrelationContext
from pff_fa_ai.common.exceptions import IntegrationError, WorkflowError
from pff_fa_ai.configuration.models import HarnessLimits
from pff_fa_ai.orchestration.harness.harness import AgentHarness

LIMITS = HarnessLimits(
    max_graph_steps=10,
    max_agent_loops=5,
    max_tool_calls=5,
    max_parallel_calls=2,
    max_context_tokens=1000,
    max_output_tokens=200,
    max_execution_time_seconds=1,
    max_retry_count=2,
    max_batch_size=20,
)


def _context(subject: str = "user-1") -> AgentExecutionContext:
    return AgentExecutionContext(
        conversation_id="conv-1",
        session_id="sess-1",
        workflow_instance_id="wf-1",
        agent_run_id="run-1",
        claims=ClaimsContext(subject=subject, organization="club-1"),
        user_message="hello",
        correlation=CorrelationContext(request_id="req-1", correlation_id="corr-1"),
    )


class _SucceedingAgent:
    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        return AgentExecutionResult(status=AgentRunStatus.COMPLETED, response="ok")


class _SlowAgent:
    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        await asyncio.sleep(10)
        return AgentExecutionResult(status=AgentRunStatus.COMPLETED)


class _FlakyAgent:
    def __init__(self, *, fail_times: int) -> None:
        self._fail_times = fail_times
        self.attempts = 0

    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        self.attempts += 1
        if self.attempts <= self._fail_times:
            raise IntegrationError("transient enterprise API failure")
        return AgentExecutionResult(status=AgentRunStatus.COMPLETED, response="recovered")


async def test_should_execute_a_successful_agent() -> None:
    harness = AgentHarness(LIMITS)

    result = await harness.execute(_SucceedingAgent(), _context())

    assert result.status is AgentRunStatus.COMPLETED
    assert result.response == "ok"


async def test_should_reject_execution_without_a_claims_subject() -> None:
    harness = AgentHarness(LIMITS)

    with pytest.raises(WorkflowError, match="claims subject"):
        await harness.execute(_SucceedingAgent(), _context(subject=""))


async def test_should_raise_when_agent_exceeds_max_execution_time() -> None:
    harness = AgentHarness(LIMITS)

    with pytest.raises(WorkflowError, match="max_execution_time_seconds"):
        await harness.execute(_SlowAgent(), _context())


async def test_should_retry_transient_integration_errors_within_budget() -> None:
    harness = AgentHarness(LIMITS)
    agent = _FlakyAgent(fail_times=2)

    result = await harness.execute(agent, _context())

    assert result.response == "recovered"
    assert agent.attempts == 3


async def test_should_give_up_after_exhausting_the_retry_budget() -> None:
    harness = AgentHarness(LIMITS)
    agent = _FlakyAgent(fail_times=10)

    with pytest.raises(IntegrationError):
        await harness.execute(agent, _context())

    assert agent.attempts == LIMITS.max_retry_count + 1
