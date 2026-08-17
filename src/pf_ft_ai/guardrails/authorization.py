from __future__ import annotations

from pf_ft_ai.guardrails.models import GuardrailContext, GuardrailResult
from pf_ft_ai.guardrails.states import GuardrailDecision, GuardrailSeverity


class AuthorizationContextPolicy:
    """doc 18 §33-37 — verifies identity and required scope before tool/API execution.
    Fail-closed: a missing subject or missing required permission always BLOCKs."""

    guardrail_id = "authorization-context"
    guardrail_version = "1.0.0"

    def __init__(self, *, required_permissions: frozenset[str] = frozenset()) -> None:
        self._required_permissions = required_permissions

    async def evaluate(self, context: GuardrailContext) -> GuardrailResult:
        if context.claims is None or not context.claims.subject:
            return GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                guardrail_id=self.guardrail_id,
                guardrail_version=self.guardrail_version,
                reason_codes=("GR-AUTH-001",),
                severity=GuardrailSeverity.CRITICAL,
            )
        missing = self._required_permissions - set(context.claims.permissions)
        if missing:
            return GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                guardrail_id=self.guardrail_id,
                guardrail_version=self.guardrail_version,
                reason_codes=("GR-AUTH-001",),
                severity=GuardrailSeverity.HIGH,
            )
        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            guardrail_id=self.guardrail_id,
            guardrail_version=self.guardrail_version,
            severity=GuardrailSeverity.INFO,
        )
