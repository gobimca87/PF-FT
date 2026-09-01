from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.engineering_agents.states import (
    AgentLifecycleStatus,
    AgentResultStatus,
    ChangedComponent,
    EngineeringAgentRisk,
    ExecutionMode,
    FindingSeverity,
    GateStatus,
    PermissionLevel,
)


class Finding(BaseModel):
    """doc 23 §66."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    finding_id: str
    agent_id: str
    severity: FindingSeverity
    rule: str | None = None
    file: str | None = None
    line: int | None = None
    description: str
    evidence: str | None = None
    recommendation: str | None = None
    auto_remediation_available: bool = False


class EngineeringAgentResult(BaseModel):
    """doc 23 §56 result contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    agent_version: str
    status: AgentResultStatus
    severity: FindingSeverity | None = None
    findings: tuple[Finding, ...] = Field(default_factory=tuple)
    metrics: dict[str, float] = Field(default_factory=dict)
    evidence: tuple[str, ...] = Field(default_factory=tuple)
    remediation: tuple[str, ...] = Field(default_factory=tuple)


class EngineeringAgentDefinition(BaseModel):
    """doc 23 §82 registry entry / §135 documentation requirements, trimmed to what's
    mechanically enforceable today."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    version: str
    purpose: str
    owner: str
    risk: EngineeringAgentRisk
    permission_level: PermissionLevel
    execution_mode: ExecutionMode
    lifecycle_status: AgentLifecycleStatus
    # None for deterministic, non-LLM agents (doc 15 "mock provider" honesty pattern
    # extends here too: an agent isn't given a model_id until one is actually approved).
    model_id: str | None = None


class EngineeringRun(BaseModel):
    """doc 23 §55 execution state / §125 final report, trimmed to this phase's scope."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    run_id: str
    repository: str
    commit: str
    pull_request: str | None = None
    changed_components: tuple[ChangedComponent, ...] = Field(default_factory=tuple)
    agent_ids: tuple[str, ...] = Field(default_factory=tuple)
    results: tuple[EngineeringAgentResult, ...] = Field(default_factory=tuple)
    gate_status: GateStatus | None = None
