#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Render every .fig-scroll figure of a diagram page to light and dark PNGs, and check the page.

    diagram-render <page.html> <out-dir> <name-1>,<name-2>,...      (installed)
    python diagram_kit/render.py <page.html> <out-dir> <name-1>,<name-2>,...

One name per .fig-scroll, in document order; each becomes <out-dir>/<name>.light.png and
<name>.dark.png at 2x pixel density. The page may be a fragment (an Artifact page starts at
<title>): it is wrapped in a document for rendering, never modified. Exit status is non-zero on
the defects a code review of the SVG text does not see:
  - a page error;
  - a request that did not load, or answered an HTTP error (a web font that fails leaves the
    figures in a fallback face);
  - figure text whose letters or digits no loaded face of its font family draws (the same fallback,
    with every request answered 200, or a face whose unicode-range leaves the text out);
  - figure text that crosses the edge of a box (a label longer than its box);
  - a dashed arrow with no label beside it (a dashed arrow is a relationship, and names it);
  - figure text under 4.5:1 contrast with the box it sits in, in either theme (WCAG 1.4.3);
  - a name/figure count mismatch;
  - horizontal page scroll at 375 px.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("playwright is not installed: python3 -m pip install playwright && python3 -m playwright install chromium")

# Figure text in a fallback face: for each first family the text asks for (generic families excepted), every
# letter and decimal digit it draws must come from a loaded face of that family. A stylesheet answering 200 can still
# leave a family out (Google Fonts drops an unknown family and returns CSS for the rest), and a face can load for a
# unicode-range that leaves the text out; in both no request fails while the text falls back (#436, 2026-09-27).
# Symbols (arrows, circled digits) are not checked: the IBM Plex subsets do not carry them (RESEARCH.md §3).
UNLOADED_FAMILIES = r"""async () => {
  const name = (f) => f.trim().replace(/^["']|["']$/g, "");
  const generic = new Set(["serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui", "ui-serif",
    "ui-sans-serif", "ui-monospace", "ui-rounded", "math", "emoji", "fangsong", "-apple-system",
    "blinkmacsystemfont"]);
  const requests = new Map();
  await document.fonts.ready;
  for (const el of document.querySelectorAll(".fig-scroll *")) {
    if (![...el.childNodes].some((n) => n.nodeType === Node.TEXT_NODE && n.textContent.trim())) continue;
    const style = getComputedStyle(el);
    const family = name(style.fontFamily.split(",")[0]);
    if (generic.has(family.toLowerCase())) continue;
    // No stretch: computed font-stretch is a percentage, which the font shorthand refuses (SyntaxError).
    const spec = `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${JSON.stringify(family)}`;
    if (!requests.has(spec)) requests.set(spec, {family, spec, chars: new Set()});
    for (const char of el.textContent)
      if (/[\p{L}\p{Nd}]/u.test(char)) requests.get(spec).chars.add(char);
  }
  const failed = new Set();
  for (const {family, spec, chars} of requests.values()) {
    for (const char of chars) {
      let faces;
      try { faces = await document.fonts.load(spec, char); }
      catch (e) { failed.add(`loading '${family}' failed (${e.name}: ${e.message})`); break; }
      if (!faces.some((face) => face.status === "loaded" &&
                                name(face.family).toLowerCase() === family.toLowerCase())) {
        failed.add(`no loaded face of '${family}' draws its letters and digits`);
        break;
      }
    }
  }
  return [...failed].sort();
}"""

# Dashed arrows (a line, path or polyline with a dasharray and a marker) with no label beside them. A dashed arrow is
# a relationship that carries no traffic, so the reader must be told which one (STANDARD.md §3, Connectors). A label
# is a <text> whose bounds come within 16 px of a point sampled every 4 units along the arrow, and that is not a box's
# own text (a box's text sits beside every arrow that ends there). A box that holds the arrow's midpoint is a container
# around it (a cluster drawn around the arrow and its label, or a chip on the line), so its text can label the arrow.
# Dashed boxes (proposed) and dashed lines without a marker (lane dividers) are not arrows.
DASHED_UNLABELLED = """() => [...document.querySelectorAll(".fig-scroll")].flatMap((figure, i) => {
  const rects = [...figure.querySelectorAll("rect")].map((r) => r.getBoundingClientRect());
  const texts = [...figure.querySelectorAll("text")].map((t) => t.getBoundingClientRect()).filter((b) => b.width);
  const inside = (r, x, y) => x > r.left && x < r.right && y > r.top && y < r.bottom;
  const centre = (b) => [(b.left + b.right) / 2, (b.top + b.bottom) / 2];
  const near = (p, b) =>
    Math.hypot(Math.max(b.left - p.x, 0, p.x - b.right), Math.max(b.top - p.y, 0, p.y - b.bottom)) <= 16;
  return [...figure.querySelectorAll("line, path, polyline")].filter((el) => {
    if (el.closest("marker")) return false;
    const s = getComputedStyle(el);
    return s.strokeDasharray !== "none" && (s.markerEnd !== "none" || s.markerStart !== "none");
  }).filter((el) => {
    const m = el.getScreenCTM(), n = el.getTotalLength(), points = [];
    for (let d = 0; d <= n + 4; d += 4) {
      const p = el.getPointAtLength(Math.min(d, n));
      points.push(new DOMPoint(p.x, p.y).matrixTransform(m));
    }
    const mid = points[Math.floor(points.length / 2)];
    const boxes = rects.filter((r) => !inside(r, mid.x, mid.y));
    const labels = texts.filter((b) => !boxes.some((r) => inside(r, ...centre(b))));
    return !points.some((p) => labels.some((b) => near(p, b)));
  }).map((el) => {
    const a = el.getPointAtLength(0), b = el.getPointAtLength(el.getTotalLength());
    return `figure ${i + 1}: from (${Math.round(a.x)},${Math.round(a.y)}) to (${Math.round(b.x)},${Math.round(b.y)})`;
  });
})"""

# Figure text whose box is partly inside and partly outside a <rect>: a label that ran past its box, which the
# template's 6.3 px-per-character budget only estimates. Measured in the face actually drawn, after it loaded.
CROSSINGS = """() => [...document.querySelectorAll(".fig-scroll")].flatMap((figure, i) => {
  const boxes = [...figure.querySelectorAll("rect")].map((r) => r.getBoundingClientRect()).filter((r) => r.width && r.height);
  const crosses = (t) => boxes.some((r) => {
    const overlap = Math.min(t.right, r.right) - Math.max(t.left, r.left) > 1 && Math.min(t.bottom, r.bottom) - Math.max(t.top, r.top) > 1;
    const inside = t.left >= r.left - 1 && t.top >= r.top - 1 && t.right <= r.right + 1 && t.bottom <= r.bottom + 1;
    const covers = t.left <= r.left + 1 && t.top <= r.top + 1 && t.right >= r.right - 1 && t.bottom >= r.bottom - 1;
    return overlap && !inside && !covers;
  });
  return [...figure.querySelectorAll("text")].filter((t) => t.textContent.trim() && crosses(t.getBoundingClientRect()))
    .map((t) => `figure ${i + 1}: ${JSON.stringify(t.textContent.trim())}`);
})"""

# Figure text under 4.5:1 (WCAG 2.2 SC 1.4.3, normal text) against what is painted under it: the last filled
# <rect> before it in document order whose box holds it, else the figure's background. A text with no fill is
# black, which the light theme hides and the dark theme shows; fill-opacity and gradients are not modelled.
LOW_CONTRAST = """() => [...document.querySelectorAll(".fig-scroll")].flatMap((figure, i) => {
  const rgb = (c) => { const m = /^rgba?\\(([^)]+)\\)/.exec(c); const v = m ? m[1].split(/[\\s,\\/]+/).map(Number) : [];
                       return v.length < 3 || v[3] === 0 ? null : v.slice(0, 3); };
  const lum = (c) => c.map((x) => (x /= 255) <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4)
                      .reduce((sum, x, k) => sum + x * [0.2126, 0.7152, 0.0722][k], 0);
  const ground = rgb(getComputedStyle(figure).backgroundColor) || rgb(getComputedStyle(document.body).backgroundColor) || [255, 255, 255];
  const painted = [], low = [];
  for (const el of figure.querySelectorAll("rect, text")) {
    const box = el.getBoundingClientRect(), fill = rgb(getComputedStyle(el).fill);
    if (el.tagName === "rect") { if (fill) painted.push([box, fill]); continue; }
    if (!fill || !el.textContent.trim()) continue;
    const holds = painted.filter(([r]) => box.left >= r.left - 1 && box.top >= r.top - 1 && box.right <= r.right + 1 && box.bottom <= r.bottom + 1);
    const [high, dark] = [lum(fill), lum(holds.length ? holds[holds.length - 1][1] : ground)].sort((a, b) => b - a);
    const ratio = (high + 0.05) / (dark + 0.05);
    if (ratio < 4.5) low.push(`figure ${i + 1}: ${JSON.stringify(el.textContent.trim())} at ${ratio.toFixed(2)}:1`);
  }
  return low;
})"""


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    page_path, out_dir = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve()
    names = [n.strip() for n in sys.argv[3].split(",") if n.strip()]
    out_dir.mkdir(parents=True, exist_ok=True)

    text = page_path.read_text()
    if "<html" not in text.lower():
        text = ('<!doctype html><html><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'
                f"{text}</body></html>")
    failures: list[str] = []

    def watch(page, label: str) -> None:
        # Every page reports for its whole life, the 375 px one included: its load is where the sideways-scroll
        # check is measured. A failed request, not a fixed sleep, is what says the fonts are missing: Chromium keeps
        # an empty sheet for a stylesheet that failed and document.fonts.check() answers true for a face never declared.
        page.on("pageerror", lambda e: failures.append(f"{label}: page error: {e}"))
        page.on("requestfailed", lambda r: failures.append(f"{label}: did not load: {r.url}"))
        page.on("response", lambda r: failures.append(f"{label}: did not load: {r.url} ({r.status})")
                if r.status >= 400 else None)
    # PNGs are staged beside their targets (one filesystem, so the move is a rename) and moved only when every check,
    # the 375 px one included, has passed: a failed render leaves the last good PNGs as they were.
    staged: list[tuple[pathlib.Path, pathlib.Path]] = []
    with (tempfile.TemporaryDirectory() as tmp,
          tempfile.TemporaryDirectory(dir=out_dir, prefix=".diagram-render-") as stage,
          sync_playwright() as p):
        doc = pathlib.Path(tmp) / "page.html"
        doc.write_text(text)
        browser = p.chromium.launch()
        for theme in ("light", "dark"):
            page = browser.new_page(viewport={"width": 1180, "height": 900}, device_scale_factor=2)
            watch(page, theme)
            page.goto(doc.as_uri(), wait_until="networkidle")
            page.evaluate(f"() => document.documentElement.setAttribute('data-theme', '{theme}')")
            failures.extend(f"{theme}: figure text in a fallback face: {reason}"
                            for reason in page.evaluate(UNLOADED_FAMILIES))
            failures.extend(f"{theme}: text under 4.5:1 contrast in {text}" for text in page.evaluate(LOW_CONTRAST))
            if theme == "light":  # the geometry is the same in both themes
                failures.extend(f"text crosses the edge of a box in {text}" for text in page.evaluate(CROSSINGS))
                failures.extend(f"a dashed arrow with no label beside it in {arrow}"
                                for arrow in page.evaluate(DASHED_UNLABELLED))
            if failures:
                break
            figures = page.locator(".fig-scroll")
            if figures.count() != len(names):
                failures.append(f"{figures.count()} .fig-scroll figures but {len(names)} names given")
                break
            for i, name in enumerate(names):
                png = pathlib.Path(stage) / f"{i}.{theme}.png"
                figures.nth(i).screenshot(path=str(png))
                staged.append((png, out_dir / f"{name}.{theme}.png"))
            page.close()
        phone = browser.new_page(viewport={"width": 375, "height": 800})
        watch(phone, "375 px")
        phone.goto(doc.as_uri(), wait_until="networkidle")
        width = phone.evaluate("document.fonts.ready.then(() => document.documentElement.scrollWidth)")
        if width > 375:
            failures.append(f"the page scrolls sideways at 375 px (scrollWidth {width})")
        browser.close()
        if not failures:
            # A name may carry a subdirectory, which the screenshot used to make: make each one before the first
            # move, so a missing directory cannot stop the moves half way.
            for _, target in staged:
                target.parent.mkdir(parents=True, exist_ok=True)
            for png, target in staged:
                png.replace(target)
                print(f"wrote {target} ({target.stat().st_size} bytes)")
    print(f"375 px viewport: scrollWidth {width}")
    for f in failures:
        print(f"FAIL: {f}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
