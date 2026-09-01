import httpx
import pytest

from pff_fa_ai.common.exceptions import IntegrationError
from pff_fa_ai.slm.models import SlmMessage, SlmRequest
from pff_fa_ai.slm.providers import HuggingFaceSLMProvider, MockSLMProvider
from pff_fa_ai.slm.states import ProviderHealthStatus


def _request(text: str = "What documents are required?") -> SlmRequest:
    return SlmRequest(
        model_id="mock-slm-v1",
        messages=(SlmMessage(role="user", content=text),),
        temperature=0.2,
        top_p=0.95,
        max_output_tokens=256,
    )


async def test_mock_provider_should_generate_a_deterministic_response() -> None:
    provider = MockSLMProvider()

    first = await provider.generate(_request())
    second = await provider.generate(_request())

    assert first.output == second.output
    assert first.finish_reason == "stop"
    assert first.usage.total_tokens == first.usage.prompt_tokens + first.usage.completion_tokens


async def test_mock_provider_should_stream_the_generated_output() -> None:
    provider = MockSLMProvider()

    chunks = [chunk async for chunk in provider.stream(_request())]

    assert "".join(chunks).strip() == (await provider.generate(_request())).output


async def test_mock_provider_should_report_healthy() -> None:
    provider = MockSLMProvider()

    assert await provider.health() is ProviderHealthStatus.HEALTHY


async def test_huggingface_provider_should_generate_a_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "output": "Clubs must submit affiliation documents.",
                "usage": {"prompt_tokens": 10, "completion_tokens": 6, "total_tokens": 16},
                "finish_reason": "stop",
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://hf.example"
    ) as client:
        provider = HuggingFaceSLMProvider(client, model_version="1.2.0")
        response = await provider.generate(_request())

    assert response.output == "Clubs must submit affiliation documents."
    assert response.model_version == "1.2.0"
    assert response.usage.total_tokens == 16


async def test_huggingface_provider_should_stream_the_generated_output() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "output": "Clubs must submit affiliation documents.",
                "usage": {"prompt_tokens": 10, "completion_tokens": 6, "total_tokens": 16},
                "finish_reason": "stop",
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://hf.example"
    ) as client:
        provider = HuggingFaceSLMProvider(client, model_version="1.2.0")
        chunks = [chunk async for chunk in provider.stream(_request())]

    assert "".join(chunks).strip() == "Clubs must submit affiliation documents."


async def test_huggingface_provider_should_raise_integration_error_on_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": "unavailable"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://hf.example"
    ) as client:
        provider = HuggingFaceSLMProvider(client, model_version="1.2.0")
        with pytest.raises(IntegrationError):
            await provider.generate(_request())


async def test_huggingface_provider_health_should_report_unavailable_on_network_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://hf.example"
    ) as client:
        provider = HuggingFaceSLMProvider(client, model_version="1.2.0")
        assert await provider.health() is ProviderHealthStatus.UNAVAILABLE


async def test_huggingface_provider_health_should_report_healthy() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://hf.example"
    ) as client:
        provider = HuggingFaceSLMProvider(client, model_version="1.2.0")
        assert await provider.health() is ProviderHealthStatus.HEALTHY
