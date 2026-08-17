from pf_ft_ai.context.projection.budget import compute_available_context_tokens


def test_should_compute_available_tokens_per_doc8_formula() -> None:
    """doc 8 §76: Available = Window - System - Agent - Conversation - Reserved - Safety."""
    available = compute_available_context_tokens(
        model_context_window=20000,
        system_tokens=500,
        agent_tokens=500,
        conversation_tokens=2000,
        reserved_output_tokens=4000,
        safety_margin_tokens=1000,
    )

    assert available == 20000 - 500 - 500 - 2000 - 4000 - 1000
    assert available == 12000


def test_should_match_documented_default_budget_with_no_conversation_or_agent_overhead() -> None:
    """doc 8 §77 defaults with zero variable overhead: 20000 - 4000 - 1000 = 15000."""
    available = compute_available_context_tokens(
        model_context_window=20000,
        system_tokens=0,
        agent_tokens=0,
        conversation_tokens=0,
        reserved_output_tokens=4000,
        safety_margin_tokens=1000,
    )

    assert available == 15000


def test_should_return_non_positive_value_on_overflow_rather_than_raise() -> None:
    """doc 8 §114-115: overflow handling is the caller's responsibility, not this formula's."""
    available = compute_available_context_tokens(
        model_context_window=1000,
        system_tokens=500,
        agent_tokens=500,
        conversation_tokens=500,
        reserved_output_tokens=4000,
        safety_margin_tokens=1000,
    )

    assert available < 0
