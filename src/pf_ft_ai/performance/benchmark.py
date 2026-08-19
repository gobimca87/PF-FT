from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable

from pydantic import BaseModel, ConfigDict, Field

from pf_ft_ai.context.collection.aggregator import aggregate_records
from pf_ft_ai.context.collection.batching import split_into_batches
from pf_ft_ai.performance.latency import LatencyRecorder, LatencySummary
from pf_ft_ai.performance.states import LoadTestProfile
from pf_ft_ai.slm.models import SlmMessage, SlmRequest
from pf_ft_ai.slm.providers import SLMProvider

# doc 26 §145 "Benchmark Dataset": RAG-heavy and multi-agent scenarios are
# deliberately not benchmarked here — there is no real RAG corpus (Phase 8 ships an
# empty catalog pending real content) and no business agent exists yet
# (`AffiliationAgent` is Phase 23). ERC batching (100+ teams/officials) and SLM/Tool
# -heavy scenarios are benchmarked below because the underlying infrastructure they
# exercise is real today.


class BenchmarkResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    scenario: str
    profile: LoadTestProfile
    latency: LatencySummary
    success_count: int = Field(ge=0)
    failure_count: int = Field(ge=0)

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total else 0.0


def run_erc_batching_benchmark(
    entity_count: int, *, batch_size: int = 20, iterations: int = 20, drop_last_n: int = 0
) -> BenchmarkResult:
    """doc 26 §145 "100+ teams"/"100+ officials" scenarios — repeatedly batches and
    aggregates a synthetic entity set of the given size to produce a real percentile
    distribution, not a single wall-clock sample. `drop_last_n` simulates a partial
    collection failure (doc 26 §30 "Failures" is one of the tracked batch metrics) —
    zero by default, so a normal run is always complete."""
    recorder = LatencyRecorder()
    records = [{"id": f"entity-{i}"} for i in range(1, entity_count + 1)]
    successes = 0
    failures = 0
    for _ in range(iterations):
        with recorder.measure():
            batches = split_into_batches(entity_count, batch_size=batch_size)
            collected: list[dict[str, str]] = []
            for batch in batches:
                collected.extend(records[batch.start - 1 : batch.end])
            if drop_last_n:
                collected = collected[:-drop_last_n]
            result = aggregate_records(
                collected, key=lambda record: record["id"], expected_count=entity_count
            )
        if result.is_complete:
            successes += 1
        else:
            failures += 1
    return BenchmarkResult(
        scenario=f"erc_batching_{entity_count}_entities",
        profile=LoadTestProfile.BASELINE,
        latency=recorder.summary(),
        success_count=successes,
        failure_count=failures,
    )


async def run_slm_heavy_benchmark(
    *, provider: SLMProvider, request_count: int, model_id: str = "mock-slm-v1"
) -> BenchmarkResult:
    """doc 26 §145 "SLM-heavy request" scenario."""
    recorder = LatencyRecorder()
    successes = 0
    failures = 0
    request = SlmRequest(
        model_id=model_id,
        messages=(SlmMessage(role="user", content="Benchmark request"),),
        temperature=0.2,
        top_p=1.0,
        max_output_tokens=64,
    )
    for _ in range(request_count):
        started = time.perf_counter()
        try:
            await provider.generate(request)
        except Exception:
            failures += 1
        else:
            successes += 1
        finally:
            recorder.record((time.perf_counter() - started) * 1000)
    return BenchmarkResult(
        scenario="slm_heavy",
        profile=LoadTestProfile.LOAD,
        latency=recorder.summary(),
        success_count=successes,
        failure_count=failures,
    )


ToolCall = Callable[[], Awaitable[bool]]  # returns True on success


async def run_tool_heavy_benchmark(
    *, call: ToolCall, call_count: int, concurrency: int = 1
) -> BenchmarkResult:
    """doc 26 §145 "Tool-heavy request" scenario. `call` is caller-supplied (typically
    wrapping a real `ToolExecutor.execute()` call) so this benchmark stays independent
    of any one tool's registration/catalog setup."""
    recorder = LatencyRecorder()
    successes = 0
    failures = 0
    semaphore = asyncio.Semaphore(concurrency)

    async def run_one() -> None:
        nonlocal successes, failures
        async with semaphore:
            started = time.perf_counter()
            try:
                ok = await call()
            except Exception:
                ok = False
            finally:
                recorder.record((time.perf_counter() - started) * 1000)
            if ok:
                successes += 1
            else:
                failures += 1

    await asyncio.gather(*(run_one() for _ in range(call_count)))
    return BenchmarkResult(
        scenario="tool_heavy",
        profile=LoadTestProfile.LOAD,
        latency=recorder.summary(),
        success_count=successes,
        failure_count=failures,
    )
