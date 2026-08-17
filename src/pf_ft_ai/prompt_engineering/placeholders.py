from __future__ import annotations

import re
from collections.abc import Mapping

from pf_ft_ai.common.exceptions import ValidationError
from pf_ft_ai.prompt_engineering.models import PromptArtifact

_PLACEHOLDER_PATTERN = re.compile(r"\{\{(\w+)\}\}")


def render_template(artifact: PromptArtifact, values: Mapping[str, str]) -> str:
    """doc 16 §28-30: required placeholders must be present; runtime values only ever
    supply placeholder *values* into an approved template — they never modify it."""
    if artifact.template is None:
        raise ValidationError(f"Prompt artifact '{artifact.id}' has no template to render")
    missing = [name for name in artifact.variables if name not in values]
    if missing:
        raise ValidationError(
            f"Missing required placeholder(s) for '{artifact.id}': {', '.join(missing)}",
            details={"prompt_id": artifact.id, "missing": missing},
        )
    rendered = artifact.template
    for name in artifact.variables:
        rendered = rendered.replace("{{" + name + "}}", str(values[name]))
    return rendered


def find_undeclared_placeholders(artifact: PromptArtifact) -> frozenset[str]:
    """doc 16 §113 lint check — a `{{token}}` in the template that isn't in `variables`
    would silently render as literal text instead of being substituted."""
    if artifact.template is None:
        return frozenset()
    found = {match.group(1) for match in _PLACEHOLDER_PATTERN.finditer(artifact.template)}
    return frozenset(found - set(artifact.variables))


def find_unused_variables(artifact: PromptArtifact) -> frozenset[str]:
    """doc 16 §113 lint check — a declared variable that never appears as `{{token}}` in
    the template is dead weight (or a sign the template is missing something)."""
    if artifact.template is None:
        return frozenset(artifact.variables)
    found = {match.group(1) for match in _PLACEHOLDER_PATTERN.finditer(artifact.template)}
    return frozenset(set(artifact.variables) - found)
