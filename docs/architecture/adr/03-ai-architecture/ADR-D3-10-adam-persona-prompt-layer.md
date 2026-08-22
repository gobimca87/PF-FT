---
id: ADR-D3-10
title: Adam persona prompt layer — versioned, reusable, workflow-independent
domain: 3 AI
ws_ref: [WS-15]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [Prompt Engineer, Conversation Designer, Product Owner]
reviewers: [Principal Architect, Product Owner]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-09, ADR-D1-09, ADR-D3-11, ADR-D3-16, ADR-D3-25]
source_docs:
  - "MD files/4 AI/16.PF-FT-AI-PROMPT-ENGINEERING.md §11, §12, §5, §6, §40, §41, §81, §82, §120, §121"
  - "MD files/Examples/SampleWorkflowchat.md"
build_phases: [6]
impacted_paths:
  - prompts/persona/
classification: Internal
review_due: 2027-08-22
---

# ADR-D3-10 — Adam persona prompt layer — versioned, reusable, workflow-independent

## 1. Summary

PFF AI will implement the Adam persona as a **dedicated, versioned prompt layer**
that sits between the system prompt and the task/workflow prompts in the layered
composition of [ADR-D3-09](ADR-D3-09-layered-prompt-composition.md), and is
**reused unchanged across all workflows**. The persona layer governs *how* Adam
communicates (football-commentary tone, workflow-first posture); it never encodes
workflow logic, authorization, or business rules. This keeps persona a single,
independently-testable artefact instead of tone duplicated into every task prompt.

## 2. Context and Problem Statement

Doc 16 §11 defines a distinct "Persona Prompt" and §12 states the persona "does not
define authorization"; `CLAUDE.md` §Adam rule 12 requires the persona to be "a
dedicated, versioned prompt layer … reusable across workflows … do not embed the
entire business workflow into the persona prompt." Without an explicit decision,
the natural failure is that each workflow author copies tone instructions into their
task prompt — producing drift (affiliation Adam sounds different from discipline
Adam), un-testable persona behaviour, and tone edits that must be made in N places.
The `SampleWorkflowchat.md` reference sets a single consistent voice that only a
shared layer can guarantee.

## 3. Decision Drivers

### 3.1 Functional drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | One consistent Adam voice across affiliation, discipline, officials, etc. | CLAUDE.md §Adam 12; doc 16 §11 |
| DR-F-02 | Persona reusable without re-authoring per workflow | CLAUDE.md §Adam 12 |
| DR-F-03 | Persona must not carry authorization or business rules | doc 16 §12; CLAUDE.md §Adam 5, 9 |

### 3.2 Non-functional drivers

| ID | Driver | Target | Source |
|---|---|---|---|
| DR-N-01 | Persona independently testable | Persona eval suite separate from workflow tests | CLAUDE.md §Persona Quality |
| DR-N-02 | Tone change is one edit, one release | Single artefact, versioned | doc 16 §35, §40 |

### 3.3 Constraints

| ID | Constraint | Type | Source |
|---|---|---|---|
| DR-C-01 | Prompt layering order is fixed by ADR-D3-09 | Architecture | ADR-D3-09; doc 16 §5, §20 |
| DR-C-02 | Enterprise truth overrides persona | Regulatory/Arch | CLAUDE.md §Adam 5; doc 16 §138 |
| DR-C-03 | Persona is a versioned artefact, immutable in prod | Organisational | doc 16 §35, §39 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | One persona voice suits all workflows | Introduce persona variants as sub-layer | Persona eval across workflows |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Voice consistency across workflows | 25 | The core goal | Persona eval variance across workflows |
| EC-02 | Separation from workflow/business logic | 25 | doc 16 §12; safety-critical | Ablation: remove persona, workflow still correct |
| EC-03 | Maintainability (edit-once) | 20 | Tone will iterate | # edit sites per tone change |
| EC-04 | Testability in isolation | 15 | Persona quality judged separately | Standalone persona suite exists |
| EC-05 | Reusability across future workflows | 15 | Many workflows planned (ADR-D1-10) | New workflow reuses persona unchanged |
| | **Total** | **100** | | |

Scoring scale: **1** unacceptable · **2** poor · **3** adequate · **4** good · **5** excellent.

## 5. Alternatives Considered

### 5.1 Option A — Dedicated shared persona layer, composed by the prompt composer

**Description.** A single `prompts/persona/adam.vN.md` artefact inserted at the
persona position of the composition pipeline for every workflow.

**Strengths.** One voice; edit-once; testable alone; reusable; clean separation.
**Weaknesses.** Requires disciplined composition and a placeholder contract so the
persona never needs workflow specifics.
**Cost / effort.** Low — one artefact + composer slot.

### 5.2 Option B — Persona embedded in each task/workflow prompt

**Description.** Each workflow prompt includes its own tone instructions.
**Strengths.** Simple to start; per-workflow tone tuning.
**Weaknesses.** Voice drift; N-place edits; persona not testable in isolation;
tone and business logic entangled (violates doc 16 §12).
**Cost / effort.** Low to start, high to maintain.

### 5.3 Option C — Persona folded into the system prompt

**Description.** Put Adam tone in the single system prompt.
**Strengths.** Always present; one place.
**Weaknesses.** doc 16 §9 forbids frequently-changing data in the system prompt;
conflates stable platform rules with iterating tone; system-prompt changes are the
highest-risk change class (doc 16 §41). Reduces reuse granularity.
**Cost / effort.** Low, but high blast radius per tone edit.

### 5.4 Option D — Fine-tune the SLM to embody the persona

**Description.** Bake the voice into model weights.
**Strengths.** Consistent tone without prompt tokens.
**Weaknesses.** doc 15 §85 — fine-tuning must not be the first step; couples tone to
a model version; every tone iteration is a re-train + eval; can't A/B tone cheaply.
**Cost / effort.** High; premature.

### 5.5 Option E — Post-generation tone rewriter (second model pass)

**Description.** Generate neutral text, then restyle it into Adam's voice.
**Strengths.** Decouples content from tone; reusable.
**Weaknesses.** Doubles latency and cost; a second pass can re-introduce claims or
soften errors (violates CLAUDE.md §Adam 7); harder to guarantee factual fidelity.
**Cost / effort.** High run cost; risky for enterprise fidelity.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No persona (neutral assistant) | DR-F-01 / product intent — Adam persona is a required product decision (ADR-D1-09) |
| Per-user persona personalization | Out of scope for first release; adds state and eval surface |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 16 §5–§12 and the
`SampleWorkflowchat.md` reference.

| Criterion | Weight | A: Shared layer | B: In task prompt | C: In system prompt | D: Fine-tune | E: Rewriter pass |
|---|---|---|---|---|---|---|
| EC-01 Consistency | 25 | 5 | 2 | 4 | 5 | 4 |
| EC-02 Separation | 25 | 5 | 2 | 3 | 2 | 4 |
| EC-03 Maintainability | 20 | 5 | 2 | 3 | 1 | 3 |
| EC-04 Testability | 15 | 5 | 2 | 3 | 2 | 4 |
| EC-05 Reusability | 15 | 5 | 2 | 4 | 3 | 4 |
| **Weighted total** | **100** | **500** | **200** | **335** | **255** | **380** |

Totals (×20): **A = 500**, **E = 380**, **C = 335**, **D = 255**, **B = 200**.

**Sensitivity.** A wins on every criterion; no plausible re-weighting changes the
outcome. E is the distant runner-up but loses decisively on cost/latency and
factual-fidelity risk (EC-02).

## 7. Decision

**PFF AI will implement Adam as a dedicated, versioned persona prompt layer**
(`prompts/persona/adam.vN.md`), composed at the persona slot of the ADR-D3-09
pipeline and reused unchanged across all workflows. The layer contains tone,
communication pattern (Context → football-flavoured explanation → clear business
state → action → confirmation → next step, per CLAUDE.md) and the persona exclusion
zones; it contains no workflow steps, no business rules, and no authorization
logic. Options B/C are rejected for entangling tone with platform/workflow layers;
D and E for cost, coupling and fidelity risk.

**Status rationale.** `Accepted` — mandated by CLAUDE.md §Adam 12 and doc 16 §11–§12;
this ADR records the reasoning behind a settled requirement.

## 8. Architecture Detail

- **Artefact.** `prompts/persona/adam.vMAJOR.MINOR.PATCH.md` with metadata (doc 16
  §33): `id`, `status` (doc 16 §34), `version`, `owner`, `risk_class` (doc 16 §41 —
  persona is high-risk since it shapes all output), `model_compatibility` (§82).
- **Composition.** The prompt composer (ADR-D3-09; doc 16 §21) inserts the persona
  layer after the system prompt and before the task prompt; ordering is deterministic
  (doc 16 §22).
- **Trust tier.** Persona is platform-authored trusted content (T0/T1 per ADR-D3-09);
  it is never assembled from user or retrieved text.
- **Exclusion zones** (from ADR-D1-09 X-1…X-6): the layer explicitly instructs Adam
  not to state transaction success before confirmation, not to invent rules/URLs,
  not to soften errors — but enforcement of these lives in guardrails (ADR-D6-09),
  not in the persona text alone.

## 9. Consequences

### 9.1 Positive
- One voice, one edit site, one persona eval suite.
- Persona reused free by every new workflow (ADR-D1-10).

### 9.2 Negative
- Requires composer discipline: the persona must stay free of workflow specifics,
  enforced by review (doc 16 §157) and a lint rule (§113).

### 9.3 Neutral
- Persona iteration becomes a normal versioned release like any prompt.

### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Per-workflow tone micro-tuning | Consistency, testability, reuse | Product Owner |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Persona shapes wording only; no decision or execution authority |
| Precedence chain | Persona is at SLM-output tier; it never overrides ERC/enterprise truth (doc 16 §138) |
| Four-state separation | Persona is a prompt artefact; carries no state |
| Versioned artefacts | Persona is versioned, immutable in prod (doc 16 §35, §39) |
| Adam persona governs *how*, not *what* | This ADR is the structural guarantee of exactly that |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Workflow logic leaks into persona | Med | High | H | Lint + review gate (doc 16 §113, §157) | Prompt Eng | Low |
| RSK-02 | Football tone reduces clarity of critical info | Med | Med | M | Persona eval for clarity; CLAUDE.md §Adam 3 | Conversation Designer | Low |
| RSK-03 | Persona celebrates unconfirmed transaction | Low | High | M | Guardrail (ADR-D6-09) + persona rule X-? | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Persona adherence score (eval) | ≥ 0.9 | < 0.8 | Persona eval suite | Every persona release |
| QM-02 | Clarity score on critical messages | ≥ 0.95 | < 0.9 | Eval | Every release |
| QM-03 | Cross-workflow voice variance | low/stable | rising | Eval across workflows | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None new; persona is trusted static content |
| Data classification touched | Internal |
| Personal data / PII | None in the artefact |
| Children's data and safeguarding | Persona must not trivialise safeguarding messaging — eval-checked |
| UK GDPR lawful basis and rights impact | None |
| Audit and evidential requirements | Persona version stamped on each trace (doc 16 §90) |
| Standards touched | ISO/IEC 42001 (artefact lifecycle) |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 (prompt engineering) |
| Repository paths | `prompts/persona/` |
| Configuration | Persona version pinned in release manifest (doc 16 §161) |
| Contracts / schemas | Prompt metadata schema (doc 16 §33) |
| Migration | N/A (new) |
| Dependencies on other ADRs | ADR-D3-09 (composition), ADR-D1-09 (charter) |
| Effort estimate | S |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Persona is a single artefact reused by ≥2 workflows | Composition trace inspection |
| AC-02 | Removing persona leaves workflow correctness intact | Ablation test (ADR-D1-02 style) |
| AC-03 | No business rule/URL/authz text in persona | Prompt lint (doc 16 §113) + review |
| AC-04 | Persona adherence eval runs in CI | CI eval gate (doc 16 §155) |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Persona version in Langfuse traces; adherence metric |
| Alerting | Adherence regression on release |
| Runbook | `docs/runbooks/prompt-release.md` |
| Failure mode and degradation | If persona load fails, composition fails closed (doc 16 §29) |
| Rollback | Repoint persona version pointer (doc 16 §103) |
| Support model impact | Owned by prompt engineering |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Persona authoring + eval harness | S | negligible | Shared with prompt tooling |
| Persona tokens per request | — | small | One layer, compressed (doc 16 §72) |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | One voice proves unsuitable for a workflow class | Persona eval variance | Introduce persona variant sub-layer |
| RT-02 | Persona adherence < 0.8 sustained | QM-01 | Reopen persona design |

**Scheduled review:** `review_due`. **Causal analysis:** persona-caused incidents
(e.g. softened error) raise a superseding persona version, never an in-place edit.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-15 Prompt Engineering |
| Specification sections | doc 16 §5, §6, §11, §12, §20, §35, §41, §81, §82, §138 |
| Requirement IDs | PROMPT-PERSONA-* |
| Build phases | 6 |
| Code paths | `prompts/persona/` |
| Configuration | Release manifest persona pin |
| Tests | persona eval suite |
| Upstream ADRs | ADR-D3-09, ADR-D1-09 |
| Downstream ADRs | ADR-D3-16, ADR-D3-25 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
