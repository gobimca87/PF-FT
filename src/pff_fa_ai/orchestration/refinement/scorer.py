from __future__ import annotations

from typing import Protocol

from pff_fa_ai.orchestration.refinement.models import QualityScore


class QualityScorer(Protocol):
    """ADR-D3-28 §8 — computes a runtime quality signal for a candidate output. Reuses the
    evaluation scorers (ADR-D7-13 / ADR-D8-05): deterministic checks (groundedness against
    ERC, citation presence, schema, persona-lint) by default; a validated LLM-as-judge
    dimension only where a strict task class opts in, to keep the common path cheap. The
    scorer only produces a *signal* — the loop's controller takes the deterministic
    decision (ADR-D3-05 §7.4)."""

    async def score(
        self, *, text: str, dimensions: tuple[str, ...], reference: str | None
    ) -> QualityScore: ...


class MockQualityScorer:
    """Deterministic scorer for tests/loop development — same "mock until the real scorer
    is wired" posture as `MockSLMProvider` / `MockJudge`. Scores each dimension by the
    fraction of the reference's words present in the candidate; with no reference every
    dimension scores a neutral 0.5."""

    async def score(
        self, *, text: str, dimensions: tuple[str, ...], reference: str | None
    ) -> QualityScore:
        if reference:
            reference_words = set(reference.lower().split())
            candidate_words = set(text.lower().split())
            value = (
                len(reference_words & candidate_words) / len(reference_words)
                if reference_words
                else 0.5
            )
        else:
            value = 0.5
        return QualityScore(dimension_scores=dict.fromkeys(dimensions, value))


class ScriptedQualityScorer:
    """Returns a pre-scripted score per call, then repeats the last one — lets a test drive
    the controller through an exact refine/escalate/commit/exhaust path deterministically."""

    def __init__(self, scores: list[QualityScore]) -> None:
        if not scores:
            raise ValueError("ScriptedQualityScorer requires at least one score")
        self._scores = scores
        self._index = 0

    async def score(
        self, *, text: str, dimensions: tuple[str, ...], reference: str | None
    ) -> QualityScore:
        score = self._scores[min(self._index, len(self._scores) - 1)]
        self._index += 1
        return score
