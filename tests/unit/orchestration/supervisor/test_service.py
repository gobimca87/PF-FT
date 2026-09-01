from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.orchestration.supervisor.models import AgentCapability, IntentClassification
from pff_fa_ai.orchestration.supervisor.registry import AgentRegistry
from pff_fa_ai.orchestration.supervisor.service import Supervisor
from pff_fa_ai.orchestration.supervisor.states import SupervisorStatus

CLAIMS = ClaimsContext(subject="user-1", organization="club-1")


class _FixedClassifier:
    def __init__(self, intent: str, confidence: float) -> None:
        self._intent = intent
        self._confidence = confidence

    async def classify(self, message: str) -> IntentClassification:
        return IntentClassification(intent=self._intent, confidence=self._confidence)


def _capability() -> AgentCapability:
    return AgentCapability(
        agent_id="affiliation_agent",
        agent_version="1.0.0",
        workflow="affiliation",
        supported_intents=("club_affiliation",),
    )


async def test_should_fail_routing_when_no_capability_matches_the_intent() -> None:
    supervisor = Supervisor(AgentRegistry(), _FixedClassifier("club_affiliation", 0.95))

    decision = await supervisor.route(user_message="help with affiliation", claims=CLAIMS)

    assert decision.status is SupervisorStatus.ROUTING_FAILED
    assert decision.agent_id is None


async def test_should_request_clarification_below_confidence_threshold() -> None:
    registry = AgentRegistry()
    registry.register(_capability())
    supervisor = Supervisor(registry, _FixedClassifier("club_affiliation", 0.4))

    decision = await supervisor.route(user_message="something vague", claims=CLAIMS)

    assert decision.status is SupervisorStatus.CLARIFICATION_REQUIRED
    assert decision.clarification_required is True


async def test_should_route_to_the_matching_agent_above_threshold() -> None:
    registry = AgentRegistry()
    registry.register(_capability())
    supervisor = Supervisor(registry, _FixedClassifier("club_affiliation", 0.95))

    decision = await supervisor.route(user_message="help with affiliation", claims=CLAIMS)

    assert decision.status is SupervisorStatus.ROUTED
    assert decision.agent_id == "affiliation_agent"
    assert decision.workflow == "affiliation"
