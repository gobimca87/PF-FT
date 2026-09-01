from __future__ import annotations

import re

from pff_fa_ai.guardrails.models import GuardrailContext, GuardrailResult
from pff_fa_ai.guardrails.states import GuardrailDecision, GuardrailSeverity

# doc 18 §64/§67 — the same category of heuristic scanning `detect-secrets` already runs
# over the repository, applied here to runtime prompt/output content.
_SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "AWS_ACCESS_KEY": re.compile(r"AKIA[0-9A-Z]{16}"),
    "PRIVATE_KEY": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GENERIC_API_KEY": re.compile(r"(?i)api[_-]?key[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{16,}"),
    "BEARER_TOKEN": re.compile(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]{20,}=*"),
}


def detect_secrets(text: str) -> frozenset[str]:
    return frozenset(name for name, pattern in _SECRET_PATTERNS.items() if pattern.search(text))


class SecretDetectionPolicy:
    """doc 18 §65-66: secrets must never be sent to the SLM or returned in output —
    unlike PII, a detected secret always BLOCKs, no ambiguity to defer."""

    guardrail_id = "secret-detection"
    guardrail_version = "1.0.0"

    async def evaluate(self, context: GuardrailContext) -> GuardrailResult:
        if not context.content:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                guardrail_id=self.guardrail_id,
                guardrail_version=self.guardrail_version,
                severity=GuardrailSeverity.INFO,
            )
        found = detect_secrets(context.content)
        if found:
            return GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                guardrail_id=self.guardrail_id,
                guardrail_version=self.guardrail_version,
                reason_codes=tuple(f"GR-SECRET-{category}" for category in sorted(found)),
                severity=GuardrailSeverity.CRITICAL,
            )
        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            guardrail_id=self.guardrail_id,
            guardrail_version=self.guardrail_version,
            severity=GuardrailSeverity.INFO,
        )
