from pf_ft_ai.engineering_agents.models import EngineeringAgentDefinition, EngineeringAgentResult
from pf_ft_ai.engineering_agents.registry import EngineeringAgentRegistry
from pf_ft_ai.engineering_agents.states import (
    AgentLifecycleStatus,
    AgentResultStatus,
    ChangedComponent,
    EngineeringAgentRisk,
    ExecutionMode,
    PermissionLevel,
)
from pf_ft_ai.engineering_agents.supervisor import (
    EngineeringAgentSupervisor,
    select_agents_for_changes,
)


def _definition(agent_id: str, status: AgentLifecycleStatus) -> EngineeringAgentDefinition:
    return EngineeringAgentDefinition(
        agent_id=agent_id,
        version="1.0.0",
        purpose="test",
        owner="platform-engineering",
        risk=EngineeringAgentRisk.LOW,
        permission_level=PermissionLevel.LEVEL_1_REPORT,
        execution_mode=ExecutionMode.VALIDATE,
        lifecycle_status=status,
    )


def test_select_agents_for_changes_should_follow_the_documented_prompt_example() -> None:
    """doc 23 §9 worked example."""
    selected = select_agents_for_changes([ChangedComponent.PROMPTS])

    assert selected == ("prompt-review", "ai-evaluation", "regression", "guardrail-validation")


def test_select_agents_for_changes_should_follow_the_documented_rag_example() -> None:
    selected = select_agents_for_changes([ChangedComponent.RAG])

    assert selected == (
        "rag-validation",
        "embedding-vector-validation",
        "ai-evaluation",
        "regression",
    )


def test_select_agents_for_changes_should_follow_the_documented_tool_example() -> None:
    selected = select_agents_for_changes([ChangedComponent.TOOLS])

    assert selected == ("api-contract", "security-scan", "unit-test", "ai-evaluation")


def test_select_agents_for_changes_should_deduplicate_across_multiple_components() -> None:
    selected = select_agents_for_changes([ChangedComponent.PROMPTS, ChangedComponent.RAG])

    assert selected.count("ai-evaluation") == 1
    assert selected.count("regression") == 1


def test_select_agents_for_changes_should_use_the_baseline_for_unmapped_components() -> None:
    selected = select_agents_for_changes([ChangedComponent.MCP])

    assert "security-scan" in selected
    assert "unit-test" in selected


async def test_supervisor_should_only_select_active_agents_from_the_registry() -> None:
    registry = EngineeringAgentRegistry()
    registry.register(_definition("security-scan", AgentLifecycleStatus.ACTIVE))
    registry.register(_definition("unit-test", AgentLifecycleStatus.PROPOSED))
    supervisor = EngineeringAgentSupervisor(registry)

    selected = supervisor.select_agents([ChangedComponent.TOOLS])

    assert selected == ("security-scan",)


async def test_supervisor_run_should_execute_selected_agents_and_collect_results() -> None:
    registry = EngineeringAgentRegistry()
    registry.register(_definition("security-scan", AgentLifecycleStatus.ACTIVE))
    supervisor = EngineeringAgentSupervisor(registry)

    async def fake_security_scan() -> EngineeringAgentResult:
        return EngineeringAgentResult(
            agent_id="security-scan", agent_version="1.0.0", status=AgentResultStatus.PASS
        )

    run = await supervisor.run(
        repository="pf-ft-ai",
        commit="abc123",
        changed_components=[ChangedComponent.TOOLS],
        agent_runners={"security-scan": fake_security_scan},
    )

    assert run.repository == "pf-ft-ai"
    assert run.agent_ids == ("security-scan",)
    assert len(run.results) == 1
    assert run.results[0].status is AgentResultStatus.PASS


async def test_supervisor_run_should_mark_a_selected_agent_without_a_runner_as_skipped() -> None:
    registry = EngineeringAgentRegistry()
    registry.register(_definition("security-scan", AgentLifecycleStatus.ACTIVE))
    supervisor = EngineeringAgentSupervisor(registry)

    run = await supervisor.run(
        repository="pf-ft-ai",
        commit="abc123",
        changed_components=[ChangedComponent.TOOLS],
        agent_runners={},
    )

    assert run.results[0].status is AgentResultStatus.SKIPPED
