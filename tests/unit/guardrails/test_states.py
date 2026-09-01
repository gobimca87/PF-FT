from pff_fa_ai.guardrails.states import (
    GuardrailBoundary,
    GuardrailDecision,
    is_blocking,
    is_fail_open_eligible,
)


def test_block_and_escalate_should_be_blocking() -> None:
    assert is_blocking(GuardrailDecision.BLOCK)
    assert is_blocking(GuardrailDecision.ESCALATE)


def test_allow_should_not_be_blocking() -> None:
    assert not is_blocking(GuardrailDecision.ALLOW)


def test_warn_should_not_be_blocking() -> None:
    assert not is_blocking(GuardrailDecision.WARN)


def test_mandatory_fail_closed_boundaries_should_not_be_fail_open_eligible() -> None:
    for boundary in (
        GuardrailBoundary.AUTHORIZATION_CONTEXT,
        GuardrailBoundary.TOOL,
        GuardrailBoundary.MODEL,
        GuardrailBoundary.DATA,
    ):
        assert not is_fail_open_eligible(boundary)


def test_other_boundaries_should_be_fail_open_eligible() -> None:
    for boundary in (
        GuardrailBoundary.INPUT,
        GuardrailBoundary.INJECTION,
        GuardrailBoundary.PROMPT,
        GuardrailBoundary.OUTPUT,
        GuardrailBoundary.RESPONSE,
    ):
        assert is_fail_open_eligible(boundary)
