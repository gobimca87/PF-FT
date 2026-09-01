from pff_fa_ai.context.collection.aggregator import aggregate_records
from pff_fa_ai.guardrails.erc_integrity import validate_erc_batch_integrity
from pff_fa_ai.guardrails.states import GuardrailDecision


def test_should_allow_a_complete_uncontaminated_batch() -> None:
    records = [{"id": "team-1", "org": "club-123"}, {"id": "team-2", "org": "club-123"}]
    result = aggregate_records(records, key=lambda r: r["id"], expected_count=2)

    outcome = validate_erc_batch_integrity(
        result, organization_ids=(r["org"] for r in records), expected_organization_id="club-123"
    )

    assert outcome.decision is GuardrailDecision.ALLOW


def test_should_block_when_entities_are_missing() -> None:
    records = [{"id": "team-1", "org": "club-123"}]
    result = aggregate_records(records, key=lambda r: r["id"], expected_count=2)

    outcome = validate_erc_batch_integrity(
        result, organization_ids=(r["org"] for r in records), expected_organization_id="club-123"
    )

    assert outcome.decision is GuardrailDecision.BLOCK
    assert "GR-ERC-INCOMPLETE" in outcome.reason_codes


def test_should_block_on_cross_club_contamination() -> None:
    records = [{"id": "team-1", "org": "club-123"}, {"id": "team-2", "org": "club-456"}]
    result = aggregate_records(records, key=lambda r: r["id"], expected_count=2)

    outcome = validate_erc_batch_integrity(
        result, organization_ids=(r["org"] for r in records), expected_organization_id="club-123"
    )

    assert outcome.decision is GuardrailDecision.BLOCK
    assert "GR-ERC-CROSS-ORG" in outcome.reason_codes


def test_cross_org_contamination_should_take_priority_over_incompleteness() -> None:
    records = [{"id": "team-1", "org": "club-456"}]
    result = aggregate_records(records, key=lambda r: r["id"], expected_count=5)

    outcome = validate_erc_batch_integrity(
        result, organization_ids=(r["org"] for r in records), expected_organization_id="club-123"
    )

    assert outcome.reason_codes == ("GR-ERC-CROSS-ORG",)


def test_should_warn_on_resolved_duplicates() -> None:
    records = [
        {"id": "team-1", "org": "club-123"},
        {"id": "team-1", "org": "club-123"},
    ]
    result = aggregate_records(records, key=lambda r: r["id"], expected_count=1)

    outcome = validate_erc_batch_integrity(
        result,
        organization_ids=(r["org"] for r in result.records),
        expected_organization_id="club-123",
    )

    assert outcome.decision is GuardrailDecision.WARN
    assert "GR-ERC-DUPLICATE" in outcome.reason_codes
