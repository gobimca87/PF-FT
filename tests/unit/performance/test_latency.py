import time

import pytest

from pff_fa_ai.common.exceptions import ValidationError
from pff_fa_ai.performance.latency import LatencyBreakdown, LatencyRecorder


def test_summary_should_return_zeros_for_no_samples() -> None:
    recorder = LatencyRecorder()

    summary = recorder.summary()

    assert summary.sample_count == 0
    assert summary.mean_ms == 0.0
    assert summary.p99_ms == 0.0


def test_summary_should_compute_percentiles_over_a_known_distribution() -> None:
    recorder = LatencyRecorder()
    for value in range(1, 101):  # 1..100 ms
        recorder.record(float(value))

    summary = recorder.summary()

    assert summary.sample_count == 100
    assert summary.p50_ms == 50.0
    assert summary.p90_ms == 90.0
    assert summary.p99_ms == 99.0
    assert summary.mean_ms == pytest.approx(50.5)


def test_should_reject_a_negative_duration() -> None:
    recorder = LatencyRecorder()

    with pytest.raises(ValidationError, match="must not be negative"):
        recorder.record(-1.0)


def test_measure_context_manager_should_record_a_sample() -> None:
    recorder = LatencyRecorder()

    with recorder.measure():
        time.sleep(0.001)

    assert recorder.summary().sample_count == 1
    assert recorder.summary().p50_ms > 0


def test_latency_breakdown_should_distinguish_ttft_from_total_completion() -> None:
    breakdown = LatencyBreakdown(time_to_first_token_ms=120.0, total_completion_ms=980.0)

    assert breakdown.is_streaming is True
    assert breakdown.time_to_first_token_ms == 120.0
    assert breakdown.total_completion_ms == 980.0


def test_latency_breakdown_should_report_not_streaming_when_ttft_is_absent() -> None:
    breakdown = LatencyBreakdown(total_completion_ms=500.0)

    assert breakdown.is_streaming is False
