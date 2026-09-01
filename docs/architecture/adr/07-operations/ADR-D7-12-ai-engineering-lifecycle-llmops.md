---
id: ADR-D7-12
title: AI engineering lifecycle (LLMOps) — prompt/model/index release bundles
domain: 7 Operations
ws_ref: [WS-32]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [ML Engineer, Release Manager, AI Governance Lead]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-11, ADR-D3-15, ADR-D5-06, ADR-D6-15, ADR-D7-13]
source_docs:
  - "MD files/4 AI/17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §42, §43, §56, §57, §58"
  - "MD files/4 AI/15.PFF-FA-AI-SLM.md §151, §152, §156, §157, §158, §159"
  - "MD files/4 AI/16.PFF-FA-AI-PROMPT-ENGINEERING.md §102, §103, §155, §156"
build_phases: [12]
impacted_paths:
  - .github/workflows/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-12 — AI engineering lifecycle (LLMOps) — prompt/model/index release bundles

## 1. Summary

PFF AI will manage prompts, models, RAG indexes, guardrails and their configs as a
**coordinated LLMOps lifecycle**: authored/versioned in Git, evaluated (ADR-D7-13),
promoted as **compatible, immutable release bundles** (ADR-D5-06) through the environment
ladder with shadow/canary for models and blue/green for indexes, under change governance
(ADR-D6-15) (17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §42–§43, §56–§58; 15.PFF-FA-AI-SLM.md §151–§159; 16.PFF-FA-AI-PROMPT-ENGINEERING.md §102–§103, §155–§156). AI
artefacts follow the same rigor as code, with AI-specific promotion mechanics.

## 2. Context and Problem Statement

17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §42–§43 RAG version deps/compatibility, §56–§58 dependency + release manifest; 15.PFF-FA-AI-SLM.md §151–§159 model promotion/release/shadow/canary/rollback; 16.PFF-FA-AI-PROMPT-ENGINEERING.md §102–§103/§155–§156
prompt promotion/rollback/regression pipeline. AI artefacts have interdependencies (a
prompt expects a model capability; an index matches an embedding). Promoting them
independently breaks compatibility. This ADR fixes the LLMOps lifecycle and bundle model.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Version all AI artefacts (Git) | ADR-D3-11/D3-15; 17.PFF-FA-AI-CONFIGURATION-VERSIONING.md |
| DR-F-02 | Promote as compatible bundles | 17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §56–§58 |
| DR-F-03 | AI-specific promotion (shadow/canary/blue-green) | 15.PFF-FA-AI-SLM.md §157–§158; 14.PFF-FA-AI-EMBEDDING-VECTOR.md §77 |
| DR-C-01 | Under change governance + eval gates | ADR-D6-15, D7-13 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Artefact compatibility is expressible | Compatibility matrix (17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §43) | Review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Compatibility integrity (no broken combos) | 30 | Core risk | Compat checks |
| EC-02 | Evaluation before promotion | 22 | Quality | Eval gate |
| EC-03 | Safe AI-specific promotion | 20 | Shadow/canary/BG | Mechanics |
| EC-04 | Traceability/rollback | 16 | Recovery | Rollback |
| EC-05 | Velocity | 12 | Ship AI changes | Lead time |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Coordinated bundles: version + eval + compatibility-checked + AI-specific promotion + governance

**Description.** All AI artefacts versioned (Git); a bundle (manifest, ADR-D5-06) pins
compatible versions with a compatibility matrix (17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §43); eval gate (ADR-D7-13);
shadow→canary for models (15.PFF-FA-AI-SLM.md §157–§158), blue/green for indexes (14.PFF-FA-AI-EMBEDDING-VECTOR.md §77); under
governance (ADR-D6-15); rollback per artefact/bundle.
**Strengths.** Compatible, evaluated, safe, traceable.
**Weaknesses.** Bundle/compat management.
**Cost / effort.** Medium.

### 5.2 Option B — Independent artefact promotion (no bundling)

**Description.** Promote each artefact on its own.
**Strengths.** Flexible/fast per artefact.
**Weaknesses.** Incompatible combos in prod; breaks compatibility guarantees.
**Cost / effort.** Low; risky.

### 5.3 Option C — Treat AI artefacts exactly like code (no AI-specific mechanics)

**Description.** Ship prompts/models/indexes via the normal code CD only.
**Strengths.** One pipeline.
**Weaknesses.** Misses shadow/canary/blue-green needed for models/indexes; risky model
swaps.
**Cost / effort.** Low; unsafe for models.

### 5.4 Option D — Manual AI-artefact management (no lifecycle automation)

**Description.** Ops manually manage prompts/models.
**Strengths.** Simple initially.
**Weaknesses.** Error-prone; no eval gate; not reproducible.
**Cost / effort.** Low; unreliable.

### 5.5 Option E — Coordinated bundles + automated compatibility matrix + shadow-eval + canary + auto-rollback on eval regression

**Description.** Option A with an automated compatibility matrix check and shadow
evaluation of new models/prompts against live traffic before canary, with auto-rollback on
eval regression.
**Strengths.** Strongest safety; catches regressions pre/at rollout.
**Weaknesses.** More automation to build.
**Cost / effort.** Medium-high.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Mutable in-place artefact edits | CLAUDE.md immutability; ADR-D5-06 |
| No eval before promotion | 20.PFF-FA-AI-GOVERNANCE.md §86; ADR-D7-13 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §42–§58, 15.PFF-FA-AI-SLM.md §151–§159, 16.PFF-FA-AI-PROMPT-ENGINEERING.md §102–§103/§155–§156.

| Criterion | Weight | A: Bundles | B: Independent | C: Like-code | D: Manual | E: Bundles+shadow+auto-rollback |
|---|---|---|---|---|---|---|
| EC-01 Compatibility | 30 | 5 | 1 | 3 | 2 | 5 |
| EC-02 Eval-before | 22 | 5 | 3 | 3 | 1 | 5 |
| EC-03 AI-specific promotion | 20 | 5 | 3 | 2 | 2 | 5 |
| EC-04 Traceability/rollback | 16 | 5 | 3 | 4 | 2 | 5 |
| EC-05 Velocity | 12 | 4 | 5 | 4 | 3 | 4 |
| **Weighted total** | **100** | **488** | **272** | **306** | **192** | **496** |

Totals (×20): **E = 496**, **A = 488**, **C = 306**, **B = 272**, **D = 192**.

**Sensitivity.** E (bundles + automated compatibility + shadow-eval + auto-rollback) edges
A by catching regressions against live traffic before full rollout. Adopted. Independent
promotion (B) breaks compatibility — the core risk.

## 7. Decision

**PFF AI will run a coordinated LLMOps lifecycle: all AI artefacts versioned in Git,
promoted as compatible immutable bundles (ADR-D5-06) with an automated compatibility
matrix, gated by evaluation (ADR-D7-13), using shadow evaluation then canary for models/
prompts and blue/green for indexes, with auto-rollback on eval regression, under change
governance (ADR-D6-15) (Option E).** Independent promotion (B), code-only mechanics (C)
and manual management (D) are rejected.

## 8. Architecture Detail

- Artefact registries: prompts (ADR-D3-11), models (ADR-D3-15), RAG index/embedding
  (ADR-D3-23/24); a release bundle (manifest, ADR-D5-06) pins compatible versions with a
  compatibility matrix (17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §43, §132).
- Promotion: eval gate (ADR-D7-13) → shadow eval (15.PFF-FA-AI-SLM.md §157) → canary (15.PFF-FA-AI-SLM.md §158;
  ADR-D7-10) for models/prompts; blue/green alias swap for indexes (14.PFF-FA-AI-EMBEDDING-VECTOR.md §77); rollback
  per artefact (15.PFF-FA-AI-SLM.md §159; 16.PFF-FA-AI-PROMPT-ENGINEERING.md §103; 28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §44–§47).
- All under change governance (ADR-D6-15); traced (ADR-D7-02).

## 9. Consequences

### 9.1 Positive
- Compatible, evaluated, safely-promoted AI artefacts with quick rollback.
### 9.2 Negative
- Bundle/compatibility/automation overhead.
### 9.3 Neutral
- Extends code release-train (D7-11) to AI artefacts.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Independent per-artefact speed | Compatibility + safety | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Lifecycle governs the AI layer; no business authority |
| Precedence chain | Eval protects authoritative-truth fidelity |
| Four-state separation | N/A |
| Versioned artefacts | This ADR operationalises immutability + bundling |
| Adam persona governs *how*, not *what* | Persona promoted as a bundled, canaried artefact |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Incompatible artefact combo in prod | Low | High | M | Compatibility matrix + bundle | AI Arch Lead | Low |
| RSK-02 | Model/prompt regression | Med | High | H | Shadow + canary + auto-rollback (E) | ML Eng | Low |
| RSK-03 | Index cutover breaks retrieval | Low | High | M | Blue/green alias (14.PFF-FA-AI-EMBEDDING-VECTOR.md §77) | AI Arch Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Incompatible bundles promoted | 0 | > 0 | Compat check | Per release |
| QM-02 | AI regressions reaching prod | ≈ 0 | rising | Eval/incident | Monthly |
| QM-03 | Rollback time (AI artefact) | ≤ target | slow | Drill | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Governed AI changes reduce unsafe deploys |
| Data classification touched | Internal; eval datasets governed (20.PFF-FA-AI-GOVERNANCE.md §84) |
| Personal data / PII | No real PII in eval (synthetic) |
| Children's data and safeguarding | Safeguarding-affecting artefacts high-risk (ADR-D6-15) |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Bundle + promotion evidence |
| Standards touched | ISO/IEC 42001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 12 |
| Repository paths | `.github/workflows/`, registries, manifest |
| Configuration | Compatibility matrix; promotion mechanics |
| Contracts / schemas | Bundle/compatibility schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-11, D3-15, D5-06, D6-15, D7-13 |
| Effort estimate | M–L |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Bundles compatibility-checked | Compat test |
| AC-02 | Eval gate precedes promotion | Gate test |
| AC-03 | Models canaried; indexes blue/green | Deploy test |
| AC-04 | Auto-rollback on eval regression | Drill |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Bundle promotion; shadow/canary metrics |
| Alerting | Eval regression; incompatible bundle |
| Runbook | `docs/runbooks/llmops.md` (28.PFF-FA-AI-OPERATIONS-RUNBOOK.md §44–§47) |
| Failure mode and degradation | Regression → auto-rollback |
| Rollback | Per-artefact/bundle (15.PFF-FA-AI-SLM.md §159) |
| Support model impact | AI platform + release mgmt |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| LLMOps automation | M | small | Build |
| Shadow/canary compute | — | small | Extra inference |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Regressions slip past shadow/canary | Incident | Strengthen eval/shadow |
| RT-02 | Compatibility matrix gaps | Compat failures | Extend matrix |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-32 |
| Specification sections | 17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §42–§43, §56–§58, §132; 15.PFF-FA-AI-SLM.md §151–§159; 16.PFF-FA-AI-PROMPT-ENGINEERING.md §102–§103, §155–§156 |
| Requirement IDs | LLMOPS-* |
| Build phases | 12 |
| Code paths | registries + workflows |
| Configuration | compatibility matrix |
| Tests | compat + promotion drills |
| Upstream ADRs | ADR-D3-11, D3-15, D5-06 |
| Downstream ADRs | ADR-D6-15, D7-13 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
