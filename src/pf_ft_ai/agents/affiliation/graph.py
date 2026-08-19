from __future__ import annotations

from langgraph.graph.state import CompiledStateGraph

from pf_ft_ai.agents.affiliation.dependencies import AffiliationDependencies
from pf_ft_ai.agents.affiliation.steps import FAILED_STATUS, STEP_HANDLERS, WAITING_FOR_EVENT_STATUS
from pf_ft_ai.orchestration.langgraph.graph_builder import COMPLETED_STATUS, build_skeleton_graph
from pf_ft_ai.orchestration.langgraph.nodes import NodeKind, NodeRegistry
from pf_ft_ai.orchestration.langgraph.state import GraphState

ENTRY_NODE = "affiliation_agent"

# doc 7 §133-135: the reference graph's every step is deterministic tool-calling/
# ERC-building except the RAG-need decision, which is itself deterministic here too
# (Phase 8's corpus is empty) — no AI-assisted node exists yet in this reference
# implementation.
_TERMINAL_STATUSES = frozenset({COMPLETED_STATUS, WAITING_FOR_EVENT_STATUS, FAILED_STATUS})


def build_affiliation_graph(
    deps: AffiliationDependencies, *, max_graph_steps: int = 20
) -> CompiledStateGraph:
    """doc 7 §133 "Affiliation Agent — Reference Graph": one reentrant LangGraph node
    (`build_skeleton_graph`'s existing Phase 4 pattern) dispatching to the named steps
    in `steps.STEP_HANDLERS` by `state["current_node"]` — reusing the generic skeleton
    rather than hand-rolling a second multi-node `StateGraph` wiring mechanism next to
    it. Parallel branches in the diagram (TEAMS/OFFICIALS batches) are real
    `asyncio.gather` concurrency inside `steps.collect_entity_context`, not separate
    LangGraph nodes — see that function's docstring for why."""

    async def dispatch(state: GraphState) -> GraphState:
        handler = STEP_HANDLERS.get(state["current_node"])
        if handler is None:
            return {
                **state,
                "execution_status": FAILED_STATUS,
                "error": {"code": "UNKNOWN_STEP", "message": state["current_node"]},
            }
        return await handler(state, deps)

    registry = NodeRegistry()
    registry.register(ENTRY_NODE, dispatch, kind=NodeKind.DETERMINISTIC)
    return build_skeleton_graph(
        registry,
        entry_node=ENTRY_NODE,
        max_graph_steps=max_graph_steps,
        terminal_statuses=_TERMINAL_STATUSES,
    )
