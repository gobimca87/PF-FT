from __future__ import annotations

from collections.abc import Mapping

from pf_ft_ai.common.exceptions import GuardrailError
from pf_ft_ai.prompt_engineering.models import ComposedPrompt, PromptSection
from pf_ft_ai.prompt_engineering.states import PromptSectionRole, PromptTrustLevel

# doc 16 §5 — the fixed composition order (DEVELOPMENT-GUIDE Phase 10). Only sections
# actually supplied are included; the order among supplied sections is never reordered.
_SECTION_ORDER: tuple[PromptSectionRole, ...] = (
    PromptSectionRole.PLATFORM_SYSTEM,
    PromptSectionRole.SECURITY_GUARDRAIL,
    PromptSectionRole.AGENT_PERSONA,
    PromptSectionRole.WORKFLOW_TASK,
    PromptSectionRole.TOOL_API_INSTRUCTIONS,
    PromptSectionRole.DATA_CONTEXT,
    PromptSectionRole.USER_REQUEST,
    PromptSectionRole.MODEL_OUTPUT_REQUIREMENTS,
)

# doc 16 §6 assigns each role to exactly one trust bucket. An exact match is required —
# not just a ceiling on DATA_CONTEXT/USER_REQUEST — because a mismatch in *either*
# direction means the section was mislabeled: a role that's supposed to carry approved
# TRUSTED/CONTROLLED instructions but arrives labeled UNTRUSTED would otherwise still
# occupy that privileged position in the composed prompt (doc 16 §201).
_REQUIRED_TRUST: dict[PromptSectionRole, PromptTrustLevel] = {
    PromptSectionRole.PLATFORM_SYSTEM: PromptTrustLevel.TRUSTED,
    PromptSectionRole.SECURITY_GUARDRAIL: PromptTrustLevel.TRUSTED,
    PromptSectionRole.AGENT_PERSONA: PromptTrustLevel.CONTROLLED,
    PromptSectionRole.WORKFLOW_TASK: PromptTrustLevel.CONTROLLED,
    PromptSectionRole.TOOL_API_INSTRUCTIONS: PromptTrustLevel.TRUSTED,
    PromptSectionRole.DATA_CONTEXT: PromptTrustLevel.UNTRUSTED,
    PromptSectionRole.USER_REQUEST: PromptTrustLevel.UNTRUSTED,
    PromptSectionRole.MODEL_OUTPUT_REQUIREMENTS: PromptTrustLevel.CONTROLLED,
}


class PromptComposer:
    """doc 16 §21-23: deterministic composition in the fixed order, with a hard guardrail
    against a section occupying a privileged position under the wrong trust label."""

    def compose(self, sections: Mapping[PromptSectionRole, PromptSection]) -> ComposedPrompt:
        ordered: list[PromptSection] = []
        for role in _SECTION_ORDER:
            section = sections.get(role)
            if section is None:
                continue
            if section.role is not role:
                raise GuardrailError(
                    f"Section supplied under role '{role}' declares role '{section.role}'",
                    details={"expected_role": role, "declared_role": section.role},
                )
            required = _REQUIRED_TRUST[role]
            if section.trust_level is not required:
                raise GuardrailError(
                    f"Section '{role}' must carry '{required}' trust, got "
                    f"'{section.trust_level}' (doc 16 §6, §201)",
                    details={
                        "role": role,
                        "required_trust": required,
                        "got_trust": section.trust_level,
                    },
                )
            ordered.append(section)
        return ComposedPrompt(sections=tuple(ordered))
