from __future__ import annotations

from pff_fa_ai.guardrails.models import GuardrailContext, GuardrailResult
from pff_fa_ai.guardrails.states import GuardrailDecision, GuardrailSeverity


class ModelAllowlistPolicy:
    """doc 18 §72-75: a model ID not in the approved registry is BLOCKed, never silently
    routed to an arbitrary provider/model."""

    guardrail_id = "model-allowlist"
    guardrail_version = "1.0.0"

    def __init__(self, approved_model_ids: frozenset[str]) -> None:
        self._approved_model_ids = approved_model_ids

    async def evaluate(self, context: GuardrailContext) -> GuardrailResult:
        model_id = context.metadata.get("model_id")
        if not model_id or model_id not in self._approved_model_ids:
            return GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                guardrail_id=self.guardrail_id,
                guardrail_version=self.guardrail_version,
                reason_codes=("GR-MODEL-001",),
                severity=GuardrailSeverity.CRITICAL,
            )
        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            guardrail_id=self.guardrail_id,
            guardrail_version=self.guardrail_version,
            severity=GuardrailSeverity.INFO,
        )
