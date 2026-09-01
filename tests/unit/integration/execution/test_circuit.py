from pff_fa_ai.configuration.models import CircuitBreakerSettings
from pff_fa_ai.integration.execution.circuit import CircuitBreaker, CircuitState

SETTINGS = CircuitBreakerSettings(failure_threshold=3, cooldown_seconds=30, half_open_max_calls=1)


class _FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_should_start_closed() -> None:
    breaker = CircuitBreaker(SETTINGS)

    assert breaker.state is CircuitState.CLOSED
    assert breaker.allow_request() is True


def test_should_stay_closed_below_failure_threshold() -> None:
    breaker = CircuitBreaker(SETTINGS)

    breaker.record_failure()
    breaker.record_failure()

    assert breaker.state is CircuitState.CLOSED


def test_should_trip_open_at_failure_threshold() -> None:
    breaker = CircuitBreaker(SETTINGS)

    for _ in range(SETTINGS.failure_threshold):
        breaker.record_failure()

    assert breaker.state is CircuitState.OPEN
    assert breaker.allow_request() is False


def test_should_move_to_half_open_after_cooldown() -> None:
    clock = _FakeClock()
    breaker = CircuitBreaker(SETTINGS, clock=clock)
    for _ in range(SETTINGS.failure_threshold):
        breaker.record_failure()

    clock.now += SETTINGS.cooldown_seconds

    assert breaker.state is CircuitState.HALF_OPEN


def test_half_open_should_allow_only_the_configured_trial_calls() -> None:
    clock = _FakeClock()
    breaker = CircuitBreaker(SETTINGS, clock=clock)
    for _ in range(SETTINGS.failure_threshold):
        breaker.record_failure()
    clock.now += SETTINGS.cooldown_seconds

    assert breaker.allow_request() is True  # the one allowed trial call
    assert breaker.allow_request() is False  # budget exhausted


def test_half_open_success_should_close_the_circuit() -> None:
    clock = _FakeClock()
    breaker = CircuitBreaker(SETTINGS, clock=clock)
    for _ in range(SETTINGS.failure_threshold):
        breaker.record_failure()
    clock.now += SETTINGS.cooldown_seconds
    breaker.allow_request()

    breaker.record_success()

    assert breaker.state is CircuitState.CLOSED
    assert breaker.allow_request() is True


def test_half_open_failure_should_reopen_the_circuit() -> None:
    clock = _FakeClock()
    breaker = CircuitBreaker(SETTINGS, clock=clock)
    for _ in range(SETTINGS.failure_threshold):
        breaker.record_failure()
    clock.now += SETTINGS.cooldown_seconds
    breaker.allow_request()

    breaker.record_failure()

    assert breaker.state is CircuitState.OPEN
