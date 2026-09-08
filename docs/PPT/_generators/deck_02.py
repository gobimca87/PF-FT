#!/usr/bin/env python3
"""Deck 02 — Application & Orchestration (D2), FA light theme."""
import os
from fa import (Deck, adrs_for, PP_ALIGN, MSO_SHAPE, MSO_ANCHOR,
                NAVY, NAVY_DEEP, BLUE, GOLD, GREY, WHITE, MUTEDBLUE, CARD, CARD_LINE,
                CX0, CX1, CW)

OUT = os.path.join(os.path.dirname(__file__), "..", "02-application-orchestration.pptx")


def layer_diagram(d, s):
    layers = [("API", "FastAPI — thin boundary: validate → build context → invoke → return"),
              ("Application", "use-case orchestration — services, commands, queries, DTOs"),
              ("Orchestration", "Supervisor · LangGraph · Agent Harness"),
              ("Domain", "entities, value objects, state enums — no framework deps"),
              ("Infrastructure", "HTTP client, Azure SDK, providers, DB drivers")]
    y = 1.95; h = 0.82; w = 8.7; x = CX0
    for i, (t, sub) in enumerate(layers):
        d.card(s, x, y, w, h)
        d._rect(s, x, y, 0.12, h, BLUE)
        d.text(s, t, x + 0.3, y + 0.1, 3.2, 0.6, size=16, color=NAVY, bold=True, font="Cambria")
        d.text(s, sub, x + 3.4, y + 0.14, w - 3.6, 0.6, size=11.5, color=GREY)
        y += h + 0.18
    d.box(s, "Dependency\nrule:\ndownward\nonly", 11.0, 1.95, 1.7, 4.82, style="navy", size=13)


def harness_diagram(d, s):
    d.card(s, CX0, 1.95, CW, 3.35)
    d.text(s, "AGENT HARNESS — the single execution boundary for every agent step",
           CX0 + 0.25, 2.05, CW - 0.5, 0.35, size=13, color=BLUE, bold=True)
    items = ["Validated\nclaims", "Prompt\n(composed)", "ERC\ncontext", "Memory /\ncache",
             "Tools /\nMCP", "RAG", "Guardrails", "Retry · timeout\nloop-limits"]
    x = CX0 + 0.2; w = 1.25; gap = 0.1; y = 2.55; h = 1.0
    for lab in items:
        d.box(s, lab, x, y, w, h, style="light", size=9.5)
        x += w + gap
    d.text(s, "One place enforces claims, prompt composition, context, tool allow-listing, guardrails "
              "and all reliability limits — agents cannot bypass it.",
           CX0 + 0.25, 3.75, CW - 0.5, 0.6, size=12.5, color=GREY)
    d.box(s, "SLM (HF → vLLM)", CX0 + 0.2, 4.5, 2.6, 0.55, style="light", size=11)
    d.box(s, "Enterprise APIs / Events (system of record)", CX0 + 2.95, 4.5, 5.0, 0.55,
          style="navy", size=11)
    d.box(s, "Validated output", CX0 + 8.15, 4.5, 2.45, 0.55, style="accent", size=11)


def build():
    d = Deck()
    d.title_slide("Application &", "Orchestration",
                  "Layering · runtime · Supervisor · LangGraph · Agent Harness · integration · eventing  —  D2 (21 ADRs)",
                  kicker="Deck 02 · Application architecture",
                  notes="How the platform is structured and how a request becomes an orchestrated, "
                        "bounded, observable execution. 21 ADRs in D2.")

    d.agenda_slide("What this deck covers", [
        "Layered architecture & the dependency rule",
        "One runtime; agents as logical capabilities; dual runtime",
        "Conversation Manager & Supervisor intent routing",
        "LangGraph orchestration & graph state",
        "Agent Harness — the single execution boundary",
        "Execution model, bounded parallelism & reliability limits",
        "Long-running workflows & HIL resume",
        "Enterprise integration pattern, contracts & binding",
        "Asynchronous eventing — Azure Service Bus",
        "Portal-link registry — no invented URLs",
    ])

    s = d.content_slide("Layered architecture & dependency rule", kicker="D2-01",
                        subtitle="Enforced, not conventional")
    layer_diagram(d, s)
    d.set_notes(s, "API → Application → Orchestration → Domain → Infrastructure. Dependencies point "
                   "downward only; domain code never imports FastAPI, Azure SDK, provider SDKs or DB drivers.")

    s = d.content_slide("One runtime · logical agents · dual runtime", kicker="D2-02 / D2-03")
    d.two_col(s, "Single runtime", [
        "One LangGraph process hosts all agents as logical capabilities.",
        "No microservice-per-agent unless a justified scaling reason exists.",
        "Shared harness, config, observability, guardrails.",
    ], "Dual runtime", [
        "Request-driven: synchronous chat/workflow path.",
        "Event-driven: Service Bus consumers for refresh, resume, HIL.",
        "Both share the same domain and integration layers.",
    ])
    d.set_notes(s, "Agents are capabilities, not deployables. Two runtimes — request and event — over one codebase.")

    s = d.content_slide("Conversation Manager & Supervisor", kicker="D2-04 / D2-05")
    d.pipeline(s, [("Conversation\nManager", "turns · session"), ("Supervisor", "intent → candidates"),
                   ("LangGraph", "route to agent"), ("Agent", "AffiliationAgent")],
               y=2.7, h=1.05)
    d.bullets(s, [
        "Conversation Manager owns conversation/session boundaries — not business logic.",
        "Supervisor classifies intent and selects candidate agents; routing is bounded to avoid loops.",
        "Deterministic routing where possible; model-decided only where justified (deck 03).",
    ], CX0, 4.3, CW, 1.9, size=14, gap=11)
    d.set_notes(s, "The Conversation Manager is a responsibility boundary; the Supervisor is the intent router.")

    s = d.content_slide("LangGraph orchestration & state", kicker="D2-06 / D2-07")
    d.two_col(s, "Engine", [
        "LangGraph is the workflow orchestration engine.",
        "Nodes = steps; edges = transitions; parallel branches & aggregation.",
        "Bounded steps, iterations, tool/model calls (deck 08 budgets).",
    ], "State typing", [
        "Graph internal state = TypedDict.",
        "Every boundary (API/tool/config/event/ERC/SLM) = Pydantic.",
        "Four state concepts kept strictly separate.",
    ])
    d.set_notes(s, "LangGraph gives explicit, inspectable orchestration; TypedDict internally, Pydantic at boundaries.")

    s = d.content_slide("Agent Harness — single execution boundary", kicker="D2-09",
                        subtitle="Nothing bypasses it")
    harness_diagram(d, s)
    d.set_notes(s, "The Harness enforces claims, prompt composition, ERC, memory/cache, tools/MCP, RAG, "
                   "guardrails and reliability limits for every agent step — what makes the Golden Rule enforceable in code.")

    s = d.content_slide("Execution model & reliability limits", kicker="D2-08 / D2-11")
    d.stat_cards(s, [("Bounded\nparallelism", "independent branches only"),
                     ("Idempotency", "safe retries, no double-execute"),
                     ("Timeouts", "per dependency & workflow"),
                     ("Loop limits", "max steps / iterations / calls")], y=2.1, h=1.9)
    d.bullets(s, [
        "Parallelise only with no data/ordering/transaction dependency and within rate limits.",
        "Retry budgets are part of capacity planning — retry amplification is designed out (deck 08).",
    ], CX0, 4.4, CW, 1.7, size=14, gap=12)
    d.set_notes(s, "Bounded everything: parallelism, retries, timeouts, loops; idempotency keys make retries safe.")

    s = d.content_slide("Long-running workflows & HIL resume", kicker="D2-10")
    d.bullets(s, [
        "Workflows can suspend at a human-in-the-loop point (user confirm, CFA review, payment) and resume later on an event.",
        "Workflow/agent state is checkpointed with optimistic concurrency (id + version + expected_version).",
        "A resume event re-hydrates state and continues from the exact step — no re-execution of completed side-effects.",
        "Adam communicates who/what the workflow is waiting for throughout the pending state.",
    ], CX0, 1.95, CW, 4.0, size=16, gap=15)
    d.set_notes(s, "Affiliation can wait days for CFA review; state is checkpointed and resumed on an event.")

    s = d.content_slide("Enterprise integration", kicker="D2-13/14/15/20/21")
    d.two_col(s, "Pattern & coupling", [
        "Catalog-driven enterprise API clients; typed contracts.",
        "Integration matrix defines allowed couplings — no ad-hoc calls.",
        "Contract & envelope versioning; backward-compatible evolution.",
    ], "Resolution & binding", [
        "Endpoint & environment resolution per stage (D2-20).",
        "Request payload parameters sourced & bound explicitly (D2-21).",
        "Shared HTTP client: pooling, timeout, retry, tracing.",
    ])
    d.set_notes(s, "Integration is catalog- and contract-driven, versioned, with explicit endpoint "
                   "resolution and payload binding — no hidden coupling.")

    s = d.content_slide("Asynchronous eventing — Service Bus", kicker="D2-16 / D2-17 / D2-18")
    d.pipeline(s, [("Producer", "workflow / enterprise"), ("Service Bus", "queue / topic"),
                   ("Consumer", "bounded concurrency"), ("Handler", "erc-refresh · hil · resume"),
                   ("Reconcile", "idempotent · dedup")], y=2.5, h=1.05)
    d.bullets(s, [
        "Versioned event envelope (D2-17); at-least-once delivery with idempotent handlers (D2-18).",
        "Reconciliation resolves uncertain transaction outcomes — never a silent guess. Dead-letter for the rest.",
        "Consumer scaling respects enterprise-API and SLM limits (deck 05/07).",
    ], CX0, 4.2, CW, 1.8, size=14, gap=11)
    d.set_notes(s, "Service Bus carries ERC-refresh, workflow-resume and HIL events with versioned "
                   "envelopes, idempotent handlers, dead-letter and reconciliation.")

    s = d.content_slide("Portal links — no invented URLs", kicker="D2-19")
    d.bullets(s, [
        "Every portal link is resolved through a registered portal-link mechanism — Adam never invents a URL.",
        "Links are registry-driven, validated, scoped and (where needed) signed/expiring.",
        "Deck 03/06 cover the same principle for IDs, tool results and technical details.",
    ], CX0, 1.95, CW, 3.2, size=16, gap=15)
    d.set_notes(s, "No-invented-URLs is a concrete anti-hallucination control: links come only from the registry.")

    d.adr_index_slides("ADR index — Application (D2)", adrs_for(2),
                       notes="All 21 application-architecture ADRs — layering, runtime, orchestration, "
                             "integration and eventing. None open in this domain.")

    d.final_slide("Application architecture — summary",
                  "Strict layering · one bounded runtime · a harness nothing bypasses · versioned integration & events",
                  notes="Structure and bounded execution make the Golden Rule enforceable and the system "
                        "observable and reliable.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
