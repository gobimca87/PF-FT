from pathlib import Path

import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.configuration.loader import load_harness_configuration
from pf_ft_ai.configuration.models import ALLOWED_ENVIRONMENTS

BASE_YAML = """
harness:
  max_graph_steps: 25
  max_agent_loops: 6
  max_tool_calls: 10
  max_parallel_calls: 5
  max_context_tokens: 20000
  max_output_tokens: 4000
  max_execution_time_seconds: 60
  max_retry_count: 3
  max_batch_size: 20
"""


def test_should_load_harness_configuration_for_a_synthetic_repository(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "harness.yaml").write_text(BASE_YAML, encoding="utf-8")
    (root / "environments" / "dev" / "harness.yaml").write_text("", encoding="utf-8")

    config = load_harness_configuration("dev", config_root=root)

    assert config.harness.max_batch_size == 20
    assert config.harness.max_execution_time_seconds == 60
    assert len(config.configuration_hash) == 64


def test_should_fail_fast_when_harness_config_missing_section(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "harness.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "harness.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_harness_configuration("dev", config_root=root)


def test_should_fail_fast_on_invalid_harness_config_value(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "harness.yaml").write_text(
        BASE_YAML.replace("max_batch_size: 20", "max_batch_size: -1"), encoding="utf-8"
    )
    (root / "environments" / "dev" / "harness.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid harness configuration"):
        load_harness_configuration("dev", config_root=root)


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_every_declared_environment_from_the_real_config_repository(
    environment: str,
) -> None:
    config = load_harness_configuration(environment)  # type: ignore[arg-type]

    assert config.harness.max_batch_size == 20
