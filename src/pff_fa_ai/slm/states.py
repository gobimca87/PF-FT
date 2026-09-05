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


class SlmPlacement(StrEnum):
    """ADR-D6-19 / ADR-D6-07 — where the resolved inference endpoint runs relative to the
    Azure tenancy. Drives the masking regime: EXTERNAL is mandatory mask/tokenise
    fail-closed; SELF_HOSTED is raw-or-masked per task class."""

    EXTERNAL = "EXTERNAL"
    SELF_HOSTED = "SELF_HOSTED"
