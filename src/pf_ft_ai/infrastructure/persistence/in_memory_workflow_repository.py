from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from pf_ft_ai.common.exceptions import WorkflowError
from pf_ft_ai.domain.versioning import assert_expected_version
from pf_ft_ai.domain.workflow.entities import WorkflowInstance
from pf_ft_ai.domain.workflow.states import WorkflowStatus


class InMemoryWorkflowRepository:
    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowInstance] = {}
        self._lock = asyncio.Lock()

    async def create(self, workflow: WorkflowInstance) -> WorkflowInstance:
        async with self._lock:
            if workflow.workflow_instance_id in self._workflows:
                raise WorkflowError(f"Workflow already exists: {workflow.workflow_instance_id}")
            self._workflows[workflow.workflow_instance_id] = workflow
            return workflow

    async def get(self, workflow_instance_id: str) -> WorkflowInstance | None:
        return self._workflows.get(workflow_instance_id)

    async def transition(
        self,
        workflow_instance_id: str,
        *,
        status: WorkflowStatus,
        current_state: str,
        expected_version: int,
    ) -> WorkflowInstance:
        async with self._lock:
            existing = self._workflows.get(workflow_instance_id)
            if existing is None:
                raise WorkflowError(f"Workflow not found: {workflow_instance_id}")
            assert_expected_version(
                current_version=existing.version, expected_version=expected_version
            )
            updated = existing.model_copy(
                update={
                    "status": status,
                    "current_state": current_state,
                    "version": existing.version + 1,
                    "updated_at": datetime.now(UTC),
                }
            )
            self._workflows[workflow_instance_id] = updated
            return updated
