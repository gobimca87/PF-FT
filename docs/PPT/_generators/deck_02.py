#!/usr/bin/env python3
"""Deck 02 — Application & Orchestration Architecture (D2)."""
import os
from orion import (Deck, PP_ALIGN, MSO_SHAPE, WHITE, GREY, MUTED, CYAN, BLUE,
                   PURPLE, PINK, VIOLET, YELLOW, GREEN, PANEL, PANEL2)
from common import adrs_for, adr_index_slides, stat_cards, two_col, pipeline, kv_panel

OUT = os.path.join(os.path.dirname(__file__), "..", "02-application-orchestration.pptx")


def layer_diagram(d, s):
    layers = [("API", "FastAPI — thin boundary: validate → build context → invoke → return", CYAN),
              ("Application", "use-case orchestration — services, commands, queries, DTOs", BLUE),
              ("Orchestration", "Supervisor · LangGraph · Agent Harness", GREEN),
              ("Domain", "entities, value objects, state enums — no framework deps", PURPLE),
              ("Infrastructure / Integrations", "HTTP client, Azure SDK, providers, DB drivers", PINK)]
    y = 1.95; h = 0.82; w = 9.6; x = 0.9
    for i, (t, sub, col) in enumerate(layers):
        d.box(s, "", x, y, w, h, fill=PANEL2, line=col, line_w=1.2)
        d.text(s, t, x + 0.25, y + 0.11, 3.4, 0.6, size=17, color=col, bold=True)
        d.text(s, sub, x + 3.5, y + 0.14, w - 3.7, 0.6, size=12, color=GREY)
        if i < len(layers) - 1:
            d.connector(s, x + w + 0.35, y + h, x + w + 0.35, y + h + 0.18, color=MUTED, width=1)
        y += h + 0.2
    d.box(s, "Dependency\nrule:\ndownward\nonly", 10.75, 1.95, 1.55, 4.9, fill=PANEL,
          line=YELLOW, textcolor=YELLOW, size=13)


def harness_diagram(d, s):
    d.box(s, "", 0.6, 1.95, 12.1, 3.4, fill=PANEL, line=VIOLET, line_w=1.1)
    d.text(s, "AGENT HARNESS — the single execution boundary for every agent step",
           0.85, 2.05, 11.6, 0.35, size=13, color=VIOLET, bold=True)
    items = [("Validated\nclaims", CYAN), ("Prompt\n(composed)", BLUE), ("ERC\ncontext", GREEN),
             ("Memory /\ncache", PINK), ("Tools /\nMCP", YELLOW), ("RAG", PURPLE),
             ("Guardrails", PINK), ("Retry · timeout\nloop-limits", CYAN)]
    x = 0.9; w = 1.4; gap = 0.11; y = 2.6; h = 1.0
    for lab, col in items:
        d.box(s, lab, x, y, w, h, fill=PANEL2, line=col, size=10)
        x += w + gap
    d.text(s, "One place enforces claims, prompt composition, context, tool allow-listing, guardrails, "
              "and all reliability limits — agents cannot bypass it.",
           0.9, 3.85, 11.5, 0.9, size=13, color=GREY)
    d.box(s, "SLM (HF → vLLM)", 0.9, 4.55, 2.6, 0.55, fill=PANEL2, line=VIOLET, size=12)
    d.box(s, "Enterprise APIs / Events (system of record)", 3.7, 4.55, 5.2, 0.55,
          fill=PANEL2, line=BLUE, size=12)
    d.box(s, "Validated output", 9.1, 4.55, 3.5, 0.55, fill=PANEL2, line=GREEN, size=12)


def servicebus_diagram(d, s):
    pipeline(d, s, [("Producer", "workflow / enterprise"), ("Service Bus", "queue / topic"),
                    ("Consumer", "bounded concurrency"), ("Handler", "erc-refresh · hil · resume"),
                    ("Reconcile", "idempotent · dedup")], y=2.5, h=1.0,
             colors=[BLUE, CYAN, GREEN, PURPLE, PINK])
    d.box(s, "Dead-letter", 5.0, 4.0, 2.0, 0.55, fill=PANEL2, line=PINK, size=12)
    d.bullets(s, [
        "Versioned event envelope (D2-17); at-least-once delivery with idempotent handlers (D2-18).",
        "Reconciliation resolves uncertain transaction outcomes — never a silent guess.",
        "Consumer scaling respects enterprise-API and SLM limits (deck 05/07).",
    ], 0.9, 4.9, 11.5, 1.7, size=14, gap=11)


def build():
    d = Deck()
    d.title_slide("02 · Application & Orchestration",
                  "Layering · runtime · Supervisor · LangGraph · Agent Harness · integration · eventing  (D2, 21 ADRs)",
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

    s = d.content_slide("Layered architecture & dependency rule", "D2-01 · enforced, not conventional")
    layer_diagram(d, s)
    s.notes_slide.notes_text_frame.text = ("API → Application → Orchestration → Domain → "
        "Infrastructure. Dependencies point downward only. Domain code never imports FastAPI, "
        "Azure SDK, provider SDKs or DB drivers — this keeps business logic pure and testable.")

    s = d.content_slide("One runtime · logical agents · dual runtime", "D2-02 / D2-03")
    two_col(d, s,
            "Single runtime", [
                "One LangGraph process hosts all agents as logical capabilities.",
                "No microservice-per-agent unless a justified scaling reason exists.",
                "Shared harness, config, observability, guardrails.",
            ],
            "Dual runtime", [
                "Request-driven: synchronous chat/workflow path.",
                "Event-driven: Service Bus consumers for refresh, resume, HIL.",
                "Both share the same domain and integration layers.",
            ])
    s.notes_slide.notes_text_frame.text = ("Agents are capabilities, not deployables. Two runtimes "
        "— request and event — over one codebase.")

    s = d.content_slide("Conversation Manager & Supervisor", "D2-04 / D2-05")
    pipeline(d, s, [("Conversation\nManager", "turns · session"), ("Supervisor", "intent → candidates"),
                    ("LangGraph", "route to agent"), ("Agent", "AffiliationAgent")],
             y=2.6, h=1.0, colors=[CYAN, YELLOW, GREEN, PURPLE])
    d.bullets(s, [
        "Conversation Manager owns conversation/session boundaries — not business logic.",
        "Supervisor classifies intent and selects candidate agents; routing is bounded to avoid loops.",
        "Deterministic routing where possible; model-decided only where justified (see deck 03).",
    ], 0.9, 4.2, 11.5, 1.9, size=14, gap=11)
    s.notes_slide.notes_text_frame.text = ("The Conversation Manager is a responsibility boundary; "
        "the Supervisor is the intent router. Both avoid unbounded loops (D2-11).")

    s = d.content_slide("LangGraph orchestration & state", "D2-06 / D2-07")
    two_col(d, s,
            "Engine", [
                "LangGraph is the workflow orchestration engine.",
                "Nodes = steps; edges = transitions; supports parallel branches & aggregation.",
                "Bounded steps, iterations, tool/model calls (deck 08 budgets).",
            ],
            "State typing", [
                "Graph internal state = TypedDict.",
                "Every boundary (API/tool/config/event/ERC/SLM) = Pydantic.",
                "Four state concepts kept strictly separate.",
            ])
    s.notes_slide.notes_text_frame.text = ("LangGraph gives explicit, inspectable orchestration. "
        "TypedDict for internal graph state; Pydantic at every data boundary.")

    s = d.content_slide("Agent Harness — single execution boundary", "D2-09 · nothing bypasses it")
    harness_diagram(d, s)
    s.notes_slide.notes_text_frame.text = ("The Harness is where claims, prompt composition, ERC, "
        "memory/cache, tools/MCP, RAG, guardrails and reliability limits are enforced for every agent "
        "step. Centralising this is what makes the Golden Rule enforceable in code.")

    s = d.content_slide("Execution model & reliability limits", "D2-08 / D2-11")
    stat_cards(d, s, [
        ("Bounded\nparallelism", "independent branches only", CYAN),
        ("Idempotency", "safe retries, no double-execute", GREEN),
        ("Timeouts", "per dependency & per workflow", YELLOW),
        ("Loop limits", "max steps / iterations / calls", PINK),
    ], y=2.1, h=2.0)
    d.bullets(s, [
        "Parallelise only with no data/ordering/transaction dependency and within rate limits.",
        "Retry budgets are part of capacity planning — retry amplification is designed out (deck 08).",
    ], 0.9, 4.5, 11.5, 1.7, size=15, gap=12)
    s.notes_slide.notes_text_frame.text = ("Bounded everything: parallelism, retries, timeouts, loops. "
        "Idempotency keys make retries safe against the enterprise.")

    s = d.content_slide("Long-running workflows & HIL resume", "D2-10")
    d.bullets(s, [
        "Workflows can suspend at a human-in-the-loop point (user confirm, CFA review, payment) and resume later on an event.",
        "Workflow/agent state is checkpointed with optimistic concurrency (id + version + expected_version).",
        "A resume event re-hydrates state and continues from the exact step — no re-execution of completed side-effects.",
        "Adam communicates who/what the workflow is waiting for throughout the pending state.",
    ], 0.9, 2.0, 11.5, 4.0, size=16, gap=15)
    s.notes_slide.notes_text_frame.text = ("Affiliation can wait days for CFA review. State is "
        "checkpointed and resumed on a Service Bus event; completed side-effects are never replayed.")

    s = d.content_slide("Enterprise integration", "D2-13 / D2-14 / D2-15 / D2-20 / D2-21")
    two_col(d, s,
            "Pattern & coupling", [
                "Catalog-driven enterprise API clients; typed contracts.",
                "Integration matrix defines allowed couplings — no ad-hoc calls.",
                "Contract & envelope versioning; backward-compatible evolution.",
            ],
            "Resolution & binding", [
                "Endpoint & environment resolution per stage (D2-20).",
                "Request payload parameters sourced & bound explicitly (D2-21).",
                "Shared HTTP client: pooling, timeout, retry, tracing.",
            ])
    s.notes_slide.notes_text_frame.text = ("Integration is catalog- and contract-driven, versioned, "
        "with explicit endpoint resolution and payload binding — no hidden coupling.")

    s = d.content_slide("Asynchronous eventing — Service Bus", "D2-16 / D2-17 / D2-18")
    servicebus_diagram(d, s)
    s.notes_slide.notes_text_frame.text = ("Azure Service Bus carries ERC-refresh, workflow-resume "
        "and HIL events. Versioned envelopes, at-least-once delivery, idempotent handlers, dead-letter "
        "and reconciliation. This is how uncertain outcomes are resolved deterministically.")

    s = d.content_slide("Portal links — no invented URLs", "D2-19")
    d.bullets(s, [
        "Every portal link is resolved through a registered portal-link mechanism — Adam never invents a URL.",
        "Links are registry-driven, validated, scoped and (where needed) signed/expiring.",
        "Deck 03/06 cover the same principle for IDs, tool results and technical details.",
    ], 0.9, 2.0, 11.5, 3.2, size=16, gap=15)
    s.notes_slide.notes_text_frame.text = ("No-invented-URLs is a concrete anti-hallucination "
        "control: links come only from the registry. Full portal-link design is in the info/security decks.")

    adr_index_slides(d, "ADR index — Application (D2)", adrs_for(2),
                     notes="All 21 application-architecture ADRs — layering, runtime, orchestration, "
                           "integration and eventing. None open in this domain.")

    d.final_slide("Application architecture — summary",
                  "Strict layering · one bounded runtime · a harness nothing bypasses · versioned integration & events",
                  notes="Takeaway: structure and bounded execution make the Golden Rule enforceable "
                        "and the system observable and reliable.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
