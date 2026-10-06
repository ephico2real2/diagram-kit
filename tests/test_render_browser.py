"""diagram_kit/render.py on real pages in Chromium, one per check, with no network.

Each page is built in tmp_path. Its one web face is tests/fixtures/fonts/Inter-latin.woff2 (OFL-1.1, beside it),
inlined as a data: URL, so no test reaches the network and none depends on Google Fonts being up.
"""

from __future__ import annotations

import base64
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RENDER = ROOT / "diagram_kit" / "render.py"
INTER = base64.b64encode((ROOT / "tests" / "fixtures" / "fonts" / "Inter-latin.woff2").read_bytes()).decode()


def page(family: str = "Inter, sans-serif", *, font_data: str = INTER, head: str = "", body: str = "",
         scroller: str = "overflow-x: auto", figures: int = 1, label: str = "a label in its box") -> str:
    """A page in the template's shape: a .fig-scroll holding an SVG at least 760 px wide, one label in one box."""
    figure = (f'<div class="fig-scroll" style="{scroller}"><svg viewBox="0 0 760 60" role="img" '
              f'aria-label="A test figure." style="display:block;width:100%;min-width:760px">'
              f'<rect x="4" y="12" width="200" height="32" fill="none" stroke="currentColor"/>'
              f'<text x="16" y="33" font-family="{family}" font-size="13">{label}</text></svg></div>')
    return ('<!doctype html><html><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<style>@font-face {{ font-family: "Inter"; src: url(data:font/woff2;base64,{font_data}) format("woff2"); }}'
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
    assert "light: figure text in a fallback face: no loaded @font-face declares 'IBM Plex Sans'" in result.stderr


def test_a_declared_face_that_does_not_decode_fails(tmp_path):
    # A data: URL is not a network request, so only the face check sees this one.
    result = render(tmp_path, page(font_data=base64.b64encode(b"not a font").decode()))
    assert result.returncode == 1
    assert "no loaded @font-face declares 'Inter'" in result.stderr


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
