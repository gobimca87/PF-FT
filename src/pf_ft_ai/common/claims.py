from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ClaimsContext(BaseModel):
    """Validated identity claims forwarded by APIM/enterprise auth (CLAUDE.md Golden Rule)."""

    model_config = ConfigDict(frozen=True)

    subject: str
    organization: str
    roles: tuple[str, ...] = Field(default_factory=tuple)
    permissions: tuple[str, ...] = Field(default_factory=tuple)
    # APIM-validated token, propagated unchanged to enterprise API calls (doc 10 §72-74)
    access_token: str | None = Field(default=None, repr=False)
