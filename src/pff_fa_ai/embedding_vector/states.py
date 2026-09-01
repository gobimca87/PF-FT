from __future__ import annotations

from enum import StrEnum


class EmbeddingModelStatus(StrEnum):
    """Doc 14 §16."""

    ACTIVE = "ACTIVE"
    TESTING = "TESTING"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"
    BLOCKED = "BLOCKED"
