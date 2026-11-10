# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The automatic handover: each hook is driven as Claude Code drives it, with the hook input as JSON on stdin, in a
temporary project that has a real git repository."""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "handover" / "scripts" / "handover.py"


def stamp(minutes_ago: int = 0) -> str:
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=minutes_ago)).strftime("%Y-%m-%d %H:%M")


def note_text(repo: pathlib.Path, *, n: int = 2, total: int = 3, minutes_ago: int = 0, extra: str = "",
              running: str = "- none") -> str:
    return f"""# Handover: demo
Last update: item {n} of {total} (build the parser), {stamp(minutes_ago)} UTC (16:12 CST). Next: run `pytest tests/test_parser.py`.

## Context
- Goal: a parser for the demo files. Story: #12.
- Repos: {repo}
- Branch: work/parser
- Tracker: claude-resumes/TRACKER-demo.md

## Done
- Unit 1, see the tracker.

## Now
- The parser reads the header. Checked with `pytest -k header` (2 passed).{extra}

## Next steps
1. Run `pytest tests/test_parser.py`.

## Running
{running}

## Temporary changes
- none

## Open
- none
"""


TRACKER = """# Tracker: demo

| # | Unit | Phase | Status | Step or evidence | Updated (UTC) |
|---|---|---|---|---|---|
| 1 | Design the parser | design | done | commit abc1234, PR #11, CI run 77 passed | 2026-11-07 20:00 |
| 2 | Build the parser | build | in progress | step: the body reader | 2026-11-07 21:00 |
| 3 | Review | review | todo | | |
"""


@pytest.fixture
def project(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {**os.environ, "GIT_AUTHOR_DATE": "2020-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2020-01-01T00:00:00Z"}
    for args in (["init", "-q", "-b", "work/parser"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                                                        "--allow-empty", "-m", "start"]):
        subprocess.run(["git", "-C", str(repo), *args], check=True, env=env)
    folder = tmp_path / "claude-resumes"
    folder.mkdir()
    (folder / "CURRENT").write_text("demo\n")
    (folder / "TRACKER-demo.md").write_text(TRACKER)
    time.sleep(0.01)
    (folder / "HANDOVER-demo.md").write_text(note_text(repo))
    return tmp_path


def run(project: pathlib.Path, *args: str, hook: dict | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project)}
    return subprocess.run([sys.executable, str(SCRIPT), *args], input=json.dumps(hook or {}), capture_output=True,
                          text=True, env=env, timeout=10)


def write_note(project: pathlib.Path, **kwargs) -> None:
    (project / "claude-resumes" / "HANDOVER-demo.md").write_text(note_text(project / "repo", **kwargs))


def test_a_current_note_passes_and_every_hook_is_silent(project):
    assert run(project, "check").returncode == 0
    assert run(project, "check").stdout == ""
    assert run(project, "stop", hook={"stop_hook_active": False}).stdout == ""
    assert run(project, "post-tool", hook={"tool_input": {"command": "ls -la"}}).stdout == ""


def test_a_stale_note_blocks_the_stop_once_and_never_loops(project):
    write_note(project, minutes_ago=90)
    first = run(project, "stop", hook={"stop_hook_active": False})
    decision = json.loads(first.stdout)
    assert decision["decision"] == "block"
    assert re.search(r"the note is 9[01] minutes old \(limit 30\)", decision["reason"])
    # The model continued once because of the block: the next stop must pass, whatever the note says.
    assert run(project, "stop", hook={"stop_hook_active": True}).stdout == ""


@pytest.mark.parametrize("change, failure", [
    (lambda t: t.replace("Last update:", "Updated:"), "line 2 is not"),
    (lambda t: t.replace("## Temporary changes\n", ""), "missing sections: Temporary changes"),
    (lambda t: t.replace("## Now", "## Nowx").replace("## Done", "## Now").replace("## Nowx", "## Done"),
     "not in the order"),
    (lambda t: t.replace("item 2 of 3", "item 2 of 4"), "line 2 says 4 units, the tracker has 3"),
    (lambda t: t.replace("item 2 of 3", "item 1 of 3"), "line 2 says item 1, the tracker says item 2"),
    (lambda t: t + "\nexport GH_TOKEN=ghp_" + "a" * 36 + "\n", "looks like a GitHub token"),
    (lambda t: t + "\nDB url postgres://app:hunter22@db:5432/app\n", "a password in a URL"),
])
def test_the_check_names_each_defect_of_the_note(project, change, failure):
    path = project / "claude-resumes" / "HANDOVER-demo.md"
    path.write_text(change(path.read_text()))
    result = run(project, "check")
    assert result.returncode == 1
    assert failure in result.stdout


def test_the_local_time_beside_utc_is_optional_but_utc_is_not(project):
    path = project / "claude-resumes" / "HANDOVER-demo.md"
    path.write_text(path.read_text().replace(" (16:12 CST)", ""))
    assert run(project, "check").returncode == 0
    path.write_text(path.read_text().replace(" UTC.", " (16:12 CST)."))
    assert "line 2 is not" in run(project, "check").stdout


def test_a_secret_name_is_allowed_but_its_value_is_not(project):
    write_note(project, extra="\n- The API key of the payment provider is in the secret store, item `payments/api-key`."
                              "\n- secret: aws/sm/payments-db, token: see the vault entry ci/deploy-token2")
    assert run(project, "check").returncode == 0
    write_note(project, extra="\n- password=hunter2xyz9")
    assert "looks like a credential value" in run(project, "check").stdout


@pytest.mark.parametrize("topic", ["../../etc", "a/b", ".hidden", ""])
def test_a_topic_must_be_a_plain_name(project, topic):
    (project / "claude-resumes" / "CURRENT").write_text(topic + "\n")
    assert "must hold one topic name" in run(project, "check").stdout


def test_precompact_warns_in_the_summary_when_no_topic_is_active(project):
    (project / "claude-resumes" / "CURRENT").unlink()
    result = run(project, "precompact", hook={"trigger": "manual"})
    assert (result.returncode, "no handover note is active" in result.stdout) == (0, True)
    assert not (project / "claude-resumes" / ".snapshots").exists()


def test_the_tracker_allows_one_unit_in_progress_and_needs_evidence(project):
    tracker = project / "claude-resumes" / "TRACKER-demo.md"
    tracker.write_text(TRACKER.replace("| todo | | |", "| in progress | step: read | 2026-11-07 21:00 |")
                       .replace("abc1234, PR #11, CI run 77 passed", ""))
    os.utime(tracker, (time.time() - 3600, time.time() - 3600))
    out = run(project, "check").stdout
    assert "more than one unit in progress: 2, 3" in out
    assert "tracker unit 1: a done unit needs its evidence" in out


def test_a_tracker_newer_than_the_note_and_a_newer_commit_are_stale(project):
    tracker = project / "claude-resumes" / "TRACKER-demo.md"
    os.utime(tracker, (time.time() + 300, time.time() + 300))
    subprocess.run(["git", "-C", str(project / "repo"), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                    "--allow-empty", "-m", "later"], check=True)
    write_note(project, minutes_ago=5)
    os.utime(tracker, (time.time() + 300, time.time() + 300))
    out = run(project, "check").stdout
    assert "the tracker changed after the note" in out
    assert "repo has a commit newer than line 2" in out


def test_the_stop_hook_needs_each_live_background_task_in_running(project):
    hook = {"stop_hook_active": False, "background_tasks": [
        {"id": "b7l2", "type": "shell", "status": "running", "description": "codex job", "command": "bash run.sh"},
        {"id": "old1", "type": "shell", "status": "completed", "description": "done", "command": "true"}]}
    reason = json.loads(run(project, "stop", hook=hook).stdout)["reason"]
    assert "background task b7l2 (codex job) is not in Running" in reason
    assert "old1" not in reason
    write_note(project, running="- b7l2 | task | the codex job | restart: `bash run.sh`")
    assert run(project, "stop", hook=hook).stdout == ""


def test_precompact_copies_both_files_and_steers_the_summary_without_blocking(project):
    write_note(project, minutes_ago=90)
    result = run(project, "precompact", hook={"trigger": "auto", "custom_instructions": None})
    assert result.returncode == 0
    copies = list((project / "claude-resumes" / ".snapshots").glob("*-auto/*"))
    assert sorted(p.name for p in copies) == ["HANDOVER-demo.md", "TRACKER-demo.md"]
    assert "active topic is 'demo'" in result.stdout
    assert "WARNING: the handover check failed" in result.stdout
    assert "decision" not in result.stdout


def test_session_start_puts_the_note_the_tracker_git_and_the_jobs_into_the_context(project):
    alive = subprocess.Popen(["sleep", "30"])
    try:
        (project / "job.pid").write_text(str(alive.pid))
        write_note(project, running="- w1 | pidfile job.pid | the build | restart: `make build`\n"
                                    "- w2 | pid 999999 | the old job | restart: `make old`")
        out = json.loads(run(project, "session-start", hook={"source": "clear"}).stdout)
    finally:
        alive.kill()
    text = out["hookSpecificOutput"]["additionalContext"]
    assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert text.startswith("RESUME after 'clear'. Use the resume-work skill now")
    assert "Last update: item 2 of 3" in text
    assert "1 done, 1 in progress, 0 blocked, 1 todo, 3 in all" in text
    assert "IN PROGRESS: 2. Build the parser (build): step: the body reader" in text
    assert "## work/parser" in text
    assert f"w1: alive (pid {alive.pid})" in text
    assert "w2: NOT RUNNING (pid 999999)" in text
    assert len(text) <= 10_000


def test_post_tool_reminds_only_after_a_commit_a_pull_request_or_a_deploy(project):
    for command in ["git commit -m x", "git -C backend push", "gh pr merge 3", "./deploy/local/up.sh"]:
        context = json.loads(run(project, "post-tool", hook={"tool_input": {"command": command}}).stdout)
        assert "record it in the tracker" in context["hookSpecificOutput"]["additionalContext"]
    for command in ["git status", "gh pr view 3", "git log --oneline"]:
        assert run(project, "post-tool", hook={"tool_input": {"command": command}}).stdout == ""


def test_the_check_finds_the_root_from_a_subfolder_when_no_project_folder_is_given(project):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    for folder in (project / "repo", project / "claude-resumes"):
        result = subprocess.run([sys.executable, str(SCRIPT), "check"], cwd=folder, capture_output=True, text=True,
                                env=env, timeout=10)
        assert (result.returncode, result.stdout) == (0, ""), folder


def test_a_project_with_no_claude_resumes_folder_is_left_alone(tmp_path):
    for command, hook in [("stop", {}), ("precompact", {"trigger": "manual"}), ("session-start", {"source": "startup"}),
                          ("post-tool", {"tool_input": {"command": "git commit"}})]:
        result = run(tmp_path, command, hook=hook)
        assert (result.returncode, result.stdout) == (0, "")


def test_a_missing_note_blocks_the_stop_with_the_path_to_create(project):
    (project / "claude-resumes" / "HANDOVER-demo.md").unlink()
    reason = json.loads(run(project, "stop").stdout)["reason"]
    assert "no handover note: create" in reason and "HANDOVER-demo.md" in reason


def test_each_hook_is_fast(project):
    for command, hook in [("stop", {}), ("precompact", {"trigger": "auto"}), ("session-start", {"source": "compact"})]:
        start = time.monotonic()
        run(project, command, hook=hook)
        assert time.monotonic() - start < 2.0, command
