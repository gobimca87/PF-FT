from __future__ import annotations

from pff_fa_ai.common.exceptions import WorkflowError
from pff_fa_ai.context.erc.states import ErcLifecycleStatus

_VALID_TRANSITIONS: dict[ErcLifecycleStatus, frozenset[ErcLifecycleStatus]] = {
    ErcLifecycleStatus.NOT_CREATED: frozenset({ErcLifecycleStatus.REQUIREMENTS_IDENTIFIED}),
    ErcLifecycleStatus.REQUIREMENTS_IDENTIFIED: frozenset({ErcLifecycleStatus.COLLECTING}),
    ErcLifecycleStatus.COLLECTING: frozenset(
        {
            ErcLifecycleStatus.NORMALIZING,
            ErcLifecycleStatus.FAILED,
        }
    ),
    ErcLifecycleStatus.NORMALIZING: frozenset(
        {
            ErcLifecycleStatus.AGGREGATING,
            ErcLifecycleStatus.FAILED,
        }
    ),
    ErcLifecycleStatus.AGGREGATING: frozenset(
        {
            ErcLifecycleStatus.VALIDATING,
            ErcLifecycleStatus.FAILED,
        }
    ),
    ErcLifecycleStatus.VALIDATING: frozenset(
        {
            ErcLifecycleStatus.READY,
            ErcLifecycleStatus.INVALID,
            ErcLifecycleStatus.FAILED,
        }
    ),
    ErcLifecycleStatus.READY: frozenset(
        {
            ErcLifecycleStatus.REFRESH_REQUIRED,
            ErcLifecycleStatus.STALE,
        }
    ),
    ErcLifecycleStatus.REFRESH_REQUIRED: frozenset({ErcLifecycleStatus.REFRESHING}),
    ErcLifecycleStatus.REFRESHING: frozenset({ErcLifecycleStatus.READY, ErcLifecycleStatus.FAILED}),
    ErcLifecycleStatus.STALE: frozenset(
        {
            ErcLifecycleStatus.REFRESH_REQUIRED,
            ErcLifecycleStatus.REFRESHING,
        }
    ),
    ErcLifecycleStatus.INVALID: frozenset({ErcLifecycleStatus.REQUIREMENTS_IDENTIFIED}),
    ErcLifecycleStatus.FAILED: frozenset({ErcLifecycleStatus.REQUIREMENTS_IDENTIFIED}),
}


def is_valid_transition(*, current: ErcLifecycleStatus, target: ErcLifecycleStatus) -> bool:
    return target in _VALID_TRANSITIONS.get(current, frozenset())


def assert_valid_transition(*, current: ErcLifecycleStatus, target: ErcLifecycleStatus) -> None:
    if not is_valid_transition(current=current, target=target):
        raise WorkflowError(f"Invalid ERC lifecycle transition: {current.value} -> {target.value}")
