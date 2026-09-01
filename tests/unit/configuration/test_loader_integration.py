from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_integration_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS

BASE_YAML = """
retry:
  max_attempts: 3
  backoff: exponential
  initial_ms: 250
  max_ms: 5000
  jitter: true

circuit_breaker:
  failure_threshold: 5
  cooldown_seconds: 30
  half_open_max_calls: 1

concurrency:
  global_max: 20
  enterprise:
    max_parallel: 10
  mcp:
    max_parallel: 5

timeout:
  connect_ms: 1000
  read_ms: 10000
  total_ms: 12000
"""


def test_should_load_integration_configuration_for_a_synthetic_repository(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "integration.yaml").write_text(BASE_YAML, encoding="utf-8")
    (root / "environments" / "dev" / "integration.yaml").write_text("", encoding="utf-8")

    config = load_integration_configuration("dev", config_root=root)

    assert config.retry.max_attempts == 3
    assert config.circuit_breaker.failure_threshold == 5
    assert config.concurrency.global_max == 20
    assert config.concurrency.enterprise.max_parallel == 10
    assert config.concurrency.mcp.max_parallel == 5
    assert config.timeout.total_ms == 12000
    assert len(config.configuration_hash) == 64


def test_should_fail_fast_when_integration_config_missing_section(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "integration.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "integration.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_integration_configuration("dev", config_root=root)


def test_should_fail_fast_on_invalid_integration_config_value(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "integration.yaml").write_text(
        BASE_YAML.replace("max_attempts: 3", "max_attempts: -1"), encoding="utf-8"
    )
    (root / "environments" / "dev" / "integration.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid integration configuration"):
        load_integration_configuration("dev", config_root=root)


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_every_declared_environment_from_the_real_config_repository(
    environment: str,
) -> None:
    config = load_integration_configuration(environment)  # type: ignore[arg-type]

    assert config.retry.max_attempts == 3
