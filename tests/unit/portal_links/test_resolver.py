from pf_ft_ai.portal_links.catalog import PortalRegistry
from pf_ft_ai.portal_links.models import LinkRequest, Portal, PortalRoute
from pf_ft_ai.portal_links.resolver import PortalLinkResolver
from pf_ft_ai.portal_links.states import LinkResolutionStatus, PortalStatus

_ALLOWED_DOMAINS = frozenset({"club-dev.example.com"})


def _registry(
    *,
    portal_status: PortalStatus = PortalStatus.ACTIVE,
    route_status: PortalStatus = PortalStatus.ACTIVE,
    require_entity_scope: bool = True,
) -> PortalRegistry:
    registry = PortalRegistry()
    registry.register(
        Portal(
            portal_id="club-portal",
            name="Club Portal",
            domain="club",
            owner="enterprise-club",
            status=portal_status,
            urls={"dev": "https://club-dev.example.com"},
            routes={
                "club.details": PortalRoute(
                    route_id="club.details",
                    version="1.0.0",
                    path="/clubs/{clubId}",
                    label="Open Club",
                    status=route_status,
                    require_entity_scope=require_entity_scope,
                    parameters={"clubId": {"source": "erc.club.id", "required": True}},  # type: ignore[dict-item]
                )
            },
        )
    )
    return registry


def _resolver(**kwargs: object) -> PortalLinkResolver:
    return PortalLinkResolver(
        _registry(**kwargs),  # type: ignore[arg-type]
        environment="dev",
        allowed_domains=_ALLOWED_DOMAINS,
    )


def test_should_resolve_a_valid_link() -> None:
    resolver = _resolver()

    result = resolver.resolve(
        LinkRequest(
            portal_id="club-portal",
            route_id="club.details",
            parameters={"clubId": "club-123"},
            organization_id="club-123",
        )
    )

    assert result.status is LinkResolutionStatus.ACTIVE
    assert result.link is not None
    assert result.link.url == "https://club-dev.example.com/clubs/club-123"
    assert result.link.label == "Open Club"


def test_should_url_encode_path_parameters() -> None:
    resolver = _resolver()

    result = resolver.resolve(
        LinkRequest(
            portal_id="club-portal",
            route_id="club.details",
            parameters={"clubId": "club 123/x"},
            organization_id="club-123",
        )
    )

    assert result.status is LinkResolutionStatus.ACTIVE
    assert result.link is not None
    assert "club%20123%2Fx" in result.link.url


def test_should_reject_an_unknown_portal() -> None:
    resolver = _resolver()

    result = resolver.resolve(LinkRequest(portal_id="unknown-portal", route_id="club.details"))

    assert result.status is LinkResolutionStatus.UNAVAILABLE
    assert result.reason_code == "PORTAL_NOT_FOUND"
    assert result.link is None


def test_should_reject_an_unknown_route() -> None:
    resolver = _resolver()

    result = resolver.resolve(LinkRequest(portal_id="club-portal", route_id="unknown-route"))

    assert result.reason_code == "ROUTE_NOT_FOUND"


def test_should_reject_a_disabled_portal() -> None:
    resolver = _resolver(portal_status=PortalStatus.DISABLED)

    result = resolver.resolve(LinkRequest(portal_id="club-portal", route_id="club.details"))

    assert result.reason_code == "PORTAL_NOT_ACTIVE"


def test_should_reject_a_deprecated_route() -> None:
    resolver = _resolver(route_status=PortalStatus.DEPRECATED)

    result = resolver.resolve(LinkRequest(portal_id="club-portal", route_id="club.details"))

    assert result.reason_code == "ROUTE_NOT_ACTIVE"


def test_should_reject_missing_entity_scope_when_required() -> None:
    resolver = _resolver()

    result = resolver.resolve(
        LinkRequest(
            portal_id="club-portal", route_id="club.details", parameters={"clubId": "club-123"}
        )
    )

    assert result.reason_code == "ENTITY_SCOPE_REQUIRED"


def test_should_allow_missing_entity_scope_when_not_required() -> None:
    resolver = _resolver(require_entity_scope=False)

    result = resolver.resolve(
        LinkRequest(
            portal_id="club-portal", route_id="club.details", parameters={"clubId": "club-123"}
        )
    )

    assert result.status is LinkResolutionStatus.ACTIVE


def test_should_reject_an_unconfigured_environment() -> None:
    registry = _registry()
    resolver = PortalLinkResolver(registry, environment="prod", allowed_domains=_ALLOWED_DOMAINS)

    result = resolver.resolve(
        LinkRequest(
            portal_id="club-portal",
            route_id="club.details",
            parameters={"clubId": "club-123"},
            organization_id="club-123",
        )
    )

    assert result.reason_code == "ENVIRONMENT_NOT_CONFIGURED"


def test_should_reject_a_missing_required_parameter() -> None:
    resolver = _resolver()

    result = resolver.resolve(
        LinkRequest(portal_id="club-portal", route_id="club.details", organization_id="club-123")
    )

    assert result.reason_code == "INVALID_PARAMETERS"


def test_should_reject_a_domain_that_is_not_allowlisted() -> None:
    resolver = PortalLinkResolver(
        _registry(), environment="dev", allowed_domains=frozenset({"other.example.com"})
    )

    result = resolver.resolve(
        LinkRequest(
            portal_id="club-portal",
            route_id="club.details",
            parameters={"clubId": "club-123"},
            organization_id="club-123",
        )
    )

    assert result.reason_code == "DOMAIN_NOT_ALLOWLISTED"


def test_should_report_invalid_parameters_when_an_optional_path_token_is_omitted() -> None:
    """Path templates have no syntax for a truly optional segment, so omitting even a
    non-required parameter leaves an unresolved `{token}` in the path — documented
    current behavior, not silently swallowed."""
    registry = PortalRegistry()
    registry.register(
        Portal(
            portal_id="club-portal",
            name="Club Portal",
            domain="club",
            owner="enterprise-club",
            status=PortalStatus.ACTIVE,
            urls={"dev": "https://club-dev.example.com"},
            routes={
                "club.details": PortalRoute(
                    route_id="club.details",
                    version="1.0.0",
                    path="/clubs/{clubId}/{tab}",
                    label="Open Club",
                    require_entity_scope=False,
                    parameters={
                        "clubId": {"source": "erc.club.id", "required": True},  # type: ignore[dict-item]
                        "tab": {"source": "request.tab", "required": False},  # type: ignore[dict-item]
                    },
                )
            },
        )
    )
    resolver = PortalLinkResolver(registry, environment="dev", allowed_domains=_ALLOWED_DOMAINS)

    result = resolver.resolve(
        LinkRequest(
            portal_id="club-portal", route_id="club.details", parameters={"clubId": "club-123"}
        )
    )

    assert result.reason_code == "INVALID_PARAMETERS"


def test_the_slm_can_only_ever_select_portal_id_and_route_id() -> None:
    """doc 12 §26-27: the SLM selects `route_id`/`entity_id`; it never supplies a URL —
    `LinkRequest` has no `url` field at all, so there is no path for one to sneak in."""
    assert "url" not in LinkRequest.model_fields
