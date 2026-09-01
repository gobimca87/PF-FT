from pff_fa_ai.guardrails.models import GuardrailContext
from pff_fa_ai.guardrails.pii import PiiDetectionPolicy, detect_pii
from pff_fa_ai.guardrails.states import GuardrailBoundary, GuardrailDecision


def test_should_detect_an_email_address() -> None:
    assert detect_pii("Contact me at alex@example.com please.") == frozenset({"EMAIL"})


def test_should_detect_a_phone_number() -> None:
    assert "PHONE" in detect_pii("Call 0161 496 0123 for details.")


def test_should_detect_nothing_in_clean_text() -> None:
    assert detect_pii("The affiliation workflow is ready for review.") == frozenset()


async def test_policy_should_warn_when_pii_is_present() -> None:
    policy = PiiDetectionPolicy()
    context = GuardrailContext(boundary=GuardrailBoundary.OUTPUT, content="alex@example.com")

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.WARN
    assert "GR-PII-EMAIL" in result.reason_codes


async def test_policy_should_allow_clean_content() -> None:
    policy = PiiDetectionPolicy()
    context = GuardrailContext(boundary=GuardrailBoundary.OUTPUT, content="No personal data here.")

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.ALLOW


async def test_policy_should_allow_when_content_is_none() -> None:
    policy = PiiDetectionPolicy()
    context = GuardrailContext(boundary=GuardrailBoundary.OUTPUT, content=None)

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.ALLOW
