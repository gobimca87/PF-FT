import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.models import RefinementSettings, RefinementTaskClassSettings
from pff_fa_ai.orchestration.refinement.models import (
    QualityScore,
    resolve_refinement_policy,
)
from pff_fa_ai.orchestration.refinement.states import OnExhaustionAction


def test_quality_score_overall_is_the_weakest_dimension() -> None:
    score = QualityScore(dimension_scores={"groundedness": 0.9, "persona": 0.4})

    assert score.overall == pytest.approx(0.4)
    assert not score.meets(0.8)
    assert score.failing_dimensions(0.8) == ("persona",)


def test_empty_score_is_treated_as_passing() -> None:
    assert QualityScore().overall == 1.0


def _settings(**overrides: object) -> RefinementSettings:
    return RefinementSettings(
        default=RefinementTaskClassSettings(),
        task_classes={"tc": RefinementTaskClassSettings(**overrides)},  # type: ignore[arg-type]
    )


def test_should_resolve_the_task_class_block_over_the_default() -> None:
    policy = resolve_refinement_policy(
        _settings(enabled=True, dimensions=("groundedness",), quality_threshold=0.9),
        task_class="tc",
    )

    assert policy.enabled
    assert policy.quality_threshold == pytest.approx(0.9)
    assert policy.dimensions == ("groundedness",)


def test_should_fall_back_to_default_for_an_unknown_task_class() -> None:
    policy = resolve_refinement_policy(_settings(), task_class="unknown")

    assert not policy.enabled  # default is opt-out


def test_should_reject_an_enabled_class_with_no_dimensions() -> None:
    with pytest.raises(ConfigurationError, match="no quality dimensions"):
        resolve_refinement_policy(_settings(enabled=True, dimensions=()), task_class="tc")


def test_should_reject_more_escalations_than_ladder_rungs() -> None:
    with pytest.raises(ConfigurationError, match="only 0 rung"):
        resolve_refinement_policy(
            _settings(enabled=True, dimensions=("q",), min_escalations=1),
            task_class="tc",
        )


def test_should_reject_a_strict_class_that_accepts_below_bar_on_exhaustion() -> None:
    with pytest.raises(ConfigurationError, match="must not accept a below-bar"):
        resolve_refinement_policy(
            _settings(
                enabled=True,
                dimensions=("q",),
                strict=True,
                escalation_ladder=("strong@1",),
                min_escalations=1,
                on_exhaustion="return_best_flagged",
            ),
            task_class="tc",
        )


def test_should_reject_a_strict_class_without_a_mandated_escalation() -> None:
    with pytest.raises(ConfigurationError, match="at least one"):
        resolve_refinement_policy(
            _settings(
                enabled=True,
                dimensions=("q",),
                strict=True,
                escalation_ladder=("strong@1",),
                min_escalations=0,
                on_exhaustion="defer_to_hil",
            ),
            task_class="tc",
        )


def test_should_reject_too_few_iterations_for_the_mandated_escalations() -> None:
    with pytest.raises(ConfigurationError, match="too few"):
        resolve_refinement_policy(
            _settings(
                enabled=True,
                dimensions=("q",),
                escalation_ladder=("a@1", "b@1"),
                min_escalations=2,
                max_refinement_iterations=1,
            ),
            task_class="tc",
        )


def test_should_accept_a_valid_strict_class() -> None:
    policy = resolve_refinement_policy(
        _settings(
            enabled=True,
            dimensions=("groundedness", "safety"),
            strict=True,
            escalation_ladder=("strong@1",),
            min_escalations=1,
            max_refinement_iterations=3,
            on_exhaustion="defer_to_hil",
        ),
        task_class="tc",
    )

    assert policy.strict
    assert policy.on_exhaustion is OnExhaustionAction.DEFER_TO_HIL
