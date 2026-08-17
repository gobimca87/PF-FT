from __future__ import annotations

from pf_ft_ai.guardrails.trust import PromptTrustTier
from pf_ft_ai.prompt_engineering.states import PromptTrustLevel

# doc 16 §6's coarse TRUSTED/CONTROLLED/UNTRUSTED classification is this phase's authority
# for prompt composition; it groups doc 27 §66's finer six-tier role hierarchy (already
# built in guardrails/trust.py) rather than replacing it — the finer tiers remain the
# authority for the per-role guardrail enforcement doc 27 describes.
_TIER_TO_LEVEL: dict[PromptTrustTier, PromptTrustLevel] = {
    PromptTrustTier.SYSTEM: PromptTrustLevel.TRUSTED,
    PromptTrustTier.DEVELOPER_POLICY: PromptTrustLevel.TRUSTED,
    PromptTrustTier.TOOL_CONTRACT: PromptTrustLevel.TRUSTED,
    PromptTrustTier.AGENT_INSTRUCTIONS: PromptTrustLevel.CONTROLLED,
    PromptTrustTier.USER_MESSAGE: PromptTrustLevel.UNTRUSTED,
    PromptTrustTier.HISTORICAL_USER_CONTENT: PromptTrustLevel.UNTRUSTED,
}


def classify_trust_level(tier: PromptTrustTier) -> PromptTrustLevel:
    return _TIER_TO_LEVEL[tier]
