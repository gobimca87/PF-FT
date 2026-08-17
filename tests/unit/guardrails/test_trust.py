from pf_ft_ai.guardrails.trust import PromptTrustTier, is_more_trusted


def test_should_rank_system_above_user_message() -> None:
    assert is_more_trusted(PromptTrustTier.SYSTEM, PromptTrustTier.USER_MESSAGE) is True


def test_should_rank_historical_user_content_as_least_trusted() -> None:
    for tier in PromptTrustTier:
        if tier is PromptTrustTier.HISTORICAL_USER_CONTENT:
            continue
        assert is_more_trusted(tier, PromptTrustTier.HISTORICAL_USER_CONTENT) is True


def test_should_not_treat_a_tier_as_more_trusted_than_itself() -> None:
    assert is_more_trusted(PromptTrustTier.SYSTEM, PromptTrustTier.SYSTEM) is False
