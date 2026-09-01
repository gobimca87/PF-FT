import pytest

from pff_fa_ai.guardrails.trust import PromptTrustTier
from pff_fa_ai.prompt_engineering.states import PromptTrustLevel
from pff_fa_ai.prompt_engineering.trust import classify_trust_level


@pytest.mark.parametrize(
    "tier",
    [PromptTrustTier.SYSTEM, PromptTrustTier.DEVELOPER_POLICY, PromptTrustTier.TOOL_CONTRACT],
)
def test_should_classify_system_level_tiers_as_trusted(tier: PromptTrustTier) -> None:
    assert classify_trust_level(tier) is PromptTrustLevel.TRUSTED


def test_should_classify_agent_instructions_as_controlled() -> None:
    assert classify_trust_level(PromptTrustTier.AGENT_INSTRUCTIONS) is PromptTrustLevel.CONTROLLED


@pytest.mark.parametrize(
    "tier", [PromptTrustTier.USER_MESSAGE, PromptTrustTier.HISTORICAL_USER_CONTENT]
)
def test_should_classify_user_content_as_untrusted(tier: PromptTrustTier) -> None:
    assert classify_trust_level(tier) is PromptTrustLevel.UNTRUSTED
