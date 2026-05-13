#!/usr/bin/env python3
"""Flatten clubs.csv -> clubs.js (window.CLUBS catalog used by the web app)."""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent

cats = defaultdict(dict)
with open(ROOT / "clubs.csv") as f:
    for row in csv.DictReader(f):
        cat = row["category"]
        name = row["name"]
        lvl = int(row["level"])
        if name not in cats[cat]:
            cats[cat][name] = {"power": [], "accuracy": []}
        # rows are already sorted by level inside each club
        cats[cat][name]["power"].append(int(row["power"]))
        cats[cat][name]["accuracy"].append(int(row["accuracy"]))

# emit as compact JSON, one club per line for readability
out = ["// Generated from clubs.csv by build_clubs_js.py — do not edit by hand.",
       "window.CLUBS = {"]
for cat in ["Drivers", "Woods", "LongIrons", "ShortIrons",
            "Wedges", "RoughIrons", "SandWedges"]:
    out.append(f'  {cat}: {{')
    for name, stats in cats[cat].items():
        out.append(f'    {json.dumps(name)}: {json.dumps(stats, separators=(",", ":"))},')
    out.append("  },")
out.append("};")

(ROOT / "clubs.js").write_text("\n".join(out) + "\n")
total = sum(len(v) for v in cats.values())
print(f"Wrote clubs.js with {total} clubs across {len(cats)} categories")
