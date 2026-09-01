from pff_fa_ai.agents.context import AgentExecutionContext
from pff_fa_ai.agents.result import AgentExecutionResult
from pff_fa_ai.agents.states import AgentRunStatus
from pff_fa_ai.orchestration.supervisor.models import AgentCapability
from pff_fa_ai.orchestration.supervisor.registry import AgentRegistry


class _StubAgent:
    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        return AgentExecutionResult(status=AgentRunStatus.COMPLETED, response="ok")


def _capability(agent_id: str = "affiliation_agent", *, enabled: bool = True) -> AgentCapability:
    return AgentCapability(
        agent_id=agent_id,
        agent_version="1.0.0",
        workflow="affiliation",
        supported_intents=("club_affiliation", "affiliation_status"),
        enabled=enabled,
    )


def test_should_find_capability_by_supported_intent() -> None:
    registry = AgentRegistry()
    registry.register(_capability())

    matches = registry.find_by_intent("club_affiliation")

    assert [capability.agent_id for capability in matches] == ["affiliation_agent"]


def test_should_not_find_capability_for_unsupported_intent() -> None:
    registry = AgentRegistry()
    registry.register(_capability())

    assert registry.find_by_intent("official_courses") == []


def test_should_exclude_disabled_capabilities_from_routing() -> None:
    registry = AgentRegistry()
    registry.register(_capability(enabled=False))

    assert registry.find_by_intent("club_affiliation") == []


def test_should_return_registered_executor() -> None:
    registry = AgentRegistry()
    executor = _StubAgent()
    registry.register(_capability(), executor=executor)

    assert registry.get_executor("affiliation_agent") is executor


def test_should_return_none_for_unregistered_executor() -> None:
    registry = AgentRegistry()
    registry.register(_capability())

    assert registry.get_executor("affiliation_agent") is None


def test_should_return_none_for_unknown_agent_id() -> None:
    registry = AgentRegistry()

    assert registry.get_capability("missing") is None
    assert registry.get_executor("missing") is None
