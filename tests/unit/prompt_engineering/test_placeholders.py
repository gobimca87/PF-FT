import pytest

from pf_ft_ai.common.exceptions import ValidationError
from pf_ft_ai.prompt_engineering.models import FewShotExample, PromptArtifact
from pf_ft_ai.prompt_engineering.placeholders import (
    find_undeclared_placeholders,
    find_unused_variables,
    render_template,
)
from pf_ft_ai.prompt_engineering.registry import load_prompt_registry
from pf_ft_ai.prompt_engineering.states import PromptCategory, PromptRiskLevel, PromptStatus


def _artifact(template: str, variables: tuple[str, ...]) -> PromptArtifact:
    return PromptArtifact(
        id="test",
        version="1.0.0",
        type=PromptCategory.TASK,
        status=PromptStatus.DRAFT,
        owner="ai-platform",
        description="test",
        risk=PromptRiskLevel.LOW,
        template=template,
        variables=variables,
    )


def test_should_render_a_template_with_all_placeholders_supplied() -> None:
    artifact = _artifact(
        "Hello {{user_name}}, welcome to {{workflow_name}}.", ("user_name", "workflow_name")
    )

    rendered = render_template(artifact, {"user_name": "Alex", "workflow_name": "Affiliation"})

    assert rendered == "Hello Alex, welcome to Affiliation."


def test_should_raise_for_a_missing_required_placeholder() -> None:
    artifact = _artifact("Hello {{user_name}}.", ("user_name",))

    with pytest.raises(ValidationError, match="Missing required placeholder"):
        render_template(artifact, {})


def test_should_raise_when_rendering_a_template_less_artifact() -> None:
    artifact = PromptArtifact(
        id="few-shot-test",
        version="1.0.0",
        type=PromptCategory.FEW_SHOT,
        status=PromptStatus.DRAFT,
        owner="ai-platform",
        description="test",
        risk=PromptRiskLevel.LOW,
        examples=(FewShotExample(scenario="s", turns=()),),
    )

    with pytest.raises(ValidationError, match="has no template"):
        render_template(artifact, {})


def test_should_never_let_a_value_inject_a_new_placeholder_token() -> None:
    artifact = _artifact("Hello {{user_name}}.", ("user_name",))

    rendered = render_template(artifact, {"user_name": "{{malicious}}"})

    # The substituted value is treated as inert text — it is not re-scanned for tokens.
    assert rendered == "Hello {{malicious}}."


def test_find_undeclared_placeholders_should_detect_a_token_missing_from_variables() -> None:
    artifact = _artifact("Hello {{user_name}}, current step {{step}}.", ("user_name",))

    assert find_undeclared_placeholders(artifact) == frozenset({"step"})


def test_find_undeclared_placeholders_should_be_empty_when_all_tokens_are_declared() -> None:
    artifact = _artifact("Hello {{user_name}}.", ("user_name",))

    assert find_undeclared_placeholders(artifact) == frozenset()


def test_find_unused_variables_should_detect_a_declared_but_unreferenced_variable() -> None:
    artifact = _artifact("Hello {{user_name}}.", ("user_name", "unused_variable"))

    assert find_unused_variables(artifact) == frozenset({"unused_variable"})


def test_find_unused_variables_should_be_empty_when_every_variable_is_referenced() -> None:
    artifact = _artifact("Hello {{user_name}}.", ("user_name",))

    assert find_unused_variables(artifact) == frozenset()


def test_known_lint_findings_across_the_real_committed_prompt_artifacts() -> None:
    """Documents today's known lint state so a *new* regression is caught while the two
    existing DRAFT findings (platform-system, affiliation-officials-assignment-task)
    don't need fixing here — they're pre-existing content, not this phase's code."""
    registry = load_prompt_registry()

    findings = {
        artifact.id: find_unused_variables(artifact)
        for artifact in registry.all_artifacts()
        if find_unused_variables(artifact) or find_undeclared_placeholders(artifact)
    }

    assert findings == {
        "platform-system": frozenset({"organization_id", "authorization_context"}),
        "affiliation-officials-assignment-task": frozenset({"erc_context"}),
    }
    for artifact in registry.all_artifacts():
        assert find_undeclared_placeholders(artifact) == frozenset()
