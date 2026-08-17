from __future__ import annotations

from enum import StrEnum


class GraphNodeStatus(StrEnum):
    PENDING = "PENDING"
    READY = "READY"
    EXECUTING = "EXECUTING"
    WAITING = "WAITING"
    SUCCEEDED = "SUCCEEDED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"
