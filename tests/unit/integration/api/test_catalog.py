from pathlib import Path

import pytest

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.integration.api.catalog import (
    ApiAuthorization,
    ApiCatalog,
    ApiCatalogEntry,
    ApiEndpoint,
    ApiExecutionPolicy,
    ApiOperation,
    load_api_catalog,
)


def _entry(api_id: str = "enterprise.club.get") -> ApiCatalogEntry:
    return ApiCatalogEntry(
        api_id=api_id,
        name="Get Club",
        version="v1",
        owner="club-service",
        domain="club",
        operation=ApiOperation.READ,
        endpoint=ApiEndpoint(method="GET", path="/api/v1/clubs/{clubId}"),
        authorization=ApiAuthorization(required=True, claims=("club.read",)),
        execution=ApiExecutionPolicy(idempotent=True, retryable=True, parallelizable=True),
    )


def test_should_register_and_get_an_entry() -> None:
    catalog = ApiCatalog()
    catalog.register(_entry())

    assert catalog.get("enterprise.club.get") is not None
    assert len(catalog) == 1


def test_should_return_none_for_unknown_api_id() -> None:
    assert ApiCatalog().get("missing") is None


def test_should_reject_duplicate_api_id() -> None:
    catalog = ApiCatalog([_entry()])

    with pytest.raises(ConfigurationError, match="Duplicate api_id"):
        catalog.register(_entry())


def test_should_load_a_single_entry_file(tmp_path: Path) -> None:
    directory = tmp_path / "api-catalog"
    directory.mkdir()
    (directory / "clubs.yaml").write_text(
        """
api_id: enterprise.club.get
name: Get Club
version: v1
owner: club-service
domain: club
operation: READ
endpoint:
  method: GET
  path: /api/v1/clubs/{clubId}
authorization:
  required: true
  claims:
    - club.read
execution:
  idempotent: true
  retryable: true
  parallelizable: true
""",
        encoding="utf-8",
    )

    catalog = load_api_catalog(directory)

    assert catalog.get("enterprise.club.get") is not None


def test_should_load_a_list_of_entries_from_one_file(tmp_path: Path) -> None:
    directory = tmp_path / "api-catalog"
    directory.mkdir()
    (directory / "teams.yaml").write_text(
        """
- api_id: enterprise.team.get
  name: Get Team
  version: v1
  owner: team-service
  domain: team
  operation: READ
  endpoint:
    method: GET
    path: /api/v1/teams/{teamId}
  authorization:
    claims: [team.read]
  execution:
    idempotent: true
    retryable: true
    parallelizable: true
- api_id: enterprise.team.list
  name: List Teams
  version: v1
  owner: team-service
  domain: team
  operation: READ
  endpoint:
    method: GET
    path: /api/v1/clubs/{clubId}/teams
  authorization:
    claims: [team.read]
  execution:
    idempotent: true
    retryable: true
    parallelizable: true
""",
        encoding="utf-8",
    )

    catalog = load_api_catalog(directory)

    assert len(catalog) == 2


def test_should_return_empty_catalog_for_missing_directory(tmp_path: Path) -> None:
    catalog = load_api_catalog(tmp_path / "does-not-exist")

    assert len(catalog) == 0


def test_should_skip_empty_yaml_files(tmp_path: Path) -> None:
    directory = tmp_path / "api-catalog"
    directory.mkdir()
    (directory / "empty.yaml").write_text("", encoding="utf-8")

    catalog = load_api_catalog(directory)

    assert len(catalog) == 0


def test_should_resolve_secret_refs_and_reject_unrecognized_fields_loudly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A `*_secret_ref` key with no matching model field must fail validation, not vanish."""
    monkeypatch.setenv("SOME_TEST_SECRET", "resolved-value")
    directory = tmp_path / "api-catalog"
    directory.mkdir()
    (directory / "clubs.yaml").write_text(
        """
api_id: enterprise.club.get
name: Get Club
version: v1
owner: club-service
domain: club
operation: READ
endpoint:
  method: GET
  path: /api/v1/clubs/{clubId}
authorization:
  claims: [club.read]
execution:
  idempotent: true
  retryable: true
  parallelizable: true
mystery_field_secret_ref: SOME_TEST_SECRET
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="Invalid API catalog entry"):
        load_api_catalog(directory)
