from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_performance_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS


def test_should_load_performance_configuration_from_the_real_config_repository() -> None:
    config = load_performance_configuration("dev")

    assert config.concurrency.max_workflows == 50
    assert config.default_budget.token_budget == 8000
    assert config.default_budget.latency_budget_ms["slm"] == 5000


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_performance_configuration_for_every_declared_environment(
    environment: str,
) -> None:
    config = load_performance_configuration(environment)  # type: ignore[arg-type]

    assert config.default_budget.cost_budget > 0
    assert config.configuration_hash


def test_should_fail_fast_when_concurrency_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "performance.yaml").write_text(
        "default_budget:\n  token_budget: 1\n  model_call_budget: 1\n"
        "  tool_call_budget: 1\n  cost_budget: 1.0\n",
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "performance.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_performance_configuration("dev", config_root=root)


def test_should_fail_fast_when_concurrency_section_is_invalid(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "performance.yaml").write_text(
        "concurrency:\n  max_workflows: not-a-number\n  max_api_calls: 1\n"
        "  max_tool_calls: 1\n  max_model_calls: 1\n"
        "default_budget:\n  token_budget: 1\n  model_call_budget: 1\n"
        "  tool_call_budget: 1\n  cost_budget: 1.0\n",
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "performance.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid performance configuration"):
        load_performance_configuration("dev", config_root=root)
