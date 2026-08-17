from __future__ import annotations

from typing import Protocol

from pf_ft_ai.guardrails.models import GuardrailContext, GuardrailResult


class GuardrailPolicy(Protocol):
    """doc 18 §94."""

    async def evaluate(self, context: GuardrailContext) -> GuardrailResult: ...
