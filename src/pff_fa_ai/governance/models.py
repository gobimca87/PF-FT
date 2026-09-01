from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.governance.states import (
    AiLifecycleState,
    GovernanceRiskLevel,
    GovernedArtifactType,
    Likelihood,
    RiskStatus,
)


class GovernedArtifact(BaseModel):
    """doc 20 §9/§33 — every governed AI capability must have a defined purpose,
    owner, risk classification and lifecycle status. Trimmed to what's mechanically
    trackable today; `business_owner` is optional since not every artifact type (e.g.
    an MCP server) necessarily has one distinct from its technical owner."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    artifact_id: str
    artifact_type: GovernedArtifactType
    name: str
    owner: str
    business_owner: str | None = None
    risk: GovernanceRiskLevel
    lifecycle_state: AiLifecycleState
    version: str


class RiskRegisterEntry(BaseModel):
    """doc 20 §18 — the exact field list DEVELOPMENT-GUIDE Phase 21 names."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    risk_id: str
    capability: str
    cause: str
    impact: str
    likelihood: Likelihood
    severity: GovernanceRiskLevel
    owner: str
    controls: tuple[str, ...] = Field(default_factory=tuple)
    residual_risk: GovernanceRiskLevel
    mitigation: str
    status: RiskStatus
    review_date: date
