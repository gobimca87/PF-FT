from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.configuration.loader import load_vector_store_configuration
from pff_fa_ai.configuration.models import ALLOWED_ENVIRONMENTS


def test_should_load_vector_store_configuration_from_the_real_config_repository() -> None:
    config = load_vector_store_configuration("dev")

    # ADR-D3-24: Azure AI Search is the build default, but provider stays inmemory until
    # the index is provisioned; dimension matches the 768 embedding index (ADR-D3-23).
    assert config.vector_store.provider == "inmemory"
    assert config.vector_store.dimension == 768
    assert config.vector_store.index_alias == "pff-fa-knowledge"
    assert config.vector_store.azure_ai_search.index_name == "pff-fa-knowledge-v1"


@pytest.mark.parametrize("environment", ALLOWED_ENVIRONMENTS)
def test_should_load_vector_store_for_every_declared_environment(environment: str) -> None:
    config = load_vector_store_configuration(environment)  # type: ignore[arg-type]

    assert config.vector_store.provider in {"inmemory", "azure_ai_search"}


def test_should_fail_fast_when_section_missing(tmp_path: Path) -> None:
    root = tmp_path / "config"
    (root / "base").mkdir(parents=True)
    (root / "environments" / "dev").mkdir(parents=True)
    (root / "base" / "vector-store.yaml").write_text("", encoding="utf-8")
    (root / "environments" / "dev" / "vector-store.yaml").write_text("", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Missing required configuration section"):
        load_vector_store_configuration("dev", config_root=root)
