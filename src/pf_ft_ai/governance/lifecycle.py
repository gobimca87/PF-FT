from __future__ import annotations

from pf_ft_ai.common.exceptions import GuardrailError
from pf_ft_ai.governance.states import AiLifecycleState

# doc 20 §11's linear flow, plus REVIEW's documented fork (CHANGE/RETIRE) and CHANGE's
# re-entry into the build/validate/approve/deploy cycle (doc 20 §76 "Change Management"
# requires the same Tests/Evaluation/Approval/Release a first build needs — a change is
# not a shortcut around the lifecycle). RETIRE is terminal.
_TRANSITIONS: dict[AiLifecycleState, frozenset[AiLifecycleState]] = {
    AiLifecycleState.IDEA: frozenset({AiLifecycleState.ASSESS}),
    AiLifecycleState.ASSESS: frozenset({AiLifecycleState.DESIGN}),
    AiLifecycleState.DESIGN: frozenset({AiLifecycleState.BUILD}),
    AiLifecycleState.BUILD: frozenset({AiLifecycleState.VALIDATE}),
    AiLifecycleState.VALIDATE: frozenset({AiLifecycleState.APPROVE}),
    AiLifecycleState.APPROVE: frozenset({AiLifecycleState.DEPLOY}),
    AiLifecycleState.DEPLOY: frozenset({AiLifecycleState.MONITOR}),
    AiLifecycleState.MONITOR: frozenset({AiLifecycleState.REVIEW}),
    AiLifecycleState.REVIEW: frozenset({AiLifecycleState.CHANGE, AiLifecycleState.RETIRE}),
    AiLifecycleState.CHANGE: frozenset({AiLifecycleState.BUILD}),
    AiLifecycleState.RETIRE: frozenset(),
}


def allowed_next_states(current: AiLifecycleState) -> frozenset[AiLifecycleState]:
    return _TRANSITIONS[current]


def assert_valid_lifecycle_transition(current: AiLifecycleState, target: AiLifecycleState) -> None:
    """doc 20 §29-30 traceability/auditability — a governed artifact's lifecycle must
    move through the defined stages, not jump ahead (e.g. IDEA straight to DEPLOY)."""
    allowed = allowed_next_states(current)
    if target not in allowed:
        raise GuardrailError(
            f"Invalid AI lifecycle transition: '{current.value}' -> '{target.value}' "
            f"(doc 20 §11). Allowed from '{current.value}': "
            f"{sorted(state.value for state in allowed) or 'none (terminal state)'}",
            details={"current": current.value, "target": target.value},
        )
