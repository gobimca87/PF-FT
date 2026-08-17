import pytest

from pf_ft_ai.common.exceptions import WorkflowError
from pf_ft_ai.context.erc.lifecycle import assert_valid_transition, is_valid_transition
from pf_ft_ai.context.erc.states import ErcLifecycleStatus


def test_should_allow_the_documented_happy_path_transitions() -> None:
    happy_path = [
        ErcLifecycleStatus.NOT_CREATED,
        ErcLifecycleStatus.REQUIREMENTS_IDENTIFIED,
        ErcLifecycleStatus.COLLECTING,
        ErcLifecycleStatus.NORMALIZING,
        ErcLifecycleStatus.AGGREGATING,
        ErcLifecycleStatus.VALIDATING,
        ErcLifecycleStatus.READY,
    ]
    for current, target in zip(happy_path, happy_path[1:], strict=False):
        assert is_valid_transition(current=current, target=target)


def test_should_allow_the_refresh_cycle() -> None:
    assert is_valid_transition(
        current=ErcLifecycleStatus.READY, target=ErcLifecycleStatus.REFRESH_REQUIRED
    )
    assert is_valid_transition(
        current=ErcLifecycleStatus.REFRESH_REQUIRED, target=ErcLifecycleStatus.REFRESHING
    )
    assert is_valid_transition(
        current=ErcLifecycleStatus.REFRESHING, target=ErcLifecycleStatus.READY
    )


def test_should_reject_skipping_directly_from_not_created_to_ready() -> None:
    assert not is_valid_transition(
        current=ErcLifecycleStatus.NOT_CREATED, target=ErcLifecycleStatus.READY
    )


def test_assert_valid_transition_should_raise_on_invalid_transition() -> None:
    with pytest.raises(WorkflowError, match="Invalid ERC lifecycle transition"):
        assert_valid_transition(
            current=ErcLifecycleStatus.NOT_CREATED, target=ErcLifecycleStatus.READY
        )


def test_assert_valid_transition_should_pass_silently_on_valid_transition() -> None:
    assert_valid_transition(current=ErcLifecycleStatus.VALIDATING, target=ErcLifecycleStatus.READY)
