from pathlib import Path

import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.prompt_engineering.models import PromptArtifact
from pf_ft_ai.prompt_engineering.registry import PromptRegistry, load_prompt_registry
from pf_ft_ai.prompt_engineering.states import (
    PromptCategory,
    PromptRiskLevel,
    PromptStatus,
)


def _artifact(
    *,
    prompt_id: str = "test-system",
    version: str = "1.0.0",
    status: PromptStatus = PromptStatus.DRAFT,
) -> PromptArtifact:
    return PromptArtifact(
        id=prompt_id,
        version=version,
        type=PromptCategory.SYSTEM,
        status=status,
        owner="ai-platform",
        description="test",
        risk=PromptRiskLevel.LOW,
        template="Hello.",
    )


def test_should_register_and_fetch_a_specific_version() -> None:
    registry = PromptRegistry()
    registry.register(_artifact())

    fetched = registry.get_version("test-system", "1.0.0")

    assert fetched.id == "test-system"


def test_should_reject_registering_a_duplicate_identity() -> None:
    registry = PromptRegistry()
    registry.register(_artifact())

    with pytest.raises(ConfigurationError, match="Duplicate prompt artifact"):
        registry.register(_artifact())


def test_should_raise_for_an_unknown_version() -> None:
    registry = PromptRegistry()

    with pytest.raises(ConfigurationError, match="Prompt not found"):
        registry.get_version("unknown", "1.0.0")


def test_get_active_should_raise_when_nothing_is_active() -> None:
    registry = PromptRegistry()
    registry.register(_artifact(status=PromptStatus.DRAFT))

    with pytest.raises(ConfigurationError, match="No ACTIVE version"):
        registry.get_active("test-system")


def test_get_active_should_return_the_active_version() -> None:
    registry = PromptRegistry()
    registry.register(_artifact(version="1.0.0", status=PromptStatus.DEPRECATED))
    registry.register(_artifact(version="2.0.0", status=PromptStatus.ACTIVE))

    active = registry.get_active("test-system")

    assert active.version == "2.0.0"


def test_get_active_should_reject_multiple_active_versions() -> None:
    registry = PromptRegistry()
    registry.register(_artifact(version="1.0.0", status=PromptStatus.ACTIVE))
    registry.register(_artifact(version="2.0.0", status=PromptStatus.ACTIVE))

    with pytest.raises(ConfigurationError, match="Multiple ACTIVE versions"):
        registry.get_active("test-system")


def test_load_prompt_registry_should_return_empty_registry_for_missing_directory(
    tmp_path: Path,
) -> None:
    registry = load_prompt_registry(tmp_path / "does-not-exist")

    assert registry.all_artifacts() == ()


def test_load_prompt_registry_should_load_yaml_files_recursively(tmp_path: Path) -> None:
    (tmp_path / "system").mkdir(parents=True)
    (tmp_path / "system" / "platform.system.yaml").write_text(
        "id: platform-system\nversion: 1.0.0\ntype: system\nstatus: DRAFT\n"
        "owner: ai-platform\ndescription: test\nrisk: CRITICAL\ntemplate: Hello.\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("not yaml", encoding="utf-8")

    registry = load_prompt_registry(tmp_path)

    assert len(registry.all_artifacts()) == 1
    assert registry.get_version("platform-system", "1.0.0").owner == "ai-platform"


def test_load_prompt_registry_should_skip_an_empty_yaml_file(tmp_path: Path) -> None:
    (tmp_path / "system").mkdir(parents=True)
    (tmp_path / "system" / "empty.system.yaml").write_text("", encoding="utf-8")

    registry = load_prompt_registry(tmp_path)

    assert registry.all_artifacts() == ()


def test_load_prompt_registry_should_raise_a_sanitized_error_for_invalid_content(
    tmp_path: Path,
) -> None:
    (tmp_path / "system").mkdir(parents=True)
    (tmp_path / "system" / "broken.system.yaml").write_text(
        "id: broken\nversion: 1.0.0\ntype: system\nstatus: DRAFT\n"
        "owner: ai-platform\ndescription: test\nrisk: CRITICAL\n",  # no template
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="Invalid prompt artifact"):
        load_prompt_registry(tmp_path)


def test_should_load_every_real_committed_prompt_artifact() -> None:
    """Integration check: every prompt actually committed under prompts/ must remain
    loadable by the registry — this is the contract the Python package is built against."""
    registry = load_prompt_registry()

    artifacts = registry.all_artifacts()

    assert len(artifacts) == 8
    ids = {artifact.id for artifact in artifacts}
    assert "platform-system" in ids
    assert "affiliation-assistant-persona" in ids
    assert "affiliation-dialogue-examples" in ids
    # None of the real artifacts have been promoted past DRAFT yet.
    assert all(artifact.status is PromptStatus.DRAFT for artifact in artifacts)
