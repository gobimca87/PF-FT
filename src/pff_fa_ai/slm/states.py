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
    fail-closed; SELF_HOSTED and MANAGED_IN_TENANCY are raw-or-masked per task class.

    MANAGED_IN_TENANCY is the Azure AI Foundry hosted-first plane (ADR-D3-29): a managed
    Azure service, but running in-tenancy in an Azure region under the enterprise EA/DPA, so
    it carries the same in-tenancy masking posture as a self-hosted SLM rather than the
    mandatory external-egress boundary."""

    EXTERNAL = "EXTERNAL"
    SELF_HOSTED = "SELF_HOSTED"
    MANAGED_IN_TENANCY = "MANAGED_IN_TENANCY"
