---
id: ADR-D5-05
title: Lint/format toolchain — Ruff as the single tool
domain: 5 Technology
ws_ref: [WS-23]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Backend Lead
contributors: [Platform Engineer]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-02, ADR-D5-04, ADR-D7-09]
source_docs:
  - "MD files/6 Production/27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §11, §12, §23"
build_phases: [0]
impacted_paths:
  - pyproject.toml
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-05 — Lint/format toolchain — Ruff as the single tool

## 1. Summary

PFF AI will use **Ruff** as the single tool for both linting and formatting,
replacing the traditional flake8 + isort + black (+ plugins) stack (CLAUDE.md; doc 27
§11–§12). One fast Rust-based tool, one config, one CI step — with `ruff format` for
formatting and `ruff check` for linting including import sorting and magic-number
rules (doc 27 §23).

## 2. Context and Problem Statement

CLAUDE.md fixes "Ruff" for lint/format; doc 27 §11 sets formatting, §12 linting, §23
the magic-numbers rule. A multi-tool stack (black + isort + flake8 + plugins) is slow,
has overlapping/conflicting rules and multiple configs. This ADR records choosing Ruff
as the consolidated tool.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Single lint+format tool | CLAUDE.md; doc 27 §11–§12 |
| DR-N-01 | Fast (pre-commit + CI) | operational |
| DR-F-02 | Import sorting + rule coverage | doc 27 §12, §23 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Ruff covers needed rules | Add targeted extra linters | Rule audit |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Consolidation (one tool) | 26 | Simplicity; CLAUDE.md | # tools |
| EC-02 | Speed | 24 | Dev feedback/CI | Run time |
| EC-03 | Rule coverage | 22 | Lint quality | Rules available |
| EC-04 | Format stability/compat | 16 | black-compatible | Diff churn |
| EC-05 | Adoption/maturity | 12 | Stability | Adoption |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Ruff for lint + format (single tool)

**Description.** `ruff check` (lint, incl. isort, pyupgrade, bugbear-style rules) +
`ruff format` (black-compatible).
**Strengths.** One tool/config; extremely fast; broad rule set; black-compatible.
**Weaknesses.** A few niche linters not yet covered (add if needed).
**Cost / effort.** Low.

### 5.2 Option B — black + isort + flake8 (+ plugins)

**Description.** Traditional stack.
**Strengths.** Mature; familiar; huge plugin ecosystem.
**Weaknesses.** Slow; multiple configs; overlapping rules; more CI steps.
**Cost / effort.** Medium ongoing.

### 5.3 Option C — black + Ruff (format by black, lint by Ruff)

**Description.** Keep black, use Ruff only for linting.
**Strengths.** black's format familiarity.
**Weaknesses.** Two tools where one suffices; ruff format is black-compatible anyway.
**Cost / effort.** Low; redundant.

### 5.4 Option D — Pylint (+ black)

**Description.** Pylint for deep linting.
**Strengths.** Very thorough checks.
**Weaknesses.** Slow; noisy; still needs a formatter; heavier config.
**Cost / effort.** Medium-high.

### 5.5 Option E — No formatter, lint-only

**Description.** Lint but leave formatting to devs.
**Strengths.** Less tooling.
**Weaknesses.** Inconsistent style; diff noise; doc 27 §11 wants formatting.
**Cost / effort.** Low; inconsistent.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| yapf/autopep8 | Superseded by ruff format/black |
| Multiple overlapping linters | EC-01 — consolidation |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by CLAUDE.md and doc 27 §11–§12/§23.

| Criterion | Weight | A: Ruff | B: black+isort+flake8 | C: black+Ruff | D: Pylint+black | E: lint-only |
|---|---|---|---|---|---|---|
| EC-01 Consolidation | 26 | 5 | 2 | 3 | 2 | 3 |
| EC-02 Speed | 24 | 5 | 2 | 4 | 1 | 4 |
| EC-03 Rule coverage | 22 | 4 | 4 | 4 | 5 | 4 |
| EC-04 Format stability | 16 | 5 | 5 | 5 | 5 | 1 |
| EC-05 Maturity | 12 | 4 | 5 | 5 | 5 | 3 |
| **Weighted total** | **100** | **462** | **332** | **404** | **332** | **328** |

Totals (×20): **A = 462**, **C = 404**, **B = 332**, **D = 332**, **E = 328**.

**Sensitivity.** A leads C by 58; C only differs by keeping black redundantly. If a
niche rule Ruff lacks becomes essential, it is added as a targeted supplementary
linter without dislodging Ruff as primary (RT-01).

## 7. Decision

**PFF AI will use Ruff as the single lint + format tool (Option A):** `ruff format`
for formatting (black-compatible) and `ruff check` for linting including import
sorting and magic-number rules (doc 27 §23), configured in `pyproject.toml` and run in
pre-commit and CI (ADR-D7-09). The multi-tool stack (B), redundant black+Ruff (C),
Pylint (D) and lint-only (E) are rejected.

**Status rationale.** `Accepted` — CLAUDE.md mandates Ruff.

## 8. Architecture Detail

- `[tool.ruff]` in `pyproject.toml`: selected rule sets (incl. isort `I`, pyupgrade,
  bugbear, magic-number PLR2004 per §23), line length, target-version 3.11.
- Pre-commit hooks: `ruff format` + `ruff check --fix`; CI runs both in check mode
  (ADR-D7-09).

## 9. Consequences

### 9.1 Positive
- One fast tool/config; consistent style; fewer CI steps.
### 9.2 Negative
- A few niche linters may need supplementing.
### 9.3 Neutral
- Complements mypy (ADR-D5-02).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Some niche Pylint checks | Speed + consolidation | Backend Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Tooling; no business authority |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | Config pinned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Missing niche rule | Low | Low | L | Add targeted linter | Backend Lead | Low |
| RSK-02 | Format churn on adoption | Low | Low | L | One-time format commit | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Lint/format pass in CI | 100% | < 100% | CI | Per build |
| QM-02 | Lint+format run time | fast | rising | CI metrics | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Some Ruff rules catch insecure patterns |
| Data classification touched | Internal |
| Personal data / PII | N/A |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | CI results retained |
| Standards touched | ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 0 |
| Repository paths | `pyproject.toml`, `.pre-commit-config.yaml` |
| Configuration | ruff config |
| Contracts / schemas | N/A |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-02, D7-09 |
| Effort estimate | S |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Ruff is the only lint/format tool | Config review |
| AC-02 | Import sorting + magic-number rules enabled | ruff config |
| AC-03 | CI gates on ruff | CI config |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | CI status |
| Alerting | CI failures |
| Runbook | `docs/runbooks/ci.md` |
| Failure mode and degradation | CI blocks on lint/format errors |
| Rollback | Config revert |
| Support model impact | Backend team |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Tooling | none | none | Open-source |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Essential rule Ruff lacks | Review | Add targeted supplementary linter |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-23 |
| Specification sections | doc 27 §11–§12, §23 |
| Requirement IDs | TECH-LINT-* |
| Build phases | 0 |
| Code paths | `pyproject.toml` |
| Configuration | ruff |
| Tests | CI lint gate |
| Upstream ADRs | ADR-D5-02 |
| Downstream ADRs | ADR-D7-09 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Backend Lead | Initial decision recorded. |
