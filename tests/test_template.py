"""template.html's palette: text drawn in a token stays readable on the fills the template draws it on.

WCAG 2.2 success criterion 1.4.3 asks 4.5:1 of normal text, and every figure text in the template is under the
18.66 px bold / 24 px that would make it large. The pairs are the ones the template and the pages built from it
draw: each colour token on --surface (the figure's ground) and on its own -wash (a box of that meaning), and
--ink and --muted on every wash. Reads the file only; no browser.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest

TEMPLATE = (pathlib.Path(__file__).resolve().parents[1] / "diagram_kit" / "template.html").read_text()
TOKENS = ("ink", "muted", "host", "remote", "gap", "none")
WASHES = ("host-wash", "remote-wash", "gap-wash", "none-wash")


def _block(selector: str) -> dict[str, str]:
    body = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", TEMPLATE).group(1)
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", body))


THEMES = {"light": _block(":root"), "dark": _block(':root[data-theme="dark"]')}


def _luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    high, low = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


PAIRS = [(t, "surface") for t in TOKENS] + [(t, f"{t}-wash") for t in TOKENS if t not in ("ink", "muted")] + \
        [(t, w) for t in ("ink", "muted") for w in WASHES]


def test_the_contrast_formula_matches_wcag():
    # The two ends of the scale, and a published pair: #767676 on white is the lightest grey that passes, 4.54:1.
    assert round(contrast("#000000", "#ffffff"), 2) == 21.0
    assert round(contrast("#767676", "#ffffff"), 2) == 4.54


def test_the_dark_media_query_and_the_dark_attribute_carry_the_same_palette():
    media = re.search(r'@media \(prefers-color-scheme: dark\)\s*\{\s*:root:not\(\[data-theme="light"\]\)\s*\{([^}]*)\}',
                      TEMPLATE).group(1)
    assert dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", media)) == THEMES["dark"]


@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("text,ground", PAIRS, ids=[f"{t}-on-{g}" for t, g in PAIRS])
def test_text_meets_wcag_aa_on_the_fills_it_is_drawn_on(theme, text, ground):
    palette = THEMES[theme]
    ratio = contrast(palette[text], palette[ground])
    assert ratio >= 4.5, f"{theme}: --{text} {palette[text]} on --{ground} {palette[ground]} is {ratio:.2f}:1"


def test_the_installed_kit_writes_this_template_and_never_overwrites(tmp_path):
    # The template ships inside the package, so a consumer who installed a tag starts a page with
    # `diagram-template <path>` and gets the template this version's renderer and tests were run against.
    command = str(pathlib.Path(sys.executable).with_name("diagram-template"))
    source = tmp_path / "docs" / "diagrams" / "first" / "source.html"
    assert subprocess.run([command, str(source)], capture_output=True, text=True).returncode == 0
    assert source.read_text() == TEMPLATE
    source.write_text("an edited diagram")
    again = subprocess.run([command, str(source)], capture_output=True, text=True)
    assert again.returncode == 1 and "refusing to overwrite" in again.stderr
    assert source.read_text() == "an edited diagram"
