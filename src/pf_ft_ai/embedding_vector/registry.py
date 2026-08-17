from __future__ import annotations

from collections.abc import Sequence

from pf_ft_ai.common.exceptions import ConfigurationError, ValidationError
from pf_ft_ai.embedding_vector.models import EmbeddingModelDescriptor


class EmbeddingModelRegistry:
    """Doc 14 §8 controlled embedding model registry."""

    def __init__(self) -> None:
        self._models: dict[str, EmbeddingModelDescriptor] = {}

    def register(self, descriptor: EmbeddingModelDescriptor) -> None:
        self._models[descriptor.model_id] = descriptor

    def get(self, model_id: str) -> EmbeddingModelDescriptor:
        try:
            return self._models[model_id]
        except KeyError as exc:
            raise ConfigurationError(f"Embedding model not registered: {model_id}") from exc

    def assert_dimension(self, model_id: str, vector: Sequence[float]) -> None:
        """Doc 14 §18-19 — dimension mismatch must fail validation, before indexing or search."""
        descriptor = self.get(model_id)
        if len(vector) != descriptor.dimension:
            raise ValidationError(
                f"Embedding dimension mismatch for '{model_id}': "
                f"expected {descriptor.dimension}, got {len(vector)}",
                details={
                    "model_id": model_id,
                    "expected": descriptor.dimension,
                    "got": len(vector),
                },
            )
