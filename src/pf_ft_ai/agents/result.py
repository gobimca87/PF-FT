from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from pf_ft_ai.agents.states import AgentRunStatus
from pf_ft_ai.common.error_category import ErrorCategory
from pf_ft_ai.domain.workflow.entities import WaitingInfo


class AgentError(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: ErrorCategory
    code: str
    message_safe: str
    retryable: bool


class AgentExecutionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: AgentRunStatus
    response: str | None = None
    erc_reference: str | None = None
    waiting: WaitingInfo | None = None
    errors: list[AgentError] = Field(default_factory=list)
