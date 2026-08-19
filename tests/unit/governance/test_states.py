from pf_ft_ai.governance.states import (
    AiLifecycleState,
    GovernanceRiskLevel,
    GovernedArtifactType,
)
from pf_ft_ai.prompt_engineering.states import PromptRiskLevel


def test_ai_lifecycle_state_should_have_the_eleven_documented_states() -> None:
    """doc 20 §11 / DEVELOPMENT-GUIDE Phase 21: IDEA through CHANGE/RETIRE."""
    assert {state.value for state in AiLifecycleState} == {
        "IDEA",
        "ASSESS",
        "DESIGN",
        "BUILD",
        "VALIDATE",
        "APPROVE",
        "DEPLOY",
        "MONITOR",
        "REVIEW",
        "CHANGE",
        "RETIRE",
    }


def test_governed_artifact_type_should_match_the_phase_21_named_scope() -> None:
    """DEVELOPMENT-GUIDE Phase 21: "for the platform and for each governed artifact
    (prompts, models, MCP servers)"."""
    assert {t.value for t in GovernedArtifactType} == {
        "PLATFORM",
        "PROMPT",
        "MODEL",
        "MCP_SERVER",
    }


def test_governance_risk_level_should_reuse_prompt_risk_level() -> None:
    assert GovernanceRiskLevel is PromptRiskLevel
