from pathlib import Path

import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.configuration.loader import load_pricing_configuration
from pf_ft_ai.configuration.models import ALLOWED_ENVIRONMENTS


def test_should_load_pricing_configuration_from_the_real_config_repository() -> None:
    config = load_pricing_configuration("dev")

    assert config.version == "1.0.0"
    assert config.models["mock-slm-v1"].input_cost_per_1k == 0.0


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_pricing_configuration_for_every_declared_environment(
    environment: str,
) -> None:
    config = load_pricing_configuration(environment)  # type: ignore[arg-type]

    assert config.configuration_hash


def test_should_fail_fast_when_version_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "pricing.yaml").write_text("models: {}\n", encoding="utf-8")
    (root / "environments" / "dev" / "pricing.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_pricing_configuration("dev", config_root=root)


def test_should_default_to_an_empty_model_map_when_models_section_absent(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "pricing.yaml").write_text('version: "1.0.0"\n', encoding="utf-8")
    (root / "environments" / "dev" / "pricing.yaml").write_text("", encoding="utf-8")

    config = load_pricing_configuration("dev", config_root=root)

    assert config.models == {}


def test_should_fail_fast_when_a_model_pricing_entry_is_invalid(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "pricing.yaml").write_text(
        'version: "1.0.0"\nmodels:\n  broken-model:\n    input_cost_per_1k: not-a-number\n'
        "    output_cost_per_1k: 0.0\n",
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "pricing.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid pricing configuration"):
        load_pricing_configuration("dev", config_root=root)
