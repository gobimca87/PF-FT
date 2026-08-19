# Guardrail Failure Runbook

**Owner:** AI Platform / Security (doc 28 §4) · **Severity:** P1 (doc 28 §9 —
"Authorization boundary failure", "Security bypass").

## Symptoms (doc 28 §87)

Guardrail service/logic fails to evaluate (raises instead of returning a decision),
unexpectedly permissive behavior, unexpected `BLOCK` on legitimate requests.

## Diagnostic steps

1. Identify the boundary — `GuardrailBoundary` (`src/pf_ft_ai/guardrails/states.py`):
   `INPUT`, `INJECTION`, `AUTHORIZATION_CONTEXT`, `DATA`, `PROMPT`, `TOOL`, `MODEL`,
   `OUTPUT`, `RESPONSE`.
2. Check whether the boundary is mandatory-fail-closed —
   `_MANDATORY_FAIL_CLOSED_BOUNDARIES` (`guardrails/states.py`): `AUTHORIZATION_CONTEXT`,
   `TOOL`, `MODEL`, `DATA` can **never** be opted into fail-open, even by
   configuration (`GuardrailPipeline.allow_fail_open()` rejects the attempt —
   `guardrails/pipeline.py`). If one of these boundaries is blocking everything, that
   is very likely correct behavior given a genuine upstream failure, not a bug to
   route around.
3. For a non-mandatory boundary, check whether it was explicitly opted into fail-open
   (`GuardrailPipeline._fail_open_boundaries`) — if so, a policy exception is
   producing `WARN` instead of `BLOCK` on raise, which is expected for that boundary
   only.
4. Check individual policy results — `SecretDetectionPolicy`, `PiiDetectionPolicy`,
   `AuthorizationContextPolicy` (`guardrails/secrets.py`, `pii.py`, `authorization.py`)
   each report their own `GuardrailResult` with `reason_codes`.

## Recovery

- **Never disable a mandatory-fail-closed guardrail to force a request through**
  (doc 28 §87, §152). This applies even under P1 pressure — a broken authorization
  check failing closed is the guardrail working as designed.
- If a guardrail policy itself is broken (raising unexpectedly on valid input), fix
  and redeploy the policy — do not patch around it by allow-listing the specific
  request in production.
- Return the platform's controlled error response; do not attempt to reconstruct what
  the guardrail "would have" allowed.

## Escalation

Security Team immediately for anything resembling an authorization or security-control
failure — do not wait to complete the full diagnostic checklist first (doc 28 §118).
