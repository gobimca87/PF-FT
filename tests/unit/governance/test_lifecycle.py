import pytest

from pff_fa_ai.common.exceptions import GuardrailError
from pff_fa_ai.governance.lifecycle import allowed_next_states, assert_valid_lifecycle_transition
from pff_fa_ai.governance.states import AiLifecycleState


def test_every_state_should_appear_in_the_transition_table() -> None:
    for state in AiLifecycleState:
        allowed_next_states(state)  # raises KeyError if a state was left out


def test_retire_should_be_a_terminal_state() -> None:
    assert allowed_next_states(AiLifecycleState.RETIRE) == frozenset()


def test_review_should_fork_to_change_or_retire() -> None:
    assert allowed_next_states(AiLifecycleState.REVIEW) == frozenset({
        AiLifecycleState.CHANGE,
        AiLifecycleState.RETIRE,
    })


def test_change_should_re_enter_the_build_cycle() -> None:
    assert allowed_next_states(AiLifecycleState.CHANGE) == frozenset({AiLifecycleState.BUILD})


def test_the_full_documented_flow_should_be_walkable_in_order() -> None:
    ordered = [
        AiLifecycleState.IDEA,
        AiLifecycleState.ASSESS,
        AiLifecycleState.DESIGN,
        AiLifecycleState.BUILD,
        AiLifecycleState.VALIDATE,
        AiLifecycleState.APPROVE,
        AiLifecycleState.DEPLOY,
        AiLifecycleState.MONITOR,
        AiLifecycleState.REVIEW,
    ]
    for current, target in zip(ordered, ordered[1:], strict=False):
        assert_valid_lifecycle_transition(current, target)  # must not raise


def test_should_reject_skipping_stages() -> None:
    with pytest.raises(GuardrailError, match="Invalid AI lifecycle transition"):
        assert_valid_lifecycle_transition(AiLifecycleState.IDEA, AiLifecycleState.DEPLOY)


def test_should_reject_a_transition_out_of_the_terminal_retire_state() -> None:
    with pytest.raises(GuardrailError, match="terminal state"):
        assert_valid_lifecycle_transition(AiLifecycleState.RETIRE, AiLifecycleState.IDEA)
