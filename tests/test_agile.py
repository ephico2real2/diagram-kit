# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The agile records are one standard: each issue form is valid and names its type and one status, the legend of the
playbook equals LEGEND.md, and the pull request template asks for the milestone, the issues and the class."""

from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess

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


STAGES = ["Mockup", "Draft", "Build", "Review", "Merged", "Released"]


def test_the_stage_table_and_the_stage_field_name_the_same_stages():
    text = (AGILE / "SKILL.md").read_text()
    table = re.findall(r"^\| (\w+) \| ", text.split("| Stage | Exit rule |", 1)[1].split("\n\n", 1)[0], re.M)
    assert table == STAGES
    assert f'--single-select-options "{",".join(STAGES)}"' in text


@pytest.mark.parametrize("name", ["3-story.yml", "4-task.yml"])
def test_the_definition_of_done_of_a_form_names_each_stage(name):
    form = yaml.safe_load((AGILE / "templates" / "ISSUE_TEMPLATE" / name).read_text())
    done = next(b for b in form["body"] if b.get("attributes", {}).get("label") == "Definition of done")
    value = done["attributes"]["value"]
    assert all(stage.lower() in value.lower() for stage in STAGES)
    bodies = (AGILE / "templates" / "bodies.md").read_text()
    body = bodies.split(f"## {form['name']}\n", 1)[1].split("```markdown\n", 1)[1].split("\n```", 1)[0]
    done = body.split("## Definition of done\n", 1)[1].split("\n## ", 1)[0]
    assert all(stage.lower() in done.lower() for stage in STAGES)


# The class rule is one rule in every file that states it. On 2026-11-07 a narrow reading left 102 issues of one
# client with no INV label, so the wide meaning and the sweep are tested here.
CLASS_FILES = [AGILE / "LEGEND.md", ROOT / "skill" / "delivery-playbook" / "PLAYBOOK.md"]


@pytest.mark.parametrize("path", CLASS_FILES, ids=lambda p: p.name)
def test_inv_covers_controls_methods_and_gates(path):
    text = path.read_text()
    assert "a security control, a test method and a CI/CD gate" in text
    assert "brings existing behavior back to its intended form and adds nothing, the defect has no class" in text
    assert "A defect in new `INV` work that is not merged yet is also `INV`" in text
    assert "A defect in an unmerged fix that has no class keeps no class." in text
    assert "usually has no class" not in text


def test_the_agile_skill_requires_a_sweep_of_all_issues():
    text = (AGILE / "SKILL.md").read_text()
    assert "Sweep the classes of all issues, not only the new ones." in text
    assert "also for each issue that keeps no class" in text
    assert 'select(startswith("class:"))' in text


@pytest.mark.parametrize("form", [f for f in FORMS if "id: class" in f.read_text()], ids=lambda p: p.stem)
def test_each_class_dropdown_states_the_wide_rule(form):
    field = next(b for b in yaml.safe_load(form.read_text())["body"] if b.get("id") == "class")
    description = field["attributes"]["description"]
    assert "security control" in description and "No class only for a fix that restores existing behavior" in description


def test_the_pull_request_template_narrows_no_class():
    text = (ROOT / "skill" / "pull-request" / "templates" / "pull_request_template.md").read_text()
    assert "- [ ] No class: the change only restores existing behavior and adds nothing" in text


def class_table_program() -> str:
    """The jq program of the class table in section 7 of the agile skill."""
    section = (AGILE / "SKILL.md").read_text().split("## 7. Show the class of each issue", 1)[1].split("\n## ", 1)[0]
    return section.split("jq -rs '", 1)[1].split("'\n```", 1)[0]


@pytest.mark.skipif(shutil.which("jq") is None, reason="jq is not installed")
def test_the_class_table_command_counts_each_issue_once():
    repo_1 = [
        {"title": "SEC-01: a new control", "labels": [{"name": "class:INV"}, {"name": "status:open"}]},
        {"title": "SEC-02: a fix", "labels": [{"name": "status:open"}]},
        {"title": "Add a dashboard", "labels": [{"name": "class:INV"}]},
    ]
    repo_2 = [
        {"title": "BP-01: a gate", "labels": [{"name": "class:TDT"}, {"name": "class:INV"}]},
        {"title": "OA-01: a decision", "labels": []},
        {"title": "TDT-01: old code", "labels": [{"name": "class:TDT"}]},
    ]
    stdin = json.dumps(repo_1) + "\n" + json.dumps(repo_2) + "\n"
    out = subprocess.run(["jq", "-rs", class_table_program()], input=stdin, capture_output=True, text=True, check=True)
    assert out.stdout.splitlines() == [
        "| Category | INV only | TDT only | Both | No class | Total |",
        "| --- | --- | --- | --- | --- | --- |",
        "| SEC | 1 | 0 | 0 | 1 | 2 |",
        "| BP | 0 | 0 | 1 | 0 | 1 |",
        "| OA | 0 | 0 | 0 | 1 | 1 |",
        "| TDT | 0 | 1 | 0 | 0 | 1 |",
        "| Other work | 1 | 0 | 0 | 0 | 1 |",
        "| Total | 2 | 1 | 1 | 2 | 6 |",
    ]


def test_the_agile_skill_asks_reports_to_highlight_innovations():
    section = (AGILE / "SKILL.md").read_text().split("### Highlight the innovations", 1)[1].split("\n## ", 1)[0]
    for state in ("Built (`status:fixed-on-review-branch`)", "Partly built (`status:partly-fixed`)",
                  "Owner decision (`status:owner-action`)"):
        assert state in section
    assert "Innovation, What it gives the business, State and Where" in section
    assert "A proposed innovation is never shown as built." in section


@pytest.mark.parametrize("name", ["1-epic.yml", "2-feature.yml", "3-story.yml"])
def test_epic_feature_and_story_forms_ask_for_the_business_value(name):
    body = yaml.safe_load((AGILE / "templates" / "ISSUE_TEMPLATE" / name).read_text())["body"]
    field = next(b for b in body if b.get("id") == "value")
    assert field["attributes"]["label"] == "Business value"
    assert "table of main innovations" in field["attributes"]["description"]


CLASS_SUMMARIES = [
    ROOT / "skill" / "delivery-playbook" / "DECK.md",
    AGILE / "templates" / "bodies.md",
    *[f for f in FORMS if "id: class" in f.read_text()],
]


@pytest.mark.parametrize("path", CLASS_SUMMARIES, ids=lambda p: p.name)
def test_class_summaries_preserve_the_unmerged_work_exceptions(path):
    text = path.read_text().replace("`", "")
    assert "A defect in unmerged INV work stays INV." in text
    assert "A defect in an unmerged fix with no class keeps no class." in text


@pytest.mark.parametrize("path", [AGILE / "SKILL.md", ROOT / "skill" / "delivery-playbook" / "DECK.md"])
def test_the_defect_class_table_allows_the_class_of_the_work(path):
    row = next(line for line in path.read_text().splitlines() if line.startswith("| Defect |"))
    assert "As the work" in row
