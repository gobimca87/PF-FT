# PFF AI — Enterprise Architecture Decision Library

This directory holds the architecture decision records (ADRs) for **PFF AI**, the
conversational orchestration layer built on top of the FA's PFF platform.

The 29 specification documents in `MD files/` describe *what* the architecture is. This
library records *why* — the drivers, the alternatives that were weighed, the criteria
they were weighed against, the decision, and what it costs. Each ADR is a standalone,
reviewable document written to the template in [`TEMPLATE.md`](TEMPLATE.md), which is
aligned to CMMI-DEV **Decision Analysis and Resolution (DAR)** with ML4/ML5 practices
(quantitative management, causal analysis) folded in.

## How to use this library

| You want to | Go to |
|---|---|
| Find a decision by ID or topic | The domain index below |
| See every decision with its status and owner | [`_register/decision-register.md`](_register/decision-register.md) |
| Trace a decision back to a workshop sheet, spec section, or code path | [`_register/traceability-matrix.md`](_register/traceability-matrix.md) |
| See what is still awaiting sign-off | [`_register/open-decisions.md`](_register/open-decisions.md) |
| Write a new ADR | [`TEMPLATE.md`](TEMPLATE.md) and [ADR-D0-02](00-decision-programme/ADR-D0-02-adr-identification-lifecycle-supersession.md) |
| Know who ratifies a decision | [ADR-D0-03](00-decision-programme/ADR-D0-03-decision-authority-and-review-board.md) |

## Identification scheme

```
ADR-D<domain>-<sequence>       e.g. ADR-D3-14
```

Domain-prefixed rather than globally sequential, so the domain is legible in every
cross-reference and a new decision slots into its domain without renumbering the
library. Filenames add a kebab-case slug:

```
docs/architecture/adr/03-ai-architecture/ADR-D3-14-slm-provider-abstraction.md
```

The full rules — status lifecycle, supersession, amendment vs. replacement — are in
[ADR-D0-02](00-decision-programme/ADR-D0-02-adr-identification-lifecycle-supersession.md).

## Relationship to `docs/adr/`

The four earlier records in [`docs/adr/`](../../adr/) (`0001` ADR process, `0002` Python
version and type checker, `0003` deferred decisions log, `0004` memory/cache store) predate
this library and use Michael Nygard's short format. They remain in place, unmodified, as
the historical record. Four ADRs here supersede them with the fuller treatment —
`ADR-D0-01`, `ADR-D0-04`, `ADR-D5-02`, `ADR-D4-10` — each declaring the file it supersedes
in its front matter. **This library is the current source of truth for architecture
decisions;** `docs/adr/` is retained for provenance, not for consultation.

## Relationship to the workshop pack

Every ADR carries a `ws_ref` to one of the 37 architecture workshop sheets (WS-01 … WS-37)
across the eight domains. The workshop sheets are *deliverables*; the ADRs are *decisions*.
Most sheets decompose into several decisions, which is why 37 sheets yield 136 ADRs. The
sheet-to-ADR mapping is in
[`_register/traceability-matrix.md`](_register/traceability-matrix.md).

## Binding constraints on every decision

Every ADR in this library must demonstrate conformance (§10 of the template) with the
project's non-negotiable constraints, defined in `CLAUDE.md` and recorded as decisions in
[ADR-D1-02](01-business-architecture/ADR-D1-02-golden-rule-binding-architectural-constraint.md)
and [ADR-D1-03](01-business-architecture/ADR-D1-03-authoritative-truth-precedence-chain.md):

> **Enterprise systems decide and execute; the AI platform interprets, orchestrates,
> contextualises, explains and communicates.**

> **Enterprise API / Enterprise Event > ERC > Cache > RAG > SLM output.**

---

## Domain index

### Domain 0 — Decision Programme and Governance

| ID | Decision | WS |
|---|---|---|
| [D0-01](00-decision-programme/ADR-D0-01-adopt-adr-driven-architecture-governance.md) | Adopt ADR-driven architecture governance with a CMMI DAR-aligned template | WS-36 |
| [D0-02](00-decision-programme/ADR-D0-02-adr-identification-lifecycle-supersession.md) | ADR identification, status lifecycle, supersession and amendment policy | WS-36 |
| [D0-03](00-decision-programme/ADR-D0-03-decision-authority-and-review-board.md) | Decision authority model (RACI) and Architecture Review Board cadence | WS-36 |
| [D0-04](00-decision-programme/ADR-D0-04-open-decision-register-and-escalation.md) | Open and deferred decision register with escalation path | WS-36 |

### Domain 1 — Business Architecture

| ID | Decision | WS |
|---|---|---|
| D1-01 | PFF AI scope boundary — orchestration layer, not system of record | WS-01 |
| D1-02 | The Golden Rule as a binding architectural constraint | WS-01/02 |
| D1-03 | Authoritative-truth precedence chain | WS-01/02 |
| D1-04 | Business problem framing and measurable success definition | WS-02 |
| D1-05 | Club Affiliation as the first end-to-end reference workflow | WS-02/05 |
| D1-06 | Business capability map and capability ownership model | WS-03 |
| D1-07 | Persona model and access archetypes | WS-04 |
| D1-08 | Conversational journey design principles and HIL touchpoints | WS-04 |
| D1-09 | Adam AI persona charter — football-commentary tone as a governed decision | WS-04 |
| D1-10 | Enterprise workflow catalogue, prioritisation and phasing | WS-05 |
| D1-11 | Agent catalogue scope — `AffiliationAgent` only in the first pass | WS-05 |
| D1-12 | FR/NFR baseline and requirement-ID traceability scheme | WS-06 |

### Domain 2 — Enterprise Application Architecture

| ID | Decision | WS |
|---|---|---|
| D2-01 | Layered architecture and enforced dependency rule | WS-07 |
| D2-02 | Single AI runtime — agents as logical capabilities, not one service per agent | WS-07 |
| D2-03 | Dual runtime model — request-driven and event-driven paths | WS-07 |
| D2-04 | Conversation Manager responsibility boundary | WS-07/08 |
| D2-05 | Supervisor intent routing and candidate-agent selection | WS-08 |
| D2-06 | Workflow orchestration engine — LangGraph | WS-08 |
| D2-07 | Graph state representation — TypedDict internal, Pydantic at boundaries | WS-08 |
| D2-08 | Sequential, parallel and hybrid execution with bounded parallelism | WS-08 |
| D2-09 | Agent Harness as the single controlled execution boundary | WS-08 |
| D2-10 | Long-running workflow suspend/resume and HIL continuation | WS-08/11 |
| D2-11 | Workflow idempotency, retry, timeout and loop-limit policy | WS-08 |
| D2-12 | ERC as the enterprise context boundary | WS-09 |
| D2-13 | Enterprise integration pattern — API catalogue, tool registry, MCP | WS-10 |
| D2-14 | 18-microservice integration matrix, ownership and coupling rules | WS-10 |
| D2-15 | Enterprise API contract, versioning and compatibility strategy | WS-10 |
| D2-16 | Asynchronous eventing platform — Azure Service Bus | WS-11 |
| D2-17 | Event envelope, schema registry and event contract versioning | WS-11 |
| D2-18 | Message reliability — deduplication, idempotency, DLQ, reconciliation | WS-11 |
| D2-19 | Portal link registry and no-invented-URL enforcement | WS-10 |

### Domain 3 — AI Architecture

| ID | Decision | WS |
|---|---|---|
| D3-01 | AI capability taxonomy and capability-to-component mapping | WS-12 |
| D3-02 | Agentic architecture style — supervisor plus workflow agents | WS-13 |
| D3-03 | Agent contract, registration and lifecycle model | WS-13 |
| D3-04 | Tool-calling architecture and the tool-validation boundary | WS-13 |
| D3-05 | Deterministic routing versus model-decided routing | WS-14 |
| D3-06 | Intent classification approach | WS-14 |
| D3-07 | Clarification, disambiguation and confirmation strategy | WS-14 |
| D3-08 | Transaction-uncertainty and ambiguous-outcome conversational policy | WS-14 |
| D3-09 | Layered prompt composition architecture | WS-15 |
| D3-10 | Adam persona prompt layer — versioned, reusable, separate from workflow logic | WS-15 |
| D3-11 | Prompt storage, versioning and promotion | WS-15 |
| D3-12 | Prompt injection defence inside the prompt layer | WS-15 |
| D3-13 | SLM strategy — hosted inference first, self-hosted as target | WS-16 |
| D3-14 | SLM provider abstraction and provider-neutral contract | WS-16 |
| D3-15 | Model registry — capability, purpose and status model | WS-16 |
| D3-16 | Generation parameter and temperature strategy per task class | WS-16 |
| D3-17 | Structured output strategy and output validation | WS-16 |
| D3-18 | SLM fallback, degradation and circuit-breaking | WS-16 |
| D3-19 | Streaming strategy and its interaction with structured output | WS-16 |
| D3-20 | RAG scope — knowledge and FAQ only, never business truth | WS-17 |
| D3-21 | Document ingestion and chunking strategy | WS-17 |
| D3-22 | Retrieval, reranking and mandatory-citation policy | WS-17 |
| D3-23 | **Embedding model selection**, versioning and re-embedding strategy — awaiting retrieval-eval sign-off | WS-17 |
| D3-24 | **Vector store selection** — awaiting sign-off | WS-17 |
| D3-25 | Context engineering — assembly order, precedence and token budget allocation | WS-18 |

### Domain 4 — Information Architecture

| ID | Decision | WS |
|---|---|---|
| D4-01 | Four-state separation — conversation, session, workflow, enterprise | WS-19/22 |
| D4-02 | ERC schema, identity and section-level versioning | WS-19 |
| D4-03 | ERC provenance, freshness policy and authority levels | WS-19 |
| D4-04 | ERC collection planning, batching and pagination safety | WS-19 |
| D4-05 | ERC partial-failure semantics and completeness tracking | WS-19 |
| D4-06 | ERC invalidation, patching and event-driven refresh | WS-19 |
| D4-07 | Data and knowledge architecture — domains, classification, ownership | WS-20 |
| D4-08 | Canonical identifier and reference-data strategy | WS-20 |
| D4-09 | Metadata, response envelope and error-code standards | WS-21 |
| D4-10 | Session and conversation state store — Azure Managed Redis | WS-22 |
| D4-11 | Memory architecture — retention, ranking and summarisation | WS-22 |
| D4-12 | Cache architecture — namespaces, TTL, invalidation, stampede protection | WS-22 |

### Domain 5 — Technology Architecture

| ID | Decision | WS |
|---|---|---|
| D5-01 | Implementation language and API framework — Python and FastAPI | WS-23 |
| D5-02 | Python version range and primary type checker | WS-23 |
| D5-03 | Boundary validation standard — Pydantic | WS-23 |
| D5-04 | Dependency management, pinning and lock-file policy | WS-23 |
| D5-05 | Lint and format toolchain — Ruff as the single tool | WS-23 |
| D5-06 | Configuration architecture and immutable release-manifest model | WS-23 |
| D5-07 | Secret management — Key Vault with secret-reference indirection | WS-23/25 |
| D5-08 | Cloud platform and compute — Azure and AKS | WS-24 |
| D5-09 | Container image, registry and image-immutability policy | WS-24 |
| D5-10 | **Self-hosted SLM serving stack** — awaiting sign-off | WS-24 |
| D5-11 | GPU node pool and CPU/GPU workload separation | WS-24 |
| D5-12 | **Infrastructure-as-Code tool** — awaiting sign-off | WS-24 |
| D5-13 | **Kubernetes manifest tool** — awaiting sign-off | WS-24 |
| D5-14 | Environment model — five stages | WS-24 |
| D5-15 | API gateway and authorization boundary — APIM | WS-25 |
| D5-16 | Shared HTTP client standard | WS-25/26 |
| D5-17 | Scalability and autoscaling model | WS-26 |
| D5-18 | Latency budget decomposition and per-hop SLO allocation | WS-26 |

### Domain 6 — Security and Governance

| ID | Decision | WS |
|---|---|---|
| D6-01 | Zero-trust model and trust-zone definition | WS-27 |
| D6-02 | Authentication and authorization boundary | WS-27 |
| D6-03 | Authorization context integrity and propagation | WS-27 |
| D6-04 | Network segmentation, private connectivity and egress control | WS-27 |
| D6-05 | Encryption, key management and rotation | WS-27 |
| D6-06 | Data classification, PII protection and data-flow policy | WS-27/29 |
| D6-07 | External SLM data boundary | WS-27 |
| D6-08 | Prompt injection and jailbreak defence architecture | WS-27 |
| D6-09 | Guardrail pipeline placement and fail-closed policy | WS-27 |
| D6-10 | Tool allowlist, parameter and output security | WS-27 |
| D6-11 | MCP server trust model and response validation | WS-27 |
| D6-12 | RAG ACL enforcement and retrieval-time authorization | WS-27 |
| D6-13 | Responsible AI principles and prohibited-use boundary | WS-28 |
| D6-14 | Human oversight and HIL governance model | WS-28 |
| D6-15 | Model, prompt and index change governance | WS-28 |
| D6-16 | UK GDPR, safeguarding and children's-data handling | WS-29 |
| D6-17 | Audit logging and evidential record model | WS-29 |
| D6-18 | Standards conformance mapping | WS-30 |

### Domain 7 — Operations

| ID | Decision | WS |
|---|---|---|
| D7-01 | Platform observability stack | WS-31 |
| D7-02 | AI-specific observability | WS-31 |
| D7-03 | Correlation ID and trace-propagation standard | WS-31 |
| D7-04 | Logging standards, levels and redaction rules | WS-31 |
| D7-05 | Error taxonomy and exception hierarchy | WS-31 |
| D7-06 | Resilience patterns | WS-31 |
| D7-07 | SLI/SLO definition and error-budget policy | WS-31 |
| D7-08 | Alerting, severity model and on-call escalation | WS-31/33 |
| D7-09 | CI pipeline design and mandatory quality gates | WS-32 |
| D7-10 | CD pipeline and deployment strategy | WS-32 |
| D7-11 | Branching, versioning and release-train model | WS-32 |
| D7-12 | AI engineering lifecycle — prompt, model and index release bundles | WS-32 |
| D7-13 | Evaluation and regression gates in CI | WS-32 |
| D7-14 | Test strategy and test pyramid | WS-32 |
| D7-15 | Engineering (dev-time) agents — scope and guardrails | WS-32 |
| D7-16 | Operational support model and runbook ownership | WS-33 |
| D7-17 | Incident management and AI-specific incident classification | WS-33 |
| D7-18 | Disaster recovery, business continuity, RPO and RTO | WS-33 |

### Domain 8 — Business Value and Evolution

| ID | Decision | WS |
|---|---|---|
| D8-01 | Cost model and unit economics | WS-34 |
| D8-02 | Build versus buy versus extend for the orchestration layer | WS-34 |
| D8-03 | ROI model and benefit-realisation tracking | WS-34 |
| D8-04 | Business KPI framework and dashboard definition | WS-35 |
| D8-05 | AI quality KPIs | WS-35 |
| D8-06 | RAID register and ownership | WS-36 |
| D8-07 | Decision register and end-to-end traceability model | WS-36 |
| D8-08 | Platform extensibility — adding a new agent or workflow | WS-37 |
| D8-09 | Multi-county and multi-tenant extensibility strategy | WS-37 |
| D8-10 | Vendor lock-in, portability and exit strategy | WS-37 |

---

## Library status

All **136 ADRs are written** across the nine domains (Domain 0 governance + Domains 1–8).
Every ADR follows the CMMI-DAR template with a weighted decision matrix over (wherever the
option space admits) at least five genuine alternatives, a stated decision and rationale,
Golden-Rule/precedence conformance, quantitative targets and revisit triggers.

**Five decisions are open (`status: Proposed`)** — each with a full evaluation and a stated
recommendation awaiting the sign-off named in
[`_register/open-decisions.md`](_register/open-decisions.md): D3-23 (embedding model),
D3-24 (vector store), D5-10 (SLM serving stack), D5-12 (IaC tool), D5-13 (K8s manifest
tool). All other ADRs are `Accepted`.

The authoritative, fully-linked list of every ADR with its live status is in
[`_register/decision-register.md`](_register/decision-register.md); sheet/spec/phase/code
traceability is in [`_register/traceability-matrix.md`](_register/traceability-matrix.md).
