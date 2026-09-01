from __future__ import annotations

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.governance.lifecycle import assert_valid_lifecycle_transition
from pff_fa_ai.governance.models import GovernedArtifact
from pff_fa_ai.governance.states import AiLifecycleState, GovernedArtifactType


class GovernedArtifactRegistry:
    """doc 20 §31 "AI System Inventory" — no production AI component should be
    ownerless or untracked (doc 20 §9)."""

    def __init__(self) -> None:
        self._artifacts: dict[str, GovernedArtifact] = {}

    def register(self, artifact: GovernedArtifact) -> None:
        if artifact.artifact_id in self._artifacts:
            raise ConfigurationError(
                f"Duplicate governed artifact registered: {artifact.artifact_id}"
            )
        self._artifacts[artifact.artifact_id] = artifact

    def get(self, artifact_id: str) -> GovernedArtifact | None:
        return self._artifacts.get(artifact_id)

    def by_type(self, artifact_type: GovernedArtifactType) -> tuple[GovernedArtifact, ...]:
        return tuple(
            artifact
            for artifact in self._artifacts.values()
            if artifact.artifact_type is artifact_type
        )

    def all_artifacts(self) -> tuple[GovernedArtifact, ...]:
        return tuple(self._artifacts.values())

    def transition(self, artifact_id: str, target: AiLifecycleState) -> GovernedArtifact:
        """doc 20 §29-30: moves a registered artifact to `target` only via a valid
        lifecycle transition (`governance.lifecycle`), replacing its registry entry
        with the updated (still-immutable) artifact."""
        artifact = self._artifacts.get(artifact_id)
        if artifact is None:
            raise ConfigurationError(f"Unknown governed artifact: {artifact_id}")
        assert_valid_lifecycle_transition(artifact.lifecycle_state, target)
        updated = artifact.model_copy(update={"lifecycle_state": target})
        self._artifacts[artifact_id] = updated
        return updated
