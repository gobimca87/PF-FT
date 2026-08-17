from __future__ import annotations

from enum import StrEnum


class DataSourcePrecedence(StrEnum):
    """Golden Rule order (CLAUDE.md): Enterprise API/Event > ERC > Cache > RAG > SLM output."""

    ENTERPRISE = "ENTERPRISE"
    ERC = "ERC"
    CACHE = "CACHE"
    RAG = "RAG"
    SLM = "SLM"


_PRECEDENCE_ORDER: tuple[DataSourcePrecedence, ...] = (
    DataSourcePrecedence.ENTERPRISE,
    DataSourcePrecedence.ERC,
    DataSourcePrecedence.CACHE,
    DataSourcePrecedence.RAG,
    DataSourcePrecedence.SLM,
)


def higher_precedence(
    first: DataSourcePrecedence, second: DataSourcePrecedence
) -> DataSourcePrecedence:
    return first if _PRECEDENCE_ORDER.index(first) <= _PRECEDENCE_ORDER.index(second) else second
