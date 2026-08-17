from datetime import UTC, datetime

from pf_ft_ai.domain.workflow.entities import WaitingInfo, WorkflowInstance
from pf_ft_ai.domain.workflow.states import WaitingType, WorkflowStatus


def test_should_create_a_new_workflow_instance_at_version_one() -> None:
    now = datetime.now(UTC)

    workflow = WorkflowInstance(
        workflow_instance_id="wf-123",
        workflow_type="affiliation",
        workflow_version="1.0.0",
        status=WorkflowStatus.CREATED,
        current_state="CREATED",
        started_at=now,
        updated_at=now,
    )

    assert workflow.version == 1
    assert workflow.waiting is None
    assert workflow.enterprise_workflow_id is None


def test_should_carry_waiting_information_distinct_from_workflow_id() -> None:
    now = datetime.now(UTC)
    waiting = WaitingInfo(
        type=WaitingType.WAITING_FOR_EXTERNAL_EVENT,
        reason="affiliation_status_update",
        created_at=now,
        resume_node="refresh_erc",
        expected_event_type="affiliation.updated",
    )

    workflow = WorkflowInstance(
        workflow_instance_id="wf-123",
        workflow_type="affiliation",
        workflow_version="1.0.0",
        status=WorkflowStatus.WAITING_FOR_EXTERNAL_EVENT,
        current_state="WAITING_FOR_EXTERNAL_EVENT",
        started_at=now,
        updated_at=now,
        enterprise_workflow_id="ent-wf-789",
        waiting=waiting,
    )

    assert workflow.waiting is not None
    assert workflow.waiting.resume_node == "refresh_erc"
    # AI workflow ID and enterprise workflow ID must be stored separately (doc 5 §16)
    assert workflow.workflow_instance_id != workflow.enterprise_workflow_id
