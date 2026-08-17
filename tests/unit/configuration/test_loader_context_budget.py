from pathlib import Path

import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.configuration.loader import load_context_budget_configuration
from pf_ft_ai.configuration.models import ALLOWED_ENVIRONMENTS

BASE_YAML = """
context_budget:
  max_input_tokens: 20000
  reserved_output_tokens: 4000
  safety_margin_tokens: 1000
"""


def test_should_load_context_budget_configuration_for_a_synthetic_repository(
    tmp_path: Path,
) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "context-budget.yaml").write_text(BASE_YAML, encoding="utf-8")
    (root / "environments" / "dev" / "context-budget.yaml").write_text("", encoding="utf-8")

    config = load_context_budget_configuration("dev", config_root=root)

    assert config.context_budget.max_input_tokens == 20000
    assert config.context_budget.reserved_output_tokens == 4000
    assert config.context_budget.safety_margin_tokens == 1000
    assert len(config.configuration_hash) == 64


def test_should_fail_fast_when_context_budget_config_missing_section(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "context-budget.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "context-budget.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_context_budget_configuration("dev", config_root=root)


def test_should_fail_fast_on_invalid_context_budget_config_value(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "context-budget.yaml").write_text(
        BASE_YAML.replace("max_input_tokens: 20000", "max_input_tokens: -1"), encoding="utf-8"
    )
    (root / "environments" / "dev" / "context-budget.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid context budget configuration"):
        load_context_budget_configuration("dev", config_root=root)


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_every_declared_environment_from_the_real_config_repository(
    environment: str,
) -> None:
    config = load_context_budget_configuration(environment)  # type: ignore[arg-type]

    assert config.context_budget.max_input_tokens == 20000
