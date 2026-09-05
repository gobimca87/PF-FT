from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_refinement_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS


def test_should_load_refinement_defaults_from_the_real_config_repository() -> None:
    config = load_refinement_configuration("dev")

    default = config.refinement.default
    # ADR-D3-28: additive and opt-in — disabled by default, no task classes opted in yet.
    assert not default.enabled
    assert default.on_exhaustion == "return_best_flagged"
    assert default.escalation_ladder == ()
    assert config.refinement.task_classes == {}


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_refinement_for_every_declared_environment(environment: str) -> None:
    config = load_refinement_configuration(environment)  # type: ignore[arg-type]

    assert 0.0 <= config.refinement.default.quality_threshold <= 1.0


def test_should_fail_fast_when_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "refinement.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "refinement.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_refinement_configuration("dev", config_root=root)
