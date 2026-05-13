#!/usr/bin/env python3
"""One-shot helper: flatten all GCN club YAML into a single CSV (clubs.csv).
Row per (club, level). Run again after re-pulling YAML if GCN data updates."""
import csv
from pathlib import Path
import yaml

ROOT = Path(__file__).parent
CATS = {
    "Drivers": "drivers.yaml",
    "Woods": "woods.yaml",
    "LongIrons": "longirons.yaml",
    "ShortIrons": "shortirons.yaml",
    "Wedges": "wedges.yaml",
    "RoughIrons": "roughirons.yaml",
    "SandWedges": "sandwedges.yaml",
}

rows = []
for cat, fname in CATS.items():
    with open(ROOT / fname) as f:
        for c in yaml.safe_load(f):
            for i, (p, a) in enumerate(zip(c["power"], c["accuracy"])):
                rows.append({
                    "category": cat,
                    "name": c["name"],
                    "type": c["type"],
                    "tour": c["tour"],
                    "level": i + 1,
                    "power": p,
                    "accuracy": a,
                    "topspin": c["topspin"][i],
                    "backspin": c["backspin"][i],
                    "curl": c["curl"][i],
                    "ballguide": c["ballguide"][i],
                })

with open(ROOT / "clubs.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"Wrote {len(rows)} rows to clubs.csv")
