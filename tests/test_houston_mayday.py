# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The helpers of /houston-mayday: a built brief passes the kit brief check, and the runner refuses bad input."""
import pathlib
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skill" / "houston-mayday"
CHECK = ROOT / "skill" / "agent-report" / "scripts" / "brief_check.py"

HEAD = """IMPLEMENTER

# Mission demo-r1

## Mission

Add one line to the README of the clone.

## Limits

- Stop after D1, or at 10 minutes.
- Do not open a browser. Do not read any `.env` file.
"""

PLANTS = """- C1 CONFIRMED: the README exists.
- C2 REFUTED: the README is empty.
- C3 NOT REACHED: the remote has the change.
"""


def make(tmp_path, head=HEAD):
    folder = tmp_path / "jobs"
    (folder / "heads").mkdir(parents=True)
    (folder / "heads" / "demo-r1.md").write_text(head)
    return subprocess.run([sys.executable, SKILL / "make_brief.py", folder, "demo-r1", "/srv/repo"],
                          capture_output=True, text=True), folder


def test_a_built_brief_passes_the_kit_brief_check(tmp_path):
    run, folder = make(tmp_path)
    assert run.returncode == 0, run.stderr
    brief = folder / "demo-r1" / "brief.md"
    assert pathlib.Path(run.stdout.strip()) == brief
    text = brief.read_text()
    assert f"{folder}/demo-r1/" in text and "`/srv/repo`" in text
    plants = tmp_path / "plants.md"
    plants.write_text(PLANTS)
    check = subprocess.run([sys.executable, CHECK, brief, "--plants", plants], capture_output=True, text=True)
    assert check.returncode == 0, check.stdout + check.stderr


def test_a_head_with_no_stop_point_fails_the_check(tmp_path):
    run, folder = make(tmp_path, HEAD.replace("Stop after D1, or at 10 minutes.", "Work on D1."))
    assert run.returncode == 0, run.stderr
    check = subprocess.run([sys.executable, CHECK, folder / "demo-r1" / "brief.md"], capture_output=True, text=True)
    assert check.returncode == 1 and "stop point" in check.stdout


def test_make_brief_refuses_missing_arguments():
    run = subprocess.run([sys.executable, SKILL / "make_brief.py", "only-one"], capture_output=True, text=True)
    assert run.returncode != 0 and "usage" in run.stderr


@pytest.mark.skipif(shutil.which("zsh") is None, reason="run-pair.sh is a zsh script")
def test_run_pair_refuses_missing_arguments():
    run = subprocess.run(["zsh", SKILL / "run-pair.sh", "a", "b"], capture_output=True, text=True)
    assert run.returncode == 2 and "usage" in run.stderr
