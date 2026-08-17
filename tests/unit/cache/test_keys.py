from pf_ft_ai.cache.keys import build_cache_key


def test_should_build_a_deterministic_key_for_identical_inputs() -> None:
    key_a = build_cache_key(
        tenant_id="tenant-1",
        organization_id="club-123",
        resource="club",
        operation="get",
        parameters={"club_id": "club-123"},
        version="v2",
    )
    key_b = build_cache_key(
        tenant_id="tenant-1",
        organization_id="club-123",
        resource="club",
        operation="get",
        parameters={"club_id": "club-123"},
        version="v2",
    )

    assert key_a == key_b


def test_should_be_insensitive_to_parameter_ordering() -> None:
    key_a = build_cache_key(
        tenant_id="tenant-1",
        organization_id="club-123",
        resource="club",
        operation="get",
        parameters={"a": 1, "b": 2},
        version="v2",
    )
    key_b = build_cache_key(
        tenant_id="tenant-1",
        organization_id="club-123",
        resource="club",
        operation="get",
        parameters={"b": 2, "a": 1},
        version="v2",
    )

    assert key_a == key_b


def test_should_isolate_keys_by_tenant() -> None:
    key_a = build_cache_key(
        tenant_id="tenant-a",
        organization_id="club-123",
        resource="club",
        operation="get",
        parameters={"club_id": "club-123"},
        version="v2",
    )
    key_b = build_cache_key(
        tenant_id="tenant-b",
        organization_id="club-123",
        resource="club",
        operation="get",
        parameters={"club_id": "club-123"},
        version="v2",
    )

    assert key_a != key_b


def test_should_isolate_keys_by_organization() -> None:
    key_a = build_cache_key(
        tenant_id="tenant-1",
        organization_id="club-123",
        resource="club",
        operation="get",
        parameters={},
        version="v2",
    )
    key_b = build_cache_key(
        tenant_id="tenant-1",
        organization_id="club-456",
        resource="club",
        operation="get",
        parameters={},
        version="v2",
    )

    assert key_a != key_b


def test_should_isolate_keys_by_schema_version() -> None:
    key_a = build_cache_key(
        tenant_id="tenant-1",
        organization_id=None,
        resource="club",
        operation="get",
        parameters={},
        version="v1",
    )
    key_b = build_cache_key(
        tenant_id="tenant-1",
        organization_id=None,
        resource="club",
        operation="get",
        parameters={},
        version="v2",
    )

    assert key_a != key_b


def test_should_change_key_when_parameters_differ() -> None:
    key_a = build_cache_key(
        tenant_id="tenant-1",
        organization_id=None,
        resource="club",
        operation="get",
        parameters={"club_id": "club-123"},
        version="v2",
    )
    key_b = build_cache_key(
        tenant_id="tenant-1",
        organization_id=None,
        resource="club",
        operation="get",
        parameters={"club_id": "club-456"},
        version="v2",
    )

    assert key_a != key_b
