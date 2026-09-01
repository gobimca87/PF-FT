from pff_fa_ai.agents.affiliation.classifier import AffiliationIntentClassifier
from pff_fa_ai.orchestration.supervisor.classifier import UNKNOWN_INTENT


async def test_should_classify_an_affiliation_status_question() -> None:
    classifier = AffiliationIntentClassifier()

    result = await classifier.classify("What's the status of my club's affiliation?")

    assert result.intent == "affiliation_status"
    assert result.confidence > 0.7


async def test_should_classify_an_affiliation_payment_question() -> None:
    classifier = AffiliationIntentClassifier()

    result = await classifier.classify("I need to pay my affiliation invoice")

    assert result.intent == "affiliation_payment"


async def test_should_return_unknown_for_an_unrelated_message() -> None:
    classifier = AffiliationIntentClassifier()

    result = await classifier.classify("What's the weather like today?")

    assert result.intent == UNKNOWN_INTENT
    assert result.confidence == 0.0
