#!/usr/bin/env python3
"""Fetch 64x64 club icons from Golf Clash Notebook for every club in clubs.csv.

Saves into icons/clubs/<key>.png where <key> is the GCN naming convention:
strip leading "The " and remove all non-alphanumerics.

Re-run if clubs.csv grows. Existing files are not re-downloaded."""
import re
import csv
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "icons" / "clubs"
OUT.mkdir(parents=True, exist_ok=True)

BASE = ("https://raw.githubusercontent.com/golf-clash-notebook/"
        "golf-clash-notebook.github.io/dev/modules/site/src/main/"
        "resources/microsite/img/golfclash/clubs")


def key(name: str) -> str:
    n = re.sub(r"^The\s+", "", name, flags=re.IGNORECASE)
    return re.sub(r"[^A-Za-z0-9]", "", n)


names = set()
with open(ROOT / "clubs.csv") as f:
    for row in csv.DictReader(f):
        names.add(row["name"])

missing = []
ok = 0
skipped = 0
for n in sorted(names):
    k = key(n)
    if not k:
        continue
    out = OUT / f"{k}.png"
    if out.exists():
        skipped += 1
        continue
    url = f"{BASE}/{k}-64x64.png"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "gc-wind/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        out.write_bytes(data)
        ok += 1
        print(f"  + {n}  ->  {k}.png  ({len(data)} bytes)")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            missing.append(f"{n}  ({k}.png)")
            print(f"  ! 404 {n}")
        else:
            missing.append(f"{n}  HTTP {e.code}")
            print(f"  ! HTTP {e.code} for {n}")
    except Exception as e:
        missing.append(f"{n}  ({e})")
        print(f"  ! {n}: {e}")

print(f"\nDownloaded {ok}, skipped {skipped} existing, {len(missing)} missing.")
if missing:
    print("Missing (will use placeholder in app):")
    for m in missing:
        print("  -", m)
