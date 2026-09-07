from pff_fa_ai.agents.affiliation.persona import build_response_text, grounded_answer_tokens
from pff_fa_ai.guardrails.groundedness import (
    GroundednessEvidence,
    GroundednessOutputPolicy,
    build_grounded_identifiers,
    check_groundedness,
    extract_grounding_tokens,
)
from pff_fa_ai.guardrails.models import GuardrailContext
from pff_fa_ai.guardrails.states import GuardrailBoundary, GuardrailDecision
from pff_fa_ai.rag.models import Citation


def _evidence(**overrides: object) -> GroundednessEvidence:
    base: dict[str, object] = {
        "grounded_identifiers": frozenset({"£150.00", "INV-1"}),
    }
    base.update(overrides)
    return GroundednessEvidence(**base)  # type: ignore[arg-type]


def test_extract_grounding_tokens_only_picks_structured_tokens() -> None:
    tokens = extract_grounding_tokens(
        "Riverside FC owes £1,234.00 on invoice INV-12345 — see https://portal.example/pay"
    )

    assert tokens == frozenset({"£1,234.00", "INV-12345", "https://portal.example/pay"})


def test_ordinary_prose_and_seasons_are_not_flagged_as_tokens() -> None:
    # "5 teams" and a "2026-27" season are bare numbers, deliberately not extracted, so
    # they can never be spuriously reported as ungrounded.
    assert extract_grounding_tokens("Your 5 teams are ready for the 2026-27 season") == frozenset()


def test_a_grounded_answer_is_allowed() -> None:
    report = check_groundedness(
        answer="Almost there — invoice INV-1, £150.00. Complete payment to finish.",
        evidence=_evidence(),
    )

    assert report.grounded
    assert report.score == 1.0
    assert report.decision is GuardrailDecision.ALLOW


def test_a_fabricated_amount_is_ungrounded() -> None:
    report = check_groundedness(
        answer="Your fee is £999.99.",
        evidence=_evidence(),
    )

    assert not report.grounded
    assert report.score == 0.0
    assert "GR-OUT-UNGROUNDED-ID" in report.reason_codes


def test_an_invented_url_is_ungrounded() -> None:
    report = check_groundedness(
        answer="Pay at https://totally-not-the-portal.example/pay now.",
        evidence=_evidence(),
    )

    assert report.decision is GuardrailDecision.BLOCK
    assert "GR-OUT-UNGROUNDED-ID" in report.reason_codes


def test_an_invented_reference_id_is_ungrounded() -> None:
    report = check_groundedness(answer="See application AFF-98765.", evidence=_evidence())

    assert "GR-OUT-UNGROUNDED-ID" in report.reason_codes


def test_a_knowledge_answer_without_a_citation_is_blocked() -> None:
    report = check_groundedness(
        answer="Clubs must renew affiliation every season.",
        evidence=_evidence(requires_citation=True, citations=()),
    )

    assert "GR-OUT-MISSING-CITATION" in report.reason_codes


def test_a_knowledge_answer_with_a_citation_is_allowed() -> None:
    citation = Citation(document_id="doc-1", document_version=1, title="Rules", chunk_id="c-1")
    report = check_groundedness(
        answer="Clubs must renew affiliation every season.",
        evidence=_evidence(
            grounded_identifiers=frozenset(), requires_citation=True, citations=(citation,)
        ),
    )

    assert report.grounded


def test_a_contradicting_status_literal_is_blocked() -> None:
    report = check_groundedness(
        answer="Your application was REJECTED.",
        evidence=_evidence(forbidden_terms=frozenset({"REJECTED", "CANCELLED"})),
    )

    assert "GR-OUT-CONTRADICTS-ERC" in report.reason_codes


async def test_policy_allows_a_grounded_response() -> None:
    policy = GroundednessOutputPolicy()
    context = GuardrailContext(
        boundary=GuardrailBoundary.OUTPUT,
        content="Invoice INV-1, £150.00.",
        metadata={"groundedness_evidence": _evidence()},
    )

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.ALLOW


async def test_policy_blocks_a_fabricated_response() -> None:
    policy = GroundednessOutputPolicy()
    context = GuardrailContext(
        boundary=GuardrailBoundary.OUTPUT,
        content="Your fee is £999.99.",
        metadata={"groundedness_evidence": _evidence()},
    )

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.BLOCK
    assert "GR-OUT-UNGROUNDED-ID" in result.reason_codes


async def test_policy_fails_closed_without_evidence() -> None:
    policy = GroundednessOutputPolicy()
    context = GuardrailContext(boundary=GuardrailBoundary.OUTPUT, content="anything")

    result = await policy.evaluate(context)

    assert result.decision is GuardrailDecision.BLOCK
    assert "GR-OUT-EVIDENCE-MISSING" in result.reason_codes


_CLUB = {"name": "Testville FC"}
_APPLICATION = {
    "total_fee": 150.0,
    "currency": "GBP",
    "season": "2026-27",
    "invoice_number": "INV-1",
}


def test_every_real_response_template_is_grounded_in_its_own_evidence() -> None:
    """Regression guard: the now-active OUTPUT boundary must never block a legitimate,
    template-generated response. For each outcome category, the answer built by
    `build_response_text` is checked against evidence built from the same authoritative
    application via `grounded_answer_tokens` — all must pass."""
    evidence = GroundednessEvidence(
        grounded_identifiers=grounded_answer_tokens(application=_APPLICATION)
    )
    for outcome in (
        "complete",
        "waiting_cfa",
        "waiting_payment",
        "rejected",
        "cancelled",
        "in_progress",
    ):
        answer = build_response_text(
            club=_CLUB,
            application={
                **_APPLICATION,
                "rejection_reason": "Missing safeguarding checks",
                "cancellation_reason": "Club withdrew",
            },
            outcome_category=outcome,
            payment_status={"status": "AWAITING_PAYMENT"},
        )
        report = check_groundedness(answer=answer, evidence=evidence)
        assert report.grounded, (outcome, report.reason_codes)


def test_build_grounded_identifiers_unions_structured_tokens_across_values() -> None:
    # "plain name" carries no structured token, and "INV-1" (one digit) is below the
    # reference-id pattern's threshold, so neither contributes — only the fee and the
    # multi-digit invoice do.
    assert build_grounded_identifiers(["£150.00", "INV-12345", "INV-1", "plain name"]) == frozenset(
        {"£150.00", "INV-12345"}
    )
