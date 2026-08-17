from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from pf_ft_ai.domain.versioning import Versioned
from pf_ft_ai.domain.workflow.states import WaitingType, WorkflowStatus


class WaitingInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: WaitingType
    reason: str
    created_at: datetime
    resume_node: str
    expected_event_type: str | None = None


class WorkflowInstance(Versioned):
    workflow_instance_id: str
    workflow_type: str
    workflow_version: str
    status: WorkflowStatus
    current_state: str
    # doc 11 §56/§148: event-driven resume must verify the workflow belongs to the
    # event's organization before resuming — added in Phase 12 for that check.
    organization_id: str
    started_at: datetime
    updated_at: datetime
    enterprise_workflow_id: str | None = None
    waiting: WaitingInfo | None = None
