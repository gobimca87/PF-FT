import pytest

from pf_ft_ai.common.exceptions import GuardrailError
from pf_ft_ai.guardrails.trust import (
    PromptTrustTier,
    assert_no_privilege_escalation,
    is_more_trusted,
)


def test_should_rank_system_above_user_message() -> None:
    assert is_more_trusted(PromptTrustTier.SYSTEM, PromptTrustTier.USER_MESSAGE) is True


def test_should_rank_historical_user_content_as_least_trusted() -> None:
    for tier in PromptTrustTier:
        if tier is PromptTrustTier.HISTORICAL_USER_CONTENT:
            continue
        assert is_more_trusted(tier, PromptTrustTier.HISTORICAL_USER_CONTENT) is True


def test_should_not_treat_a_tier_as_more_trusted_than_itself() -> None:
    assert is_more_trusted(PromptTrustTier.SYSTEM, PromptTrustTier.SYSTEM) is False


def test_should_reject_content_declaring_a_more_trusted_tier_than_its_source() -> None:
    with pytest.raises(GuardrailError, match="refusing to escalate privilege"):
        assert_no_privilege_escalation(
            declared=PromptTrustTier.TOOL_CONTRACT, verified_source=PromptTrustTier.USER_MESSAGE
        )


def test_should_allow_content_declaring_a_tier_at_or_below_its_verified_source() -> None:
    assert_no_privilege_escalation(
        declared=PromptTrustTier.USER_MESSAGE, verified_source=PromptTrustTier.USER_MESSAGE
    )
    assert_no_privilege_escalation(
        declared=PromptTrustTier.HISTORICAL_USER_CONTENT,
        verified_source=PromptTrustTier.USER_MESSAGE,
    )
