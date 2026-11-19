# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The pandoc filter of the delivery playbook: each figure is its light render, the only render there is.

Each test runs pandoc on a small document. They are skipped where pandoc is not installed, except in CI (ci.yml
installs it): there a missing pandoc fails them.
"""

from __future__ import annotations

from html.parser import HTMLParser
import os
import pathlib
import re
import shutil
import subprocess

import pytest

SKILL = pathlib.Path(__file__).resolve().parent.parent / "skill" / "delivery-playbook"
needs_pandoc = pytest.mark.skipif(shutil.which("pandoc") is None and not os.environ.get("CI"),
                                  reason="pandoc is not installed")

DECK = "## A slide\n\n![Rate &quot;p95&quot; of the API](figures/rate.light.png)\n"


def build(tmp_path: pathlib.Path, text: str, *filters: str) -> str:
    source = tmp_path / "in.md"
    source.write_text(text, encoding="utf-8")
    args = ["pandoc", str(source), "-t", "html5"]
    for name in filters:
        args += ["--lua-filter", str(SKILL / name)]
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def tags(html: str) -> list[str]:
    return re.findall(r"<(?:img|source)\b[^>]*>", html)


@needs_pandoc
def test_the_deck_shows_only_the_light_render(tmp_path):
    # The figures are light only (the owner, 2026-11-18): one image, and no dark one for the page CSS to swap in.
    html = build(tmp_path, DECK, "deck.lua")
    found = tags(html)
    assert len(found) == 1
    assert 'class="fig"' in found[0] and 'src="figures/rate.light.png"' in found[0]
    assert "dark" not in html


@needs_pandoc
def test_an_alt_text_with_a_quote_stays_inside_its_attribute(tmp_path):
    found = tags(build(tmp_path, DECK, "deck.lua"))
    assert len(found) == 1
    assert 'alt="Rate &quot;p95&quot; of the API"' in found[0]


@needs_pandoc
def test_the_client_build_commands_use_the_shared_templates(tmp_path):
    for name in ("PLAYBOOK.md", "DECK.md"):
        shutil.copyfile(SKILL / name, tmp_path / name)
    figures = tmp_path / "figures"
    figures.mkdir()
    for source in (SKILL / "figures").glob("*.png"):
        shutil.copyfile(source, figures / source.name)
    recipe = (SKILL / "SKILL.md").read_text().split("```sh\n", 1)[1].split("\n```", 1)[0]
    commands = [line for line in recipe.replace("\\\n", "").splitlines() if line.startswith("pandoc ")]
    assert len(commands) == 3
    environment = dict(os.environ, playbook_templates=str(SKILL))
    for command in commands:
        subprocess.run(["/bin/sh", "-c", command], cwd=tmp_path, env=environment,
                       check=True, capture_output=True, text=True)
    for name in ("playbook.html", "playbook.pptx", "deck.html"):
        assert (tmp_path / name).stat().st_size > 0
    # Each built page shows the five figures, light, and names no dark render.
    for name in ("playbook.html", "deck.html"):
        html = (tmp_path / name).read_text()
        assert len(re.findall(r'<img [^>]*src="figures/[a-z-]+\.light\.png"', html)) == 5, name
        assert ".dark.png" not in html and "<source" not in html, name


@needs_pandoc
def test_the_deck_preserves_entity_text_in_figure_paths(tmp_path):
    class Images(HTMLParser):
        def __init__(self):
            super().__init__()
            self.sources = []

        def handle_starttag(self, tag, attrs):
            if tag == "img":
                self.sources.append(dict(attrs)["src"])

    text = "![Rate](figures/rate&amp;copy;.light.png)\n"
    plain = Images()
    plain.feed(build(tmp_path, text))
    assert plain.sources == ["figures/rate&copy;.light.png"]
    themed = Images()
    themed.feed(build(tmp_path, text, "deck.lua"))
    assert themed.sources == ["figures/rate&copy;.light.png"]
