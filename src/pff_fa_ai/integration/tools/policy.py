from __future__ import annotations

from enum import StrEnum


class ToolRiskClass(StrEnum):
    """doc 10 §164."""

    READ = "READ"
    LOW_RISK_WRITE = "LOW_RISK_WRITE"
    HIGH_RISK_WRITE = "HIGH_RISK_WRITE"
    TRANSACTIONAL = "TRANSACTIONAL"


_HIL_REQUIRED_RISK_CLASSES = frozenset({ToolRiskClass.HIGH_RISK_WRITE, ToolRiskClass.TRANSACTIONAL})


def requires_hil(risk_class: ToolRiskClass) -> bool:
    """DEVELOPMENT-GUIDE.md Phase 6: HIGH_RISK_WRITE/TRANSACTIONAL require HIL."""
    return risk_class in _HIL_REQUIRED_RISK_CLASSES
