from __future__ import annotations

from enum import StrEnum

from pf_ft_ai.common.exceptions import GuardrailError


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


def assert_no_privilege_escalation(
    *, declared: PromptTrustTier, verified_source: PromptTrustTier
) -> None:
    """doc 27 §66 role hierarchy, actually enforced starting this phase (Phase 11):
    content may never be labeled as more trusted than its actual verified origin —
    e.g. user-supplied text must never be accepted into the prompt labeled as if it
    came from a tool contract or the system itself."""
    if is_more_trusted(declared, verified_source):
        raise GuardrailError(
            f"Content declared trust tier '{declared}' but its verified source is only "
            f"'{verified_source}' — refusing to escalate privilege",
            details={"declared": declared, "verified_source": verified_source},
        )
