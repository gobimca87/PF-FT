from __future__ import annotations

from enum import StrEnum


class SlmStatus(StrEnum):
    REQUESTED = "REQUESTED"
    QUEUED = "QUEUED"
    EXECUTING = "EXECUTING"
    SUCCEEDED = "SUCCEEDED"
    RETRYING = "RETRYING"
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"
    FALLBACK = "FALLBACK"
    BLOCKED = "BLOCKED"


class ProviderHealthStatus(StrEnum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
