from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from pff_fa_ai.context.erc.states import ErcAuthority


class Provenance(BaseModel):
    model_config = ConfigDict(frozen=True)

    system: str
    api: str
    endpoint_ref: str
    retrieved_at: datetime
    authority: ErcAuthority
