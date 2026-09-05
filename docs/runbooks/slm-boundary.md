# SLM Input-Masking Boundary & Token Vault Runbook

**Owner:** DPO (policy) · Security (vault operation) — ADR-D6-19 §16 · **Severity:** P1 for
any raw-PII or sensitive-class egress (QM-01/QM-04); P2 for mask-verify failures or vault
unavailability.

Implements **ADR-D6-19** (refines ADR-D6-07). The boundary transform lives in
`src/pff_fa_ai/guardrails/masking.py` (`SlmInputMasker`) with the token vault in
`src/pff_fa_ai/guardrails/token_vault.py`; the external provider decorator is
`src/pff_fa_ai/slm/masking_provider.py` (`MaskedExternalSLMProvider`). Policy is
`config/base/data-handling.yaml`.

## The two regimes

- **External / hosted SLM (`SlmPlacement.EXTERNAL`):** masking is **mandatory and
  default**. Order at the boundary: hard-block special-category / children's / secrets
  (`RESTRICTED`/`SECRET` ⇒ `hard_block`) → mask/tokenise all remaining PII and enterprise
  values → verify no raw PII remains → egress. The model's tokenised output is unmasked
  via the vault inside the boundary before use. **Fails closed:** if masking cannot be
  applied or verified, the call is blocked and routed to the self-hosted SLM (or raises
  `ModelError` when none is configured).
- **Self-hosted SLM (`SlmPlacement.SELF_HOSTED`):** masking is **optional** per task class
  (`data_handling.self_hosted`, default `raw`) because the payload never leaves the
  tenancy. Injection and output guardrails still run regardless.

Any classification absent from `egress_matrix` fails closed (treated as hard-block) in
code — do not rely on the YAML being exhaustive to be safe.

## Diagnostic steps

1. Confirm the resolved provider placement and the policy: `config/base/data-handling.yaml`
   + `config/environments/<env>/data-handling.yaml`.
2. For a suspected raw egress (QM-01/QM-04, P1): inspect the boundary egress test corpus
   and the guardrail audit; a masked payload must contain `PFFTKN-…` tokens and no raw
   value. Treat as an incident (RT-02) — CAR, strengthen mask/verify.
3. Mask-verify failures / unexpected blocks: check the detector patterns
   (`guardrails/pii.py`, `guardrails/secrets.py`) and whether callers pass known
   enterprise values via `KnownSensitiveValue`.
4. Unmask returning tokens or wrong values (QM-03): check vault TTL/scope — the mapping is
   turn/session-scoped; an expired token cannot be re-identified.

## Recovery

- **Vault unavailable:** external calls fail closed and are routed to self-host;
  self-host is unaffected. Restore the vault before re-enabling external inference.
- **Policy rollback:** revert the `data-handling.yaml` version; the external regime can be
  disabled entirely by removing the Hugging Face egress allowlist entry (ADR-D6-04).
- Never send raw data to an external model to "unblock" a flow; never widen a
  classification to `can_send_external` without DPO sign-off.

## Escalation

DPO owns the egress matrix and any change to hard-blocks; Security operates the vault and
handles suspected vault compromise (RSK-02). On self-host cutover (ADR-D5-10) the external
regime closes and this path becomes dormant (RT-01).
