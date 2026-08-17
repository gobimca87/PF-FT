import pytest

from pf_ft_ai.common.exceptions import WorkflowError
from pf_ft_ai.common.precedence import DataSourcePrecedence
from pf_ft_ai.context.erc.states import ErcSectionStatus
from pf_ft_ai.domain.state_consistency import (
    assert_child_not_completed_while_parent_cancelled,
    assert_erc_completion_consistent,
    assert_state_update_respects_precedence,
    assert_tool_execution_authorized,
    assert_waiting_workflow_has_resume_information,
    assert_workflow_completion_allowed,
    should_process_event,
)
from pf_ft_ai.domain.workflow.states import WorkflowStatus


def test_rule1_should_reject_completed_child_under_cancelled_parent() -> None:
    with pytest.raises(WorkflowError, match="CANCELLED"):
        assert_child_not_completed_while_parent_cancelled(
            parent_status=WorkflowStatus.CANCELLED, child_status=WorkflowStatus.COMPLETED
        )


def test_rule1_should_allow_completed_child_under_active_parent() -> None:
    assert_child_not_completed_while_parent_cancelled(
        parent_status=WorkflowStatus.REASONING, child_status=WorkflowStatus.COMPLETED
    )


def test_rule2_should_reject_tool_execution_when_workflow_unauthorized() -> None:
    with pytest.raises(WorkflowError, match="unauthorized"):
        assert_tool_execution_authorized(workflow_authorized=False)


def test_rule2_should_allow_tool_execution_when_workflow_authorized() -> None:
    assert_tool_execution_authorized(workflow_authorized=True)


def test_rule3_should_reject_completion_with_unresolved_mandatory_operation() -> None:
    with pytest.raises(WorkflowError, match="mandatory operation"):
        assert_workflow_completion_allowed(mandatory_operations_resolved=False)


def test_rule3_should_allow_completion_when_mandatory_operations_resolved() -> None:
    assert_workflow_completion_allowed(mandatory_operations_resolved=True)


def test_rule4_should_reject_partial_section_presented_as_complete() -> None:
    with pytest.raises(WorkflowError, match="PARTIAL"):
        assert_erc_completion_consistent(section_status=ErcSectionStatus.PARTIAL)


def test_rule4_should_allow_complete_section() -> None:
    assert_erc_completion_consistent(section_status=ErcSectionStatus.COMPLETE)


def test_rule5_should_reject_waiting_workflow_without_resume_information() -> None:
    with pytest.raises(WorkflowError, match="resume information"):
        assert_waiting_workflow_has_resume_information(has_resume_information=False)


def test_rule5_should_allow_waiting_workflow_with_resume_information() -> None:
    assert_waiting_workflow_has_resume_information(has_resume_information=True)


def test_rule6_should_not_reprocess_a_duplicate_event() -> None:
    assert should_process_event(already_processed=True) is False


def test_rule6_should_process_a_new_event() -> None:
    assert should_process_event(already_processed=False) is True


def test_rule7_should_reject_slm_output_overriding_enterprise_state() -> None:
    with pytest.raises(WorkflowError, match="overrides stale AI state"):
        assert_state_update_respects_precedence(
            incoming=DataSourcePrecedence.SLM, existing=DataSourcePrecedence.ENTERPRISE
        )


def test_rule7_should_allow_enterprise_state_to_override_slm_output() -> None:
    assert_state_update_respects_precedence(
        incoming=DataSourcePrecedence.ENTERPRISE, existing=DataSourcePrecedence.SLM
    )


def test_rule7_should_allow_equal_precedence_update() -> None:
    assert_state_update_respects_precedence(
        incoming=DataSourcePrecedence.ERC, existing=DataSourcePrecedence.ERC
    )
