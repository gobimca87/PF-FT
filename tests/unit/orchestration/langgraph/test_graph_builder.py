import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.orchestration.langgraph.graph_builder import (
    COMPLETED_STATUS,
    STEP_LIMIT_EXCEEDED_STATUS,
    build_skeleton_graph,
)
from pf_ft_ai.orchestration.langgraph.nodes import NodeRegistry
from pf_ft_ai.orchestration.langgraph.state import GraphState


def _initial_state() -> GraphState:
    return {
        "request": {},
        "conversation": {},
        "session": {},
        "claims": {},
        "workflow": {},
        "intent": {},
        "entities": {},
        "context_requirements": {},
        "erc_reference": {},
        "knowledge_context": [],
        "tool_results": [],
        "pending_action": None,
        "current_node": "reason",
        "execution_status": "RUNNING",
        "step_count": 0,
        "error": None,
        "trace_context": {},
    }


def test_should_raise_when_entry_node_is_not_registered() -> None:
    with pytest.raises(ConfigurationError, match="Entry node not registered"):
        build_skeleton_graph(NodeRegistry(), entry_node="reason", max_graph_steps=5)


async def test_should_terminate_normally_when_node_marks_completed() -> None:
    async def complete_after_two_steps(state: GraphState) -> GraphState:
        if state["step_count"] >= 2:
            return {**state, "execution_status": COMPLETED_STATUS}
        return state

    registry = NodeRegistry()
    registry.register("reason", complete_after_two_steps)
    graph = build_skeleton_graph(registry, entry_node="reason", max_graph_steps=10)

    result = await graph.ainvoke(_initial_state())

    assert result["execution_status"] == COMPLETED_STATUS
    assert result["step_count"] == 3


async def test_should_terminate_on_a_custom_terminal_status() -> None:
    async def waits_after_one_step(state: GraphState) -> GraphState:
        if state["step_count"] >= 1:
            return {**state, "execution_status": "WAITING_FOR_EVENT"}
        return state

    registry = NodeRegistry()
    registry.register("reason", waits_after_one_step)
    graph = build_skeleton_graph(
        registry,
        entry_node="reason",
        max_graph_steps=10,
        terminal_statuses=frozenset({COMPLETED_STATUS, "WAITING_FOR_EVENT"}),
    )

    result = await graph.ainvoke(_initial_state())

    assert result["execution_status"] == "WAITING_FOR_EVENT"
    assert result["step_count"] == 2


async def test_should_terminate_via_step_limit_when_node_never_completes() -> None:
    async def never_completes(state: GraphState) -> GraphState:
        return state

    registry = NodeRegistry()
    registry.register("reason", never_completes)
    graph = build_skeleton_graph(registry, entry_node="reason", max_graph_steps=5)

    result = await graph.ainvoke(_initial_state())

    assert result["execution_status"] == STEP_LIMIT_EXCEEDED_STATUS
    assert result["step_count"] == 5
