from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_evaluation_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS


def test_should_load_evaluation_configuration_from_the_real_config_repository() -> None:
    config = load_evaluation_configuration("dev")

    assert config.judge.model_id == "mock-slm-v1"
    assert config.thresholds.minimum_scores["QUALITY"] == 0.8
    assert config.thresholds.max_critical_security_failures == 0


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_evaluation_configuration_for_every_declared_environment(
    environment: str,
) -> None:
    config = load_evaluation_configuration(environment)  # type: ignore[arg-type]

    assert config.judge.rubric_id
    assert config.configuration_hash


def test_should_fail_fast_when_judge_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "evaluation.yaml").write_text(
        "thresholds:\n  minimum_scores: {}\n", encoding="utf-8"
    )
    (root / "environments" / "dev" / "evaluation.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_evaluation_configuration("dev", config_root=root)
