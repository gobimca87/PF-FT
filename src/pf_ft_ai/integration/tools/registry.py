from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError as PydanticValidationError

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.common.validation import format_validation_error
from pf_ft_ai.configuration.loader import resolve_secret_refs
from pf_ft_ai.configuration.secrets import EnvVarSecretResolver, SecretResolver
from pf_ft_ai.integration.api.catalog import ApiCatalog
from pf_ft_ai.integration.tools.models import ToolDefinition


class ToolRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition, *, catalog: ApiCatalog | None = None) -> None:
        """doc 10 §128: tool registration must reference a real, registered API."""
        if definition.tool_id in self._definitions:
            raise ConfigurationError(f"Duplicate tool_id in registry: {definition.tool_id}")
        if catalog is not None and catalog.get(definition.source.api_id) is None:
            raise ConfigurationError(
                f"Tool '{definition.tool_id}' references unknown api_id "
                f"'{definition.source.api_id}'"
            )
        self._definitions[definition.tool_id] = definition

    def get(self, tool_id: str) -> ToolDefinition | None:
        return self._definitions.get(tool_id)

    def is_agent_allowed(self, tool_id: str, agent_id: str) -> bool:
        """doc 10 §46: tools without an explicit allow-list permit no agent (deny-by-default)."""
        definition = self.get(tool_id)
        if definition is None:
            return False
        return agent_id in definition.allowed_agents

    def __len__(self) -> int:
        return len(self._definitions)


def load_tool_registry(
    directory: Path,
    *,
    catalog: ApiCatalog | None = None,
    secret_resolver: SecretResolver | None = None,
) -> ToolRegistry:
    """doc 10 §28, §123: tool_registry/<domain>/<name>.yaml; `*_secret_ref` keys are
    resolved the same way as every other configuration category."""
    registry = ToolRegistry()
    if not directory.is_dir():
        return registry

    resolver = secret_resolver or EnvVarSecretResolver()
    for path in sorted(directory.rglob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not raw:
            continue
        definitions = raw if isinstance(raw, list) else [raw]
        for definition_data in definitions:
            resolved = resolve_secret_refs(definition_data, resolver)
            try:
                definition = ToolDefinition.model_validate(resolved)
            except PydanticValidationError as exc:
                raise ConfigurationError(
                    f"Invalid tool definition in {path}: {format_validation_error(exc)}"
                ) from exc
            registry.register(definition, catalog=catalog)

    return registry
