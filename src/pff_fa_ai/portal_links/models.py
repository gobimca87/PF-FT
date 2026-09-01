from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.portal_links.states import (
    LinkResolutionStatus,
    LinkType,
    PortalStatus,
    RouteSecurityClassification,
)


class RouteParameter(BaseModel):
    """doc 12 §17/§65 — never substituted from arbitrary user text."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: str
    required: bool = True


class PortalRoute(BaseModel):
    """doc 12 §14/§125."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    route_id: str
    version: str
    path: str
    label: str
    parameters: dict[str, RouteParameter] = Field(default_factory=dict)
    security_classification: RouteSecurityClassification = RouteSecurityClassification.AUTHORIZED
    require_entity_scope: bool = True
    status: PortalStatus = PortalStatus.ACTIVE


class Portal(BaseModel):
    """doc 12 §6/§64/§124."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    portal_id: str
    name: str
    domain: str
    owner: str
    status: PortalStatus
    # doc 12 §7: base URLs come from environment configuration, never hard-coded.
    urls: dict[str, str] = Field(default_factory=dict)
    routes: dict[str, PortalRoute] = Field(default_factory=dict)


class LinkRequest(BaseModel):
    """doc 12 §28 `PortalLinkResolver.resolve()` input."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    portal_id: str
    route_id: str
    link_type: LinkType = LinkType.ENTITY
    parameters: dict[str, str] = Field(default_factory=dict)
    organization_id: str | None = None


class ResolvedLink(BaseModel):
    """doc 12 §68-69 UI link metadata — structured, never a bare string."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    link_id: str
    type: LinkType
    label: str
    url: str
    portal_id: str
    route_id: str
    security_classification: RouteSecurityClassification


class LinkResolutionResult(BaseModel):
    """doc 12 §55/§104: a failed resolution never fails the whole chat response — it
    returns `UNAVAILABLE` with a reason code, never a fabricated URL."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: LinkResolutionStatus
    reason_code: str | None = None
    link: ResolvedLink | None = None
