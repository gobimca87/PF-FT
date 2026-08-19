from pf_ft_ai.agents.affiliation.graph import build_affiliation_graph
from pf_ft_ai.agents.affiliation.steps import FAILED_STATUS, STEP_ORDER
from pf_ft_ai.orchestration.langgraph.state import GraphState
from tests.unit.agents.affiliation.support import (
    build_test_dependencies,
    enterprise_response_handler,
)


def _initial_state() -> GraphState:
    return {
        "request": {"user_message": "status please"},
        "conversation": {"conversation_id": "conv-1"},
        "session": {"session_id": "sess-1"},
        "claims": {
            "subject": "user-1",
            "organization": "club-1",
            "roles": (),
            "permissions": ("affiliation.read",),
        },
        "workflow": {"workflow_instance_id": "wf-1"},
        "intent": {},
        "entities": {},
        "context_requirements": {},
        "erc_reference": {},
        "knowledge_context": [],
        "tool_results": [],
        "pending_action": None,
        "current_node": STEP_ORDER[0],
        "execution_status": "RUNNING",
        "step_count": 0,
        "error": None,
        "trace_context": {},
    }


async def test_build_affiliation_graph_should_run_the_full_step_sequence_to_completion() -> None:
    deps = build_test_dependencies(enterprise_response_handler(application_status="COMPLETE"))
    graph = build_affiliation_graph(deps)

    final_state = await graph.ainvoke(_initial_state())

    assert final_state["execution_status"] == "COMPLETED"
    assert final_state["step_count"] == len(STEP_ORDER)


async def test_build_affiliation_graph_should_stop_at_an_unknown_step() -> None:
    deps = build_test_dependencies(enterprise_response_handler())
    graph = build_affiliation_graph(deps)
    state = _initial_state()
    state["current_node"] = "not_a_real_step"

    final_state = await graph.ainvoke(state)

    assert final_state["execution_status"] == FAILED_STATUS
    assert final_state["error"] is not None
    assert final_state["error"]["code"] == "UNKNOWN_STEP"


async def test_build_affiliation_graph_should_respect_the_max_graph_steps_limit() -> None:
    deps = build_test_dependencies(enterprise_response_handler(application_status="COMPLETE"))
    graph = build_affiliation_graph(deps, max_graph_steps=2)

    final_state = await graph.ainvoke(_initial_state())

    # The full sequence needs len(STEP_ORDER) steps to reach COMPLETED; capped at 2
    # steps it must stop via the step-limit path instead.
    assert final_state["execution_status"] == "STEP_LIMIT_EXCEEDED"
    assert final_state["step_count"] == 2
