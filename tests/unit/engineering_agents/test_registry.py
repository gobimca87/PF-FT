import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.engineering_agents.models import EngineeringAgentDefinition
from pf_ft_ai.engineering_agents.registry import EngineeringAgentRegistry, build_default_registry
from pf_ft_ai.engineering_agents.states import (
    AgentLifecycleStatus,
    EngineeringAgentRisk,
    ExecutionMode,
    PermissionLevel,
)


def _definition(
    agent_id: str = "security-scan",
    lifecycle_status: AgentLifecycleStatus = AgentLifecycleStatus.ACTIVE,
) -> EngineeringAgentDefinition:
    return EngineeringAgentDefinition(
        agent_id=agent_id,
        version="1.0.0",
        purpose="test agent",
        owner="platform-engineering",
        risk=EngineeringAgentRisk.LOW,
        permission_level=PermissionLevel.LEVEL_1_REPORT,
        execution_mode=ExecutionMode.VALIDATE,
        lifecycle_status=lifecycle_status,
    )


def test_should_register_and_fetch_a_definition() -> None:
    registry = EngineeringAgentRegistry()
    registry.register(_definition())

    fetched = registry.get("security-scan")

    assert fetched is not None
    assert fetched.owner == "platform-engineering"


def test_should_return_none_for_an_unregistered_agent() -> None:
    registry = EngineeringAgentRegistry()

    assert registry.get("does-not-exist") is None


def test_should_reject_a_duplicate_agent_id() -> None:
    registry = EngineeringAgentRegistry()
    registry.register(_definition())

    with pytest.raises(ConfigurationError, match="Duplicate engineering agent"):
        registry.register(_definition())


def test_active_should_only_return_active_agents() -> None:
    registry = EngineeringAgentRegistry()
    registry.register(_definition("security-scan", AgentLifecycleStatus.ACTIVE))
    registry.register(_definition("code-review", AgentLifecycleStatus.PROPOSED))

    active_ids = {definition.agent_id for definition in registry.active()}

    assert active_ids == {"security-scan"}


def test_build_default_registry_should_mark_the_five_real_agents_active() -> None:
    registry = build_default_registry()

    active_ids = {definition.agent_id for definition in registry.active()}

    assert active_ids == {
        "configuration",
        "architecture-compliance",
        "security-scan",
        "dependency",
        "unit-test",
    }


def test_build_default_registry_should_mark_llm_dependent_agents_proposed() -> None:
    registry = build_default_registry()

    code_review = registry.get("code-review")

    assert code_review is not None
    assert code_review.lifecycle_status is AgentLifecycleStatus.PROPOSED
    assert code_review.model_id is None


def test_build_default_registry_should_have_no_duplicate_agent_ids() -> None:
    registry = build_default_registry()

    agent_ids = [definition.agent_id for definition in registry.all_definitions()]

    assert len(agent_ids) == len(set(agent_ids))
