"""doc 22 §61/§119-121 "Security Testing" / "Authorization Context Testing": claims must
be tamper-proof and the guardrail pipeline must fail closed on missing/insufficient
authorization and on secret leakage — exercised end-to-end through the real
`GuardrailPipeline`, not just the individual policy unit tests."""

import pytest
from pydantic import ValidationError

from pff_fa_ai.guardrails.authorization import AuthorizationContextPolicy
from pff_fa_ai.guardrails.models import GuardrailContext
from pff_fa_ai.guardrails.pipeline import GuardrailPipeline
from pff_fa_ai.guardrails.secrets import SecretDetectionPolicy
from pff_fa_ai.guardrails.states import GuardrailBoundary, GuardrailDecision
from tests.fixtures.factories import make_claims


def test_claims_context_should_be_immutable_after_issuance() -> None:
    """CLAUDE.md Golden Rule: the AI platform never authorizes itself — the claims APIM
    validated must not be alterable anywhere downstream, including by a coding mistake."""
    claims = make_claims(permissions=("club.read",))

    with pytest.raises(ValidationError):
        claims.permissions = ("club.write",)  # type: ignore[misc]


def _pipeline_with_authorization(required_permissions: frozenset[str]) -> GuardrailPipeline:
    pipeline = GuardrailPipeline()
    pipeline.register(
        GuardrailBoundary.AUTHORIZATION_CONTEXT,
        AuthorizationContextPolicy(required_permissions=required_permissions),
    )
    return pipeline


async def test_pipeline_should_block_a_request_with_no_authenticated_subject() -> None:
    pipeline = _pipeline_with_authorization(frozenset({"club.write"}))
    context = GuardrailContext(
        boundary=GuardrailBoundary.AUTHORIZATION_CONTEXT,
        claims=make_claims(subject="", permissions=("club.write",)),
    )

    result = await pipeline.evaluate(GuardrailBoundary.AUTHORIZATION_CONTEXT, context)

    assert result.decision is GuardrailDecision.BLOCK


async def test_pipeline_should_block_when_required_permission_is_missing() -> None:
    pipeline = _pipeline_with_authorization(frozenset({"club.write"}))
    context = GuardrailContext(
        boundary=GuardrailBoundary.AUTHORIZATION_CONTEXT,
        claims=make_claims(permissions=("club.read",)),
    )

    result = await pipeline.evaluate(GuardrailBoundary.AUTHORIZATION_CONTEXT, context)

    assert result.decision is GuardrailDecision.BLOCK


async def test_pipeline_should_allow_when_the_required_permission_is_present() -> None:
    pipeline = _pipeline_with_authorization(frozenset({"club.write"}))
    context = GuardrailContext(
        boundary=GuardrailBoundary.AUTHORIZATION_CONTEXT,
        claims=make_claims(permissions=("club.write", "club.read")),
    )

    result = await pipeline.evaluate(GuardrailBoundary.AUTHORIZATION_CONTEXT, context)

    assert result.decision is GuardrailDecision.ALLOW


async def test_pipeline_should_block_output_that_leaks_a_bearer_token() -> None:
    """doc 22 §61 "Secret handling" — a leaked credential must never reach the user,
    regardless of how it entered the model's output."""
    pipeline = GuardrailPipeline()
    pipeline.register(GuardrailBoundary.OUTPUT, SecretDetectionPolicy())
    context = GuardrailContext(
        boundary=GuardrailBoundary.OUTPUT,
        content="Here is the token: Bearer sk-live-abcdefghijklmnopqrstuvwxyz0123456789",
    )

    result = await pipeline.evaluate(GuardrailBoundary.OUTPUT, context)

    assert result.decision is GuardrailDecision.BLOCK
