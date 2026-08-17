from __future__ import annotations

from pf_ft_ai.common.exceptions import WorkflowError
from pf_ft_ai.common.precedence import DataSourcePrecedence, higher_precedence
from pf_ft_ai.context.erc.states import ErcSectionStatus
from pf_ft_ai.domain.workflow.states import WorkflowStatus


def assert_child_not_completed_while_parent_cancelled(
    *, parent_status: WorkflowStatus, child_status: WorkflowStatus
) -> None:
    """Rule 1 (doc 5 §50)."""
    if parent_status is WorkflowStatus.CANCELLED and child_status is WorkflowStatus.COMPLETED:
        raise WorkflowError(
            "A child cannot be COMPLETED while its required parent workflow is CANCELLED"
        )


def assert_tool_execution_authorized(*, workflow_authorized: bool) -> None:
    """Rule 2 (doc 5 §50)."""
    if not workflow_authorized:
        raise WorkflowError("A tool cannot execute when the workflow is unauthorized")


def assert_workflow_completion_allowed(*, mandatory_operations_resolved: bool) -> None:
    """Rule 3 (doc 5 §50)."""
    if not mandatory_operations_resolved:
        raise WorkflowError(
            "A workflow cannot be COMPLETED while a mandatory operation remains unresolved"
        )


def assert_erc_completion_consistent(*, section_status: ErcSectionStatus) -> None:
    """Rule 4 (doc 5 §50): a section marked PARTIAL can never be reported as COMPLETE."""
    if section_status is ErcSectionStatus.PARTIAL:
        raise WorkflowError("An ERC section marked PARTIAL cannot be represented as COMPLETE")


def assert_waiting_workflow_has_resume_information(*, has_resume_information: bool) -> None:
    """Rule 5 (doc 5 §50)."""
    if not has_resume_information:
        raise WorkflowError("A waiting workflow must persist its resume information")


def should_process_event(*, already_processed: bool) -> bool:
    """Rule 6 (doc 5 §50, §39): a duplicate event resolves to no-op, not failure."""
    return not already_processed


def assert_state_update_respects_precedence(
    *, incoming: DataSourcePrecedence, existing: DataSourcePrecedence
) -> None:
    """Rule 7 (doc 5 §50): enterprise state always overrides stale AI state."""
    if higher_precedence(incoming, existing) == existing and incoming != existing:
        raise WorkflowError(
            "Enterprise state always overrides stale AI state: "
            f"'{incoming}' may not override higher-precedence '{existing}'"
        )
