# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Independent guards for hook roots, tracker validation, and context size."""
import importlib.util
import json
from test_handover import project, run, SCRIPT, TRACKER, write_note


def load_module():
    spec = importlib.util.spec_from_file_location("handover", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hook_cwd_selects_its_project_without_the_environment(project, monkeypatch):
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    monkeypatch.chdir(project.parent)
    assert load_module().root_of({"cwd": str(project / "repo")}) == project


def test_explicit_project_takes_precedence_over_hook_cwd(project, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    assert load_module().root_of({"cwd": str(project.parent)}) == project


def test_tracker_rejects_unknown_status(project):
    path = project / "claude-resumes" / "TRACKER-demo.md"
    path.write_text(TRACKER.replace("| design | done |", "| design | finished |"))
    result = run(project, "check")
    assert result.returncode == 1
    assert "status 'finished'" in result.stdout


def test_tracker_rejects_unknown_phase(project):
    path = project / "claude-resumes" / "TRACKER-demo.md"
    path.write_text(TRACKER.replace("| design | done |", "| guess | done |"))
    result = run(project, "check")
    assert result.returncode == 1
    assert "phase 'guess'" in result.stdout


def test_active_unit_requires_a_step(project):
    path = project / "claude-resumes" / "TRACKER-demo.md"
    path.write_text(TRACKER.replace("step: the body reader", ""))
    result = run(project, "check")
    assert result.returncode == 1
    assert "in progress unit needs its current step" in result.stdout


def test_blocked_unit_requires_a_blocker(project):
    path = project / "claude-resumes" / "TRACKER-demo.md"
    path.write_text(TRACKER.replace("| in progress | step: the body reader |", "| blocked | |"))
    write_note(project, n=1)
    result = run(project, "check")
    assert result.returncode == 1
    assert "blocked unit needs its current step or its blocker" in result.stdout


def test_large_inputs_keep_session_context_within_the_reference_limit(project):
    write_note(project, extra="\n" + "x" * 20000)
    path = project / "claude-resumes" / "TRACKER-demo.md"
    path.write_text(TRACKER.replace("step: the body reader", "step: " + "x" * 20000))
    result = run(project, "session-start", hook={"source": "compact"})
    assert result.returncode == 0
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert len(context) <= 10000
