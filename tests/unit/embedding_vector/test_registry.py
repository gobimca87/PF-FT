import pytest

from pf_ft_ai.common.exceptions import ConfigurationError, ValidationError
from pf_ft_ai.embedding_vector.models import EmbeddingModelDescriptor
from pf_ft_ai.embedding_vector.registry import EmbeddingModelRegistry
from pf_ft_ai.embedding_vector.states import EmbeddingModelStatus


def _descriptor(dimension: int = 32) -> EmbeddingModelDescriptor:
    return EmbeddingModelDescriptor(
        model_id="mock-embedding-v1",
        provider="mock",
        version="1.0.0",
        dimension=dimension,
        max_input_tokens=512,
        status=EmbeddingModelStatus.ACTIVE,
    )


def test_should_register_and_retrieve_a_model() -> None:
    registry = EmbeddingModelRegistry()
    registry.register(_descriptor())

    descriptor = registry.get("mock-embedding-v1")

    assert descriptor.dimension == 32


def test_should_raise_configuration_error_for_unregistered_model() -> None:
    registry = EmbeddingModelRegistry()

    with pytest.raises(ConfigurationError, match="not registered"):
        registry.get("unknown-model")


def test_should_accept_a_vector_matching_the_registered_dimension() -> None:
    registry = EmbeddingModelRegistry()
    registry.register(_descriptor(dimension=4))

    registry.assert_dimension("mock-embedding-v1", [0.1, 0.2, 0.3, 0.4])


def test_should_reject_a_vector_with_the_wrong_dimension() -> None:
    registry = EmbeddingModelRegistry()
    registry.register(_descriptor(dimension=4))

    with pytest.raises(ValidationError, match="dimension mismatch"):
        registry.assert_dimension("mock-embedding-v1", [0.1, 0.2])
