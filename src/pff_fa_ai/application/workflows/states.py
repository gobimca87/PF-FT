from __future__ import annotations

from enum import StrEnum


class OrchestrationStatus(StrEnum):
    """Response states the Chat UI may see (doc 4 §42)."""

    COMPLETED = "COMPLETED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    WAITING_FOR_EXTERNAL_EVENT = "WAITING_FOR_EXTERNAL_EVENT"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    FAILED = "FAILED"
