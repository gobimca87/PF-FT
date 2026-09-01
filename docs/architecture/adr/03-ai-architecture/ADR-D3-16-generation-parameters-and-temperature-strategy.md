---
id: ADR-D3-16
title: Generation parameter and temperature strategy per task class
domain: 3 AI
ws_ref: [WS-16]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [ML Engineer, Prompt Engineer]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-15, ADR-D3-17, ADR-D3-10, ADR-D3-05]
source_docs:
  - "MD files/4 AI/15.PFF-FA-AI-SLM.md §33, §34, §35, §36, §37, §38, §39, §40"
build_phases: [6]
impacted_paths:
  - config/models/
  - src/pff_fa_ai/slm/
classification: Internal
review_due: 2027-08-22
---

# ADR-D3-16 — Generation parameter and temperature strategy per task class

## 1. Summary

PFF AI will bind generation parameters (temperature, top-p, max output tokens, stop
sequences) to a **declared task class**, not to ad-hoc call sites: deterministic
tasks (structured extraction, routing rationale, tool-argument formatting) run at
**temperature 0 / low top-p**, while user-facing persona narration runs at a
**low-but-non-zero temperature** for natural tone. Parameters are declared per task
class in config (15.PFF-FA-AI-SLM.md §33–§36), never hard-coded, and never used to compensate for
missing structure or validation.

## 2. Context and Problem Statement

15.PFF-FA-AI-SLM.md §33–§36 define output-token budget and a temperature strategy; §37–§40 tie
structured output to validation and state the SLM "must not execute business rules."
Uncontrolled temperature is a correctness and safety hazard: high randomness in a
routing or extraction step produces non-reproducible, sometimes invalid results;
zero temperature everywhere makes Adam's persona flat. Without a decision, each call
site picks its own parameters, defeating reproducibility, eval and cost control.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Deterministic tasks must be reproducible | 15.PFF-FA-AI-SLM.md §36, §38 |
| DR-F-02 | Persona narration must feel natural | CLAUDE.md §Adam; ADR-D3-10 |
| DR-F-03 | Output-token budget enforced per workflow | 15.PFF-FA-AI-SLM.md §33–§34 |
| DR-N-01 | Parameters declared, versioned, not hard-coded | 15.PFF-FA-AI-SLM.md §35; CLAUDE.md |
| DR-C-01 | Temperature never substitutes for validation | 15.PFF-FA-AI-SLM.md §39–§40 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Task classes cleanly partition calls | Add finer classes | Eval per class |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Determinism for deterministic tasks | 30 | Correctness/reproducibility | Repeatability rate |
| EC-02 | Naturalness for persona output | 18 | UX/persona quality | Persona eval |
| EC-03 | Simplicity & consistency | 16 | Avoid per-call chaos | # distinct configs |
| EC-04 | Cost control (token budgets) | 14 | Spend management | tokens/workflow |
| EC-05 | Versioned & auditable | 12 | Governance | In config? |
| EC-06 | Tunability per task | 10 | Room to optimise | Override granularity |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Parameters bound to declared task class in config

**Description.** Each task class (extraction, routing, tool-args, narration,
summarisation) has a config-declared parameter set; calls specify their class.
**Strengths.** Deterministic where needed, natural where wanted; versioned; auditable;
consistent.
**Weaknesses.** Requires disciplined task-class tagging.
**Cost / effort.** Low.

### 5.2 Option B — Single global parameter set

**Description.** One temperature/top-p for everything.
**Strengths.** Simplest.
**Weaknesses.** Either non-deterministic extraction (too high) or flat persona (too
low); no fit to task.
**Cost / effort.** Low, poor quality.

### 5.3 Option C — Per-call-site ad-hoc parameters

**Description.** Each call picks parameters inline.
**Strengths.** Maximum flexibility.
**Weaknesses.** Drift; unversioned; un-auditable; reproducibility lost.
**Cost / effort.** Low now, high chaos.

### 5.4 Option D — Model-decided (let the model self-select creativity)

**Description.** Prompt the model to modulate its own randomness.
**Strengths.** None material.
**Weaknesses.** Not how sampling works; non-deterministic; unenforceable.
**Cost / effort.** N/A — infeasible.

### 5.5 Option E — Task-class defaults + narrow per-workflow overrides

**Description.** Option A plus a governed override slot per workflow where a class
default doesn't fit.
**Strengths.** A's benefits + escape hatch; overrides are versioned and reviewed.
**Weaknesses.** Slightly more config surface.
**Cost / effort.** Low.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| High temperature for "creativity" on business flows | DR-C-01 — correctness/safety hazard |
| Random seed exposure to users | Out of scope; not meaningful for enterprise flows |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 15.PFF-FA-AI-SLM.md §33–§40.

| Criterion | Weight | A: Task-class config | B: Global | C: Ad-hoc | D: Model-decided | E: Class + overrides |
|---|---|---|---|---|---|---|
| EC-01 Determinism | 30 | 5 | 3 | 2 | 1 | 5 |
| EC-02 Naturalness | 18 | 4 | 3 | 4 | 2 | 5 |
| EC-03 Simplicity | 16 | 4 | 5 | 2 | 3 | 4 |
| EC-04 Cost control | 14 | 5 | 3 | 2 | 2 | 5 |
| EC-05 Versioned/audit | 12 | 5 | 4 | 1 | 1 | 5 |
| EC-06 Tunability | 10 | 4 | 2 | 5 | 2 | 5 |
| **Weighted total** | **100** | **456** | **342** | **246** | **176** | **488** |

Totals (×20): **E = 488**, **A = 456**, **B = 342**, **C = 246**, **D = 176**.

**Sensitivity.** E edges A by 32 purely on tunability (EC-02/EC-06) via governed
overrides. Since overrides stay versioned and reviewed, E keeps A's determinism and
audit properties, so E is selected.

## 7. Decision

**PFF AI will bind generation parameters to declared task classes in versioned
config, with narrow governed per-workflow overrides (Option E).** Deterministic
classes (extraction, routing, tool-argument formatting, structured output) run at
temperature 0; persona narration runs at a low non-zero temperature tuned for tone;
output-token budgets are set per workflow (15.PFF-FA-AI-SLM.md §34). Parameters are never
hard-coded, and temperature is never raised to mask missing validation or structure
(15.PFF-FA-AI-SLM.md §39–§40). B/C/D rejected.

**Status rationale.** `Accepted` — 15.PFF-FA-AI-SLM.md §33–§40 govern this; ADR records the
rationale.

## 8. Architecture Detail

- Task-class → parameter map in `config/models/generation.yaml`; overrides in the
  workflow's config, both versioned in the release manifest.
- The SLM abstraction (ADR-D3-14) reads class+overrides into `SLMRequest`.
- Structured-output classes always pair temperature 0 with schema validation
  (ADR-D3-17); a validation failure retries/repairs — it never bumps temperature.
- Persona narration parameters live with the persona layer's task class (ADR-D3-10).

## 9. Consequences

### 9.1 Positive
- Reproducible business logic; natural persona; controlled cost.
### 9.2 Negative
- Config surface for classes + overrides (mitigated by review).
### 9.3 Neutral
- Establishes task-class tagging reused by routing (ADR-D3-05) and eval.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Per-call freedom | Reproducibility, audit, cost control | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Determinism keeps SLM from improvising business outcomes |
| Precedence chain | Sampling never elevates SLM output over authoritative sources |
| Four-state separation | Parameters are config, not state |
| Versioned artefacts | Parameters versioned; no hard-coding |
| Adam persona governs *how*, not *what* | Non-zero temperature affects wording only |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Non-zero temp leaks into deterministic task | Med | High | H | Class map + CI check; structured classes pinned to 0 | ML Eng | Low |
| RSK-02 | Override abused to raise temp on business flow | Low | High | M | Review gate; lint disallows temp>0 on deterministic classes | Security Architect | Low |
| RSK-03 | Token budget too low truncates output | Med | Med | M | Per-workflow budget tuning + tests | ML Eng | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Deterministic-task repeatability | 100% | < 100% | Eval (fixed input) | Per release |
| QM-02 | Persona naturalness score | ≥ 0.9 | < 0.8 | Persona eval | Per release |
| QM-03 | Output truncation rate | ≈ 0 | rising | Langfuse finish-reason | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None |
| Data classification touched | Internal |
| Personal data / PII | None |
| Children's data and safeguarding | Determinism aids consistent safeguarding messaging |
| UK GDPR lawful basis and rights impact | None |
| Audit and evidential requirements | Parameters versioned + traced |
| Standards touched | ISO/IEC 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 |
| Repository paths | `config/models/`, `src/pff_fa_ai/slm/` |
| Configuration | Task-class parameter map; overrides |
| Contracts / schemas | Params in `SLMRequest` |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-14, ADR-D3-17 |
| Effort estimate | S |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Deterministic classes fixed at temp 0 | CI config check + repeatability test |
| AC-02 | No hard-coded parameters in code | Lint/import check |
| AC-03 | Overrides are versioned and reviewed | Manifest review |
| AC-04 | Structured output never raises temp on failure | Unit test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Finish reasons, token usage per class |
| Alerting | Truncation spikes; unexpected temp values |
| Runbook | `docs/runbooks/slm.md` |
| Failure mode and degradation | Truncation → increase budget or compress prompt |
| Rollback | Config revert |
| Support model impact | ML platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Class map + tuning | S | negligible | Config |
| Token budgets | — | reduces spend | Per-workflow caps |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Task classes too coarse for quality | Eval per class | Split classes |
| RT-02 | Repeatability < 100% on deterministic task | QM-01 | Investigate provider/seed handling |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-16 |
| Specification sections | 15.PFF-FA-AI-SLM.md §33–§40 |
| Requirement IDs | SLM-GEN-* |
| Build phases | 6 |
| Code paths | `config/models/`, `src/pff_fa_ai/slm/` |
| Configuration | generation.yaml, overrides |
| Tests | repeatability + persona eval |
| Upstream ADRs | ADR-D3-14, ADR-D3-15 |
| Downstream ADRs | ADR-D3-17 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
