# Tool Registry

Empty by design, same reasoning as `../api-catalog/README.md`. `load_tool_registry()` in
`src/pf_ft_ai/integration/tools/registry.py` recursively loads every `*.yaml` file under
here (doc 10 §28: `tool-registry/<domain>/<name>.yaml`) into a `ToolRegistry`, and — if given
an `ApiCatalog` — validates each tool's `source.api_id` actually exists (doc 10 §128). Real
tool definitions (`club/get.yaml`, `affiliation/get.yaml`, `team/list.yaml`, ...) are added
once the API catalog they reference is populated, starting `DEVELOPMENT-GUIDE.md` Phase 23.
