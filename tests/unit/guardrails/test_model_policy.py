from pff_fa_ai.guardrails.model_policy import ModelAllowlistPolicy
from pff_fa_ai.guardrails.models import GuardrailContext
from pff_fa_ai.guardrails.states import GuardrailBoundary, GuardrailDecision


async def test_should_allow_an_approved_model() -> None:
    policy = ModelAllowlistPolicy(frozenset({"mock-slm-v1"}))
    context = GuardrailContext(
        boundary=GuardrailBoundary.MODEL, metadata={"model_id": "mock-slm-v1"}
    )

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.ALLOW


async def test_should_block_an_unapproved_model() -> None:
    policy = ModelAllowlistPolicy(frozenset({"mock-slm-v1"}))
    context = GuardrailContext(
        boundary=GuardrailBoundary.MODEL, metadata={"model_id": "unapproved-model"}
    )

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.BLOCK
    assert "GR-MODEL-001" in result.reason_codes


async def test_should_block_when_model_id_is_missing() -> None:
    policy = ModelAllowlistPolicy(frozenset({"mock-slm-v1"}))
    context = GuardrailContext(boundary=GuardrailBoundary.MODEL, metadata={})

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.BLOCK
