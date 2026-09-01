from pff_fa_ai.portal_links.link_budget import apply_link_budget
from pff_fa_ai.portal_links.models import ResolvedLink
from pff_fa_ai.portal_links.states import LinkType, RouteSecurityClassification


def _link(link_id: str, *, portal_id: str = "club-portal", url: str | None = None) -> ResolvedLink:
    return ResolvedLink(
        link_id=link_id,
        type=LinkType.ENTITY,
        label="Open Club",
        url=url or f"https://portal.example.com/clubs/{link_id}",
        portal_id=portal_id,
        route_id="club.details",
        security_classification=RouteSecurityClassification.AUTHORIZED,
    )


def test_should_cap_links_at_max_links() -> None:
    links = [_link(str(i)) for i in range(15)]

    result = apply_link_budget(links, max_links=10)

    assert len(result) == 10


def test_should_deduplicate_identical_links() -> None:
    links = [
        _link("1", url="https://portal.example.com/clubs/123"),
        _link("2", url="https://portal.example.com/clubs/123"),
    ]

    result = apply_link_budget(links, max_links=10)

    assert len(result) == 1


def test_should_preserve_order() -> None:
    links = [_link("a"), _link("b"), _link("c")]

    result = apply_link_budget(links, max_links=10)

    assert [link.link_id for link in result] == ["a", "b", "c"]


def test_should_handle_an_empty_input() -> None:
    assert apply_link_budget([], max_links=10) == ()
