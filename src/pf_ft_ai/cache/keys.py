from __future__ import annotations

import hashlib
import json
from typing import Any

_EMPTY_SEGMENT = "-"


def build_cache_key(
    *,
    tenant_id: str,
    organization_id: str | None,
    resource: str,
    operation: str,
    parameters: dict[str, Any],
    version: str,
) -> str:
    """Doc 9 §36-37 — key includes tenant + org + resource + operation + parameters + version."""
    parameters_hash = hashlib.sha256(
        json.dumps(parameters, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]
    organization_segment = organization_id or _EMPTY_SEGMENT
    return f"{tenant_id}:{organization_segment}:{resource}:{operation}:{version}:{parameters_hash}"
