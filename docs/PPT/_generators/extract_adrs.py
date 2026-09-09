#!/usr/bin/env python3
"""Parse all ADRs into a structured JSON index for the decks."""
import glob
import json
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "architecture", "adr")
OUT = os.path.join(os.path.dirname(__file__), "adr_index.json")

DOMAIN_NAMES = {
    "0": "Decision Programme", "1": "Business Architecture",
    "2": "Application Architecture", "3": "AI Architecture",
    "4": "Information Architecture", "5": "Technology Architecture",
    "6": "Security & Governance", "7": "Operations", "8": "Business Value",
}


def first_sentence(md):
    m = re.search(r"##\s*1\.\s*Summary\s*\n(.+?)(?:\n##|\Z)", md, re.S)
    if not m:
        return ""
    text = re.sub(r"\s+", " ", m.group(1)).strip()
    text = re.sub(r"\*\*|\*|`", "", text)
    # first 1-2 sentences up to ~200 chars
    out = ""
    for part in re.split(r"(?<=[.;])\s+", text):
        if not out:
            out = part
        elif len(out) < 130:
            out += " " + part
        else:
            break
    return out[:240]


def parse(path):
    raw = open(path, encoding="utf-8").read()
    fm = {}
    m = re.match(r"---\n(.*?)\n---\n", raw, re.S)
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"([a-z_]+):\s*(.*)", line)
            if mm and mm.group(2) and not mm.group(2).startswith("["):
                fm[mm.group(1)] = mm.group(2).strip().strip('"')
    idm = re.search(r"ADR-D(\d)-(\d+)", os.path.basename(path))
    domain = idm.group(1) if idm else "?"
    num = int(idm.group(2)) if idm else 0
    return {
        "id": fm.get("id", os.path.basename(path).split("-md")[0]),
        "title": fm.get("title", ""),
        "status": fm.get("status", ""),
        "domain": domain,
        "num": num,
        "summary": first_sentence(raw),
    }


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "*", "ADR-*.md")))
    by_domain = {}
    for f in files:
        a = parse(f)
        by_domain.setdefault(a["domain"], []).append(a)
    for d in by_domain:
        by_domain[d].sort(key=lambda a: a["num"])
    total = sum(len(v) for v in by_domain.values())
    proposed = [a["id"] for v in by_domain.values() for a in v if a["status"] == "Proposed"]
    result = {"domains": by_domain, "domain_names": DOMAIN_NAMES,
              "total": total, "proposed": proposed}
    json.dump(result, open(OUT, "w"), indent=1)
    print(f"parsed {total} ADRs across {len(by_domain)} domains -> {OUT}")
    for d in sorted(by_domain):
        print(f"  D{d} {DOMAIN_NAMES.get(d,''):24} {len(by_domain[d])} ADRs")
    print("Proposed:", ", ".join(sorted(proposed)))


if __name__ == "__main__":
    main()
