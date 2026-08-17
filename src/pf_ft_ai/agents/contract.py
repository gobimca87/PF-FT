from __future__ import annotations

from typing import Protocol

from pf_ft_ai.agents.context import AgentExecutionContext
from pf_ft_ai.agents.result import AgentExecutionResult


class Agent(Protocol):
    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult: ...
