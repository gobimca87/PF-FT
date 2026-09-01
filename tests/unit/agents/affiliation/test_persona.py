from pff_fa_ai.agents.affiliation.persona import build_response_text

_CLUB = {"name": "Testville FC"}
_APPLICATION = {"season": "2026-27", "total_fee": 150.0, "currency": "GBP"}


def test_complete_outcome_should_celebrate() -> None:
    text = build_response_text(
        club=_CLUB, application=_APPLICATION, outcome_category="complete", payment_status=None
    )

    assert "GOAL" in text
    assert "Testville FC" in text
    assert "150.00" in text


def test_waiting_cfa_outcome_should_use_var_check_framing_without_celebrating() -> None:
    text = build_response_text(
        club=_CLUB, application=_APPLICATION, outcome_category="waiting_cfa", payment_status=None
    )

    assert "GOAL" not in text
    assert "VAR check" in text


def test_waiting_payment_outcome_should_include_the_invoice_and_payment_status() -> None:
    application = {**_APPLICATION, "invoice_number": "INV-1"}
    text = build_response_text(
        club=_CLUB,
        application=application,
        outcome_category="waiting_payment",
        payment_status={"status": "AWAITING_PAYMENT"},
    )

    assert "INV-1" in text
    assert "AWAITING_PAYMENT" in text
    assert "GOAL" not in text


def test_waiting_payment_outcome_should_handle_a_missing_invoice_number() -> None:
    text = build_response_text(
        club=_CLUB,
        application=_APPLICATION,
        outcome_category="waiting_payment",
        payment_status=None,
    )

    assert "pending" in text


def test_rejected_outcome_should_be_factual_and_include_the_reason() -> None:
    application = {**_APPLICATION, "rejection_reason": "Missing safeguarding checks"}
    text = build_response_text(
        club=_CLUB, application=application, outcome_category="rejected", payment_status=None
    )

    assert "GOAL" not in text
    assert "Missing safeguarding checks" in text


def test_rejected_outcome_should_handle_a_missing_reason() -> None:
    text = build_response_text(
        club=_CLUB, application=_APPLICATION, outcome_category="rejected", payment_status=None
    )

    assert "no reason was provided" in text


def test_cancelled_outcome_should_be_factual_and_include_the_reason() -> None:
    application = {**_APPLICATION, "cancellation_reason": "Club withdrew"}
    text = build_response_text(
        club=_CLUB, application=application, outcome_category="cancelled", payment_status=None
    )

    assert "Club withdrew" in text


def test_in_progress_outcome_should_explain_what_is_still_needed() -> None:
    text = build_response_text(
        club=_CLUB, application=_APPLICATION, outcome_category="in_progress", payment_status=None
    )

    assert "in progress" in text


def test_non_gbp_currency_should_use_the_currency_code_not_the_pound_sign() -> None:
    application = {**_APPLICATION, "currency": "EUR"}
    text = build_response_text(
        club=_CLUB, application=application, outcome_category="complete", payment_status=None
    )

    assert "EUR" in text
    assert "£" not in text
