---
id: ADR-D5-06
title: Configuration architecture and immutable release-manifest model
domain: 5 Technology
ws_ref: [WS-23]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Principal Architect
contributors: [Platform Engineer, Release Manager, AI Architecture Lead]
reviewers: [Security Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-07, ADR-D3-11, ADR-D3-15, ADR-D6-15, ADR-D5-14, ADR-D7-12]
source_docs:
  - "MD files/4 AI/17.PF-FT-AI-CONFIGURATION-VERSIONING.md §3, §11, §12, §13, §14, §15, §16, §18, §19, §20, §21, §22, §23, §57, §58, §59, §60, §61, §62, §63, §64"
build_phases: [0, 1]
impacted_paths:
  - config/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-06 — Configuration architecture and immutable release-manifest model

## 1. Summary

PFF AI will use a **layered YAML configuration** (base + environment overlays) loaded
**fail-fast** into an **immutable runtime configuration object**, with an **immutable
release manifest as the single deployment truth** that pins every versioned artefact
(prompts, models, RAG index, guardrails, agents, workflows, API contracts) plus a
config hash/fingerprint for startup audit (17.PF-FT-AI-CONFIGURATION-VERSIONING.md §3, §11–§23, §57–§64). Secrets are
never in YAML — only `*_secret_ref` indirection (ADR-D5-07).

## 2. Context and Problem Statement

17.PF-FT-AI-CONFIGURATION-VERSIONING.md §3/§11–§16 define the configuration architecture, repo structure, base/env
layering, precedence and merge; §18–§23 define schema, validation, fail-fast loading
and the immutable runtime config object; §57–§64 define the dependency + release
manifest, release id, git-commit association, config hash and startup audit. CLAUDE.md
requires artefacts to be released as immutable, compatible bundles. Without this, config
drifts between environments, "what is actually deployed" is ambiguous, and the versioned
artefacts (prompts/models/etc.) aren't pinned together. This ADR fixes the config and
release-manifest model.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Layered base+env config with defined precedence | 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §11–§15 |
| DR-F-02 | Fail-fast validation + immutable runtime object | 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §19–§23 |
| DR-F-03 | Release manifest as deployment truth, pins all artefacts | 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §57–§59 |
| DR-F-04 | Config hash/fingerprint + startup audit | 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §62–§64 |
| DR-C-01 | Secrets by reference only | 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §7, §10; ADR-D5-07 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Config volume suits file-based layering | Add config service | Ops review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Deployment determinism (what's live) | 28 | Release truth | Manifest pins all |
| EC-02 | Immutability & auditability | 24 | CLAUDE.md; governance | No runtime mutation |
| EC-03 | Environment isolation/precedence | 18 | No cross-env leak | Overlay correctness |
| EC-04 | Fail-fast safety | 16 | No bad config live | Startup validation |
| EC-05 | Simplicity | 14 | Maintainability | Concepts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Layered YAML + immutable runtime object + release manifest + fingerprint

**Description.** base + env overlays merged by precedence (§14–§15); schema-validated
fail-fast (§19–§21); immutable runtime config (§23); release manifest pins all artefact
versions (§58) with git commit + config hash (§61–§63) audited at startup (§64).
**Strengths.** Deterministic, immutable, auditable, isolated.
**Weaknesses.** Manifest discipline required.
**Cost / effort.** Medium.

### 5.2 Option B — Environment variables only

**Description.** All config via env vars.
**Strengths.** 12-factor; simple.
**Weaknesses.** Poor for structured/nested config; no artefact manifest; weak validation/
audit; hard to review.
**Cost / effort.** Low; insufficient for artefact pinning.

### 5.3 Option C — Central config service (runtime-fetched)

**Description.** App Configuration / Consul at runtime.
**Strengths.** Dynamic updates; central.
**Weaknesses.** Runtime mutability undercuts immutability; runtime dependency on hot
path; still need a manifest.
**Cost / effort.** Medium; coupling.

### 5.4 Option D — Config baked into the image only

**Description.** Config compiled into the container.
**Strengths.** Fully immutable per image.
**Weaknesses.** No env overlays without rebuild per env; secrets baking risk; less
flexible.
**Cost / effort.** Low; rigid.

### 5.5 Option E — Layered YAML without a release manifest

**Description.** Option A's config but no artefact manifest.
**Strengths.** Simpler.
**Weaknesses.** Artefacts (prompts/models/index) not pinned together → incompatible
combinations can deploy; loses "deployment truth".
**Cost / effort.** Low; incomplete.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Mutable runtime config | 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §23; CLAUDE.md |
| Secrets in YAML | 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §10; ADR-D5-07 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §3–§64.

| Criterion | Weight | A: YAML+manifest | B: env vars | C: config service | D: baked image | E: YAML no-manifest |
|---|---|---|---|---|---|---|
| EC-01 Determinism | 28 | 5 | 2 | 3 | 4 | 3 |
| EC-02 Immutability/audit | 24 | 5 | 2 | 2 | 5 | 4 |
| EC-03 Isolation/precedence | 18 | 5 | 3 | 4 | 2 | 5 |
| EC-04 Fail-fast | 16 | 5 | 3 | 3 | 4 | 5 |
| EC-05 Simplicity | 14 | 4 | 5 | 3 | 4 | 4 |
| **Weighted total** | **100** | **484** | **282** | **300** | **394** | **410** |

Totals (×20): **A = 484**, **E = 410**, **D = 394**, **C = 300**, **B = 282**.

**Sensitivity.** A leads E by 74 — the release manifest (pinning all artefacts) is the
differentiator and is essential given the many versioned artefacts (prompts, models,
RAG index). No re-weighting removes that need.

## 7. Decision

**PFF AI will use layered YAML (base + environment overlays) merged by defined
precedence, schema-validated and loaded fail-fast into an immutable runtime
configuration object, with an immutable release manifest as the single deployment
truth pinning every versioned artefact plus git commit and a config
hash/fingerprint audited at startup (Option A).** Secrets appear only as
`*_secret_ref` (ADR-D5-07). Env-only (B), runtime config service (C), baked-only (D)
and manifest-less (E) are rejected.

**Status rationale.** `Accepted` — 17.PF-FT-AI-CONFIGURATION-VERSIONING.md governs this.

## 8. Architecture Detail

- `config/base/*.yaml` + `config/<env>/*.yaml`; precedence base < env (§14); merge
  (§15); environment identity (§17).
- Schema validation (§18–§19); fail-fast load (§21) → immutable `RuntimeConfig` (§22–§23).
- Release manifest (§58) pins prompt/model/RAG/guardrail/agent/workflow/API versions
  (§56–§57), release id (§60), git commit (§61), config hash (§62), fingerprint (§63);
  startup audit logs the fingerprint (§64).
- Governance gates (ADR-D6-15) approve manifest changes; promotion across environments
  (ADR-D5-14) uses the manifest.

## 9. Consequences

### 9.1 Positive
- Deterministic, immutable, auditable deployments; compatible artefact bundles.
### 9.2 Negative
- Manifest discipline and schema upkeep.
### 9.3 Neutral
- Underpins prompt/model registries (D3-11/15) and LLMOps (D7-12).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Dynamic runtime reconfig | Immutability + deployment truth | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Config governs the platform, not business truth |
| Precedence chain | Config precedence separate from data authority chain |
| Four-state separation | Config is not runtime state |
| Versioned artefacts | Manifest pins all artefacts immutably |
| Adam persona governs *how*, not *what* | Persona version pinned in manifest |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Incompatible artefact combo deployed | Low | High | M | Manifest compatibility checks (§43, §56) | Release Manager | Low |
| RSK-02 | Bad config reaches prod | Low | High | M | Fail-fast validation (§21) | Platform Eng | Low |
| RSK-03 | Secret leaks into YAML | Low | High | M | Secret-ref only + scan (ADR-D5-07) | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Deploys with a pinned manifest | 100% | < 100% | CD | Per deploy |
| QM-02 | Startup config-fingerprint audited | 100% | < 100% | Startup logs | Continuous |
| QM-03 | Secrets found in YAML | 0 | > 0 | Secret scan | Per build |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Secret-ref indirection; no secrets in config |
| Data classification touched | Internal |
| Personal data / PII | None in config |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Manifest + fingerprint = deployment evidence |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 0, 1 |
| Repository paths | `config/`, release manifest |
| Configuration | base/env YAML; manifest |
| Contracts / schemas | Config schema; manifest schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-07, D3-11, D3-15, D6-15 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Runtime config is immutable | Code review |
| AC-02 | Bad config fails startup | Test (§21) |
| AC-03 | Manifest pins all artefact versions | Manifest schema check |
| AC-04 | Fingerprint audited at startup | Startup log test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Config fingerprint per instance |
| Alerting | Config load failure; fingerprint mismatch |
| Runbook | `docs/runbooks/config.md` |
| Failure mode and degradation | Invalid config → refuse start (fail closed) |
| Rollback | Deploy previous manifest |
| Support model impact | Platform + release management |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Config + manifest tooling | M | negligible | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Need for dynamic feature flags | Product | Add a governed flag service alongside (not replacing) manifest |
| RT-02 | Config volume unmanageable in files | Ops | Consider config service with immutability controls |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-23 |
| Specification sections | 17.PF-FT-AI-CONFIGURATION-VERSIONING.md §3, §11–§23, §56–§64 |
| Requirement IDs | CFG-* |
| Build phases | 0, 1 |
| Code paths | `config/` |
| Configuration | base/env + manifest |
| Tests | config load + manifest suites |
| Upstream ADRs | ADR-D5-07 |
| Downstream ADRs | ADR-D3-11, D3-15, D6-15, D7-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Principal Architect | Initial decision recorded. |
