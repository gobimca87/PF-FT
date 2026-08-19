import pytest

from pf_ft_ai.common.exceptions import ConfigurationError, GuardrailError
from pf_ft_ai.governance.models import GovernedArtifact
from pf_ft_ai.governance.registry import GovernedArtifactRegistry
from pf_ft_ai.governance.states import AiLifecycleState, GovernanceRiskLevel, GovernedArtifactType


def _artifact(
    artifact_id: str = "prompt-1",
    artifact_type: GovernedArtifactType = GovernedArtifactType.PROMPT,
    lifecycle_state: AiLifecycleState = AiLifecycleState.IDEA,
) -> GovernedArtifact:
    return GovernedArtifact(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        name="Test artifact",
        owner="ai-platform",
        risk=GovernanceRiskLevel.MEDIUM,
        lifecycle_state=lifecycle_state,
        version="1.0.0",
    )


def test_should_register_and_fetch_an_artifact() -> None:
    registry = GovernedArtifactRegistry()
    registry.register(_artifact())

    fetched = registry.get("prompt-1")

    assert fetched is not None
    assert fetched.owner == "ai-platform"


def test_should_reject_a_duplicate_artifact_id() -> None:
    registry = GovernedArtifactRegistry()
    registry.register(_artifact())

    with pytest.raises(ConfigurationError, match="Duplicate governed artifact"):
        registry.register(_artifact())


def test_all_artifacts_should_return_every_registered_artifact() -> None:
    registry = GovernedArtifactRegistry()
    registry.register(_artifact("prompt-1", GovernedArtifactType.PROMPT))
    registry.register(_artifact("model-1", GovernedArtifactType.MODEL))

    assert {a.artifact_id for a in registry.all_artifacts()} == {"prompt-1", "model-1"}


def test_by_type_should_filter_correctly() -> None:
    registry = GovernedArtifactRegistry()
    registry.register(_artifact("prompt-1", GovernedArtifactType.PROMPT))
    registry.register(_artifact("model-1", GovernedArtifactType.MODEL))

    prompts = registry.by_type(GovernedArtifactType.PROMPT)

    assert {a.artifact_id for a in prompts} == {"prompt-1"}


def test_transition_should_advance_the_stored_artifacts_lifecycle_state() -> None:
    registry = GovernedArtifactRegistry()
    registry.register(_artifact())

    updated = registry.transition("prompt-1", AiLifecycleState.ASSESS)

    assert updated.lifecycle_state is AiLifecycleState.ASSESS
    assert registry.get("prompt-1").lifecycle_state is AiLifecycleState.ASSESS  # type: ignore[union-attr]


def test_transition_should_reject_an_invalid_target_state() -> None:
    registry = GovernedArtifactRegistry()
    registry.register(_artifact())

    with pytest.raises(GuardrailError, match="Invalid AI lifecycle transition"):
        registry.transition("prompt-1", AiLifecycleState.DEPLOY)


def test_transition_should_reject_an_unknown_artifact() -> None:
    registry = GovernedArtifactRegistry()

    with pytest.raises(ConfigurationError, match="Unknown governed artifact"):
        registry.transition("does-not-exist", AiLifecycleState.ASSESS)
