from __future__ import annotations

from enum import StrEnum


class RefinementDecision(StrEnum):
    """ADR-D3-28 §14 loop-decision enum. The gate is deterministic (ADR-D3-05 §7.4): the
    model produces the score signal, this decision is taken by code. REFINE/ESCALATE are
    per-iteration; COMMIT/EXHAUST are terminal."""

    REFINE = "REFINE"
    ESCALATE = "ESCALATE"
    COMMIT = "COMMIT"
    EXHAUST = "EXHAUST"


class OnExhaustionAction(StrEnum):
    """ADR-D3-28 §7 — the action taken when `max_refinement_iterations` is reached without
    clearing the bar. The loop never silently ships a below-bar output as if it passed."""

    RETURN_BEST_FLAGGED = "return_best_flagged"
    DEFER_TO_HIL = "defer_to_hil"
    FAIL_CLOSED = "fail_closed"
