from __future__ import annotations

from enum import StrEnum


class ErcLifecycleStatus(StrEnum):
    """doc 8 §9-10 (authoritative for Phase 5 — supersedes the simplified doc 5 §24 sketch)."""

    NOT_CREATED = "NOT_CREATED"
    REQUIREMENTS_IDENTIFIED = "REQUIREMENTS_IDENTIFIED"
    COLLECTING = "COLLECTING"
    NORMALIZING = "NORMALIZING"
    AGGREGATING = "AGGREGATING"
    VALIDATING = "VALIDATING"
    READY = "READY"
    REFRESH_REQUIRED = "REFRESH_REQUIRED"
    REFRESHING = "REFRESHING"
    STALE = "STALE"
    INVALID = "INVALID"
    FAILED = "FAILED"


class ErcSectionStatus(StrEnum):
    NOT_REQUESTED = "NOT_REQUESTED"
    REQUESTED = "REQUESTED"
    COLLECTING = "COLLECTING"
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"
    STALE = "STALE"
    FAILED = "FAILED"


class ErcValidationStatus(StrEnum):
    """doc 8 §71."""

    VALID = "VALID"
    VALID_WITH_WARNINGS = "VALID_WITH_WARNINGS"
    INVALID = "INVALID"
    INCOMPLETE = "INCOMPLETE"
    STALE = "STALE"


class FreshnessStatus(StrEnum):
    """doc 8 §17."""

    FRESH = "FRESH"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"
    EXPIRED = "EXPIRED"


class ErcAuthority(StrEnum):
    """doc 8 §19 — highest to lowest authority."""

    AUTHORITATIVE = "AUTHORITATIVE"
    DERIVED = "DERIVED"
    AI_INTERPRETED = "AI_INTERPRETED"
    RAG_CONTEXT = "RAG_CONTEXT"
    USER_PROVIDED = "USER_PROVIDED"


_ERC_AUTHORITY_ORDER: tuple[ErcAuthority, ...] = (
    ErcAuthority.AUTHORITATIVE,
    ErcAuthority.DERIVED,
    ErcAuthority.AI_INTERPRETED,
    ErcAuthority.RAG_CONTEXT,
    ErcAuthority.USER_PROVIDED,
)


def higher_erc_authority(first: ErcAuthority, second: ErcAuthority) -> ErcAuthority:
    return (
        first if _ERC_AUTHORITY_ORDER.index(first) <= _ERC_AUTHORITY_ORDER.index(second) else second
    )
