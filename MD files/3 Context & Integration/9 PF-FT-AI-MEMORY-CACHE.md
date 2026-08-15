# PF-FT Enterprise Agentic AI Platform — Memory & Cache Architecture

**Document ID:** PF-FT-AI-MEMORY-CACHE  
**Phase:** Phase 2 — Context, State & Continuity  
**Version:** 1.0.0  
**Status:** Development Baseline  
**Platform:** PF-FT Enterprise Agentic AI Platform / Adam AI  
**Runtime:** Python / FastAPI / LangGraph  
**Primary Scope:** Conversation Memory, Workflow Memory, User Memory, ERC Memory, Session State, Cache, Cache Invalidation, TTL, Recovery, Security, Observability and Evaluation

---

# 1. Purpose

This document defines the complete Memory and Cache architecture for the PF-FT Enterprise Agentic AI Platform.

The platform must support multiple forms of state and continuity without mixing their responsibilities.

The architecture covers:

- Chat/session state
- Conversation history
- Short-term memory
- Long-term memory
- Workflow memory
- Agent execution memory
- ERC-related memory/reference
- Working context
- Cache
- API response cache
- RAG retrieval cache
- Prompt/model configuration cache
- Session cache
- State/checkpoint persistence
- Cache invalidation
- TTL
- Versioning
- Consistency
- Recovery
- Security isolation
- Tenant/user/workflow isolation
- Memory retrieval
- Memory write policy
- Memory summarization
- Memory compaction
- Context projection
- Memory evaluation
- Observability
- Cost and performance optimization
- Failure handling
- Data retention
- Privacy and deletion

The primary objective is to provide continuity to the AI platform while preventing memory from becoming an uncontrolled source of truth.

---

# 2. Core Principle

> **Memory provides continuity; cache provides performance; ERC provides workflow context; enterprise systems provide authoritative truth.**

The architecture must preserve the following distinction:

```text
Enterprise Systems
       │
       ▼
Authoritative Data
       │
       ▼
ERC
       │
       ├──────────────┐
       │              │
       ▼              ▼
    Memory          Cache
       │              │
       └──────┬───────┘
              ▼
        Context Builder
              │
              ▼
          Agent Harness
              │
              ▼
             SLM
```

---

# 3. Memory vs Cache vs ERC

These are three different concepts.

| Component | Primary Purpose | Authority |
|---|---|---|
| ERC | Current workflow enterprise context | Derived from authoritative enterprise systems |
| Memory | Historical/continuity context | Not authoritative |
| Cache | Performance optimization | Never authoritative |
| Enterprise API | Current business state | Authoritative |

---

# 4. Golden Rule

The AI platform must never treat:

```text
Memory
Cache
RAG
SLM output
```

as a replacement for current authoritative enterprise state.

For transaction-sensitive or current-status decisions:

```text
Memory/Cache
     ↓
may provide hints
     ↓
Enterprise API
     ↓
authoritative verification
```

---

# 5. Memory Categories

The platform should distinguish the following memory categories:

```text
1. Conversation Memory
2. Session Memory
3. Working Memory
4. Workflow Memory
5. Agent Run Memory
6. User Preference Memory
7. Organizational Context Memory
8. ERC Reference Memory
9. Decision Memory
10. Summary Memory
```

Not every category needs to persist permanently.

---

# 6. Conversation Memory

Conversation memory represents the current user conversation.

Example:

```text
User:
"Show my club affiliation."

Assistant:
"Which club?"

User:
"Example FC."
```

The second turn requires the first turn as context.

---

# 7. Conversation Memory Scope

Conversation memory is scoped to:

```text
conversation_id
```

and associated with:

```text
user_id
organization_id
session_id
```

---

# 8. Session Memory

Session memory represents the current interaction/session.

It may contain:

```yaml
session:
  session_id: session-123
  user_id: user-123
  conversation_id: conv-123
  active_workflow: affiliation
  active_agent: affiliation_agent
  current_state: collecting_context
```

---

# 9. Session vs Conversation

```text
Session
 = runtime interaction lifecycle

Conversation
 = logical conversation/history
```

A session may contain one or more conversations depending on the application design.

The exact relationship must remain explicit in the runtime model.

---

# 10. Working Memory

Working memory contains temporary information required during an active agent execution.

Example:

```text
Current intent
Current entities
Current tool results
Current reasoning inputs
Current graph state references
Current temporary context
```

Working memory is generally short-lived.

---

# 11. Workflow Memory

Workflow memory stores information required to continue a workflow.

Example:

```yaml
workflow_memory:
  workflow_instance_id: wf-123
  workflow: affiliation
  current_state: WAITING_FOR_HIL
  last_completed_step: validate_erc
  pending_action: human_review
```

This is critical for long-running workflows.

---

# 12. Workflow Memory Is Not Business Truth

Workflow memory says:

```text
"The workflow was waiting for HIL."
```

It does not say:

```text
"The enterprise system has approved the affiliation."
```

The second must come from the enterprise system.

---

# 13. Agent Run Memory

Each agent run may have temporary execution information:

```yaml
agent_run:
  run_id: run-123
  agent_id: affiliation_agent
  graph_version: 1.0.0
  started_at: "..."
  status: RUNNING
```

It supports:

- Debugging
- Recovery
- Observability
- Evaluation
- Audit

---

# 14. User Preference Memory

Only approved, useful preferences should be persisted.

Examples:

```text
Preferred response language
Preferred presentation style
User-selected display preferences
```

Do not automatically persist arbitrary user statements as permanent preferences.

---

# 15. Organizational Context Memory

Where appropriate, the platform may maintain reusable organizational context.

Example:

```text
Club preferred terminology
Known organizational identifiers
Previously selected business context
```

This must respect authorization and tenancy boundaries.

---

# 16. ERC Reference Memory

Do not duplicate the complete ERC into long-term memory.

Store references such as:

```yaml
erc_reference:
  erc_id: erc-123
  version: 7
  workflow_instance_id: wf-123
```

The current ERC can then be retrieved when required.

---

# 17. Why ERC Should Not Be Copied to Memory

If the entire ERC is copied into memory:

```text
Enterprise data
 ↓
ERC
 ↓
Memory
 ↓
Stale duplicate
```

This creates:

- Staleness
- Duplication
- Security exposure
- Larger storage
- Conflicting versions

Prefer storing:

```text
ERC reference
+
important workflow facts
```

rather than a full uncontrolled copy.

---

# 18. Decision Memory

The platform may preserve important decisions made during a workflow.

Example:

```yaml
decision:
  workflow: affiliation
  decision_type: context_selection
  selected: officials
  reason: required_for_compliance
  source: workflow_policy
```

AI-generated reasoning should not automatically become authoritative business decisions.

---

# 19. Summary Memory

Long conversations may be summarized.

Example:

```text
100 chat messages
       ↓
Conversation summarizer
       ↓
Conversation Summary
       ↓
Memory
```

The summary must retain information required to continue the workflow.

---

# 20. Memory Lifecycle

```text
CREATED
   │
   ▼
ACTIVE
   │
   ▼
UPDATED
   │
   ├──► COMPACTED
   │
   ├──► EXPIRED
   │
   └──► DELETED
```

Workflow memory may instead follow:

```text
CREATED
 ↓
ACTIVE
 ↓
WAITING
 ↓
RESUMED
 ↓
COMPLETED
 ↓
RETAINED / ARCHIVED / DELETED
```

---

# 21. Memory Storage Model

Recommended logical separation:

```text
Memory Service
    │
    ├── Conversation Store
    ├── Workflow Store
    ├── User Memory Store
    ├── Summary Store
    └── Reference Store
```

The physical technology is an architecture/ADR decision.

---

# 22. Memory Provider Abstraction

Agents should not directly access the database.

Use an abstraction:

```python
class MemoryProvider:

    async def retrieve(...):
        ...

    async def store(...):
        ...

    async def update(...):
        ...

    async def delete(...):
        ...

    async def summarize(...):
        ...
```

---

# 23. Memory Retrieval

Memory retrieval should be intentional.

```text
Current Request
      │
      ▼
Memory Requirement
      │
      ▼
Memory Retrieval
      │
      ▼
Relevance Filtering
      │
      ▼
Security Filtering
      │
      ▼
Context Projection
```

Do not inject all historical memory into every prompt.

---

# 24. Memory Retrieval Policy

Each workflow should define:

```yaml
memory_policy:
  enabled: true
  scopes:
    - conversation
    - workflow
  max_items: 20
  relevance_threshold: configured
```

---

# 25. Memory Relevance

Memory should be selected based on:

```text
Current workflow
Current user request
Current organization
Current conversation
Memory type
Recency
Relevance
Security classification
```

---

# 26. Memory Recency

Recent memory generally receives higher priority.

Example:

```text
Today
 ↓
Last interaction
 ↓
Older interaction
 ↓
Archived
```

But relevance must remain more important than recency alone.

---

# 27. Memory Ranking

Potential ranking signals:

```text
Semantic relevance
Workflow relevance
Recency
Explicit user reference
Entity match
Organization match
Memory confidence
```

---

# 28. Memory Confidence

Memory entries may contain:

```yaml
confidence:
  source: USER_EXPLICIT
  confidence: HIGH
```

Possible source classes:

```text
USER_EXPLICIT
ENTERPRISE_DERIVED
WORKFLOW_DERIVED
AI_SUMMARY
AI_INFERENCE
```

AI inference should receive the lowest trust for factual reuse.

---

# 29. Memory Trust

Recommended:

```text
Enterprise-derived fact
      ↓
High trust, but still verify current state

User explicit statement
      ↓
Useful historical context

AI-generated summary
      ↓
Use cautiously

AI inference
      ↓
Never treat as authoritative
```

---

# 30. Memory Write Policy

Not every conversation statement should become memory.

Before writing:

```text
Candidate memory
 ↓
Memory policy
 ↓
Is it useful?
 ↓
Is it safe?
 ↓
Is it persistent?
 ↓
Is it within scope?
 ↓
Store
```

---

# 31. Explicit vs Implicit Memory

Explicit:

```text
User:
"Always show my club information first."
```

Potentially suitable for preference memory.

Implicit:

```text
User repeatedly asks for club information first.
```

Do not automatically persist this as a permanent preference without a configured policy.

---

# 32. Memory Categories and Retention

Example:

| Memory | Suggested Lifecycle |
|---|---|
| Working memory | Minutes/hours |
| Session state | Session lifecycle |
| Conversation | Configured retention |
| Workflow state | Until workflow completion + policy retention |
| ERC reference | Workflow lifecycle |
| User preference | Long-lived if explicitly allowed |
| Summary | Conversation lifecycle |
| Cache | TTL based |

Actual retention must follow enterprise policy.

---

# 33. Cache Categories

Cache should be separated by purpose.

```text
1. Enterprise API Response Cache
2. Reference Data Cache
3. Configuration Cache
4. Prompt Cache
5. Model Metadata Cache
6. RAG Retrieval Cache
7. Embedding Cache
8. Session Cache
9. Context Projection Cache
10. Portal Link Cache
```

Only applicable caches should be implemented.

---

# 34. Enterprise API Response Cache

Safe read-only enterprise responses may be cached.

Example:

```text
GET club profile
 ↓
Cache
 ↓
Reuse within TTL
```

---

# 35. Transaction Cache Rule

Do not blindly cache:

```text
POST
PUT
PATCH
DELETE
```

or transaction-sensitive current status.

For these operations:

```text
Enterprise system remains authoritative.
```

---

# 36. Cache Key Design

Cache keys must include all relevant dimensions.

Example:

```text
enterprise:
club:get:
organization=club-123:
api-version=v2:
parameters-hash=abc
```

---

# 37. Cache Key Isolation

Never use:

```text
club:123
```

if the same logical identifier could exist across tenants/environments.

Prefer:

```text
tenant
+
organization
+
resource
+
operation
+
parameters
+
version
```

---

# 38. Cache TTL

Every cache entry should have a TTL.

Example:

```yaml
cache:
  club_profile:
    ttl_seconds: 300

  reference_data:
    ttl_seconds: 3600
```

TTL values are configuration-driven.

---

# 39. TTL Must Reflect Data Volatility

Example:

```text
Static reference data
 → longer TTL

Club profile
 → moderate TTL

Application status
 → short TTL

Transaction status
 → current authoritative lookup
```

---

# 40. Cache Freshness

Cache lookup:

```text
Cache HIT
 ↓
Check TTL
 ↓
Fresh?
 ├── YES → Use
 └── NO → Refresh
```

A cache hit does not automatically mean the data is valid for a business decision.

---

# 41. Cache-aside Pattern

Recommended initial pattern:

```text
Application
 ↓
Cache GET
 ├── HIT → Return
 └── MISS
      ↓
   Enterprise API
      ↓
    Cache SET
      ↓
    Return
```

---

# 42. Write-through / Write-behind

Do not introduce write-behind for authoritative enterprise transactions unless explicitly approved.

The AI platform should not create an alternative source of transactional truth.

---

# 43. Cache Invalidation

Invalidate cache when:

```text
TTL expires
Enterprise event received
Known mutation occurs
Workflow requires fresh data
Manual administrative invalidation
```

---

# 44. Event-Driven Cache Invalidation

Example:

```text
Enterprise Update
      ↓
Service Bus
      ↓
AI Event Consumer
      ↓
Identify Cache Keys
      ↓
Invalidate
      ↓
Next Read → Enterprise API
```

---

# 45. Cache Stampede Protection

If a popular key expires:

```text
100 requests
 ↓
same cache miss
```

Do not send 100 enterprise API calls.

Use:

```text
Request coalescing
Distributed lock
Single-flight
Jittered refresh
```

---

# 46. Cache Penetration Protection

Repeated invalid/nonexistent queries can overload enterprise APIs.

Use controlled negative caching where safe:

```text
Resource Not Found
 ↓
Short negative TTL
```

Do not cache business errors indefinitely.

---

# 47. Cache Poisoning Protection

Only validated responses may be cached.

```text
Enterprise Response
 ↓
Schema Validation
 ↓
Authorization Boundary
 ↓
Cache
```

Never cache arbitrary user-generated content as authoritative enterprise data.

---

# 48. RAG Retrieval Cache

RAG retrieval results may be cached using:

```text
query hash
index version
embedding model version
filter hash
tenant
```

Example:

```text
RAG:
tenant=club-123
index=v5
embedding=v2
query_hash=abc
```

---

# 49. RAG Cache Invalidation

Invalidate when:

```text
Index version changes
Embedding version changes
Document corpus changes
Security ACL changes
Tenant context changes
```

---

# 50. Embedding Cache

Embedding results may be cached.

Key:

```text
model_version
+
input_hash
```

If the embedding model changes:

```text
Embedding v1
 ≠
Embedding v2
```

Do not mix incompatible cached vectors.

---

# 51. Prompt Cache

Prompt/configuration caching may improve performance.

Cache key should include:

```text
prompt_id
prompt_version
environment
```

---

# 52. Prompt Cache Security

Never allow:

```text
user input
```

to overwrite prompt cache.

Prompt configuration is controlled platform configuration.

---

# 53. Model Metadata Cache

May cache:

```text
model capabilities
context window
tokenizer information
provider metadata
```

Version changes must invalidate the cache.

---

# 54. Session Cache

Session cache may hold:

```text
session ID
current conversation
active workflow
agent reference
temporary UI state
```

Do not use session cache as the only durable workflow state for long-running workflows.

---

# 55. Session Recovery

If the runtime pod restarts:

```text
Request
 ↓
Session ID
 ↓
Session Store
 ↓
Recover
```

For active long-running workflows:

```text
Checkpoint Store
```

must remain authoritative for runtime state.

---

# 56. Working Context Cache

Temporary derived context may be cached:

```text
Context projection
Batch summary
Normalized reference data
```

Use short TTLs and workflow scoping.

---

# 57. Cache vs Memory Matrix

| Requirement | Memory | Cache |
|---|---:|---:|
| Conversation continuity | Yes | Optional |
| User preference | Yes | No |
| Workflow resume | Yes | No |
| API performance | No | Yes |
| RAG retrieval acceleration | No | Yes |
| Temporary derived data | Possible | Yes |
| Authoritative truth | No | No |
| Long-term context | Yes | No |
| Short-lived performance | No | Yes |

---

# 58. Cache vs ERC Matrix

| Requirement | ERC | Cache |
|---|---:|---:|
| Current workflow context | Yes | No |
| Enterprise source mapping | Yes | No |
| Provenance | Yes | Optional |
| Freshness | Yes | Yes |
| Performance optimization | No | Yes |
| Durable workflow reference | Yes | No |
| Current transaction state | Verified | No |
| SLM projection | Yes | Optional |

---

# 59. Memory vs ERC Matrix

| Requirement | ERC | Memory |
|---|---:|---:|
| Current enterprise context | Yes | No |
| Conversation history | No | Yes |
| Workflow state | Reference | Yes |
| Enterprise source provenance | Yes | Optional |
| User preferences | No | Yes |
| Current status | Yes | No |
| Historical context | No | Yes |
| Authoritative business state | Derived | No |

---

# 60. Memory + ERC + Cache Runtime

```text
                 USER
                  │
                  ▼
            Conversation
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
      Memory     ERC       Cache
        │         │         │
        └─────────┼─────────┘
                  ▼
          Context Projection
                  │
                  ▼
             Agent Harness
                  │
                  ▼
                 SLM
```

---

# 61. Context Assembly

The context builder should selectively combine:

```text
Current User Request
+
Conversation Memory
+
Relevant Workflow Memory
+
Current ERC
+
Relevant RAG
+
Validated Tool Results
```

Cache is normally an intermediate optimization and should not be blindly added as a separate prompt section.

---

# 62. Memory Selection Policy

Example:

```yaml
memory_policy:
  conversation:
    enabled: true
    max_items: 20

  workflow:
    enabled: true
    max_items: 20

  user_preference:
    enabled: true
    max_items: 10

  organizational:
    enabled: false
```

---

# 63. Context Budget for Memory

Memory receives a dedicated budget.

Example:

```yaml
context_budget:
  memory:
    max_tokens: 1500
```

Memory must not consume the entire context window.

---

# 64. Memory Compression

Long conversations should be compacted.

```text
Conversation
 ↓
Recent Messages
 +
Summary
 ↓
Context
```

Keep recent turns verbatim where required and older turns summarized.

---

# 65. Memory Summary Versioning

Example:

```yaml
summary:
  conversation_id: conv-123
  version: 4
  generated_by: memory_summarizer
  model: configured-model
```

When the summarization strategy/model changes, regression tests should be performed.

---

# 66. Summary Integrity

A summary must not invent facts.

Evaluation should check:

```text
Source conversation
      ↓
Summary
      ↓
Fact preservation
```

---

# 67. Memory Conflict

Example:

```text
Memory:
Application is pending.

Enterprise API:
Application is approved.
```

Use:

```text
Enterprise API
      ↓
Current truth
```

Memory becomes historical context.

---

# 68. Memory Staleness

Memory may contain:

```text
historical truth
```

rather than:

```text
current truth
```

The platform must distinguish these.

---

# 69. Memory Provenance

Each memory record should contain:

```yaml
memory:
  id: mem-123
  type: WORKFLOW_FACT
  source:
    type: ENTERPRISE_API
    reference: get-application
  created_at: "..."
  updated_at: "..."
```

---

# 70. Memory Source Types

Recommended:

```text
USER
ENTERPRISE_API
ENTERPRISE_EVENT
WORKFLOW
AI_SUMMARY
AI_INFERENCE
SYSTEM
```

---

# 71. Memory Write Sources

The safest initial policy is to permit writes from:

```text
Explicit user preference
Validated enterprise fact
Workflow state
Approved summarization process
```

AI inference should not automatically become permanent memory.

---

# 72. Memory Deduplication

Before storing:

```text
Candidate
 ↓
Normalize
 ↓
Hash/identity
 ↓
Existing?
 ├── YES → Update/ignore
 └── NO → Store
```

---

# 73. Memory Versioning

When a memory item changes:

```text
Memory v1
 ↓
Memory v2
```

For critical workflow facts, preserve sufficient history for audit/recovery.

---

# 74. Memory Expiration

Memory records may expire based on:

```text
TTL
Workflow completion
Business policy
User deletion
Data retention policy
```

---

# 75. Memory Deletion

Support:

```text
Delete conversation memory
Delete session memory
Delete user preference memory
Delete workflow memory
```

Deletion must respect enterprise retention/legal policies.

---

# 76. Memory Security

Memory access must be filtered by:

```text
User
Tenant
Organization
Conversation
Workflow
Role/claims
Data classification
```

---

# 77. Cross-User Isolation

This must never happen:

```text
User A
 ↓
Memory Search
 ↓
User B memory
```

Every query must be scoped.

---

# 78. Cross-Club Isolation

If users can operate across clubs:

```text
user_id
+
organization_id
+
club_id
```

must be part of the memory access boundary where applicable.

---

# 79. Memory Authorization

Authorization comes from the existing enterprise/APIM boundary where applicable, while the AI platform must enforce context isolation after claims are passed into the API context.

The memory layer must never broaden the permissions contained in the request claims.

---

# 80. Cache Authorization

Cache keys must respect the same security boundary.

A cache hit must never return data merely because another authorized request populated the key.

---

# 81. Cache Encryption

Sensitive persisted cache data should use approved encryption mechanisms.

Secrets must never be used as cache payloads.

---

# 82. Memory Encryption

Sensitive memory at rest must use approved encryption.

Transport must use approved secure protocols.

---

# 83. Secret Handling

Never store:

```text
JWT tokens
API keys
Client secrets
Passwords
Private keys
Connection strings containing secrets
```

in memory or cache.

---

# 84. Logging Policy

Do not log complete memory records by default.

Prefer:

```text
memory_id
type
scope
size
retrieval_count
trace_id
```

Mask sensitive values.

---

# 85. Cache Logging

Log:

```text
cache_key_hash
cache_type
hit/miss
TTL
latency
invalidation_reason
```

Do not expose raw sensitive cache keys.

---

# 86. Memory Observability

Track:

```text
Memory reads
Memory writes
Memory hits
Memory misses
Retrieval latency
Stored item count
Summary count
Deletion count
Expiration count
```

---

# 87. Cache Observability

Track:

```text
Cache hits
Cache misses
Hit ratio
Evictions
Invalidations
TTL expiry
Latency
Entry count
Memory utilization
Stampede events
```

---

# 88. Memory Quality Metrics

Track:

```text
Memory relevance
Memory contradiction rate
Memory retrieval precision
Memory stale rate
Summary accuracy
Memory write acceptance rate
```

---

# 89. Cache Performance Metrics

Track:

```text
Hit ratio
Miss ratio
Average latency
P95 latency
P99 latency
Eviction rate
Backend call reduction
```

---

# 90. Cost Optimization

Memory/cache should reduce:

```text
Enterprise API calls
RAG calls
Embedding calls
SLM context tokens
Latency
```

But optimization must not violate freshness or authorization requirements.

---

# 91. Cache Hit Ratio Target

Target values should be established through baseline measurement rather than arbitrary assumptions.

Track separately:

```text
API cache hit ratio
RAG cache hit ratio
Embedding cache hit ratio
Configuration cache hit ratio
```

---

# 92. Cache Failure Behavior

If cache becomes unavailable:

```text
Cache failure
 ↓
Bypass cache
 ↓
Enterprise API / source
```

For non-critical caches, cache failure should not normally fail the entire AI request.

---

# 93. Memory Store Failure

If memory is unavailable:

```text
Memory failure
 ↓
Determine mandatory?
 ├── NO → Continue without memory
 └── YES → Safe degradation / failure
```

Current authoritative enterprise context should still be retrieved when required.

---

# 94. Cache Dependency Isolation

The platform should prevent cache failure from cascading into:

```text
FastAPI
Supervisor
LangGraph
SLM
```

---

# 95. Memory Dependency Isolation

Similarly:

```text
Memory unavailable
 ↓
No uncontrolled retries
 ↓
Bounded fallback
```

---

# 96. Distributed Runtime

Because the AI runtime will scale across AKS pods:

```text
Pod 1
Pod 2
Pod 3
...
```

local process memory cannot be the only source of durable state.

Use shared persistence for:

```text
Session
Workflow
Checkpoint
Memory
Required cache
```

---

# 97. Local In-Process Cache

A small local cache may be used for:

```text
Immutable configuration
Prompt metadata
Model metadata
Short-lived safe values
```

But local cache must not be treated as globally consistent state.

---

# 98. Distributed Cache

A distributed cache may be used for:

```text
API responses
Session cache
RAG results
Embedding results
Context projections
Rate/concurrency coordination
```

The specific technology will be decided separately.

---

# 99. Cache Namespaces

Recommended:

```text
pf-ft:
  session:
  api:
  rag:
  embedding:
  prompt:
  model:
  context:
```

---

# 100. Environment Isolation

Cache namespaces must include environment where necessary:

```text
dev
test
staging
prod
```

Development cache must never collide with production cache.

---

# 101. Memory Namespace

Memory should be scoped by:

```text
environment
tenant
organization
user
conversation
workflow
```

as applicable.

---

# 102. Cache Versioning

Cache keys should include version when data contract changes.

Example:

```text
api:get-club:v2:<hash>
```

Schema/mapping changes should invalidate incompatible cache entries.

---

# 103. Memory Schema Versioning

Example:

```yaml
memory:
  schema_version: 1.0.0
```

Schema changes must have migration/backward compatibility plans.

---

# 104. Cache Schema Versioning

Cache payloads should contain:

```yaml
schema_version: 1.0.0
```

or be encoded in the key.

---

# 105. Memory and LangGraph

LangGraph state should reference durable memory where required.

Example:

```python
state.memory_refs = [
    "mem-123",
    "mem-456"
]
```

Avoid storing unlimited memory directly in graph state.

---

# 106. Memory and Agent Harness

The Harness should control memory:

```text
Agent
 ↓
Harness
 ↓
Memory Policy
 ↓
Retrieve
 ↓
Filter
 ↓
Budget
 ↓
Prompt
```

Agents should not bypass the Harness.

---

# 107. Cache and Agent Harness

The Harness may use cache internally:

```text
Tool result cache
RAG cache
Prompt cache
Model metadata cache
```

The agent should not directly manipulate shared infrastructure caches.

---

# 108. Memory + RAG

Memory and RAG remain separate retrieval channels.

```text
Memory
 → conversation/workflow/user history

RAG
 → knowledge/document corpus
```

They may both feed the Context Builder.

---

# 109. Memory + ERC

```text
Memory
 → historical context

ERC
 → current enterprise context
```

If conflict exists:

```text
Current authoritative enterprise data wins.
```

---

# 110. Cache + ERC

Cache can accelerate ERC construction:

```text
Cache
 ↓
Validated fresh API response
 ↓
ERC
```

But the cache itself does not become ERC authority.

---

# 111. Context Construction Example

```text
User:
"Continue the affiliation process."

       │
       ▼
Conversation Memory
       │
       ├── Previous workflow = affiliation
       │
       ▼
Workflow Memory
       │
       ├── Last state = waiting_for_event
       │
       ▼
ERC Reference
       │
       ├── ERC v7
       │
       ▼
Freshness Check
       │
       ▼
Enterprise API if required
       │
       ▼
Current ERC v8
       │
       ▼
Context Builder
       │
       ▼
SLM
```

---

# 112. Cache-Assisted Example

```text
Need Club Profile
       │
       ▼
Cache
   ┌───┴───┐
   │       │
  HIT     MISS
   │       │
Fresh?    API
   │       │
   └───┬───┘
       ▼
      ERC
```

---

# 113. Memory-Assisted Example

```text
Current User Request
       │
       ▼
Memory Search
       │
       ▼
Previous workflow context
       │
       ▼
Current ERC
       │
       ▼
Context Builder
```

---

# 114. Cache Invalidation from Workflow Actions

When a known enterprise mutation occurs:

```text
Transaction
 ↓
Known affected entity
 ↓
Invalidate related cache
 ↓
Refresh ERC if needed
```

Example:

```text
Update Official
 ↓
Invalidate official cache
 ↓
Refresh ERC officials
```

---

# 115. Cache Invalidation Granularity

Prefer targeted invalidation:

```text
official:123
```

rather than:

```text
invalidate entire system cache
```

---

# 116. Memory Invalidation

Memory should be invalidated when:

```text
Memory is explicitly corrected
Data retention expires
User requests deletion
Workflow lifecycle ends
Security policy changes
```

---

# 117. Historical vs Current Data

The platform should explicitly distinguish:

```yaml
fact:
  value: "Pending"
  observed_at: "2026-08-16"
  source: enterprise_api
```

from:

```yaml
memory:
  previous_value: "Submitted"
  observed_at: "2026-08-10"
```

This prevents stale memory from being confused with current state.

---

# 118. Memory Correction

If a user says:

```text
"That information is no longer correct."
```

the platform should not silently rewrite authoritative enterprise data.

It should update only the relevant memory record and, where appropriate, re-query enterprise systems.

---

# 119. Memory Contradiction Handling

```text
Memory says X
Enterprise says Y
       │
       ▼
Enterprise = current truth
       │
       ▼
Memory marked stale/contradicted
```

---

# 120. Cache Contradiction Handling

If cached data conflicts with a fresh enterprise response:

```text
Fresh enterprise response
       ↓
Replace/invalidate cache
       ↓
Use current enterprise data
```

---

# 121. Memory Evaluation Dataset

Maintain test cases:

```text
Query
Expected relevant memory
Expected irrelevant memory
Expected memory exclusion
Expected conflict handling
```

---

# 122. Cache Testing

Test:

- Hit
- Miss
- Expiry
- Invalidation
- Stampede protection
- Key isolation
- Version mismatch
- Backend failure
- Recovery

---

# 123. Memory Testing

Test:

- Retrieval
- Storage
- Scope
- Ranking
- Deduplication
- Expiration
- Summarization
- Conflict
- Deletion
- Security isolation

---

# 124. Security Testing

Mandatory scenarios:

```text
User A → User B memory attempt
Club A → Club B memory attempt
Tenant A → Tenant B cache attempt
Expired authorization
Sensitive memory retrieval
Prompt injection in memory
Malicious cached content
```

---

# 125. Performance Testing

Measure:

```text
Memory retrieval P50/P95/P99
Cache retrieval P50/P95/P99
Memory write latency
Cache write latency
Summary generation latency
Context assembly latency
```

---

# 126. Failure Testing

Simulate:

```text
Memory store unavailable
Cache unavailable
Partial cache failure
Network partition
Concurrent updates
Expired session
Stale memory
Invalid memory record
```

---

# 127. Unit Test Coverage

Required modules:

```text
memory policy
memory repository
memory retrieval
memory ranking
memory summarizer
memory deduplication
memory retention
cache key builder
cache policy
cache invalidation
cache TTL
cache serializer
cache fallback
scope isolation
```

---

# 128. Integration Test Flow

```text
FastAPI
 ↓
Session
 ↓
Memory
 ↓
ERC
 ↓
Cache
 ↓
Context Builder
 ↓
Agent Harness
 ↓
SLM
```

---

# 129. End-to-End Test

Scenario:

```text
Conversation 1
 ↓
User identifies club
 ↓
Workflow starts
 ↓
ERC built
 ↓
Workflow pauses
 ↓
Session ends
```

Later:

```text
Conversation 2
 ↓
"Continue"
 ↓
Memory identifies workflow
 ↓
Workflow state loaded
 ↓
ERC refreshed
 ↓
Workflow resumes
```

---

# 130. Long-Running Workflow Test

```text
Workflow
 ↓
Checkpoint
 ↓
Pod restart
 ↓
New pod
 ↓
Load workflow state
 ↓
Load ERC reference
 ↓
Load required memory
 ↓
Resume
```

---

# 131. Memory/Cache Definition of Done

The implementation is complete when:

- Memory types are defined.
- Memory scopes are defined.
- Memory provider is abstracted.
- Memory retrieval is policy-driven.
- Memory writes are policy-driven.
- Memory retention is defined.
- Memory summarization is defined.
- Memory security is implemented.
- Memory versioning is implemented.
- ERC references are supported.
- Cache categories are defined.
- Cache keys are deterministic.
- TTL is configurable.
- Invalidation is supported.
- Cache security isolation is implemented.
- Stampede protection is addressed.
- Cache failure fallback is defined.
- Observability is implemented.
- Unit tests exist.
- Integration tests exist.
- Security tests exist.
- Performance tests exist.
- Evaluation tests exist.

---

# 132. Recommended Python Package Boundary

```text
src/
└── pf_ft_ai/
    ├── memory/
    │   ├── models.py
    │   ├── provider.py
    │   ├── service.py
    │   ├── policy.py
    │   ├── retrieval.py
    │   ├── ranking.py
    │   ├── summarization.py
    │   ├── retention.py
    │   ├── deletion.py
    │   └── repository.py
    │
    ├── cache/
    │   ├── models.py
    │   ├── provider.py
    │   ├── service.py
    │   ├── policy.py
    │   ├── keys.py
    │   ├── ttl.py
    │   ├── invalidation.py
    │   ├── serialization.py
    │   └── protection.py
    │
    └── tests/
        ├── unit/
        │   ├── memory/
        │   └── cache/
        ├── integration/
        │   ├── memory/
        │   └── cache/
        └── evaluation/
            └── memory/
```

The final repository will merge these logical packages into the complete PF-FT platform structure.

---

# 133. Configuration

Recommended:

```text
config/
├── base/
│   ├── memory.yaml
│   ├── cache.yaml
│   ├── retention.yaml
│   └── memory-policies.yaml
│
├── dev/
├── test/
├── staging/
└── prod/
```

---

# 134. Memory Configuration Example

```yaml
memory:
  conversation:
    enabled: true
    retention_days: 30

  workflow:
    enabled: true

  user_preference:
    enabled: true

  summarization:
    enabled: true
    trigger_message_count: 20
```

Actual retention values must be aligned with enterprise policy.

---

# 135. Cache Configuration Example

```yaml
cache:
  enabled: true

  defaults:
    ttl_seconds: 300

  enterprise_api:
    enabled: true

  rag:
    enabled: true

  embedding:
    enabled: true

  prompt:
    enabled: true
```

---

# 136. Environment Configuration

```text
Development
 → local/test memory
 → development cache
 → synthetic data

Test
 → isolated test stores
 → controlled TTL
 → evaluation datasets

Staging
 → production-like configuration
 → production-like security

Production
 → approved shared stores
 → strict retention
 → encryption
 → monitoring
```

---

# 137. Recommended Store Abstraction

The application should use interfaces:

```python
class MemoryStore:
    async def get(...)
    async def put(...)
    async def delete(...)
```

```python
class CacheStore:
    async def get(...)
    async def set(...)
    async def delete(...)
    async def invalidate(...)
```

This prevents infrastructure coupling.

---

# 138. Provider Independence

The business/agent layer should not directly depend on:

```text
Redis
PostgreSQL
Cosmos DB
SQL
specific vendor APIs
```

The infrastructure implementation can be selected independently.

---

# 139. Persistence Decision

The exact technologies for:

```text
Memory
Session
Workflow state
Checkpoint
Cache
```

should be selected through the platform's technology decision process.

This document defines the required behavior, not the final infrastructure product choice.

---

# 140. Recommended Logical Separation

Even if the same physical technology is used:

```text
Memory Store
Session Store
Workflow/Checkpoint Store
Cache
```

should remain logically separated by namespace, schema or database boundary.

---

# 141. No Shared Uncontrolled State

Avoid:

```text
One giant key/value store
```

with no ownership boundaries.

Every stored object must identify:

```text
type
scope
version
owner
retention
classification
```

---

# 142. Memory Object Example

```yaml
memory:
  id: mem-123
  type: WORKFLOW_CONTEXT
  version: 1
  tenant_id: tenant-1
  user_id: user-1
  organization_id: club-123
  conversation_id: conv-1
  workflow_instance_id: wf-1

  source:
    type: ENTERPRISE_API
    reference: get-application

  content:
    application_id: app-123
    historical_status: SUBMITTED

  created_at: "..."
  expires_at: "..."
```

---

# 143. Cache Object Example

```yaml
cache:
  key_hash: abc123
  type: ENTERPRISE_API
  schema_version: 1.0.0
  source: enterprise.club.get

  metadata:
    tenant: tenant-1
    organization: club-123

  created_at: "..."
  expires_at: "..."
```

---

# 144. Memory Retrieval Contract

```python
class MemoryQuery:
    user_id: str
    organization_id: str | None
    conversation_id: str | None
    workflow_instance_id: str | None
    memory_types: list[str]
    query: str | None
    limit: int
```

---

# 145. Cache Retrieval Contract

```python
class CacheQuery:
    namespace: str
    key: str
    tenant_id: str
    organization_id: str | None
```

The cache implementation must enforce scope independently of the caller.

---

# 146. Memory Write Contract

```python
class MemoryWriteRequest:
    type: str
    scope: MemoryScope
    content: dict
    source: MemorySource
    retention_policy: str
    schema_version: str
```

---

# 147. Cache Write Contract

```python
class CacheWriteRequest:
    namespace: str
    key: str
    value: dict
    ttl_seconds: int
    schema_version: str
```

---

# 148. Context Builder Contract

```python
class ContextBuilder:
    async def build(
        self,
        request,
        session,
        memory_refs,
        erc_ref,
        rag_context,
        tool_results,
        policy
    ):
        ...
```

The builder returns a model-ready context projection.

---

# 149. Final Memory/Cache Runtime Flow

```text
                 USER REQUEST
                      │
                      ▼
                CONVERSATION
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       MEMORY       SESSION      ERC
          │           │           │
          │           │           │
          └───────────┼───────────┘
                      ▼
               CACHE LOOKUPS
                      │
          ┌───────────┼────────────┐
          ▼           ▼            ▼
       API Cache    RAG Cache   Context Cache
          │           │            │
          └───────────┼────────────┘
                      ▼
                CONTEXT BUILDER
                      │
                      ▼
                AGENT HARNESS
                      │
                      ▼
                     SLM
                      │
                      ▼
                  RESPONSE
```

---

# 150. Final Architecture Statement

The PF-FT Memory and Cache subsystem provides continuity and performance without becoming an alternative source of enterprise truth.

The architecture follows:

```text
Conversation
     ↓
Memory
     ↓
Current Workflow State
     ↓
ERC
     ↓
Cache-assisted retrieval
     ↓
Context Builder
     ↓
Agent Harness
     ↓
SLM
```

with the authoritative boundary remaining:

```text
Enterprise Systems
        ↓
Enterprise APIs / Events
        ↓
ERC
```

The platform therefore follows the fundamental rule:

> **Memory remembers, cache accelerates, ERC represents current workflow context, and enterprise systems remain authoritative.**
