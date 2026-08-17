from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pf_ft_ai.common.claims import ClaimsContext
from pf_ft_ai.guardrails.states import GuardrailBoundary, GuardrailDecision, GuardrailSeverity


class GuardrailResult(BaseModel):
    """doc 18 §10."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    decision: GuardrailDecision
    guardrail_id: str
    guardrail_version: str
    reason_codes: tuple[str, ...] = Field(default_factory=tuple)
    severity: GuardrailSeverity


class GuardrailContext(BaseModel):
    """doc 18 §96, trimmed to what's actually available at this phase."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    boundary: GuardrailBoundary
    claims: ClaimsContext | None = None
    content: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
