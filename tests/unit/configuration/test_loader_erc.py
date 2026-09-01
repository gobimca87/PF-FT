from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_erc_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS

BASE_YAML = """
erc:
  schema_version: 1.0.0

  freshness:
    default_ttl_seconds: 300

  validation:
    enforce_schema: true
    enforce_completeness: true
    enforce_referential_integrity: true
"""


def test_should_load_erc_configuration_for_a_synthetic_repository(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "erc.yaml").write_text(BASE_YAML, encoding="utf-8")
    (root / "environments" / "dev" / "erc.yaml").write_text("", encoding="utf-8")

    config = load_erc_configuration("dev", config_root=root)

    assert config.erc.schema_version == "1.0.0"
    assert config.erc.freshness.default_ttl_seconds == 300
    assert config.erc.validation.enforce_referential_integrity is True
    assert len(config.configuration_hash) == 64


def test_should_fail_fast_when_erc_config_missing_section(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "erc.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "erc.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_erc_configuration("dev", config_root=root)


def test_should_fail_fast_on_invalid_erc_config_value(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "erc.yaml").write_text(
        BASE_YAML.replace("default_ttl_seconds: 300", "default_ttl_seconds: -1"),
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "erc.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid erc configuration"):
        load_erc_configuration("dev", config_root=root)


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_every_declared_environment_from_the_real_config_repository(
    environment: str,
) -> None:
    config = load_erc_configuration(environment)  # type: ignore[arg-type]

    assert config.erc.schema_version == "1.0.0"
