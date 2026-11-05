# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Every skill is one a person can install: a SKILL.md whose name is its directory, a description that says when to
use it, and a README row that says where to link it. The two mockup skills are one standard and name each other."""

from __future__ import annotations

import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = sorted(p.parent for p in ROOT.glob("skill/*/SKILL.md"))


def frontmatter(path: pathlib.Path) -> dict[str, str]:
    match = re.match(r"---\n(.*?)\n---\n", path.read_text(), re.S)
    assert match, f"{path.relative_to(ROOT)} starts without a --- frontmatter block"
    return dict(line.split(": ", 1) for line in match.group(1).splitlines())


def test_the_kit_ships_every_skill():
    assert [p.name for p in SKILLS] == ["adversarial-review", "app-architect", "build-mockup", "dashboard", "document", "mockup-to-page",
                                      "visual"]


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_a_skill_is_named_for_its_directory_and_says_when_to_use_it(skill):
    meta = frontmatter(skill / "SKILL.md")
    assert meta["name"] == skill.name
    assert "Use when" in meta["description"]


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_the_readme_says_where_to_link_each_skill(skill):
    assert f"link `~/.claude/skills/{skill.name}` to this directory" in (ROOT / "README.md").read_text()


def test_the_mockup_skills_are_one_standard():
    build = (ROOT / "skill" / "build-mockup" / "SKILL.md").read_text()
    page = (ROOT / "skill" / "mockup-to-page" / "SKILL.md").read_text()
    assert "`/mockup-to-page` are one standard: change them together" in build
    assert "`/build-mockup` are one standard: change them together" in page


def test_the_architect_skill_runs_in_its_own_agent_and_receives_its_subject():
    skill = ROOT / "skill" / "app-architect" / "SKILL.md"
    meta = frontmatter(skill)
    assert (meta["context"], meta["agent"]) == ("fork", "general-purpose")
    assert "$ARGUMENTS" in skill.read_text()


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_a_frontmatter_value_that_yaml_reads_as_a_list_or_a_map_is_quoted(skill):
    # `argument-hint: [path] [scope]` is a YAML list followed by stray text, and a strict parser refuses the block
    for key, value in frontmatter(skill / "SKILL.md").items():
        assert not value.startswith(("[", "{")), f"{skill.name}: quote the value of {key}"


def test_the_review_skill_names_the_templates_it_ships():
    skill = ROOT / "skill" / "adversarial-review"
    text = (skill / "SKILL.md").read_text()
    for template in ("brief-template.md", "record-template.md"):
        assert (skill / template).is_file()
        assert f"${{CLAUDE_SKILL_DIR}}/{template}" in text
