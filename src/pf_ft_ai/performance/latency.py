from __future__ import annotations

import math
import time
from collections.abc import Iterator
from contextlib import contextmanager

from pydantic import BaseModel, ConfigDict, Field

from pf_ft_ai.common.exceptions import ValidationError

# doc 26 §7: "Do not use only averages" — these are the five percentiles every
# production latency decision must be made from.
_PERCENTILES: tuple[int, ...] = (50, 75, 90, 95, 99)


class LatencySummary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    sample_count: int = Field(ge=0)
    mean_ms: float = Field(ge=0)
    p50_ms: float = Field(ge=0)
    p75_ms: float = Field(ge=0)
    p90_ms: float = Field(ge=0)
    p95_ms: float = Field(ge=0)
    p99_ms: float = Field(ge=0)


def _percentile(sorted_samples: list[float], percentile: int) -> float:
    """Nearest-rank method — simple, deterministic, no interpolation ambiguity."""
    if not sorted_samples:
        return 0.0
    rank = math.ceil((percentile / 100) * len(sorted_samples))
    index = max(rank - 1, 0)
    return sorted_samples[min(index, len(sorted_samples) - 1)]


class LatencyRecorder:
    """doc 26 §7/§16 — accumulates duration samples (milliseconds) for one measured
    stage/dependency and reports the percentile breakdown, never just an average."""

    def __init__(self) -> None:
        self._samples: list[float] = []

    def record(self, duration_ms: float) -> None:
        if duration_ms < 0:
            raise ValidationError("duration_ms must not be negative")
        self._samples.append(duration_ms)

    @contextmanager
    def measure(self) -> Iterator[None]:
        started = time.perf_counter()
        try:
            yield
        finally:
            self.record((time.perf_counter() - started) * 1000)

    def summary(self) -> LatencySummary:
        ordered = sorted(self._samples)
        mean = sum(ordered) / len(ordered) if ordered else 0.0
        return LatencySummary(
            sample_count=len(ordered),
            mean_ms=mean,
            **{f"p{p}_ms": _percentile(ordered, p) for p in _PERCENTILES},
        )


class LatencyBreakdown(BaseModel):
    """doc 26 §10-11: time-to-first-token must be tracked separately from total
    completion time — never conflated into a single "response time" number."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    time_to_first_token_ms: float | None = Field(default=None, ge=0)
    total_completion_ms: float = Field(ge=0)
    per_stage_ms: dict[str, float] = Field(default_factory=dict)

    @property
    def is_streaming(self) -> bool:
        return self.time_to_first_token_ms is not None
