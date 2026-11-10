# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""herdr_job.py runs a job in its own Herdr tab and reports its exit code. A fake `herdr` on PATH stands in for the
server, so the test needs no Herdr install: it keeps its workspaces in a JSON file and runs `pane run` at once."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill/herdr-jobs/herdr_job.py"

FAKE = r'''#!/usr/bin/env python3
import json, os, pathlib, subprocess, sys
state_path = pathlib.Path(os.environ["FAKE_HERDR_STATE"])
state = json.loads(state_path.read_text()) if state_path.exists() else {"workspaces": [], "calls": []}
args = sys.argv[1:]
session = args[1]
args = args[2:]
state["calls"].append(args)
def answer(result):
    state_path.write_text(json.dumps(state))
    print(json.dumps({"id": "cli", "result": result}))
    sys.exit(0)
if os.environ.get("FAKE_HERDR_DOWN") == "1":
    state_path.write_text(json.dumps(state))
    print(json.dumps({"id": "cli", "error": {"code": "server_not_running", "message": "no herdr server"}}))
    sys.exit(0)
if args[:2] == ["workspace", "list"]:
    answer({"workspaces": state["workspaces"]})
if args[:2] == ["workspace", "create"]:
    ws = {"workspace_id": f"w{len(state['workspaces']) + 1}", "label": args[args.index("--label") + 1]}
    state["workspaces"].append(ws)
    answer({"workspace": ws})
if args[:2] == ["tab", "create"]:
    n = len([c for c in state["calls"] if c[:2] == ["tab", "create"]])
    answer({"tab": {"tab_id": f"w1:t{n}"}, "root_pane": {"pane_id": f"w1:p{n}"}})
if args[:2] == ["pane", "rename"]:
    answer({})
if args[:2] == ["pane", "run"]:
    state_path.write_text(json.dumps(state))
    subprocess.run(args[3], shell=True, check=False)
    sys.exit(0)
sys.exit(2)
'''


@pytest.fixture
def fake(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    herdr = bin_dir / "herdr"
    herdr.write_text(FAKE)
    herdr.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_HERDR_STATE", str(tmp_path / "state.json"))
    return tmp_path


def run(fake, *args, env=None):
    return subprocess.run([sys.executable, str(SCRIPT), "--status", str(fake / "status.txt"), "--poll", "0.05", *args],
                          capture_output=True, text=True, env={**os.environ, **(env or {})}, check=False)


def calls(fake):
    return json.loads((fake / "state.json").read_text())["calls"]


def test_a_job_runs_in_its_own_tab_and_wait_returns_its_exit_code(fake):
    done = run(fake, "--name", "build-a", "--cwd", str(fake), "--wait", "--", "bash", "-c", "exit 7")
    assert done.returncode == 7
    line = (fake / "status.txt").read_text().splitlines()[0].split()
    assert line[0] == "build-a" and line[2] == "exit=7"
    made = calls(fake)
    assert ["workspace", "create", "--label", "jobs", "--cwd", str(fake.resolve()), "--no-focus"] in made
    assert any(c[:2] == ["tab", "create"] and c[c.index("--label") + 1] == "build-a" for c in made)
    assert ["pane", "rename", "w1:p1", "build-a"] in made


def test_a_second_job_reuses_the_workspace(fake):
    run(fake, "--name", "one", "--cwd", str(fake), "--wait", "--", "true")
    run(fake, "--name", "two", "--cwd", str(fake), "--wait", "--", "true")
    assert len([c for c in calls(fake) if c[:2] == ["workspace", "create"]]) == 1


def test_the_runner_passes_a_named_variable_and_deletes_itself(fake):
    out = fake / "seen.txt"
    done = run(fake, "--name", "env-job", "--cwd", str(fake), "--env", "JOB_TOKEN", "--wait", "--",
               "bash", "-c", f'printf %s "$JOB_TOKEN" > {out}', env={"JOB_TOKEN": "a b'c"})
    assert done.returncode == 0
    assert out.read_text() == "a b'c"
    assert not list(fake.glob("run-*.sh"))
    assert "a b'c" not in done.stdout


def test_with_no_server_the_job_runs_here(fake):
    done = run(fake, "--name", "local", "--cwd", str(fake), "--", "bash", "-c", "echo here; exit 4",
               env={"FAKE_HERDR_DOWN": "1"})
    assert done.returncode == 4
    assert "here" in done.stdout
    assert " exit=4 " in (fake / "status.txt").read_text()


def test_no_fallback_refuses_when_no_server_runs(fake):
    done = run(fake, "--no-fallback", "--name", "strict", "--", "true", env={"FAKE_HERDR_DOWN": "1"})
    assert done.returncode == 3
    assert "herdr session attach jobs" in done.stderr


@pytest.mark.parametrize("name", ["Build", "1job", "a b", ""])
def test_a_bad_job_name_is_refused(fake, name):
    assert run(fake, "--name", name, "--", "true").returncode == 2


def test_an_unset_variable_is_refused_before_anything_runs(fake):
    done = run(fake, "--name", "x", "--env", "NOT_SET_ANYWHERE_42", "--", "true")
    assert done.returncode == 2
    assert not (fake / "state.json").exists()
