#!/usr/bin/env python3
"""Shared slide patterns for the PFF AI ARB domain decks."""
import json
import os
from orion import (PP_ALIGN, MSO_SHAPE, WHITE, GREY, MUTED, CYAN, BLUE, PURPLE,
                   PINK, VIOLET, YELLOW, GREEN, PANEL, PANEL2, ACCENT, MAGENTA, HAIR)

_IDX = json.load(open(os.path.join(os.path.dirname(__file__), "adr_index.json")))


def adrs_for(*domains):
    out = []
    for dm in domains:
        out.extend(_IDX["domains"].get(str(dm), []))
    return out


def _short_id(adr_id):
    return adr_id.replace("ADR-", "")


def _st(status):
    return "✓ Acc" if status == "Accepted" else ("◆ Prop" if status == "Proposed" else status[:6])


def adr_index_slides(d, title, adrs, notes=None, rows_per_table=14):
    """Render a compact index of ADRs: two tables per slide (left/right)."""
    per_slide = rows_per_table * 2
    pages = [adrs[i:i + per_slide] for i in range(0, len(adrs), per_slide)]
    for pi, page in enumerate(pages):
        suffix = f"  ({pi+1}/{len(pages)})" if len(pages) > 1 else ""
        s = d.content_slide(f"{title}{suffix}",
                            f"{len(adrs)} decisions — higher-trust sources always win; ◆ = Proposed, awaiting ARB")
        left = page[:rows_per_table]
        right = page[rows_per_table:]
        for col, chunk in enumerate((left, right)):
            if not chunk:
                continue
            rows = [["ADR", "Decision", "Status"]]
            for a in chunk:
                t = a["title"] or ""
                if len(t) > 52:
                    t = t[:51] + "…"
                rows.append([_short_id(a["id"]), t, _st(a["status"])])
            x = 0.55 + col * 6.30
            d.table(s, rows, x, 1.95, 6.0, min(0.34 * len(rows), 5.0),
                    col_widths=[1.1, 4.15, 0.95], font_size=9)
        if pi == len(pages) - 1 and notes:
            s.notes_slide.notes_text_frame.text = notes
    return pages


def stat_cards(d, s, cards, y=2.2, h=1.9, x0=0.9, x1=12.43, gap=0.3):
    """cards: list of (big, small, color) — the passed colour is ignored in favour
    of a restrained azure/magenta alternation; cards are borderless panels."""
    n = len(cards)
    w = (x1 - x0 - gap * (n - 1)) / n
    x = x0
    for i, (big, small, _col) in enumerate(cards):
        col = ACCENT if i % 2 == 0 else MAGENTA
        d.box(s, "", x, y, w, h, fill=PANEL2, line=None)
        d.text(s, big, x + 0.25, y + 0.22, w - 0.5, 0.9, size=22, color=col, bold=True)
        d.text(s, small, x + 0.25, y + 1.02, w - 0.5, h - 1.1, size=12, color=GREY)
        x += w + gap


def two_col(d, s, left_title, left_items, right_title, right_items,
            y=1.9, size=15, gap=12):
    d.text(s, left_title, 0.9, y, 5.6, 0.4, size=15, color=ACCENT, bold=True)
    d.bullets(s, left_items, 0.9, y + 0.5, 5.6, 4.6, size=size, gap=gap)
    d.text(s, right_title, 6.85, y, 5.6, 0.4, size=15, color=ACCENT, bold=True)
    d.bullets(s, right_items, 6.85, y + 0.5, 5.6, 4.6, size=size, gap=gap)


def pipeline(d, s, steps, y=3.0, h=0.95, x0=0.55, x1=12.78, colors=None):
    """Horizontal box→box→box flow — uniform borderless panels, azure labels,
    grey connectors (no rainbow). steps: list of 'label' or (label, sublabel)."""
    n = len(steps)
    gap = 0.28
    w = (x1 - x0 - gap * (n - 1)) / n
    x = x0
    prev = None
    for i, step in enumerate(steps):
        if isinstance(step, str):
            d.box(s, step, x, y, w, h, fill=PANEL2, line=None, textcolor=ACCENT, size=12)
        else:
            d.box(s, "", x, y, w, h, fill=PANEL2, line=None)
            d.text(s, step[0], x + 0.1, y + 0.14, w - 0.2, 0.5, size=12.5, color=ACCENT,
                   bold=True, align=PP_ALIGN.CENTER)
            d.text(s, step[1], x + 0.1, y + h - 0.42, w - 0.2, 0.4, size=10.5, color=GREY,
                   align=PP_ALIGN.CENTER)
        if prev is not None:
            d.connector(s, prev, y + h / 2, x, y + h / 2, color=MUTED, width=1.5)
        prev = x + w
        x += w + gap


def kv_panel(d, s, title, pairs, x, y, w, h, col=ACCENT, size=12):
    d.box(s, "", x, y, w, h, fill=PANEL2, line=None)
    d.text(s, title, x + 0.24, y + 0.16, w - 0.48, 0.4, size=14, color=col, bold=True)
    yy = y + 0.7
    for k, v in pairs:
        d.text(s, k, x + 0.24, yy, w - 0.48, 0.3, size=size, color=WHITE, bold=True)
        d.text(s, v, x + 0.24, yy + 0.28, w - 0.48, 0.5, size=size - 1, color=GREY)
        yy += 0.78
