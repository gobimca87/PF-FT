---
id: ADR-D7-15
title: Engineering (dev-time) agents — scope and guardrails
domain: 7 Operations
ws_ref: [WS-32]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [Backend Lead, Security Architect, AI Governance Lead]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-09, ADR-D6-15, ADR-D3-12, ADR-D7-13, ADR-D1-11]
source_docs:
  - "MD files/5 QualityGovernance/23.PFF-FA-AI-ENGINEERING-AGENTS.md §2, §3, §4, §8, §9, §11, §12, §16, §23, §35, §48, §49"
build_phases: [12]
impacted_paths:
  - .github/workflows/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-15 — Engineering (dev-time) agents — scope and guardrails

## 1. Summary

PFF AI may use **AI engineering agents at development time** (code review, test/doc
generation, security scan, prompt review, eval, architecture-compliance) as **advisory,
least-privilege assistants that never merge, deploy, or bypass human review or CI gates**
(23.PFF-FA-AI-ENGINEERING-AGENTS.md §2–§4, §8–§12, §48–§49). Dev-time engineering agents are strictly separate from
the runtime AffiliationAgent (ADR-D1-11) and produce suggestions gated by the same CI/
governance as any human change.

## 2. Context and Problem Statement

23.PFF-FA-AI-ENGINEERING-AGENTS.md §2–§4 principle/scope/architecture, §8–§9 change-impact analysis/selection, §11–§12
permission levels/least-privilege, §16 restrictions, §23 security-agent restrictions, §35
doc-agent restrictions, §48–§49 architecture-compliance agent/rules. Engineering agents can
accelerate development but, unbounded, could merge unsafe code or leak secrets. This ADR
fixes their scope and guardrails (distinct from runtime agents in Domain 1/3).

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-C-01 | Advisory only; never merge/deploy | 23.PFF-FA-AI-ENGINEERING-AGENTS.md §11–§12, §16 |
| DR-C-02 | Least privilege | 23.PFF-FA-AI-ENGINEERING-AGENTS.md §12 |
| DR-F-01 | Change-impact-based agent selection | 23.PFF-FA-AI-ENGINEERING-AGENTS.md §8–§9 |
| DR-C-03 | Subject to CI gates + human review | ADR-D7-09, D6-15 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Engineering agents add net value | Disable low-value agents | Metrics |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Safety (no autonomous merge/deploy/leak) | 32 | Highest risk | Boundary |
| EC-02 | Least privilege | 22 | Blast radius | Permissions |
| EC-03 | Dev value (quality/velocity) | 20 | Why use them | Accepted suggestions |
| EC-04 | Governance integration | 14 | Same gates | Gate coverage |
| EC-05 | Simplicity | 12 | Maintainable | Concepts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Advisory, least-privilege engineering agents, gated by CI + human review

**Description.** Agents (code review, test/doc gen, security scan, prompt review, eval,
architecture compliance) run with least privilege (23.PFF-FA-AI-ENGINEERING-AGENTS.md §12), produce suggestions/PR
comments, never merge/deploy (§16); change-impact selects which run (§8–§9); all output
gated by CI (ADR-D7-09) and human review (ADR-D6-15).
**Strengths.** Safe, bounded, useful, governed.
**Weaknesses.** Agent quality/upkeep.
**Cost / effort.** Medium.

### 5.2 Option B — Autonomous engineering agents (can merge/deploy)

**Description.** Agents merge/deploy approved changes.
**Strengths.** Fastest.
**Weaknesses.** Unsafe; bypasses human authority/CI; 23.PFF-FA-AI-ENGINEERING-AGENTS.md §16 forbids.
**Cost / effort.** Low; forbidden.

### 5.3 Option C — No engineering agents (humans only)

**Description.** Don't use dev-time agents.
**Strengths.** Simplest; no new risk.
**Weaknesses.** Foregoes real productivity/quality gains the spec anticipates.
**Cost / effort.** Low; lower value.

### 5.4 Option D — Engineering agents with write access (auto-fix + auto-commit to branch)

**Description.** Agents auto-fix and commit to a branch (still PR-gated).
**Strengths.** Less manual toil.
**Weaknesses.** Broader privilege; needs strict guardrails; secret-leak/scope risk higher.
**Cost / effort.** Medium; more risk.

### 5.5 Option E — Advisory agents + supervised auto-fix on a branch (opt-in, least-privilege, still PR/CI-gated)

**Description.** Option A plus opt-in auto-fix that commits only to a feature branch,
never main, always PR/CI/human-gated, with least-privilege scoped tokens.
**Strengths.** A's safety + toil reduction where opted-in.
**Weaknesses.** Careful token scoping.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Agents that bypass CI/review | 23.PFF-FA-AI-ENGINEERING-AGENTS.md §16 |
| Agents with prod access | 23.PFF-FA-AI-ENGINEERING-AGENTS.md §12 (least privilege) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 23.PFF-FA-AI-ENGINEERING-AGENTS.md §2–§49.

| Criterion | Weight | A: Advisory | B: Autonomous | C: None | D: Write-access | E: Advisory+supervised auto-fix |
|---|---|---|---|---|---|---|
| EC-01 Safety | 32 | 5 | 1 | 5 | 3 | 5 |
| EC-02 Least privilege | 22 | 5 | 1 | 5 | 3 | 5 |
| EC-03 Dev value | 20 | 4 | 5 | 1 | 5 | 5 |
| EC-04 Governance | 14 | 5 | 2 | 5 | 4 | 5 |
| EC-05 Simplicity | 12 | 4 | 4 | 5 | 3 | 3 |
| **Weighted total** | **100** | **462** | **228** | **420** | **352** | **476** |

Totals (×20): **E = 476**, **A = 462**, **C = 420**, **D = 352**, **B = 228**.

**Sensitivity.** E (advisory + opt-in supervised auto-fix to a branch, still PR/CI/human-
gated) edges A by cutting toil without loosening safety. Adopted. Autonomous (B) is
forbidden; no-agents (C) foregoes value.

## 7. Decision

**PFF AI may use least-privilege, advisory dev-time engineering agents (code review, test/
doc generation, security scan, prompt review, eval, architecture compliance) that never
merge, deploy, or bypass CI/human review; opt-in supervised auto-fix may commit only to a
feature branch under PR/CI/human gates (Option E).** They are strictly separate from
runtime agents (ADR-D1-11). Autonomous agents (B) are forbidden; write-to-main (D) is
rejected.

## 8. Architecture Detail

- Engineering-agent supervisor (23.PFF-FA-AI-ENGINEERING-AGENTS.md §6–§7) selects agents by change-impact (§8–§9);
  agents run with least-privilege scoped tokens (§12) — read code, comment on PRs, or
  (opt-in) commit to a feature branch only; never main/prod.
- Outputs are suggestions gated by CI (ADR-D7-09) and human review (ADR-D6-15); security/
  doc agents have explicit restrictions (§23, §35); architecture-compliance agent enforces
  layering rules (§48–§49; ADR-D2-01). Agent actions audited (ADR-D6-17).

## 9. Consequences

### 9.1 Positive
- Productivity/quality gains with no autonomous-merge/deploy risk.
### 9.2 Negative
- Agent quality/token-scope upkeep.
### 9.3 Neutral
- Separate from runtime agents.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Full automation of dev tasks | Safety + human authority | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Humans/CI decide merges; agents advise |
| Precedence chain | N/A (dev-time) |
| Four-state separation | Dev-time only; no runtime state |
| Versioned artefacts | Agent configs versioned |
| Adam persona governs *how*, not *what* | N/A (not the Adam runtime persona) |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Agent commits unsafe code | Low | High | M | Advisory/branch-only + CI + human review | AI Arch Lead | Low |
| RSK-02 | Agent leaks secrets/code externally | Low | High | M | Least-privilege; in-tenancy; data-boundary (ADR-D6-07) | Security Architect | Low |
| RSK-03 | Over-reliance reduces human scrutiny | Med | Med | M | Human review mandatory; agent output labelled | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Autonomous merges/deploys by agents | 0 | > 0 | Audit | Continuous |
| QM-02 | Agent suggestion acceptance rate | tracked | very low | PR data | Monthly |
| QM-03 | Agent token scope violations | 0 | > 0 | Access audit | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Scoped dev-time agents; no prod access |
| Data classification touched | Source code (Internal) |
| Personal data / PII | No prod data access |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Agent actions audited |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 12 |
| Repository paths | `.github/workflows/` (agent runners) |
| Configuration | Agent scopes/permissions; impact rules |
| Contracts / schemas | Agent output format |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-09, D6-15, D3-12 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Agents cannot merge/deploy | Permission audit |
| AC-02 | Least-privilege tokens | Access audit |
| AC-03 | Output gated by CI + human review | Workflow review |
| AC-04 | Auto-fix commits only to feature branch | Config test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Agent runs; acceptance; scope |
| Alerting | Scope violations |
| Runbook | `docs/runbooks/engineering-agents.md` |
| Failure mode and degradation | Agent failure → humans proceed unaffected |
| Rollback | Disable agent |
| Support model impact | AI platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Engineering agents | M | inference | Build + LLM calls |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Low agent value | QM-02 | Disable/replace agent |
| RT-02 | Agent-caused incident | Incident | Tighten scope/guardrails |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-32 |
| Specification sections | 23.PFF-FA-AI-ENGINEERING-AGENTS.md §2–§4, §8–§12, §16, §23, §35, §48–§49 |
| Requirement IDs | ENG-AGENT-* |
| Build phases | 12 |
| Code paths | `.github/workflows/` |
| Configuration | agent scopes |
| Tests | permission/scope tests |
| Upstream ADRs | ADR-D7-09, D6-15 |
| Downstream ADRs | ADR-D7-13 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
