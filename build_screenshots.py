#!/usr/bin/env python3
"""Capture README screenshots of the app at different viewports + states.
Run once after layout changes. Uses Playwright (Chromium).

Prereq: a local server on http://localhost:8765 (`python3 -m http.server
8765` in this folder).

State is seeded by writing localStorage on a blank `about:blank` page,
then navigating to the app — that way the IIFE reads our values on its
first run instead of falling back to the default seed. Dark color scheme
is emulated on every page.
"""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
OUT = ROOT / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)
URL = "http://localhost:8765/"

SEED_BAG = {
    "id": "bag-default",
    "name": "My Bag",
    "ballPower": 0,
    "slots": {
        "Drivers":    {"name": "The Quarterback", "level": 8, "power": 231, "accuracy": 100},
        "Woods":      {"name": "The Sniper",      "level": 7, "power": 166, "accuracy": 100},
        "LongIrons":  {"name": "The Grizzly",     "level": 5, "power": 122, "accuracy": 60},
        "ShortIrons": {"name": "The Hornet",      "level": 4, "power": 84,  "accuracy": 91},
        "Wedges":     {"name": "The Endbringer",  "level": 3, "power": 41,  "accuracy": 79},
        "RoughIrons": {"name": "Nirvana",         "level": 4, "power": 123, "accuracy": 74},
        "SandWedges": {"name": "The Malibu",      "level": 6, "power": 101, "accuracy": 96},
    },
}

TOUR_BAG = {
    "id": "bag-tour",
    "name": "Tour Bag",
    "ballPower": 3,
    "slots": {
        "Drivers":    {"name": "The Apocalypse",  "level": 6, "power": 236, "accuracy": 73},
        "Woods":      {"name": "Big Topper",      "level": 5, "power": 172, "accuracy": 64},
        "LongIrons":  {"name": "The Apache",      "level": 4, "power": 128, "accuracy": 65},
        "ShortIrons": {"name": "The Spitfire",    "level": 5, "power": 86,  "accuracy": 82},
        "Wedges":     {"name": "The Rapier",      "level": 4, "power": 39,  "accuracy": 82},
        "RoughIrons": {"name": "The Roughcutter", "level": 5, "power": 120, "accuracy": 74},
        "SandWedges": {"name": "The Sahara",      "level": 4, "power": 95,  "accuracy": 73},
    },
}


def new_page(p, w, h):
    ctx = p.chromium_ctx
    page = ctx.new_page()
    page.set_viewport_size({"width": w, "height": h})
    return page


def seed_and_open(page, bags, inputs, hash_="play"):
    """Navigate to the app's origin with localStorage primed."""
    # Hit the origin first so we can write localStorage for that origin.
    page.goto(URL + "?seed=1")
    page.evaluate(
        """([bags, inputs, hash]) => {
            localStorage.setItem('gc.bags', JSON.stringify(bags));
            localStorage.setItem('gc.activeBagId', bags[0].id);
            localStorage.setItem('gc.lastInputs', JSON.stringify(inputs));
            location.hash = '#' + hash;
        }""",
        [bags, inputs, hash_],
    )
    # Now reload so the IIFE picks up the localStorage values on boot.
    page.reload()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(250)


def shoot(page, name, full_page=False):
    path = OUT / f"{name}.png"
    page.screenshot(path=str(path), full_page=full_page)
    print(f"  + {path.relative_to(ROOT)}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            color_scheme="dark",
            device_scale_factor=2,
        )
        p.chromium_ctx = ctx  # stash for new_page helper

        # 1. Play view — wide, default bag, 8 MPH side wind
        page = new_page(p, 1180, 720)
        seed_and_open(
            page, [SEED_BAG],
            {"mph": "8", "dir": 90, "pinYd": "", "sliders": {"Wedges": 60, "RoughIrons": 100, "SandWedges": 100}},
        )
        shoot(page, "01-play-wide")
        page.close()

        # 2. Play view with a Shot distance entered — shows the
        # recommendation card and the highlighted club row. Uses side
        # wind (deg=90, E) so the recommendation card has non-zero
        # rings to demonstrate the feature.
        page = new_page(p, 1180, 760)
        seed_and_open(
            page, [SEED_BAG],
            {"mph": "12", "dir": 90, "pinYd": "160", "sliders": {"Wedges": 60, "RoughIrons": 100, "SandWedges": 100}},
        )
        shoot(page, "02-play-with-pin")
        page.close()

        # 3. Mobile portrait — full-page so the README can show the
        # complete vertical stack.
        page = new_page(p, 390, 844)
        seed_and_open(
            page, [SEED_BAG],
            {"mph": "8", "dir": 90, "pinYd": "", "sliders": {"Wedges": 60, "RoughIrons": 100, "SandWedges": 100}},
        )
        shoot(page, "03-play-mobile", full_page=True)
        page.close()

        # 4. Bags page — two bags so the list looks alive
        page = new_page(p, 1180, 520)
        seed_and_open(
            page, [SEED_BAG, TOUR_BAG],
            {"mph": "0", "dir": 90, "pinYd": "", "sliders": {"Wedges": 100, "RoughIrons": 100, "SandWedges": 100}},
            hash_="bags",
        )
        shoot(page, "04-bags")
        page.close()

        # 5. Edit-bag page — full-page so all 7 slots are visible
        page = new_page(p, 640, 900)
        seed_and_open(
            page, [SEED_BAG],
            {"mph": "0", "dir": 90, "pinYd": "", "sliders": {"Wedges": 100, "RoughIrons": 100, "SandWedges": 100}},
            hash_="edit/bag-default",
        )
        shoot(page, "05-edit-bag", full_page=True)
        page.close()

        # 6. Dropdown open — showcases the image-aware club picker
        page = new_page(p, 640, 720)
        seed_and_open(
            page, [SEED_BAG],
            {"mph": "0", "dir": 90, "pinYd": "", "sliders": {"Wedges": 100, "RoughIrons": 100, "SandWedges": 100}},
            hash_="edit/bag-default",
        )
        page.locator('.slot[data-cat="Drivers"] .cs-trigger').click()
        page.wait_for_timeout(200)
        shoot(page, "06-dropdown-open")
        page.close()

        ctx.close()
        browser.close()
    print("Done.")


if __name__ == "__main__":
    main()
