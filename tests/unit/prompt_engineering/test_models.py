import pytest
from pydantic import ValidationError as PydanticValidationError

from pff_fa_ai.prompt_engineering.models import (
    ComposedPrompt,
    DialogueTurn,
    FewShotExample,
    PromptArtifact,
    PromptSection,
)
from pff_fa_ai.prompt_engineering.states import (
    PromptCategory,
    PromptRiskLevel,
    PromptSectionRole,
    PromptStatus,
    PromptTrustLevel,
)


def test_should_construct_a_template_artifact() -> None:
    artifact = PromptArtifact(
        id="test-system",
        version="1.0.0",
        type=PromptCategory.SYSTEM,
        status=PromptStatus.DRAFT,
        owner="ai-platform",
        description="test",
        risk=PromptRiskLevel.CRITICAL,
        template="You are the platform.",
    )

    assert artifact.template == "You are the platform."


def test_should_reject_a_non_few_shot_artifact_without_a_template() -> None:
    with pytest.raises(PydanticValidationError, match="must declare a template"):
        PromptArtifact(
            id="test-task",
            version="1.0.0",
            type=PromptCategory.TASK,
            status=PromptStatus.DRAFT,
            owner="ai-platform",
            description="test",
            risk=PromptRiskLevel.LOW,
        )


def test_should_construct_a_few_shot_artifact_with_examples() -> None:
    artifact = PromptArtifact(
        id="test-few-shot",
        version="1.0.0",
        type=PromptCategory.FEW_SHOT,
        status=PromptStatus.DRAFT,
        owner="ai-platform",
        description="test",
        risk=PromptRiskLevel.LOW,
        examples=(
            FewShotExample(
                scenario="greeting",
                turns=(DialogueTurn(role="assistant", content="Hello!"),),
            ),
        ),
    )

    assert artifact.examples[0].scenario == "greeting"


def test_should_reject_a_few_shot_artifact_without_examples() -> None:
    with pytest.raises(PydanticValidationError, match="at least one example"):
        PromptArtifact(
            id="test-few-shot",
            version="1.0.0",
            type=PromptCategory.FEW_SHOT,
            status=PromptStatus.DRAFT,
            owner="ai-platform",
            description="test",
            risk=PromptRiskLevel.LOW,
        )


def test_composed_prompt_text_should_join_sections_in_order() -> None:
    composed = ComposedPrompt(
        sections=(
            PromptSection(
                role=PromptSectionRole.PLATFORM_SYSTEM,
                trust_level=PromptTrustLevel.TRUSTED,
                content="System instructions.",
            ),
            PromptSection(
                role=PromptSectionRole.USER_REQUEST,
                trust_level=PromptTrustLevel.UNTRUSTED,
                content="What documents are required?",
            ),
        )
    )

    assert composed.text == "System instructions.\n\nWhat documents are required?"
