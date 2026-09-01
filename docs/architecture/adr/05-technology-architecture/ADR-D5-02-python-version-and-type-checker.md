---
id: ADR-D5-02
title: Python version range and primary type checker — mypy
domain: 5 Technology
ws_ref: [WS-23]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Backend Lead
contributors: [Principal Architect, AI Architecture Lead]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes:
  - "docs/adr/0002-python-version-and-type-checker.md"
superseded_by: []
related_adrs: [ADR-D5-01, ADR-D5-03, ADR-D5-05, ADR-D7-09]
source_docs:
  - "MD files/6 Production/27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §9, §13, §14, §16"
build_phases: [0, 1]
impacted_paths:
  - pyproject.toml
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-02 — Python version range and primary type checker — mypy

> **Supersedes** `docs/adr/0002-python-version-and-type-checker.md` with the full DAR
> evaluation. The decision is unchanged: Python `>=3.11,<3.13`, **mypy** (strict) as
> the single primary type checker. `docs/adr/0002` is left in place per ADR-D0-01.

## 1. Summary

PFF AI will target **Python `>=3.11,<3.13`** and use **mypy in strict mode** (with the
`pydantic.mypy` plugin) as the single primary type checker across CI and pre-commit.
CLAUDE.md requires exactly one primary checker; mypy is chosen for its maturity,
Pydantic-plugin support and ecosystem alignment (27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §13–§14).

## 2. Context and Problem Statement

27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §9 requires a pinned Python version range; §13–§14 require static type checking
and a type-annotation standard; §16 fixes the Pydantic standard. CLAUDE.md leaves the
checker as a Phase-0 decision but insists on **one** primary tool (mypy or pyright).
Running two checkers produces conflicting diagnostics and ignore-comment dialects.
This ADR fixes the version range and the single checker.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Pinned, supported Python range | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §9 |
| DR-F-02 | One primary strict type checker | CLAUDE.md; 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §13 |
| DR-F-03 | First-class Pydantic v2 typing | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §16; ADR-D5-03 |
| DR-N-01 | CI + pre-commit consistency | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §12–§13 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Dependencies support 3.11–3.12 | Adjust range | CI matrix |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Type-checking correctness/strictness | 26 | Catch bugs early | Strict-mode coverage |
| EC-02 | Pydantic v2 support | 22 | Boundary models everywhere | Plugin fidelity |
| EC-03 | Ecosystem/maturity | 18 | Stability, docs | Adoption |
| EC-04 | CI performance | 14 | Fast feedback | Check time |
| EC-05 | Editor/IDE integration | 12 | DX | IDE support |
| EC-06 | Single-tool simplicity | 8 | CLAUDE.md rule | One tool |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Python 3.11–3.12 + mypy strict (+ pydantic.mypy)

**Description.** Pin `>=3.11,<3.13`; mypy strict with the Pydantic plugin in CI +
pre-commit.
**Strengths.** Mature; excellent Pydantic-plugin; wide adoption; strict catches most.
**Weaknesses.** Slower than pyright on large trees (acceptable at this size).
**Cost / effort.** Low.

### 5.2 Option B — Python 3.11–3.12 + pyright/basedpyright

**Description.** Use pyright as the primary checker.
**Strengths.** Very fast; excellent inference; great VS Code integration.
**Weaknesses.** Node dependency in CI; different ignore dialect; Pydantic plugin story
weaker than mypy's dedicated plugin; team more mypy-familiar.
**Cost / effort.** Low; ecosystem mismatch.

### 5.3 Option C — Both mypy + pyright

**Description.** Run both.
**Strengths.** Maximum coverage.
**Weaknesses.** Conflicting diagnostics/ignore dialects; violates CLAUDE.md "one
primary"; double CI cost.
**Cost / effort.** Higher; disallowed.

### 5.4 Option D — Python 3.12 only (single version)

**Description.** Pin exactly 3.12.
**Strengths.** Simpler matrix; newest features.
**Weaknesses.** Less deployment flexibility; some deps may lag; range is safer.
**Cost / effort.** Low; less flexible.

### 5.5 Option E — No enforced type checking (annotations advisory)

**Description.** Annotate but don't gate.
**Strengths.** Fastest CI.
**Weaknesses.** Loses the correctness benefit; violates 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §13.
**Cost / effort.** Low; unsafe.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Python ≤3.10 | Misses 3.11+ typing/perf; 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §9 |
| Pyre/other checkers | Smaller ecosystem than mypy/pyright |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §9/§13–§16 and CLAUDE.md.

| Criterion | Weight | A: mypy | B: pyright | C: both | D: 3.12-only+mypy | E: no checking |
|---|---|---|---|---|---|---|
| EC-01 Strictness | 26 | 5 | 5 | 5 | 5 | 1 |
| EC-02 Pydantic support | 22 | 5 | 3 | 5 | 5 | 2 |
| EC-03 Maturity | 18 | 5 | 4 | 4 | 5 | 3 |
| EC-04 CI perf | 14 | 3 | 5 | 2 | 3 | 5 |
| EC-05 IDE integration | 12 | 4 | 5 | 5 | 4 | 3 |
| EC-06 Single-tool | 8 | 5 | 5 | 1 | 5 | 5 |
| **Weighted total** | **100** | **458** | **436** | **404** | **466** | **256** |

Totals (×20): **D = 466**, **A = 458**, **B = 436**, **C = 404**, **E = 256**.

**Sensitivity.** D (3.12-only) edges A by 8 purely on matrix simplicity, but a version
*range* gives deployment flexibility with negligible cost and matches legacy 0002 —
so **A is chosen** (range over single version). B (pyright) is close but the dedicated
`pydantic.mypy` plugin and team familiarity tip it to mypy; C violates the one-tool
rule; E is unsafe.

## 7. Decision

**PFF AI targets Python `>=3.11,<3.13` and uses mypy strict (with `pydantic.mypy`) as
the single primary type checker in CI and pre-commit (Option A).** pyright may be used
locally by individuals but is not the CI gate and pyright-specific ignores are
disallowed. This confirms and supersedes `docs/adr/0002`.

**Status rationale.** `Accepted` — resolves the Phase-0 choice; unchanged from 0002.

## 8. Architecture Detail

- `pyproject.toml`: `requires-python = ">=3.11,<3.13"`; `[tool.mypy]` strict with
  `plugins = ["pydantic.mypy"]`; CI job `mypy src` (27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §13); pre-commit hook.
- Typed domain objects and Pydantic at boundaries (27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §14–§16; ADR-D5-03).

## 9. Consequences

### 9.1 Positive
- Strong static guarantees; one consistent checker; Pydantic-aware.
### 9.2 Negative
- mypy slower than pyright on very large trees (not an issue at current size).
### 9.3 Neutral
- Aligns with Ruff (ADR-D5-05) and CI gates (ADR-D7-09).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| pyright's speed | Pydantic-plugin fidelity + maturity | Backend Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Tooling; no business authority |
| Precedence chain | N/A |
| Four-state separation | Types enforce state-model boundaries |
| Versioned artefacts | Version range + tool config pinned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | mypy CI time grows | Low | Low | L | Incremental mode; caching | Backend Lead | Low |
| RSK-02 | Dep incompatible with 3.11 floor | Low | Med | M | CI matrix; adjust range | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | mypy strict pass on `src` | 100% | < 100% | CI | Per build |
| QM-02 | mypy CI duration | acceptable | rising | CI metrics | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Type safety reduces certain bug classes |
| Data classification touched | Internal |
| Personal data / PII | N/A |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | CI results retained |
| Standards touched | ISO 9001 (quality) |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 0, 1 |
| Repository paths | `pyproject.toml` |
| Configuration | mypy strict + plugin |
| Contracts / schemas | Enforced by types |
| Migration | Supersedes 0002 (no change) |
| Dependencies on other ADRs | ADR-D5-01, D5-03, D5-05 |
| Effort estimate | S |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | `requires-python` = >=3.11,<3.13 | pyproject check |
| AC-02 | mypy strict gates CI | CI config |
| AC-03 | pydantic.mypy plugin enabled | config |
| AC-04 | No pyright-specific ignores in repo | lint |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | CI check status |
| Alerting | CI failures |
| Runbook | `docs/runbooks/ci.md` |
| Failure mode and degradation | CI blocks merge on type errors |
| Rollback | Config revert |
| Support model impact | Backend team |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Tooling | none | CI minutes | Open-source |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Dep requires ≥3.13 | CI | Move range forward |
| RT-02 | mypy CI time unacceptable | QM-02 | Re-evaluate pyright |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-23 |
| Specification sections | 27.PF-FT-AI-DEVELOPMENT-STANDARDS.md §9, §13–§16 |
| Requirement IDs | TECH-PY-* |
| Build phases | 0, 1 |
| Code paths | `pyproject.toml` |
| Configuration | mypy config |
| Tests | CI type-check gate |
| Upstream ADRs | ADR-D5-01 |
| Downstream ADRs | ADR-D5-03, D7-09 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Backend Lead | Initial decision recorded; supersedes docs/adr/0002 with full DAR. |
