from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_data_handling_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS


def test_should_load_data_handling_matrix_from_the_real_config_repository() -> None:
    config = load_data_handling_configuration("dev")

    matrix = config.data_handling.egress_matrix
    # ADR-D6-19: personal data is masked, secrets/restricted are hard-blocked.
    assert matrix["CONFIDENTIAL"].mask_required
    assert matrix["SECRET"].hard_block
    assert matrix["RESTRICTED"].hard_block
    assert not matrix["PUBLIC"].mask_required
    assert config.data_handling.self_hosted.default == "raw"


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_data_handling_for_every_declared_environment(environment: str) -> None:
    config = load_data_handling_configuration(environment)  # type: ignore[arg-type]

    assert "SECRET" in config.data_handling.egress_matrix


def test_should_fail_fast_when_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "data-handling.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "data-handling.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_data_handling_configuration("dev", config_root=root)
