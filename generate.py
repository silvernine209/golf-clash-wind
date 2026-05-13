#!/usr/bin/env python3
"""
Golf Clash wind cheat sheet generator.

Reads my_bag.yaml + the cached GCN club data, prints two tables (rings per MPH)
to stdout AND writes them to cheatsheet.md.

Formula (from Golf Clash Notebook wind.scala):
  rings_per_mph = actual_carry
                  / ( category_max
                      * (3 - acc/50)
                      * category_mult           # 1.45 Rough, 1.15 Sand, else 1.0
                      * rule_based_correction ) # 0.9 for B52/Grizzly at lvl >= 5

Usage:
  python3 generate.py           # uses ./my_bag.yaml
  python3 generate.py other.yaml
"""

import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).parent

CATEGORY_MAX = {
    "Drivers": 240,
    "Woods": 180,
    "LongIrons": 135,
    "ShortIrons": 90,
    "Wedges": 45,
    "RoughIrons": 135,
    "SandWedges": 120,
}

CATEGORY_MULT = {
    "RoughIrons": 1.45,
    "SandWedges": 1.15,
}

CATEGORY_YAML = {
    "Drivers": "drivers.yaml",
    "Woods": "woods.yaml",
    "LongIrons": "longirons.yaml",
    "ShortIrons": "shortirons.yaml",
    "Wedges": "wedges.yaml",
    "RoughIrons": "roughirons.yaml",
    "SandWedges": "sandwedges.yaml",
}

NORMAL_ORDER = ["Drivers", "Woods", "LongIrons", "ShortIrons"]
SLIDER_ORDER = ["Wedges", "RoughIrons", "SandWedges"]


def load_all_clubs():
    db = {}
    for cat, fname in CATEGORY_YAML.items():
        with open(ROOT / fname) as f:
            for c in yaml.safe_load(f):
                db[(cat, c["name"].lower())] = c
    return db


def lookup(db, category, name, level):
    key = (category, name.lower())
    if key not in db:
        # tolerate missing "The " prefix
        key = (category, ("the " + name).lower())
    if key not in db:
        return None
    c = db[key]
    i = level - 1
    if i < 0 or i >= len(c["power"]):
        raise ValueError(f"{name} only has levels 1..{len(c['power'])}, got {level}")
    return {
        "name": c["name"],
        "power": c["power"][i],
        "accuracy": c["accuracy"][i],
    }


def correction(club_name, level):
    n = club_name.lower()
    if ("b52" in n or "grizzly" in n) and level >= 5:
        return 0.9
    return 1.0


def rings_per_mph(category, power, accuracy, actual_carry, club_name, level):
    base = 3 - accuracy / 50.0
    cat_max = CATEGORY_MAX[category]
    cat_mult = CATEGORY_MULT.get(category, 1.0)
    corr = correction(club_name, level)
    denom = cat_max * base * cat_mult * corr
    return actual_carry / denom


def resolve(bag_slot, db, category):
    """Return dict with name, level, power, accuracy.

    Per-club `power` and `accuracy` fields in my_bag.yaml are the source of
    truth — set these to your actual in-game stats (including any perk/card
    bonuses or penalties). If omitted, falls back to cached GCN data via
    name+level lookup. Legacy field names `power_override`/`accuracy_override`
    are also accepted.
    """
    name = bag_slot["name"]
    level = bag_slot["level"]
    looked = lookup(db, category, name, level)
    power = bag_slot.get("power", bag_slot.get("power_override",
                          looked["power"] if looked else None))
    acc = bag_slot.get("accuracy", bag_slot.get("accuracy_override",
                       looked["accuracy"] if looked else None))
    if power is None or acc is None:
        raise ValueError(
            f"Could not resolve {category} {name} lvl {level}. "
            f"Add explicit `power:` and `accuracy:` fields in my_bag.yaml."
        )
    return {"name": name, "level": level, "power": power, "accuracy": acc}


def fmt(x):
    return f"{x:.2f}"


def build_normal_table(bag, db):
    rows = []
    # MIN of each row needs the previous (shorter) club's power
    powers_by_cat = {
        cat: resolve(bag["clubs"][cat], db, cat)["power"] for cat in NORMAL_ORDER
    }
    powers_by_cat["Wedges"] = resolve(bag["clubs"]["Wedges"], db, "Wedges")["power"]
    shorter = {
        "Drivers": "Woods",
        "Woods": "LongIrons",
        "LongIrons": "ShortIrons",
        "ShortIrons": "Wedges",
    }
    for cat in NORMAL_ORDER:
        c = resolve(bag["clubs"][cat], db, cat)
        min_carry = powers_by_cat[shorter[cat]]
        max_carry = c["power"]
        mid_carry = (min_carry + max_carry) / 2
        rmin = rings_per_mph(cat, c["power"], c["accuracy"], min_carry, c["name"], c["level"])
        rmid = rings_per_mph(cat, c["power"], c["accuracy"], mid_carry, c["name"], c["level"])
        rmax = rings_per_mph(cat, c["power"], c["accuracy"], max_carry, c["name"], c["level"])
        rows.append({
            "category": cat,
            "label": f"{display_cat(cat)} — {c['name']} {c['level']}",
            "acc": c["accuracy"],
            "power": c["power"],
            "min_carry": min_carry,
            "mid_carry": mid_carry,
            "max_carry": max_carry,
            "rmin": rmin,
            "rmid": rmid,
            "rmax": rmax,
        })
    return rows


def build_slider_table(bag, db):
    cols = []
    for cat in SLIDER_ORDER:
        c = resolve(bag["clubs"][cat], db, cat)
        rmax = rings_per_mph(cat, c["power"], c["accuracy"], c["power"], c["name"], c["level"])
        cols.append({
            "category": cat,
            "label": f"{display_cat(cat)} — {c['name']} {c['level']}",
            "acc": c["accuracy"],
            "power": c["power"],
            "rmax": rmax,
        })
    return cols


def display_cat(cat):
    return {
        "Wedges": "Wedge",
        "RoughIrons": "Rough Iron",
        "SandWedges": "Sand Wedge",
        "Drivers": "Driver",
        "Woods": "Wood",
        "LongIrons": "Long Iron",
        "ShortIrons": "Short Iron",
    }[cat]


def render(rows, slider_cols, bag):
    out = []
    out.append("# Golf Clash Wind Cheat Sheet — rings per MPH")
    out.append("")
    out.append(f"Generated from `my_bag.yaml`. Ball power assumed: **Power {bag.get('ball_power', 0)}**.")
    out.append("")
    out.append("Formula: `rings = wind_mph × cell_value`")
    out.append("")
    out.append("## Table 1 — Normal Club Range (rings/MPH)")
    out.append("")
    out.append("| Club | Acc | Power | MIN | MID | MAX |")
    out.append("|---|---:|---:|---:|---:|---:|")
    for r in rows:
        out.append(f"| {r['label']} | {r['acc']} | {r['power']} | {fmt(r['rmin'])} | {fmt(r['rmid'])} | {fmt(r['rmax'])} |")
    out.append("")
    out.append("### Bag-specific MIN actual-carry values")
    out.append("")
    out.append("| Club | MIN carry | from |")
    out.append("|---|---:|---|")
    shorter_labels = {
        "Drivers": "Woods",
        "Woods": "LongIrons",
        "LongIrons": "ShortIrons",
        "ShortIrons": "Wedges",
    }
    for r in rows:
        out.append(f"| {display_cat(r['category'])} | {r['min_carry']:.0f} | {display_cat(shorter_labels[r['category']])} power |")
    out.append("")
    out.append("## Table 2 — Slider Cheat Sheet (rings/MPH)")
    out.append("")
    header = "| Slider % | " + " | ".join(c["label"] for c in slider_cols) + " |"
    sep = "|---:|" + "|".join(["---:"] * len(slider_cols)) + "|"
    out.append(header)
    out.append(sep)
    for pct in range(100, 0, -10):
        cells = [fmt(c["rmax"] * pct / 100) for c in slider_cols]
        out.append(f"| {pct}% | " + " | ".join(cells) + " |")
    out.append("")
    out.append("### MAX rings/MPH (100% slider)")
    out.append("")
    for c in slider_cols:
        out.append(f"- **{c['label']}** = `{fmt(c['rmax'])}`")
    out.append("")
    out.append("---")
    out.append("")
    out.append("**Caveats:**")
    out.append("- Tables assume ball Power 0 unless `ball_power` in bag config is non-zero (multiplies actual_carry by 1.00/1.03/1.05/1.07/1.10/1.13 for Power 0..5).")
    out.append("- Head/tail winds are reduced by ~40% in-game vs side winds.")
    out.append("- MIN values are bag-specific: upgrading a shorter club raises the next-longer club's MIN.")
    out.append("- Grizzly/B52 at level >= 5 apply the 0.9x correction automatically.")
    return "\n".join(out)


def apply_ball_power(rows, slider_cols, ball_power):
    coef = [1.00, 1.03, 1.05, 1.07, 1.10, 1.13][ball_power]
    if coef == 1.0:
        return
    for r in rows:
        r["rmin"] *= coef
        r["rmid"] *= coef
        r["rmax"] *= coef
    for c in slider_cols:
        c["rmax"] *= coef


def main():
    bag_path = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "my_bag.yaml")
    with open(bag_path) as f:
        bag = yaml.safe_load(f)
    db = load_all_clubs()
    rows = build_normal_table(bag, db)
    slider_cols = build_slider_table(bag, db)
    apply_ball_power(rows, slider_cols, bag.get("ball_power", 0))
    md = render(rows, slider_cols, bag)
    out_path = ROOT / "cheatsheet.md"
    out_path.write_text(md + "\n")
    print(md)
    print(f"\n[wrote {out_path}]", file=sys.stderr)


if __name__ == "__main__":
    main()
