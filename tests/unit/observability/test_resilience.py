from pff_fa_ai.configuration.models import CircuitBreakerSettings
from pff_fa_ai.integration.execution.circuit import CircuitBreaker, CircuitState
from pff_fa_ai.observability.resilience import ResilienceDependency, ResilienceRegistry

_SETTINGS = CircuitBreakerSettings(failure_threshold=2, cooldown_seconds=30, half_open_max_calls=1)


def test_should_provide_a_circuit_breaker_for_every_dependency() -> None:
    registry = ResilienceRegistry(_SETTINGS)

    for dependency in ResilienceDependency:
        breaker = registry.get(dependency)
        assert isinstance(breaker, CircuitBreaker)
        assert breaker.state is CircuitState.CLOSED


def test_should_isolate_failures_between_dependencies() -> None:
    registry = ResilienceRegistry(_SETTINGS)

    slm_breaker = registry.get(ResilienceDependency.SLM)
    slm_breaker.record_failure()
    slm_breaker.record_failure()

    assert slm_breaker.state is CircuitState.OPEN
    assert registry.get(ResilienceDependency.RAG).state is CircuitState.CLOSED


def test_should_return_the_same_breaker_instance_on_repeated_lookup() -> None:
    registry = ResilienceRegistry(_SETTINGS)

    assert registry.get(ResilienceDependency.CACHE) is registry.get(ResilienceDependency.CACHE)
