from __future__ import annotations

from urllib.parse import quote

from pf_ft_ai.common.correlation import new_id
from pf_ft_ai.portal_links.catalog import PortalRegistry
from pf_ft_ai.portal_links.models import (
    LinkRequest,
    LinkResolutionResult,
    PortalRoute,
    ResolvedLink,
)
from pf_ft_ai.portal_links.security import assert_safe_url
from pf_ft_ai.portal_links.states import LinkResolutionStatus, PortalStatus


def _unavailable(reason_code: str) -> LinkResolutionResult:
    return LinkResolutionResult(status=LinkResolutionStatus.UNAVAILABLE, reason_code=reason_code)


def _substitute_parameters(route: PortalRoute, parameters: dict[str, str]) -> str | None:
    """Returns the resolved path, or `None` if a required parameter is missing or the
    template has an unresolved token left over (doc 12 §17/§34-35/§65)."""
    path = route.path
    for name, spec in route.parameters.items():
        token = "{" + name + "}"
        if name not in parameters:
            if spec.required:
                return None
            continue
        path = path.replace(token, quote(parameters[name], safe=""))
    if "{" in path and "}" in path:
        return None
    return path


class PortalLinkResolver:
    """doc 12 §25/§28/§54: `URL = Portal Base URL + Registered Route + Validated
    Parameters` — this is the only component allowed to construct that URL. Never
    `URL = SLM output` (doc 12 §26-27)."""

    def __init__(
        self, registry: PortalRegistry, *, environment: str, allowed_domains: frozenset[str]
    ) -> None:
        self._registry = registry
        self._environment = environment
        self._allowed_domains = allowed_domains

    def resolve(self, request: LinkRequest) -> LinkResolutionResult:
        portal = self._registry.get_portal(request.portal_id)
        if portal is None:
            return _unavailable("PORTAL_NOT_FOUND")
        if portal.status is not PortalStatus.ACTIVE:
            return _unavailable("PORTAL_NOT_ACTIVE")

        route = portal.routes.get(request.route_id)
        if route is None:
            return _unavailable("ROUTE_NOT_FOUND")
        if route.status is not PortalStatus.ACTIVE:
            return _unavailable("ROUTE_NOT_ACTIVE")

        # doc 12 §41-42: entity scope must be validated before a link is generated.
        if route.require_entity_scope and request.organization_id is None:
            return _unavailable("ENTITY_SCOPE_REQUIRED")

        base_url = portal.urls.get(self._environment)
        if not base_url:
            return _unavailable("ENVIRONMENT_NOT_CONFIGURED")

        path = _substitute_parameters(route, request.parameters)
        if path is None:
            return _unavailable("INVALID_PARAMETERS")

        url = base_url.rstrip("/") + path

        failure_reason = assert_safe_url(url, allowed_domains=self._allowed_domains)
        if failure_reason is not None:
            return _unavailable(failure_reason)

        link = ResolvedLink(
            link_id=new_id("link"),
            type=request.link_type,
            label=route.label,
            url=url,
            portal_id=portal.portal_id,
            route_id=route.route_id,
            security_classification=route.security_classification,
        )
        return LinkResolutionResult(status=LinkResolutionStatus.ACTIVE, link=link)
