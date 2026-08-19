from pathlib import Path

import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.configuration.loader import load_agents_configuration
from pf_ft_ai.configuration.models import ALLOWED_ENVIRONMENTS


def test_should_load_agents_configuration_from_the_real_config_repository() -> None:
    config = load_agents_configuration("dev")

    assert config.affiliation.enterprise_base_url == "https://enterprise.pff.example"
    assert config.affiliation.team_official_batch_size == 20
    assert "affiliation_status" in config.affiliation.supported_intents


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_agents_configuration_for_every_declared_environment(
    environment: str,
) -> None:
    config = load_agents_configuration(environment)  # type: ignore[arg-type]

    assert config.configuration_hash


def test_should_fail_fast_when_affiliation_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "agents.yaml").write_text("other: {}\n", encoding="utf-8")
    (root / "environments" / "dev" / "agents.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_agents_configuration("dev", config_root=root)


def test_should_fail_fast_when_affiliation_section_is_invalid(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "agents.yaml").write_text(
        "affiliation:\n  enterprise_base_url: https://enterprise.pff.example\n"
        "  supported_intents: []\n  team_official_batch_size: not-a-number\n",
        encoding="utf-8",
    )
    (root / "environments" / "dev" / "agents.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid agents configuration"):
        load_agents_configuration("dev", config_root=root)
