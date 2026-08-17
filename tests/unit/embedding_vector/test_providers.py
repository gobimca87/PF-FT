import httpx
import pytest

from pf_ft_ai.common.exceptions import IntegrationError
from pf_ft_ai.embedding_vector.providers import HuggingFaceEmbeddingProvider, MockEmbeddingProvider


async def test_mock_provider_should_be_deterministic() -> None:
    provider = MockEmbeddingProvider(dimension=16)

    first = await provider.embed_query("Example FC affiliation")
    second = await provider.embed_query("Example FC affiliation")

    assert first == second
    assert len(first) == 16


async def test_mock_provider_should_produce_different_vectors_for_different_text() -> None:
    provider = MockEmbeddingProvider(dimension=16)

    a = await provider.embed_query("club affiliation")
    b = await provider.embed_query("official accreditation")

    assert a != b


async def test_mock_provider_should_batch_embed_documents() -> None:
    provider = MockEmbeddingProvider(dimension=8)

    vectors = await provider.embed_documents(["one", "two", "three"])

    assert len(vectors) == 3
    assert all(len(vector) == 8 for vector in vectors)


async def test_huggingface_provider_should_embed_documents() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/models/test-model"
        return httpx.Response(200, json=[[0.1, 0.2, 0.3]])

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://hf.example"
    ) as client:
        provider = HuggingFaceEmbeddingProvider(client, model_id="test-model")
        vectors = await provider.embed_documents(["hello"])

    assert vectors == [(0.1, 0.2, 0.3)]


async def test_huggingface_provider_should_embed_a_single_query() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[[0.4, 0.5]])

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://hf.example"
    ) as client:
        provider = HuggingFaceEmbeddingProvider(client, model_id="test-model")
        vector = await provider.embed_query("hello")

    assert vector == (0.4, 0.5)


async def test_huggingface_provider_should_raise_integration_error_on_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": "unavailable"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://hf.example"
    ) as client:
        provider = HuggingFaceEmbeddingProvider(client, model_id="test-model")
        with pytest.raises(IntegrationError):
            await provider.embed_query("hello")
