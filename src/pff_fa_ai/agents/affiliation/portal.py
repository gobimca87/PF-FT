from __future__ import annotations

from pff_fa_ai.agents.affiliation.dependencies import AffiliationDependencies
from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.portal_links.models import LinkRequest, ResolvedLink
from pff_fa_ai.portal_links.states import LinkResolutionStatus


def resolve_affiliation_portal_links(
    deps: AffiliationDependencies, *, claims: ClaimsContext, club_id: str, application_id: str
) -> tuple[ResolvedLink, ...]:
    """doc 12 §25-28: `URL = Portal Base URL + Registered Route + Validated
    Parameters` — the resolver is the only thing allowed to build these URLs; a failed
    resolution (doc 12 §55/§104) is simply omitted, never replaced with a fabricated
    link."""
    requests = (
        LinkRequest(
            portal_id="club-portal",
            route_id="affiliation_application_status",
            parameters={"clubId": club_id},
            organization_id=claims.organization,
        ),
        LinkRequest(
            portal_id="club-portal",
            route_id="affiliation_payment",
            parameters={"clubId": club_id, "applicationId": application_id},
            organization_id=claims.organization,
        ),
    )
    links: list[ResolvedLink] = []
    for request in requests:
        result = deps.portal_resolver.resolve(request)
        if result.status is LinkResolutionStatus.ACTIVE and result.link is not None:
            links.append(result.link)
    return tuple(links)
