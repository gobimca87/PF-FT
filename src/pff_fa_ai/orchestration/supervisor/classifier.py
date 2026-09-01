from __future__ import annotations

from typing import Protocol

from pff_fa_ai.orchestration.supervisor.models import IntentClassification

UNKNOWN_INTENT = "unknown"


class IntentClassifier(Protocol):
    async def classify(self, message: str) -> IntentClassification: ...


class UnknownIntentClassifier:
    """Honest default until Phase 9/10 wire real SLM-based intent interpretation."""

    async def classify(self, message: str) -> IntentClassification:
        return IntentClassification(intent=UNKNOWN_INTENT, confidence=0.0)
