from __future__ import annotations

from typing import Protocol

from pf_ft_ai.domain.workflow.entities import WaitingInfo, WorkflowInstance
from pf_ft_ai.domain.workflow.states import WorkflowStatus


class WorkflowRepository(Protocol):
    async def create(self, workflow: WorkflowInstance) -> WorkflowInstance: ...

    async def get(self, workflow_instance_id: str) -> WorkflowInstance | None: ...

    async def transition(
        self,
        workflow_instance_id: str,
        *,
        status: WorkflowStatus,
        current_state: str,
        expected_version: int,
        waiting: WaitingInfo | None = None,
    ) -> WorkflowInstance: ...
