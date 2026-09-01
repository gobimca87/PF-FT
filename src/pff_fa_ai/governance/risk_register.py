from __future__ import annotations

from datetime import date

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.governance.models import RiskRegisterEntry
from pff_fa_ai.governance.states import RiskStatus


class RiskRegister:
    """doc 20 §18 "AI Risk Register" — maintained as an append/update log keyed by
    `risk_id`, never silently overwritten (mirrors `GovernedArtifactRegistry`'s and
    every other Phase 16-21 registry's duplicate-rejection discipline)."""

    def __init__(self) -> None:
        self._entries: dict[str, RiskRegisterEntry] = {}

    def add(self, entry: RiskRegisterEntry) -> None:
        if entry.risk_id in self._entries:
            raise ConfigurationError(f"Duplicate risk register entry: {entry.risk_id}")
        self._entries[entry.risk_id] = entry

    def get(self, risk_id: str) -> RiskRegisterEntry | None:
        return self._entries.get(risk_id)

    def update_status(self, risk_id: str, status: RiskStatus) -> RiskRegisterEntry:
        entry = self._entries.get(risk_id)
        if entry is None:
            raise ConfigurationError(f"Unknown risk register entry: {risk_id}")
        updated = entry.model_copy(update={"status": status})
        self._entries[risk_id] = updated
        return updated

    def all_entries(self) -> tuple[RiskRegisterEntry, ...]:
        return tuple(self._entries.values())

    def by_status(self, status: RiskStatus) -> tuple[RiskRegisterEntry, ...]:
        return tuple(entry for entry in self._entries.values() if entry.status is status)

    def overdue_for_review(self, *, as_of: date) -> tuple[RiskRegisterEntry, ...]:
        """doc 20 §18 "Review Date" — a risk not reviewed by its due date must be
        surfaced, not silently carried forward (doc 20 §103 "avoid permanent
        exceptions")."""
        return tuple(
            entry
            for entry in self._entries.values()
            if entry.review_date < as_of and entry.status is not RiskStatus.CLOSED
        )
