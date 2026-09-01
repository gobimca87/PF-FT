import pytest

from pff_fa_ai.common.exceptions import GuardrailError
from pff_fa_ai.evaluation.judge import MockJudge, assert_judge_not_sole_evaluator, calibrate_judge
from pff_fa_ai.evaluation.states import JudgeDimension, NonJudgeableDimension


@pytest.mark.parametrize("dimension", list(NonJudgeableDimension))
def test_assert_judge_not_sole_evaluator_should_reject_every_non_judgeable_dimension(
    dimension: NonJudgeableDimension,
) -> None:
    with pytest.raises(GuardrailError, match="must never be the sole evaluator"):
        assert_judge_not_sole_evaluator(dimension.value)


@pytest.mark.parametrize("dimension", list(JudgeDimension))
def test_assert_judge_not_sole_evaluator_should_allow_every_judgeable_dimension(
    dimension: JudgeDimension,
) -> None:
    assert_judge_not_sole_evaluator(dimension.value)


async def test_mock_judge_should_score_full_overlap_as_one() -> None:
    judge = MockJudge()

    verdict = await judge.evaluate(
        dimension=JudgeDimension.RELEVANCE,
        response_text="the club affiliation was submitted successfully",
        reference_text="the club affiliation was submitted",
    )

    assert verdict.score == 1.0


async def test_mock_judge_should_score_partial_overlap_proportionally() -> None:
    judge = MockJudge()

    verdict = await judge.evaluate(
        dimension=JudgeDimension.RELEVANCE,
        response_text="the club affiliation",
        reference_text="the club affiliation was submitted",
    )

    assert verdict.score == pytest.approx(3 / 5)


async def test_mock_judge_should_return_midpoint_score_for_a_whitespace_only_reference() -> None:
    judge = MockJudge()

    verdict = await judge.evaluate(
        dimension=JudgeDimension.CLARITY, response_text="anything", reference_text="   "
    )

    assert verdict.score == 0.5


async def test_mock_judge_should_return_midpoint_score_for_missing_reference() -> None:
    judge = MockJudge()

    verdict = await judge.evaluate(
        dimension=JudgeDimension.CLARITY, response_text="anything", reference_text=None
    )

    assert verdict.score == 0.5


def test_calibrate_judge_should_count_full_agreement() -> None:
    result = calibrate_judge(judge_scores=[0.9, 0.2], human_scores=[0.9, 0.1], pass_threshold=0.5)

    assert result.agreement == 2
    assert result.disagreement == 0
    assert result.agreement_rate == 1.0


def test_calibrate_judge_should_classify_false_acceptance() -> None:
    result = calibrate_judge(judge_scores=[0.9], human_scores=[0.1], pass_threshold=0.5)

    assert result.false_acceptance == 1
    assert result.false_rejection == 0


def test_calibrate_judge_should_classify_false_rejection() -> None:
    result = calibrate_judge(judge_scores=[0.1], human_scores=[0.9], pass_threshold=0.5)

    assert result.false_rejection == 1
    assert result.false_acceptance == 0


def test_calibrate_judge_should_reject_mismatched_length_lists() -> None:
    with pytest.raises(GuardrailError, match="equal-length"):
        calibrate_judge(judge_scores=[0.9, 0.1], human_scores=[0.9], pass_threshold=0.5)


def test_calibrate_judge_agreement_rate_should_be_zero_for_no_scores() -> None:
    result = calibrate_judge(judge_scores=[], human_scores=[], pass_threshold=0.5)

    assert result.agreement_rate == 0.0
