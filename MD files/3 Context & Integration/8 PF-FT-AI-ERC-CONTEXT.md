# PF-FT Enterprise Agentic AI Platform — ERC & Context Architecture

**Document ID:** PF-FT-AI-ERC-CONTEXT  
**Phase:** Phase 2 — Context & Enterprise Data Orchestration  
**Version:** 1.0.0  
**Status:** Development Baseline  
**Platform:** PF-FT Enterprise Agentic AI Platform / Adam AI  
**Runtime:** Python / FastAPI / LangGraph  
**Primary Scope:** ERC, ERC Construction, ERC Batching, Context Budget Management, Context Projection  

---

# 1. Purpose

This document defines the complete ERC and Context architecture for the PF-FT Enterprise Agentic AI Platform.

The ERC — Enterprise Runtime Context — is the structured, workflow-scoped representation of authoritative enterprise information required by the AI runtime to understand, reason about and execute a user interaction safely.

This document covers:

- ERC definition
- ERC lifecycle
- ERC ownership
- ERC schema
- ERC sections
- ERC source provenance
- ERC freshness
- ERC versioning
- ERC construction
- Enterprise API data ingestion
- Sequential data collection
- Parallel data collection
- Fan-out/fan-in
- Large collection handling
- 20-record batching
- 100+ teams
- 100+ officials
- Batch loops
- Partial failures
- Aggregation
- Normalization
- Validation
- Completeness
- Context budget
- Token budgeting
- Context prioritization
- Context compression
- Context projection
- SLM context preparation
- RAG context integration
- Memory context integration
- Context security
- Context observability
- Context evaluation
- ERC recovery
- ERC refresh
- Event-driven ERC updates

The objective is to create a reliable context boundary between enterprise systems and AI reasoning.

---

# 2. Core Principle

> **ERC is the structured context supplied to AI; it is not a replacement for the enterprise systems that own the underlying truth.**

The architecture must preserve this hierarchy:

```text
Enterprise Systems
       │
       ▼
Enterprise APIs / Events
       │
       ▼
Normalization
       │
       ▼
ERC
       │
       ├── Validation
       ├── Freshness
       ├── Provenance
       └── Version
       │
       ▼
Context Projection
       │
       ├── Conversation
       ├── Memory
       ├── RAG
       └── Current User Request
       │
       ▼
Agent Harness
       │
       ▼
SLM
```

---

# 3. What ERC Means in PF-FT

ERC is the **Enterprise Runtime Context** required by an AI workflow.

It is a structured snapshot/reference of the enterprise information needed for the current workflow execution.

Example:

```text
User
  │
  ▼
"Help me complete club affiliation."
  │
  ▼
Affiliation Agent
  │
  ▼
Determine Required Context
  │
  ▼
Enterprise APIs
  │
  ├── Club
  ├── Application
  ├── Teams
  ├── Officials
  ├── Courses
  └── Compliance
  │
  ▼
ERC
```

---

# 4. ERC Is Not the Enterprise Database

The enterprise database remains authoritative.

```text
Enterprise Database
        │
        ▼
Enterprise API
        │
        ▼
       ERC
        │
        ▼
       AI
```

AI must never assume that ERC is more authoritative than the current enterprise source.

---

# 5. ERC Is Not Conversation Memory

Conversation memory:

```text
"What did the user previously say?"
```

ERC:

```text
"What enterprise context is currently required for this workflow?"
```

They must remain separate.

---

# 6. ERC Is Not Cache

Cache exists primarily for performance.

ERC exists for structured workflow context.

A cached enterprise response may be used to construct an ERC section only when freshness policy permits it.

---

# 7. ERC Is Not RAG

RAG provides knowledge/context from approved knowledge sources.

ERC provides operational enterprise context.

```text
ERC
= Operational enterprise context

RAG
= Knowledge/context retrieval

Memory
= Historical interaction context
```

They may be combined in the final AI context but must retain separate source identity.

---

# 8. ERC Scope

ERC should be scoped to:

```text
User
+
Organization
+
Conversation
+
Workflow
+
Agent Run
```

Conceptually:

```yaml
erc_scope:
  subject_reference: user-123
  organization_reference: club-123
  conversation_id: conv-123
  workflow_instance_id: wf-123
  agent_run_id: run-123
```

---

# 9. ERC Lifecycle

```text
NOT_CREATED
     │
     ▼
REQUIREMENTS_IDENTIFIED
     │
     ▼
COLLECTING
     │
     ▼
NORMALIZING
     │
     ▼
AGGREGATING
     │
     ▼
VALIDATING
     │
     ▼
READY
     │
     ├──► REFRESH_REQUIRED
     │          │
     │          ▼
     │       REFRESHING
     │          │
     │          ▼
     │         READY
     │
     └──► INVALID / INCOMPLETE
```

---

# 10. ERC Status

Recommended statuses:

```text
NOT_CREATED
COLLECTING
PARTIAL
VALIDATING
READY
STALE
REFRESHING
INVALID
FAILED
```

---

# 11. ERC Identity

Each ERC requires:

```yaml
erc_id: erc-01J...
```

The ERC should also contain:

```yaml
version: 1
schema_version: 1.0.0
```

---

# 12. ERC Version

Every meaningful ERC update creates a new logical version.

Example:

```text
ERC v1
 ↓
Teams updated
 ↓
ERC v2
 ↓
Officials updated
 ↓
ERC v3
```

This supports traceability and reproducibility.

---

# 13. ERC Schema Version

The structure itself is versioned independently.

```yaml
schema_version: 1.0.0
```

Example:

```text
ERC instance version
= 17

ERC schema version
= 1.2.0
```

---

# 14. ERC Metadata

Recommended:

```yaml
erc:
  erc_id: erc-123
  version: 7
  schema_version: 1.0.0
  status: READY
  created_at: "..."
  updated_at: "..."
  workflow_instance_id: wf-123
  conversation_id: conv-123
  agent_id: affiliation_agent
  agent_version: 1.0.0
```

---

# 15. ERC Source Provenance

Every important data section should identify its source.

Example:

```yaml
source:
  system: enterprise-club-service
  api: get-club
  endpoint_ref: enterprise.club.get
  retrieved_at: "..."
  response_version: "..."
  authority: AUTHORITATIVE
```

---

# 16. Provenance Principle

The AI must be able to answer:

```text
Where did this information come from?
When was it retrieved?
Which enterprise API provided it?
Which ERC version contains it?
```

---

# 17. ERC Freshness

Every source section should have freshness information.

```yaml
freshness:
  retrieved_at: "..."
  expires_at: "..."
  ttl_seconds: 300
  status: FRESH
```

Possible statuses:

```text
FRESH
STALE
UNKNOWN
EXPIRED
```

---

# 18. Freshness Policy

Not every ERC section requires the same freshness.

Example:

```text
Club Profile
    → longer TTL

Application Status
    → short TTL

Eligibility
    → current verification

Transaction Status
    → authoritative current lookup
```

Exact TTL values are configuration/ADR decisions.

---

# 19. ERC Authority Levels

Recommended:

```text
AUTHORITATIVE
DERIVED
AI_INTERPRETED
RAG_CONTEXT
USER_PROVIDED
```

Enterprise API data should normally be marked:

```text
AUTHORITATIVE
```

AI-generated summaries must never be mislabeled as authoritative.

---

# 20. ERC High-Level Structure

Recommended:

```yaml
erc:
  metadata: {}
  identity: {}
  organization: {}
  club: {}
  affiliation: {}
  teams: {}
  officials: {}
  courses: {}
  compliance: {}
  documents: {}
  transactions: {}
  workflow: {}
  user_context: {}
  provenance: {}
  freshness: {}
  validation: {}
```

Not every workflow requires every section.

---

# 21. ERC Dynamic Sections

ERC should be capability-driven.

Example:

```text
Affiliation workflow
 → club
 → application
 → teams
 → officials
 → courses
 → compliance

Course workflow
 → course
 → participants
 → eligibility
 → schedule
```

Avoid constructing unnecessary data.

---

# 22. Context Requirement Identification

Before collecting data:

```text
User Request
      │
      ▼
Supervisor
      │
      ▼
Workflow Agent
      │
      ▼
Context Requirement Analysis
      │
      ▼
Required ERC Sections
```

The workflow should identify the minimum required context.

---

# 23. Context Requirement Model

Example:

```yaml
context_requirements:
  - section: club
    required: true

  - section: application
    required: true

  - section: teams
    required: true

  - section: officials
    required: true

  - section: courses
    required: false
```

---

# 24. Mandatory vs Optional Context

Each ERC section should define:

```yaml
required: true
```

or:

```yaml
required: false
```

If mandatory context cannot be obtained, the workflow should not silently continue as if it were complete.

---

# 25. Context Dependency Graph

Context collection may have dependencies.

Example:

```text
Club
 │
 ├── Application
 │
 ├── Teams
 │
 └── Officials
```

Some APIs may require:

```text
club_id
```

before they can be called.

---

# 26. Sequential Context Collection

Example:

```text
Get Club
   ↓
Get Application
   ↓
Get Application Details
```

Use sequential execution when one API depends on the previous result.

---

# 27. Parallel Context Collection

Example:

```text
Get Club
   │
   ▼
Context Identifiers
   │
   ├── Teams
   ├── Officials
   ├── Courses
   └── Compliance
```

Independent APIs should execute concurrently where safe.

---

# 28. Parallel Execution Rule

Parallel execution is permitted only when:

```text
No data dependency
+
No transaction conflict
+
Enterprise API permits concurrency
+
APIM limits permit concurrency
```

---

# 29. Context Collection Planner

The graph should construct a collection plan.

Example:

```yaml
collection_plan:
  sequential:
    - get_club
    - get_application

  parallel:
    - get_teams
    - get_officials
    - get_courses
```

The planner itself must be validated against the configured API dependency graph.

---

# 30. ERC Construction Pipeline

```text
Context Requirements
        │
        ▼
Collection Plan
        │
        ▼
Enterprise API Calls
        │
        ▼
Raw Responses
        │
        ▼
Schema Validation
        │
        ▼
Normalization
        │
        ▼
Batch Processing
        │
        ▼
Aggregation
        │
        ▼
Provenance
        │
        ▼
Freshness
        │
        ▼
ERC Validation
        │
        ▼
ERC READY
```

---

# 31. Raw Enterprise Response

The raw response should not be inserted directly into the SLM prompt.

Example:

```json
{
  "clubId": "123",
  "clubName": "Example FC",
  "statusCode": 1,
  "teams": [...]
}
```

It must first pass through normalization.

---

# 32. Normalization

Convert enterprise-specific payloads into platform context structures.

Example:

```json
{
  "club": {
    "id": "123",
    "name": "Example FC",
    "status": "ACTIVE"
  }
}
```

Normalization isolates AI from enterprise API-specific payload formats.

---

# 33. Response-to-Context Transformation

Every API integration should define:

```text
Enterprise Request
Enterprise Response
Context Mapping
```

Example:

```yaml
api: get-club

response_mapping:
  clubId: club.id
  clubName: club.name
  statusCode: club.status
```

---

# 34. Data Transformation Rule

Do not allow the SLM to decide how raw API payloads are transformed into ERC structure.

Transformation should be deterministic wherever possible.

---

# 35. ERC Collection for Large Data

PF-FT must support enterprise responses containing:

```text
100+ Teams
100+ Officials
100+ Courses
```

The runtime must not assume small collections.

---

# 36. Agreed Batch Size

Initial platform configuration:

```yaml
context_batching:
  batch_size: 20
```

This is the initial development baseline.

It should remain configurable.

---

# 37. Team Batching

Example:

```text
103 Teams

Batch 1 → 1-20
Batch 2 → 21-40
Batch 3 → 41-60
Batch 4 → 61-80
Batch 5 → 81-100
Batch 6 → 101-103
```

---

# 38. Official Batching

Example:

```text
127 Officials

Batch 1 → 1-20
Batch 2 → 21-40
Batch 3 → 41-60
Batch 4 → 61-80
Batch 5 → 81-100
Batch 6 → 101-120
Batch 7 → 121-127
```

---

# 39. Batch Processing Architecture

```text
Collection
   │
   ▼
Validate Collection
   │
   ▼
Split into Batches
   │
   ├── Batch 1
   ├── Batch 2
   ├── Batch 3
   ├── ...
   └── Batch N
   │
   ▼
Controlled Execution
   │
   ▼
Batch Results
   │
   ▼
Aggregation
```

---

# 40. Batch Processing Does Not Mean SLM Calls

Batching is primarily an application/runtime mechanism.

Example:

```text
103 Teams
 ↓
20-record batches
 ↓
Normalize
 ↓
Aggregate
 ↓
ERC
```

It does not mean:

```text
Call SLM for every 20 teams
```

unless the workflow explicitly requires AI analysis of each batch.

---

# 41. Batch AI Processing

If AI analysis is required per batch:

```text
Batch 1
 ↓
Agent/SLM
 ↓
Batch Result

Batch 2
 ↓
Agent/SLM
 ↓
Batch Result
```

Then:

```text
Batch Results
 ↓
Aggregate
 ↓
Final Reasoning
```

The number of SLM calls must be explicitly controlled.

---

# 42. Batch Execution Modes

Supported modes:

```text
SEQUENTIAL
BOUNDED_PARALLEL
PARALLEL
```

Recommended default:

```text
BOUNDED_PARALLEL
```

subject to enterprise API limits.

---

# 43. Bounded Parallelism

Example:

```yaml
context_batching:
  batch_size: 20
  max_parallel_batches: 5
```

This means 100 records can be processed as:

```text
5 batches × 20 records
```

without unlimited concurrency.

---

# 44. Batch State

Each batch should have:

```yaml
batch:
  batch_id: teams-003
  collection: teams
  index: 3
  start: 41
  end: 60
  status: COMPLETED
  attempt: 1
  record_count: 20
```

---

# 45. Batch Status

```text
PENDING
RUNNING
COMPLETED
PARTIAL
FAILED
RETRYING
SKIPPED
```

---

# 46. Batch Retry

Only failed batches should be retried where possible.

```text
Batch 1 → SUCCESS
Batch 2 → SUCCESS
Batch 3 → FAILURE
Batch 4 → SUCCESS

Retry Batch 3
```

Do not repeat successful batches unnecessarily.

---

# 47. Batch Retry Limits

Example:

```yaml
context_batching:
  retry:
    max_attempts: 2
```

Actual values are configuration-driven.

---

# 48. Partial Batch Failure

Example:

```text
Batch 1 → SUCCESS
Batch 2 → SUCCESS
Batch 3 → FAILED
Batch 4 → SUCCESS
```

The ERC must record:

```yaml
teams:
  status: PARTIAL
  total_expected: 80
  total_received: 60
  failed_batches:
    - 3
```

---

# 49. Mandatory Collection Failure

If the collection is mandatory:

```text
Failed batch
 ↓
ERC incomplete
 ↓
Workflow cannot claim complete context
```

Possible action:

```text
Retry
Wait
Ask
Fail safely
```

---

# 50. Optional Collection Failure

If optional:

```text
Optional collection fails
 ↓
ERC PARTIAL
 ↓
Continue
 ↓
Explicitly record missing data
```

The response must not imply that the optional data was successfully checked.

---

# 51. Completeness Tracking

ERC should track:

```yaml
completeness:
  required_sections: 6
  completed_sections: 5
  missing_sections:
    - officials
```

---

# 52. Record Completeness

For large collections:

```yaml
collection:
  expected_count: 127
  received_count: 127
  processed_count: 127
  failed_count: 0
```

---

# 53. Pagination

Pagination should be handled before batching.

```text
API
 ↓
Page 1
 ↓
Page 2
 ↓
Page 3
 ↓
Full Collection
 ↓
Batch into 20
```

Do not assume one API response contains all records.

---

# 54. Pagination Safety

Validate:

```text
page number
page size
total count
continuation token
duplicate records
missing pages
```

---

# 55. Duplicate Record Detection

During aggregation:

```text
Batch 1 → Team A
Batch 2 → Team A
```

The aggregator must detect duplicates based on the enterprise identifier.

---

# 56. Missing Record Detection

If the enterprise API reports:

```text
total = 100
```

but only:

```text
95
```

are received:

```text
ERC completeness = INCOMPLETE
```

unless the enterprise contract explicitly permits eventual consistency.

---

# 57. Aggregation

Aggregation should be deterministic.

```text
Batch Results
 ↓
Deduplicate
 ↓
Sort/Normalize
 ↓
Validate
 ↓
Merge
 ↓
ERC Section
```

---

# 58. Aggregation Ordering

Where deterministic ordering matters:

```text
enterprise_id
```

or a defined stable business field should be used.

This makes evaluation and regression testing reproducible.

---

# 59. ERC Section-Level Versioning

Each section may contain:

```yaml
section_version: 4
```

Example:

```text
ERC
 ├── club v2
 ├── teams v5
 ├── officials v3
 └── courses v1
```

This helps identify which part of context changed.

---

# 60. ERC Update Strategy

Avoid rebuilding the entire ERC when only one section changed.

Example:

```text
Officials changed
 ↓
Refresh Officials
 ↓
Update ERC officials section
 ↓
ERC version +1
```

---

# 61. ERC Patch Model

Conceptual:

```yaml
erc_patch:
  section: officials
  operation: REPLACE
  source: enterprise.officials
  version: 4
```

Possible operations:

```text
ADD
REPLACE
REMOVE
MERGE
INVALIDATE
```

---

# 62. ERC Invalidation

Invalidate a section when:

- Enterprise event indicates change
- TTL expires
- User performs a transaction
- Workflow requires fresh state
- API reports stale data
- Business policy requires current verification

---

# 63. ERC Refresh

```text
ERC Section
 ↓
STALE
 ↓
Refresh Required
 ↓
Enterprise API
 ↓
Normalize
 ↓
Validate
 ↓
Replace Section
 ↓
New ERC Version
```

---

# 64. Event-Driven ERC Refresh

```text
Service Bus Event
       │
       ▼
Event Consumer
       │
       ▼
Identify affected entity
       │
       ▼
Identify ERC section
       │
       ▼
Invalidate
       │
       ▼
Refresh
       │
       ▼
Resume Workflow
```

Detailed Service Bus architecture is defined in the Service Bus document.

---

# 65. ERC and Transaction State

Before transaction-sensitive actions:

```text
Current ERC
 ↓
Freshness Check
 ↓
If stale
 ↓
Refresh authoritative state
 ↓
Execute
```

This prevents decisions based on stale context.

---

# 66. Transaction Uncertainty

Example:

```text
Enterprise API call
 ↓
Timeout
 ↓
Unknown transaction state
```

Do not blindly modify ERC as:

```text
SUCCESS
```

Instead:

```yaml
transaction:
  status: UNKNOWN
  verification_required: true
```

---

# 67. ERC Validation

Validation occurs at multiple levels:

```text
Schema
 ↓
Required fields
 ↓
Business data consistency
 ↓
Source provenance
 ↓
Freshness
 ↓
Completeness
 ↓
Cross-section consistency
```

---

# 68. Schema Validation

Validate:

```text
Data types
Required fields
Enumerations
Nested structure
Identifiers
Dates
Status values
```

---

# 69. Cross-Section Validation

Example:

```text
Club ID
must match
Team.club_id
```

And:

```text
Official.club_id
must belong to
ERC.club.id
```

Cross-section validation prevents inconsistent context.

---

# 70. Referential Integrity

Example:

```text
team.club_id = club.id
official.club_id = club.id
application.club_id = club.id
```

Invalid references must be flagged.

---

# 71. ERC Validation Result

Example:

```yaml
validation:
  status: VALID
  errors: []
  warnings: []
  checked_at: "..."
```

Possible status:

```text
VALID
VALID_WITH_WARNINGS
INVALID
INCOMPLETE
STALE
```

---

# 72. ERC Warning

A warning does not necessarily block workflow execution.

Example:

```text
Optional course information unavailable.
```

The workflow can continue if policy permits.

---

# 73. ERC Error

An error means a required condition is not satisfied.

Example:

```text
Application ID missing.
```

The workflow should not pretend the ERC is complete.

---

# 74. Context Budget

The SLM has a finite context window.

The ERC may contain significantly more information than can be passed to the model.

Therefore:

```text
ERC
 ↓
Context Budget Manager
 ↓
Context Projection
 ↓
SLM
```

---

# 75. Context Budget Inputs

The budget manager considers:

```text
System prompt
Persona
Agent instructions
User query
Conversation
ERC
Memory
RAG
Tool results
Expected output
Model context window
Safety reserve
```

---

# 76. Token Budget Formula

Conceptually:

```text
Available Context
=
Model Context Window
-
System Tokens
-
Agent Tokens
-
Conversation Tokens
-
Reserved Output Tokens
-
Safety Margin
```

The exact implementation must account for tokenizer behavior.

---

# 77. Context Budget Configuration

Example:

```yaml
context_budget:
  max_input_tokens: 20000
  reserved_output_tokens: 4000
  safety_margin_tokens: 1000
```

These are initial configuration examples and must be aligned with the selected model.

---

# 78. Context Priority

Recommended order:

```text
1. System / security instructions
2. Current user request
3. Active workflow state
4. Required ERC sections
5. Authoritative enterprise data
6. Relevant tool results
7. Relevant RAG
8. Relevant memory
9. Recent conversation
10. Older conversation
```

---

# 79. Mandatory Context Protection

Mandatory context must not be removed simply to fit the model.

If mandatory context exceeds the model budget:

```text
Compress
 ↓
Summarize
 ↓
Batch
 ↓
Use additional deterministic processing
 ↓
Escalate / fail safely if still impossible
```

---

# 80. Context Compression

Compression options:

```text
Structured summarization
Field reduction
Aggregation
Deduplication
Relevant-record filtering
Hierarchical summarization
```

Do not compress away fields required for the business decision.

---

# 81. Structured Aggregation

Instead of passing:

```text
100 officials
```

the runtime may produce:

```yaml
official_summary:
  total: 127
  active: 118
  inactive: 9
  roles:
    coach: 30
    administrator: 20
    medical: 12
```

Only if the workflow requires the summary rather than individual records.

---

# 82. Record-Level Filtering

If the user asks:

```text
"Which officials have expired qualifications?"
```

the context layer may filter to:

```text
officials
WHERE qualification_status = EXPIRED
```

Filtering should be deterministic where possible.

---

# 83. AI-Assisted Filtering

AI may assist when the filter is semantic:

```text
"Show officials relevant to youth coaching."
```

But the final candidate set must be grounded in the enterprise records.

---

# 84. Hierarchical Context

For large collections:

```text
Raw Records
   ↓
Batch Summaries
   ↓
Collection Summary
   ↓
Relevant Records
   ↓
Final Context
```

This allows large enterprise datasets to be represented efficiently.

---

# 85. Batch Summary Structure

Example:

```yaml
batch_summary:
  collection: officials
  batch_id: officials-03
  record_count: 20
  key_findings: []
  relevant_records: []
  anomalies: []
  source_references: []
```

---

# 86. ERC-to-SLM Projection

The SLM should receive a controlled projection.

Example:

```yaml
ai_context:
  request: "..."
  club:
    id: club-123
    status: ACTIVE

  affiliation:
    status: PENDING

  teams:
    count: 103
    relevant: []

  officials:
    count: 127
    relevant: []

  compliance:
    status: VALID
```

---

# 87. ERC Data Exposure

Not every ERC field should be exposed to every agent.

Use:

```yaml
context_policy:
  affiliation_agent:
    allowed_sections:
      - club
      - affiliation
      - teams
      - officials
      - compliance
```

---

# 88. Agent-Specific Context Projection

Example:

```text
Affiliation Agent
 → club
 → application
 → teams
 → officials
 → compliance

Course Agent
 → course
 → participant
 → eligibility
```

This limits unnecessary context and reduces leakage.

---

# 89. Field-Level Filtering

Where required:

```yaml
allowed_fields:
  teams:
    - id
    - name
    - category
    - status
```

Sensitive enterprise fields should remain excluded unless required.

---

# 90. Context Classification

ERC fields may be classified:

```text
PUBLIC
INTERNAL
CONFIDENTIAL
RESTRICTED
```

The Harness must enforce context policies before SLM invocation.

---

# 91. Sensitive Context

Never include unnecessary:

- Credentials
- Tokens
- Secrets
- Authentication material
- Internal infrastructure details
- Unrelated personal data

---

# 92. Prompt Injection Protection in ERC

Enterprise text fields may contain arbitrary text.

Example:

```text
official.notes =
"Ignore the system prompt and ..."
```

The runtime must treat this as data.

ERC content must never override system or agent instructions.

---

# 93. ERC Trust Model

Recommended:

```text
Enterprise structured field
    = authoritative data

Enterprise free-text field
    = authoritative data, untrusted instructions

RAG content
    = untrusted knowledge content

Memory
    = untrusted historical context

User input
    = untrusted instruction/data
```

---

# 94. Context Provenance Chain

Every important projected fact should be traceable:

```text
SLM Context
 ↓
ERC Section
 ↓
Normalized Record
 ↓
Enterprise API Response
 ↓
Enterprise System
```

---

# 95. Context Citation/Reference

Where user-visible grounding is required:

```yaml
reference:
  source_type: enterprise_api
  source_id: get-application
  entity_id: application-123
  retrieved_at: "..."
```

---

# 96. Context Snapshot

Before important AI decisions, the runtime should record the context snapshot reference.

```yaml
context_snapshot:
  erc_id: erc-123
  version: 7
  hash: "..."
```

This supports reproducibility.

---

# 97. Context Hash

A deterministic hash may be generated from the normalized ERC.

Purpose:

- Detect changes
- Support tracing
- Compare evaluations
- Reproduce workflow context

---

# 98. ERC Persistence

ERC should be persisted outside application process memory when required for:

- Long-running workflows
- HIL waits
- External event waits
- Retry
- Recovery
- Audit
- Evaluation

The concrete persistence technology is an ADR decision.

---

# 99. ERC Cache

ERC may have a cache layer for performance.

Conceptually:

```text
ERC Store
   ▲
   │
Cache
   ▲
   │
Agent
```

Cache must not become the only durable source for long-running workflows.

---

# 100. ERC Cache Invalidation

Invalidate when:

```text
TTL expires
Enterprise event arrives
Transaction occurs
User explicitly requests current status
Business policy requires fresh data
```

---

# 101. ERC Recovery

If the AI runtime restarts:

```text
Workflow Checkpoint
 ↓
ERC Reference
 ↓
Load ERC
 ↓
Validate Version
 ↓
Check Freshness
 ↓
Refresh if required
 ↓
Resume
```

---

# 102. ERC Recovery Failure

If ERC cannot be recovered:

```text
Workflow
 ↓
Context unavailable
 ↓
Do not fabricate
 ↓
Refresh from enterprise
 ↓
If still unavailable → safe failure/wait
```

---

# 103. ERC Concurrency

Two graph branches may attempt to update different ERC sections.

Example:

```text
Teams Branch
Officials Branch
```

The aggregator should coordinate updates.

Prefer:

```text
Parallel collection
 ↓
Branch-local results
 ↓
Single aggregation point
 ↓
ERC update
```

This reduces conflicting writes.

---

# 104. ERC Locking

Avoid unnecessary global ERC locks.

Use:

```text
section-level versioning
+
optimistic concurrency
```

where appropriate.

---

# 105. ERC Idempotency

Repeated collection must not duplicate records.

Example:

```text
Retry Teams API
 ↓
Same Team IDs
 ↓
Deduplicate
 ↓
Stable ERC
```

---

# 106. ERC Determinism

Given the same authoritative enterprise inputs and configuration:

```text
Same input
 ↓
Same normalized ERC
```

as far as practical.

This is important for:

- Evaluation
- Debugging
- Regression testing
- Auditing

---

# 107. ERC Evaluation

ERC should be evaluated independently of the SLM.

Metrics:

```text
Completeness
Correctness
Freshness
Schema validity
Source validity
Referential integrity
Duplicate rate
Missing record rate
Batch success rate
```

---

# 108. ERC Golden Dataset

Maintain test cases containing:

```text
Enterprise API responses
Expected normalized ERC
Expected completeness
Expected validation
Expected batch results
```

---

# 109. ERC Regression

Changes to:

```text
API mapping
ERC schema
Normalization
Batch size
Aggregation
Context filtering
```

must trigger ERC regression tests.

---

# 110. ERC Observability

Metrics:

```text
ERC build duration
API calls
Records retrieved
Records processed
Batch count
Failed batches
Retry count
ERC size
Context tokens
Refresh count
Stale count
```

---

# 111. Batch Observability

Each batch should expose:

```text
batch_id
collection
record_count
duration
status
attempt
error
trace_id
```

---

# 112. Context Budget Observability

Track:

```text
ERC raw size
Projected context size
Input tokens
Reserved output tokens
Dropped fields
Compressed tokens
Summarized tokens
Model context utilization
```

---

# 113. Context Drop Audit

If data is removed from context:

```yaml
context_reduction:
  removed:
    - old_conversation
    - unrelated_courses
  reason:
    - token_budget
    - relevance
```

The runtime should know what was excluded and why.

---

# 114. Context Overflow Handling

If context exceeds the budget:

```text
Overflow
 ↓
Remove low-priority conversation
 ↓
Compress summaries
 ↓
Reduce RAG
 ↓
Filter irrelevant records
 ↓
Recalculate
```

Mandatory enterprise data should not be dropped without an explicit safe policy.

---

# 115. Context Overflow Final Failure

If still too large:

```text
Do not call SLM
 ↓
Alternative deterministic processing
or
Ask clarification
or
Split into sub-workflows
or
Fail safely
```

---

# 116. Context Sub-Workflows

For extremely large datasets:

```text
Main Workflow
 ├── Team Analysis Sub-workflow
 ├── Official Analysis Sub-workflow
 └── Compliance Analysis Sub-workflow
             │
             ▼
       Aggregated Result
             │
             ▼
          Final ERC
```

This should be used only when necessary.

---

# 117. ERC and Agent Harness

The Harness obtains:

```text
ERC Reference
 ↓
Context Policy
 ↓
Relevant Sections
 ↓
Field Filtering
 ↓
Context Budget
 ↓
AI Context
```

The Agent itself should not independently assemble unrestricted enterprise context.

---

# 118. ERC and LangGraph

The graph should maintain:

```text
erc_reference
```

rather than repeatedly copying the full ERC into state.

Nodes retrieve required sections through the ERC service/provider.

---

# 119. ERC Node Responsibilities

Recommended nodes:

```text
determine_context_requirements
plan_collection
collect_context
normalize_context
process_batches
aggregate_context
validate_erc
refresh_erc
project_context
```

---

# 120. Context Requirement Node

Output:

```json
{
  "required_sections": [
    "club",
    "application",
    "teams",
    "officials"
  ]
}
```

---

# 121. Collection Planner Node

Output:

```json
{
  "sequential": [
    "get_club",
    "get_application"
  ],
  "parallel": [
    "get_teams",
    "get_officials"
  ]
}
```

---

# 122. Collection Node

The collection node invokes approved enterprise tools.

It does not:

- invent endpoints
- invent request payloads
- bypass authorization
- interpret business rules

---

# 123. Normalization Node

Responsibilities:

```text
Validate response
 ↓
Map fields
 ↓
Normalize types
 ↓
Normalize status
 ↓
Attach provenance
```

---

# 124. Batch Node

Responsibilities:

```text
Detect large collection
 ↓
Split into 20
 ↓
Execute controlled batches
 ↓
Track state
 ↓
Retry failed batches
 ↓
Return batch results
```

---

# 125. Aggregation Node

Responsibilities:

```text
Collect batch results
 ↓
Deduplicate
 ↓
Check completeness
 ↓
Validate references
 ↓
Merge
 ↓
Create ERC section
```

---

# 126. Validation Node

Responsibilities:

```text
Schema
Completeness
Freshness
Provenance
Cross-section integrity
```

---

# 127. Context Projection Node

Responsibilities:

```text
Read agent context policy
 ↓
Select sections
 ↓
Filter fields
 ↓
Apply relevance
 ↓
Apply token budget
 ↓
Create SLM context
```

---

# 128. Context Projection Output

Example:

```yaml
projected_context:
  source_erc:
    id: erc-123
    version: 7

  sections:
    club: {}
    affiliation: {}
    teams:
      total: 103
      relevant: []
    officials:
      total: 127
      relevant: []

  omitted:
    - courses

  token_estimate: 14500
```

---

# 129. ERC Context Contract

The Agent Harness should receive:

```python
class ERCContext:
    erc_id: str
    version: int
    schema_version: str
    sections: dict
    provenance: dict
    freshness: dict
    completeness: dict
```

---

# 130. Context Contract

The final model input should be constructed from:

```python
class ModelContext:
    system_prompt: str
    agent_prompt: str
    user_request: str
    conversation_context: dict
    erc_context: ERCContext
    memory_context: dict
    rag_context: list
    tool_context: list
```

---

# 131. Context Assembly Rule

Never concatenate arbitrary objects into a prompt.

Use explicit serializers:

```text
Enterprise Data
 ↓
Typed Model
 ↓
Approved Serializer
 ↓
Prompt Context
```

---

# 132. Context Serialization

Recommended formats:

```text
JSON
Structured YAML
Compact key-value
```

The exact representation should be selected based on model behavior and token efficiency.

---

# 133. Context Token Estimation

Before SLM call:

```text
Serialize
 ↓
Tokenizer
 ↓
Token Estimate
 ↓
Budget Check
```

Use the actual configured model tokenizer where available.

---

# 134. Model Context Compatibility

Context preparation must know:

```text
model
context window
tokenizer
input limit
output limit
```

Do not assume every SLM has the same context window.

---

# 135. Model-Specific Projection

The same ERC may be projected differently for different models.

Example:

```text
Large model
 → richer context

Small model
 → tighter structured context
```

The underlying ERC remains unchanged.

---

# 136. Context and Cost Optimization

Optimization options:

```text
Use relevant sections only
Use structured summaries
Avoid duplicate data
Cache safe reads
Batch large collections
Use smaller model for simple tasks
Reserve large model for complex reasoning
```

---

# 137. Context and Latency Optimization

```text
Parallel APIs
Bounded batch concurrency
Caching
Incremental ERC updates
Selective RAG
Selective memory
Avoid unnecessary summarization
```

---

# 138. Context and Reliability

Reliability requires:

```text
Typed schema
Validation
Provenance
Freshness
Versioning
Checkpoint
Retry
Idempotency
Deterministic aggregation
```

---

# 139. Context Security

Controls:

```text
Tenant isolation
User isolation
Field-level filtering
Data classification
Prompt injection protection
Secret exclusion
Audit
Access control
```

---

# 140. ERC Security Rule

An ERC must never contain:

```text
Access tokens
API keys
Passwords
Secrets
Private keys
Unnecessary credentials
```

---

# 141. Context Logging Rule

Do not log the complete ERC by default.

Prefer:

```text
ERC ID
Version
Hash
Section names
Record counts
Classification
```

Sensitive fields must be masked.

---

# 142. Langfuse Data Policy

Langfuse should preferably receive:

```text
ERC ID
ERC version
Section metadata
Token counts
Evaluation references
```

rather than unrestricted raw enterprise data.

Actual observability policy is defined in the Observability/Security documents.

---

# 143. ERC Retention

Retention should support:

```text
Active workflow recovery
Audit
Evaluation
Troubleshooting
```

but must follow enterprise data retention policy.

---

# 144. ERC Deletion

When retention expires:

```text
ERC
 ↓
Delete/archive according to policy
```

Do not delete enterprise records.

---

# 145. ERC Disaster Recovery

Recovery should support:

```text
Workflow checkpoint
+
ERC reference
+
ERC version
```

If ERC is unavailable:

```text
Reconstruct from enterprise APIs
```

where policy permits.

---

# 146. ERC Reconstruction

A workflow may reconstruct ERC from:

```text
Workflow requirements
+
Enterprise APIs
+
Current event state
```

This is safer than relying solely on stale snapshots.

---

# 147. ERC and Eventual Consistency

Enterprise systems may not update simultaneously.

The ERC should record:

```yaml
freshness:
  section: teams
  retrieved_at: "..."

  section: officials
  retrieved_at: "..."
```

The AI should not assume all sections were retrieved at exactly the same time.

---

# 148. ERC Snapshot Consistency

Where the business workflow requires a consistent snapshot, the enterprise API layer must provide the appropriate consistency mechanism.

The AI platform must not manufacture transactional consistency across independent enterprise APIs.

---

# 149. ERC Source Conflict

If two enterprise APIs disagree:

```text
Source A → ACTIVE
Source B → INACTIVE
```

The AI must not guess.

The platform should:

```text
Detect conflict
 ↓
Apply configured source precedence
or
 ↓
Flag unresolved conflict
```

---

# 150. Source Precedence

Source precedence should be configuration-driven.

Example:

```yaml
source_precedence:
  club_status:
    - club-master-api
    - affiliation-api
```

This must align with enterprise ownership.

---

# 151. ERC Conflict State

Example:

```yaml
validation:
  status: VALID_WITH_WARNINGS
  conflicts:
    - field: club.status
      sources:
        - club-master-api
        - affiliation-api
```

---

# 152. ERC Schema Evolution

Schema changes must support:

```text
Backward compatibility
Migration
Version pinning
Regression testing
```

---

# 153. ERC Contract Testing

For each enterprise API:

```text
API response
 ↓
Mapping
 ↓
Normalized model
 ↓
Expected ERC section
```

Contract tests must fail when enterprise payload changes unexpectedly.

---

# 154. ERC API Mapping Registry

Maintain:

```yaml
api_mappings:
  - api_id: enterprise.club.get
    response_schema: v2
    erc_section: club
    mapping_version: 1.0.0
```

---

# 155. ERC Field Mapping Version

Mappings should be versioned independently:

```text
enterprise API version
mapping version
ERC schema version
```

This supports controlled evolution.

---

# 156. ERC Error Taxonomy

```text
SOURCE_UNAVAILABLE
SOURCE_TIMEOUT
INVALID_RESPONSE
SCHEMA_MISMATCH
MAPPING_ERROR
MISSING_REQUIRED_DATA
DUPLICATE_RECORD
CONFLICTING_DATA
STALE_DATA
BATCH_FAILURE
AGGREGATION_FAILURE
VALIDATION_FAILURE
CONTEXT_OVERFLOW
```

---

# 157. Error Handling Strategy

```text
Error
 ↓
Classify
 ↓
Is retryable?
 ├── YES → Retry
 └── NO
      ↓
Is mandatory?
 ├── YES → Block / Wait / Fail
 └── NO → Continue with warning
```

---

# 158. ERC Performance Metrics

Track:

```text
ERC build latency
Section build latency
API call count
API parallelism
Batch count
Batch latency
Records/sec
Aggregation latency
Validation latency
Projection latency
Token preparation latency
```

---

# 159. ERC Cost Metrics

Track:

```text
API calls
SLM calls caused by context processing
RAG calls
Embedding/retrieval calls where applicable
Token volume
Cache hit ratio
```

---

# 160. ERC Quality Metrics

Track:

```text
Completeness %
Freshness %
Validation success %
Duplicate rate
Conflict rate
Missing field rate
Batch failure %
Context grounding %
```

---

# 161. ERC Acceptance Criteria

The implementation must satisfy:

1. ERC is clearly separated from enterprise databases.
2. ERC is clearly separated from memory.
3. ERC is clearly separated from cache.
4. ERC is clearly separated from RAG.
5. ERC is workflow scoped.
6. ERC has unique identity.
7. ERC has instance versioning.
8. ERC has schema versioning.
9. ERC has source provenance.
10. ERC has freshness metadata.
11. ERC has completeness metadata.
12. ERC supports dynamic sections.
13. Required context is identified before collection.
14. Sequential API collection is supported.
15. Parallel API collection is supported.
16. Fan-out/fan-in is supported.
17. Pagination is supported.
18. 20-record batching is supported.
19. 100+ teams are supported.
20. 100+ officials are supported.
21. Batches can execute with bounded concurrency.
22. Failed batches can be retried independently.
23. Partial failures are represented.
24. Duplicate records are detected.
25. Missing records are detected.
26. Aggregation is deterministic.
27. Cross-section references are validated.
28. ERC sections can be refreshed independently.
29. ERC sections can be invalidated.
30. Event-driven refresh is supported.
31. Context budget is enforced before SLM calls.
32. Context prioritization is deterministic.
33. Context compression is supported.
34. Large collections can be summarized/filtered.
35. Agent-specific context projection is supported.
36. Field-level filtering is supported.
37. Sensitive data is excluded.
38. Prompt injection protection applies to ERC text.
39. ERC snapshots are traceable.
40. ERC reconstruction is supported.
41. Context overflow is handled safely.
42. ERC evaluation is independent of SLM evaluation.
43. ERC regression testing is supported.
44. ERC observability is implemented.
45. ERC version/configuration is reproducible.
46. Enterprise systems remain authoritative.
47. AI never fabricates missing enterprise context.
48. Transaction-sensitive decisions verify freshness.
49. ERC state can survive pod/workflow restart.
50. The complete context chain is auditable.

---

# 162. Recommended Python Package Boundary

```text
src/
└── pf_ft_ai/
    ├── context/
    │   ├── erc/
    │   │   ├── models.py
    │   │   ├── schema.py
    │   │   ├── lifecycle.py
    │   │   ├── service.py
    │   │   ├── repository.py
    │   │   ├── versioning.py
    │   │   └── provenance.py
    │   │
    │   ├── collection/
    │   │   ├── planner.py
    │   │   ├── executor.py
    │   │   ├── pagination.py
    │   │   ├── batching.py
    │   │   ├── aggregator.py
    │   │   └── concurrency.py
    │   │
    │   ├── normalization/
    │   │   ├── mapper.py
    │   │   ├── validators.py
    │   │   └── mappings.py
    │   │
    │   └── projection/
    │       ├── projector.py
    │       ├── policy.py
    │       ├── budget.py
    │       ├── serializer.py
    │       └── tokenizer.py
    │
    └── tests/
        ├── unit/
        │   ├── erc/
        │   ├── collection/
        │   ├── batching/
        │   ├── normalization/
        │   └── projection/
        │
        ├── integration/
        │   └── context/
        │
        └── evaluation/
            └── erc/
```

This is the logical package boundary. The final repository structure will consolidate these packages with the complete PF-FT platform structure.

---

# 163. Configuration

Recommended:

```text
config/
├── base/
│   ├── erc.yaml
│   ├── context-budget.yaml
│   ├── batching.yaml
│   └── source-precedence.yaml
│
├── dev/
├── test/
├── staging/
└── prod/
```

---

# 164. ERC Configuration Example

```yaml
erc:
  schema_version: 1.0.0

  batching:
    default_batch_size: 20
    max_parallel_batches: 5
    max_retry_attempts: 2

  freshness:
    default_ttl_seconds: 300

  validation:
    enforce_schema: true
    enforce_completeness: true
    enforce_referential_integrity: true
```

---

# 165. Context Budget Configuration Example

```yaml
context_budget:
  default:
    max_input_tokens: 20000
    reserved_output_tokens: 4000
    safety_margin_tokens: 1000

  policies:
    affiliation_agent:
      max_erc_tokens: 12000
      max_rag_tokens: 3000
      max_memory_tokens: 1500
```

Values are examples and will be finalized against the selected SLM/model profiles.

---

# 166. Batch Configuration Example

```yaml
batching:
  teams:
    batch_size: 20
    max_parallel_batches: 5

  officials:
    batch_size: 20
    max_parallel_batches: 5

  default:
    batch_size: 20
    max_parallel_batches: 5
```

---

# 167. Development Workflow

Implementation sequence:

```text
1. Define ERC schema
2. Define section models
3. Define source mappings
4. Implement normalization
5. Implement collection planner
6. Implement sequential collection
7. Implement parallel collection
8. Implement pagination
9. Implement batching
10. Implement batch retry
11. Implement aggregation
12. Implement ERC validation
13. Implement provenance
14. Implement freshness
15. Implement ERC persistence
16. Implement ERC refresh
17. Implement context projection
18. Implement token budgeting
19. Implement model-specific serialization
20. Integrate Harness
21. Integrate LangGraph
22. Add observability
23. Add evaluation
24. Add security tests
25. Performance test
```

---

# 168. Unit Test Coverage

Minimum test categories:

## ERC

- Creation
- Versioning
- Schema validation
- Status transitions
- Provenance
- Freshness
- Section updates
- Invalidation

## Collection

- Sequential dependencies
- Parallel calls
- Pagination
- Empty results
- Large results
- API failures

## Batching

- Exact 20
- Less than 20
- More than 20
- 100+
- Partial final batch
- Failed batch
- Retry
- Duplicate records
- Missing records

## Aggregation

- Merge
- Deduplication
- Ordering
- Completeness
- Referential integrity
- Conflict detection

## Context Budget

- Under budget
- At budget
- Over budget
- Compression
- Filtering
- Mandatory context
- Overflow failure

## Projection

- Agent policy
- Section filtering
- Field filtering
- Sensitive fields
- RAG integration
- Memory integration

---

# 169. Integration Tests

Test:

```text
Enterprise API
 ↓
Normalization
 ↓
Batching
 ↓
Aggregation
 ↓
ERC
 ↓
Projection
 ↓
Agent Harness
 ↓
SLM
```

Scenarios:

- 10 teams
- 100 teams
- 103 teams
- 127 officials
- API timeout
- partial batch failure
- stale ERC
- event refresh
- context overflow
- pod restart

---

# 170. Evaluation Tests

Evaluate:

```text
ERC completeness
ERC correctness
ERC freshness
ERC grounding
Context relevance
Context compression
Context token efficiency
```

The ERC should be evaluated before measuring final SLM response quality.

---

# 171. Security Tests

Test:

- Cross-user ERC access
- Cross-tenant ERC access
- Sensitive field exposure
- Secret leakage
- Prompt injection in enterprise text
- Malicious free-text fields
- Unauthorized section access
- Unauthorized refresh
- Unauthorized context projection

---

# 172. Performance Tests

Test:

```text
20 records
100 records
500 records
1000 records
```

Measure:

```text
Collection time
Batch throughput
Aggregation time
ERC generation time
Projection time
Token generation
Memory consumption
```

---

# 173. Failure Injection Tests

Inject:

```text
API timeout
429
500
503
Malformed JSON
Missing fields
Duplicate records
Missing records
Conflicting data
Service Bus refresh
State store unavailable
```

Verify safe recovery.

---

# 174. Final Runtime Flow

```text
USER REQUEST
     │
     ▼
SUPERVISOR
     │
     ▼
WORKFLOW AGENT
     │
     ▼
CONTEXT REQUIREMENTS
     │
     ▼
COLLECTION PLAN
     │
     ├───────────────┐
     ▼               ▼
SEQUENTIAL       PARALLEL
API CALLS        API CALLS
     │               │
     └───────┬───────┘
             ▼
        PAGINATION
             │
             ▼
       BATCHING × 20
             │
             ▼
      BOUNDED PARALLEL
             │
             ▼
         NORMALIZE
             │
             ▼
         AGGREGATE
             │
             ▼
       ERC VALIDATION
             │
             ▼
             ERC
             │
             ▼
     FRESHNESS CHECK
             │
             ▼
      CONTEXT BUDGET
             │
             ▼
    CONTEXT PROJECTION
             │
       ┌─────┼─────┐
       ▼     ▼     ▼
    MEMORY  RAG  ERC
       │     │     │
       └─────┼─────┘
             ▼
        AGENT HARNESS
             │
             ▼
             SLM
             │
             ▼
        OUTPUT / NEXT ACTION
```

---

# 175. Golden Architecture Rule

The PF-FT AI platform must follow:

```text
Enterprise Systems
       ↓
Authoritative APIs / Events
       ↓
ERC Construction
       ↓
ERC Validation
       ↓
Context Projection
       ↓
Agent Harness
       ↓
SLM
```

The SLM must never be used as the source of enterprise truth.

---

# 176. Final Design Principles

1. **Enterprise APIs remain authoritative.**
2. **ERC is a structured runtime context, not a database replacement.**
3. **ERC is separate from conversation memory.**
4. **ERC is separate from cache.**
5. **ERC is separate from RAG.**
6. **Only required context should be collected.**
7. **Independent APIs should execute in parallel where safe.**
8. **Dependent APIs must execute sequentially.**
9. **Large collections must be paginated and batched.**
10. **The agreed initial batch size is 20.**
11. **100+ teams and officials must be supported.**
12. **Batch processing must use bounded concurrency.**
13. **Failed batches must be independently retryable.**
14. **Aggregation must be deterministic.**
15. **ERC completeness must be measurable.**
16. **ERC freshness must be explicit.**
17. **Every important value must have provenance.**
18. **ERC versions must be traceable.**
19. **Context projection must be agent-specific.**
20. **Sensitive fields must be filtered.**
21. **Prompt injection can exist inside enterprise text and must be treated as untrusted content.**
22. **Context budget must be enforced before SLM invocation.**
23. **Mandatory context must not be silently dropped.**
24. **Context compression must preserve decision-critical information.**
25. **Transaction-sensitive operations require fresh authoritative state.**
26. **ERC must survive long-running workflow boundaries.**
27. **ERC can be reconstructed from authoritative enterprise sources when required.**
28. **ERC quality must be evaluated independently.**
29. **Context preparation must be observable and auditable.**
30. **AI reasoning consumes ERC; it does not redefine enterprise truth.**
