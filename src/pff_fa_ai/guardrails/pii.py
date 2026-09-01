from __future__ import annotations

import re

from pff_fa_ai.guardrails.models import GuardrailContext, GuardrailResult
from pff_fa_ai.guardrails.states import GuardrailDecision, GuardrailSeverity

# doc 18 §61: names/free-text classification needs a real NLP model, which this platform
# doesn't have yet — these are the categories reliably detectable with pattern matching.
_PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "EMAIL": re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}"),
    "PHONE": re.compile(
        r"(?<!\d)(?:\+?\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}(?!\d)"
    ),
}


def detect_pii(text: str) -> frozenset[str]:
    return frozenset(
        category for category, pattern in _PII_PATTERNS.items() if pattern.search(text)
    )


class PiiDetectionPolicy:
    """doc 18 §61-63: detected PII WARNs by default — the actual ALLOW/MASK/REDACT/
    TOKENIZE/BLOCK/ESCALATE decision depends on enterprise data-classification policy
    this platform doesn't own yet, so this policy surfaces the finding rather than
    silently deciding an enterprise data-governance question."""

    guardrail_id = "pii-detection"
    guardrail_version = "1.0.0"

    async def evaluate(self, context: GuardrailContext) -> GuardrailResult:
        if not context.content:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                guardrail_id=self.guardrail_id,
                guardrail_version=self.guardrail_version,
                severity=GuardrailSeverity.INFO,
            )
        found = detect_pii(context.content)
        if found:
            return GuardrailResult(
                decision=GuardrailDecision.WARN,
                guardrail_id=self.guardrail_id,
                guardrail_version=self.guardrail_version,
                reason_codes=tuple(f"GR-PII-{category}" for category in sorted(found)),
                severity=GuardrailSeverity.MEDIUM,
            )
        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            guardrail_id=self.guardrail_id,
            guardrail_version=self.guardrail_version,
            severity=GuardrailSeverity.INFO,
        )
