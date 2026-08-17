from __future__ import annotations

import json
from typing import Any, Protocol

from azure.servicebus.aio import ServiceBusClient
from azure.servicebus.aio import ServiceBusReceiver as AzureReceiver

from pf_ft_ai.configuration.models import ServiceBusConnectionSettings, TopicSettings


class ServiceBusReceiverPort(Protocol):
    """doc 11 §138 `messaging/service_bus/client.py` — the consumer depends on this,
    never on the Azure SDK type directly (same "provider independence" discipline as
    every other infra boundary in this platform)."""

    async def receive_messages(
        self, *, max_message_count: int, max_wait_time: float
    ) -> list[Any]: ...

    async def complete_message(self, message: Any) -> None: ...

    async def abandon_message(self, message: Any) -> None: ...

    async def dead_letter_message(
        self, message: Any, *, reason: str, error_description: str
    ) -> None: ...

    def decode_body(self, message: Any) -> dict[str, Any]: ...


class AzureServiceBusReceiver:
    """Real receiver adapter around `azure.servicebus.aio.ServiceBusReceiver`."""

    def __init__(self, receiver: AzureReceiver) -> None:
        self._receiver = receiver

    async def receive_messages(self, *, max_message_count: int, max_wait_time: float) -> list[Any]:
        return await self._receiver.receive_messages(
            max_message_count=max_message_count, max_wait_time=max_wait_time
        )

    async def complete_message(self, message: Any) -> None:
        await self._receiver.complete_message(message)

    async def abandon_message(self, message: Any) -> None:
        await self._receiver.abandon_message(message)

    async def dead_letter_message(
        self, message: Any, *, reason: str, error_description: str
    ) -> None:
        await self._receiver.dead_letter_message(
            message, reason=reason, error_description=error_description
        )

    def decode_body(self, message: Any) -> dict[str, Any]:
        chunks = message.body
        body_bytes = bytes(chunks) if isinstance(chunks, bytes | bytearray) else b"".join(chunks)
        return json.loads(body_bytes.decode("utf-8"))  # type: ignore[no-any-return]


def build_service_bus_client(settings: ServiceBusConnectionSettings) -> ServiceBusClient:
    """doc 11 §27/§123-124: the connection string is Key Vault-backed (resolved via
    `connection.connection_string_secret_ref`) — never hardcoded here."""
    return ServiceBusClient.from_connection_string(settings.connection_string)


def build_subscription_receiver(client: ServiceBusClient, *, topic: TopicSettings) -> AzureReceiver:
    """doc 11 §29: a dedicated AI subscription, never the raw topic — prevents
    consuming enterprise events unrelated to this platform."""
    return client.get_subscription_receiver(
        topic_name=topic.name, subscription_name=topic.subscription_name
    )
