from __future__ import annotations

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.orchestration.langgraph.nodes import NodeRegistry
from pf_ft_ai.orchestration.langgraph.state import GraphState

COMPLETED_STATUS = "COMPLETED"
STEP_LIMIT_EXCEEDED_STATUS = "STEP_LIMIT_EXCEEDED"
_LIMIT_NODE_ID = "_limit_exceeded"


def build_skeleton_graph(
    registry: NodeRegistry,
    *,
    entry_node: str,
    max_graph_steps: int,
    terminal_statuses: frozenset[str] | None = None,
) -> CompiledStateGraph:
    """`terminal_statuses` lets a caller stop the loop on outcomes other than plain
    completion (e.g. `AffiliationAgent`'s graph also stops on a `WAITING_FOR_*` status
    — doc 7 §134-135's async/HIL paths end the graph run there, not at COMPLETED).
    Defaults to `{COMPLETED_STATUS}` for backward compatibility."""
    node = registry.get(entry_node)
    if node is None:
        raise ConfigurationError(f"Entry node not registered: {entry_node}")
    stop_statuses = terminal_statuses or frozenset({COMPLETED_STATUS})

    builder = StateGraph(GraphState)

    async def run_step(state: GraphState) -> GraphState:
        result = await node.handler(state)
        result["step_count"] = state["step_count"] + 1
        return result

    def should_continue(state: GraphState) -> str:
        if state["execution_status"] in stop_statuses:
            return "end"
        if state["step_count"] >= max_graph_steps:
            return "limit_exceeded"
        return "continue"

    async def mark_limit_exceeded(state: GraphState) -> GraphState:
        return {**state, "execution_status": STEP_LIMIT_EXCEEDED_STATUS}

    builder.add_node(entry_node, run_step)
    builder.add_node(_LIMIT_NODE_ID, mark_limit_exceeded)
    builder.set_entry_point(entry_node)
    builder.add_conditional_edges(
        entry_node,
        should_continue,
        {"continue": entry_node, "limit_exceeded": _LIMIT_NODE_ID, "end": END},
    )
    builder.add_edge(_LIMIT_NODE_ID, END)

    return builder.compile()
