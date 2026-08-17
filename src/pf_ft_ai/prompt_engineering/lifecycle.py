from __future__ import annotations

from pf_ft_ai.common.exceptions import WorkflowError
from pf_ft_ai.prompt_engineering.states import PromptStatus

# doc 16 §34/§102, DEVELOPMENT-GUIDE Phase 10: DRAFT -> TESTING -> APPROVED -> ACTIVE ->
# DEPRECATED -> RETIRED, with BLOCKED reachable from any non-terminal state (a security
# finding can surface at any point) and remediable back to DRAFT.
_VALID_TRANSITIONS: dict[PromptStatus, frozenset[PromptStatus]] = {
    PromptStatus.DRAFT: frozenset({PromptStatus.TESTING, PromptStatus.BLOCKED}),
    PromptStatus.TESTING: frozenset(
        {PromptStatus.APPROVED, PromptStatus.DRAFT, PromptStatus.BLOCKED}
    ),
    PromptStatus.APPROVED: frozenset({PromptStatus.ACTIVE, PromptStatus.BLOCKED}),
    PromptStatus.ACTIVE: frozenset({PromptStatus.DEPRECATED, PromptStatus.BLOCKED}),
    PromptStatus.DEPRECATED: frozenset({PromptStatus.RETIRED}),
    PromptStatus.RETIRED: frozenset(),
    PromptStatus.BLOCKED: frozenset({PromptStatus.DRAFT}),
}


def is_valid_transition(*, current: PromptStatus, target: PromptStatus) -> bool:
    return target in _VALID_TRANSITIONS.get(current, frozenset())


def assert_valid_transition(*, current: PromptStatus, target: PromptStatus) -> None:
    if not is_valid_transition(current=current, target=target):
        raise WorkflowError(
            f"Invalid prompt lifecycle transition: {current.value} -> {target.value}"
        )
