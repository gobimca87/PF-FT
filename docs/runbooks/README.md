# Operations Runbooks

Phase 22 (doc 28) — component-specific troubleshooting runbooks, wired to this
codebase's actual implementation rather than left as abstract doc-28 prose. Each
runbook below follows doc 28's structure (Symptoms → Diagnostic steps → Recovery →
Escalation) and references real files/functions so an operator can act immediately.

**What "wired" means here**: no environment is deployed yet (Phase 19's IaC/manifest
tool decision is still deferred — `docs/adr/0003-deferred-decisions-log.md`), so these
runbooks cannot link to a live dashboard or paging system. They *are* the on-call
documentation for now; once a real environment and alerting stack exist, wire actual
alert links into the "Diagnostic steps" section of each file without changing its
structure. The daily/weekly/monthly operational checklists (doc 28 §135-137) **are**
implemented as real scheduled code — see `src/pff_fa_ai/operations/` and
`.github/workflows/operational-checks.yml`.

## Severity (doc 28 §8-12)

| Level | Meaning | Examples |
|---|---|---|
| P1 — Critical | Platform unavailable, authorization/security bypass, large-scale workflow failure | See `docs/runbooks/guardrail.md`, `prompt-injection-incident.md` |
| P2 — High | Major latency degradation, RAG unavailable, large Service Bus backlog, SLM degraded | See per-component runbooks below |
| P3 — Medium | Limited degradation, individual agent/dependency failures | — |
| P4 — Low | Documentation, low-impact telemetry, minor config issues | — |

## Incident lifecycle (doc 28 §13)

`Alert → Acknowledge → Classify → Correlate → Diagnose → Contain → Recover → Validate → Monitor → Close → RCA`

Always start with `correlation_id` (`x-correlation-id` header / `request.state.correlation_id`,
`src/pff_fa_ai/api/app.py`'s `add_correlation_context` middleware) — every runbook below
assumes it's in hand.

## Escalation (doc 28 §116, trimmed to what this codebase actually owns)

| Dependency | Escalate to |
|---|---|
| AI Runtime / FastAPI / LangGraph / Agents | AI Platform Team |
| SLM | AI Platform / Model Team |
| RAG / Vector | AI Platform / Data Team |
| Enterprise APIs | Enterprise Integration Team |
| MCP | AI Platform / Integration (not implemented yet — see `mcp.md`) |
| Service Bus | Integration / Platform |
| Security incident (guardrail bypass, prompt injection, data leakage) | Security Team — immediately, before completing any checklist (doc 28 §118) |

## Component runbooks

- [`slm.md`](slm.md)
- [`enterprise-api.md`](enterprise-api.md)
- [`rag.md`](rag.md)
- [`vector.md`](vector.md)
- [`mcp.md`](mcp.md)
- [`service-bus-dlq.md`](service-bus-dlq.md)
- [`erc-batch-recovery.md`](erc-batch-recovery.md)
- [`guardrail.md`](guardrail.md)
- [`prompt-injection-incident.md`](prompt-injection-incident.md)

## Operational checklists (doc 28 §135-137)

Implemented as real code, not just a markdown checkbox list:

- `src/pff_fa_ai/operations/checks.py` — `configuration_check()`, `architecture_check()`,
  `dependency_check()`, `platform_health_check()`.
- `src/pff_fa_ai/operations/registry.py` — `build_default_checklist()` assigns each
  check to DAILY/WEEKLY/MONTHLY per doc 28's own checklist item placement.
- `.github/workflows/operational-checks.yml` — cron-scheduled CI runs each cadence.
- `scripts/run_operational_checklist.py` — the CLI entrypoint the workflow calls.
