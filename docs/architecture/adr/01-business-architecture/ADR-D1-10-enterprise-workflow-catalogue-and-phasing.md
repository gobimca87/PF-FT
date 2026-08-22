---
id: ADR-D1-10
title: Enterprise workflow catalogue, prioritisation and phasing
domain: 1 Business Architecture
ws_ref: [WS-05]
status: Accepted
version: 1.0.0
date: 2026-08-21
decision_owner: AI Product Owner
contributors: [Business Owner, AI Solution Architect, AI Platform Owner]
reviewers: [Compliance/Legal, AI Engineering Lead]
approver: AI Product Owner
supersedes: []
superseded_by: []
related_adrs: [ADR-D1-04, ADR-D1-05, ADR-D1-06, ADR-D1-11, ADR-D2-14, ADR-D8-08]
source_docs:
  - "MD files/2 Agent Runtime/7 PF-FT-AI-AGENTIC-ORCHESTRATION.md §6, §7"
  - "MD files/1 Foundation/2. PF-FT-AI-ARCHITECTURE-DETAILED.md §49"
  - "MD files/0 Workflow/pff_affiliation_e2e_flow.md"
build_phases: [23]
impacted_paths:
  - config/base/workflows.yaml
classification: Internal
review_due: 2027-02-21
---

# ADR-D1-10 — Enterprise workflow catalogue, prioritisation and phasing

## 1. Summary

A workflow catalogue is maintained as a **candidate list with explicit prioritisation
criteria**, not as a committed roadmap. Only affiliation is committed. Candidates are ranked by
a stated method so that the choice of workflow two is a decision made with evidence from
workflow one, rather than a plan made before that evidence exists.

## 2. Context and Problem Statement

Doc 7 §6 lists seven example agents — `AffiliationAgent`, `RegistrationAgent`,
`CompetitionAgent`, `DisciplineAgent`, `ClubAdministrationAgent`, `CourseAgent`,
`OfficialManagementAgent` — and then says, in one sentence: *"The actual agent catalog will be
finalized separately."*

`DEVELOPMENT-GUIDE.md` §2 goes further and flags this as a genuine reconciliation item: the
Foundation documents list a different set of eight capabilities, doc 7 lists these seven, and
the guide's instruction is to *"treat this as genuinely unfinalized — build only
`AffiliationAgent` first; defer the rest of the catalogue to a real product decision, don't
invent it."*

That instruction is unambiguous about what not to do and silent about what to do instead. The
practical problem is that "the catalogue is unfinalised" and "there is no catalogue" produce
very different behaviour, and the second is what tends to happen by default:

- **Nothing is written down.** The candidate workflows exist only as two inconsistent lists in
  specification documents, so nobody can answer what the platform might eventually cover.
- **Design decisions are made blind.** Whether the ERC schema should generalise, whether the
  tool registry should be workflow-scoped, whether the supervisor's routing model needs to
  handle overlapping intents — these depend on what else might arrive, and are being decided
  now, in Phases 4–11, before workflow two is chosen.
- **The choice of workflow two gets made by whoever asks loudest.** With no criteria recorded,
  the second workflow is selected by availability, enthusiasm or the accident of which county
  association complains first.

There is also a real risk in the opposite direction. Writing a committed roadmap of seven
workflows before the first one has shipped would be inventing exactly what
`DEVELOPMENT-GUIDE.md` §2 forbids, and would create expectations the programme cannot support.
The seven names in doc 7 §6 are *examples of workflow-level granularity*, offered to illustrate
§7's "one agent = one business interaction" principle. They are not a product plan, and reading
them as one would be a misreading of the source.

The decision needed is therefore narrow: how to hold a catalogue that informs design without
committing delivery.

## 3. Decision Drivers

### 3.1 Functional drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Candidate workflows must be recorded so design can generalise appropriately | doc 2 §49 |
| DR-F-02 | The catalogue must not read as a delivery commitment | `DEVELOPMENT-GUIDE.md` §2 |
| DR-F-03 | Prioritisation criteria must exist before the choice of workflow two is made | Programme practice |
| DR-F-04 | Workflow granularity must follow "one agent = one business interaction" | doc 7 §7 |
| DR-F-05 | Each candidate must record what is unknown about it, not only what is known | Honest catalogue |

### 3.2 Non-functional drivers

| ID | Driver | Target | Source |
|---|---|---|---|
| DR-N-01 | The catalogue must be cheap to maintain | ≤0.5 day per quarter | Programme practice |
| DR-N-02 | Adding a candidate must not require redesign | Catalogue is data, not architecture | doc 2 §49 |
| DR-N-03 | Prioritisation must be reproducible | Two people scoring independently agree within one rank | Programme practice |

### 3.3 Constraints

| ID | Constraint | Type | Source |
|---|---|---|---|
| DR-C-01 | Only `AffiliationAgent` is built in the first pass | Organisational | `DEVELOPMENT-GUIDE.md` §2; ADR-D1-11 |
| DR-C-02 | The agent catalogue is genuinely unfinalised and must not be invented | Organisational | doc 7 §6; `DEVELOPMENT-GUIDE.md` §2 |
| DR-C-03 | Every workflow's authority rests with the enterprise | Platform | ADR-D1-01 §7.2 |
| DR-C-04 | A workflow requires enterprise API coverage to be orchestrable | Platform | ADR-D1-01 §9.2 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Affiliation's build will materially change what is known about workflow cost and value | Prioritisation can proceed on current information | Reviewed at Phase 23 exit |
| DR-A-02 | Candidate workflows exist that are worth doing after affiliation | The platform is a single-workflow product; extensibility investment was misplaced | Business review at Phase 23 exit |
| DR-A-03 | The two inconsistent lists in the specifications describe overlapping intent, not conflicting plans | The reconciliation is substantive and needs enterprise resolution | Raised at the Phase 23 review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Informs current design decisions | 30 | Phases 4–11 are being built now and need to know what might arrive | Can a designer tell whether to generalise a component? |
| EC-02 | Avoids implying commitment | 25 | DR-C-02 is explicit; an invented roadmap creates expectations and forecloses a real product decision | Would a reader mistake it for a plan? |
| EC-03 | Quality of the eventual choice of workflow two | 20 | The catalogue's practical purpose | Are criteria stated and applied? |
| EC-04 | Maintenance cost | 15 | A catalogue nobody maintains misleads | Effort per quarter |
| EC-05 | Honesty about uncertainty | 10 | A catalogue implying more knowledge than exists is worse than none | Are unknowns recorded? |
| | **Total** | **100** | | |

Scoring scale: **1** unacceptable · **2** poor · **3** adequate · **4** good · **5** excellent.

## 5. Alternatives Considered

### 5.1 Option A — No catalogue; decide workflow two when affiliation ships

**Description.** Record nothing. Revisit the question at Phase 23 exit.

**Strengths.**
- Cannot possibly be mistaken for a commitment (EC-02).
- Zero maintenance.
- Maximum honesty about the fact that nothing is decided.
- Fully compliant with DR-C-02's letter.

**Weaknesses.**
- Leaves Phases 4–11 designing blind. Whether ERC sections should be workflow-generic, whether
  the tool registry needs workflow scoping, whether prompts should be workflow-parameterised —
  all decided now, all better decided knowing the candidate set (EC-01).
- When the question does arise, it arises with no criteria, so the choice is made ad hoc
  (EC-03).
- Loses the specification's own information: doc 7 §6's seven examples and the Foundation
  documents' eight are real signal about the domain even if not a plan.

**Cost / effort.** Nil.

### 5.2 Option B — Committed roadmap of the seven doc 7 agents

**Description.** Adopt doc 7 §6's list as the delivery plan, sequenced across releases.

**Strengths.**
- Maximum clarity for design and for stakeholders.
- Enables long-range resourcing and enterprise API planning.
- Uses the specification's own list rather than inventing one.

**Weaknesses.**
- Directly contradicts DR-C-02. Doc 7 §6 says the catalogue will be finalised separately;
  treating it as final is exactly the invention `DEVELOPMENT-GUIDE.md` §2 forbids (EC-02 fails).
- Ignores the Foundation documents' different list, silently resolving a reconciliation item
  the guide flags as open.
- Commits to workflows whose value, cost and API coverage are unknown.
- Creates expectations that will be broken, damaging credibility with county associations.

**Cost / effort.** Low to write; high in unmet expectations.

### 5.3 Option C — Candidate catalogue with prioritisation criteria, no commitment

**Description.** Record the candidates from both specification lists, reconciled to workflow
granularity per doc 7 §7. For each, record what is known, what is unknown, and its enterprise
API dependency. State the prioritisation criteria. Commit to nothing beyond affiliation.

**Strengths.**
- Gives designers the candidate set, so generalisation decisions are informed (EC-01).
- Explicitly non-committal; the artefact says so in its own heading (EC-02).
- Criteria exist before they are needed, so the choice of workflow two is made on evidence
  rather than advocacy (EC-03).
- Recording unknowns per candidate is more honest than a confident list (EC-05).
- Reconciles the two specification lists without deciding between them.

**Weaknesses.**
- Risk of being read as a plan despite disclaimers — lists look like roadmaps.
- Requires maintenance as understanding changes.
- Prioritisation criteria stated now may not be the right criteria when the decision arrives.

**Cost / effort.** Low one-off, low recurring.

### 5.4 Option D — Catalogue driven by enterprise API readiness

**Description.** Rank candidates purely by which have adequate enterprise API coverage today,
building whichever is most readily orchestrable.

**Strengths.**
- Objective and easily measured (DR-C-04 is a hard constraint anyway).
- Minimises delivery risk and enterprise change requests.
- Fastest possible delivery of workflow two.

**Weaknesses.**
- Optimises for ease rather than value. The most API-ready workflow may be the least useful.
- Lets enterprise API history determine product strategy.
- Ignores ADR-D1-04's framing: value is measured by completion of workflows users struggle
  with, and struggle does not correlate with API readiness.
- API coverage is a gating factor, not a ranking factor — it belongs as a constraint, which is
  how §7.3 treats it.

**Cost / effort.** Low.

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, with EC-02 tested by asking whether each option's
artefact would survive being shown to a county association without creating an expectation.

| Criterion | Weight | A: No catalogue | B: Committed roadmap | C: Candidates + criteria | D: API-readiness |
|---|---|---|---|---|---|
| EC-01 Informs design | 30 | 1 | 5 | 5 | 3 |
| EC-02 Avoids commitment | 25 | 5 | 1 | 4 | 3 |
| EC-03 Choice quality | 20 | 1 | 3 | 5 | 2 |
| EC-04 Maintenance cost | 15 | 5 | 3 | 4 | 4 |
| EC-05 Honesty about uncertainty | 10 | 5 | 1 | 5 | 3 |
| **Weighted total** | **100** | **270** | **300** | **455** | **295** |

- **Option C:** (30×5) + (25×4) + (20×5) + (15×4) + (10×5) = 150 + 100 + 100 + 60 + 50 = **455**

**Sensitivity.** C leads by 155 points and scores 4 or 5 throughout. Its only sub-maximum score
is EC-02, where A is better — a catalogue that does not exist cannot be mistaken for a plan.
That 25-point criterion would have to more than double, and EC-01 and EC-03 fall to near zero,
before A overtakes C; that would amount to asserting that informing design and improving the
eventual choice have no value. B is eliminated by DR-C-02 regardless of score.

## 7. Decision

### 7.1 A candidate catalogue, not a roadmap

The catalogue below records **what the platform might eventually cover**. Nothing in it beyond
affiliation is committed, scheduled or promised. It exists to inform design and to make the
choice of workflow two an evidenced decision.

### 7.2 Candidates

Reconciled from doc 7 §6's seven examples and the Foundation documents' eight capabilities, at
the granularity doc 7 §7 requires — one agent per business interaction, not per API.

| Candidate | Business interaction | Known | Unknown | API dependency |
|---|---|---|---|---|
| **Affiliation** | Affiliate a club and its teams for a season | Fully documented: 32 scenarios, 6 statuses, 6 flags | — | **Committed** — Phase 23 |
| **Player and team registration** | Register players and teams | Adjacent to affiliation; shares club, team and official context | Volume, seasonality, eligibility complexity | Unassessed |
| **Discipline** | Case, sanction, fine, appeal | Referenced in affiliation's debt rule (discipline/GRF cases) | Case model, appeal workflow, sensitivity of content | Unassessed |
| **County cups** | Cup entry and eligibility | Products configured in affiliation Phase 0; entry criteria by age, gender, step, day | Entry workflow, competition administration | Unassessed |
| **Officials management** | Appoint officials, manage accreditation | Officials and DBS appear in affiliation pre-checks | Appointment workflow, availability model | Unassessed |
| **Courses and accreditation** | Book and complete courses | `get_courses` appears in doc 7 §7's tool example | Course catalogue, booking, certification | Unassessed |
| **Club administration** | General club record maintenance | Broad; may be several interactions rather than one | Whether it is one workflow or many | Unassessed |
| **Insurance administration** | Cover selection and policy management | Partially covered within affiliation Phase 3 | Whether it is a standalone workflow at all | Partially covered |

The **Unknown** column is deliberately populated and is the most useful column in the table. A
candidate catalogue that recorded only what is known would imply the unknowns are small.

### 7.3 Prioritisation method

When workflow two is chosen, candidates are ranked on four criteria. API coverage is a **gate**,
not a criterion — a workflow without adequate enterprise API coverage is not rankable, it is
blocked, and the response is an enterprise change request (DR-C-04).

| Criterion | Weight | Question |
|---|---|---|
| **User struggle** | 40 | How much do users currently fail at this? Measured by abandonment, escalation and rework, per ADR-D1-04's framing. A process users complete easily is not a candidate however popular. |
| **Reuse of built capability** | 25 | How much of what affiliation built does this reuse? Measured against ADR-D1-05 QM-03's component inventory. |
| **Volume** | 20 | How many users, how often? Seasonal peaks count differently from steady load. |
| **Sensitivity** | 15 | How much safeguarding, disciplinary or personal-data exposure does it carry? Higher sensitivity is a reason for more care, and for later scheduling while the platform matures. |

Sensitivity is scored inversely — a highly sensitive workflow ranks lower for *earliness*, not
lower for value. Discipline is the clearest case: it is likely high on struggle and volume, and
carries content about individuals' conduct that a young platform should not handle first.

### 7.4 When the choice is made

At Phase 23 exit, not before. The inputs that make the choice sound do not exist until
affiliation has shipped:

- actual component reuse, from ADR-D1-05 QM-03;
- actual build cost against estimate;
- actual BM-01 to BM-04 outcomes, showing whether the value hypothesis held;
- enterprise API coverage assessments produced during affiliation's integration work.

Choosing earlier would mean choosing on the same information available today, which is the
condition DR-C-02 exists to avoid.

### 7.5 What this means for design now

The catalogue's immediate purpose. Designers building Phases 4–11 should assume:

- **Multiple workflows will exist.** Components are workflow-generic unless there is a specific
  reason otherwise. ERC sections, tool registration, prompt layers and evaluation harnesses are
  parameterised by workflow.
- **Workflows will share entities.** Club, team, official and season appear in nearly every
  candidate. Their ERC representations should be shared, not affiliation-specific.
- **Workflows will overlap in intent.** "My club's registration" could mean affiliation or
  player registration. The supervisor's routing must handle ambiguity from the start
  (ADR-D3-07), even though there is currently nothing to be ambiguous between.
- **Sensitivity varies.** Discipline content is more sensitive than cup entry. Guardrail and
  retention policies should be per-workflow configurable rather than global.

None of this commits to building any candidate. All of it is cheaper to design in now than to
retrofit.

**Status rationale.** Accepted. Tier 2d under ADR-D0-03 §7.1 — it concerns what the platform
supports — ratified by the AI Product Owner. Explicitly does **not** finalise the agent
catalogue, which remains open per doc 7 §6 and is tracked in ADR-D1-11.

## 8. Architecture Detail

### 8.1 Catalogue as data, not architecture

The catalogue lives in this ADR and, for the committed entry only, in
`config/base/workflows.yaml`. Candidates are not configured, not registered and not stubbed. A
candidate becomes configuration when it becomes a decision.

This is what makes DR-N-02 hold: adding a candidate to §7.2 is an amendment to this ADR with a
change-log row, and touches no code.

### 8.2 Relationship to the agent catalogue

Workflows and agents are not the same thing, and conflating them is how the doc 7 §6 list came
to look like a plan.

| | Workflow | Agent |
|---|---|---|
| What it is | A business interaction a user completes | A logical capability in the AI runtime that orchestrates one |
| Decided by | This ADR's candidate list plus §7.4's choice | ADR-D1-11 |
| Granularity | One business interaction (doc 7 §7) | One workflow, per doc 7 §6 |
| Currently | One committed, seven candidates | One built |

A candidate workflow does not imply a future agent of the same name. Club administration, for
instance, may prove to be several interactions and therefore several agents, or none.

### 8.3 Reconciling the two specification lists

`DEVELOPMENT-GUIDE.md` §2 flags that the Foundation documents and doc 7 list different sets.
§7.2 reconciles them by mapping to business interactions rather than choosing between the
lists:

| Foundation list | Doc 7 §6 list | §7.2 candidate |
|---|---|---|
| Affiliation | `AffiliationAgent` | Affiliation |
| Player Registration | `RegistrationAgent` | Player and team registration |
| Discipline | `DisciplineAgent` | Discipline |
| Accreditation | `CourseAgent` | Courses and accreditation |
| Insurance | — | Insurance administration |
| Officials | `OfficialManagementAgent` | Officials management |
| League Management | `CompetitionAgent` | County cups (competition) |
| Approval/Reviewer | — | *Not a workflow* — a role's view of other workflows, handled by archetype per ADR-D1-07 |
| — | `ClubAdministrationAgent` | Club administration |

The last row of the Foundation list is the substantive reconciliation: "Approval/Reviewer" is
not a workflow but a county administrator's participation in workflows others start. ADR-D1-07's
archetype model already handles it, so it does not need an agent. Recording that resolves part
of the open reconciliation without pre-empting the catalogue decision.

## 9. Consequences

### 9.1 Positive

- Designers building Phases 4–11 know what might arrive and can generalise proportionately.
- The choice of workflow two will be made with stated criteria and real evidence.
- The two inconsistent specification lists are reconciled to business interactions without
  either being adopted as a plan.
- Recording unknowns per candidate keeps the catalogue honest about how little is settled.
- "Approval/Reviewer" is resolved as an archetype rather than a workflow, removing one source
  of confusion.

### 9.2 Negative

- A list will be read as a roadmap by some readers regardless of the heading; the disclaimer
  bears real weight.
- §7.3's criteria may prove to be the wrong criteria by the time they are used, though they
  are revisable.
- Designing workflow-generically costs something now for a benefit that depends on DR-A-02
  holding.

### 9.3 Neutral

- Nothing beyond affiliation is committed, which is the position `DEVELOPMENT-GUIDE.md` §2
  already requires.
- Candidates carry no configuration and no code.

### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| The clarity of a committed roadmap | Not inventing a catalogue the specifications leave open | AI Product Owner |
| Some generalisation effort that may prove unnecessary | Components that do not need retrofitting for workflow two | AI Solution Architect |
| Deciding workflow two now | Deciding it with affiliation's evidence | Business Owner |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Every candidate in §7.2 is an enterprise-owned business capability per ADR-D1-06 §7.3. The catalogue records what the platform might *orchestrate*, never what it might decide. |
| Authoritative-truth precedence | Not applicable — no runtime data path. |
| Four-state separation | Supported by §7.5's guidance that workflow state be parameterised by workflow rather than global. |
| Versioned artefacts, never mutated in place | The catalogue is versioned as an ADR; adding a candidate is an amendment with a change-log row. |
| Adam persona governs how, never what | §7.5 notes that guardrail and retention policy should be per-workflow, which extends to persona exclusion zones per ADR-D1-09 §7.2. |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | The catalogue is read as a commitment by stakeholders | High | Medium | High | §7.1's explicit disclaimer; no candidate appears in configuration; the artefact is an ADR, not a roadmap document | AI Product Owner | Medium |
| RSK-02 | Workflow-generic design costs effort for workflows never built (DR-A-02 false) | Medium | Medium | Medium | Generalisation limited to §7.5's four specific areas, all of which have present-tense justification | AI Solution Architect | Low |
| RSK-03 | Workflow two is chosen before Phase 23 exit under commercial pressure | Medium | Medium | Medium | §7.4 states the required inputs; choosing without them is a decision requiring its own ADR | Business Owner | Medium |
| RSK-04 | §7.3's criteria prove wrong when applied | Medium | Low | Low | Criteria are revisable at the point of use; stating them now surfaces disagreement early | AI Product Owner | Low |
| RSK-05 | A high-sensitivity workflow is chosen second while the platform is immature | Low | High | Medium | Sensitivity scored inversely for earliness in §7.3; Compliance/Legal consulted on the choice | Compliance/Legal | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Candidate workflows appearing in configuration or code | 0 | ≥1 | `config/` and `src/` audit | Per release |
| QM-02 | Components in Phases 4–11 hard-coded to affiliation | 0 | ≥3 | Architecture review | Per phase |
| QM-03 | Workflow-two choice made with all four §7.4 inputs available | Yes | No | Phase 23 exit review | At Phase 23 exit |
| QM-04 | Independent prioritisation scorings agreeing within one rank | Yes | No | Dual scoring at the choice point | At the choice point |
| QM-05 | Catalogue maintenance effort | ≤0.5 day per quarter | >1 day | Timesheet | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None. No candidate is implemented. |
| Data classification touched | Internal. |
| Personal data / PII | None in the catalogue. §7.3's sensitivity criterion is where personal-data exposure enters the prioritisation. |
| Children's data and safeguarding | Two candidates carry material safeguarding exposure: officials management (DBS, welfare officers) and discipline (conduct cases, potentially involving minors). §7.3's inverse sensitivity scoring is intended to keep both from being chosen while the platform is young. Compliance/Legal is consulted on the choice per RSK-05. |
| UK GDPR lawful basis and rights impact | None now. Each future workflow needs its own assessment before selection; that is part of the sensitivity criterion. |
| Audit and evidential requirements | Records that the catalogue was deliberately left open per doc 7 §6, which is itself the evidence that it was not invented. |
| Standards touched | ISO/IEC 42001 (AI system planning and scope); ISO 9001 §6.2 (objectives and planning); CMMI-DEV PP. |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 23 (affiliation only); §7.5 informs Phases 4–11 |
| Repository paths | `config/base/workflows.yaml` — affiliation only |
| Configuration | Workflow-parameterised guardrail, retention and prompt configuration per §7.5 |
| Contracts / schemas | Shared entity representations (club, team, official, season) designed workflow-generically |
| Migration | None |
| Dependencies on other ADRs | ADR-D1-05 (affiliation committed), ADR-D1-11 (agent catalogue) |
| Effort estimate | Small for the catalogue; §7.5's generalisation is absorbed into Phases 4–11 |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | No candidate workflow appears in configuration or code | `config/` and `src/` audit; QM-01 |
| AC-02 | ERC sections for club, team, official and season are not affiliation-specific | Schema review |
| AC-03 | Tool registry, prompt layers and evaluation harness are workflow-parameterised | Architecture review; QM-02 |
| AC-04 | Guardrail and retention configuration is per-workflow capable | Configuration schema test |
| AC-05 | The choice of workflow two cites all four §7.4 inputs | Phase 23 exit review record; QM-03 |
| AC-06 | Every candidate in §7.2 has a populated Unknown column | This record |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | None runtime |
| Alerting | None |
| Runbook | None |
| Failure mode and degradation | The failure mode is design that hard-codes affiliation, discovered only when workflow two costs as much as workflow one. QM-02 is the leading indicator; ADR-D1-05 QM-03 is the lagging one. |
| Rollback | Not applicable |
| Support model impact | None until workflow two |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Catalogue definition and reconciliation | ~1 day | ~0.5 day per quarter | This record |
| Workflow-generic design in Phases 4–11 | Absorbed | — | §7.5's four areas |
| Prioritisation exercise at Phase 23 exit | ~2 days | — | §7.3 method plus API coverage assessment |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Phase 23 exit reached | Phase review | Apply §7.3's method; choose workflow two or record that none is chosen |
| RT-02 | QM-02 finds components hard-coded to affiliation | Phase review | Correct before the phase exits; retrofitting after workflow two is chosen is more expensive |
| RT-03 | The enterprise finalises the agent catalogue | Change notice | Reconcile §7.2 against it; the enterprise decision supersedes this candidate list |
| RT-04 | A stakeholder treats the catalogue as a commitment | Stakeholder communication | Reinforce §7.1; consider whether the artefact needs a stronger disclaimer |
| RT-05 | A candidate not in §7.2 is proposed | Product review | Add it with its Unknown column populated; the list is not closed |
| RT-06 | Affiliation's BM-01 to BM-04 show the value hypothesis failing (DR-A-02) | Quarterly review | Question whether a workflow two is warranted at all |

**Scheduled review:** 2027-02-21, or at Phase 23 exit, whichever is sooner.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-05 Enterprise Workflow Catalogue |
| Specification sections | doc 7 §6 (Workflow-Level Agent Responsibility — the seven examples and the "finalized separately" note), §7 (Why Workflow-Level Agents); doc 2 §49 (Architecture Extension Model); `DEVELOPMENT-GUIDE.md` §2 (reconciliation item 2); affiliation flow |
| Requirement IDs | Per ADR-D1-12 |
| Build phases | 23; informs 4–11 |
| Code paths | Workflow-parameterised components across `src/pf_ft_ai/` |
| Configuration | `config/base/workflows.yaml` |
| Tests | AC-01 to AC-06 |
| Upstream ADRs | ADR-D1-04, ADR-D1-05, ADR-D1-06 |
| Downstream ADRs | ADR-D1-11, ADR-D2-14, ADR-D3-07, ADR-D8-08 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-21 | AI Product Owner | Initial decision recorded. Candidate catalogue with prioritisation criteria and no commitment beyond affiliation; the two specification lists reconciled to business interactions; "Approval/Reviewer" resolved as an archetype rather than a workflow. |
