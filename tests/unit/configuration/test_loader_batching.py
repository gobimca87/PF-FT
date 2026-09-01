from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_batching_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS

BASE_YAML = """
batching:
  batch_size: 20
  max_parallel_batches: 5
  max_retry_attempts: 2
"""


def test_should_load_batching_configuration_for_a_synthetic_repository(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "batching.yaml").write_text(BASE_YAML, encoding="utf-8")
    (root / "environments" / "dev" / "batching.yaml").write_text("", encoding="utf-8")

    config = load_batching_configuration("dev", config_root=root)

    assert config.batching.batch_size == 20
    assert config.batching.max_parallel_batches == 5
    assert config.batching.max_retry_attempts == 2
    assert len(config.configuration_hash) == 64


def test_should_fail_fast_when_batching_config_missing_section(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "batching.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "batching.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_batching_configuration("dev", config_root=root)


def test_should_fail_fast_on_invalid_batching_config_value(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "batching.yaml").write_text(
        BASE_YAML.replace("batch_size: 20", "batch_size: -1"), encoding="utf-8"
    )
    (root / "environments" / "dev" / "batching.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid batching configuration"):
        load_batching_configuration("dev", config_root=root)


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_every_declared_environment_from_the_real_config_repository(
    environment: str,
) -> None:
    config = load_batching_configuration(environment)  # type: ignore[arg-type]

    assert config.batching.batch_size == 20
