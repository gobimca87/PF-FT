#!/usr/bin/env python3
"""Deck 06 — Security & Governance (D6), FA light theme."""
import os
from fa import (Deck, adrs_for, PP_ALIGN, MSO_SHAPE, MSO_ANCHOR,
                NAVY, NAVY_DEEP, BLUE, GOLD, GREY, WHITE, MUTEDBLUE, CARD, CARD_LINE,
                CX0, CX1, CW)

OUT = os.path.join(os.path.dirname(__file__), "..", "06-security-governance.pptx")


def trust_zones(d, s):
    zones = [("UNTRUSTED", "user input · external SLM · public content"),
             ("PERIMETER", "APIM — authN / authZ / rate-limit"),
             ("TRUSTED RUNTIME", "AKS — agents, harness, guardrails (in-tenancy)"),
             ("SYSTEM OF RECORD", "PFF enterprise APIs / DB — decides & executes")]
    widths = [2.55, 2.4, 2.95, 2.45]; x = CX0; y = 2.2; h = 3.15
    for (t, sub), w in zip(zones, widths):
        d.card(s, x, y, w, h)
        d._rect(s, x, y, w, 0.1, BLUE)
        d.text(s, t, x + 0.2, y + 0.2, w - 0.4, 0.5, size=13, color=NAVY, bold=True, font="Cambria")
        d.text(s, sub, x + 0.2, y + 0.85, w - 0.4, 2.1, size=12, color=GREY)
        if x > CX0 + 0.1:
            d.connector(s, x - 0.16, y + h / 2, x, y + h / 2, color=BLUE, width=1.4)
        x += w + 0.16
    d.text(s, "Trust decreases left→right for data; authority increases left→right. Nothing crosses a "
              "boundary without validation; egress to the untrusted zone is masked & fail-closed.",
           CX0, 5.6, CW, 0.8, size=13, color=GREY)


def build():
    d = Deck()
    d.title_slide("Security &", "Governance",
                  "Zero-trust · masking · guardrails · GDPR · audit  —  D6 (19 ADRs, 1 open)",
                  kicker="Deck 06 · Security & governance",
                  notes="The controls that make the Golden Rule and data protection real. One ADR is "
                        "Proposed (the SLM input masking regime, deck 09).")

    d.agenda_slide("What this deck covers", [
        "Zero-trust & trust zones",
        "AuthN/authZ boundary & context propagation",
        "Network segmentation, egress, encryption & keys",
        "Data classification & PII protection",
        "External-SLM data boundary & masking regime",
        "Guardrail pipeline & prompt-injection defence",
        "Tool & MCP security; RAG ACL enforcement",
        "Responsible AI, human oversight & HIL governance",
        "GDPR, safeguarding & children's data; audit logging",
        "Change governance, release gates & standards conformance",
    ])

    s = d.content_slide("Zero-trust & trust zones", kicker="D6-01")
    trust_zones(d, s)
    d.set_notes(s, "Zero-trust: every boundary validates. Data trust decreases toward the untrusted "
                   "zone; business authority increases toward the system of record; egress to the "
                   "untrusted zone is masked and fails closed.")

    s = d.content_slide("AuthN/authZ boundary & propagation", kicker="D6-02 / D6-03")
    d.two_col(s, "Boundary", [
        "APIM/enterprise auth authenticates & authorizes — the AI never does.",
        "The AI only consumes validated claims.",
        "A model output is never an authorization decision.",
    ], "Context integrity", [
        "Authorization context is integrity-protected & propagated with the request.",
        "Correlation IDs carry it through async/event paths.",
        "Cache & RAG are authorization-aware (never cross scopes).",
    ])
    d.set_notes(s, "Authorization happens at the boundary and is propagated with integrity through the "
                   "whole request; the AI consumes claims, never issues them.")

    s = d.content_slide("Network, egress, encryption & keys", kicker="D6-04 / D6-05")
    d.two_col(s, "Segmentation & egress", [
        "Network segmentation between zones; controlled egress.",
        "The only external egress is the masked SLM path.",
    ], "Encryption & key management", [
        "Encryption in transit and at rest.",
        "Keys managed in Key Vault (SPN-only access, deck 05).",
        "Token vault for masking is in-tenancy (next slide).",
    ])
    d.set_notes(s, "Segmented network, minimal controlled egress, encryption everywhere, keys in Key Vault.")

    s = d.content_slide("Data classification & PII", kicker="D6-06")
    d.bullets(s, [
        "Data is classified (public → confidential → special-category / children's data).",
        "PII protection policies drive masking, logging redaction and retention.",
        "Special-category data, children's personal data and secrets are the most tightly controlled.",
        "Classification decides what may reach a model and how — feeding the masking regime.",
    ], CX0, 1.95, CW, 3.8, size=16, gap=14)
    d.set_notes(s, "Classification is the input to masking, redaction and retention decisions; "
                   "children's and special-category data get the strongest protection.")

    s = d.content_slide("SLM input masking regime", kicker="D6-19 · PROPOSED",
                        subtitle="Refines D6-07 — ARB sign-off (deck 09)")
    d.kv_panel(s, "Two regimes", [
        ("External / hosted SLM", "MANDATORY mask/tokenise-all, fail-closed — no raw PII/records egress"),
        ("Hard-blocked", "special-category, children's data, secrets — never sent"),
        ("Self-hosted SLM", "raw OR masked, per task class (stays in-tenancy)"),
        ("Token vault", "reversible re-identification inside the boundary"),
    ], CX0, 1.95, 6.3, 4.4, col=GOLD)
    d.bullets(s, [
        "Strengthens D6-07 from 'minimise & redact' into a testable, binary default.",
        "External boundary fails closed if it cannot verify masking.",
        "Awaiting ARB sign-off (DPO owner, DPIA update) + Phase 20 vault sizing.",
    ], 8.5, 2.1, 4.2, 4.2, size=14, gap=13)
    d.set_notes(s, "The headline security decision: nothing raw leaves the tenancy to an external model "
                   "— masked/tokenised, special classes hard-blocked, fail-closed. Self-hosted may use "
                   "raw data. A reversible token vault re-identifies masked outputs in-tenancy.")

    s = d.content_slide("Guardrail pipeline", kicker="D6-09",
                        subtitle="At every boundary")
    d.pipeline(s, ["Input", "Context", "Prompt", "Tool", "Model", "Output"], y=2.6, h=1.05)
    d.bullets(s, [
        "Guardrails are middleware applied at every boundary, not a single output filter.",
        "Each stage can block, sanitise, or escalate; failures are typed (GuardrailError).",
        "Placement (D6-09) guarantees no path reaches the model or the user unchecked.",
    ], CX0, 4.3, CW, 1.8, size=14, gap=11)
    d.set_notes(s, "Guardrails at input, context, prompt, tool, model and output boundaries — middleware, "
                   "not a single filter.")

    s = d.content_slide("Prompt-injection & jailbreak defence", kicker="D6-08")
    d.bullets(s, [
        "Untrusted content (user text, RAG documents, tool output) is treated as data, never as instructions.",
        "Defence is layered: prompt/security layer (deck 03) + guardrail pipeline (this deck).",
        "Attempts to redirect the agent, escalate access, or exfiltrate data are detected and blocked.",
        "Suspicious redirection escalates to a human rather than being silently followed.",
    ], CX0, 1.95, CW, 3.8, size=16, gap=14)
    d.set_notes(s, "Injection defence is defence-in-depth: quarantine untrusted content, layered "
                   "detection, escalate rather than obey.")

    s = d.content_slide("Tool, MCP & RAG security", kicker="D6-10 / D6-11 / D6-12")
    d.two_col(s, "Tool & MCP", [
        "Tools allow-listed per agent; parameters & outputs validated.",
        "MCP servers carry an explicit trust model — no implicit trust.",
        "Only registered, approved servers/tools are callable.",
    ], "RAG ACL enforcement", [
        "Retrieval is ACL-enforced — users only see documents they may see.",
        "ACLs applied at query time, not post-filtered.",
        "Citations respect the same access scope.",
    ])
    d.set_notes(s, "Tools and MCP servers are allow-listed and trust-modelled; RAG enforces document "
                   "ACLs at retrieval so knowledge never leaks across authorization scopes.")

    s = d.content_slide("Responsible AI & human oversight", kicker="D6-13 / D6-14")
    d.two_col(s, "Responsible AI & prohibited use", [
        "Explicit prohibited-use policy.",
        "No invented business rules, outcomes, URLs, IDs or technical details.",
        "Fairness, transparency and accountability by design.",
    ], "Human oversight & HIL governance", [
        "HIL touchpoints are governed, not ad-hoc (deck 01/02).",
        "Humans confirm state-changing actions.",
        "Oversight is auditable.",
    ])
    d.set_notes(s, "Responsible-AI guardrails plus governed human oversight; prohibited uses are "
                   "explicit; humans stay in control of state-changing actions.")

    s = d.content_slide("GDPR, safeguarding & audit", kicker="D6-16 / D6-17")
    d.two_col(s, "GDPR & safeguarding", [
        "GDPR compliance; children's data specially protected (safeguarding).",
        "DPIA maintained; masking regime feeds it (deck 09).",
        "Retention & erasure policies applied.",
    ], "Audit & evidential record", [
        "Auditable, evidential logging of decisions & actions.",
        "Correlation IDs tie conversation → workflow → enterprise call.",
        "Logs are redacted per classification (deck 07).",
    ])
    d.set_notes(s, "GDPR and safeguarding are first-class; an evidential audit record links every step; "
                   "children's data protection is explicit and drives the DPIA.")

    s = d.content_slide("Change governance & standards", kicker="D6-15 / D6-18")
    d.two_col(s, "Change governance & release gates", [
        "Security-relevant changes pass release gates.",
        "Immutable versioned bundles; no in-place prod change.",
        "Ties to CI/CD quality gates (deck 07).",
    ], "Standards conformance", [
        "Conformance to applicable enterprise & regulatory standards.",
        "Evidenced and reviewed.",
        "Part of ARB governance (D0).",
    ])
    d.set_notes(s, "Change is governed through release gates; the platform conforms to applicable "
                   "standards, evidenced and reviewed under ARB governance.")

    d.adr_index_slides("ADR index — Security & Governance (D6)", adrs_for(6),
                       notes="All 19 security & governance ADRs. One is Proposed (◆): D6-19 SLM input "
                             "masking regime (deck 09), refining the external-SLM data boundary D6-07.")

    d.final_slide("Security & governance — summary",
                  "Zero-trust · AI never authorizes · mask-all to external models · guardrails everywhere · fully audited",
                  notes="Defence-in-depth around an absolute boundary — the AI never decides or "
                        "authorizes, nothing raw leaves the tenancy, everything is audited.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
