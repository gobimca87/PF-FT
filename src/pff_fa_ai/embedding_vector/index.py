from __future__ import annotations

from pff_fa_ai.common.exceptions import ConfigurationError


class IndexAliasRegistry:
    """Doc 14 §77-78 blue/green indexing — application code addresses a logical index
    name, never a hard-coded physical index version."""

    def __init__(self) -> None:
        self._aliases: dict[str, str] = {}

    def switch(self, logical_name: str, index_version: str) -> None:
        self._aliases[logical_name] = index_version

    def resolve(self, logical_name: str) -> str:
        try:
            return self._aliases[logical_name]
        except KeyError as exc:
            raise ConfigurationError(f"No active index for alias: {logical_name}") from exc
