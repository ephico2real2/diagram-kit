# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""diagram_kit/render.py's exit status, on every path its docstring promises.

The renderer's value is its refusals: a figure drawn in a fallback face, or a page that scrolls sideways at
375 px, looks like a design choice once it is a PNG. So every page it opens, the 375 px one included, must turn a
page error, a failed request or an HTTP error into a non-zero exit, and figure text in a fallback face fails
too. A failed render writes no PNG: the ones from the last good render stay as they were. Playwright is replaced
by a stand-in that fires those events on demand, so this needs no browser and no network;
tests/test_render_browser.py renders real pages in Chromium.
"""

from __future__ import annotations

import importlib.util
import pathlib
from types import SimpleNamespace

import pytest

RENDER = pathlib.Path(__file__).resolve().parents[1] / "diagram_kit" / "render.py"

# case -> (fired on the 375 px page?, event, payload); the cases not listed here fire nothing.
EVENTS = {
    "offline": (False, "requestfailed", SimpleNamespace(url="https://fonts.invalid/face.woff2")),
    "404": (False, "response", SimpleNamespace(url="https://fonts.invalid/face.woff2", status=404)),
    "pageerror": (False, "pageerror", RuntimeError("broken page")),
    "phone-requestfailed": (True, "requestfailed", SimpleNamespace(url="https://fonts.invalid/face.woff2")),
    "phone-404": (True, "response", SimpleNamespace(url="https://fonts.invalid/face.woff2", status=404)),
    "phone-pageerror": (True, "pageerror", RuntimeError("broken page")),
}


def _render():
    spec = importlib.util.spec_from_file_location("diagram_render", RENDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("case", ["ok", "mismatch", "scroll", "fallback-face", "crossing", "low-contrast",
                                  "dark-low-contrast", "unlabelled-dashed", *EVENTS])
def test_every_page_turns_a_failure_into_a_non_zero_exit(monkeypatch, tmp_path, case):
    render = _render()

    class Page:
        def __init__(self, phone: bool):
            self.phone, self.handlers, self.theme = phone, {}, None

        def on(self, name, callback):
            self.handlers.setdefault(name, []).append(callback)

        def goto(self, url, **kwargs):
            assert url.startswith("file:")
            on_phone, event, payload = EVENTS.get(case, (None, None, None))
            if on_phone is self.phone:
                for callback in self.handlers.get(event, []):
                    callback(payload)

        def evaluate(self, expression):
            if "setAttribute('data-theme'" in expression:
                self.theme = "dark" if "'dark'" in expression else "light"
            if expression == render.UNLOADED_FAMILIES:
                return ["no loaded face of 'IBM Plex Sans' draws its letters"] if case == "fallback-face" else []
            if expression == render.LOW_CONTRAST:
                # dark-low-contrast fails in the dark pass only, after the light PNGs were taken
                low = case == "low-contrast" or (case == "dark-low-contrast" and self.theme == "dark")
                return ['figure 1: "Ownership" at 1.22:1'] if low else []
            if expression == render.CROSSINGS:
                return ['figure 1: "a label longer than its box"'] if case == "crossing" else []
            if expression == render.DASHED_UNLABELLED:
                return ["figure 1: from (10,30) to (150,30)"] if case == "unlabelled-dashed" else []
            return (500 if case == "scroll" else 375) if "scrollWidth" in expression else True

        def locator(self, selector):
            assert selector == ".fig-scroll"
            return self

        def count(self):
            return 3 if case == "mismatch" else 4

        def nth(self, index):
            return self

        def screenshot(self, path):
            pathlib.Path(path).write_bytes(b"png")

        def close(self):
            pass

    class Browser:
        def __init__(self, *, args):
            assert args == render.CHROMIUM_ARGS       # the same text widths on Linux as on macOS

        def new_page(self, *, viewport, **kwargs):
            return Page(viewport["width"] == 375)

        def close(self):
            pass

    class Playwright:
        chromium = SimpleNamespace(launch=Browser)

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(render, "sync_playwright", Playwright)
    # The browser's part runs in a process of its own; here it runs in this one, where the stand-in is.
    monkeypatch.setattr(render, "_stage_in_child", render._stage)
    page = tmp_path / "page.html"
    page.write_text("<html><body>four figures</body></html>")
    out = tmp_path / "png"
    out.mkdir()
    previous = {f"{name}.{theme}.png": b"last good render" for name in "abcd" for theme in ("light", "dark")}
    for name, data in previous.items():
        (out / name).write_bytes(data)
    monkeypatch.setattr(render.sys, "argv", ["render.py", str(page), str(out), "a,b,c,d"])
    assert render.main() == (0 if case == "ok" else 1), case
    after = {p.name: p.read_bytes() for p in out.iterdir()}
    if case == "ok":
        assert after == {name: b"png" for name in previous}, case
    else:
        assert after == previous, case  # the 375 px and dark-theme failures included, and no staging dir left
