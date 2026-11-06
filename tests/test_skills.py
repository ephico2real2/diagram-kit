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
    assert [p.name for p in SKILLS] == ["adversarial-review", "agent-report", "app-architect", "build-mockup", "codex-arbiter", "dashboard",
                                      "document", "fix-defect", "mockup-to-page", "mockup-to-page-react", "test-ui",
                                      "tokensave-fork", "visual"]


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


def test_the_patternfly_page_skill_is_part_of_the_mockup_standard():
    build = (ROOT / "skill" / "build-mockup" / "SKILL.md").read_text()
    page = (ROOT / "skill" / "mockup-to-page-react" / "SKILL.md").read_text()
    assert "`/mockup-to-page-react` are one standard" in build
    assert "`react-pf-ts`" in build
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


def test_the_agent_report_skill_ships_its_brief_and_an_audit_of_real_work():
    skill = (ROOT / "skill" / "agent-report" / "SKILL.md").read_text()
    brief = (ROOT / "skill" / "agent-report" / "brief-standard.md").read_text()
    assert "${CLAUDE_SKILL_DIR}/brief-standard.md" in skill
    assert "Plant claims with known answers" in skill
    assert "Operate the tests again" in skill
    for report in ("plan.md", "research.md", "tests.md", "verdicts.md", "fixes.md", "recommendations.md", "resume.md"):
        assert report in brief, report
    assert "Do not write a program to test the format" in brief


def test_the_defect_skill_and_the_fork_skill_use_the_brief_standard():
    assert "`/agent-report`" in (ROOT / "skill" / "fix-defect" / "SKILL.md").read_text()
    assert "`/agent-report`" in (ROOT / "skill" / "tokensave-fork" / "SKILL.md").read_text()


def test_the_fork_skill_installs_from_nothing_and_warns_about_upgrade():
    skill = (ROOT / "skill" / "tokensave-fork" / "SKILL.md").read_text()
    assert "## Install from nothing" in skill
    assert "${CLAUDE_SKILL_DIR}/cursor-allow.py" in skill
    assert (ROOT / "skill" / "tokensave-fork" / "cursor-allow.py").is_file()
    assert "Do not run `tokensave upgrade`" in skill
    assert "brew install git rustup ripgrep" in skill


def test_the_fork_skill_audits_the_log_and_the_brief_warns_about_the_default_read():
    skill = (ROOT / "skill" / "tokensave-fork" / "SKILL.md").read_text()
    assert "${CLAUDE_SKILL_DIR}/tool-use-audit.py" in skill
    assert (ROOT / "skill" / "tokensave-fork" / "tool-use-audit.py").is_file()
    assert "${CLAUDE_SKILL_DIR}/cursor-job-config.py" in skill
    assert (ROOT / "skill" / "tokensave-fork" / "cursor-job-config.py").is_file()
    assert "`tool-use-audit.py`" in (ROOT / "skill" / "agent-report" / "SKILL.md").read_text()
    assert "Its default reads the whole file" in (ROOT / "skill" / "agent-report" / "brief-standard.md").read_text()


def test_the_fork_skill_builds_with_the_pinned_toolchain_and_moves_the_shell_before_it_removes_upstream():
    skill = (ROOT / "skill" / "tokensave-fork" / "SKILL.md").read_text()
    # a direct toolchain path skips rustup, and a bare `cargo` is not on PATH with Homebrew's rustup
    builds = [line.strip() for line in skill.splitlines() if "cargo install --locked" in line]
    assert builds and all(line.startswith('PATH="$HOME/.rustup/toolchains/1.98.1-') for line in builds), builds
    assert not re.search(r"gitRepos/tokensave(?!2)", skill)
    assert "## 8. Put the fork on the shell PATH" in skill
    assert skill.index('export PATH="$HOME/.cargo/bin:$PATH"') < skill.index("brew uninstall aovestdipaperino/tap/tokensave")
    assert "`source ~/.zshrc`" in skill
    assert "### How to know that it works" in skill


def test_no_new_skill_names_a_private_path():
    for name in ("agent-report", "codex-arbiter", "fix-defect", "tokensave-fork"):
        for path in (ROOT / "skill" / name).iterdir():
            text = path.read_text()
            assert "/Users/" not in text and "agent-report-standard.md" not in text, path
