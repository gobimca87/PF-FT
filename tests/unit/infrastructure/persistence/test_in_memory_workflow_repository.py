from datetime import UTC, datetime

import pytest

from pff_fa_ai.common.exceptions import WorkflowError
from pff_fa_ai.domain.workflow.entities import WaitingInfo, WorkflowInstance
from pff_fa_ai.domain.workflow.states import WaitingType, WorkflowStatus
from pff_fa_ai.infrastructure.persistence.in_memory_workflow_repository import (
    InMemoryWorkflowRepository,
)


def _workflow(
    *, workflow_instance_id: str = "wf-1", organization_id: str = "club-123"
) -> WorkflowInstance:
    now = datetime.now(UTC)
    return WorkflowInstance(
        workflow_instance_id=workflow_instance_id,
        workflow_type="affiliation",
        workflow_version="1.0.0",
        status=WorkflowStatus.WAITING_FOR_EXTERNAL_EVENT,
        current_state="WAITING_FOR_EXTERNAL_EVENT",
        organization_id=organization_id,
        started_at=now,
        updated_at=now,
        waiting=WaitingInfo(
            type=WaitingType.WAITING_FOR_EXTERNAL_EVENT,
            reason="hil_pending",
            created_at=now,
            resume_node="refresh_erc",
            expected_event_type="HIL_TASK_COMPLETED",
        ),
    )


async def test_should_create_and_fetch_a_workflow() -> None:
    repository = InMemoryWorkflowRepository()
    workflow = _workflow()

    await repository.create(workflow)
    fetched = await repository.get("wf-1")

    assert fetched is not None
    assert fetched.organization_id == "club-123"


async def test_should_return_none_for_a_missing_workflow() -> None:
    repository = InMemoryWorkflowRepository()

    assert await repository.get("does-not-exist") is None


async def test_should_reject_creating_a_duplicate_workflow() -> None:
    repository = InMemoryWorkflowRepository()
    await repository.create(_workflow())

    with pytest.raises(WorkflowError, match="already exists"):
        await repository.create(_workflow())


async def test_transition_should_bump_version_and_update_state() -> None:
    repository = InMemoryWorkflowRepository()
    await repository.create(_workflow())

    updated = await repository.transition(
        "wf-1", status=WorkflowStatus.RESUMING, current_state="refresh_erc", expected_version=1
    )

    assert updated.version == 2
    assert updated.status is WorkflowStatus.RESUMING
    assert updated.current_state == "refresh_erc"


async def test_transition_should_reject_a_stale_expected_version() -> None:
    repository = InMemoryWorkflowRepository()
    await repository.create(_workflow())
    await repository.transition(
        "wf-1", status=WorkflowStatus.RESUMING, current_state="refresh_erc", expected_version=1
    )

    with pytest.raises(WorkflowError, match="Concurrency conflict"):
        await repository.transition(
            "wf-1", status=WorkflowStatus.COMPLETING, current_state="finish", expected_version=1
        )


async def test_transition_should_raise_for_an_unknown_workflow() -> None:
    repository = InMemoryWorkflowRepository()

    with pytest.raises(WorkflowError, match="not found"):
        await repository.transition(
            "unknown", status=WorkflowStatus.RESUMING, current_state="x", expected_version=1
        )
