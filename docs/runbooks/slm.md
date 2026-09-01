# SLM Runbook

**Owner:** AI Platform / Model Team (doc 28 §4) · **Severity:** usually P2, P1 if no fallback is configured and the platform can't respond at all (doc 28 §9).

## Symptoms (doc 28 §48)

Timeout, 5xx, 429, provider unavailable, malformed output, latency spike.

## Diagnostic steps

1. Identify the environment and the deployed model config: `config/base/slm.yaml` +
   `config/environments/<env>/slm.yaml` (`slm.provider`, `slm.model_id`, `fallback`).
2. Check circuit state — `SlmService` (`src/pff_fa_ai/slm/service.py`) owns one
   `CircuitBreaker` per instance; a P2 "SLM degraded" alert usually means it's
   `OPEN` (`CircuitState.OPEN`, `src/pff_fa_ai/integration/execution/circuit.py`).
   `SlmService._fallback_or_raise()` is what returns `SlmExecutionResult.status ==
   FALLBACK` — check whether requests are already failing over.
3. Check `_TRANSIENT_STATUS_CODES` classification (`slm/service.py`) — only
   429/500/502/503/504 retry; anything else fails immediately by design.
4. If self-hosted (not yet in production — doc 15/ADR): check GPU/VRAM/model-loading
   per doc 28 §32/§50 (no code path exists for this yet, since only the mock and
   Hugging Face providers are implemented — `src/pff_fa_ai/slm/providers.py`).
5. Check whether the request itself was rejected by a guardrail first
   (`GuardrailBoundary.MODEL` is mandatory-fail-closed — `guardrails/states.py`)
   before assuming the SLM provider is at fault.

## Recovery

- If circuit is `OPEN` and cooldown hasn't elapsed: wait for `CircuitBreakerSettings.cooldown_seconds`
  (config) — do not manually force-close it without confirming the provider recovered.
- If no `fallback` is configured and the primary is down: this is a P1 (doc 28 §9
  "Production SLM outage with no approved fallback") — escalate immediately rather
  than attempting a workaround; never route to an unapproved model (doc 26 §97).
- Never fabricate an SLM response to "unblock" a workflow.

## Escalation

AI Platform / Model Team → provider status page / support if the primary provider
(Hugging Face API, per doc 15) is confirmed down.
