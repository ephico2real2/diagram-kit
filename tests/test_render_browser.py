# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""diagram_kit/render.py on real pages in Chromium, one per check, with no network.

Each page is built in tmp_path. Its one web face is tests/fixtures/fonts/Inter-latin.woff2 (OFL-1.1, beside it),
inlined as a data: URL, so no test reaches the network and none depends on Google Fonts being up.
"""

from __future__ import annotations

import base64
import importlib.util
import pathlib
import subprocess
import sys

import pytest
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
RENDER = ROOT / "diagram_kit" / "render.py"
INTER = base64.b64encode((ROOT / "tests" / "fixtures" / "fonts" / "Inter-latin.woff2").read_bytes()).decode()


def page(family: str = "Inter, sans-serif", *, font_data: str = INTER, font_descriptors: str = "",
         head: str = "", body: str = "", scroller: str = "overflow-x: auto", figures: int = 1,
         label: str = "a label in its box") -> str:
    """A page in the template's shape: a .fig-scroll holding an SVG at least 760 px wide, one label in one box."""
    figure = (f'<div class="fig-scroll" style="{scroller}"><svg viewBox="0 0 760 60" role="img" '
              f'aria-label="A test figure." style="display:block;width:100%;min-width:760px">'
              f'<rect x="4" y="12" width="200" height="32" fill="none" stroke="currentColor"/>'
              f'<text x="16" y="33" font-family="{family}" font-size="13">{label}</text></svg></div>')
    return ('<!doctype html><html><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<style>@font-face {{ font-family: "Inter"; src: url(data:font/woff2;base64,{font_data}) '
            f'format("woff2"); {font_descriptors} }}'
            f'body {{ margin: 0; }}</style>{head}</head><body>{body}{figure * figures}</body></html>')


def render(tmp_path: pathlib.Path, html: str, names: str = "fig") -> subprocess.CompletedProcess:
    source = tmp_path / "page.html"
    source.write_text(html)
    return subprocess.run([sys.executable, str(RENDER), str(source), str(tmp_path / "out"), names],
                          capture_output=True, text=True, timeout=120)


def test_a_page_drawn_in_its_declared_face_renders_both_themes(tmp_path):
    result = render(tmp_path, page())
    assert result.returncode == 0, result.stderr
    assert sorted(p.name for p in (tmp_path / "out").glob("*.png")) == ["fig.dark.png", "fig.light.png"]
    assert "375 px viewport: scrollWidth 375" in result.stdout


def test_a_generic_family_is_not_a_fallback(tmp_path):
    result = render(tmp_path, page("sans-serif"))
    assert result.returncode == 0, result.stderr


def test_a_family_no_stylesheet_declares_fails(tmp_path):
    # The gap #436 measured: every request succeeds, and the text is drawn in a fallback face.
    result = render(tmp_path, page("'IBM Plex Sans', sans-serif"))
    assert result.returncode == 1
    assert ("light: figure text in a fallback face: no loaded face of 'IBM Plex Sans' draws its letters and digits"
            in result.stderr)


def test_a_declared_face_that_does_not_decode_fails(tmp_path):
    # A data: URL is not a network request, so only the face check sees this one.
    result = render(tmp_path, page(font_data=base64.b64encode(b"not a font").decode()))
    assert result.returncode == 1
    assert "figure text in a fallback face: loading 'Inter' failed (NetworkError" in result.stderr


def test_a_loaded_face_that_does_not_draw_the_label_fails(tmp_path):
    # Inter loads for "A" only, so every other letter of the label falls back: a check of loaded family names passes it.
    result = render(tmp_path, page(label="A Ownership", font_descriptors="unicode-range: U+0041;"))
    assert result.returncode == 1
    assert "no loaded face of 'Inter' draws its letters and digits" in result.stderr


def test_a_stylesheet_that_does_not_load_fails(tmp_path):
    missing = (tmp_path / "missing.css").as_uri()
    result = render(tmp_path, page(head=f'<link rel="stylesheet" href="{missing}">'))
    assert result.returncode == 1
    assert f"light: did not load: {missing}" in result.stderr


def test_a_page_error_fails(tmp_path):
    result = render(tmp_path, page(body="<script>throw new Error('boom')</script>"))
    assert result.returncode == 1
    assert "light: page error: " in result.stderr and "boom" in result.stderr


def test_a_name_count_that_does_not_match_the_figures_fails(tmp_path):
    result = render(tmp_path, page(figures=2), names="only-one")
    assert result.returncode == 1
    assert "2 .fig-scroll figures but 1 names given" in result.stderr


def test_text_is_as_wide_on_linux_as_on_macos(tmp_path):
    # Forty "i" in Inter at 10.5 px: 101.7 px on macOS, and on Linux 77.3 px with Chromium's default hinting and
    # 101.7 px without it (measured 2026-10-07). A page checked in CI must be the page a person rendered.
    module = load_renderer()
    source = tmp_path / "page.html"
    source.write_text(page(label="i" * 40).replace('font-size="13"', 'font-size="10.5"'))
    with sync_playwright() as p:
        browser = p.chromium.launch(args=module.CHROMIUM_ARGS)
        tab = browser.new_page(viewport={"width": 1180, "height": 900}, device_scale_factor=2)
        tab.goto(source.as_uri(), wait_until="networkidle")
        width = tab.evaluate("document.fonts.ready.then(() => document.querySelector('svg text')"
                             ".getComputedTextLength())")
        browser.close()
    assert width == pytest.approx(101.7, abs=0.5)


def check(tmp_path: pathlib.Path, **pages: str) -> subprocess.CompletedProcess:
    """diagram-render --check on the pages given, run from tmp_path so that the pages are named as a job names them."""
    for name, html in pages.items():
        (tmp_path / f"{name}.html").write_text(html)
    return subprocess.run([sys.executable, str(RENDER), "--check", *(f"{name}.html" for name in pages)],
                          capture_output=True, text=True, timeout=180, cwd=tmp_path)


def test_check_runs_every_check_on_every_page_and_writes_nothing(tmp_path):
    result = check(tmp_path, one=page(), three=page(figures=3))
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["ok    one.html (1 figures)", "ok    three.html (3 figures)",
                                          "2 of 2 pages pass"]
    assert sorted(p.name for p in tmp_path.rglob("*")) == ["one.html", "three.html"]      # no PNG, nothing staged


def test_check_fails_when_one_page_fails_and_names_it(tmp_path):
    result = check(tmp_path, good=page(), long=page(label="NOT_FOUND → 404, ALREADY_EXISTS → 409"),
                   wide=page(scroller="overflow: visible"))
    assert result.returncode == 1
    assert result.stdout.splitlines() == ["ok    good.html (1 figures)", "FAIL  long.html", "FAIL  wide.html",
                                          "1 of 3 pages pass"]
    assert 'FAIL: long.html: text crosses the edge of a box in figure 1: "NOT_FOUND → 404, ALREADY_EXISTS → 409"' \
        in result.stderr
    assert "FAIL: wide.html: the page scrolls sideways at 375 px" in result.stderr
    assert sorted(p.name for p in tmp_path.rglob("*")) == ["good.html", "long.html", "wide.html"]


def test_check_fails_a_page_that_holds_no_figure(tmp_path):
    # A page whose figures lost their class would otherwise pass every check: there would be nothing to check.
    result = check(tmp_path, empty=page(figures=0))
    assert result.returncode == 1
    assert "FAIL: empty.html: no .fig-scroll figure on the page" in result.stderr


def test_check_goes_on_past_a_page_it_cannot_read(tmp_path):
    # A page that is missing, or is not UTF-8, raised: a traceback, no line for any page, and the pages after it
    # never checked. It is a page that fails, named like the others.
    (tmp_path / "latin1.html").write_bytes(page(label="caf\u00e9").encode("latin-1"))
    (tmp_path / "good.html").write_text(page())
    result = subprocess.run([sys.executable, str(RENDER), "--check", "gone.html", "latin1.html", "good.html"],
                            capture_output=True, text=True, timeout=180, cwd=tmp_path)
    assert result.returncode == 1
    assert result.stdout.splitlines() == ["FAIL  gone.html", "FAIL  latin1.html", "ok    good.html (1 figures)",
                                          "1 of 3 pages pass"]
    assert "FAIL: gone.html: FileNotFoundError" in result.stderr
    assert "FAIL: latin1.html: UnicodeDecodeError" in result.stderr
    assert "Traceback" not in result.stderr


def load_renderer():
    spec = importlib.util.spec_from_file_location("diagram_render", RENDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NEVER_ENDS = "<script>addEventListener('load', () => setTimeout(() => { while (true) {} }, 50))</script>"


def test_check_fails_a_page_whose_script_never_ends_and_checks_the_next(tmp_path, monkeypatch, capsys):
    # Playwright has no limit on an evaluation: without ours this waited for ever (still waiting at 330 s).
    module = load_renderer()
    monkeypatch.setattr(module, "PAGE_SECONDS", 6)
    (tmp_path / "loop.html").write_text(page(body=NEVER_ENDS))
    (tmp_path / "good.html").write_text(page())
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(module.sys, "argv", ["render.py", "--check", "loop.html", "good.html"])
    assert module.main() == 1
    said = capsys.readouterr()
    assert said.out.splitlines() == ["FAIL  loop.html", "ok    good.html (1 figures)", "1 of 2 pages pass"]
    assert "FAIL: loop.html: TimeoutError: not checked in 6 s: a script on the page that never ends?" in said.err
    assert sorted(p.name for p in tmp_path.rglob("*")) == ["good.html", "loop.html"]


def test_a_page_whose_script_never_ends_fails_the_render_and_writes_nothing(tmp_path, monkeypatch, capsys):
    module = load_renderer()
    monkeypatch.setattr(module, "PAGE_SECONDS", 6)
    (tmp_path / "loop.html").write_text(page(body=NEVER_ENDS))
    monkeypatch.setattr(module.sys, "argv", ["render.py", str(tmp_path / "loop.html"), str(tmp_path / "out"), "fig"])
    assert module.main() == 1
    assert "FAIL: not checked in 6 s: a script on the page that never ends?" in capsys.readouterr().err
    assert list((tmp_path / "out").iterdir()) == []                          # no PNG, and no staging directory left


def test_a_page_that_scrolls_sideways_at_375_px_fails(tmp_path):
    # Without overflow-x: auto on .fig-scroll, the 760 px figure widens the page instead of scrolling inside it.
    result = render(tmp_path, page(scroller="overflow: visible"))
    assert result.returncode == 1
    assert "the page scrolls sideways at 375 px" in result.stderr


def test_a_label_that_runs_past_its_box_fails(tmp_path):
    # The shape of envoy-grpc-modernization's "NOT_FOUND → 404, ALREADY_EXISTS → 409", whose "409" crosses its box.
    result = render(tmp_path, page(label="NOT_FOUND → 404, ALREADY_EXISTS → 409"))
    assert result.returncode == 1
    assert 'text crosses the edge of a box in figure 1: "NOT_FOUND → 404, ALREADY_EXISTS → 409"' in result.stderr


def test_text_with_no_fill_on_a_dark_figure_fails_in_the_dark_theme(tmp_path):
    # The shape of mongodb-poc's "Ownership" legend: no fill, so black, readable in light and lost in dark.
    dark = '<style>:root[data-theme="dark"] .fig-scroll { background: #151c25; }</style>'
    result = render(tmp_path, page(head=dark, label="Ownership"))
    assert result.returncode == 1
    assert 'dark: text under 4.5:1 contrast in figure 1: "Ownership" at 1.22:1' in result.stderr
    assert "light: text under" not in result.stderr


def test_contrast_is_measured_against_the_last_box_painted_under_the_text(tmp_path):
    # The measured pair: --none #6b7684 on --none-wash #eef0f3 is 4.04:1 and fails; the template's #5f6a77 is 4.82:1
    # and passes. Each wash is painted over a dark box, so only the last box under the text gives these verdicts.
    def figure(fill: str) -> str:
        return ('<div class="fig-scroll"><svg viewBox="0 0 760 60" role="img" aria-label="A test figure." '
                'style="display:block;width:100%;min-width:760px">'
                '<rect x="4" y="8" width="320" height="44" fill="#151c25"/>'
                '<rect x="8" y="12" width="300" height="36" fill="#eef0f3"/>'
                f'<text x="16" y="35" font-family="Inter, sans-serif" font-size="13" fill="{fill}">denied</text>'
                '</svg></div>')
    result = render(tmp_path, page(body=figure("#6b7684") + figure("#5f6a77"), figures=0), names="old,new")
    assert result.returncode == 1
    assert 'light: text under 4.5:1 contrast in figure 1: "denied" at 4.04:1' in result.stderr
    assert "figure 2" not in result.stderr


def test_a_name_in_a_subdirectory_renders_the_whole_set(tmp_path):
    # Before staging, Playwright's screenshot made the directory a name carries. The move must too, or the render
    # stops half way through the moves with a traceback: one figure's PNGs replaced, the other's not.
    result = render(tmp_path, page(figures=2), names="a,sub/b")
    assert result.returncode == 0, result.stderr
    out = tmp_path / "out"
    assert sorted(str(p.relative_to(out)) for p in out.rglob("*.png")) == [
        "a.dark.png", "a.light.png", "sub/b.dark.png", "sub/b.light.png"]


def dashed_figure(arrow: str, label: str = "") -> str:
    """A figure with two boxes and one connector between them, and optionally a free label."""
    return ('<div class="fig-scroll" style="overflow-x: auto"><svg viewBox="0 0 760 120" role="img" aria-label="A test figure." '
            'style="display:block;width:100%;min-width:760px">'
            '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>'
            '<rect x="10" y="40" width="140" height="40" fill="none" stroke="currentColor"/>'
            # right-aligned against the arrow's start, as a box's text often is: it must not pass for the label
            '<text x="144" y="65" text-anchor="end" font-family="Inter, sans-serif" font-size="13" '
            'fill="currentColor">envoy</text>'
            '<rect x="560" y="40" width="140" height="40" fill="none" stroke="currentColor"/>'
            '<text x="574" y="65" font-family="Inter, sans-serif" font-size="13" fill="currentColor">service</text>'
            f'{arrow}{label}</svg></div>')


DASHED_ARROW = ('<path d="M150,60 C350,60 350,60 558,60" fill="none" stroke="currentColor" stroke-dasharray="6 5" '
                'marker-end="url(#ah)"/>')


def test_a_dashed_arrow_with_no_label_fails(tmp_path):
    # The box texts sit at both ends of the arrow and do not count: a box's own text is not the arrow's label.
    result = render(tmp_path, page(body=dashed_figure(DASHED_ARROW), figures=0))
    assert result.returncode == 1
    assert "a dashed arrow with no label beside it in figure 1: from (150,60) to (558,60)" in result.stderr


def test_a_dashed_arrow_with_its_label_beside_it_renders(tmp_path):
    label = '<text x="320" y="52" font-family="Inter, sans-serif" font-size="12" fill="currentColor">DNS lookup</text>'
    result = render(tmp_path, page(body=dashed_figure(DASHED_ARROW, label), figures=0))
    assert result.returncode == 0, result.stderr


def test_dashed_shapes_that_are_not_arrows_render(tmp_path):
    # A dashed box is a proposal and a dashed line with no marker is a lane divider: neither needs an arrow label.
    shapes = ('<rect x="300" y="40" width="140" height="40" fill="none" stroke="currentColor" stroke-dasharray="5 4"/>'
              '<line x1="480" y1="10" x2="480" y2="110" stroke="currentColor" stroke-dasharray="6 5"/>'
              '<line x1="150" y1="60" x2="298" y2="60" stroke="currentColor" marker-end="url(#ah)"/>')
    result = render(tmp_path, page(body=dashed_figure(shapes), figures=0))
    assert result.returncode == 0, result.stderr


def test_a_label_inside_a_box_drawn_around_the_arrow_counts(tmp_path):
    # A cluster box drawn around both the arrow and its label is a container, not the box the label belongs to: the
    # text beside the line labels it (mongodb-poc mongot-openshift's sync legs, 2026-10-06).
    around = ('<rect x="160" y="20" width="390" height="90" fill="none" stroke="currentColor"/>'
              '<text x="320" y="52" font-family="Inter, sans-serif" font-size="12" fill="currentColor">sync leg</text>')
    result = render(tmp_path, page(body=dashed_figure(DASHED_ARROW, around), figures=0))
    assert result.returncode == 0, result.stderr


def test_a_box_text_beside_an_arrow_inside_a_container_is_still_not_a_label(tmp_path):
    # The end boxes keep their own text out, container or not: only the container's free text is the label.
    around = '<rect x="2" y="20" width="720" height="90" fill="none" stroke="currentColor"/>'
    result = render(tmp_path, page(body=dashed_figure(DASHED_ARROW, around), figures=0))
    assert result.returncode == 1
    assert "a dashed arrow with no label beside it in figure 1" in result.stderr


def test_an_end_box_holding_the_arrows_midpoint_is_still_a_box(tmp_path):
    # An arrow drawn from inside its start box (centre to centre, the box painted over it) has its midpoint in that
    # box: the box holds one end, so it is the arrow's end box, not a container, and its own text is not the label.
    figure = ('<div class="fig-scroll" style="overflow-x: auto"><svg viewBox="0 0 760 120" role="img" '
              'aria-label="A test figure." style="display:block;width:100%;min-width:760px">'
              '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
              'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>'
              '<path d="M200,60 L558,60" fill="none" stroke="currentColor" stroke-dasharray="6 5" '
              'marker-end="url(#ah)"/>'
              '<rect x="10" y="40" width="400" height="40" fill="var(--surface, #fff)" stroke="currentColor"/>'
              '<text x="404" y="65" text-anchor="end" font-family="Inter, sans-serif" font-size="13" '
              'fill="currentColor">envoy</text>'
              '<rect x="560" y="40" width="140" height="40" fill="none" stroke="currentColor"/>'
              '<text x="574" y="65" font-family="Inter, sans-serif" font-size="13" fill="currentColor">service</text>'
              '</svg></div>')
    result = render(tmp_path, page(body=figure, figures=0))
    assert result.returncode == 1
    assert "a dashed arrow with no label beside it in figure 1: from (200,60) to (558,60)" in result.stderr


def test_a_chip_on_the_line_labels_the_arrow(tmp_path):
    # A chip drawn on the line holds the midpoint and neither end: its text names the arrow.
    chip = ('<rect x="300" y="48" width="110" height="24" rx="12" fill="#fff" stroke="currentColor"/>'
            '<text x="312" y="65" font-family="Inter, sans-serif" font-size="12" fill="currentColor">DNS lookup</text>')
    result = render(tmp_path, page(body=dashed_figure(DASHED_ARROW, chip), figures=0))
    assert result.returncode == 0, result.stderr
