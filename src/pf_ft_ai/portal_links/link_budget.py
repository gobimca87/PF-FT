from __future__ import annotations

from collections.abc import Iterable

from pf_ft_ai.portal_links.models import ResolvedLink


def apply_link_budget(links: Iterable[ResolvedLink], *, max_links: int) -> tuple[ResolvedLink, ...]:
    """doc 12 §75-76/§103: deduplicate (same portal+route+URL) then cap at `max_links` —
    100+ entities must never turn into 100+ UI links."""
    deduplicated: list[ResolvedLink] = []
    seen: set[tuple[str, str, str]] = set()
    for link in links:
        key = (link.portal_id, link.route_id, link.url)
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(link)
    return tuple(deduplicated[:max_links])
