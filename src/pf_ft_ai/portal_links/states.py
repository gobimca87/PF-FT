from __future__ import annotations

from enum import StrEnum


class PortalStatus(StrEnum):
    """doc 12 §11."""

    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    MAINTENANCE = "MAINTENANCE"
    DISABLED = "DISABLED"


class RouteSecurityClassification(StrEnum):
    """doc 12 §44."""

    PUBLIC = "PUBLIC"
    AUTHENTICATED = "AUTHENTICATED"
    AUTHORIZED = "AUTHORIZED"
    SENSITIVE = "SENSITIVE"
    HIGH_RISK = "HIGH_RISK"


class LinkType(StrEnum):
    """doc 12 §71."""

    PORTAL = "portal"
    ENTITY = "entity"
    WORKFLOW = "workflow"
    TASK = "task"
    EXTERNAL = "external"
    TEMPORARY = "temporary"


class LinkResolutionStatus(StrEnum):
    """doc 12 §55/§95/§132 — the top-level outcome of a resolution attempt."""

    ACTIVE = "ACTIVE"
    UNAVAILABLE = "UNAVAILABLE"
