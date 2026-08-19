# Prompt Injection Incident Runbook

**Owner:** AI Platform / Security (doc 28 §4) · **Severity:** P1 (doc 28 §9 — treat as
a security incident, not a quality issue).

## Symptoms (doc 28 §88)

A user message, RAG document, tool result, or enterprise API response appears to have
caused the model to: reveal system-prompt content, ignore prior instructions, attempt
an unauthorized tool call, or otherwise act on embedded instructions rather than the
platform's own.

## Immediate actions (doc 28 §88 — do these before diagnosing root cause)

```text
Block/contain the request
Record a security event
Preserve safe evidence (correlation ID, trace, the offending content)
Do not execute any injected tool instruction
Do not expose protected/system context in the response
Escalate to Security immediately
```

## Diagnostic steps (after containment)

1. Identify the channel the injected content came through —
   `wrap_rag_evidence()`, `wrap_enterprise_api_result()`, `wrap_tool_result()`,
   `wrap_repository_content()` (`src/pf_ft_ai/guardrails/content.py`) each wrap
   content as clearly-delimited, non-instructional data. Confirm the content was
   actually wrapped through one of these before reaching the model — unwrapped raw
   content reaching a prompt is itself the root-cause bug.
2. Check `PromptComposer` (`prompt_engineering/composer.py`) — it enforces an exact
   trust-level match per `PromptSectionRole` (`_REQUIRED_TRUST`); a role/trust
   mismatch (e.g. untrusted content occupying a role that requires `TRUSTED`) raises
   `GuardrailError` rather than composing. If injected content reached a privileged
   role, look for a bug in whatever assigned that section's `trust_level` — the
   composer cannot independently verify a caller's trust claim, only that it's
   consistent with the role (see `tests/adversarial/test_prompt_injection.py` for the
   exact threat model this defends against and its limits).
3. Confirm no tool call was actually executed as a result — `ToolExecutor` only acts
   on explicit, schema-validated tool requests (`integration/tools/executor.py`); an
   injected "call this tool" instruction in prompt text has no code path to become a
   real `ToolExecutionRequest` by itself.

## Recovery

- Do not silently patch around the specific payload — identify why the structural
  containment (wrapping + trust enforcement) didn't stop it, and fix that.
- If the injection succeeded in producing an unsafe response, treat it as a data
  leakage / integrity concern too — see doc 28 §90.

## Escalation

Security Team, immediately — per doc 28 §118, do not delay escalation of a suspected
security incident to finish a checklist.
