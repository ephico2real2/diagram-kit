# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""State-name boundaries and the documented scope of --check."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("review_render", ROOT / "diagram_kit/render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)


@pytest.mark.parametrize(("names", "count"), [
    (["x-after", "x-before"], 1),
    (["a-before", "b-today"], 0),
    (["target", "before-after"], 0),  # Multiple ranks are explicitly exempt.
    (["after", "beforehand"], 0),
    (["after", "thereafter"], 0),
    (["AFTER", "BEFORE"], 1),
    (["flow/after", "flow/before"], 1),
    (["after/path", "before/path"], 0),  # Only the filename is a figure name.
])
def test_state_name_boundaries(names, count):
    assert len(render.state_order(names)) == count


def test_check_without_names_has_no_state_order_input(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(render, "state_order", lambda names: calls.append(names) or [])
    monkeypatch.setattr(render, "_stage_in_child", lambda *args: {
        "failures": [], "count": 2, "width": 375})
    monkeypatch.setattr(render.sys, "argv", ["diagram-render", "--check", str(tmp_path / "page.html")])
    assert render.main() == 0
    assert calls == []


def test_check_documents_the_limits_of_unnamed_figures():
    skill = (ROOT / "skill/visual/SKILL.md").read_text()
    paragraph = skill.split("`diagram-render --check <page.html>...`", 1)[1].split("\n\n", 1)[0]
    assert "except" in paragraph and "state order" in paragraph and "name/figure count" in paragraph
    assert "except" in render.render_page.__doc__ and "state order" in render.render_page.__doc__
    assert "except name/figure count and state order" in render.__doc__
