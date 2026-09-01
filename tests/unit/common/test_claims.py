from pff_fa_ai.common.claims import ClaimsContext


def test_should_default_roles_and_permissions_to_empty() -> None:
    claims = ClaimsContext(subject="user-1", organization="club-1")

    assert claims.roles == ()
    assert claims.permissions == ()
