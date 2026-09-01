# PF-FT Enterprise Agentic AI Platform — Conversation & Session Architecture

**Document ID:** PF-FT-AI-CONVERSATION-SESSION  
**Phase:** Phase 2 — Core Runtime & Interaction Management  
**Version:** 1.0.0  
**Status:** Development Baseline  
**Platform:** PF-FT Enterprise Agentic AI Platform / Adam AI  
**Runtime:** Python / FastAPI / LangGraph  

---

# 1. Purpose

This document defines the Conversation and Session management architecture for the PF-FT Enterprise Agentic AI Platform.

The Conversation & Session layer provides the continuity boundary between the Chat UI and the AI runtime.

It is responsible for:

- Creating conversations
- Loading conversations
- Maintaining message history
- Managing sessions
- Maintaining user interaction context
- Identifying active AI workflows
- Resuming workflows
- Managing conversation summaries
- Maintaining conversation memory references
- Managing session lifecycle
- Handling concurrent requests
- Supporting asynchronous workflow continuation
- Controlling context size
- Protecting sensitive information
- Providing state references to the Supervisor and Agents

This component does **not** own enterprise business state.

---

# 2. Core Principle

> **Conversation represents what the user and AI discussed. Session represents the interaction/runtime lifecycle. Workflow state represents what the AI workflow is doing. Enterprise state represents the authoritative business state.**

These four concepts must remain separate.

```text
Conversation
    │
    ├── Session
    │
    └── AI Workflow
            │
            └── ERC

Enterprise Business State
    ↑
    │
Enterprise APIs / Events
```

---

# 3. Boundary

The Conversation & Session layer sits between FastAPI and the AI orchestration runtime.

```text
Chat UI
   │
   ▼
FastAPI
   │
   ▼
Conversation & Session
   │
   ├──────────────► Supervisor
   │
   ├──────────────► Workflow Agent
   │
   ├──────────────► Memory
   │
   ├──────────────► Workflow State
   │
   └──────────────► ERC Reference
```

---

# 4. Responsibilities

The Conversation & Session layer owns:

| Capability | Responsibility |
|---|---|
| Conversation creation | Create conversation |
| Conversation retrieval | Load conversation |
| Message history | Maintain conversational history |
| Session creation | Create session |
| Session validation | Validate session lifecycle |
| Session expiry | Apply session TTL |
| Active workflow | Identify active AI workflow |
| Workflow resume | Provide workflow reference |
| Context projection | Provide relevant conversation context |
| Conversation summary | Maintain compressed history |
| Memory reference | Connect to memory layer |
| Concurrency | Protect concurrent conversation updates |
| Security | Prevent cross-user conversation access |
| Audit | Record lifecycle events |
| State versioning | Version conversation/session schema |

---

# 5. Non-Responsibilities

This component does not own:

- Enterprise authentication
- Enterprise authorization
- Enterprise business rules
- Enterprise workflow
- Enterprise database
- Enterprise transaction state
- Enterprise scheduling
- Human approval
- Business compliance decision
- SLM reasoning
- Agent routing
- Tool execution
- RAG retrieval

Those responsibilities belong to other platform components.

---

# 6. Conversation vs Session vs Workflow

These concepts must not be merged.

## Conversation

Represents the user's logical chat.

Example:

```text
Conversation #1001
 ├── User message
 ├── AI response
 ├── User clarification
 ├── AI response
 └── Active workflow
```

## Session

Represents an interaction lifecycle.

Example:

```text
Session #2001
 ├── Started
 ├── Active
 ├── Idle
 └── Expired
```

## Workflow

Represents an AI business interaction.

Example:

```text
Affiliation Workflow
 ├── Understand
 ├── Collect Context
 ├── Build ERC
 ├── Reason
 ├── Execute
 └── Wait/Complete
```

---

# 7. Conversation Identity

Every conversation requires a unique identifier.

```yaml
conversation_id: conv-01J...
```

The identifier must be:

- Unique
- Non-guessable
- Stable
- Traceable
- Safe to expose to the client where required

Do not expose internal database identifiers if they reveal implementation details.

---

# 8. Session Identity

Every session requires:

```yaml
session_id: sess-01J...
```

The session is associated with:

```text
user
conversation
client/channel
environment
created_at
last_activity_at
expiry
```

---

# 9. User Context

Conversation access must always be associated with the validated enterprise identity context.

Conceptual:

```yaml
user_context:
  subject_reference: user-123
  organization_reference: club-456
  roles: []
  claims_reference: claims-123
```

The actual authorization remains controlled by APIM/enterprise security.

---

# 10. Conversation Creation

New conversation flow:

```text
POST /chat
    │
    ▼
Conversation ID supplied?
    │
 ┌──┴───┐
No     Yes
 │       │
Create  Load
 │       │
 └──┬────┘
    ▼
Validate Ownership
    │
    ▼
Create/Load Session
    │
    ▼
Create Message
    │
    ▼
Start AI Runtime
```

---

# 11. Conversation Creation Contract

Conceptual:

```json
{
  "conversation_id": "conv-123",
  "session_id": "sess-123",
  "status": "ACTIVE",
  "created_at": "2026-08-15T10:00:00Z",
  "last_activity_at": "2026-08-15T10:00:00Z"
}
```

---

# 12. Conversation Status

Recommended states:

```text
NEW
ACTIVE
WAITING_FOR_USER
WAITING_FOR_HUMAN
WAITING_FOR_EXTERNAL_EVENT
COMPLETED
CLOSED
EXPIRED
ERROR
```

---

# 13. Conversation State Transitions

```text
NEW
 ↓
ACTIVE
 ├───────────────┐
 ↓               │
WAITING_FOR_USER │
 ↓               │
ACTIVE ◄─────────┘
 │
 ├──► WAITING_FOR_HUMAN
 │          │
 │          ▼
 │        ACTIVE
 │
 ├──► WAITING_FOR_EXTERNAL_EVENT
 │          │
 │          ▼
 │        ACTIVE
 │
 └──► COMPLETED
          │
          ▼
        CLOSED
```

---

# 14. Session Status

Recommended states:

```text
CREATED
ACTIVE
IDLE
EXPIRED
TERMINATED
```

Transitions:

```text
CREATED
 ↓
ACTIVE
 ↓
IDLE
 ├──► ACTIVE
 └──► EXPIRED
```

---

# 15. Session TTL

Session expiration must be configuration driven.

Example:

```yaml
session:
  idle_timeout_minutes: 30
  absolute_timeout_hours: 8
```

The actual values are environment-specific and must not be hard-coded.

---

# 16. Conversation Lifetime vs Session Lifetime

A conversation can outlive a session.

Example:

```text
Conversation
     │
     ├── Session 1 → Expired
     │
     ├── Session 2 → Active
     │
     └── Session 3 → Active
```

The conversation remains the logical user interaction.

The session represents a particular interaction period.

---

# 17. Message Model

Recommended message structure:

```yaml
message:
  message_id: msg-123
  conversation_id: conv-123
  session_id: sess-123
  role: user
  content: "What is the affiliation status?"
  created_at: "..."
  sequence_number: 15
  metadata: {}
```

Roles:

```text
USER
ASSISTANT
SYSTEM
TOOL
```

Internal messages should not automatically be exposed to the Chat UI.

---

# 18. Message Sequence

Messages must maintain deterministic ordering.

```text
sequence_number
```

Example:

```text
1 USER
2 ASSISTANT
3 USER
4 ASSISTANT
```

Sequence handling must support concurrent requests.

---

# 19. Message Idempotency

A client request should support an idempotency key.

Example:

```yaml
idempotency_key: client-msg-123
```

If the same request is submitted twice:

```text
Request A → Process
Request B → Detect duplicate
```

The platform must not create duplicate user messages or duplicate enterprise operations.

---

# 20. Message Persistence

Messages should be persisted before or as part of controlled runtime execution depending on the failure policy.

Recommended lifecycle:

```text
Receive
 ↓
Validate
 ↓
Persist User Message
 ↓
Execute AI Runtime
 ↓
Persist Assistant Response
```

For streaming responses, final assistant content must be persisted after successful completion.

---

# 21. Message Failure Handling

If AI execution fails:

```text
User Message
      ↓
Persisted
      ↓
AI Runtime Failure
      ↓
Conversation remains recoverable
```

The platform should preserve enough state to retry/resume rather than losing the user request.

---

# 22. Active Workflow Association

A conversation may have:

```yaml
active_workflow:
  workflow_instance_id: wf-123
  workflow_type: affiliation
  status: IN_PROGRESS
```

This is a reference.

The complete workflow state belongs to the Workflow/State layer.

---

# 23. Multiple Workflows in One Conversation

A conversation can contain multiple workflows over time.

Example:

```text
Conversation
 ├── Affiliation Workflow → COMPLETED
 ├── Registration Workflow → COMPLETED
 └── Affiliation Status Workflow → ACTIVE
```

Only one workflow should normally be marked as the active workflow unless the platform explicitly supports concurrent workflows.

---

# 24. Workflow Resume

When a new user message arrives:

```text
Conversation
 ↓
Active Workflow?
 ↓
YES
 ↓
Load Workflow State
 ↓
Resume
```

The Supervisor should not unnecessarily start a new workflow.

---

# 25. Workflow Resume vs New Intent

Example:

```text
User:
"Continue with the affiliation."
```

Expected:

```text
Conversation
 ↓
Active Affiliation Workflow
 ↓
Resume
```

New intent:

```text
User:
"Now show me the official courses."
```

Expected:

```text
Supervisor
 ↓
New/alternate workflow decision
```

The exact switching policy is defined by the Supervisor architecture.

---

# 26. Conversation Context Projection

The complete conversation history should not always be passed to the SLM.

Instead:

```text
Full Conversation
       ↓
Context Selection
       ↓
Relevant Messages
       ↓
Summary
       ↓
Current User Message
       ↓
SLM Context
```

---

# 27. Conversation Context Priority

Recommended priority:

```text
1. Current User Message
2. Active Workflow Context
3. Recent Conversation
4. Conversation Summary
5. Important Persistent Facts
6. Older Conversation
```

Security/claims context is handled separately and must not be treated as ordinary conversation memory.

---

# 28. Conversation Summary

Long conversations require summarization.

Summary should preserve:

- User intent
- Important entities
- Important decisions
- Workflow progress
- Pending actions
- Clarifications
- User-provided relevant facts
- Enterprise references
- Important constraints

---

# 29. Summary Example

```yaml
conversation_summary:
  version: "1.0.0"
  summary:
    intent: club_affiliation
    club_reference: club-123
    current_status: context_collection
    pending_action: retrieve_officials
    important_facts:
      - "User wants to complete affiliation."
```

The summary is derived AI context, not enterprise truth.

---

# 30. Summary Update Strategy

Do not summarize after every message unnecessarily.

Possible strategy:

```text
Recent messages
      ↓
Token threshold?
      │
 ┌────┴────┐
No        Yes
 │          │
Keep       Summarize
```

The threshold must be configurable.

---

# 31. Summary Versioning

Every summary should record:

```yaml
summary_version: 1.0.0
created_at: "..."
source_message_sequence: 1-40
model_version: "..."
```

This supports reproducibility.

---

# 32. Conversation Memory

Conversation memory is different from conversation storage.

```text
Conversation Store
    ↓
Complete history

Memory Layer
    ↓
Relevant information for future reasoning
```

Memory may contain:

- Summaries
- Important facts
- Preferences where permitted
- Workflow references
- Relevant prior context

---

# 33. Memory Selection

Before an AI run:

```text
Current User Query
        ↓
Memory Retrieval
        ↓
Relevant Memory
        ↓
Context Projection
```

Do not load all historical memory into every prompt.

---

# 34. Memory Security

Memory must not retain sensitive information unnecessarily.

Never persist:

- Passwords
- Tokens
- Secrets
- API keys
- Authentication credentials
- Raw authorization tokens

Sensitive enterprise data must follow approved data retention and access policies.

---

# 35. Session Context

Session context may contain:

```yaml
session_context:
  locale: en-IN
  timezone: Asia/Kolkata
  client: web
  last_activity: "..."
  active_conversation: conv-123
```

Only approved client metadata should be retained.

---

# 36. Claims Context

Claims are received from the enterprise/APIM boundary.

Conversation & Session may reference:

```yaml
claims_reference:
  subject: user-123
  roles: []
  permissions: []
```

Do not store raw access tokens as conversation/session data.

---

# 37. Conversation Ownership

Every conversation must be associated with an identity boundary.

Before retrieval:

```text
conversation_id
      ↓
User identity
      ↓
Ownership/access check
      ↓
Load conversation
```

A user must never be able to access another user's conversation by guessing an ID.

---

# 38. Multi-Tenant Boundary

Where applicable:

```text
Tenant
 ↓
Organization
 ↓
User
 ↓
Conversation
 ↓
Session
```

Conversation queries must always apply tenant/organization isolation.

---

# 39. Concurrent Conversation Requests

Potential scenario:

```text
Request A
"What is my affiliation status?"

Request B
"What documents are pending?"
```

arrive simultaneously.

The platform must prevent:

- Message sequence corruption
- Workflow state corruption
- Duplicate tool execution
- Conflicting ERC updates

---

# 40. Concurrency Control

Recommended:

```text
conversation_id
+
version
+
optimistic concurrency
```

Example:

```text
Conversation Version = 10

Request A → 10 → 11
Request B → 10 → conflict
```

Request B should reload/reconcile rather than overwrite state blindly.

---

# 41. Workflow Concurrency

If multiple messages target the same active workflow:

```text
Conversation Lock / Workflow Version
       ↓
Serialize critical workflow transitions
```

Independent read-only operations may still execute concurrently where safe.

---

# 42. Async Workflow Support

Conversation/session must support workflows that outlive HTTP requests.

Example:

```text
POST /chat
 ↓
AI workflow starts
 ↓
Enterprise action
 ↓
WAITING_FOR_EXTERNAL_EVENT
 ↓
HTTP request completes
```

Later:

```text
Service Bus event
 ↓
Workflow resume
```

---

# 43. Waiting for User

When the AI requires information:

```text
Workflow
 ↓
WAITING_FOR_USER
 ↓
Conversation response
```

The user response must reconnect to the same workflow where applicable.

Example:

```text
AI:
"Which team should I use?"

User:
"Senior Men's team."

 ↓

Existing workflow resumes
```

---

# 44. Waiting for Human

The AI Platform supports the waiting state but does not own the human decision.

```text
AI Workflow
 ↓
WAITING_FOR_HUMAN
 ↓
Enterprise HIL
 ↓
Enterprise event/result
 ↓
Conversation/Workflow resume
```

---

# 45. Waiting for External Event

Example:

```text
AI Workflow
 ↓
Enterprise async operation
 ↓
WAITING_FOR_EXTERNAL_EVENT
```

The workflow stores:

```yaml
waiting:
  event_type: affiliation.updated
  enterprise_reference: app-123
  resume_node: refresh_erc
```

---

# 46. Event Resume

```text
Service Bus
 ↓
Event Consumer
 ↓
Find workflow
 ↓
Validate event
 ↓
Load workflow state
 ↓
Invalidate relevant ERC
 ↓
Refresh enterprise context
 ↓
Resume LangGraph
```

---

# 47. Conversation After External Event

The user does not necessarily need to send another message.

The platform can update workflow state and make the next response available.

If product requirements support push/notification:

```text
Event
 ↓
Workflow Resume
 ↓
Conversation Update
 ↓
UI Notification
```

This mechanism is separate from enterprise scheduled workflows.

---

# 48. Session Expiration During Workflow

A session can expire while an AI workflow remains active.

Example:

```text
Session → EXPIRED
Workflow → WAITING_FOR_EXTERNAL_EVENT
```

The workflow state must remain recoverable according to workflow retention policy.

A future session may resume the conversation after validating access.

---

# 49. Conversation Closure

A conversation can be closed when:

- User explicitly ends it
- Product policy closes it
- Retention period ends
- Workflow is completed and no further interaction is expected

Closing conversation must not automatically cancel an enterprise transaction.

---

# 50. Conversation Reopening

If supported:

```text
CLOSED
 ↓
New Session
 ↓
Access Validation
 ↓
Conversation Context Projection
 ↓
New Workflow / Resume
```

The platform must determine whether the previous workflow is still valid before resuming.

---

# 51. Session Termination

Session termination may occur because:

- Logout
- Timeout
- Security event
- Client termination
- Administrative action

Termination removes active session state but does not automatically delete conversation history.

---

# 52. Session Security

Session identifiers must be:

- Non-predictable
- Bound to the user
- Validated on every request
- Expirable
- Revocable

Do not trust a session ID supplied by the client without server-side validation.

---

# 53. Session Context and SLM

The SLM should receive only the required session context.

Example:

```text
Locale
Timezone
Channel
Current workflow reference
Relevant interaction context
```

Do not send unnecessary session metadata.

---

# 54. Conversation Context and ERC

ERC is not conversation history.

```text
Conversation
  = what was discussed

ERC
  = current structured operational context
```

The AI may use both:

```text
Conversation Context
+
Current ERC
```

The current authoritative ERC should supersede stale conversational claims about enterprise state.

---

# 55. Conversation Context and RAG

RAG may use:

```text
Current User Query
+
Relevant Conversation Context
+
Workflow Context
```

Do not use the entire conversation as the retrieval query.

---

# 56. Conversation Context and Prompt Injection

Conversation history may contain malicious content.

Therefore:

```text
Historical Message
      ↓
Context Classification
      ↓
Trusted / Untrusted
      ↓
Prompt Construction
```

User-generated content must never be treated as system instructions.

---

# 57. Prompt Injection Protection

Conversation/session layer must preserve role boundaries.

Example:

```text
SYSTEM
  ↓
DEVELOPER / PLATFORM POLICY
  ↓
AGENT INSTRUCTIONS
  ↓
TOOL CONTRACT
  ↓
USER MESSAGE
  ↓
HISTORICAL USER CONTENT
```

Historical messages must not override system/agent policies.

---

# 58. Conversation Data Classification

Recommended metadata:

```yaml
data_classification:
  level: INTERNAL
  contains_sensitive_data: false
```

The actual classification policy will be defined by enterprise security requirements.

---

# 59. Conversation Retention

Retention must be configurable.

Possible policies:

```yaml
retention:
  conversation_days: 90
  session_days: 1
  workflow_days: 180
  audit_days: 365
```

These are examples only.

Actual values must be determined through security/compliance governance.

---

# 60. Conversation Deletion

Deletion policy must define:

- User deletion
- Administrative deletion
- Retention expiration
- Legal hold
- Audit preservation
- Backup deletion

Deleting a conversation must not accidentally delete enterprise records.

---

# 61. Conversation Export

If required, export should provide:

```text
Conversation metadata
Messages
Relevant workflow status
User-visible responses
References
```

Internal prompts, hidden reasoning and secrets must not be included.

---

# 62. Conversation Audit

Audit significant actions:

```text
Conversation Created
Session Created
Message Received
Workflow Started
Workflow Resumed
Workflow Paused
Workflow Completed
Conversation Closed
Session Expired
```

Audit must include:

```text
timestamp
conversation_id
session_id
workflow_id
actor
correlation_id
```

---

# 63. Conversation Observability

Metrics:

- Active conversations
- New conversations
- Messages/conversation
- Average conversation duration
- Session duration
- Session expiration rate
- Workflow resume rate
- Clarification rate
- Abandonment rate
- Error rate
- Concurrent conversation count

---

# 64. Conversation Tracing

Trace hierarchy:

```text
Conversation
   └── Session
         └── Request
               └── Workflow
                     └── Agent Run
                           └── LangGraph
```

This should map into Langfuse/OpenTelemetry according to the observability architecture.

---

# 65. Langfuse Integration

Conversation-level trace metadata may include:

```yaml
conversation_id: conv-123
session_id: sess-123
workflow_id: wf-123
agent_id: affiliation_agent
```

Do not send sensitive conversation content to Langfuse unless explicitly permitted by the data policy.

---

# 66. Error Handling

Conversation/session errors should be classified.

| Error | Behavior |
|---|---|
| Invalid conversation ID | Reject |
| Conversation not found | Safe error |
| Access denied | Reject |
| Session expired | Create/re-establish session according to policy |
| Concurrent update | Reload/retry |
| Persistence unavailable | Fail safely |
| Workflow missing | Route/recover |
| Corrupted state | Recovery/error |
| Retention expired | Do not restore |
| Unauthorized resume | Reject |

---

# 67. Conversation Recovery

If the application pod restarts:

```text
New Request
 ↓
Conversation ID
 ↓
Session
 ↓
Workflow
 ↓
Checkpoint
 ↓
Resume
```

No critical conversation/workflow state should depend on local Python memory.

---

# 68. Stateless API Principle

FastAPI instances should remain horizontally scalable.

```text
                ┌── FastAPI Pod 1
Chat UI ────────┼── FastAPI Pod 2
                ├── FastAPI Pod 3
                └── FastAPI Pod N
                         │
                         ▼
                 Shared State Stores
```

The API pod must not own durable conversation state.

---

# 69. Session Affinity

Sticky sessions should not be required for correctness.

Correctness must come from shared durable state.

Load balancing:

```text
Request 1 → Pod 1
Request 2 → Pod 3
Request 3 → Pod 2
```

All pods must resolve the same conversation/session state.

---

# 70. State Storage Abstractions

Recommended interfaces:

```python
class ConversationStore:
    async def create(...)
    async def get(...)
    async def update(...)
    async def close(...)

class SessionStore:
    async def create(...)
    async def get(...)
    async def touch(...)
    async def expire(...)
    async def terminate(...)

class MessageStore:
    async def append(...)
    async def list(...)
    async def get_by_sequence(...)
```

Resolved: Azure Managed Redis, behind these store interfaces — see ADR-D4-10.

---

# 71. Repository Boundary

Application code should depend on interfaces:

```text
ConversationService
      ↓
ConversationStore
      ↓
Concrete Persistence Adapter
```

Avoid:

```text
FastAPI endpoint
      ↓
Direct database query
```

---

# 72. Transaction Boundary

A user message lifecycle may require:

```text
Persist Message
+
Create/Update Conversation
+
Create/Update Session
```

These operations should have a clearly defined consistency strategy.

AI execution should not be tightly coupled to a long database transaction.

---

# 73. Conversation Versioning

Conversation schema should be versioned.

```yaml
conversation_schema_version: 1.0.0
```

Changes to message structure, workflow references or metadata should be backward-compatible or migrated.

---

# 74. Session Versioning

```yaml
session_schema_version: 1.0.0
```

The runtime must validate state before use.

---

# 75. Configuration

Environment-specific configuration should be externalized.

Example:

```yaml
conversation:
  max_history_messages: 50
  summary_threshold_tokens: 12000
  max_message_size: 10000

session:
  idle_timeout_minutes: 30
  absolute_timeout_hours: 8

workflow:
  resume_enabled: true
```

Secrets must not be stored in YAML configuration.

---

# 76. API Contract

Recommended endpoints:

```text
POST   /api/v1/chat
GET    /api/v1/conversations/{conversation_id}
GET    /api/v1/conversations/{conversation_id}/messages
POST   /api/v1/conversations
POST   /api/v1/conversations/{conversation_id}/close
GET    /api/v1/sessions/{session_id}
```

The exact API contract will be defined separately.

---

# 77. Chat Request Processing

Recommended flow:

```text
POST /chat
      ↓
Validate request
      ↓
Validate claims
      ↓
Resolve conversation
      ↓
Resolve session
      ↓
Check message idempotency
      ↓
Persist user message
      ↓
Resolve active workflow
      ↓
Supervisor or resume
      ↓
AI Runtime
      ↓
Persist response/state
      ↓
Return response
```

---

# 78. Chat Response Processing

```text
AI Runtime
 ↓
Response Validation
 ↓
User-Safe Formatting
 ↓
Persist Assistant Message
 ↓
Update Conversation
 ↓
Update Session
 ↓
Return FastAPI Response
```

---

# 79. Streaming Response

If SSE is used:

```text
POST /chat
 ↓
Create/resolve conversation
 ↓
Start workflow
 ↓
Stream approved progress/events
 ↓
Final response
 ↓
Persist final state
```

The connection itself must not be the source of durable workflow state.

---

# 80. Conversation Cancellation

If the UI disconnects:

```text
Browser disconnect
       ↓
HTTP stream ends
```

This does not automatically mean:

```text
Workflow cancelled
```

The runtime must distinguish:

```text
Client disconnected
vs
Workflow cancelled
```

For durable operations, the workflow may continue.

---

# 81. Duplicate Request Protection

The same client request may arrive because of:

- Browser retry
- Network retry
- Load balancer retry
- Client retry

Use:

```text
idempotency_key
+
conversation_id
+
user identity
```

to detect duplicates.

---

# 82. Conversation and Transaction Safety

Conversation processing must not trigger duplicate enterprise operations.

Example:

```text
User:
"Submit my application."

Request A → enterprise submission
Request timeout
Request B → duplicate user retry
```

The workflow must detect the previous transaction state before submitting again.

---

# 83. Conversation and Enterprise Truth

A previous message may say:

```text
"Your application is approved."
```

Later the enterprise API may return:

```text
PENDING
```

The runtime must communicate the current authoritative enterprise state.

Historical conversation content does not override current enterprise state.

---

# 84. Conversation and ERC Freshness

Before answering a state-sensitive question:

```text
Conversation
 ↓
Active ERC
 ↓
Check freshness
 ↓
If stale
 ↓
Refresh required enterprise context
 ↓
Answer
```

---

# 85. Conversation and Cache

Conversation responses should not blindly reuse cached text.

Cache may store structured information where safe.

Prefer:

```text
Cached structured data
 ↓
Current context
 ↓
Fresh response generation
```

rather than caching complete AI responses for operational workflows unless explicitly approved.

---

# 86. Conversation Security Threats

Threats include:

- Conversation ID enumeration
- Cross-user access
- Cross-tenant access
- Session fixation
- Session hijacking
- Replay
- Duplicate requests
- Prompt injection through history
- Sensitive data leakage
- Excessive history exposure
- Malicious metadata
- Unauthorized workflow resume

---

# 87. Security Controls

Controls include:

```text
APIM authorization
 ↓
Identity/claims validation
 ↓
Conversation ownership validation
 ↓
Tenant isolation
 ↓
Input validation
 ↓
Message sanitization/classification
 ↓
Prompt injection controls
 ↓
Output filtering
 ↓
Audit
```

---

# 88. Conversation Access Control

Every conversation retrieval should validate:

```text
Authenticated Subject
+
Tenant/Organization
+
Conversation Ownership
+
Current Claims
```

Never rely only on `conversation_id`.

---

# 89. Data Minimization

Only store data needed for:

- Conversation continuity
- Workflow recovery
- Audit
- User experience
- AI evaluation where approved

Do not duplicate entire enterprise datasets into conversation storage.

ERC remains a separate derived context store.

---

# 90. Performance Considerations

Conversation retrieval should avoid loading:

```text
Entire conversation
+
Entire memory
+
Entire ERC
```

for every request.

Use:

```text
Recent messages
+
Summary
+
Relevant memory
+
ERC reference
```

and fetch detailed data only when required.

---

# 91. Large Conversation Handling

Example:

```text
5,000 messages
```

The runtime should not pass all 5,000 messages to the SLM.

Instead:

```text
5,000 messages
 ↓
Summaries
 ↓
Recent window
 ↓
Relevant retrieval
 ↓
Current query
```

---

# 92. Context Window Protection

Conversation manager must enforce:

```text
max_history_tokens
max_summary_tokens
max_message_size
max_context_items
```

When limits are exceeded:

```text
Summarize
 ↓
Compress
 ↓
Retrieve relevant history
```

---

# 93. Conversation Context Quality

The system should preserve context that changes workflow behavior.

Examples:

```text
User selected club A
User selected senior team
User confirmed official X
User declined option Y
HIL requested
```

These should not disappear simply because old messages were summarized.

---

# 94. Important Facts

Important facts should be stored as structured references where possible.

Example:

```yaml
facts:
  club_reference: club-123
  selected_team_reference: team-456
  selected_official_reference: official-789
```

The authoritative entity data should still be retrieved from enterprise systems when current information is required.

---

# 95. Conversation State vs Memory

Conversation:

```text
Complete interaction record
```

Memory:

```text
Selected useful information
```

Workflow:

```text
Current AI execution
```

ERC:

```text
Current structured context
```

These must remain separate.

---

# 96. State Transition Example

User:

```text
"Help me complete club affiliation."
```

Runtime:

```text
Conversation NEW
 ↓
Session CREATED
 ↓
Conversation ACTIVE
 ↓
Supervisor ROUTED
 ↓
Workflow CREATED
 ↓
Agent EXECUTING
 ↓
Conversation ACTIVE
```

---

# 97. Waiting Example

```text
AI:
"Your request requires human review."

Conversation:
WAITING_FOR_HUMAN

Workflow:
WAITING_FOR_HUMAN

Session:
ACTIVE / IDLE
```

Enterprise HIL completes:

```text
Service Bus Event
 ↓
Workflow RESUMING
 ↓
Conversation ACTIVE
```

---

# 98. Completion Example

```text
Workflow
 ↓
COMPLETED

Conversation
 ↓
ACTIVE

Session
 ↓
ACTIVE
```

The conversation can continue after workflow completion.

---

# 99. Session Expiry Example

```text
Conversation:
ACTIVE

Session:
EXPIRED

Workflow:
WAITING_FOR_EXTERNAL_EVENT
```

Later:

```text
User returns
 ↓
New session
 ↓
Access validation
 ↓
Conversation loaded
 ↓
Workflow status checked
 ↓
Resume or start new workflow
```

---

# 100. Acceptance Criteria

The Conversation & Session implementation must satisfy:

1. Conversation and session are separate entities.
2. Workflow state is separate from conversation state.
3. Enterprise state is never stored as authoritative conversation state.
4. Conversation ownership is validated.
5. Tenant boundaries are enforced where applicable.
6. Session expiration is configurable.
7. Conversation can outlive a session.
8. Workflow can outlive an HTTP request.
9. External events can resume workflows.
10. HIL waiting state is supported.
11. User clarification can resume the same workflow.
12. Message ordering is deterministic.
13. Duplicate messages are handled.
14. Concurrent requests are safely handled.
15. Long conversations are summarized.
16. Context selection is token-aware.
17. Historical messages cannot override system instructions.
18. Sensitive data is protected.
19. State is recoverable after pod restart.
20. API instances remain stateless.
21. Conversation data is observable.
22. State transitions are auditable.
23. Schema versions are maintained.
24. Conversation retrieval is performant.
25. Enterprise current state overrides stale conversation context.

---

# 101. Recommended Implementation Components

Logical components:

```text
Conversation API
      ↓
Conversation Service
      ├── Conversation Manager
      ├── Message Manager
      ├── Session Manager
      ├── Context Projector
      ├── Summary Manager
      ├── Access Validator
      └── Concurrency Manager
```

Dependencies:

```text
Conversation Service
 ├── Conversation Store
 ├── Session Store
 ├── Message Store
 ├── Workflow State Store
 ├── Memory Service
 ├── ERC Service
 ├── Audit Service
 └── Observability
```

---

# 102. Suggested Python Package Boundary

```text
src/
└── pf_ft_ai/
    ├── api/
    │   └── v1/
    │       └── chat.py
    │
    ├── application/
    │   ├── conversation/
    │   │   ├── service.py
    │   │   ├── commands.py
    │   │   ├── queries.py
    │   │   └── dto.py
    │   │
    │   └── session/
    │       ├── service.py
    │       └── dto.py
    │
    ├── domain/
    │   ├── conversation/
    │   │   ├── entities.py
    │   │   ├── value_objects.py
    │   │   └── states.py
    │   │
    │   └── session/
    │       ├── entities.py
    │       └── states.py
    │
    ├── infrastructure/
    │   ├── persistence/
    │   │   ├── conversation_store.py
    │   │   ├── session_store.py
    │   │   └── message_store.py
    │   │
    │   └── cache/
    │       └── session_cache.py
    │
    └── tests/
        ├── unit/
        │   ├── conversation/
        │   └── session/
        └── integration/
```

This is a logical boundary; the final repository structure will be consolidated with the complete platform folder structure.

---

# 103. Unit Test Requirements

Minimum unit test areas:

## Conversation

- Create conversation
- Retrieve conversation
- Update conversation
- Close conversation
- Ownership validation
- Tenant validation
- Status transition
- Duplicate request
- Concurrent update

## Session

- Create session
- Resolve session
- Touch session
- Expire session
- Terminate session
- Session ownership
- TTL handling

## Messages

- Append
- Ordering
- Duplicate detection
- Message size validation
- Role validation

## Summary

- Threshold detection
- Summary generation
- Summary versioning
- Important fact preservation

## Workflow Resume

- Active workflow detection
- Resume
- New workflow
- Waiting state
- External event resume

---

# 104. Integration Test Requirements

Test:

```text
FastAPI
 ↓
Conversation Service
 ↓
Session Service
 ↓
State Store
 ↓
Workflow Runtime
```

Scenarios:

- New conversation
- Existing conversation
- New session
- Expired session
- Active workflow resume
- HIL resume
- Service Bus resume
- Concurrent messages
- Pod restart/recovery

---

# 105. Security Test Requirements

Test:

- Unauthorized conversation access
- Cross-user conversation access
- Cross-tenant access
- Session fixation
- Replay
- Duplicate requests
- Prompt injection in history
- Sensitive data exposure
- Token leakage
- Malicious message metadata

---

# 106. Performance Test Requirements

Measure:

- Conversation retrieval latency
- Message append latency
- Session lookup latency
- Concurrent conversation requests
- Large conversation retrieval
- Summary generation overhead
- State store throughput
- Concurrent workflow resume

Targets should be established through the NFR/ADR process.

---

# 107. Observability Requirements

Every operation should provide:

```text
conversation_id
session_id
workflow_id
request_id
correlation_id
user_reference
timestamp
state_before
state_after
duration
result
```

Sensitive data must be masked.

---

# 108. Configuration Files

Conversation/session configuration should be version controlled as non-secret configuration.

Example:

```text
config/
├── base/
│   └── conversation.yaml
├── dev/
│   └── conversation.yaml
├── test/
│   └── conversation.yaml
├── staging/
│   └── conversation.yaml
└── prod/
    └── conversation.yaml
```

Secrets are not stored here.

---

# 109. Environment Configuration

Example:

```yaml
conversation:
  max_history_messages: 50
  max_history_tokens: 12000
  summary_threshold_tokens: 10000

session:
  idle_timeout_minutes: 30
  absolute_timeout_hours: 8

security:
  enforce_ownership: true
  enforce_tenant_isolation: true

workflow:
  resume_enabled: true
```

---

# 110. Versioning

The following must be versioned independently:

```text
Conversation schema
Session schema
Message schema
Summary schema
Workflow reference schema
API contract
Configuration
Prompt
Agent
Workflow
ERC
Model
```

---

# 111. Final Architecture

```text
                         CHAT UI
                            │
                            ▼
                         FASTAPI
                            │
                    ┌───────┴────────┐
                    │                │
             Conversation         Session
                    │                │
                    └───────┬────────┘
                            │
                    Context Projection
                            │
              ┌─────────────┼──────────────┐
              │             │              │
              ▼             ▼              ▼
         Conversation     Memory         Workflow
          Summary                       State
              │             │              │
              └─────────────┼──────────────┘
                            ▼
                       Supervisor
                            │
                            ▼
                         Agent
                            │
                            ▼
                       LangGraph
                            │
                            ▼
                           ERC
```

---

# 112. Final Principles

The Conversation & Session layer must follow these principles:

1. **Conversation is not workflow state.**
2. **Session is not conversation.**
3. **AI workflow is not enterprise workflow.**
4. **ERC is not conversation memory.**
5. **Memory is not enterprise truth.**
6. **Historical messages are untrusted user content.**
7. **Enterprise current state overrides stale conversation context.**
8. **FastAPI remains stateless.**
9. **Durable state lives outside application process memory.**
10. **Long-running workflows must survive HTTP/session boundaries.**
11. **External events can resume workflows.**
12. **HIL remains enterprise-authoritative.**
13. **Conversation access must be identity/tenant controlled.**
14. **State must be versioned and recoverable.**
15. **Every critical state transition must be observable.**
16. **Conversation context must be token-budget aware.**
17. **Duplicate requests must not cause duplicate enterprise actions.**
18. **Secrets must never enter conversation or memory.**
19. **The SLM receives a controlled context projection, not the entire conversation store.**
20. **The Conversation & Session layer provides continuity; it does not become a second enterprise system.**
