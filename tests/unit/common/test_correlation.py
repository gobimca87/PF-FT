from pf_ft_ai.common.correlation import CorrelationContext, new_id


def test_should_generate_a_prefixed_unique_id() -> None:
    first = new_id("req")
    second = new_id("req")

    assert first.startswith("req-")
    assert first != second


def test_should_default_optional_correlation_fields_to_none() -> None:
    context = CorrelationContext(request_id="req-1", correlation_id="corr-1")

    assert context.conversation_id is None
    assert context.session_id is None
    assert context.workflow_instance_id is None
    assert context.langgraph_run_id is None
    assert context.agent_run_id is None
    assert context.tool_call_id is None
    assert context.api_call_id is None
    assert context.service_bus_message_id is None
    assert context.evaluation_id is None


def test_should_carry_the_full_doc_24_correlation_chain_when_populated() -> None:
    context = CorrelationContext(
        request_id="req-1",
        correlation_id="corr-1",
        conversation_id="conv-1",
        session_id="sess-1",
        workflow_instance_id="wf-1",
        langgraph_run_id="run-1",
        agent_run_id="agent-run-1",
        tool_call_id="tool-1",
        api_call_id="api-1",
        service_bus_message_id="msg-1",
        evaluation_id="eval-1",
    )

    assert context.langgraph_run_id == "run-1"
    assert context.agent_run_id == "agent-run-1"
    assert context.tool_call_id == "tool-1"
    assert context.api_call_id == "api-1"
    assert context.service_bus_message_id == "msg-1"
    assert context.evaluation_id == "eval-1"
