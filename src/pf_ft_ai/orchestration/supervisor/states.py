from __future__ import annotations

from enum import StrEnum


class SupervisorStatus(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    ANALYZING = "ANALYZING"
    ROUTED = "ROUTED"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    ROUTING_FAILED = "ROUTING_FAILED"
    COMPLETED = "COMPLETED"
