from pf_ft_ai.prompt_engineering.states import PromptTrustLevel, trust_rank


def test_trusted_should_outrank_controlled() -> None:
    assert trust_rank(PromptTrustLevel.TRUSTED) > trust_rank(PromptTrustLevel.CONTROLLED)


def test_controlled_should_outrank_untrusted() -> None:
    assert trust_rank(PromptTrustLevel.CONTROLLED) > trust_rank(PromptTrustLevel.UNTRUSTED)
