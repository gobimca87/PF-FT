from __future__ import annotations

from pf_ft_ai.orchestration.supervisor.classifier import UNKNOWN_INTENT
from pf_ft_ai.orchestration.supervisor.models import IntentClassification


class AffiliationIntentClassifier:
    """doc 7 (Agentic Orchestration) / DEVELOPMENT-GUIDE Phase 23. A deterministic
    keyword classifier standing in for real SLM-based intent classification — Phase
    9/10 built the SLM/prompt layers behind interfaces only, since no model has been
    evaluation-selected yet (docs/adr/0003). This keeps the affiliation reference
    workflow reachable through the chat pipeline today; swapping in a real classifier
    later needs no change to the `IntentClassifier` protocol or the supervisor."""

    async def classify(self, message: str) -> IntentClassification:
        lowered = message.lower()
        if "affiliat" not in lowered:
            return IntentClassification(intent=UNKNOWN_INTENT, confidence=0.0)
        if "pay" in lowered or "invoice" in lowered:
            return IntentClassification(intent="affiliation_payment", confidence=0.9)
        return IntentClassification(intent="affiliation_status", confidence=0.9)
