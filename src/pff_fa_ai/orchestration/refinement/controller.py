from __future__ import annotations

from typing import Protocol

from pff_fa_ai.orchestration.refinement.models import (
    QualityScore,
    RefinementOutcome,
    ResolvedRefinementPolicy,
)
from pff_fa_ai.orchestration.refinement.scorer import QualityScorer
from pff_fa_ai.orchestration.refinement.states import OnExhaustionAction, RefinementDecision


class CandidateGenerator(Protocol):
    """ADR-D3-28 §8 — produces a language / pre-commit decision *candidate* on a given
    model, optionally given a critique of the previous attempt. The controller only ever
    calls this; it never re-invokes an enterprise tool or a committed write (DR-C-02,
    AC-05), and it never varies temperature to mask a miss (DR-C-04, AC-06) — the critique
    is the only lever between iterations."""

    async def generate(self, *, model_id: str, critique: str | None) -> str: ...


def _build_critique(score: QualityScore, policy: ResolvedRefinementPolicy) -> str:
    failing = score.failing_dimensions(policy.quality_threshold)
    weak = ", ".join(
        f"{dimension} ({score.dimension_scores[dimension]:.2f})" for dimension in failing
    )
    return (
        "The previous attempt fell below the quality bar on: "
        f"{weak or 'overall quality'}. Improve these while keeping every factual value, "
        "enterprise status, amount, date and identifier exactly as given — do not invent "
        "or change any of them."
    )


class QualityRefinementController:
    """ADR-D3-28 §8 — the runtime quality-gated refinement loop:
    `generate → score → gate → (refine ↺ | commit)`.

    The gate is a deterministic threshold comparison against `refinement.yaml` (ADR-D3-05
    §7.4); below the bar the controller regenerates with critique and/or escalates up the
    configured model ladder (ADR-D3-15), bounded by `max_refinement_iterations`. On
    exhaustion it takes the configured `on_exhaustion` action and never silently accepts a
    below-bar output. The loop operates on language / pre-commit decision candidates only
    and is subordinate to every existing constraint — a refined output remains *data* for
    deterministic code and the enterprise to act on (ADR-D1-02), and enterprise/ERC truth
    always outranks it (ADR-D1-03).
    """

    def __init__(
        self,
        policy: ResolvedRefinementPolicy,
        *,
        generator: CandidateGenerator,
        scorer: QualityScorer,
    ) -> None:
        self._policy = policy
        self._generator = generator
        self._scorer = scorer

    async def run(self, *, base_model_id: str, reference: str | None = None) -> RefinementOutcome:
        policy = self._policy
        text = await self._generator.generate(model_id=base_model_id, critique=None)
        score = await self._score(text)

        # Disabled task class: single-shot, no gate — behaviour is unchanged from before a
        # class opts in (ADR-D3-28 §14 migration).
        if not policy.enabled:
            return RefinementOutcome(
                task_class=policy.task_class,
                final_text=text,
                decision=RefinementDecision.COMMIT,
                committed=True,
                score=score,
                iterations=0,
                escalations=0,
                model_used=base_model_id,
            )

        models = (base_model_id, *policy.escalation_ladder)
        model_index = 0
        escalations = 0
        iterations = 0
        best_text = text
        best_score = score

        while True:
            if score.overall > best_score.overall:
                best_text, best_score = text, score

            if score.meets(policy.quality_threshold) and escalations >= policy.min_escalations:
                return RefinementOutcome(
                    task_class=policy.task_class,
                    final_text=text,
                    decision=RefinementDecision.COMMIT,
                    committed=True,
                    score=score,
                    iterations=iterations,
                    escalations=escalations,
                    model_used=models[model_index],
                )

            if iterations >= policy.max_refinement_iterations:
                return self._on_exhaustion(
                    best_text=best_text,
                    best_score=best_score,
                    iterations=iterations,
                    escalations=escalations,
                    model_used=models[model_index],
                )

            iterations += 1
            critique = _build_critique(score, policy)
            if model_index + 1 < len(models):
                model_index += 1
                escalations += 1
            text = await self._generator.generate(model_id=models[model_index], critique=critique)
            score = await self._score(text)

    async def _score(self, text: str) -> QualityScore:
        return await self._scorer.score(
            text=text, dimensions=self._policy.dimensions, reference=None
        )

    def _on_exhaustion(
        self,
        *,
        best_text: str,
        best_score: QualityScore,
        iterations: int,
        escalations: int,
        model_used: str,
    ) -> RefinementOutcome:
        action = self._policy.on_exhaustion
        flagged = action == OnExhaustionAction.RETURN_BEST_FLAGGED
        deferred = action == OnExhaustionAction.DEFER_TO_HIL
        failed_closed = action == OnExhaustionAction.FAIL_CLOSED
        return RefinementOutcome(
            task_class=self._policy.task_class,
            final_text=None if failed_closed else best_text,
            decision=RefinementDecision.EXHAUST,
            flagged=flagged,
            deferred_to_hil=deferred,
            failed_closed=failed_closed,
            score=best_score,
            iterations=iterations,
            escalations=escalations,
            model_used=model_used,
        )
