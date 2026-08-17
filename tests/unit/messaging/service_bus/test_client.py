from azure.servicebus.aio import ServiceBusClient
from azure.servicebus.aio import ServiceBusReceiver as AzureReceiver

from pf_ft_ai.configuration.models import ServiceBusConnectionSettings, TopicSettings
from pf_ft_ai.messaging.service_bus.client import (
    AzureServiceBusReceiver,
    build_service_bus_client,
    build_subscription_receiver,
)

_FAKE_CONNECTION_STRING = (
    "Endpoint=sb://pf-ft-example.servicebus.windows.net/;"
    "SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=fakekey123=="
)


def _topic() -> TopicSettings:
    return TopicSettings(
        name="pf-ft-enterprise-events-dev",
        description="dev topic",
        subscription_name="pf-ft-ai-runtime-dev",
        subscription_description="dev subscription",
    )


def test_build_service_bus_client_should_construct_a_client_without_connecting() -> None:
    client = build_service_bus_client(
        ServiceBusConnectionSettings(connection_string=_FAKE_CONNECTION_STRING)
    )

    assert isinstance(client, ServiceBusClient)


def test_build_subscription_receiver_should_target_the_configured_topic_and_subscription() -> None:
    client = build_service_bus_client(
        ServiceBusConnectionSettings(connection_string=_FAKE_CONNECTION_STRING)
    )

    receiver = build_subscription_receiver(client, topic=_topic())

    assert isinstance(receiver, AzureReceiver)
    assert receiver.entity_path == "pf-ft-enterprise-events-dev/Subscriptions/pf-ft-ai-runtime-dev"


class _FakeRawReceiver:
    """Stands in for `azure.servicebus.aio.ServiceBusReceiver` to prove the adapter
    forwards calls/kwargs correctly without needing a live Azure connection."""

    def __init__(self) -> None:
        self.completed: list[object] = []
        self.abandoned: list[object] = []
        self.dead_lettered: list[tuple[object, str, str]] = []

    async def receive_messages(self, *, max_message_count: int, max_wait_time: float) -> list[str]:
        return [f"message-{i}" for i in range(max_message_count)]

    async def complete_message(self, message: object) -> None:
        self.completed.append(message)

    async def abandon_message(self, message: object) -> None:
        self.abandoned.append(message)

    async def dead_letter_message(
        self, message: object, *, reason: str, error_description: str
    ) -> None:
        self.dead_lettered.append((message, reason, error_description))


async def test_receiver_adapter_should_forward_receive_messages() -> None:
    raw = _FakeRawReceiver()
    receiver = AzureServiceBusReceiver(raw)  # type: ignore[arg-type]

    messages = await receiver.receive_messages(max_message_count=3, max_wait_time=1.0)

    assert messages == ["message-0", "message-1", "message-2"]


async def test_receiver_adapter_should_forward_complete_message() -> None:
    raw = _FakeRawReceiver()
    receiver = AzureServiceBusReceiver(raw)  # type: ignore[arg-type]

    await receiver.complete_message("message-1")

    assert raw.completed == ["message-1"]


async def test_receiver_adapter_should_forward_abandon_message() -> None:
    raw = _FakeRawReceiver()
    receiver = AzureServiceBusReceiver(raw)  # type: ignore[arg-type]

    await receiver.abandon_message("message-1")

    assert raw.abandoned == ["message-1"]


async def test_receiver_adapter_should_forward_dead_letter_message() -> None:
    raw = _FakeRawReceiver()
    receiver = AzureServiceBusReceiver(raw)  # type: ignore[arg-type]

    await receiver.dead_letter_message(
        "message-1", reason="INVALID_SCHEMA", error_description="bad payload"
    )

    assert raw.dead_lettered == [("message-1", "INVALID_SCHEMA", "bad payload")]


class _FakeBody:
    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = chunks

    def __iter__(self) -> object:
        return iter(self._chunks)


class _FakeAzureMessage:
    def __init__(self, body: object) -> None:
        self.body = body


def test_decode_body_should_join_chunked_bytes_and_parse_json() -> None:
    receiver = AzureServiceBusReceiver(receiver=object())  # type: ignore[arg-type]
    message = _FakeAzureMessage(_FakeBody([b'{"event_id": "evt-1", ', b'"event_type": "X"}']))

    decoded = receiver.decode_body(message)

    assert decoded == {"event_id": "evt-1", "event_type": "X"}


def test_decode_body_should_handle_a_plain_bytes_body() -> None:
    receiver = AzureServiceBusReceiver(receiver=object())  # type: ignore[arg-type]
    message = _FakeAzureMessage(b'{"event_id": "evt-1"}')

    decoded = receiver.decode_body(message)

    assert decoded == {"event_id": "evt-1"}
