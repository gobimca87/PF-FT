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
