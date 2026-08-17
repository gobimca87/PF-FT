from pf_ft_ai.guardrails.models import GuardrailContext
from pf_ft_ai.guardrails.secrets import SecretDetectionPolicy, detect_secrets
from pf_ft_ai.guardrails.states import GuardrailBoundary, GuardrailDecision


def test_should_detect_an_aws_access_key() -> None:
    assert "AWS_ACCESS_KEY" in detect_secrets("key=AKIAABCDEFGHIJKLMNOP")


def test_should_detect_a_private_key_header() -> None:
    assert "PRIVATE_KEY" in detect_secrets("-----BEGIN RSA PRIVATE KEY-----\nMII...")


def test_should_detect_a_generic_api_key_assignment() -> None:
    assert "GENERIC_API_KEY" in detect_secrets('api_key: "sk-abcdefghij1234567890"')


def test_should_detect_a_bearer_token() -> None:
    assert "BEARER_TOKEN" in detect_secrets("Authorization: Bearer abcDEF123456789012345")


def test_should_detect_nothing_in_clean_text() -> None:
    assert detect_secrets("The affiliation workflow is ready for review.") == frozenset()


async def test_policy_should_block_when_a_secret_is_present() -> None:
    policy = SecretDetectionPolicy()
    context = GuardrailContext(
        boundary=GuardrailBoundary.OUTPUT, content="key=AKIAABCDEFGHIJKLMNOP"
    )

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.BLOCK
    assert "GR-SECRET-AWS_ACCESS_KEY" in result.reason_codes


async def test_policy_should_allow_clean_content() -> None:
    policy = SecretDetectionPolicy()
    context = GuardrailContext(boundary=GuardrailBoundary.OUTPUT, content="Nothing sensitive.")

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.ALLOW


async def test_policy_should_allow_when_content_is_none() -> None:
    policy = SecretDetectionPolicy()
    context = GuardrailContext(boundary=GuardrailBoundary.OUTPUT, content=None)

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.ALLOW
