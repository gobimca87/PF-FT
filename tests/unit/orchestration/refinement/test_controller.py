from pff_fa_ai.configuration.models import RefinementSettings, RefinementTaskClassSettings
from pff_fa_ai.orchestration.refinement.controller import QualityRefinementController
from pff_fa_ai.orchestration.refinement.models import (
    QualityScore,
    ResolvedRefinementPolicy,
    resolve_refinement_policy,
)
from pff_fa_ai.orchestration.refinement.scorer import ScriptedQualityScorer
from pff_fa_ai.orchestration.refinement.states import RefinementDecision


class RecordingGenerator:
    def __init__(self, texts: list[str]) -> None:
        self._texts = texts
        self.calls: list[tuple[str, str | None]] = []

    async def generate(self, *, model_id: str, critique: str | None) -> str:
        self.calls.append((model_id, critique))
        return self._texts[min(len(self.calls) - 1, len(self._texts) - 1)]


def _policy(**overrides: object) -> ResolvedRefinementPolicy:
    settings = RefinementSettings(
        task_classes={"tc": RefinementTaskClassSettings(**overrides)}  # type: ignore[arg-type]
    )
    return resolve_refinement_policy(settings, task_class="tc")


def _scorer(*values: float) -> ScriptedQualityScorer:
    return ScriptedQualityScorer([QualityScore(dimension_scores={"q": v}) for v in values])


async def test_disabled_class_is_single_shot_and_commits() -> None:
    policy = _policy(enabled=False)
    generator = RecordingGenerator(["only answer"])
    controller = QualityRefinementController(policy, generator=generator, scorer=_scorer(0.1))

    outcome = await controller.run(base_model_id="base@1")

    assert outcome.committed
    assert outcome.iterations == 0
    assert len(generator.calls) == 1


async def test_first_try_pass_commits_without_refinement() -> None:
    policy = _policy(enabled=True, dimensions=("q",), quality_threshold=0.8)
    generator = RecordingGenerator(["good"])
    controller = QualityRefinementController(policy, generator=generator, scorer=_scorer(0.9))

    outcome = await controller.run(base_model_id="base@1")

    assert outcome.decision is RefinementDecision.COMMIT
    assert outcome.iterations == 0
    assert outcome.escalations == 0
    assert generator.calls == [("base@1", None)]


async def test_regenerate_only_refines_then_commits_with_a_critique() -> None:
    policy = _policy(
        enabled=True, dimensions=("q",), quality_threshold=0.8, max_refinement_iterations=2
    )
    generator = RecordingGenerator(["weak", "better"])
    controller = QualityRefinementController(policy, generator=generator, scorer=_scorer(0.5, 0.9))

    outcome = await controller.run(base_model_id="base@1")

    assert outcome.committed
    assert outcome.iterations == 1
    assert outcome.escalations == 0
    assert generator.calls[0] == ("base@1", None)
    assert generator.calls[1][0] == "base@1"
    assert generator.calls[1][1] is not None  # a critique was supplied


async def test_escalation_moves_up_the_ladder() -> None:
    policy = _policy(
        enabled=True,
        dimensions=("q",),
        quality_threshold=0.8,
        escalation_ladder=("strong@1",),
        max_refinement_iterations=2,
    )
    generator = RecordingGenerator(["weak", "strong-answer"])
    controller = QualityRefinementController(policy, generator=generator, scorer=_scorer(0.5, 0.9))

    outcome = await controller.run(base_model_id="base@1")

    assert outcome.committed
    assert outcome.escalations == 1
    assert outcome.model_used == "strong@1"
    assert generator.calls[1][0] == "strong@1"


async def test_loop_terminates_at_the_iteration_cap() -> None:
    policy = _policy(
        enabled=True,
        dimensions=("q",),
        quality_threshold=0.8,
        max_refinement_iterations=2,
        on_exhaustion="return_best_flagged",
    )
    generator = RecordingGenerator(["a", "b", "c", "d"])
    controller = QualityRefinementController(
        policy, generator=generator, scorer=_scorer(0.5, 0.5, 0.5)
    )

    outcome = await controller.run(base_model_id="base@1")

    assert outcome.decision is RefinementDecision.EXHAUST
    assert outcome.iterations == 2
    assert len(generator.calls) == 3  # first + two refinements, never unbounded


async def test_return_best_flagged_is_usable_but_marked() -> None:
    policy = _policy(
        enabled=True,
        dimensions=("q",),
        quality_threshold=0.8,
        max_refinement_iterations=1,
        on_exhaustion="return_best_flagged",
    )
    generator = RecordingGenerator(["a", "b"])
    controller = QualityRefinementController(policy, generator=generator, scorer=_scorer(0.5, 0.6))

    outcome = await controller.run(base_model_id="base@1")

    assert outcome.flagged
    assert outcome.usable
    assert outcome.final_text == "b"  # the best-scored candidate


async def test_fail_closed_yields_no_usable_text() -> None:
    policy = _policy(
        enabled=True,
        dimensions=("q",),
        quality_threshold=0.8,
        max_refinement_iterations=1,
        on_exhaustion="fail_closed",
    )
    controller = QualityRefinementController(
        policy, generator=RecordingGenerator(["a", "b"]), scorer=_scorer(0.5)
    )

    outcome = await controller.run(base_model_id="base@1")

    assert outcome.failed_closed
    assert not outcome.usable
    assert outcome.final_text is None


async def test_strict_mode_forces_an_escalation_before_acceptance() -> None:
    policy = _policy(
        enabled=True,
        dimensions=("q",),
        quality_threshold=0.8,
        strict=True,
        escalation_ladder=("strong@1",),
        min_escalations=1,
        max_refinement_iterations=2,
        on_exhaustion="defer_to_hil",
    )
    # Base already clears the bar, but strict mode must still escalate at least once.
    generator = RecordingGenerator(["base-ok", "strong-ok"])
    controller = QualityRefinementController(
        policy, generator=generator, scorer=_scorer(0.95, 0.95)
    )

    outcome = await controller.run(base_model_id="base@1")

    assert outcome.committed
    assert outcome.escalations == 1
    assert outcome.model_used == "strong@1"


async def test_strict_mode_defers_to_hil_when_below_bar_persists() -> None:
    policy = _policy(
        enabled=True,
        dimensions=("q",),
        quality_threshold=0.9,
        strict=True,
        escalation_ladder=("strong@1",),
        min_escalations=1,
        max_refinement_iterations=1,
        on_exhaustion="defer_to_hil",
    )
    controller = QualityRefinementController(
        policy, generator=RecordingGenerator(["a", "b"]), scorer=_scorer(0.5)
    )

    outcome = await controller.run(base_model_id="base@1")

    assert outcome.deferred_to_hil
    assert not outcome.usable
