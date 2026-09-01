from __future__ import annotations

from enum import StrEnum


class AffiliationApplicationStatus(StrEnum):
    """`MD files/0 Workflow/pff_affiliation_e2e_flow.md` "Application Status
    Reference" table — the 6 authoritative statuses. This platform never assigns or
    infers a status; it only reports whatever `get_application` returns (CLAUDE.md
    Golden Rule)."""

    IN_PROGRESS = "IN_PROGRESS"
    PENDING_CFA = "PENDING_CFA"
    INVOICED = "INVOICED"
    COMPLETE = "COMPLETE"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


# doc 5 §92 / flow doc Scenarios 6-9: these statuses mean the workflow must stop and
# wait for an enterprise/HIL event (CFA decision, payment confirmation) before an
# affiliation-status conversation can reach a final answer.
WAITING_STATUSES = frozenset({
    AffiliationApplicationStatus.PENDING_CFA,
    AffiliationApplicationStatus.INVOICED,
})

# Statuses where the workflow has reached a final, explainable outcome with nothing
# left to wait for.
TERMINAL_STATUSES = frozenset({
    AffiliationApplicationStatus.COMPLETE,
    AffiliationApplicationStatus.REJECTED,
    AffiliationApplicationStatus.CANCELLED,
})
