from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError as PydanticValidationError

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.common.validation import format_validation_error
from pff_fa_ai.portal_links.models import Portal, PortalRoute

PORTALS_ROOT = Path(__file__).resolve().parents[3] / "config" / "portals"


class PortalRegistry:
    """doc 12 §29/§129 — portal_id/route_id uniqueness enforced at registration."""

    def __init__(self) -> None:
        self._portals: dict[str, Portal] = {}

    def register(self, portal: Portal) -> None:
        if portal.portal_id in self._portals:
            raise ConfigurationError(f"Duplicate portal registered: {portal.portal_id}")
        self._portals[portal.portal_id] = portal

    def get_portal(self, portal_id: str) -> Portal | None:
        return self._portals.get(portal_id)

    def get_route(self, portal_id: str, route_id: str) -> PortalRoute | None:
        portal = self._portals.get(portal_id)
        if portal is None:
            return None
        return portal.routes.get(route_id)

    def all_portals(self) -> tuple[Portal, ...]:
        return tuple(self._portals.values())


def load_portal_catalog(directory: Path | None = None) -> PortalRegistry:
    root = directory or PORTALS_ROOT
    registry = PortalRegistry()
    if not root.is_dir():
        return registry
    for path in sorted(root.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not raw:
            continue
        try:
            portal = Portal.model_validate(raw)
        except PydanticValidationError as exc:
            raise ConfigurationError(
                f"Invalid portal catalog entry in {path}: {format_validation_error(exc)}"
            ) from exc
        registry.register(portal)
    return registry
