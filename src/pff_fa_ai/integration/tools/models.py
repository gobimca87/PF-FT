from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.context.erc.provenance import Provenance
from pff_fa_ai.integration.errors.codes import IntegrationErrorCode
from pff_fa_ai.integration.tools.policy import ToolRiskClass
from pff_fa_ai.integration.tools.states import ToolCallStatus


class ToolSource(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    type: str = "enterprise_api"
    api_id: str


class ToolExecutionPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    timeout_ms: int = Field(gt=0)
    idempotent: bool


class ToolDefinition(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    tool_id: str
    version: str
    description: str
    source: ToolSource
    input_schema_ref: str
    output_schema_ref: str
    execution_policy: ToolExecutionPolicy
    risk_class: ToolRiskClass = ToolRiskClass.READ
    allowed_agents: tuple[str, ...] = Field(default_factory=tuple)


class ToolResultError(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    code: IntegrationErrorCode
    message: str
    retryable: bool


class ToolResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    tool_id: str
    status: ToolCallStatus
    data: Any = None
    provenance: Provenance | None = None
    error: ToolResultError | None = None


class ToolExecutionRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    tool_id: str
    agent_id: str
    claims: ClaimsContext
    arguments: dict[str, str] = Field(default_factory=dict)
    workflow_instance_id: str
    operation_id: str
