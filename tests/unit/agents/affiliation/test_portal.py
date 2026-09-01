from pff_fa_ai.agents.affiliation.portal import resolve_affiliation_portal_links
from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.portal_links.catalog import load_portal_catalog
from pff_fa_ai.portal_links.resolver import PortalLinkResolver
from tests.unit.agents.affiliation.support import (
    build_test_dependencies,
    enterprise_response_handler,
)


def test_should_resolve_both_affiliation_portal_links() -> None:
    deps = build_test_dependencies(enterprise_response_handler())
    claims = ClaimsContext(subject="user-1", organization="club-1")

    links = resolve_affiliation_portal_links(
        deps, claims=claims, club_id="club-1", application_id="app-1"
    )

    route_ids = {link.route_id for link in links}
    assert route_ids == {"affiliation_application_status", "affiliation_payment"}
    for link in links:
        assert link.url.startswith("https://portal-dev.pff.example")


def test_resolved_links_should_embed_the_real_club_and_application_ids() -> None:
    deps = build_test_dependencies(enterprise_response_handler())
    claims = ClaimsContext(subject="user-1", organization="club-1")

    links = resolve_affiliation_portal_links(
        deps, claims=claims, club_id="club-42", application_id="app-99"
    )

    status_link = next(link for link in links if link.route_id == "affiliation_application_status")
    payment_link = next(link for link in links if link.route_id == "affiliation_payment")
    assert "club-42" in status_link.url
    assert "club-42" in payment_link.url
    assert "app-99" in payment_link.url


def test_a_failed_resolution_should_be_omitted_not_fabricated() -> None:
    """doc 12 §55/§104 — an un-allowlisted domain must fail resolution closed, and the
    caller must simply not get that link back, never a fabricated URL."""
    deps = build_test_dependencies(enterprise_response_handler())
    deps.portal_resolver = PortalLinkResolver(
        load_portal_catalog(), environment="dev", allowed_domains=frozenset()
    )
    claims = ClaimsContext(subject="user-1", organization="club-1")

    links = resolve_affiliation_portal_links(
        deps, claims=claims, club_id="club-1", application_id="app-1"
    )

    assert links == ()
