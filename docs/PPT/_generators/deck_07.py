#!/usr/bin/env python3
"""Deck 07 — Operations, Observability & Quality (D7), FA light theme."""
import os
from fa import (Deck, adrs_for, PP_ALIGN, MSO_SHAPE, MSO_ANCHOR,
                NAVY, NAVY_DEEP, BLUE, GOLD, GREY, WHITE, MUTEDBLUE, CARD, CARD_LINE,
                CX0, CX1, CW)

OUT = os.path.join(os.path.dirname(__file__), "..", "07-operations-quality.pptx")


def observability_diagram(d, s):
    d.box(s, "PFF AI runtime\n(correlation ID on every request)", CX0, 3.0, 3.0, 1.1,
          style="navy", size=12)
    outs = [("langfuse", "Langfuse — traces · prompts · tokens · cost", 2.0),
            ("appinsights", "App Insights — metrics · APM", 3.15),
            ("loganalytics", "Log Analytics — logs (redacted)", 4.3)]
    for logo, label, y in outs:
        d.card(s, CX0 + 3.6, y, 4.4, 0.95)
        d.image(s, logo, CX0 + 3.72, y + 0.24, h=0.48)
        d.text(s, label, CX0 + 4.35, y + 0.16, 3.5, 0.7, size=11, color=NAVY, bold=True,
               anchor=MSO_ANCHOR.MIDDLE)
        d.connector(s, CX0 + 3.0, 3.55, CX0 + 3.6, y + 0.47, color=BLUE, width=1.2)
    d.box(s, "Dashboards\n· Alerts\n· SLO / error budget", CX0 + 8.2, 3.0, 2.45, 1.4,
          style="light", size=12)
    for y in (2.0, 3.15, 4.3):
        d.connector(s, CX0 + 8.0, y + 0.47, CX0 + 8.2, 3.7, color=BLUE, width=1.0, arrow=(y == 3.15))
    d.text(s, "AI-specific observability (Langfuse) sits alongside platform observability (Azure "
              "Monitor / App Insights / Log Analytics). One correlation ID threads conversation → "
              "workflow → enterprise call.", CX0, 5.6, CW, 0.9, size=13, color=GREY)


def error_hierarchy(d, s):
    d.box(s, "PlatformError", CX0 + 3.9, 1.95, 3.0, 0.7, style="navy", size=16)
    subs = ["ValidationError", "ConfigurationError", "IntegrationError", "ToolError",
            "ModelError", "RAGError", "GuardrailError", "WorkflowError"]
    x0 = CX0; y0 = 3.4; w = 2.5; gap = 0.28
    for i, sub in enumerate(subs):
        cx = x0 + (i % 4) * (w + gap)
        cy = y0 + (i // 4) * 1.05
        d.box(s, sub, cx, cy, w, 0.7, style="light", size=12)
        d.connector(s, CX0 + 5.4, 2.65, cx + w / 2, cy, color=MUTEDBLUE, width=0.75, arrow=False)
    d.text(s, "Every failure maps to one typed error — uniform handling, logging and user messaging.",
           CX0, 5.6, CW, 0.5, size=13, color=GREY)


def build():
    d = Deck()
    d.title_slide("Operations, Observability", "& Quality",
                  "Langfuse · SLI/SLO · CI/CD · testing · LLMOps · DR  —  D7 (18 ADRs)",
                  kicker="Deck 07 · Operations",
                  notes="How the platform is run, observed, tested and evolved safely. Covers docs 21 "
                        "(evaluation), 22 (testing), 23 (engineering agents), 24 (observability/"
                        "resilience), 27 (dev standards), 28 (ops runbook). 18 ADRs.")

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

    s = d.content_slide("Observability — platform + AI", kicker="D7-01 / D7-02")
    observability_diagram(d, s)
    d.set_notes(s, "Two complementary layers: platform observability (Azure Monitor / App Insights / "
                   "Log Analytics) and AI-specific observability (Langfuse: traces, prompts, tokens, "
                   "cost). Langfuse is also the source for AI cost telemetry in deck 08.")

    s = d.content_slide("Correlation, tracing & logging", kicker="D7-03 / D7-04")
    d.two_col(s, "Correlation & trace propagation", [
        "One correlation ID per request, propagated through async/event paths.",
        "Traces link conversation → workflow → tool → enterprise call.",
    ], "Logging standards & redaction", [
        "Structured logs with consistent fields.",
        "Redaction by data classification (deck 06) — no PII in logs.",
        "Excessive logging is a cost anti-pattern (deck 08).",
    ])
    d.set_notes(s, "Correlation IDs make the whole distributed flow traceable; logs are structured and "
                   "redacted by classification.")

    s = d.content_slide("Error taxonomy", kicker="D7-05",
                        subtitle="One root, typed subclasses")
    error_hierarchy(d, s)
    d.set_notes(s, "A single PlatformError root with typed subclasses gives uniform error handling, "
                   "logging and user messaging across the platform.")

    s = d.content_slide("Resilience patterns", kicker="D7-06")
    d.stat_cards(s, [("Retry", "bounded, idempotent"), ("Timeout", "per dependency & workflow"),
                     ("Circuit breaker", "protect downstream"), ("Backpressure", "bounded queues")],
                 y=2.1, h=1.9)
    d.bullets(s, [
        "Failure is expected and handled: retry with budgets, timeouts, circuit-breaking, bounded queues.",
        "Reconciliation resolves uncertain transaction outcomes (deck 02) — never a silent guess.",
    ], CX0, 4.4, CW, 1.7, size=14, gap=12)
    d.set_notes(s, "Resilience is designed in: bounded retries, timeouts, circuit breakers, backpressure.")

    s = d.content_slide("SLI/SLO, error budget & alerting", kicker="D7-07 / D7-08")
    d.two_col(s, "SLI / SLO / error budget", [
        "Service-level indicators & objectives per critical path.",
        "Error budgets govern change pace.",
        "Latency SLOs use p95/p99 (deck 05/08).",
    ], "Alerting & escalation", [
        "Severity-tiered alerts with clear escalation.",
        "Cost & anomaly alerts included (deck 08).",
        "Ties into the incident process.",
    ])
    d.set_notes(s, "SLIs/SLOs and error budgets make reliability measurable and govern change pace; "
                   "alerts are severity-tiered with defined escalation.")

    s = d.content_slide("CI/CD & deployment strategy", kicker="D7-09 / D7-10")
    d.pipeline(s, [("Build", "lint · type · test"), ("Quality gate", "SonarQube"),
                   ("Package", "immutable bundle"), ("Deploy", "rolling / canary / blue-green")],
               y=2.7, h=1.05)
    d.bullets(s, [
        "Runs on the enterprise Azure DevOps build.yaml / release.yaml (deck 05).",
        "Deployment: rolling by default; canary for AI-artifact changes; blue/green for GPU/index cutover (D7-10, Accepted).",
    ], CX0, 4.3, CW, 1.7, size=14, gap=12)
    d.set_notes(s, "CI enforces lint/type/test and the SonarQube gate; CD uses rolling by default, "
                   "canary for AI-artifact changes, blue/green for GPU or index cutovers.")

    s = d.content_slide("Branching, versioning & release train", kicker="D7-11")
    d.bullets(s, [
        "Branch model: main / develop / feature/* / bugfix/* / hotfix/* / release/*.",
        "Conventional commits; semantic versioning MAJOR.MINOR.PATCH.",
        "A release train coordinates code + AI-artifact bundles (prompts, models, RAG indexes, guardrails).",
    ], CX0, 1.95, CW, 3.2, size=16, gap=15)
    d.set_notes(s, "A disciplined branch/versioning model and a release train that versions code and AI "
                   "artifacts together as immutable bundles.")

    s = d.content_slide("AI engineering lifecycle (LLMOps)", kicker="D7-12")
    d.pipeline(s, [("Author", "prompts · agents"), ("Evaluate", "golden datasets"),
                   ("Promote", "immutable bundle"), ("Observe", "Langfuse"), ("Improve", "data-driven")],
               y=2.7, h=1.05)
    d.text(s, "AI artifacts follow a full lifecycle — authored, evaluated, promoted, observed and "
              "improved — never mutated in place in production.", CX0, 4.3, CW, 0.9, size=14, color=GREY)
    d.set_notes(s, "LLMOps: prompts/agents/models/indexes are authored, evaluated against golden "
                   "datasets, promoted as bundles, observed in Langfuse, improved from production telemetry.")

    s = d.content_slide("Evaluation & regression gates", kicker="D7-13 · doc 21")
    d.bullets(s, [
        "Golden datasets + evaluators + LLM-as-judge score quality before release.",
        "Regression gates block a release that degrades quality, groundedness or safety.",
        "Distinct from the runtime refinement loop (D3-28): these are offline release gates.",
        "Evaluation adds model usage — its cost is tracked (deck 08).",
    ], CX0, 1.95, CW, 3.8, size=16, gap=14)
    d.set_notes(s, "Offline evaluation with golden datasets and LLM-as-judge, gating releases on "
                   "quality/groundedness/safety regressions.")

    s = d.content_slide("Test strategy & pyramid", kicker="D7-14 · doc 22")
    d.bullets(s, [
        "A broad test pyramid: unit · component · api · contract · integration · agents · supervisor · harness · workflows.",
        "AI-specific layers: rag · embeddings · vector · slm · prompts · guardrails · adversarial.",
        "Plus security, performance, resilience, regression and e2e — with golden datasets.",
    ], CX0, 1.95, CW, 3.4, size=16, gap=15)
    d.set_notes(s, "Testing spans classic layers and AI-specific layers plus security/perf/resilience/"
                   "regression/e2e.")

    s = d.content_slide("Engineering agents", kicker="D7-15 · doc 23")
    d.bullets(s, [
        "AI agents assist engineering: code review, security analysis, test generation, evaluation, docs.",
        "Scope & guardrails are explicit — they assist, they do not bypass human review or release gates.",
        "Their model usage/CI cost is tracked as a cost category (deck 08).",
    ], CX0, 1.95, CW, 3.2, size=16, gap=15)
    d.set_notes(s, "Engineering agents accelerate the team within explicit guardrails — never replacing "
                   "human review or release gates.")

    s = d.content_slide("Support, incidents & continuity", kicker="D7-16 / D7-17 / D7-18 · doc 28")
    d.two_col(s, "Support & incidents", [
        "Defined operational support model.",
        "Incident process: detect → correlate → mitigate → recover → learn.",
        "Performance & cost incidents have runbooks (deck 08).",
    ], "DR & continuity", [
        "Disaster recovery & business continuity plans.",
        "State (Redis) and artifacts (bundles) recoverable.",
        "Regular capacity & cost reviews.",
    ])
    d.set_notes(s, "A clear support model, an incident process with runbooks, and DR/continuity plans "
                   "covering state and artifact recovery.")

    d.adr_index_slides("ADR index — Operations (D7)", adrs_for(7),
                       notes="All 18 operations ADRs — observability, resilience, SLO, CI/CD, LLMOps, "
                             "testing, engineering agents, incident and DR. None open in this domain.")

    d.final_slide("Operations & quality — summary",
                  "Observed (Langfuse + Azure) · typed failures · gated releases · evaluated AI · DR-ready",
                  notes="The platform is observable, resilient, release-gated and continuously "
                        "evaluated — safe to operate and safe to change.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
