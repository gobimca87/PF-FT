from datetime import date

import pytest
from pydantic import ValidationError

from pf_ft_ai.governance.models import GovernedArtifact, RiskRegisterEntry
from pf_ft_ai.governance.states import (
    AiLifecycleState,
    GovernanceRiskLevel,
    GovernedArtifactType,
    Likelihood,
    RiskStatus,
)


def test_governed_artifact_should_default_business_owner_to_none() -> None:
    artifact = GovernedArtifact(
        artifact_id="prompt-affiliation-system-v1",
        artifact_type=GovernedArtifactType.PROMPT,
        name="Affiliation system prompt",
        owner="ai-platform",
        risk=GovernanceRiskLevel.MEDIUM,
        lifecycle_state=AiLifecycleState.IDEA,
        version="1.0.0",
    )

    assert artifact.business_owner is None


def test_governed_artifact_should_be_frozen() -> None:
    artifact = GovernedArtifact(
        artifact_id="prompt-1",
        artifact_type=GovernedArtifactType.PROMPT,
        name="Test",
        owner="ai-platform",
        risk=GovernanceRiskLevel.LOW,
        lifecycle_state=AiLifecycleState.IDEA,
        version="1.0.0",
    )

    with pytest.raises(ValidationError):
        artifact.lifecycle_state = AiLifecycleState.DEPLOY  # type: ignore[misc]


def test_risk_register_entry_should_require_all_documented_fields() -> None:
    entry = RiskRegisterEntry(
        risk_id="RISK-001",
        capability="Affiliation Agent",
        cause="SLM hallucination under sparse enterprise data",
        impact="Incorrect affiliation status communicated to a club",
        likelihood=Likelihood.MEDIUM,
        severity=GovernanceRiskLevel.HIGH,
        owner="ai-platform",
        controls=("Output guardrail cross-check against enterprise API",),
        residual_risk=GovernanceRiskLevel.LOW,
        mitigation="Golden dataset regression covering sparse-data scenarios",
        status=RiskStatus.MITIGATING,
        review_date=date(2026, 12, 1),
    )

    assert entry.risk_id == "RISK-001"
    assert entry.controls == ("Output guardrail cross-check against enterprise API",)


def test_risk_register_entry_should_default_controls_to_empty() -> None:
    entry = RiskRegisterEntry(
        risk_id="RISK-002",
        capability="Affiliation Agent",
        cause="x",
        impact="y",
        likelihood=Likelihood.LOW,
        severity=GovernanceRiskLevel.LOW,
        owner="ai-platform",
        residual_risk=GovernanceRiskLevel.LOW,
        mitigation="none needed",
        status=RiskStatus.OPEN,
        review_date=date(2026, 12, 1),
    )

    assert entry.controls == ()
