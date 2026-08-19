from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from pf_ft_ai.common.exceptions import GuardrailError
from pf_ft_ai.evaluation.states import JudgeDimension, NonJudgeableDimension

# doc 21 §61: an LLM judge must never be the *sole* evaluator for these — always require
# a deterministic assertion or human review alongside it.
_NON_JUDGEABLE_VALUES = frozenset(dimension.value for dimension in NonJudgeableDimension)


def assert_judge_not_sole_evaluator(dimension: str) -> None:
    if dimension in _NON_JUDGEABLE_VALUES:
        raise GuardrailError(
            f"An LLM judge must never be the sole evaluator for '{dimension}' (doc 21 §61) "
            "— pair it with a deterministic assertion or human review",
            details={"dimension": dimension},
        )


class JudgeConfiguration(BaseModel):
    """doc 21 §62 judge model governance."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: str
    model_version: str
    rubric_id: str


class JudgeVerdict(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    dimension: JudgeDimension
    score: float = Field(ge=0, le=1)
    rationale: str


class Judge(Protocol):
    async def evaluate(
        self, *, dimension: JudgeDimension, response_text: str, reference_text: str | None
    ) -> JudgeVerdict: ...


class MockJudge:
    """Deterministic judge for tests/evaluation-pipeline development — required for the
    same reason `MockSLMProvider`/`MockEmbeddingProvider` are (doc 15/14): reproducible
    results without a live model call. Scores 1.0 when the reference text's words are a
    subset of the response's words, degrading proportionally otherwise."""

    async def evaluate(
        self, *, dimension: JudgeDimension, response_text: str, reference_text: str | None
    ) -> JudgeVerdict:
        if not reference_text:
            return JudgeVerdict(dimension=dimension, score=0.5, rationale="No reference supplied")
        reference_words = set(reference_text.lower().split())
        response_words = set(response_text.lower().split())
        if not reference_words:
            return JudgeVerdict(dimension=dimension, score=0.5, rationale="Empty reference")
        overlap = len(reference_words & response_words) / len(reference_words)
        return JudgeVerdict(
            dimension=dimension, score=overlap, rationale=f"Reference word overlap: {overlap:.2f}"
        )


class JudgeCalibrationResult(BaseModel):
    """doc 21 §63 — compares judge verdicts against human-reviewed cases."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agreement: int = Field(ge=0)
    disagreement: int = Field(ge=0)
    false_acceptance: int = Field(ge=0)
    false_rejection: int = Field(ge=0)

    @property
    def total(self) -> int:
        return self.agreement + self.disagreement

    @property
    def agreement_rate(self) -> float:
        return self.agreement / self.total if self.total else 0.0


def calibrate_judge(
    *, judge_scores: list[float], human_scores: list[float], pass_threshold: float
) -> JudgeCalibrationResult:
    if len(judge_scores) != len(human_scores):
        raise GuardrailError(
            "Judge calibration requires equal-length judge and human score lists",
            details={"judge_count": len(judge_scores), "human_count": len(human_scores)},
        )
    agreement = 0
    disagreement = 0
    false_acceptance = 0
    false_rejection = 0
    for judge_score, human_score in zip(judge_scores, human_scores, strict=True):
        judge_pass = judge_score >= pass_threshold
        human_pass = human_score >= pass_threshold
        if judge_pass == human_pass:
            agreement += 1
        else:
            disagreement += 1
            if judge_pass and not human_pass:
                false_acceptance += 1
            else:
                false_rejection += 1
    return JudgeCalibrationResult(
        agreement=agreement,
        disagreement=disagreement,
        false_acceptance=false_acceptance,
        false_rejection=false_rejection,
    )
