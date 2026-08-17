from __future__ import annotations

from pf_ft_ai.agents.contract import Agent
from pf_ft_ai.orchestration.supervisor.models import AgentCapability


class AgentRegistry:
    def __init__(self) -> None:
        self._capabilities: dict[str, AgentCapability] = {}
        self._executors: dict[str, Agent] = {}

    def register(self, capability: AgentCapability, *, executor: Agent | None = None) -> None:
        self._capabilities[capability.agent_id] = capability
        if executor is not None:
            self._executors[capability.agent_id] = executor

    def find_by_intent(self, intent: str) -> list[AgentCapability]:
        return [
            capability
            for capability in self._capabilities.values()
            if capability.enabled and intent in capability.supported_intents
        ]

    def get_capability(self, agent_id: str) -> AgentCapability | None:
        return self._capabilities.get(agent_id)

    def get_executor(self, agent_id: str) -> Agent | None:
        return self._executors.get(agent_id)
