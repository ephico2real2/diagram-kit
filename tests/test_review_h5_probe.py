# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Broken PID probes must not break context recovery."""
import importlib.util
import json
import os
import pathlib
import pytest
from test_handover import project, run, SCRIPT, write_note


@pytest.mark.parametrize("pid", ["0", "999999999999999999999999999999"])
def test_invalid_pid_does_not_crash_or_claim_a_live_job(project, pid):
    write_note(project, running=f"- job | pid {pid} | build | restart: make")
    result = run(project, "session-start")
    assert result.returncode == 0
    assert result.stderr == ""
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "job:" in context
    assert "alive (pid" not in context


@pytest.mark.parametrize("unreadable", [False, True])
def test_pidfile_is_read_once_and_read_errors_are_reported(project, monkeypatch, unreadable):
    spec = importlib.util.spec_from_file_location("handover", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    path = project / "job.pid"
    path.write_text("123")
    original = pathlib.Path.read_text
    reads = []

    def read(candidate, *args, **kwargs):
        if candidate != path:
            return original(candidate, *args, **kwargs)
        reads.append(candidate)
        if unreadable:
            raise PermissionError("unreadable test pidfile")
        return "123" if len(reads) == 1 else ""

    monkeypatch.setattr(pathlib.Path, "read_text", read)
    monkeypatch.setattr(module.os, "kill", lambda pid, signal: None)
    report = module.running_jobs("## Running\n- job | pidfile job.pid | build | restart: make\n", project)
    assert len(reads) == 1
    assert len(report) == 1
    assert ("unknown" if unreadable else "alive (pid 123)") in report[0]


def test_nonregular_pidfile_stays_unknown_without_opening_it(project):
    os.mkfifo(project / "job.pid")
    write_note(project, running="- job | pidfile job.pid | build | restart: make")
    result = run(project, "session-start")
    assert result.returncode == 0
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "job: unknown" in context
