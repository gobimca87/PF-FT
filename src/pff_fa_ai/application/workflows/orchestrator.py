from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict

from pff_fa_ai.application.workflows.states import OrchestrationStatus
from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.common.correlation import CorrelationContext
from pff_fa_ai.common.exceptions import WorkflowError
from pff_fa_ai.domain.conversation.entities import Conversation


class OrchestrationRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    conversation: Conversation
    user_message: str
    claims: ClaimsContext
    correlation: CorrelationContext


class OrchestrationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: OrchestrationStatus
    response_message: str
    workflow_instance_id: str | None = None


class WorkflowOrchestrator(Protocol):
    async def handle_message(self, request: OrchestrationRequest) -> OrchestrationResult: ...


class NullWorkflowOrchestrator:
    async def handle_message(self, request: OrchestrationRequest) -> OrchestrationResult:
        raise WorkflowError(
            "Workflow orchestration is not yet available: Phase 4 wires the "
            "Supervisor/Agent/Harness/LangGraph stack behind this port"
        )
