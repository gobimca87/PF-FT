from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_slm_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS


def test_should_load_slm_configuration_from_the_real_config_repository() -> None:
    config = load_slm_configuration("dev")

    assert config.slm.provider == "mock"
    assert config.slm.max_output_tokens == 1024
    assert config.retry.max_attempts == 3
    assert config.circuit_breaker.failure_threshold == 5


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_slm_configuration_for_every_declared_environment(environment: str) -> None:
    config = load_slm_configuration(environment)  # type: ignore[arg-type]

    assert config.slm.max_output_tokens > 0


def test_should_fail_fast_when_slm_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "slm.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "slm.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_slm_configuration("dev", config_root=root)
