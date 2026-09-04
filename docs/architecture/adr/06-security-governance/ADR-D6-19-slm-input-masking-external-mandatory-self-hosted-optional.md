---
id: ADR-D6-19
title: SLM input masking regime — mandatory for external, optional for self-hosted
domain: 6 Security & Governance
ws_ref: [WS-27]
status: Proposed
version: 1.0.0
date: 2026-09-04
decision_owner: Data Protection Officer
contributors: [Security Architect, AI Architecture Lead]
reviewers: [Principal Architect, AI Governance Lead]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D6-07, ADR-D6-06, ADR-D6-04, ADR-D3-13, ADR-D3-14, ADR-D6-16, ADR-D7-04, ADR-D6-09]
source_docs:
  - "MD files/5 QualityGovernance/19.PFF-FA-AI-SECURITY.md §22, §23, §24"
  - "MD files/4 AI/18.PFF-FA-AI-GUARDRAILS.md §62, §69, §70, §71"
  - "MD files/4 AI/15.PFF-FA-AI-SLM.md §124, §125, §126"
build_phases: [6, 20]
impacted_paths:
  - src/pff_fa_ai/slm/
  - src/pff_fa_ai/guardrails/
classification: Confidential
review_due: 2027-09-04
---

# ADR-D6-19 — SLM input masking regime — mandatory for external, optional for self-hosted

## 1. Summary

PFF AI adopts an explicit **two-regime masking rule** for data sent to a language model,
strengthening ADR-D6-07 from "minimise, redact and hard-block the most sensitive classes"
into a testable default: for an **external / hosted SLM** (any inference endpoint outside
the Azure tenancy), **every payload MUST be masked before egress** — all personal data
and enterprise-record values are replaced with reversible tokens or masked, so that **no
raw PII and no raw enterprise records ever leave the tenancy** — while special-category
data, children's personal data and secrets remain hard-blocked entirely (ADR-D6-16). For a
**self-hosted SLM** (in-tenancy vLLM/TGI on AKS), masking is **optional** — raw or masked
data may be used, chosen per task class, because the data never crosses the trust
boundary. A tenancy-internal **token vault** (extending ADR-D6-06) maps tokens to original
values so masked model outputs can be re-identified inside the boundary before use.

## 2. Context and Problem Statement

ADR-D6-07 already establishes the external-vs-self-hosted data boundary and is the
upstream decision here. But it encodes the rule as *"only the minimum non-personal,
redacted text"* may leave, with hard blocks on the most sensitive classes — a
**minimisation** posture. Two things the platform's data owners require are therefore not
yet stated unambiguously, and 19.PFF-FA-AI-SECURITY.md §23–§24, 18.PFF-FA-AI-GUARDRAILS.md §70–§71 and
15.PFF-FA-AI-SLM.md §124–§126 inherit the same softness:

1. **The absolute external rule.** "Minimise and redact" leaves room for a code path to
   send a personal or enterprise-record value it did not recognise as sensitive. The
   required rule is stronger and binary: *nothing raw goes to an external model* — PII and
   enterprise values are masked/tokenised as a matter of course, not only when a detector
   fires, and the boundary **fails closed** if it cannot verify masking.
2. **The self-hosted permission.** The docs only ever describe self-host as the place
   sensitive flows are *routed to*; nowhere do they state plainly that **raw data is
   permitted** to a self-hosted model. Implementers are left to infer it. The
   self-hosted-boundary description (18.PFF-FA-AI-GUARDRAILS.md §71) simply omits a redaction step, which
   is an *implication*, not a decision.

A third gap is mechanical: ADR-D6-06 adopts reversible tokenisation only for *identifiers*
"where referential utility is needed", not as a general mask-in / unmask-out path for SLM
calls. Without a defined token vault, a masked external call cannot map the model's
tokenised output back to real values inside the tenancy, so masking would break otherwise
workable flows.

Left as-is, the strongest privacy control the platform advertises (external egress
protection) rests on detector recall and reviewer diligence rather than on a default-safe
transform. This ADR closes all three gaps.

## 3. Decision Drivers

### 3.1 Functional drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | External payloads must be masked/tokenised by default, not only on detector hit | 19.PFF-FA-AI-SECURITY.md §23; ADR-D6-07 §7 |
| DR-F-02 | Self-hosted SLM may receive raw or masked data, stated explicitly | 19.PFF-FA-AI-SECURITY.md §24; 18.PFF-FA-AI-GUARDRAILS.md §71 |
| DR-F-03 | Masked external outputs must be re-identifiable inside the tenancy | ADR-D6-06 §5.5, §8 |
| DR-F-04 | Enforced at the external-SLM guardrail boundary, fail-closed | 18.PFF-FA-AI-GUARDRAILS.md §70; ADR-D6-09 |

### 3.2 Non-functional drivers

| ID | Driver | Target | Source |
|---|---|---|---|
| DR-N-01 | Masking must not add material turn latency | Within latency budget | ADR-D5-18 |
| DR-N-02 | Token vault reads/writes are tenancy-internal only | No vault data egresses | ADR-D6-05 |

### 3.3 Constraints

| ID | Constraint | Type | Source |
|---|---|---|---|
| DR-C-01 | Special-category, children's data and secrets are never sent externally, masked or not | Regulatory | ADR-D6-16; ADR-D6-07 §7 |
| DR-C-02 | Raw enterprise records are never sent raw externally | Platform | ADR-D6-07 §10 |
| DR-C-03 | Masking is a *transform at the boundary*, not a business decision | Platform | ADR-D6-09 |
| DR-C-04 | The token vault is a Confidential store with controlled reverse access | Regulatory | ADR-D6-06 §8; ADR-D6-05 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Masking preserves enough utility for external flows to work | Route more flows to self-host earlier (ADR-D3-13) | Flow-level utility test |
| DR-A-02 | A reversible token vault is affordable at expected volumes | Restrict tokenisation to identifiers, mask the rest irreversibly | Vault sizing (Phase 20) |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | No raw PII / enterprise data egress | 34 | The core requirement | Boundary egress tests |
| EC-02 | Enforceability & fail-closed at boundary | 22 | Default-safe, not detector-dependent | Guardrail coverage |
| EC-03 | Utility (external flows still work, outputs re-identifiable) | 18 | Ship value; reversibility | Flows enabled + unmask correctness |
| EC-04 | Clarity of the two-regime rule | 14 | Team follows it consistently | Policy legibility |
| EC-05 | Cost / complexity (vault, transform) | 12 | Sustainable | Build + run cost |
| | **Total** | **100** | | |

Scoring scale: **1** unacceptable · **2** poor · **3** adequate · **4** good · **5** excellent.

## 5. Alternatives Considered

### 5.1 Option A — Keep ADR-D6-07 as-is (minimise + redact-on-detection + hard-block sensitive)

**Description.** Retain the current minimisation posture; redact PII when a detector fires;
hard-block special-category/children's/secrets; no default masking of all values.
**Strengths.** Already decided; lowest effort; keeps most flows working.
**Weaknesses.** External safety depends on detector recall; an unrecognised personal or
enterprise value can egress raw; self-hosted permission stays implicit. Fails EC-01/EC-02
against the stricter requirement.
**Cost / effort.** None.

### 5.2 Option B — Two-regime masking: mandatory mask/tokenise for external (fail-closed), optional for self-hosted, with a reversible token vault

**Description.** External calls pass through a mandatory masking transform at the boundary
guardrail; all PII and enterprise values are tokenised (reversible) or masked before
egress; special-category/children's/secrets stay hard-blocked; the boundary fails closed
if masking cannot be verified. Self-hosted calls may use raw or masked data per task
class. A tenancy-internal token vault maps tokens ↔ values so external outputs are
re-identified inside the boundary.
**Strengths.** Default-safe (not detector-dependent); explicit self-host permission;
preserves referential utility and output re-identification; testable and fail-closed.
**Weaknesses.** Token vault to build and secure; masking may reduce free-text utility.
**Cost / effort.** Medium.

### 5.3 Option C — Block all external SLM; self-host only from day one

**Description.** No external inference at all; all flows on the self-hosted SLM.
**Strengths.** Maximum protection; no masking needed.
**Weaknesses.** Contradicts the phased ADR-D3-13 strategy; delays time-to-value; GPU ops
up front. (Already rejected as Option C in ADR-D6-07.)
**Cost / effort.** High up-front.

### 5.4 Option D — Format-preserving encryption of all fields for external

**Description.** Encrypt every field with an FPE scheme before egress; decrypt outputs.
**Strengths.** Strong confidentiality; reversible.
**Weaknesses.** Ciphertext is poor model input (destroys the semantics the model needs);
key-management burden (ADR-D6-05); heavier than tokenisation for little added protection
over B.
**Cost / effort.** High.

### 5.5 Option E — Irreversible anonymisation of everything for external

**Description.** Strip/anonymise all identifiers and PII irreversibly before egress.
**Strengths.** No vault; strong against re-identification.
**Weaknesses.** Cannot map the model's output back to real values, breaking any flow that
needs the result tied to a record; free-text anonymisation is imperfect (residual
re-identification risk, per ADR-D6-07 §5.4). Fails EC-03.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Send raw to external, rely on provider DPA | ADR-D6-07 §5.2 — unacceptable GDPR/safeguarding risk |
| Mandatory masking for self-hosted too | Over-restrictive — data never leaves the trust boundary (DR-F-02) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by ADR-D6-07, ADR-D6-06 and the specs
(19.PFF-FA-AI-SECURITY.md §22–§24; 18.PFF-FA-AI-GUARDRAILS.md §69–§71; 15.PFF-FA-AI-SLM.md §124–§126).

| Criterion | Weight | A: As-is | B: Two-regime masking + vault | C: Block external | D: FPE all | E: Anonymise all |
|---|---|---|---|---|---|---|
| EC-01 No raw egress | 34 | 3 | 5 | 5 | 5 | 5 |
| EC-02 Enforceability | 22 | 3 | 5 | 5 | 4 | 4 |
| EC-03 Utility & reversibility | 18 | 4 | 5 | 2 | 3 | 1 |
| EC-04 Clarity | 14 | 3 | 5 | 4 | 3 | 3 |
| EC-05 Cost/complexity | 12 | 5 | 3 | 3 | 2 | 4 |
| **Weighted total** | **100** | **342** | **476** | **408** | **378** | **366** |

Totals: **B = 476**, **C = 408**, **D = 378**, **E = 366**, **A = 342**.

**Sensitivity.** B leads by 68 points over the next option. Its only weaker criterion is
EC-05 (the token vault); if DR-A-02 proves the vault too costly, B degrades gracefully to
"tokenise identifiers, mask the rest irreversibly" — i.e. toward E for free text while
keeping reversibility where it matters. Block-all (C) remains the strategic end-state once
self-hosting lands (ADR-D5-10), at which point the external regime is closed entirely and
this ADR's external half falls away.

## 7. Decision

**PFF AI will enforce a two-regime SLM input masking rule (Option B).** For any external
/ hosted SLM endpoint outside the Azure tenancy, the external-SLM boundary guardrail
(18.PFF-FA-AI-GUARDRAILS.md §70; ADR-D6-09) **must** apply a masking transform to every payload before
egress: all personal data and enterprise-record values are replaced with reversible
tokens or masked, so no raw PII and no raw enterprise records leave the tenancy;
special-category data, children's personal data and secrets are hard-blocked entirely and
are never sent even in masked form (ADR-D6-16, DR-C-01). The boundary **fails closed** —
if masking cannot be applied or verified, the call is blocked and the flow routed to the
self-hosted SLM. For the self-hosted SLM inside the tenancy, masking is **optional**: raw
or masked data may be used, chosen per task class, because the payload never crosses the
trust boundary; injection and output guardrails remain mandatory regardless. A
tenancy-internal **token vault** (extending ADR-D6-06 from identifiers to a general
mask-in / unmask-out mechanism) maps tokens to original values under controlled reverse
access, so a masked external model output is re-identified inside the boundary before use.

This **refines and strengthens ADR-D6-07; it does not supersede it** — the boundary,
hard-blocks, routing and self-host-priority of D6-07 all stand, and this ADR makes the
external transform mandatory-and-default rather than minimisation-on-detection and states
the self-hosted permission explicitly. Block-all (C) is the post-self-host end-state, not
the current base policy; FPE (D) and irreversible anonymisation (E) are rejected on model
utility and reversibility; as-is (A) is insufficient against the stricter requirement.

**Status rationale.** `Proposed`. It tightens a Confidential data-egress control and adds
a token vault with GDPR implications; it awaits **Architecture Review Board** sign-off with
the **Data Protection Officer** as decision owner (DPIA update, ADR-D6-16), plus a Phase 20
vault-sizing validation of DR-A-02. Ratification moves it to `Accepted` per ADR-D0-04.

## 8. Architecture Detail

- **Boundary transform.** The external-SLM boundary guardrail gains a mandatory
  `mask(payload) → (masked_payload, token_map)` step in `src/pff_fa_ai/guardrails/`,
  invoked by the SLM provider abstraction (ADR-D3-14) whenever the resolved provider is
  external. Order at the boundary: classify → hard-block special-category/children's/secrets
  (ADR-D6-16) → **mask/tokenise all remaining PII and enterprise values** → verify no raw
  PII remains → egress. Verification failure ⇒ block + route to self-host (fail-closed).
- **Token vault.** A Confidential, tenancy-internal store (Redis/Key Vault-backed per
  ADR-D4-10 / ADR-D6-05) holding `token ↔ value` with a short TTL scoped to the turn/session
  and controlled reverse access (audited, ADR-D6-17). It is the ADR-D6-06 §8 "controlled
  reverse path", generalised from identifiers to the SLM mask/unmask path. Vault contents
  never egress (DR-N-02).
- **Unmask on return.** For external calls, the model's (tokenised) output is passed back
  through `unmask(output, token_map)` inside the boundary before the result is used, so
  downstream code sees real values. Structured-output validation (ADR-D3-17) runs on the
  unmasked result.
- **Self-hosted path.** When the resolved provider is self-hosted, the mask step is
  governed by a per-task-class `masking: raw | masked` setting (default `raw`), reflecting
  that the data stays in-tenancy. Injection/prompt and output guardrails (ADR-D6-08,
  ADR-D6-09) still run.
- **Configuration.** A new `config/base/data-handling.yaml` (versioned, ADR-D5-06) holds
  the per-classification egress matrix (PUBLIC/INTERNAL/CONFIDENTIAL/RESTRICTED/SECRET →
  `can_send_external`, `mask_required`, `hard_block`) referenced by 18.PFF-FA-AI-GUARDRAILS.md §69,
  and the self-hosted per-task-class `masking` defaults. Detector/masker policy config sits
  alongside `config/base/guardrails.yaml`.
- **Phase-out.** On self-host cutover (ADR-D3-13 / ADR-D5-10) the external regime closes,
  the HF egress allowlist entry is removed (ADR-D6-04), and the mandatory-mask path becomes
  dormant — matching ADR-D6-07 RT-01.

```mermaid
flowchart LR
    P[Generation payload] --> R{Provider resolved}
    R -- self-hosted --> SH[masking: raw|masked per task class<br/>injection/output guardrails] --> M1[In-tenancy SLM]
    R -- external --> HB{special-category /<br/>children's / secret?}
    HB -- yes --> BLK[Hard-block → route to self-host]
    HB -- no --> MK[Mask/tokenise ALL PII + enterprise values<br/>verify no raw PII] --> EG[Egress to external SLM]
    EG --> UN[unmask output via token vault<br/>inside boundary] --> V[validate + use]
    MK -. cannot verify .-> BLK
```

## 9. Consequences

### 9.1 Positive

- External safety no longer depends on detector recall — masking is the default transform.
- The self-hosted "raw permitted" permission is explicit, unblocking implementers.
- Reversible tokenisation lets masked external flows work end-to-end (output re-identified).
- The rule is binary and testable, which strengthens the DPIA and audit story.

### 9.2 Negative

- A token vault must be built, secured, sized and operated.
- Masking can reduce free-text utility, pushing some flows to self-host sooner.

### 9.3 Neutral

- The external regime is transitional; it closes on self-host cutover.
- Reinforces ADR-D6-07 rather than replacing it.

### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Full raw context to an external model | No raw PII/enterprise data ever leaving the tenancy | DPO |
| Simplicity (a vault to run) | Reversibility and end-to-end masked flows | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise systems decide and execute; the AI platform interprets, orchestrates, contextualises, explains, communicates | Masking is a boundary transform on data sent for language generation; it changes nothing the enterprise decides or executes. |
| Authoritative-truth precedence | The external model is lowest authority; masking further limits what it even sees. Unmasking restores enterprise values inside the boundary before use. |
| Four-state separation | Enterprise Business State values are tokenised before egress; the token vault is a controlled, tenancy-internal mapping, not a new state store conflated with the others. |
| Versioned artefacts, never mutated in place | The data-handling matrix and masking policy are versioned config released in the bundle (ADR-D5-06, ADR-D6-15). |
| Adam persona governs *how*, never *what* | Not applicable — masking is a data-protection transform, independent of persona. |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | A raw personal/enterprise value egresses despite the rule | Low | Critical | H | Default mask-all (not detector-only) + verify step + fail-closed + egress tests (QM-01) | DPO | Low |
| RSK-02 | Token vault compromise re-identifies masked data | Low | High | M | Confidential store, short TTL, controlled+audited reverse access (ADR-D6-05/D6-17) | Security Architect | Low |
| RSK-03 | Masking degrades external output quality | Med | Med | M | Per-task-class utility tests; route low-utility flows to self-host; compose with ADR-D3-28 refinement | AI Arch Lead | Med |
| RSK-04 | Vault cost/latency at volume (DR-A-02) | Med | Med | M | Phase 20 sizing; degrade to identifier-only tokenisation + irreversible mask for free text | FinOps | Med |
| RSK-05 | Self-hosted "raw" misread as "no guardrails" | Low | High | M | Explicit: injection/output guardrails remain mandatory for self-host (§8) | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Raw PII / enterprise-record values in external payloads | 0 | > 0 | Boundary egress tests | Continuous |
| QM-02 | External payloads passing the mask+verify step | 100% | < 100% | Guardrail audit | Per release |
| QM-03 | Unmask correctness (output re-identified to right value) | 100% | < 100% | Round-trip tests | Per release |
| QM-04 | Special-category/children's/secret egress (masked or not) | 0 | > 0 | Boundary tests | Continuous |
| QM-05 | Token-vault reverse accesses audited | 100% | < 100% | Audit log (ADR-D6-17) | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Adds a token vault (new Confidential store) and a boundary transform; both tenancy-internal with controlled access. |
| Data classification touched | Confidential — governs Personal and enterprise-record data at the egress boundary. |
| Personal data / PII | No raw PII leaves the tenancy for external inference; masked/tokenised only, sensitive classes hard-blocked. |
| Children's data and safeguarding | Children's personal data is never sent externally, masked or not (DR-C-01) — unchanged from ADR-D6-16/D6-07. |
| UK GDPR lawful basis and rights impact | Strengthens the international-transfer and minimisation controls; DPIA updated for the token vault. |
| Audit and evidential requirements | Masking outcomes and every vault reverse access are logged (ADR-D6-17). |
| Standards touched | UK GDPR, ISO/IEC 27701, 27001, 42001; NIST AI RMF MAP/MANAGE. |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 (external phase — mandatory masking), 20 (vault sizing, tighten on self-host approach) |
| Repository paths | `src/pff_fa_ai/guardrails/` (mask/verify at boundary), `src/pff_fa_ai/slm/` (provider hook), token vault module; `config/base/data-handling.yaml` (new) |
| Configuration | Per-classification egress matrix; self-hosted per-task-class `masking` defaults; masker/detector policy |
| Contracts / schemas | `MaskingResult` / `token_map` boundary models; classification enum reused from 18.PFF-FA-AI-GUARDRAILS.md §68 |
| Migration | Strengthens ADR-D6-07's guardrail from redact-on-detection to mandatory mask-all; additive vault; self-host default `raw` |
| Dependencies on other ADRs | ADR-D6-07 (refines), ADR-D6-06 (token vault), ADR-D3-14 (provider hook), ADR-D6-09 (boundary placement) |
| Effort estimate | M–L — masker + verify + token vault + config matrix |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | No raw PII or enterprise-record value appears in any external payload | Boundary egress test corpus |
| AC-02 | Mask step is applied to 100% of external calls and fails closed if unverifiable | Guardrail unit + fault-injection test |
| AC-03 | Special-category/children's/secret content is hard-blocked, never masked-and-sent | Boundary test |
| AC-04 | A masked external output is correctly unmasked to the original value before use | Round-trip integration test |
| AC-05 | Self-hosted calls may send raw per config, with injection/output guardrails still applied | Self-host path test |
| AC-06 | Every token-vault reverse access is authorised and audited | Audit-log assertion |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | External mask rate, verify-failure/block rate, unmask correctness, vault access volume |
| Alerting | Any raw-egress detection (QM-01), any sensitive-class egress (QM-04), mask-verify failures |
| Runbook | `docs/runbooks/slm-boundary.md` (amend) — masking + token-vault operations, reverse-access procedure |
| Failure mode and degradation | Mask cannot be verified ⇒ block + route to self-host; vault unavailable ⇒ external calls blocked (fail-closed), self-host unaffected |
| Rollback | Revert masking/data-handling policy version; external regime disabled entirely by removing the egress allowlist (ADR-D6-04) |
| Support model impact | DPO owns the policy; Security operates the vault |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Masker + verify + boundary wiring | M | small | Build + per-call transform |
| Token vault | M | small–med | Store + secure operation; sized in Phase 20 |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Self-hosted SLM live | ADR-D5-10 | Close the external regime; remove HF egress; vault path becomes dormant |
| RT-02 | Any raw-egress or sensitive-egress incident | QM-01 / QM-04 | CAR; strengthen mask/verify; supersede if design flaw |
| RT-03 | Token vault cost/latency exceeds budget (DR-A-02) | QM / Phase 20 sizing | Degrade to identifier-only tokenisation + irreversible free-text mask |

**Scheduled review:** `review_due` in the front matter. **Causal analysis:** if an
incident is traced to this decision, record it here and raise a superseding ADR rather
than editing §7 in place.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-27 Security & data protection |
| Specification sections | 19.PFF-FA-AI-SECURITY.md §22–§24; 18.PFF-FA-AI-GUARDRAILS.md §62, §68–§71; 15.PFF-FA-AI-SLM.md §124–§126 |
| Requirement IDs | SEC-SLM-MASK-* (per ADR-D1-12) |
| Build phases | 6, 20 |
| Code paths | `src/pff_fa_ai/guardrails/`, `src/pff_fa_ai/slm/` |
| Configuration | `config/base/data-handling.yaml`, `config/base/guardrails.yaml` |
| Tests | boundary egress, mask/verify, unmask round-trip, self-host path |
| Upstream ADRs | ADR-D6-07, ADR-D6-06, ADR-D3-13 |
| Downstream ADRs | ADR-D6-16, ADR-D3-14 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-09-04 | Data Protection Officer | Initial decision recorded (Proposed). Refines ADR-D6-07 into an explicit two-regime rule — mandatory mask/tokenise for external SLM (fail-closed, no raw PII/enterprise egress), optional for self-hosted — and adds a reversible token vault. Awaits ARB sign-off and Phase 20 vault sizing. |
