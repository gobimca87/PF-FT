# Service Bus / DLQ Runbook

**Owner:** Integration / Platform (doc 28 §4) · **Severity:** P2 for backlog growth,
P1 if it's blocking a large share of active workflows (doc 28 §9-10).

## Symptoms (doc 28 §65)

Backlog growth, processing failures, lock loss, duplicate messages, consumer
unavailable, DLQ growth.

## Diagnostic steps

1. Identify topic/subscription — `config/base/service-bus.yaml`'s `topic` section
   (each entry documents its own purpose — Phase 12's explicit requirement).
2. Check consumer health — `src/pff_fa_ai/messaging/service_bus/consumer.py` and
   `processing.py`'s `EventProcessingService` (validate → idempotency → route →
   execute → record). A stuck backlog is usually a slow or failing step in that chain,
   not the Service Bus service itself.
3. Check idempotency claims — `InMemoryEventIdempotencyStore.try_claim()`
   (`messaging/reliability/idempotency.py`) holds its lock across the full
   check-and-set, so duplicate-message symptoms point elsewhere (e.g. a genuinely
   duplicated enterprise event) rather than a race in this store.
4. Check the DLQ itself — `messaging/reliability/dead_letter.py`. For each DLQ'd
   message capture: message ID, event type, failure reason, schema/version
   (doc 28 §69).

## Recovery — DLQ replay (doc 28 §70-71)

Replay **only** after all of:

```text
Root cause corrected
Message still valid
Consumer healthy
Schema compatible
Idempotency confirmed
Authorization context still valid
```

Record: message ID, original failure, replay time, operator, reason, result (doc 28 §71).
Never replay a message just to clear a queue.

## Backlog recovery

Do not blindly increase consumer concurrency if the downstream dependency (enterprise
API, SLM) is itself saturated (doc 28 §67) — check `ResilienceRegistry`
(`observability/resilience.py`) for the relevant dependency's circuit state first.

## Escalation

Integration / Platform team, with topic, subscription, backlog depth, oldest message
age, and DLQ count.
