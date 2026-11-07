#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The automatic handover: one self-check and the four Claude Code hooks that keep the working note current.

The files are the source of truth, so that /compact, auto-compact and /clear lose nothing:

  claude-resumes/CURRENT                 one line: the active topic
  claude-resumes/HANDOVER-<topic>.md     the working state (the handover skill owns it)
  claude-resumes/TRACKER-<topic>.md      the units of work and their evidence (the build-tracker skill owns it)
  claude-resumes/.snapshots/             copies that the PreCompact hook makes

Subcommands:

  check [topic]      read-only self-check of the note and the tracker; exit 1 and one line per failure
  stop               Stop hook: block the stop once when the check fails, never twice in a row
  precompact         PreCompact hook: copy the note and the tracker to .snapshots, steer the summary, never block
  session-start      SessionStart hook: put the note, the tracker summary, git and the live jobs into the new context
  post-tool          PostToolUse hook on Bash: after a commit, a pull request or a deploy, remind the model of the tracker

The root is $CLAUDE_PROJECT_DIR, else the nearest folder up from the `cwd` of the hook input (or the current folder)
that holds claude-resumes/. Every hook is silent when
all is well, reads only, and writes only the snapshot copy. Only the Python standard library is used.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

SECTIONS = ["Context", "Done", "Now", "Next steps", "Running", "Temporary changes", "Open"]
STATUSES = {"todo", "in progress", "blocked", "done"}
PHASES = {"plan", "design", "build", "test", "review", "release", "deploy"}
MAX_AGE_MIN = int(os.environ.get("HANDOVER_MAX_AGE_MIN", "30"))
CONTEXT_LIMIT = 9000  # SessionStart text that goes into the new context, in characters

LINE2 = re.compile(
    r"^Last update: (?:item )?(?P<n>\d+) of (?P<total>\d+) \((?P<what>.+?)\), "
    r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC(?: \((?P<local>\d{2}:\d{2} [A-Z][A-Za-z+0-9:-]{1,9})\))?\. "
    r"Next: (?P<next>\S.*)$"
)
TOPIC = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}")
EVIDENCE = re.compile(r"\b[0-9a-f]{7,40}\b|#\d+|https?://|\b(?:passed|failed|run \d+|deployed)\b", re.I)
UTC_TIME = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}")
# Shapes of real credentials. A name such as "the API key of the payment provider" is allowed: a value is not.
SECRET_SHAPES = [
    (r"gh[pousr]_[A-Za-z0-9]{36,}", "a GitHub token"),
    (r"github_pat_[A-Za-z0-9_]{40,}", "a GitHub token"),
    (r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}", "an API key"),
    (r"\bA(?:KIA|SIA)[0-9A-Z]{16}\b", "an AWS access key"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "a private key"),
    (r"\bxox[abprs]-[A-Za-z0-9-]{10,}", "a Slack token"),
    (r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "a JSON web token"),
    # A value, not a place: no slash (a path or a store item), at least 8 characters and one digit.
    (r"(?i)\b(?:password|passwd|secret|api[_-]?key|token)\s*[:=]\s*['\"]?(?=[^\s'\"`<>/]*\d)[^\s'\"`<>/]{8,}(?![^\s'\"`<>]*/)",
     "a credential value"),
    (r"://[^/\s:@]+:[^/\s@]+@", "a password in a URL"),
]


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def root_of(hook: dict | None = None) -> pathlib.Path:
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        return pathlib.Path(os.environ["CLAUDE_PROJECT_DIR"])
    # With no project folder from Claude Code, the nearest folder up from cwd that holds claude-resumes/ is the root,
    # so that the check also works from a repository or from inside claude-resumes/ itself.
    start = pathlib.Path((hook or {}).get("cwd") or os.getcwd()).resolve()
    for folder in [start, *start.parents]:
        if (folder / "claude-resumes").is_dir():
            return folder
    return start


def paths(root: pathlib.Path, topic: str | None = None) -> dict[str, pathlib.Path] | None:
    folder = root / "claude-resumes"
    if topic is None:
        current = folder / "CURRENT"
        if not current.is_file():
            return None
        topic = current.read_text().strip().splitlines()[0].strip() if current.read_text().strip() else ""
    return {
        "folder": folder,
        "topic": pathlib.Path(topic),
        "note": folder / f"HANDOVER-{topic}.md",
        "tracker": folder / f"TRACKER-{topic}.md",
        "snapshots": folder / ".snapshots",
    }


def sections(text: str) -> dict[str, str]:
    found, name = {}, None
    for line in text.splitlines():
        heading = re.match(r"^## (.+?)\s*$", line)
        if heading:
            name = heading.group(1)
            found[name] = ""
        elif name is not None:
            found[name] += line + "\n"
    return found


def context_value(note: str, key: str) -> str:
    match = re.search(rf"^- {re.escape(key)}:\s*(.+)$", sections(note).get("Context", ""), re.M)
    return match.group(1).strip() if match else ""


def tracker_rows(text: str) -> list[dict[str, str]]:
    """The rows of the units table: | # | Unit | Phase | Status | Step or evidence | Updated (UTC) |"""
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 6 and cells[0].isdigit():
            rows.append(dict(zip(["n", "unit", "phase", "status", "evidence", "updated"], cells)))
    return rows


def repos(note: str, root: pathlib.Path) -> list[pathlib.Path]:
    found = []
    for item in re.split(r"[,;]\s*", context_value(note, "Repos")):
        item = item.strip().strip("`")
        if item:
            path = pathlib.Path(item)
            found.append(path if path.is_absolute() else root / path)
    return found


def git(repo: pathlib.Path, *args: str) -> str:
    try:
        out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=4)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def check(root: pathlib.Path, topic: str | None = None) -> tuple[list[str], dict]:
    """Return the failures, and the facts that the hooks reuse. An empty list means that the note is current."""
    files = paths(root, topic)
    if files is None:
        return [f"no active topic: write the topic name into {root / 'claude-resumes' / 'CURRENT'}"], {}
    if not TOPIC.fullmatch(str(files["topic"])):
        return [f"{files['folder'] / 'CURRENT'} must hold one topic name of letters, digits, '.', '-' or '_'"], {}
    note_path, tracker_path = files["note"], files["tracker"]
    if not note_path.is_file():
        return [f"no handover note: create {note_path} (handover skill)"], {"files": files}
    note = note_path.read_text()
    failures: list[str] = []
    facts: dict = {"files": files, "note": note}

    lines = note.splitlines()
    line2 = LINE2.match(lines[1]) if len(lines) > 1 else None
    if not line2:
        failures.append("line 2 is not 'Last update: item <n> of <total> (<what>), <YYYY-MM-DD HH:MM> UTC "
                        "(<HH:MM> <local zone>). Next: <step>.'")
    else:
        stamp = dt.datetime.strptime(line2["time"], "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)
        facts["stamp"] = stamp
        age = (utcnow() - stamp).total_seconds() / 60
        if age > MAX_AGE_MIN:
            failures.append(f"the note is {age:.0f} minutes old (limit {MAX_AGE_MIN}): update line 2 and the sections")
        elif age < -5:
            failures.append(f"line 2 is {-age:.0f} minutes in the future: use the UTC time from `date -u`")
        for repo in repos(note, root):
            head = git(repo, "log", "-1", "--format=%ct")
            if head and dt.datetime.fromtimestamp(int(head), dt.timezone.utc) > stamp + dt.timedelta(minutes=1):
                failures.append(f"{repo.name} has a commit newer than line 2: record it in the tracker and the note")

    present = [name for name in SECTIONS if name in sections(note)]
    missing = [name for name in SECTIONS if name not in present]
    if missing:
        failures.append("missing sections: " + ", ".join(missing))
    elif present != [name for name in sections(note) if name in SECTIONS]:
        failures.append("the sections are not in the order " + ", ".join(SECTIONS))

    for pattern, what in SECRET_SHAPES:
        hit = re.search(pattern, note)
        if hit:
            line_no = note[: hit.start()].count("\n") + 1
            failures.append(f"line {line_no} holds what looks like {what}: name the place of the secret, not its value")

    if not tracker_path.is_file():
        failures.append(f"no tracker: create {tracker_path} (build-tracker skill)")
        return failures, facts
    tracker = tracker_path.read_text()
    rows = tracker_rows(tracker)
    facts["rows"] = rows
    if not rows:
        failures.append("the tracker has no unit rows: | # | Unit | Phase | Status | Step or evidence | Updated (UTC) |")
        return failures, facts
    for row in rows:
        if row["status"] not in STATUSES:
            failures.append(f"tracker unit {row['n']}: status '{row['status']}' is not one of {sorted(STATUSES)}")
        if row["phase"] not in PHASES:
            failures.append(f"tracker unit {row['n']}: phase '{row['phase']}' is not one of {sorted(PHASES)}")
        if row["status"] == "done" and not (EVIDENCE.search(row["evidence"]) and UTC_TIME.match(row["updated"])):
            failures.append(f"tracker unit {row['n']}: a done unit needs its evidence (a SHA, a PR or issue number, "
                            "a CI run, a test result or a URL) and its UTC time from git, CI or a log")
        elif row["status"] in {"in progress", "blocked"} and not row["evidence"]:
            failures.append(f"tracker unit {row['n']}: a {row['status']} unit needs its current step or its blocker")
    active = [row for row in rows if row["status"] == "in progress"]
    if len(active) > 1:
        failures.append("the tracker has more than one unit in progress: " + ", ".join(r["n"] for r in active))
    if tracker_path.stat().st_mtime > note_path.stat().st_mtime + 60:
        failures.append("the tracker changed after the note: update the note")
    if line2:
        if int(line2["total"]) != len(rows):
            failures.append(f"line 2 says {line2['total']} units, the tracker has {len(rows)}")
        expected = int(active[0]["n"]) if active else sum(r["status"] == "done" for r in rows)
        if int(line2["n"]) != expected:
            failures.append(f"line 2 says item {line2['n']}, the tracker says item {expected}")
    return failures, facts


def running_jobs(note: str, root: pathlib.Path) -> list[str]:
    """Each Running entry: `- <id> | pid <n>, pidfile <path> or task | <purpose> | restart: <command>`.

    No hook can list the background tasks of Claude Code except Stop, so a long job also writes a pidfile."""
    report = []
    for line in sections(note).get("Running", "").splitlines():
        if not line.startswith("- ") or "|" not in line:
            continue
        cells = [c.strip() for c in line[2:].split("|")]
        pid = None
        probe = cells[1] if len(cells) > 1 else ""
        if probe.startswith("pidfile "):
            pidfile = pathlib.Path(probe[8:].strip().strip("`"))
            pidfile = pidfile if pidfile.is_absolute() else root / pidfile
            if pidfile.is_file() and pidfile.read_text().strip().isdigit():
                pid = int(pidfile.read_text().strip())
        elif re.fullmatch(r"pid \d+", probe):
            pid = int(probe[4:])
        if probe == "task":
            state = "a Claude Code background task: alive only if /tasks lists it, else start it again"
        elif pid is None:
            state = "unknown (no pid): check it by hand"
        else:
            try:
                os.kill(pid, 0)
                state = f"alive (pid {pid})"
            except ProcessLookupError:
                state = f"NOT RUNNING (pid {pid}): start it again if its work is not done"
            except PermissionError:
                state = f"alive (pid {pid}, other user)"
        report.append(f"{cells[0]}: {state}. {' | '.join(cells[2:])}")
    return report


def summary(rows: list[dict[str, str]]) -> str:
    counts = {status: sum(r["status"] == status for r in rows) for status in ["done", "in progress", "blocked", "todo"]}
    out = [", ".join(f"{v} {k}" for k, v in counts.items()) + f", {len(rows)} in all"]
    for row in rows:
        if row["status"] in {"in progress", "blocked"}:
            out.append(f"{row['status'].upper()}: {row['n']}. {row['unit']} ({row['phase']}): {row['evidence']}")
    done = [r for r in rows if r["status"] == "done"][-3:]
    out += [f"done: {r['n']}. {r['unit']}: {r['evidence']} ({r['updated']})" for r in done]
    return "\n".join(out)


def read_hook() -> dict:
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def cmd_check(args: list[str]) -> int:
    root = root_of()
    failures, _ = check(root, args[0] if args else None)
    for failure in failures:
        print(failure)
    return 1 if failures else 0


def unlisted_tasks(hook: dict, note: str) -> list[str]:
    """Each live background task of the Stop input that the Running section does not name by its id."""
    running = sections(note).get("Running", "")
    return [f"background task {task.get('id')} ({task.get('description') or task.get('command', '')[:60]}) is "
            "not in Running: add its id, purpose and restart command"
            for task in hook.get("background_tasks") or []
            if task.get("status") in {"running", "pending"} and str(task.get("id")) not in running]


def cmd_stop() -> int:
    hook = read_hook()
    root = root_of(hook)
    # The loop guard: the model already continued once because of this hook, so let it stop now.
    if hook.get("stop_hook_active") or not (root / "claude-resumes").is_dir():
        return 0
    failures, facts = check(root)
    failures += unlisted_tasks(hook, facts.get("note", ""))
    if failures:
        reason = ("The handover check failed. Update the note and the tracker now (handover and build-tracker skills), "
                  "then stop.\n- " + "\n- ".join(failures))
        print(json.dumps({"decision": "block", "reason": reason}))
    return 0


def cmd_precompact() -> int:
    hook = read_hook()
    root = root_of(hook)
    if not (root / "claude-resumes").is_dir():
        return 0
    failures, facts = check(root)
    files = facts.get("files")
    if files:
        stamp = utcnow().strftime("%Y%m%dT%H%M%SZ")
        target = files["snapshots"] / f"{stamp}-{hook.get('trigger', 'unknown')}"
        target.mkdir(parents=True, exist_ok=True)
        for name in ("note", "tracker"):
            if files[name].is_file():
                shutil.copy2(files[name], target / files[name].name)
    # Claude Code uses the stdout of a PreCompact hook as instructions for the summary, and drops a systemMessage.
    # So the warning goes into the summary, and the SessionStart hook after the compaction repeats the check.
    if files:
        lines = [f"Keep in the summary: the active topic is '{files['topic']}'. The handover note {files['note']} and "
                 f"the tracker {files['tracker']} are the source of truth. After the compaction, use the resume-work "
                 f"skill and continue the step on line 2 of the note. A copy of both is in {target}."]
        if failures:
            lines.append("WARNING: the handover check failed before this compaction. The first action after it is to "
                         "update the note and the tracker:\n- " + "\n- ".join(failures))
        print("\n".join(lines))
    elif failures:
        print("WARNING: no handover note is active, so nothing was copied before this compaction:\n- " + "\n- ".join(failures))
    return 0


def cmd_session_start() -> int:
    hook = read_hook()
    root = root_of(hook)
    if not (root / "claude-resumes").is_dir():
        return 0
    failures, facts = check(root)
    note = facts.get("note", "")
    parts = [f"RESUME after '{hook.get('source', 'startup')}'. Use the resume-work skill now: the note and the tracker "
             "below are the source of truth. Confirm them against git, CI, the jobs and the environment, start each job "
             "that is not running again, and continue from Next steps without asking, unless an Open item needs the user."]
    files = facts.get("files")
    if files and note:
        body = note if len(note) <= CONTEXT_LIMIT - 3000 else note[: CONTEXT_LIMIT - 3000] + "\n[truncated: read the file]"
        parts.append(f"== {files['note']} ==\n{body.strip()}")
    if facts.get("rows"):
        parts.append(f"== {files['tracker']} ==\n{summary(facts['rows'])}")
    lines = []
    for repo in repos(note, root):
        branch = git(repo, "status", "-sb").splitlines()
        changed = git(repo, "status", "--porcelain").splitlines()
        lines.append(f"{repo}: {branch[0] if branch else 'not a git repository'}, {len(changed)} changed, "
                     f"head {git(repo, 'log', '-1', '--format=%h %s (%cI)')}")
    if lines:
        parts.append("== git ==\n" + "\n".join(lines))
    jobs = running_jobs(note, root)
    if jobs:
        parts.append("== Running ==\n" + "\n".join(jobs))
    if failures:
        parts.append("== handover check ==\n- " + "\n- ".join(failures))
    text = "\n\n".join(parts)[:CONTEXT_LIMIT]
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))
    return 0


MILESTONE = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?(?:commit|push|merge)\b|\bgh\s+pr\s+(?:create|merge)\b|"
                       r"\bgh\s+workflow\s+run\b|\bdeploy\S*\.sh\b|\b(?:helm|argocd)\s+(?:upgrade|install|sync)\b")


def cmd_post_tool() -> int:
    hook = read_hook()
    root = root_of(hook)
    command = (hook.get("tool_input") or {}).get("command", "")
    if not (root / "claude-resumes").is_dir() or not MILESTONE.search(command):
        return 0
    text = ("A commit, a pull request or a deploy ran. If it changes the status of a unit, record it in the tracker now, "
            "with its evidence (SHA, PR, CI run, deploy) and the UTC time from git or CI, then update line 2 of the note.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}))
    return 0


def main(argv: list[str]) -> int:
    commands = {"stop": cmd_stop, "precompact": cmd_precompact, "session-start": cmd_session_start,
                "post-tool": cmd_post_tool}
    if argv and argv[0] == "check":
        return cmd_check(argv[1:])
    if argv and argv[0] in commands:
        return commands[argv[0]]()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
