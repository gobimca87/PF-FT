from __future__ import annotations

from enum import StrEnum


class MemoryCategory(StrEnum):
    """Doc 9 §5 — the 10 recognized memory categories."""

    CONVERSATION = "CONVERSATION"
    SESSION = "SESSION"
    WORKING = "WORKING"
    WORKFLOW = "WORKFLOW"
    AGENT_RUN = "AGENT_RUN"
    USER_PREFERENCE = "USER_PREFERENCE"
    ORGANIZATIONAL_CONTEXT = "ORGANIZATIONAL_CONTEXT"
    ERC_REFERENCE = "ERC_REFERENCE"
    DECISION = "DECISION"
    SUMMARY = "SUMMARY"


class MemoryLifecycleStatus(StrEnum):
    """Doc 9 §20 — union of the generic and workflow-memory lifecycle flows."""

    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    UPDATED = "UPDATED"
    WAITING = "WAITING"
    RESUMED = "RESUMED"
    COMPACTED = "COMPACTED"
    EXPIRED = "EXPIRED"
    COMPLETED = "COMPLETED"
    RETAINED = "RETAINED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


class MemorySourceType(StrEnum):
    """Doc 9 §70 — provenance of a memory record."""

    USER = "USER"
    ENTERPRISE_API = "ENTERPRISE_API"
    ENTERPRISE_EVENT = "ENTERPRISE_EVENT"
    WORKFLOW = "WORKFLOW"
    AI_SUMMARY = "AI_SUMMARY"
    AI_INFERENCE = "AI_INFERENCE"
    SYSTEM = "SYSTEM"


class MemoryConfidence(StrEnum):
    """Doc 9 §28-29 — trust grading; AI_INFERENCE must never be treated as authoritative."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
