from __future__ import annotations

from typing import Protocol

from pff_fa_ai.agents.context import AgentExecutionContext
from pff_fa_ai.agents.result import AgentExecutionResult


class Agent(Protocol):
    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult: ...
