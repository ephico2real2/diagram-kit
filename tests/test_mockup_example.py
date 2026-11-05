# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The example mockup of /build-mockup follows its own skill, and it holds at 390, 820 and 1440 px in both themes and
in every UI state. The file is opened from disk, so no test reaches the network.

Set MOCKUP_EVIDENCE to a directory to keep one PNG per state, theme and width there.
"""

from __future__ import annotations

import json
import os
import pathlib
import re

import pytest
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "build-mockup" / "SKILL.md"
EXAMPLE = ROOT / "skill" / "build-mockup" / "example" / "workspaces.html"

STATES = ("loading", "empty", "error", "forbidden", "conflict", "success")
VIEWS = ("ready",) + STATES
WIDTHS = (390, 820, 1440)
THEMES = ("light", "dark")
TARGETS = ("react-ts", "preact-ts", "react-pf-ts")
REQUIRED_TOKENS = ("bg surface raised border track control text muted accent accentFg "
                   "okFg okBg warnFg warnBg infoFg infoBg stopFg stopBg").split()
CATEGORIES = [f"cat.{c}" for c in "emerald sky amber violet coral pink teal slate".split()]


def source() -> str:
    return EXAMPLE.read_text()


def section_types() -> set[str]:
    """The section types in the skill's "Sections: a fixed vocabulary" table, read from it so the two cannot drift."""
    text = SKILL.read_text()
    table = text.split("Sections: a fixed vocabulary", 1)[1].split("\n## ", 1)[0]
    return set(re.findall(r"^\| `([a-z-]+)` \|", table, re.M))


def token_tables() -> dict[str, dict[str, str]]:
    block = re.search(r"// tokens:start\n(.*?)// tokens:end", source(), re.S)
    assert block, "the token tables sit between // tokens:start and // tokens:end"
    tables = {}
    for theme in THEMES:
        body = re.search(rf"\b{theme}: \{{(.*?)\}}", block.group(1), re.S)
        assert body, f"no {theme} table"
        tables[theme] = dict(re.findall(r"'([\w.]+)': '(#[0-9a-f]{6})'", body.group(1)))
    return tables


def luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


# --- the file follows the skill ------------------------------------------------------------------------------------

def test_the_example_declares_its_target_first():
    props = json.loads(re.search(r"data-props='(.*?)'", source(), re.S).group(1))
    assert props["$target"]["framework"] in TARGETS
    assert set(props["$target"]) >= {"framework", "styling", "state", "data"}


def test_every_section_is_a_type_the_skill_names():
    used = set(re.findall(r'data-component="([a-z-]+)"', source()))
    assert used, "the example has no sections"
    assert used <= section_types(), f"types the skill does not name: {sorted(used - section_types())}"


def test_every_dataset_has_its_source_its_type_and_its_states():
    text = source()
    for name in sorted(set(re.findall(r'data-dataset="(\w+)"', text))):
        assert re.search(rf"^\s*// dataset {name}: (GET|POST|PUT|PATCH|DELETE) /\S+ → \S+", text, re.M), name
        states = re.search(rf"^\s*// states {name}: (.+)$", text, re.M)
        assert states, f"dataset {name} lists no UI states"
        assert set(states.group(1).split(" | ")) <= set(STATES), states.group(1)
    for typename in re.findall(r"→ (?:Page<)?(\w+)", text):
        assert re.search(rf"^\s*// type {typename} = \{{", text, re.M), f"no // type for {typename}"


def test_the_example_shows_every_ui_state():
    shown = set()
    for line in re.findall(r"^\s*// states \w+: (.+)$", source(), re.M):
        shown |= set(line.split(" | "))
    assert shown == set(STATES)


def test_every_state_key_is_declared_with_its_owner_type_and_default():
    keys = re.findall(r"^\s*// state (\w+): owner=\w+ type=\S+ default='\w+'", source(), re.M)
    assert {"theme", "view", "role"} <= set(keys)


def test_no_hex_colour_outside_the_token_tables():
    text = re.sub(r"// tokens:start.*?// tokens:end", "", source(), flags=re.S)
    assert not re.findall(r"#[0-9a-fA-F]{3,8}\b", text)


def test_both_token_tables_hold_every_required_name():
    tables = token_tables()
    for theme in THEMES:
        assert set(REQUIRED_TOKENS + CATEGORIES) <= set(tables[theme]), theme


@pytest.mark.parametrize("theme", THEMES)
def test_the_token_pairs_meet_their_contrast(theme):
    t = token_tables()[theme]
    text_pairs = [("text", "bg"), ("text", "surface"), ("text", "raised"), ("muted", "surface"), ("muted", "bg"),
                  ("accent", "surface"), ("accentFg", "accent")] + \
                 [(f"{s}Fg", f"{s}Bg") for s in ("ok", "warn", "info", "stop")]
    for fg, bg in text_pairs:
        assert contrast(t[fg], t[bg]) >= 4.5, f"{theme}: {fg} on {bg} is {contrast(t[fg], t[bg]):.2f}:1"
    for cat in CATEGORIES:
        assert contrast(t[cat], t["surface"]) >= 3, f"{theme}: {cat} on surface"


# --- the file holds in a browser -----------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.mark.parametrize("width", WIDTHS)
@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("view", VIEWS)
def test_each_state_fits_each_width_in_each_theme(browser, view, theme, width):
    page = browser.new_page(viewport={"width": width, "height": 800})
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"{EXAMPLE.as_uri()}?theme={theme}&view={view}")
    assert not errors
    assert page.evaluate("document.documentElement.dataset.theme") == theme
    metrics = page.evaluate("""() => ({
        scroll: document.documentElement.scrollWidth, inner: innerWidth,
        bg: document.querySelector('#app').getBoundingClientRect().height, tall: innerHeight,
        text: document.body.innerText })""")
    assert metrics["scroll"] <= metrics["inner"], f"sideways scroll at {width} px"
    assert metrics["bg"] >= metrics["tall"], "the background stops short"
    for leftover in ("{{", "sc-", "undefined", "NaN", "null"):
        assert leftover not in metrics["text"], leftover
    if evidence := os.environ.get("MOCKUP_EVIDENCE"):
        pathlib.Path(evidence).mkdir(parents=True, exist_ok=True)
        page.screenshot(path=f"{evidence}/{view}.{theme}.{width}.png", full_page=True)
    page.close()


@pytest.mark.parametrize("view,role", [("loading", "status"), ("success", "status"), ("error", "alert"),
                                       ("conflict", "alert")])
def test_a_state_that_changes_without_a_click_is_announced(browser, view, role):
    page = browser.new_page()
    page.goto(f"{EXAMPLE.as_uri()}?view={view}")
    assert page.locator(f'[data-dataset="workspaces"] [role="{role}"]').count() == 1
    page.close()


def test_a_forbidden_action_says_why_and_stays_focusable(browser):
    page = browser.new_page()
    page.goto(f"{EXAMPLE.as_uri()}?role=viewer")
    delete = page.get_by_role("button", name=re.compile("^Delete"))
    assert delete.count() > 0
    for i in range(delete.count()):
        button = delete.nth(i)
        assert button.get_attribute("aria-disabled") == "true"
        reason = page.locator(f"#{button.get_attribute('aria-describedby')}")
        assert reason.is_visible() and reason.inner_text().strip()
    page.close()


def test_every_control_has_a_name_and_a_visible_focus(browser):
    page = browser.new_page(viewport={"width": 1440, "height": 800})
    page.goto(EXAMPLE.as_uri())
    names = page.evaluate("""() => [...document.querySelectorAll('button, a[href], input, select')]
        .map(e => (e.getAttribute('aria-label') || e.labels?.[0]?.innerText || e.textContent || '').trim())""")
    assert all(names), names
    visible = page.evaluate("""() => [...document.querySelectorAll('button, a[href], input, select')]
        .filter(e => e.checkVisibility()).length""")
    reached = set()
    for _ in range(visible):
        page.keyboard.press("Tab")
        focus = page.evaluate("""() => { const e = document.activeElement; const s = getComputedStyle(e);
            return { id: e.dataset.key || e.getAttribute('aria-label') || e.id || e.innerText, ring: s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) >= 2 } }""")
        assert focus["ring"], f"no visible focus on {focus['id']}"
        reached.add(focus["id"])
    assert len(reached) == visible
    page.close()


def test_a_preview_prop_that_is_not_a_listed_value_falls_back_to_its_default(browser):
    page = browser.new_page()
    page.goto(f"{EXAMPLE.as_uri()}?theme=purple&view=nope&role=root")
    assert page.evaluate("document.documentElement.dataset.theme") == "dark"
    assert page.locator('[data-dataset="workspaces"] [data-state="ready"]').count() == 1
    page.close()


def test_a_destructive_action_asks_first_and_gives_the_focus_back(browser):
    page = browser.new_page()
    page.goto(EXAMPLE.as_uri())
    delete = page.get_by_role("button", name="Delete sandbox-1")
    delete.click()
    assert page.locator("dialog[open]").count() == 1
    assert page.evaluate("document.activeElement.textContent") == "Cancel"
    page.keyboard.press("Escape")
    assert page.locator("dialog[open]").count() == 0
    assert page.evaluate("document.activeElement.getAttribute('aria-label')") == "Delete sandbox-1"
    delete.click()
    page.get_by_role("button", name="Delete workspace").click()
    status = page.locator('[data-dataset="workspaces"] [role="status"]')
    assert status.inner_text() == "Workspace sandbox-1 is deleted."
    assert page.evaluate("document.activeElement.getAttribute('role')") == "status"
    assert page.get_by_role("button", name="Delete sandbox-1").count() == 0
    page.close()
