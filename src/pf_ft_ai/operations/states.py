from __future__ import annotations

from enum import StrEnum


class CheckFrequency(StrEnum):
    """doc 28 §135-137 / DEVELOPMENT-GUIDE Phase 22 — the three operational checklist
    cadences named by the guide."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
