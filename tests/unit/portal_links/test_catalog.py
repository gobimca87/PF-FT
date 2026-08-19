from pathlib import Path

import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.portal_links.catalog import PortalRegistry, load_portal_catalog
from pf_ft_ai.portal_links.models import Portal, PortalRoute
from pf_ft_ai.portal_links.states import PortalStatus


def _portal(portal_id: str = "club-portal") -> Portal:
    return Portal(
        portal_id=portal_id,
        name="Club Portal",
        domain="club",
        owner="enterprise-club",
        status=PortalStatus.ACTIVE,
        urls={"dev": "https://club-dev.example.com"},
        routes={
            "club.details": PortalRoute(
                route_id="club.details", version="1.0.0", path="/clubs/{clubId}", label="Open Club"
            )
        },
    )


def test_should_register_and_fetch_a_portal() -> None:
    registry = PortalRegistry()
    registry.register(_portal())

    portal = registry.get_portal("club-portal")

    assert portal is not None
    assert portal.name == "Club Portal"


def test_should_fetch_a_route_from_a_registered_portal() -> None:
    registry = PortalRegistry()
    registry.register(_portal())

    route = registry.get_route("club-portal", "club.details")

    assert route is not None
    assert route.path == "/clubs/{clubId}"


def test_should_return_none_for_an_unknown_portal_or_route() -> None:
    registry = PortalRegistry()
    registry.register(_portal())

    assert registry.get_portal("unknown") is None
    assert registry.get_route("club-portal", "unknown-route") is None
    assert registry.get_route("unknown-portal", "club.details") is None


def test_should_reject_a_duplicate_portal_registration() -> None:
    registry = PortalRegistry()
    registry.register(_portal())

    with pytest.raises(ConfigurationError, match="Duplicate portal"):
        registry.register(_portal())


def test_load_portal_catalog_should_return_empty_registry_for_missing_directory(
    tmp_path: Path,
) -> None:
    registry = load_portal_catalog(tmp_path / "does-not-exist")

    assert registry.all_portals() == ()


def test_load_portal_catalog_should_load_yaml_files(tmp_path: Path) -> None:
    (tmp_path / "club.yaml").write_text(
        "portal_id: club-portal\nname: Club Portal\ndomain: club\nowner: enterprise-club\n"
        "status: ACTIVE\nurls:\n  dev: https://club-dev.example.com\n"
        "routes:\n  club.details:\n    route_id: club.details\n    version: 1.0.0\n"
        "    path: /clubs/{clubId}\n    label: Open Club\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("not yaml", encoding="utf-8")

    registry = load_portal_catalog(tmp_path)

    assert len(registry.all_portals()) == 1
    assert registry.get_portal("club-portal") is not None


def test_load_portal_catalog_should_skip_an_empty_yaml_file(tmp_path: Path) -> None:
    (tmp_path / "empty.yaml").write_text("", encoding="utf-8")

    registry = load_portal_catalog(tmp_path)

    assert registry.all_portals() == ()


def test_load_portal_catalog_should_raise_a_sanitized_error_for_invalid_content(
    tmp_path: Path,
) -> None:
    (tmp_path / "broken.yaml").write_text(
        "portal_id: broken\nname: Broken\ndomain: club\n",  # missing required fields
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="Invalid portal catalog entry"):
        load_portal_catalog(tmp_path)


def test_the_real_portals_directory_should_contain_the_phase_23_club_portal() -> None:
    """Phase 23 populated config/portals/affiliation.yaml — see its README for why
    the hostnames inside it are still TODO placeholders pending a real PFF hostname."""
    registry = load_portal_catalog()

    assert {portal.portal_id for portal in registry.all_portals()} == {"club-portal"}
