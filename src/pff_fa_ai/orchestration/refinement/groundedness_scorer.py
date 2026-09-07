from __future__ import annotations

from pff_fa_ai.guardrails.groundedness import GroundednessEvidence, check_groundedness
from pff_fa_ai.orchestration.refinement.models import QualityScore

GROUNDEDNESS_DIMENSION = "groundedness"


class GroundednessQualityScorer:
    """ADR-D3-28 §8 — the real, deterministic `groundedness` dimension of the runtime
    refinement loop's `QualityScorer`, replacing the `MockQualityScorer` word-overlap stub
    for that dimension. It reuses the same `check_groundedness` engine the OUTPUT guardrail
    runs (ADR-D3-22 §91), so a candidate that fabricates an amount, link or reference id
    scores 0 on `groundedness` and the controller regenerates/escalates rather than
    committing it.

    The turn's authoritative `GroundednessEvidence` is supplied at construction because the
    `QualityScorer` protocol's `score(text, dimensions, reference)` signature carries no
    evidence parameter — the same closure-over-state pattern `ScriptedQualityScorer` uses.
    This scorer only owns the `groundedness` dimension; persona/schema/LLM-judge dimensions
    are scored by their own scorers and combined by a composite aggregator (future work),
    so any other requested dimension is left for those to fill."""

    def __init__(self, evidence: GroundednessEvidence) -> None:
        self._evidence = evidence

    async def score(
        self, *, text: str, dimensions: tuple[str, ...], reference: str | None
    ) -> QualityScore:
        if GROUNDEDNESS_DIMENSION not in dimensions:
            return QualityScore()
        report = check_groundedness(answer=text, evidence=self._evidence)
        return QualityScore(dimension_scores={GROUNDEDNESS_DIMENSION: report.score})
