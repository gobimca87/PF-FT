from pf_ft_ai.common.claims import ClaimsContext
from pf_ft_ai.guardrails.authorization import AuthorizationContextPolicy
from pf_ft_ai.guardrails.models import GuardrailContext
from pf_ft_ai.guardrails.states import GuardrailBoundary, GuardrailDecision


def _claims(*, subject: str = "user-1", permissions: tuple[str, ...] = ()) -> ClaimsContext:
    return ClaimsContext(subject=subject, organization="club-123", permissions=permissions)


async def test_should_block_when_claims_are_missing() -> None:
    policy = AuthorizationContextPolicy()
    context = GuardrailContext(boundary=GuardrailBoundary.AUTHORIZATION_CONTEXT, claims=None)

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.BLOCK
    assert "GR-AUTH-001" in result.reason_codes


async def test_should_block_when_subject_is_empty() -> None:
    policy = AuthorizationContextPolicy()
    context = GuardrailContext(
        boundary=GuardrailBoundary.AUTHORIZATION_CONTEXT, claims=_claims(subject="")
    )

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.BLOCK


async def test_should_block_when_a_required_permission_is_missing() -> None:
    policy = AuthorizationContextPolicy(required_permissions=frozenset({"affiliation:write"}))
    context = GuardrailContext(
        boundary=GuardrailBoundary.AUTHORIZATION_CONTEXT, claims=_claims(permissions=())
    )

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.BLOCK


async def test_should_allow_when_required_permissions_are_present() -> None:
    policy = AuthorizationContextPolicy(required_permissions=frozenset({"affiliation:write"}))
    context = GuardrailContext(
        boundary=GuardrailBoundary.AUTHORIZATION_CONTEXT,
        claims=_claims(permissions=("affiliation:write", "affiliation:read")),
    )

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.ALLOW
