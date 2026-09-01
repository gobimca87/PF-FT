from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError as PydanticValidationError

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.common.validation import format_validation_error
from pff_fa_ai.prompt_engineering.models import PromptArtifact
from pff_fa_ai.prompt_engineering.states import PromptStatus

PROMPTS_ROOT = Path(__file__).resolve().parents[3] / "prompts"


class PromptRegistry:
    """doc 16 §87 — `get_active`/`get_version`, backed by an in-process index."""

    def __init__(self) -> None:
        self._artifacts: dict[tuple[str, str], PromptArtifact] = {}

    def register(self, artifact: PromptArtifact) -> None:
        # doc 16 §169: never allow multiple conflicting copies of the same identity.
        key = (artifact.id, artifact.version)
        if key in self._artifacts:
            raise ConfigurationError(
                f"Duplicate prompt artifact registered: {artifact.id}@{artifact.version}"
            )
        self._artifacts[key] = artifact

    def get_version(self, prompt_id: str, version: str) -> PromptArtifact:
        try:
            return self._artifacts[(prompt_id, version)]
        except KeyError as exc:
            raise ConfigurationError(f"Prompt not found: {prompt_id}@{version}") from exc

    def get_active(self, prompt_id: str) -> PromptArtifact:
        active = [
            artifact
            for (pid, _version), artifact in self._artifacts.items()
            if pid == prompt_id and artifact.status is PromptStatus.ACTIVE
        ]
        if not active:
            raise ConfigurationError(f"No ACTIVE version registered for prompt: {prompt_id}")
        if len(active) > 1:
            raise ConfigurationError(f"Multiple ACTIVE versions registered for prompt: {prompt_id}")
        return active[0]

    def all_artifacts(self) -> tuple[PromptArtifact, ...]:
        return tuple(self._artifacts.values())


def load_prompt_registry(directory: Path | None = None) -> PromptRegistry:
    root = directory or PROMPTS_ROOT
    registry = PromptRegistry()
    if not root.is_dir():
        return registry
    for path in sorted(root.rglob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not raw:
            continue
        try:
            artifact = PromptArtifact.model_validate(raw)
        except PydanticValidationError as exc:
            raise ConfigurationError(
                f"Invalid prompt artifact in {path}: {format_validation_error(exc)}"
            ) from exc
        registry.register(artifact)
    return registry
