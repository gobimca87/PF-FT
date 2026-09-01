from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_guardrail_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS


def test_should_load_guardrail_configuration_from_the_real_config_repository() -> None:
    config = load_guardrail_configuration("dev")

    assert "mock-slm-v1" in config.guardrail.approved_model_ids
    assert config.guardrail.fail_open_boundaries == ()


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_guardrail_configuration_for_every_declared_environment(
    environment: str,
) -> None:
    config = load_guardrail_configuration(environment)  # type: ignore[arg-type]

    assert len(config.guardrail.approved_model_ids) > 0


def test_should_fail_fast_when_guardrail_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "guardrails.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "guardrails.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_guardrail_configuration("dev", config_root=root)
