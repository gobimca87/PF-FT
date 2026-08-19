# Tool Registry

`load_tool_registry()` in `src/pf_ft_ai/integration/tools/registry.py` recursively loads
every `*.yaml` file under here (doc 10 §28: `tool-registry/<domain>/<name>.yaml`) into a
`ToolRegistry`, and — if given an `ApiCatalog` — validates each tool's `source.api_id`
actually exists (doc 10 §128).

`affiliation/tools.yaml` (Phase 23) registers the 7 tools matching
`../api-catalog/affiliation.yaml`'s entries, each restricted to `allowed_agents:
[affiliation_agent]` (doc 10 §46 deny-by-default). Further domains get their own
`<domain>/tools.yaml` once a business agent needing them is built.
