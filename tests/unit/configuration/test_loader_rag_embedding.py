from pathlib import Path

import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.configuration.loader import load_embedding_configuration, load_rag_configuration
from pf_ft_ai.configuration.models import ALLOWED_ENVIRONMENTS


def test_should_load_rag_configuration_from_the_real_config_repository() -> None:
    config = load_rag_configuration("dev")

    assert config.chunking.target_tokens == 400
    assert config.chunking.overlap_tokens == 50
    assert config.retrieval.vector_top_k == 20
    assert config.retrieval.keyword_top_k == 20
    assert config.reranking.top_n == 8
    assert config.agentic_rag.max_iterations == 2


def test_should_load_embedding_configuration_from_the_real_config_repository() -> None:
    config = load_embedding_configuration("dev")

    assert config.embedding.provider == "mock"
    assert config.embedding.dimension == 32


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_rag_and_embedding_configuration_for_every_declared_environment(
    environment: str,
) -> None:
    rag_config = load_rag_configuration(environment)  # type: ignore[arg-type]
    embedding_config = load_embedding_configuration(environment)  # type: ignore[arg-type]

    assert rag_config.chunking.target_tokens > 0
    assert embedding_config.embedding.dimension > 0


def test_should_fail_fast_when_rag_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "rag.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "rag.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_rag_configuration("dev", config_root=root)


def test_should_fail_fast_when_embedding_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "embedding.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "embedding.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_embedding_configuration("dev", config_root=root)
