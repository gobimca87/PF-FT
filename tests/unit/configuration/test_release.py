from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.release import load_release_manifest

VALID_RELEASE_YAML = """
release:
  release_id: pff-fa-ai-0.1.0
  version: 0.1.0
  environment: dev
  application_version: 0.1.0
  components: {}
"""


def test_should_load_release_manifest(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "releases").mkdir(parents=True)
    (root / "releases" / "0.1.0.yaml").write_text(VALID_RELEASE_YAML, encoding="utf-8")

    manifest = load_release_manifest("0.1.0", config_root=root)

    assert manifest.release_id == "pff-fa-ai-0.1.0"
    assert manifest.environment == "dev"
    assert manifest.components == {}


def test_should_raise_when_release_manifest_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "releases").mkdir(parents=True)

    with pytest.raises(ConfigurationError, match="Release manifest not found"):
        load_release_manifest("9.9.9", config_root=root)


def test_should_raise_when_release_manifest_invalid(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "releases").mkdir(parents=True)
    (root / "releases" / "0.2.0.yaml").write_text(
        "release:\n  release_id: pff-fa-ai-0.2.0\n", encoding="utf-8"
    )

    with pytest.raises(ConfigurationError, match="Invalid release manifest"):
        load_release_manifest("0.2.0", config_root=root)


def test_should_raise_when_release_manifest_missing_release_key(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "releases").mkdir(parents=True)
    (root / "releases" / "0.3.0.yaml").write_text("application_version: 0.3.0\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="missing top-level 'release' key"):
        load_release_manifest("0.3.0", config_root=root)


def test_should_load_real_repository_release_manifest() -> None:
    manifest = load_release_manifest("0.1.0")

    assert manifest.version == "0.1.0"
    assert manifest.environment == "dev"
