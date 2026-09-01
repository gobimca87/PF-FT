import pytest

from pff_fa_ai.common.exceptions import WorkflowError
from pff_fa_ai.prompt_engineering.lifecycle import assert_valid_transition, is_valid_transition
from pff_fa_ai.prompt_engineering.states import PromptStatus


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (PromptStatus.DRAFT, PromptStatus.TESTING),
        (PromptStatus.TESTING, PromptStatus.APPROVED),
        (PromptStatus.TESTING, PromptStatus.DRAFT),
        (PromptStatus.APPROVED, PromptStatus.ACTIVE),
        (PromptStatus.ACTIVE, PromptStatus.DEPRECATED),
        (PromptStatus.DEPRECATED, PromptStatus.RETIRED),
        (PromptStatus.DRAFT, PromptStatus.BLOCKED),
        (PromptStatus.ACTIVE, PromptStatus.BLOCKED),
        (PromptStatus.BLOCKED, PromptStatus.DRAFT),
    ],
)
def test_should_allow_the_documented_happy_path_transitions(
    current: PromptStatus, target: PromptStatus
) -> None:
    assert is_valid_transition(current=current, target=target)
    assert_valid_transition(current=current, target=target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (PromptStatus.DRAFT, PromptStatus.ACTIVE),
        (PromptStatus.DRAFT, PromptStatus.RETIRED),
        (PromptStatus.RETIRED, PromptStatus.ACTIVE),
        (PromptStatus.ACTIVE, PromptStatus.DRAFT),
        (PromptStatus.APPROVED, PromptStatus.DRAFT),
    ],
)
def test_should_reject_undocumented_transitions(
    current: PromptStatus, target: PromptStatus
) -> None:
    assert not is_valid_transition(current=current, target=target)
    with pytest.raises(WorkflowError, match="Invalid prompt lifecycle transition"):
        assert_valid_transition(current=current, target=target)


def test_retired_should_be_a_terminal_state() -> None:
    for target in PromptStatus:
        assert not is_valid_transition(current=PromptStatus.RETIRED, target=target)
