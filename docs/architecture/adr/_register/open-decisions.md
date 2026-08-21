# Open Decisions — Awaiting Sign-Off

Decisions in this library that carry `status: Proposed`. Each has a complete evaluation —
criteria, alternatives, weighted matrix — and a stated recommendation, but has **not** been
ratified. Nothing downstream may treat a `Proposed` decision as settled.

`CLAUDE.md` §Confirmed Tech Stack is explicit that several of these must be *resolved via
ADR, not silently picked*. That is why they are recorded here with full analysis and a
recommendation rather than either guessed at or left undocumented.

Escalation path and the deferral rules are in
[ADR-D0-04](../00-decision-programme/ADR-D0-04-open-decision-register-and-escalation.md).

## Open decisions

| ID | Decision | Recommendation | Needed by | Blocking | Decision owner |
|---|---|---|---|---|---|

*Rows are added as each `Proposed` ADR lands.*

## Relationship to `docs/adr/0003-deferred-decisions-log.md`

The earlier deferred-decisions log in `docs/adr/` is superseded by this file together with
[ADR-D0-04](../00-decision-programme/ADR-D0-04-open-decision-register-and-escalation.md).
It remains in place unmodified as the historical record.
