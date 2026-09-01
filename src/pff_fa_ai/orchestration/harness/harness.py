from __future__ import annotations

import asyncio

from pff_fa_ai.agents.context import AgentExecutionContext
from pff_fa_ai.agents.contract import Agent
from pff_fa_ai.agents.result import AgentExecutionResult
from pff_fa_ai.common.exceptions import IntegrationError, WorkflowError
from pff_fa_ai.configuration.models import HarnessLimits


class AgentHarness:
    """Controlled execution boundary every agent runs inside (doc 7 §8, §50, §171)."""

    def __init__(self, limits: HarnessLimits) -> None:
        self._limits = limits

    async def execute(self, agent: Agent, context: AgentExecutionContext) -> AgentExecutionResult:
        if not context.claims.subject:
            raise WorkflowError("Agent execution requires a validated claims subject")

        attempt = 0
        while True:
            attempt += 1
            try:
                return await asyncio.wait_for(
                    agent.execute(context), timeout=self._limits.max_execution_time_seconds
                )
            except TimeoutError as exc:
                raise WorkflowError(
                    "Agent execution exceeded max_execution_time_seconds="
                    f"{self._limits.max_execution_time_seconds}"
                ) from exc
            except IntegrationError:
                if attempt > self._limits.max_retry_count:
                    raise
