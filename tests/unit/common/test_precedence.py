import pytest

from pff_fa_ai.common.precedence import DataSourcePrecedence, higher_precedence


@pytest.mark.parametrize(
    "first,second,expected",
    [
        (
            DataSourcePrecedence.ENTERPRISE,
            DataSourcePrecedence.SLM,
            DataSourcePrecedence.ENTERPRISE,
        ),
        (
            DataSourcePrecedence.SLM,
            DataSourcePrecedence.ENTERPRISE,
            DataSourcePrecedence.ENTERPRISE,
        ),
        (DataSourcePrecedence.ERC, DataSourcePrecedence.CACHE, DataSourcePrecedence.ERC),
        (DataSourcePrecedence.RAG, DataSourcePrecedence.SLM, DataSourcePrecedence.RAG),
        (DataSourcePrecedence.CACHE, DataSourcePrecedence.CACHE, DataSourcePrecedence.CACHE),
    ],
)
def test_should_resolve_higher_precedence_source(
    first: DataSourcePrecedence, second: DataSourcePrecedence, expected: DataSourcePrecedence
) -> None:
    assert higher_precedence(first, second) == expected
