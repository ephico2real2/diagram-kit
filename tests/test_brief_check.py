# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""brief_check.py refuses a brief that breaks the brief standard of /agent-report, and passes one that keeps it."""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill/agent-report/scripts/brief_check.py"
STANDARD = (ROOT / "skill/agent-report/brief-standard.md").read_text()
spec = importlib.util.spec_from_file_location("brief_check", SCRIPT)
brief_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brief_check)

HEAD = """IMPLEMENTER

You are the author of job demo. Your job folder: `/work/jobs/demo/`.

Rules: no browser and no computer-use tool. Read no `.env` file. Limit: stop after D3.

"""


def filled(standard: str = STANDARD) -> str:
    lines = []
    for line in standard.splitlines():
        if not line.startswith(brief_check.INSTRUCTION_PREFIX):
            line = line.replace("<folder>", "/work/jobs").replace("<job>", "demo").replace("<graph_root>", "/work/repo")
        lines.append(line)
    return "\n".join(lines) + "\n"


def good() -> str:
    return HEAD + filled()


def plants(tmp_path: pathlib.Path, text: str = "- C1 CONFIRMED\n- C2 REFUTED\n- C3 NOT REACHED\n") -> pathlib.Path:
    path = tmp_path / "plants" / "demo.md"
    path.parent.mkdir()
    path.write_text(text)
    return path


def test_a_brief_that_keeps_the_standard_passes(tmp_path):
    assert brief_check.check(good(), STANDARD, plants(tmp_path), tmp_path / "jobs" / "demo") == []


def test_the_role_can_follow_a_role_label():
    assert brief_check.check("Role: TESTER under the test loop.\n" + good().split("\n", 1)[1], STANDARD) == []


@pytest.mark.parametrize("first", ["Do this job", "WRITER", ""])
def test_a_brief_with_no_role_line_fails(first):
    problems = brief_check.check(first + "\n" + good().split("\n", 1)[1], STANDARD)
    assert any("names no role" in p for p in problems)


def test_a_brief_with_no_standard_fails():
    problems = brief_check.check(HEAD, STANDARD)
    assert any("the brief standard is missing" in p for p in problems)


def test_an_older_copy_of_the_standard_fails():
    old = filled().replace("9. Your final message states how many graph calls and how many shell calls you made.",
                           "9. Your final message states three counts: graph calls, shell calls and file changes.")
    assert old != filled()
    problems = brief_check.check(HEAD + old, STANDARD)
    assert any("not the current version" in p for p in problems)


def test_a_rule_in_the_wrong_order_fails():
    body = filled().splitlines()
    rule1 = next(i for i, line in enumerate(body) if line.startswith("1. After each ID"))
    rule2 = next(i for i, line in enumerate(body) if line.startswith("2. Use one heading"))
    body[rule1], body[rule2] = body[rule2], body[rule1]
    problems = brief_check.check(HEAD + "\n".join(body), STANDARD)
    assert any("not the current version" in p for p in problems)


@pytest.mark.parametrize("placeholder", ["<folder>", "<job>", "<graph_root>"])
def test_an_unfilled_placeholder_fails(placeholder):
    text = HEAD + STANDARD.replace("<folder>/<job>/", "/work/jobs/demo/").replace("`<graph_root>`", "`/work/repo`")
    text = text.replace("Write to `/work/jobs/demo/`", f"Write to `{placeholder}/`")
    problems = brief_check.check(text, STANDARD)
    assert any(f"the placeholder {placeholder} is not filled in" in p for p in problems)


def test_the_instruction_line_may_keep_its_placeholder_names():
    assert "<job>" in [line for line in good().splitlines() if line.startswith(brief_check.INSTRUCTION_PREFIX)][0]
    assert brief_check.check(good(), STANDARD) == []


@pytest.mark.parametrize("cut, message", [
    ("Limit: stop after D3.", "no stop point"),
    ("no browser and no computer-use tool. ", "browser rule"),
    ("Read no `.env` file. ", "env files"),
])
def test_a_head_without_a_rule_fails(cut, message):
    problems = brief_check.check(good().replace(cut, ""), STANDARD)
    assert any(message in p for p in problems)


@pytest.mark.parametrize("missing", ["CONFIRMED", "REFUTED", "NOT REACHED"])
def test_planted_answers_need_each_verdict(tmp_path, missing):
    text = "\n".join(f"- C{i} {v}" for i, v in enumerate(brief_check.VERDICTS, 1) if v != missing)
    problems = brief_check.check(good(), STANDARD, plants(tmp_path, text), tmp_path / "jobs" / "demo")
    assert any(f"no {missing} answer" in p for p in problems)


def test_planted_answers_inside_the_job_folder_fail(tmp_path):
    job = tmp_path / "jobs" / "demo"
    job.mkdir(parents=True)
    inside = job / "plants.md"
    inside.write_text("C1 CONFIRMED C2 REFUTED C3 NOT REACHED")
    problems = brief_check.check(good(), STANDARD, inside, job)
    assert any("inside the job folder" in p for p in problems)


def test_a_missing_plants_file_fails(tmp_path):
    problems = brief_check.check(good(), STANDARD, tmp_path / "none.md")
    assert any("does not exist" in p for p in problems)


def test_the_command_exits_0_on_a_good_brief_and_1_on_a_bad_one(tmp_path):
    ok, bad = tmp_path / "ok.md", tmp_path / "bad.md"
    ok.write_text(good())
    bad.write_text(HEAD)
    assert subprocess.run([sys.executable, SCRIPT, ok], capture_output=True).returncode == 0
    result = subprocess.run([sys.executable, SCRIPT, bad], capture_output=True, text=True)
    assert result.returncode == 1 and "the brief standard is missing" in result.stdout
    assert subprocess.run([sys.executable, SCRIPT, tmp_path / "none.md"], capture_output=True).returncode == 2


def test_a_brief_that_cuts_the_last_line_of_the_standard_fails():
    body = filled().rstrip("\n").splitlines()
    last = max(i for i, line in enumerate(body) if line.strip())
    problems = brief_check.check(HEAD + "\n".join(body[:last]), STANDARD)
    assert any("not the current version" in p for p in problems)
