"""doc 22 §102 "Stub Strategy": deterministic stub payloads for boundary and large-data
conditions, shared across whichever layer needs them (contract, component, performance)
rather than each layer inventing its own large/malformed fixture."""

from __future__ import annotations

from typing import Any


def large_enterprise_list_payload(count: int, *, entity_type: str = "team") -> dict[str, Any]:
    """doc 22 §127 "Large Data Testing" — a 100+ entity enterprise API response shape."""
    return {
        "total": count,
        "items": [
            {"id": f"{entity_type}-{index}", "type": entity_type, "status": "ACTIVE"}
            for index in range(1, count + 1)
        ],
    }


MALFORMED_JSON_BODY = '{"clubId": "club-123", "status": '  # truncated mid-value
