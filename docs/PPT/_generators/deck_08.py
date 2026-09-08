#!/usr/bin/env python3
"""Deck 08 — Cost & FinOps (doc 26), FA light theme."""
import os
from PIL import Image
from fa import (Deck, PP_ALIGN, MSO_SHAPE, MSO_ANCHOR,
                NAVY, NAVY_DEEP, BLUE, GOLD, GREY, WHITE, MUTEDBLUE, CARD, CARD_LINE,
                LOGOS_NAVY, LOGOS, CX0, CX1, CW)
from pricing import SNAPSHOT, TECHS, ROLLUP, SOURCES

OUT = os.path.join(os.path.dirname(__file__), "..", "08-cost-finops.pptx")
STAMP = f"Indicative · {SNAPSHOT['region']} · {SNAPSHOT['currency']} · {SNAPSHOT['date']} · verify with FinOps"


def fit_logo(d, s, logo, right=CX1, top=0.34, maxw=1.5, maxh=0.62):
    path = None
    for base in (LOGOS_NAVY, LOGOS):
        cand = os.path.join(base, f"{logo}.png")
        if os.path.exists(cand):
            path = cand; break
    iw, ih = Image.open(path).size
    ar = iw / ih; h = maxh; w = h * ar
    if w > maxw:
        w = maxw; h = w / ar
    d.image(s, path, right - w, top + (maxh - h) / 2, w=w, h=h)


def cost_tech(d, key):
    e = TECHS[key]
    s = d.content_slide(e["name"], kicker=f"Cost · ADR {e['adr']}", subtitle=STAMP)
    fit_logo(d, s, e["logo"])
    d.kv_panel(s, "Cost drivers", e["drivers"], CX0, 1.8, 5.6, 3.15, size=12)
    d.box(s, "Formula:  " + e["formula"], CX0, 5.1, 5.6, 0.7, style="light", size=11.5,
          align=PP_ALIGN.LEFT, bold=False)
    labels = ["Low", "Expected", "High"]; y = 1.8
    for i, cell in enumerate(e["leh"]):
        amount, _, sub = cell.partition("\n")
        d.card(s, 7.4, y, 5.25, 1.0)
        d._rect(s, 7.4, y + 0.16, 0.12, 0.68, (BLUE if i == 1 else NAVY))
        d.text(s, labels[i], 7.65, y + 0.12, 1.6, 0.8, size=13, color=(BLUE if i == 1 else NAVY),
               bold=True, anchor=MSO_ANCHOR.MIDDLE)
        d.text(s, amount, 9.05, y + 0.08, 1.9, 0.85, size=22, color=NAVY, bold=True,
               anchor=MSO_ANCHOR.MIDDLE, font="Cambria")
        d.text(s, sub, 11.0, y + 0.18, 1.55, 0.7, size=10.5, color=GREY, anchor=MSO_ANCHOR.MIDDLE)
        y += 1.1
    d.text(s, "Optimization levers", 7.4, 5.15, 5.25, 0.32, size=13, color=BLUE, bold=True)
    d.bullets(s, e["levers"], 7.4, 5.5, 5.25, 1.4, size=11, gap=5)
    d.set_notes(s, f"{e['name']}: drivers/formula left; Low/Expected/High indicative monthly right; "
                   f"optimization levers below. Figures indicative ({SNAPSHOT['region']}, "
                   f"{SNAPSHOT['date']}) — confirm with FinOps.")


def cost_bars(d, s, labels, values, y0=1.95, color=BLUE):
    vmax = max(values); n = len(labels)
    row_h = min(0.5, (6.7 - y0) / n); y = y0; x0 = CX0 + 3.0; maxlen = 6.5
    for lab, val in zip(labels, values):
        d.text(s, lab.replace("\n", " "), CX0, y - 0.02, 2.9, row_h, size=10.5, color=NAVY,
               bold=True, anchor=MSO_ANCHOR.MIDDLE)
        w = maxlen * val / vmax
        d._rect(s, x0, y + 0.05, max(w, 0.05), row_h - 0.16, color)
        d.text(s, f"${val:,}", x0 + max(w, 0.05) + 0.1, y - 0.02, 1.2, row_h, size=10.5,
               color=NAVY, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        y += row_h


def build():
    d = Deck()
    d.title_slide("Cost", "& FinOps",
                  "Per-technology cost model · scenarios · budget controls  —  doc 26",
                  kicker="Deck 08 · Cost",
                  notes="The cost story per technology. Every figure is an indicative public list "
                        "price, USD, Azure UK South, captured 2026-09-08 — directional for ARB, to be "
                        "confirmed by FinOps and converted to GBP + VAT. Pricing lives in a versioned "
                        "data file, never in application code.")

    s = d.content_slide("The cost model", kicker="doc 26 §74",
                        subtitle="Total cost decomposition")
    d.box(s, "Total = Infrastructure + Model/SLM + Embedding + RAG/Vector + API/Integration\n"
             "+ Service Bus + Storage + Network + Observability + Engineering-AI",
          CX0, 1.9, CW, 1.2, style="navy", size=14)
    d.bullets(s, [
        "Cost is measured per workflow and per successful outcome — not only per request.",
        "Allocation dimensions: environment · component · workflow · agent · model · team · capability.",
        "Cost tags: application=pff-fa-ai · environment=prod · component=ai-runtime · workflow=affiliation.",
        "Optimize without weakening security, authorization, correctness, AI quality or guardrails.",
    ], CX0, 3.4, CW, 2.8, size=15, gap=13)
    d.set_notes(s, "Ten cost categories. The meaningful unit for agentic work is cost-per-workflow / "
                   "per-successful-affiliation. Everything is tagged and allocable.")

    s = d.content_slide("Cost drivers & allocation", kicker="what moves the bill")
    d.two_col(s, "Highest-impact variables", [
        "SLM tokens & GPU hours (dominant lever).",
        "RAG/embedding volume & re-index frequency.",
        "Vector search units; observability trace/log volume.",
        "Retry amplification & agent loops (bounded — deck 02).",
    ], "Allocation & tags", [
        "Per environment / workflow / agent / model.",
        "Cost tags on every resource.",
        "Langfuse gives per-trace token & cost telemetry.",
        "Enables cost-per-successful-affiliation.",
    ])
    d.set_notes(s, "SLM and GPU dominate; RAG, vector and observability volume follow; bounded "
                   "retries/loops keep cost predictable.")

    for key in ["slm", "embedding", "vector", "observability", "compute",
                "eventing", "cache", "platform", "aiops"]:
        cost_tech(d, key)

    s = d.content_slide("Cost per request / workflow / outcome", kicker="doc 26 §76–79")
    d.stat_cards(s, [("Per request", "narrow view — misleading for agents"),
                     ("Per workflow", "multi-agent, multi-API, RAG, SLM"),
                     ("Per outcome", "per successful affiliation — the true unit"),
                     ("Per club/org", "where permitted, access-controlled")], y=2.1, h=1.9)
    d.text(s, "A single affiliation workflow may span multiple agents, enterprise API calls, RAG "
              "queries and model calls — so cost-per-successful-affiliation is the metric that matters.",
           CX0, 4.4, CW, 1.0, size=15, color=GREY)
    d.set_notes(s, "Report cost per workflow and per successful outcome; per-request understates "
                   "agentic workloads.")

    s = d.content_slide("Budget controls & guardrails", kicker="doc 26 §90–98")
    d.two_col(s, "Budgets & alerts", [
        "Budgets per month / environment / workflow / model / evaluation.",
        "Alerts at 50 / 75 / 90 / 100 %.",
        "Cost anomaly detection (token/GPU/API spikes).",
    ], "Cost guardrails & routing", [
        "Max tokens/model-calls/tool-calls/retries per workflow.",
        "On budget breach: stop · degrade · route to cheaper approved model.",
        "Model routing optimises cost, latency & quality together.",
    ])
    d.set_notes(s, "Budgets and alerts at 50/75/90/100%, anomaly detection, configurable cost "
                   "guardrails; on breach we degrade or route to a cheaper approved model.")

    s = d.content_slide("Scenario rollup — indicative monthly", kicker="Scenarios", subtitle=STAMP)
    d.table(s, [
        ["Scenario", "Profile", "Indicative total / month"],
        ["Low", "pilot · hosted SLM · minimal infra", f"${sum(ROLLUP['low']):,}"],
        ["Expected", "production season · self-hosted SLM", f"${sum(ROLLUP['expected']):,}"],
        ["High", "peak window · GPU HA · full observability", f"${sum(ROLLUP['high']):,}"],
    ], CX0, 1.95, CW, 2.0, col_widths=[2.0, 5.8, 3.0], font_size=14)
    d.text(s, "SLM/GPU dominates the Expected and High scenarios — the single biggest lever, and the "
              "reason the vLLM decision (deck 09) matters for cost.", CX0, 4.2, CW, 0.9, size=14, color=GREY)
    d.text(s, "Not a quote. USD indicative list, ex-VAT — convert to GBP and add VAT with FinOps.",
           CX0, 6.4, CW, 0.4, size=12, color=BLUE, bold=True)
    d.set_notes(s, "Three scenarios; Expected ≈ ${:,}/mo, dominated by self-hosted GPU.".format(sum(ROLLUP['expected'])))

    s = d.content_slide("Expected monthly cost by technology", kicker="Breakdown", subtitle=STAMP)
    cost_bars(d, s, ROLLUP["labels"], ROLLUP["expected"])
    d.set_notes(s, "Expected-scenario breakdown; the SLM/GPU bar dwarfs the rest — optimisation targets it first.")

    s = d.content_slide("Pricing sources & caveats", kicker=SNAPSHOT["date"])
    d.bullets(s, [
        f"Region: {SNAPSHOT['region']}   ·   Currency: {SNAPSHOT['currency']}   ·   Snapshot: {SNAPSHOT['date']}   ·   Pricing version {SNAPSHOT['version']}",
        "All figures are INDICATIVE public list prices for directional planning — not a quote or commitment.",
        "Convert to GBP and add VAT; apply enterprise agreement / reservation discounts with FinOps.",
        "Pricing is maintained in a versioned data file (pricing.py), never hard-coded in application logic (doc 26 §138).",
    ], CX0, 1.95, CW, 2.6, size=14, gap=12)
    d.text(s, "Anchored to:", CX0, 4.7, CW, 0.35, size=13, color=BLUE, bold=True)
    d.bullets(s, SOURCES, CX0, 5.05, CW, 1.6, size=12, gap=6)
    d.set_notes(s, "Transparency slide: region, currency, date, version and the public sources each "
                   "figure is anchored to.")

    d.final_slide("Cost & FinOps — summary",
                  "SLM/GPU dominates · measure per outcome · budgets + guardrails + routing · verify with FinOps",
                  notes="Cost is dominated by the SLM/GPU choice, measured per successful outcome, and "
                        "controlled by budgets, guardrails and model routing; figures indicative pending FinOps.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
