from __future__ import annotations

from typing import Any

# CLAUDE.md "Adam AI Persona & Conversational Style — Mandatory": workflow-first,
# football-commentary tone used *contextually* at meaningful moments, never forced,
# never celebrating an unconfirmed transaction, and errors stay factual. These are
# deterministic Python templates (no SLM call) — CLAUDE.md's rule 5 ("Enterprise truth
# overrides persona") is enforced structurally here: every fact substituted into a
# template comes from `entities["application"]`/`entities["club"]`, i.e. directly from
# the enterprise `get_application`/`get_club` tool results, never invented.


def _money(amount: float, currency: str) -> str:
    symbol = "£" if currency == "GBP" else f"{currency} "
    return f"{symbol}{amount:,.2f}"


def build_response_text(
    *,
    club: dict[str, Any],
    application: dict[str, Any],
    outcome_category: str,
    payment_status: dict[str, Any] | None,
) -> str:
    club_name = club["name"]
    season = application["season"]
    fee = _money(application["total_fee"], application.get("currency", "GBP"))

    if outcome_category == "complete":
        return (
            f"GOAL! {club_name}'s affiliation for the {season} season is complete. "
            f"Total fee: {fee}. Teams are affiliated and ready to go."
        )

    if outcome_category == "waiting_cfa":
        return (
            f"{club_name}'s application has gone to review — think of it as a VAR "
            "check: the county (CFA) is looking it over before the final whistle. "
            "We'll update you as soon as a decision comes through."
        )

    if outcome_category == "waiting_payment":
        invoice = application.get("invoice_number") or "pending"
        payment_note = ""
        if payment_status is not None and payment_status.get("status"):
            payment_note = f" Current payment status: {payment_status['status']}."
        return (
            f"Almost there! {club_name}'s application has been approved and is "
            f"awaiting payment — invoice {invoice}, {fee}. Complete payment to get "
            f"affiliation over the line.{payment_note}"
        )

    if outcome_category == "rejected":
        reason = application.get("rejection_reason") or "no reason was provided"
        return (
            f"{club_name}'s application was not approved. Reason: {reason}. "
            "You can update the application and resubmit."
        )

    if outcome_category == "cancelled":
        reason = application.get("cancellation_reason") or "no reason was provided"
        return (
            f"{club_name}'s application was cancelled. Reason: {reason}. "
            "A new application can be submitted."
        )

    return (
        f"{club_name}'s affiliation application is still in progress — teams, "
        "insurance and products need to be finalized before it can be submitted."
    )
