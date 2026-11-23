# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Figures are light only (the owner, 2026-11-18): the kit ships no dark render, and nothing in it tells a writer to make
or embed one.

The renderer's side is tested in test_render.py and test_render_browser.py. This file reads the kit's own files: no dark
PNG is kept, no figure page carries a dark palette, and no document or skill embeds a dark `<source>` or says to render
a light and a dark PNG. RESEARCH.md and the review records in docs/reviews/ are measurements and decisions as they were
taken, so they are not read. The mockup and app skills keep their dark themes: an app's theme is not a figure.
"""

from __future__ import annotations

import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIPPED = {".git", ".tmp", ".venv", "out", "node_modules", "__pycache__"}
HISTORY = {ROOT / "RESEARCH.md", ROOT / "docs" / "reviews"}


def _kit_files(*suffixes: str) -> list[pathlib.Path]:
    return sorted(p for p in ROOT.rglob("*") if p.is_file() and p.suffix in suffixes
                  and not SKIPPED.intersection(p.relative_to(ROOT).parts)
                  and not any(p == h or h in p.parents for h in HISTORY))


TEXTS = [p for p in _kit_files(".md", ".html", ".lua", ".css", ".js", ".yml") if ROOT / "tests" not in p.parents]
FIGURE_PAGES = [ROOT / "diagram_kit" / "template.html",
                *(p for p in _kit_files(".html") if p.name == "source.html")]

# A <source> (or a src/srcset) that serves a dark render, GitHub's retired dark-only fragment, and the instruction to
# render both themes.
DARK_EMBED = re.compile(r"<source\b[^>]*(prefers-color-scheme:\s*dark|\.dark\.png)"
                        r"|\b(src|srcset)=\"[^\"]*\.dark\.png"
                        r"|#gh-dark-mode-only")
BOTH_RENDERS = re.compile(r"\blight\s+and\s+(a\s+)?dark\s+(PNG|render)", re.I)
DARK_PALETTE = re.compile(r"prefers-color-scheme:\s*dark|data-theme=\"dark\"")


def _id(path: pathlib.Path) -> str:
    return str(path.relative_to(ROOT))


def test_the_scan_reads_the_files_that_teach_the_figures():
    # A glob that silently matched nothing would make every test below pass.
    names = {_id(p) for p in TEXTS}
    assert {"README.md", "STANDARD.md", "TUTORIAL.md", "skill/visual/SKILL.md", "skill/delivery-playbook/PLAYBOOK.md",
            "skill/delivery-playbook/deck.lua"} <= names
    assert {_id(p) for p in FIGURE_PAGES} >= {"diagram_kit/template.html", "examples/fan-out/source.html",
                                               "skill/delivery-playbook/figures/source.html"}


def test_no_dark_render_is_kept():
    dark = [p for p in ROOT.rglob("*.dark.png") if not SKIPPED.intersection(p.relative_to(ROOT).parts)]
    assert [_id(p) for p in dark] == []


@pytest.mark.parametrize("path", FIGURE_PAGES, ids=_id)
def test_a_figure_page_carries_no_dark_palette(path):
    assert DARK_PALETTE.findall(path.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("path", TEXTS, ids=_id)
def test_no_document_or_skill_embeds_a_dark_render_or_says_to_make_one(path):
    text = path.read_text(encoding="utf-8")
    found = [m.group(0) for m in DARK_EMBED.finditer(text)] + [m.group(0) for m in BOTH_RENDERS.finditer(text)]
    assert found == []


def test_job_scratch_files_are_not_kit_figures_or_instructions(tmp_path, monkeypatch):
    monkeypatch.setitem(globals(), "ROOT", tmp_path)
    scratch = tmp_path / ".tmp" / "job"
    scratch.mkdir(parents=True)
    (scratch / "source.html").write_text('<html data-theme="dark"></html>')
    (scratch / "fixture.dark.png").write_bytes(b"test fixture")
    (scratch / "README.md").write_text("light and dark PNG")
    (tmp_path / "README.md").write_text("light only")
    assert _kit_files(".md", ".html") == [tmp_path / "README.md"]
    test_no_dark_render_is_kept()
