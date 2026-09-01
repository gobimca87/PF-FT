from __future__ import annotations

import time
from collections.abc import Callable
from enum import StrEnum

from pff_fa_ai.configuration.models import CircuitBreakerSettings


class CircuitState(StrEnum):
    """doc 10 §90."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(
        self, settings: CircuitBreakerSettings, *, clock: Callable[[], float] = time.monotonic
    ) -> None:
        self._settings = settings
        self._clock = clock
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at: float | None = None
        self._half_open_calls = 0

    @property
    def state(self) -> CircuitState:
        if self._state is CircuitState.OPEN and self._cooldown_elapsed():
            self._state = CircuitState.HALF_OPEN
            self._half_open_calls = 0
        return self._state

    def allow_request(self) -> bool:
        current = self.state
        if current is CircuitState.CLOSED:
            return True
        if current is CircuitState.OPEN:
            return False
        if self._half_open_calls < self._settings.half_open_max_calls:
            self._half_open_calls += 1
            return True
        return False

    def record_success(self) -> None:
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at = None
        self._half_open_calls = 0

    def record_failure(self) -> None:
        if self.state is CircuitState.HALF_OPEN:
            self._trip()
            return
        self._failure_count += 1
        if self._failure_count >= self._settings.failure_threshold:
            self._trip()

    def _cooldown_elapsed(self) -> bool:
        return (
            self._opened_at is not None
            and (self._clock() - self._opened_at) >= self._settings.cooldown_seconds
        )

    def _trip(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = self._clock()
        self._failure_count = 0
        self._half_open_calls = 0
