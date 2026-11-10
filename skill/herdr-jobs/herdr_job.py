#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Run one background job in its own tab of a Herdr session, so a person can watch it live.

The job gets a tab named after it in the workspace `--workspace` of the session `--session`. A small runner script
does the work in that tab and appends one line to the status file when the command ends:

    <name> <run id> exit=<code> <UTC time>

With `--wait`, this command returns only after that line exists, with the exit code of the job. A caller that runs
it in the background (a Claude Code background shell, for example) is woken when the job ends, as before.

If no Herdr server runs for the session, the job runs here, in the foreground, and writes the same status line.
`--no-fallback` turns that into exit code 3 instead.

Herdr: https://github.com/herdrdev/herdr (Apache-2.0). Tested with herdr 0.9.5.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys
import time
import uuid

NO_SERVER = 3
NAME = re.compile(r"[a-z][a-z0-9_.-]{0,63}")


class HerdrError(RuntimeError):
    """A herdr call failed. The message holds the code and text that herdr returned."""


def herdr(session: str, *args: str) -> dict:
    """Call the herdr CLI for one session and return the `result` object of its JSON answer."""
    proc = subprocess.run(["herdr", "--session", session, *args], capture_output=True, text=True, check=False)
    for stream in (proc.stdout, proc.stderr):
        try:
            answer = json.loads(stream)
        except json.JSONDecodeError:
            continue
        if "error" in answer:
            error = answer["error"]
            raise HerdrError(f"{error.get('code', 'error')}: {error.get('message', '')}")
        if "result" in answer:
            return answer["result"]
    if proc.returncode == 0 and not proc.stdout.strip():
        return {}  # some commands, such as `pane run`, answer a success with no output
    raise HerdrError(f"herdr {' '.join(args)} exited {proc.returncode} with no JSON answer: {proc.stderr.strip()}")


def server_runs(session: str) -> bool:
    try:
        herdr(session, "workspace", "list")
    except HerdrError as error:
        if str(error).startswith("server_not_running"):
            return False
        raise
    return True


def workspace_id(session: str, label: str, cwd: str) -> str:
    """Return the id of the workspace with this label, and create it when it does not exist."""
    for workspace in herdr(session, "workspace", "list")["workspaces"]:
        if workspace.get("label") == label:
            return workspace["workspace_id"]
    created = herdr(session, "workspace", "create", "--label", label, "--cwd", cwd, "--no-focus")
    return created["workspace"]["workspace_id"]


def write_runner(path: pathlib.Path, name: str, run_id: str, cwd: str, env: dict[str, str], command: list[str],
                 status: pathlib.Path) -> None:
    """Write the script that the tab runs. It deletes itself first, so an environment value does not stay on disk."""
    lines = ["#!/bin/bash", 'rm -f -- "$0"']
    lines += [f"export {key}={shlex.quote(value)}" for key, value in env.items()]
    lines += [
        f"cd -- {shlex.quote(cwd)} || exit 1",
        shlex.join(command),
        "rc=$?",
        f"printf '%s %s exit=%s %s\\n' {shlex.quote(name)} {shlex.quote(run_id)} \"$rc\" "
        f"\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\" >> {shlex.quote(str(status))}",
        'exit "$rc"',
    ]
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as handle:
        handle.write("\n".join(lines) + "\n")


def wait_for(status: pathlib.Path, name: str, run_id: str, poll: float) -> int:
    """Block until the status file has the line of this run, then return its exit code."""
    pattern = re.compile(rf"^{re.escape(name)} {re.escape(run_id)} exit=(\d+) ")
    while True:
        if status.exists():
            for line in status.read_text().splitlines():
                match = pattern.match(line)
                if match:
                    return int(match.group(1))
        time.sleep(poll)


def parse(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--name", required=True, help="job name, also the tab label: [a-z][a-z0-9_.-]{0,63}")
    parser.add_argument("--session", default=os.environ.get("HERDR_JOBS_SESSION", "jobs"))
    parser.add_argument("--workspace", default=os.environ.get("HERDR_JOBS_WORKSPACE", "jobs"))
    parser.add_argument("--cwd", default=os.getcwd())
    parser.add_argument("--env", action="append", default=[], metavar="KEY", help="pass this variable of the "
                        "current environment to the job; repeat it for each variable")
    parser.add_argument("--status", type=pathlib.Path,
                        default=pathlib.Path.home() / ".local/state/herdr-jobs/status.txt")
    parser.add_argument("--wait", action="store_true", help="return when the job ends, with its exit code")
    parser.add_argument("--no-fallback", action="store_true", help=f"exit {NO_SERVER} when no Herdr server runs")
    parser.add_argument("--poll", type=float, default=5.0, help=argparse.SUPPRESS)
    parser.add_argument("command", nargs=argparse.REMAINDER, help="-- then the command and its arguments")
    args = parser.parse_args(argv)
    if args.command[:1] == ["--"]:
        args.command = args.command[1:]
    if not args.command:
        parser.error("give the command after --")
    if not NAME.fullmatch(args.name):
        parser.error(f"--name {args.name!r} does not match {NAME.pattern}")
    missing = [key for key in args.env if key not in os.environ]
    if missing:
        parser.error(f"--env names a variable that is not set: {', '.join(missing)}")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse(sys.argv[1:] if argv is None else argv)
    cwd = str(pathlib.Path(args.cwd).resolve())
    env = {key: os.environ[key] for key in args.env}
    run_id = uuid.uuid4().hex[:12]
    args.status.parent.mkdir(parents=True, exist_ok=True)

    if not server_runs(args.session):
        if args.no_fallback:
            print(f"herdr-jobs: no Herdr server runs for session {args.session!r}. Start it with "
                  f"`herdr session attach {args.session}`.", file=sys.stderr)
            return NO_SERVER
        print(f"herdr-jobs: no Herdr server for session {args.session!r}; {args.name} runs here.", file=sys.stderr)
        rc = subprocess.run(args.command, cwd=cwd, env={**os.environ, **env}, check=False).returncode
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with args.status.open("a") as handle:
            handle.write(f"{args.name} {run_id} exit={rc} {stamp}\n")
        return rc

    runner = args.status.parent / f"run-{args.name}-{run_id}.sh"
    write_runner(runner, args.name, run_id, cwd, env, args.command, args.status)
    workspace = workspace_id(args.session, args.workspace, cwd)
    tab = herdr(args.session, "tab", "create", "--workspace", workspace, "--cwd", cwd, "--label", args.name,
                "--no-focus")
    pane = tab["root_pane"]["pane_id"]
    herdr(args.session, "pane", "rename", pane, args.name)
    herdr(args.session, "pane", "run", pane, f"bash {shlex.quote(str(runner))}")
    print(json.dumps({"name": args.name, "run_id": run_id, "session": args.session, "workspace": workspace,
                      "tab": tab["tab"]["tab_id"], "pane": pane, "status": str(args.status)}))
    sys.stdout.flush()
    return wait_for(args.status, args.name, run_id, args.poll) if args.wait else 0


if __name__ == "__main__":
    sys.exit(main())
