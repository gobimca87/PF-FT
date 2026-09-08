#!/usr/bin/env python3
"""Deck 07 — Operations, Observability & Quality (D7)."""
import os
from orion import (Deck, PP_ALIGN, MSO_SHAPE, WHITE, GREY, MUTED, CYAN, BLUE,
                   PURPLE, PINK, VIOLET, YELLOW, GREEN, PANEL, PANEL2)
from common import adrs_for, adr_index_slides, stat_cards, two_col, pipeline, kv_panel

OUT = os.path.join(os.path.dirname(__file__), "..", "07-operations-quality.pptx")


def observability_diagram(d, s):
    d.box(s, "PFF AI runtime\n(correlation ID on every request)", 0.7, 3.0, 3.0, 1.1,
          fill=PANEL2, line=CYAN, size=12)
    outs = [("langfuse", "Langfuse\ntraces · prompts · tokens · cost", PINK, 2.0),
            ("appinsights", "App Insights\nmetrics · APM", BLUE, 3.15),
            ("loganalytics", "Log Analytics\nlogs (redacted)", GREEN, 4.3)]
    for logo, label, col, y in outs:
        d.box(s, "", 4.5, y, 4.0, 0.95, fill=PANEL2, line=col, line_w=1.0)
        d.image(s, logo, 4.62, y + 0.22, h=0.5)
        d.text(s, label, 5.25, y + 0.16, 3.1, 0.7, size=11, color=WHITE, bold=True, anchor=1)
        d.connector(s, 3.7, 3.55, 4.5, y + 0.47, color=col, width=1.3)
    d.box(s, "Dashboards\n· Alerts\n· SLO/error budget", 9.0, 3.0, 3.3, 1.4,
          fill=PANEL, line=YELLOW, size=12)
    for y in (2.0, 3.15, 4.3):
        d.connector(s, 8.5, y + 0.47, 9.0, 3.7, color=GREY, width=1.0, arrow=(y == 3.15))
    d.text(s, "AI-specific observability (Langfuse) sits alongside platform observability (Azure "
              "Monitor / App Insights / Log Analytics). One correlation ID threads conversation → "
              "workflow → enterprise call.", 0.7, 5.6, 11.9, 0.9, size=13, color=GREY)


def error_hierarchy(d, s):
    d.box(s, "PlatformError", 5.2, 1.95, 3.0, 0.7, fill=PANEL, line=YELLOW,
          textcolor=YELLOW, size=16)
    subs = ["ValidationError", "ConfigurationError", "IntegrationError", "ToolError",
            "ModelError", "RAGError", "GuardrailError", "WorkflowError"]
    cols = [CYAN, BLUE, GREEN, PURPLE, VIOLET, PINK, CYAN, BLUE]
    x = 0.7; y = 3.4; w = 2.9; gap = 0.15
    for i, (sub, col) in enumerate(zip(subs, cols)):
        cx = x + (i % 4) * (w + gap)
        cy = y + (i // 4) * 1.0
        d.box(s, sub, cx, cy, w, 0.7, fill=PANEL2, line=col, size=12)
        d.connector(s, 6.7, 2.65, cx + w/2, cy, color=MUTED, width=0.75)
    d.text(s, "Every failure maps to one typed error — uniform handling, logging and user messaging.",
           0.7, 5.7, 11.9, 0.5, size=13, color=GREY)


def build():
    d = Deck()
    d.title_slide("07 · Operations, Observability & Quality",
                  "Langfuse · SLI/SLO · CI/CD · testing · LLMOps · DR  (D7, 18 ADRs)",
                  notes="How the platform is run, observed, tested and evolved safely. Covers docs 21 "
                        "(evaluation), 22 (testing), 23 (engineering agents), 24 (observability/resilience), "
                        "27 (dev standards), 28 (ops runbook). 18 ADRs in D7.")

    d.agenda_slide("What this deck covers", [
        "Platform + AI observability (Langfuse)",
        "Correlation IDs, tracing & logging/redaction",
        "Error taxonomy — the PlatformError hierarchy",
        "Resilience patterns",
        "SLI/SLO, error budget & alerting",
        "CI/CD pipelines, quality gates & deployment strategy",
        "Branching, versioning & the release train",
        "AI engineering lifecycle (LLMOps)",
        "Evaluation & regression gates; the test pyramid",
        "Engineering agents; support, incidents & DR",
    ])

    s = d.content_slide("Observability — platform + AI", "D7-01 / D7-02")
    observability_diagram(d, s)
    s.notes_slide.notes_text_frame.text = ("Two complementary layers: platform observability (Azure "
        "Monitor / App Insights / Log Analytics) and AI-specific observability (Langfuse: traces, "
        "prompts, tokens, cost). Langfuse is also the source for AI cost telemetry in deck 08.")

    s = d.content_slide("Correlation, tracing & logging", "D7-03 / D7-04")
    two_col(d, s,
            "Correlation & trace propagation", [
                "One correlation ID per request, propagated through async/event paths.",
                "Traces link conversation → workflow → tool → enterprise call.",
            ],
            "Logging standards & redaction", [
                "Structured logs with consistent fields.",
                "Redaction by data classification (deck 06) — no PII in logs.",
                "Excessive logging is a cost anti-pattern (deck 08).",
            ])
    s.notes_slide.notes_text_frame.text = ("Correlation IDs make the whole distributed flow traceable; "
        "logs are structured and redacted by classification.")

    s = d.content_slide("Error taxonomy", "D7-05 · one root, typed subclasses")
    error_hierarchy(d, s)
    s.notes_slide.notes_text_frame.text = ("A single PlatformError root with typed subclasses gives "
        "uniform error handling, logging and user messaging across the whole platform.")

    s = d.content_slide("Resilience patterns", "D7-06")
    stat_cards(d, s, [
        ("Retry", "bounded, idempotent", CYAN),
        ("Timeout", "per dependency & workflow", YELLOW),
        ("Circuit breaker", "protect downstream", PINK),
        ("Backpressure", "bounded queues", GREEN),
    ], y=2.1, h=2.0)
    d.bullets(s, [
        "Failure is expected and handled: retry with budgets, timeouts, circuit-breaking, bounded queues.",
        "Reconciliation resolves uncertain transaction outcomes (deck 02) — never a silent guess.",
    ], 0.9, 4.5, 11.5, 1.7, size=15, gap=12)
    s.notes_slide.notes_text_frame.text = ("Resilience is designed in: bounded retries, timeouts, "
        "circuit breakers, backpressure — feeding capacity and cost planning.")

    s = d.content_slide("SLI/SLO, error budget & alerting", "D7-07 / D7-08")
    two_col(d, s,
            "SLI / SLO / error budget", [
                "Service-level indicators & objectives per critical path.",
                "Error budgets govern change pace.",
                "Latency SLOs use p95/p99 (deck 05/08).",
            ],
            "Alerting & escalation", [
                "Severity-tiered alerts with clear escalation.",
                "Cost & anomaly alerts included (deck 08).",
                "Ties into the incident process.",
            ])
    s.notes_slide.notes_text_frame.text = ("SLIs/SLOs and error budgets make reliability measurable "
        "and govern how fast we change; alerts are severity-tiered with defined escalation.")

    s = d.content_slide("CI/CD & deployment strategy", "D7-09 / D7-10")
    pipeline(d, s, [("Build", "lint · type · test"), ("Quality gate", "SonarQube"),
                    ("Package", "immutable bundle"), ("Deploy", "rolling / canary / blue-green")],
             y=2.6, h=1.0, colors=[CYAN, YELLOW, BLUE, GREEN])
    d.bullets(s, [
        "Runs on the enterprise Azure DevOps build.yaml / release.yaml (deck 05).",
        "Deployment: rolling by default; canary for AI-artifact changes; blue/green for GPU/index cutover (D7-10, Accepted).",
    ], 0.9, 4.2, 11.5, 1.8, size=14, gap=12)
    s.notes_slide.notes_text_frame.text = ("CI enforces lint/type/test and the SonarQube gate; CD uses "
        "rolling by default, canary for AI-artifact changes, blue/green for GPU or index cutovers.")

    s = d.content_slide("Branching, versioning & release train", "D7-11")
    d.bullets(s, [
        "Branch model: main / develop / feature/* / bugfix/* / hotfix/* / release/*.",
        "Conventional commits; semantic versioning MAJOR.MINOR.PATCH.",
        "A release train coordinates code + AI-artifact bundles (prompts, models, RAG indexes, guardrails).",
    ], 0.9, 2.0, 11.5, 3.2, size=16, gap=15)
    s.notes_slide.notes_text_frame.text = ("A disciplined branch/versioning model and a release train "
        "that versions code and AI artifacts together as immutable bundles.")

    s = d.content_slide("AI engineering lifecycle (LLMOps)", "D7-12")
    pipeline(d, s, [("Author", "prompts · agents"), ("Evaluate", "golden datasets"),
                    ("Promote", "immutable bundle"), ("Observe", "Langfuse"),
                    ("Improve", "data-driven")], y=2.6, h=1.0,
             colors=[CYAN, YELLOW, BLUE, PINK, GREEN])
    d.text(s, "AI artifacts follow a full lifecycle — authored, evaluated, promoted, observed and "
              "improved — never mutated in place in production.",
           0.9, 4.3, 11.5, 0.9, size=14, color=GREY)
    s.notes_slide.notes_text_frame.text = ("LLMOps: prompts/agents/models/indexes are authored, "
        "evaluated against golden datasets, promoted as bundles, observed in Langfuse, and improved "
        "from production telemetry.")

    s = d.content_slide("Evaluation & regression gates", "D7-13 · doc 21")
    d.bullets(s, [
        "Golden datasets + evaluators + LLM-as-judge score quality before release.",
        "Regression gates block a release that degrades quality, groundedness or safety.",
        "Distinct from the runtime refinement loop (D3-28): these are offline release gates.",
        "Evaluation adds model usage — its cost is tracked (deck 08).",
    ], 0.9, 2.0, 11.5, 3.8, size=16, gap=14)
    s.notes_slide.notes_text_frame.text = ("Offline evaluation with golden datasets and LLM-as-judge, "
        "gating releases on quality/groundedness/safety regressions. Not the same as runtime refinement.")

    s = d.content_slide("Test strategy & pyramid", "D7-14 · doc 22")
    d.bullets(s, [
        "A broad test pyramid: unit · component · api · contract · integration · agents · supervisor · harness · workflows.",
        "AI-specific layers: rag · embeddings · vector · slm · prompts · guardrails · adversarial.",
        "Plus security, performance, resilience, regression and e2e — with golden datasets.",
    ], 0.9, 2.0, 11.5, 3.4, size=16, gap=15)
    s.notes_slide.notes_text_frame.text = ("Testing spans classic layers and AI-specific layers "
        "(RAG, embeddings, vector, SLM, prompts, guardrails, adversarial) plus security/perf/resilience/"
        "regression/e2e.")

    s = d.content_slide("Engineering agents", "D7-15 · doc 23")
    d.bullets(s, [
        "AI agents assist engineering: code review, security analysis, test generation, evaluation, docs.",
        "Scope & guardrails are explicit — they assist, they do not bypass human review or release gates.",
        "Their model usage/CI cost is tracked as a cost category (deck 08).",
    ], 0.9, 2.0, 11.5, 3.2, size=16, gap=15)
    s.notes_slide.notes_text_frame.text = ("Engineering agents accelerate the team within explicit "
        "guardrails — they never replace human review or release gates.")

    s = d.content_slide("Support, incidents & continuity", "D7-16 / D7-17 / D7-18 · doc 28")
    two_col(d, s,
            "Support & incidents", [
                "Defined operational support model.",
                "Incident process: detect → correlate → mitigate → recover → learn.",
                "Performance & cost incidents have runbooks (deck 08).",
            ],
            "DR & continuity", [
                "Disaster recovery & business continuity plans.",
                "State (Redis) and artifacts (bundles) recoverable.",
                "Regular capacity & cost reviews.",
            ])
    s.notes_slide.notes_text_frame.text = ("A clear support model, an incident process with runbooks, "
        "and DR/continuity plans covering state and artifact recovery.")

    adr_index_slides(d, "ADR index — Operations (D7)", adrs_for(7),
                     notes="All 18 operations ADRs — observability, resilience, SLO, CI/CD, LLMOps, "
                           "testing, engineering agents, incident and DR. None open in this domain.")

    d.final_slide("Operations & quality — summary",
                  "Observed (Langfuse + Azure) · typed failures · gated releases · evaluated AI · DR-ready",
                  notes="Takeaway: the platform is observable, resilient, release-gated and continuously "
                        "evaluated — safe to operate and safe to change.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
