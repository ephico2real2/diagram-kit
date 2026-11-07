# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The agile records are one standard: each issue form is valid and names its type and one status, the legend of the
playbook equals LEGEND.md, and the pull request template asks for the milestone, the issues and the class."""

from __future__ import annotations

import pathlib
import re

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGILE = ROOT / "skill" / "agile"
FORMS = sorted((AGILE / "templates" / "ISSUE_TEMPLATE").glob("[0-9]-*.yml"))
# The issue types that GitHub gives each organization. An epic has no type, because "Epic" is not a default type.
TYPES = {"Feature", "Task", "Bug"}


def table_column(text: str, header: str) -> list[str]:
    """The first column of the Markdown table whose header row starts with `header`."""
    block = text.split(header, 1)[1].split("\n\n", 1)[0]
    return [row.split("|")[1].strip() for row in block.splitlines()[2:] if row.startswith("|")]


def test_there_is_a_form_for_each_item():
    names = [yaml.safe_load(f.read_text())["name"] for f in FORMS]
    assert names == ["Epic", "Feature", "Story", "Task", "Spike", "Defect", "Owner action", "Release milestone"]


@pytest.mark.parametrize("form", FORMS, ids=lambda p: p.stem)
def test_a_form_names_its_type_and_exactly_one_status(form):
    data = yaml.safe_load(form.read_text())
    assert data["description"] and data["body"]
    assert data.get("type") in TYPES | ({None} if data["name"] == "Epic" else set())
    assert len([label for label in data["labels"] if label.startswith("status:")]) == 1


@pytest.mark.parametrize("form", FORMS, ids=lambda p: p.stem)
def test_a_form_asks_for_the_parent_and_each_dropdown_has_options(form):
    body = yaml.safe_load(form.read_text())["body"]
    assert "parent" in [item.get("id") for item in body]
    for item in body:
        if item["type"] == "dropdown":
            assert item["attributes"]["options"], item["id"]


def test_the_playbook_legend_equals_the_standard_legend():
    legend = (AGILE / "LEGEND.md").read_text()
    playbook = (ROOT / "skill" / "delivery-playbook" / "PLAYBOOK.md").read_text().split("## 14. Legend", 1)[1]
    for header in ("| Prefix |", "| Class |", "| Verdict |"):
        assert table_column(playbook, header) == table_column(legend, header), header
    assert table_column(legend, "| Prefix |")[-2:] == ["`INV`", "`TDT`"]


def test_the_classes_have_their_labels_in_the_legend():
    legend = (AGILE / "LEGEND.md").read_text()
    for label in ("`class:INV`", "`class:TDT`", "`status:open`", "`status:owner-action`", "`sev:critical`"):
        assert label in legend, label


def test_the_pull_request_template_asks_for_the_record():
    template = (ROOT / "skill" / "pull-request" / "templates" / "pull_request_template.md").read_text()
    headings = re.findall(r"^## (.+)$", template, re.M)
    for need in ("Release milestone or hotfix", "Issues", "Class", "What changes, and why", "Proof"):
        assert need in headings, need
    assert "- [ ] INV: innovation." in template and "- [ ] TDT: tech debt." in template
