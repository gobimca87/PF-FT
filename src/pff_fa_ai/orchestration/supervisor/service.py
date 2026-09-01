from __future__ import annotations

from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.orchestration.supervisor.classifier import IntentClassifier
from pff_fa_ai.orchestration.supervisor.models import SupervisorDecision
from pff_fa_ai.orchestration.supervisor.registry import AgentRegistry
from pff_fa_ai.orchestration.supervisor.states import SupervisorStatus

CLARIFICATION_CONFIDENCE_THRESHOLD = 0.7


class Supervisor:
    def __init__(self, registry: AgentRegistry, classifier: IntentClassifier) -> None:
        self._registry = registry
        self._classifier = classifier

    async def route(self, *, user_message: str, claims: ClaimsContext) -> SupervisorDecision:
        classification = await self._classifier.classify(user_message)
        candidates = self._registry.find_by_intent(classification.intent)

        if not candidates:
            return SupervisorDecision(
                status=SupervisorStatus.ROUTING_FAILED,
                intent=classification.intent,
                confidence=classification.confidence,
                clarification_required=False,
            )

        if classification.confidence < CLARIFICATION_CONFIDENCE_THRESHOLD:
            return SupervisorDecision(
                status=SupervisorStatus.CLARIFICATION_REQUIRED,
                intent=classification.intent,
                confidence=classification.confidence,
                clarification_required=True,
            )

        selected = candidates[0]
        return SupervisorDecision(
            status=SupervisorStatus.ROUTED,
            intent=classification.intent,
            confidence=classification.confidence,
            clarification_required=False,
            agent_id=selected.agent_id,
            workflow=selected.workflow,
        )
