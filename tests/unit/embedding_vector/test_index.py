import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.embedding_vector.index import IndexAliasRegistry


def test_should_resolve_the_active_index_version() -> None:
    registry = IndexAliasRegistry()
    registry.switch("affiliation", "affiliation-v2")

    assert registry.resolve("affiliation") == "affiliation-v2"


def test_should_support_blue_green_switching() -> None:
    registry = IndexAliasRegistry()
    registry.switch("affiliation", "affiliation-v2")

    registry.switch("affiliation", "affiliation-v3")

    assert registry.resolve("affiliation") == "affiliation-v3"


def test_should_raise_for_an_unknown_alias() -> None:
    registry = IndexAliasRegistry()

    with pytest.raises(ConfigurationError, match="No active index"):
        registry.resolve("unknown")
