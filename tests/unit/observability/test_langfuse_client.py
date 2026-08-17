from pf_ft_ai.common.correlation import CorrelationContext
from pf_ft_ai.configuration.models import LangfuseSettings
from pf_ft_ai.observability.langfuse_client import (
    LangfuseObservabilityClient,
    NullObservabilityClient,
    build_observability_client,
)


class _StubLangfuseClient:
    def __init__(self, *, raise_on_trace: bool = False, raise_on_flush: bool = False) -> None:
        self.traces: list[dict[str, object]] = []
        self.flushed = False
        self._raise_on_trace = raise_on_trace
        self._raise_on_flush = raise_on_flush

    def trace(self, **kwargs: object) -> None:
        if self._raise_on_trace:
            raise RuntimeError("langfuse unavailable")
        self.traces.append(kwargs)

    def flush(self) -> None:
        if self._raise_on_flush:
            raise RuntimeError("flush failed")
        self.flushed = True


def _correlation() -> CorrelationContext:
    return CorrelationContext(
        request_id="req-1",
        correlation_id="corr-1",
        conversation_id="conv-1",
        workflow_instance_id="wf-1",
    )


def test_null_client_should_be_a_genuine_no_op() -> None:
    client = NullObservabilityClient()

    client.record_event(name="chat_message", correlation=_correlation())
    client.flush()


def test_langfuse_client_should_forward_a_trace() -> None:
    stub = _StubLangfuseClient()
    client = LangfuseObservabilityClient(stub)

    client.record_event(name="chat_message", correlation=_correlation(), metadata={"key": "value"})

    assert len(stub.traces) == 1
    assert stub.traces[0]["name"] == "chat_message"
    assert stub.traces[0]["id"] == "corr-1"
    assert stub.traces[0]["metadata"]["key"] == "value"  # type: ignore[index]
    assert stub.traces[0]["metadata"]["workflow_instance_id"] == "wf-1"  # type: ignore[index]


def test_langfuse_client_should_swallow_a_trace_failure() -> None:
    """doc 24 §48: Langfuse failure must never break core execution."""
    stub = _StubLangfuseClient(raise_on_trace=True)
    client = LangfuseObservabilityClient(stub)

    client.record_event(name="chat_message", correlation=_correlation())  # must not raise


def test_langfuse_client_should_swallow_a_flush_failure() -> None:
    stub = _StubLangfuseClient(raise_on_flush=True)
    client = LangfuseObservabilityClient(stub)

    client.flush()  # must not raise


def test_langfuse_client_flush_should_forward_when_healthy() -> None:
    stub = _StubLangfuseClient()
    client = LangfuseObservabilityClient(stub)

    client.flush()

    assert stub.flushed is True


def test_build_should_return_null_client_when_disabled() -> None:
    settings = LangfuseSettings(enabled=False)

    client = build_observability_client(settings)

    assert isinstance(client, NullObservabilityClient)


def test_build_should_return_null_client_when_enabled_but_missing_credentials() -> None:
    settings = LangfuseSettings(enabled=True, host="https://cloud.langfuse.com")

    client = build_observability_client(settings)

    assert isinstance(client, NullObservabilityClient)


def test_build_should_return_a_real_client_when_fully_configured() -> None:
    settings = LangfuseSettings(
        enabled=True,
        host="https://cloud.langfuse.com",
        public_key="pk-fake",
        secret_key="sk-fake",
    )

    client = build_observability_client(settings)

    assert isinstance(client, LangfuseObservabilityClient)
