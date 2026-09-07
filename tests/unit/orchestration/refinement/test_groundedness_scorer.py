from pff_fa_ai.configuration.models import RefinementSettings, RefinementTaskClassSettings
from pff_fa_ai.guardrails.groundedness import GroundednessEvidence
from pff_fa_ai.orchestration.refinement.controller import QualityRefinementController
from pff_fa_ai.orchestration.refinement.groundedness_scorer import GroundednessQualityScorer
from pff_fa_ai.orchestration.refinement.models import resolve_refinement_policy
from pff_fa_ai.orchestration.refinement.states import RefinementDecision

_EVIDENCE = GroundednessEvidence(grounded_identifiers=frozenset({"£150.00"}))


async def test_a_grounded_candidate_scores_one() -> None:
    scorer = GroundednessQualityScorer(_EVIDENCE)

    score = await scorer.score(
        text="Your fee is £150.00.", dimensions=("groundedness",), reference=None
    )

    assert score.dimension_scores == {"groundedness": 1.0}


async def test_a_fabricated_candidate_scores_zero() -> None:
    scorer = GroundednessQualityScorer(_EVIDENCE)

    score = await scorer.score(
        text="Your fee is £999.99.", dimensions=("groundedness",), reference=None
    )

    assert score.dimension_scores == {"groundedness": 0.0}


async def test_a_dimension_it_does_not_own_is_left_empty() -> None:
    scorer = GroundednessQualityScorer(_EVIDENCE)

    score = await scorer.score(text="anything", dimensions=("persona", "schema"), reference=None)

    assert score.dimension_scores == {}


class _TwoShotGenerator:
    """First returns a fabricated candidate, then a grounded one — lets the loop show that
    a hallucinated amount is caught by the deterministic scorer and refined away."""

    def __init__(self) -> None:
        self._texts = ["Your fee is £999.99.", "Your fee is £150.00."]
        self.calls = 0

    async def generate(self, *, model_id: str, critique: str | None) -> str:
        text = self._texts[min(self.calls, len(self._texts) - 1)]
        self.calls += 1
        return text


async def test_the_loop_refines_away_a_hallucinated_amount() -> None:
    settings = RefinementSettings(
        task_classes={
            "tc": RefinementTaskClassSettings(
                enabled=True,
                dimensions=("groundedness",),
                quality_threshold=0.8,
                max_refinement_iterations=2,
            )
        }
    )
    policy = resolve_refinement_policy(settings, task_class="tc")
    controller = QualityRefinementController(
        policy, generator=_TwoShotGenerator(), scorer=GroundednessQualityScorer(_EVIDENCE)
    )

    outcome = await controller.run(base_model_id="base@1")

    assert outcome.decision is RefinementDecision.COMMIT
    assert outcome.final_text == "Your fee is £150.00."
    assert outcome.iterations == 1
