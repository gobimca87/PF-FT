from pf_ft_ai.performance.benchmark import (
    run_erc_batching_benchmark,
    run_slm_heavy_benchmark,
    run_tool_heavy_benchmark,
)
from pf_ft_ai.performance.states import LoadTestProfile
from pf_ft_ai.slm.models import SlmRequest, SlmResponse
from pf_ft_ai.slm.providers import MockSLMProvider


class _FlakySlmProvider(MockSLMProvider):
    def __init__(self) -> None:
        super().__init__()
        self._call_count = 0

    async def generate(self, request: SlmRequest) -> SlmResponse:
        self._call_count += 1
        if self._call_count % 2 == 0:
            raise RuntimeError("simulated provider failure")
        return await super().generate(request)


def test_erc_batching_benchmark_should_succeed_for_100_plus_teams() -> None:
    result = run_erc_batching_benchmark(137, iterations=5)

    assert result.scenario == "erc_batching_137_entities"
    assert result.profile is LoadTestProfile.BASELINE
    assert result.success_count == 5
    assert result.failure_count == 0
    assert result.success_rate == 1.0
    assert result.latency.sample_count == 5


def test_erc_batching_benchmark_should_succeed_for_100_plus_officials() -> None:
    result = run_erc_batching_benchmark(143, batch_size=20, iterations=3)

    assert result.success_rate == 1.0


def test_erc_batching_benchmark_should_report_failures_for_a_dropped_collection() -> None:
    result = run_erc_batching_benchmark(137, iterations=4, drop_last_n=2)

    assert result.failure_count == 4
    assert result.success_count == 0
    assert result.success_rate == 0.0


async def test_slm_heavy_benchmark_should_record_a_sample_per_request() -> None:
    result = await run_slm_heavy_benchmark(provider=MockSLMProvider(), request_count=10)

    assert result.scenario == "slm_heavy"
    assert result.success_count == 10
    assert result.failure_count == 0
    assert result.latency.sample_count == 10


async def test_slm_heavy_benchmark_should_count_provider_exceptions_as_failures() -> None:
    result = await run_slm_heavy_benchmark(provider=_FlakySlmProvider(), request_count=10)

    assert result.success_count == 5
    assert result.failure_count == 5
    assert result.latency.sample_count == 10


async def test_tool_heavy_benchmark_should_record_success_and_failure_outcomes() -> None:
    call_count = 0

    async def flaky_call() -> bool:
        nonlocal call_count
        call_count += 1
        return call_count % 2 == 0

    result = await run_tool_heavy_benchmark(call=flaky_call, call_count=10, concurrency=2)

    assert result.scenario == "tool_heavy"
    assert result.success_count + result.failure_count == 10
    assert result.latency.sample_count == 10


async def test_tool_heavy_benchmark_should_treat_a_raised_exception_as_failure() -> None:
    async def always_raises() -> bool:
        raise RuntimeError("dependency unavailable")

    result = await run_tool_heavy_benchmark(call=always_raises, call_count=3)

    assert result.failure_count == 3
    assert result.success_count == 0
