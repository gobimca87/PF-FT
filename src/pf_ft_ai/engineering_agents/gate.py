from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, Field

from pf_ft_ai.engineering_agents.models import EngineeringAgentResult
from pf_ft_ai.engineering_agents.states import (
    FINDING_SEVERITY_RANK,
    AgentResultStatus,
    FindingSeverity,
    GateStatus,
)


class QualityGateConfig(BaseModel):
    """doc 23 §121. `severity_block` is the minimum finding severity that fails the
    gate outright, regardless of which agent raised it (doc 23 §59 "Critical security
    issue → FAIL")."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    severity_block: FindingSeverity = FindingSeverity.CRITICAL
    required_agent_ids: frozenset[str] = Field(default_factory=frozenset)


class GateOutcome(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: GateStatus
    blocking_reasons: tuple[str, ...] = Field(default_factory=tuple)
    warning_reasons: tuple[str, ...] = Field(default_factory=tuple)


def evaluate_quality_gate(
    *, results: Sequence[EngineeringAgentResult], config: QualityGateConfig
) -> GateOutcome:
    """doc 23 §58-59/§115-117: mandatory-agent FAIL/ERROR always blocks (§116);
    optional-agent FAIL/ERROR only warns (§117); any finding at or above
    `severity_block` always blocks, regardless of which agent raised it (§59)."""
    blocking: list[str] = []
    warnings: list[str] = []

    seen_agent_ids = {result.agent_id for result in results}
    for missing_agent_id in sorted(config.required_agent_ids - seen_agent_ids):
        blocking.append(f"REQUIRED_AGENT_DID_NOT_RUN:{missing_agent_id}")

    for result in results:
        is_required = result.agent_id in config.required_agent_ids
        requirement = "REQUIRED" if is_required else "OPTIONAL"
        if result.status is AgentResultStatus.FAIL:
            target = blocking if is_required else warnings
            target.append(f"{requirement}_AGENT_FAILED:{result.agent_id}")
        elif result.status is AgentResultStatus.ERROR:
            target = blocking if is_required else warnings
            target.append(f"{requirement}_AGENT_ERRORED:{result.agent_id}")
        elif result.status is AgentResultStatus.WARNING:
            warnings.append(f"AGENT_WARNING:{result.agent_id}")

        for finding in result.findings:
            severity_rank = FINDING_SEVERITY_RANK[finding.severity]
            if severity_rank >= FINDING_SEVERITY_RANK[config.severity_block]:
                blocking.append(f"CRITICAL_FINDING:{finding.finding_id}")

    if blocking:
        status = GateStatus.FAIL
    elif warnings:
        status = GateStatus.WARNING
    else:
        status = GateStatus.PASS
    return GateOutcome(
        status=status, blocking_reasons=tuple(blocking), warning_reasons=tuple(warnings)
    )
