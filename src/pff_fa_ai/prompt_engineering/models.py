from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from pff_fa_ai.prompt_engineering.states import (
    PromptCategory,
    PromptRiskLevel,
    PromptSectionRole,
    PromptStatus,
    PromptTrustLevel,
)


class PromptCompatibility(BaseModel):
    """doc 16 §37-38 — matches the real artifacts' `compatibility.model: [{id: constraint}]`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    model: tuple[dict[str, str], ...] = Field(default_factory=tuple)


class DialogueTurn(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    role: Literal["system", "user", "assistant", "tool"]
    content: str


class FewShotExample(BaseModel):
    """doc 16 §46."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scenario: str
    turns: tuple[DialogueTurn, ...]


class OutputSchemaReference(BaseModel):
    """doc 16 §33/§43 — a pointer to a schema definition, not the schema itself; no
    concrete output schema has been designed yet (see prompts/schemas/README.md)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    version: str


class PromptArtifact(BaseModel):
    """doc 16 §85/§168 prompt artifact — the on-disk shape under `prompts/`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    version: str
    type: PromptCategory
    status: PromptStatus
    owner: str
    description: str
    risk: PromptRiskLevel
    compatibility: PromptCompatibility = Field(default_factory=PromptCompatibility)
    variables: tuple[str, ...] = Field(default_factory=tuple)
    template: str | None = None
    examples: tuple[FewShotExample, ...] = Field(default_factory=tuple)
    output_schema: OutputSchemaReference | None = None

    @model_validator(mode="after")
    def _validate_type_specific_payload(self) -> PromptArtifact:
        if self.type is PromptCategory.FEW_SHOT:
            if not self.examples:
                raise ValueError("A few-shot prompt artifact must declare at least one example")
        elif not self.template:
            raise ValueError(f"A '{self.type.value}' prompt artifact must declare a template")
        return self


class PromptSection(BaseModel):
    """doc 16 §21 composer input — one already-rendered slot in the fixed composition
    order, carrying the trust level of its content (doc 16 §6, §57)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    role: PromptSectionRole
    trust_level: PromptTrustLevel
    content: str


class ComposedPrompt(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    sections: tuple[PromptSection, ...]

    @property
    def text(self) -> str:
        return "\n\n".join(section.content for section in self.sections)
