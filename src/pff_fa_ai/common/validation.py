from __future__ import annotations

from pydantic import ValidationError as PydanticValidationError


def format_validation_error(exc: PydanticValidationError) -> str:
    """Field location + message only — never `input` (may be a resolved secret value)."""
    parts = [
        f"{'.'.join(str(segment) for segment in error['loc'])}: {error['msg']}"
        for error in exc.errors()
    ]
    return "; ".join(parts)
