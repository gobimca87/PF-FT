"""doc 22 §100 "Test Fixtures": centralized, reusable test data builders. These are
plain factory functions (not pytest fixtures) so both pytest-fixture-style tests and
plain test functions across every layer can call them directly."""

from __future__ import annotations

from pf_ft_ai.common.claims import ClaimsContext


def make_claims(
    *,
    subject: str = "user-1",
    organization: str = "club-1",
    roles: tuple[str, ...] = (),
    permissions: tuple[str, ...] = (),
    access_token: str | None = None,
) -> ClaimsContext:
    return ClaimsContext(
        subject=subject,
        organization=organization,
        roles=roles,
        permissions=permissions,
        access_token=access_token,
    )


def make_enterprise_record(*, entity_id: str, entity_type: str = "team") -> dict[str, str]:
    """A minimal synthetic enterprise record shape (doc 22 §98 "Synthetic" test data)
    for exercising batching/aggregation without depending on a real API contract."""
    return {"id": entity_id, "type": entity_type, "status": "ACTIVE"}


def make_enterprise_records(count: int, *, entity_type: str = "team") -> list[dict[str, str]]:
    return [
        make_enterprise_record(entity_id=f"{entity_type}-{index}", entity_type=entity_type)
        for index in range(1, count + 1)
    ]
