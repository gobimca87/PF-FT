from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.common.correlation import CorrelationContext


class AgentExecutionContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    conversation_id: str
    session_id: str
    workflow_instance_id: str
    agent_run_id: str
    claims: ClaimsContext
    user_message: str
    correlation: CorrelationContext
