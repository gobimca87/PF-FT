---
id: ADR-D3-11
title: Prompt storage, versioning and promotion
domain: 3 AI
ws_ref: [WS-15]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [Prompt Engineer, Platform Engineer, Release Manager]
reviewers: [Principal Architect, Security Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-09, ADR-D3-10, ADR-D5-06, ADR-D6-15, ADR-D7-12]
source_docs:
  - "MD files/4 AI/16.PFF-FA-AI-PROMPT-ENGINEERING.md §31, §32, §33, §34, §35, §36, §37, §39, §84, §102, §103, §161, §166, §167, §168, §169"
build_phases: [6]
impacted_paths:
  - prompts/
classification: Internal
review_due: 2027-08-22
---

# ADR-D3-11 — Prompt storage, versioning and promotion

## 1. Summary

PFF AI will treat **Git as the canonical source of truth for all prompts**, stored
as versioned Markdown-body-with-YAML-metadata artefacts under `prompts/`, promoted
through environments as immutable, semantically-versioned releases via the release
manifest. A prompt registry loads prompts by `id@version`; production never reads a
mutable prompt. This mirrors 16.PFF-FA-AI-PROMPT-ENGINEERING.md §169 ("prompt source of truth" = Git) and the
versioned-artefact rule in `CLAUDE.md`.

## 2. Context and Problem Statement

16.PFF-FA-AI-PROMPT-ENGINEERING.md §31–§39 defines a template registry, file naming, metadata, status lifecycle
and semantic versioning; §166–§169 discuss storage and name Git as the source of
truth; §102–§103 define promotion and rollback. `CLAUDE.md` requires prompts to be
"versioned software artifacts — never mutate in place in production." Without a
storage/promotion decision, prompts drift into a database editable at runtime, or
into code, losing review, diff, rollback and provenance — and making the "immutable
in prod" rule unenforceable. The choice determines how every prompt (system,
persona, task, tool) is authored, reviewed, promoted and rolled back.

## 3. Decision Drivers

### 3.1 Functional drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Load prompt deterministically by id@version | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §35, §87 |
| DR-F-02 | Full review/diff/history on every prompt change | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §96, §157 |
| DR-F-03 | Promote across DEV→…→PROD as immutable release | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §102, §161 |
| DR-F-04 | Roll back to a prior version instantly | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §103, §160 |

### 3.2 Non-functional drivers

| ID | Driver | Target | Source |
|---|---|---|---|
| DR-N-01 | Production prompt is immutable | No runtime edit path | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §39, §155 |
| DR-N-02 | Provenance on every generation | Version in every trace | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §90 |
| DR-N-03 | Human-readable authoring + machine metadata | MD body + YAML | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §167, §168 |

### 3.3 Constraints

| ID | Constraint | Type | Source |
|---|---|---|---|
| DR-C-01 | Prompts are versioned artefacts, not in-place mutable | Organisational | CLAUDE.md; 16.PFF-FA-AI-PROMPT-ENGINEERING.md §39 |
| DR-C-02 | Change governance/approval gates apply | Governance | ADR-D6-15; 16.PFF-FA-AI-PROMPT-ENGINEERING.md §96 |
| DR-C-03 | Secrets never embedded in prompts | Security | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §114, §116 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Prompt-editing audience is technical (works in Git/PR) | Add an authoring UI over Git | Author feedback |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Immutability & release integrity | 25 | The binding rule | Runtime mutation possible? |
| EC-02 | Review, diff, history, provenance | 22 | Governance & audit | PR/diff available on every change |
| EC-03 | Rollback speed & safety | 18 | Incident recovery | Time-to-rollback |
| EC-04 | Authoring ergonomics | 12 | Prompt engineers iterate often | Author effort |
| EC-05 | Operational simplicity | 13 | Fewer moving parts | # systems to run |
| EC-06 | Security (secret-free, scannable) | 10 | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §114 | Secret-scan in CI |
| | **Total** | **100** | | |

Scoring scale: **1**–**5** as elsewhere.

## 5. Alternatives Considered

### 5.1 Option A — Git-canonical files + registry loader + release manifest

**Description.** Prompts as MD+YAML files in `prompts/`; a loader/registry resolves
`id@version`; promotion pins versions in an immutable release manifest (16.PFF-FA-AI-PROMPT-ENGINEERING.md §161).
**Strengths.** PR review/diff/history; immutable prod; instant rollback (repoint
manifest); secret-scannable in CI; no extra datastore.
**Weaknesses.** Non-technical authors need Git literacy.
**Cost / effort.** Low; reuses CI/CD.

### 5.2 Option B — Database-stored prompts, edited via admin UI

**Description.** Prompts in a DB, edited at runtime through a console.
**Strengths.** Friendly authoring; no deploy to change a prompt.
**Weaknesses.** Runtime mutability violates DR-C-01/16.PFF-FA-AI-PROMPT-ENGINEERING.md §39; weak diff/review;
provenance and rollback bespoke; secret-scanning harder.
**Cost / effort.** Higher; new datastore + UI + guardrails to re-impose immutability.

### 5.3 Option C — Prompts hard-coded in Python source

**Description.** Prompt strings in code modules.
**Strengths.** Versioned with code; simple.
**Weaknesses.** Couples prompt iteration to code releases; poor separation from the
prompt-engineering lifecycle (16.PFF-FA-AI-PROMPT-ENGINEERING.md §40); harder for prompt engineers; no metadata
registry; A/B and per-environment overlays awkward.
**Cost / effort.** Low but rigid.

### 5.4 Option D — Third-party prompt-management SaaS (e.g. hosted prompt registry)

**Description.** External prompt CMS with versioning APIs.
**Strengths.** Rich UI, A/B, analytics.
**Weaknesses.** Off-tenancy storage of prompts (some sensitive, 16.PFF-FA-AI-PROMPT-ENGINEERING.md §116); new
vendor dependency; provenance split from code; conflicts with Git-as-truth (§169).
**Cost / effort.** Licence + integration; lock-in.

### 5.5 Option E — Langfuse-managed prompts (reuse the AI-observability platform)

**Description.** Store/version prompts in Langfuse (already selected for tracing).
**Strengths.** Integrated with traces; versioning + fetch API; already in stack.
**Weaknesses.** Makes Langfuse a runtime dependency on the critical prompt-load path;
prompt source-of-truth would move out of Git against §169; runtime-editable unless
constrained. Better used as a *mirror/label* than the canonical store.
**Cost / effort.** Low integration, but architectural coupling and truth-source
conflict.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Object storage (blob) of prompt files | No review/diff/PR workflow; reinvents Git poorly |
| Config service (App Configuration) as canonical | Weaker diff/review than Git; §169 names Git |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 16.PFF-FA-AI-PROMPT-ENGINEERING.md §166–§169 and the
release-manifest model (ADR-D5-06).

| Criterion | Weight | A: Git+manifest | B: DB+UI | C: In code | D: SaaS | E: Langfuse |
|---|---|---|---|---|---|---|
| EC-01 Immutability | 25 | 5 | 2 | 4 | 3 | 3 |
| EC-02 Review/history | 22 | 5 | 3 | 4 | 4 | 3 |
| EC-03 Rollback | 18 | 5 | 3 | 3 | 4 | 4 |
| EC-04 Authoring | 12 | 3 | 5 | 2 | 5 | 4 |
| EC-05 Ops simplicity | 13 | 5 | 2 | 4 | 3 | 4 |
| EC-06 Security | 10 | 5 | 3 | 4 | 3 | 3 |
| **Weighted total** | **100** | **480** | **295** | **360** | **363** | **338** |

Totals (×20): **A = 480**, **D = 363**, **C = 360**, **E = 338**, **B = 295**.

**Sensitivity.** A leads by > 100 points. Only if EC-04 (authoring ergonomics) were
weighted above ~40 would B/D approach — indefensible given the immutability and
governance rules. An authoring UI *over* Git (mitigation) captures B's one strength
without its cost.

## 7. Decision

**PFF AI will make Git the canonical prompt store**: MD-body + YAML-metadata files
under `prompts/`, resolved at runtime by a registry keyed on `id@version`, promoted
across environments as immutable entries in the release manifest, with rollback by
repointing the manifest. Production has no runtime prompt-edit path. Langfuse (E) is
used to *label/trace* prompt versions, not as the source of truth. B and D are
rejected for runtime mutability and off-tenancy/lock-in concerns; C for coupling
prompt iteration to code releases.

**Status rationale.** `Accepted` — 16.PFF-FA-AI-PROMPT-ENGINEERING.md §169 and CLAUDE.md fix Git-as-truth and
immutability; this ADR records the alternatives and rationale.

## 8. Architecture Detail

- **Layout** (16.PFF-FA-AI-PROMPT-ENGINEERING.md §84): `prompts/{system,persona,task,tool}/…vN.md`, each with
  metadata (16.PFF-FA-AI-PROMPT-ENGINEERING.md §33): `id`, `version` (semver, §35–§36), `status` (§34),
  `owner` (§40), `risk_class` (§41), `model_compatibility` (§82), `dependencies`
  (§106).
- **Registry/loader** (16.PFF-FA-AI-PROMPT-ENGINEERING.md §86–§87): resolves and caches by `id@version`;
  missing/invalid version fails closed (16.PFF-FA-AI-PROMPT-ENGINEERING.md §29).
- **Promotion** (16.PFF-FA-AI-PROMPT-ENGINEERING.md §102, §118 overlays, §161 manifest): environment overlays
  layer non-secret env values; the release manifest pins exact versions per env.
- **Rollback** (16.PFF-FA-AI-PROMPT-ENGINEERING.md §103, §160): change the manifest pointer; previous version is
  still present and immutable.
- **CI gates** (16.PFF-FA-AI-PROMPT-ENGINEERING.md §113 lint, §114 secret-scan, §155 regression): every prompt
  change runs lint, secret-scan, contract and regression tests before promotion.

## 9. Consequences

### 9.1 Positive
- Every prompt change is a reviewable, revertible, provenanced PR.
- Immutability in prod is structurally guaranteed, not policy-only.

### 9.2 Negative
- Non-technical authoring needs tooling over Git (tracked mitigation).

### 9.3 Neutral
- Prompt lifecycle aligns with the code/release lifecycle (ADR-D7-12).

### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Instant no-deploy prompt edits (B) | Immutability, review, provenance | Release Manager |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Storage choice; no business authority |
| Precedence chain | Not applicable — storage layer |
| Four-state separation | Prompts are artefacts, not state |
| Versioned artefacts, never mutated in place | This ADR *is* the enforcement mechanism |
| Adam persona governs *how*, not *what* | Persona artefact stored under the same rules |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Secret committed in a prompt | Low | High | M | CI secret-scan (16.PFF-FA-AI-PROMPT-ENGINEERING.md §114) | Security Architect | Low |
| RSK-02 | Non-technical author blocked | Med | Low | L | Authoring UI over Git PRs | Prompt Eng | Low |
| RSK-03 | Wrong version promoted | Low | Med | M | Manifest review gate (ADR-D6-15) | Release Manager | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Prompt version present in trace | 100% | < 100% | Langfuse | Continuous |
| QM-02 | Time-to-rollback | ≤ 5 min | > 15 min | Release logs | Per incident |
| QM-03 | Prompts failing secret-scan reaching prod | 0 | > 0 | CI | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Prompts in-repo; secret-scanned; no runtime edit endpoint |
| Data classification touched | Internal |
| Personal data / PII | None in prompts (enforced by scan) |
| Children's data and safeguarding | N/A at storage layer |
| UK GDPR lawful basis and rights impact | None |
| Audit and evidential requirements | Git history + manifest = full provenance |
| Standards touched | ISO/IEC 42001, 27001 (change control) |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 |
| Repository paths | `prompts/`, release manifest |
| Configuration | Env overlays (16.PFF-FA-AI-PROMPT-ENGINEERING.md §118); manifest (§161) |
| Contracts / schemas | Prompt metadata schema (§33) |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-06 (config/manifest), ADR-D6-15 (gates) |
| Effort estimate | S–M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | No runtime prompt-edit endpoint exists | Code/route audit |
| AC-02 | Every prompt resolvable only by id@version | Registry unit test |
| AC-03 | Rollback repoints manifest without redeploying prompts | Release drill |
| AC-04 | Secret-scan + lint block promotion on failure | CI gate |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Prompt version metrics; load errors |
| Alerting | Prompt load failure; secret-scan failure |
| Runbook | `docs/runbooks/prompt-release.md` |
| Failure mode and degradation | Missing version → fail closed, use pinned prod version |
| Rollback | Manifest pointer change |
| Support model impact | Prompt eng + release management |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Registry/loader + CI gates | S | negligible | Reuses Git/CI |
| Optional authoring UI | M (if built) | low | Deferred |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Author throughput blocked by Git workflow | Team feedback | Build authoring UI over Git |
| RT-02 | Rollback repeatedly > 15 min | QM-02 | Re-engineer manifest/rollback |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-15 |
| Specification sections | 16.PFF-FA-AI-PROMPT-ENGINEERING.md §31–§41, §84–§87, §102–§103, §161, §166–§169 |
| Requirement IDs | PROMPT-STORE-* |
| Build phases | 6 |
| Code paths | `prompts/`, registry loader |
| Configuration | Release manifest, env overlays |
| Tests | prompt registry + CI gate suites |
| Upstream ADRs | ADR-D3-09, ADR-D5-06 |
| Downstream ADRs | ADR-D6-15, ADR-D7-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
