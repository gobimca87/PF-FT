from __future__ import annotations

from enum import StrEnum


class PromptTrustTier(StrEnum):
    """Role hierarchy (doc 27 §66, enforced end-to-end starting Phase 11)."""

    SYSTEM = "SYSTEM"
    DEVELOPER_POLICY = "DEVELOPER_POLICY"
    AGENT_INSTRUCTIONS = "AGENT_INSTRUCTIONS"
    TOOL_CONTRACT = "TOOL_CONTRACT"
    USER_MESSAGE = "USER_MESSAGE"
    HISTORICAL_USER_CONTENT = "HISTORICAL_USER_CONTENT"


_TRUST_ORDER: tuple[PromptTrustTier, ...] = (
    PromptTrustTier.SYSTEM,
    PromptTrustTier.DEVELOPER_POLICY,
    PromptTrustTier.AGENT_INSTRUCTIONS,
    PromptTrustTier.TOOL_CONTRACT,
    PromptTrustTier.USER_MESSAGE,
    PromptTrustTier.HISTORICAL_USER_CONTENT,
)


def is_more_trusted(first: PromptTrustTier, second: PromptTrustTier) -> bool:
    return _TRUST_ORDER.index(first) < _TRUST_ORDER.index(second)
