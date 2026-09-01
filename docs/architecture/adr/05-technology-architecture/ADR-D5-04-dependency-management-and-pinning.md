---
id: ADR-D5-04
title: Dependency management, pinning and lock-file policy
domain: 5 Technology
ws_ref: [WS-23]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Backend Lead
contributors: [Platform Engineer, Security Architect]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-02, ADR-D5-09, ADR-D7-09, ADR-D6-18]
source_docs:
  - "MD files/6 Production/27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §6, §9"
build_phases: [0]
impacted_paths:
  - pyproject.toml
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-04 — Dependency management, pinning and lock-file policy

## 1. Summary

PFF AI will manage dependencies with **`pyproject.toml` + a committed lock file and
fully pinned, hash-verified versions**, with reproducible installs across dev, CI and
production images and automated vulnerability + update scanning (CLAUDE.md; 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §6).
The recommended tool is **uv** (fast, lock-file-native), with `pip-tools` as the
fallback if uv adoption is blocked.

## 2. Context and Problem Statement

CLAUDE.md fixes "`pyproject.toml` + lock file, pinned versions"; 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §6 sets the
project-structure standard. Unpinned or unlocked dependencies produce non-reproducible
builds, supply-chain risk, and "works on my machine" drift between CI and the container
image (ADR-D5-09). This ADR fixes the dependency toolchain and pinning policy.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | pyproject.toml + committed lock, pinned | CLAUDE.md |
| DR-F-02 | Reproducible installs dev/CI/image | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §6; ADR-D5-09 |
| DR-N-01 | Fast installs (CI, image build) | operational |
| DR-C-01 | Vulnerability + license scanning | ADR-D6-18 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | uv is acceptable in the org toolchain | Use pip-tools | Toolchain review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Reproducibility (lock + hashes) | 30 | Supply-chain integrity | Deterministic install |
| EC-02 | Speed | 20 | CI/image build time | Install time |
| EC-03 | Ecosystem/standard fit | 18 | pyproject-native | Compatibility |
| EC-04 | Security tooling integration | 16 | Scan/update | Scanner support |
| EC-05 | Simplicity/adoption | 16 | Team learning | Onboarding |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — uv (pyproject + uv.lock, hashes)

**Description.** uv for resolution/lock/install; `uv.lock` committed; hashes pinned.
**Strengths.** Very fast; lock-native; pyproject-native; reproducible.
**Weaknesses.** Newer tool; org familiarity varies.
**Cost / effort.** Low.

### 5.2 Option B — pip-tools (pyproject + requirements.txt lock)

**Description.** `pip-compile` to a hashed lock; pip install.
**Strengths.** Mature; simple; widely understood.
**Weaknesses.** Slower; two-file workflow; less ergonomic than uv.
**Cost / effort.** Low.

### 5.3 Option C — Poetry

**Description.** Poetry for deps + lock + packaging.
**Strengths.** Popular; integrated; lock file.
**Weaknesses.** Historically non-standard resolver quirks; slower; heavier.
**Cost / effort.** Low-medium.

### 5.4 Option D — PDM

**Description.** PDM (PEP 582/standards-focused).
**Strengths.** Standards-aligned; lock.
**Weaknesses.** Smaller community than the above.
**Cost / effort.** Low-medium.

### 5.5 Option E — Plain pip + manual pinning (no lock)

**Description.** Pin in requirements.txt by hand.
**Strengths.** Zero extra tooling.
**Weaknesses.** No transitive lock/hashes; drift; supply-chain risk.
**Cost / effort.** Low; unsafe.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| conda | Heavier; not needed for this stack |
| Unpinned installs | CLAUDE.md — must pin |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by CLAUDE.md and 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §6.

| Criterion | Weight | A: uv | B: pip-tools | C: Poetry | D: PDM | E: plain pip |
|---|---|---|---|---|---|---|
| EC-01 Reproducibility | 30 | 5 | 5 | 5 | 5 | 2 |
| EC-02 Speed | 20 | 5 | 3 | 3 | 4 | 3 |
| EC-03 Standard fit | 18 | 5 | 4 | 4 | 5 | 3 |
| EC-04 Security tooling | 16 | 4 | 5 | 4 | 4 | 3 |
| EC-05 Simplicity | 16 | 4 | 5 | 3 | 4 | 5 |
| **Weighted total** | **100** | **464** | **440** | **396** | **452** | **312** |

Totals (×20): **A = 464**, **D = 452**, **B = 440**, **C = 396**, **E = 312**.

**Sensitivity.** A, D and B are close; all give reproducible locks. uv's speed edges it
ahead; **pip-tools (B) is the explicit fallback** if uv is not permitted, since it is
the most conservative/mature. C (Poetry) trails on speed/standards.

## 7. Decision

**PFF AI will use `pyproject.toml` with uv and a committed `uv.lock` pinning all
transitive versions with hashes; if uv is blocked by org policy, pip-tools with a
hashed lock is the fallback (Option A, fallback B).** Vulnerability and license
scanning (ADR-D6-18) run in CI; the same lock builds the container image (ADR-D5-09)
for dev/CI/prod parity. Plain unpinned pip (E) is forbidden.

**Status rationale.** `Accepted` — CLAUDE.md mandates pinning + lock.

## 8. Architecture Detail

- `pyproject.toml` declares deps + `[tool.uv]`; `uv.lock` committed; `uv sync
  --frozen` in CI and image build for identical trees.
- CI runs dependency vulnerability scan + license check (ADR-D6-18, D7-09).
- Update automation (e.g. scheduled dependency PRs) proposes bumps; lock regenerated
  by tooling, never hand-edited.

## 9. Consequences

### 9.1 Positive
- Deterministic, fast, scanned installs; dev/CI/prod parity.
### 9.2 Negative
- uv relatively new; fallback documented.
### 9.3 Neutral
- Underpins image immutability (D5-09).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Tool familiarity (uv new) | Speed + reproducibility | Backend Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Tooling; no business authority |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | Lock file pins exact versions |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Supply-chain compromise via dep | Low | High | M | Hash-pinned lock + scanning (ADR-D6-18) | Security Architect | Low |
| RSK-02 | uv unsupported in org | Low | Low | L | Fallback to pip-tools | Backend Lead | Low |
| RSK-03 | Stale deps accrue CVEs | Med | Med | M | Automated update PRs | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Builds from committed lock | 100% | < 100% | CI | Per build |
| QM-02 | High/critical CVEs in deps | 0 | > 0 | Scanner | Continuous |
| QM-03 | Dev/CI/image tree parity | identical | drift | Build check | Per build |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Hash-pinning + scanning reduce supply-chain risk |
| Data classification touched | Internal |
| Personal data / PII | N/A |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Lock + scan results retained (SBOM) |
| Standards touched | ISO/IEC 27001, NIST SSDF |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 0 |
| Repository paths | `pyproject.toml`, `uv.lock` |
| Configuration | uv config; CI scan jobs |
| Contracts / schemas | N/A |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-09, D6-18, D7-09 |
| Effort estimate | S |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Lock committed and used with --frozen | CI check |
| AC-02 | Hashes pinned | Lock inspection |
| AC-03 | Vulnerability scan gates CI | CI config |
| AC-04 | Image builds from same lock | Build audit |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | CVE scan results; update PR flow |
| Alerting | New high/critical CVE |
| Runbook | `docs/runbooks/dependencies.md` |
| Failure mode and degradation | CI blocks on CVE/lock mismatch |
| Rollback | Revert lock |
| Support model impact | Backend team |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Tooling | none | CI minutes | Open-source |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | uv proves unstable | CI failures | Switch to pip-tools |
| RT-02 | Supply-chain incident | Incident | Tighten pinning/scanning |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-23 |
| Specification sections | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §6, §9 |
| Requirement IDs | TECH-DEP-* |
| Build phases | 0 |
| Code paths | `pyproject.toml`, `uv.lock` |
| Configuration | uv/CI |
| Tests | CI dep gates |
| Upstream ADRs | ADR-D5-02 |
| Downstream ADRs | ADR-D5-09, D6-18 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Backend Lead | Initial decision recorded. |
