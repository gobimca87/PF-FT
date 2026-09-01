from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_portal_link_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS


def test_should_load_portal_link_configuration_from_the_real_config_repository() -> None:
    config = load_portal_link_configuration("dev")

    assert config.link_policy.max_links_per_response == 10
    # Phase 23 populated the placeholder Club Portal hostnames — see
    # config/portals/affiliation.yaml and its README for why they're TODO placeholders.
    assert "portal-dev.pff.example" in config.link_policy.allowed_domains


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_portal_link_configuration_for_every_declared_environment(
    environment: str,
) -> None:
    config = load_portal_link_configuration(environment)  # type: ignore[arg-type]

    assert config.link_policy.max_links_per_response == 10


def test_should_fail_fast_when_link_policy_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "portal-links.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "portal-links.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_portal_link_configuration("dev", config_root=root)
