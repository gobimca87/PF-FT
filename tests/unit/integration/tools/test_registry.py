from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.integration.api.catalog import (
    ApiAuthorization,
    ApiCatalog,
    ApiCatalogEntry,
    ApiEndpoint,
    ApiExecutionPolicy,
    ApiOperation,
)
from pff_fa_ai.integration.tools.models import ToolDefinition, ToolExecutionPolicy, ToolSource
from pff_fa_ai.integration.tools.registry import ToolRegistry, load_tool_registry


def _api_entry() -> ApiCatalogEntry:
    return ApiCatalogEntry(
        api_id="enterprise.club.get",
        name="Get Club",
        version="v1",
        owner="club-service",
        domain="club",
        operation=ApiOperation.READ,
        endpoint=ApiEndpoint(method="GET", path="/api/v1/clubs/{clubId}"),
        authorization=ApiAuthorization(required=True, claims=("club.read",)),
        execution=ApiExecutionPolicy(idempotent=True, retryable=True, parallelizable=True),
    )


def _tool_definition(*, allowed_agents: tuple[str, ...] = ("affiliation_agent",)) -> ToolDefinition:
    return ToolDefinition(
        tool_id="club.get",
        version="1.0.0",
        description="Get club",
        source=ToolSource(api_id="enterprise.club.get"),
        input_schema_ref="ClubGetRequest",
        output_schema_ref="ClubContext",
        execution_policy=ToolExecutionPolicy(timeout_ms=10000, idempotent=True),
        allowed_agents=allowed_agents,
    )


def test_should_register_and_get_a_tool() -> None:
    registry = ToolRegistry()
    registry.register(_tool_definition())

    assert registry.get("club.get") is not None
    assert len(registry) == 1


def test_should_reject_duplicate_tool_id() -> None:
    registry = ToolRegistry()
    registry.register(_tool_definition())

    with pytest.raises(ConfigurationError, match="Duplicate tool_id"):
        registry.register(_tool_definition())


def test_should_reject_tool_referencing_unknown_api_when_catalog_given() -> None:
    registry = ToolRegistry()
    empty_catalog = ApiCatalog()

    with pytest.raises(ConfigurationError, match="unknown api_id"):
        registry.register(_tool_definition(), catalog=empty_catalog)


def test_should_accept_tool_referencing_a_registered_api() -> None:
    registry = ToolRegistry()
    catalog = ApiCatalog([_api_entry()])

    registry.register(_tool_definition(), catalog=catalog)

    assert registry.get("club.get") is not None


def test_should_allow_only_agents_in_the_allow_list() -> None:
    registry = ToolRegistry()
    registry.register(_tool_definition(allowed_agents=("affiliation_agent",)))

    assert registry.is_agent_allowed("club.get", "affiliation_agent") is True
    assert registry.is_agent_allowed("club.get", "other_agent") is False


def test_should_deny_by_default_when_allow_list_is_empty() -> None:
    registry = ToolRegistry()
    registry.register(_tool_definition(allowed_agents=()))

    assert registry.is_agent_allowed("club.get", "affiliation_agent") is False


def test_should_deny_for_unknown_tool() -> None:
    assert ToolRegistry().is_agent_allowed("missing", "affiliation_agent") is False


def test_should_load_tool_definitions_from_directory(tmp_path: Path) -> None:
    directory = tmp_path / "tool-registry" / "club"
    directory.mkdir(parents=True)
    (directory / "get.yaml").write_text(
        """
tool_id: club.get
version: 1.0.0
description: Get club
source:
  api_id: enterprise.club.get
input_schema_ref: ClubGetRequest
output_schema_ref: ClubContext
execution_policy:
  timeout_ms: 10000
  idempotent: true
allowed_agents:
  - affiliation_agent
""",
        encoding="utf-8",
    )

    registry = load_tool_registry(tmp_path / "tool-registry")

    assert registry.get("club.get") is not None


def test_should_return_empty_registry_for_missing_directory(tmp_path: Path) -> None:
    registry = load_tool_registry(tmp_path / "does-not-exist")

    assert len(registry) == 0


def test_should_skip_empty_yaml_files(tmp_path: Path) -> None:
    directory = tmp_path / "tool-registry" / "club"
    directory.mkdir(parents=True)
    (directory / "empty.yaml").write_text("", encoding="utf-8")

    registry = load_tool_registry(tmp_path / "tool-registry")

    assert len(registry) == 0


def test_should_resolve_secret_refs_and_reject_unrecognized_fields_loudly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A `*_secret_ref` key with no matching model field must fail validation, not vanish."""
    monkeypatch.setenv("SOME_TEST_SECRET", "resolved-value")
    directory = tmp_path / "tool-registry" / "club"
    directory.mkdir(parents=True)
    (directory / "get.yaml").write_text(
        """
tool_id: club.get
version: 1.0.0
description: Get club
source:
  api_id: enterprise.club.get
input_schema_ref: ClubGetRequest
output_schema_ref: ClubContext
execution_policy:
  timeout_ms: 10000
  idempotent: true
mystery_field_secret_ref: SOME_TEST_SECRET
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="Invalid tool definition"):
        load_tool_registry(tmp_path / "tool-registry")
