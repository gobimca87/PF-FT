from __future__ import annotations

from enum import StrEnum


class RagStatus(StrEnum):
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUESTED = "REQUESTED"
    RETRIEVING = "RETRIEVING"
    RETRIEVED = "RETRIEVED"
    NO_RESULTS = "NO_RESULTS"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


class InformationRequirement(StrEnum):
    """Doc 13 §5 — the RAG decision boundary classification."""

    CURRENT_TRANSACTIONAL = "CURRENT_TRANSACTIONAL"
    CURRENT_AUTHORITATIVE = "CURRENT_AUTHORITATIVE"
    REFERENCE_KNOWLEDGE = "REFERENCE_KNOWLEDGE"
    POLICY = "POLICY"
    HISTORICAL = "HISTORICAL"
    PROCEDURAL = "PROCEDURAL"
    DOCUMENTARY = "DOCUMENTARY"


class RetrievalRoute(StrEnum):
    """Doc 13 §5 recommended routing outcome."""

    ENTERPRISE_API = "ENTERPRISE_API"
    RAG = "RAG"
    BOTH = "BOTH"


class SourceAuthorityLevel(StrEnum):
    """Doc 13 §10 — untrusted sources must never be used as authoritative evidence."""

    AUTHORITATIVE = "AUTHORITATIVE"
    CONTROLLED_REFERENCE = "CONTROLLED_REFERENCE"
    REFERENCE = "REFERENCE"
    UNTRUSTED = "UNTRUSTED"


class DocumentLifecycleStatus(StrEnum):
    """Doc 13 §79 — only appropriate states should be searchable."""

    ACTIVE = "ACTIVE"
    DRAFT = "DRAFT"
    SUPERSEDED = "SUPERSEDED"
    RETIRED = "RETIRED"
    QUARANTINED = "QUARANTINED"
