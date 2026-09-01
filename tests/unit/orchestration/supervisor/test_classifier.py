from pff_fa_ai.orchestration.supervisor.classifier import UNKNOWN_INTENT, UnknownIntentClassifier


async def test_unknown_classifier_should_return_zero_confidence_unknown_intent() -> None:
    classification = await UnknownIntentClassifier().classify("anything at all")

    assert classification.intent == UNKNOWN_INTENT
    assert classification.confidence == 0.0
