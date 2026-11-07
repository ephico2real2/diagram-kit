# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The sweeper survives a task file that is gone, reports without ending anything, and names only what its test finds.

The dangling link is the shape measured on 2026-11-07: a `*.output` link whose target's temporary directory was deleted
stopped the prompt hook with FileNotFoundError on every prompt. No test here reads the real process table."""

from __future__ import annotations

import builtins
import glob
import importlib.util
import json
import os
import pathlib
import sys
import time

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "skill" / "sweep-stale" / "sweep-stale.py"
SOCKET = "/tmp/cxc-test/broker.sock"


@pytest.fixture
def sweep(monkeypatch):
    spec = importlib.util.spec_from_file_location("sweep_stale", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(glob, "glob", lambda pattern: [])
    monkeypatch.setattr(module, "writers", lambda paths: set())
    return module


def serve_tasks(monkeypatch, files: list[pathlib.Path]) -> None:
    """Answer only the sweeper's first task pattern, so that each file is listed once."""
    monkeypatch.setattr(glob, "glob", lambda pattern: [str(f) for f in files] if pattern.startswith("/private/tmp/") else [])


def task(path: pathlib.Path, age_minutes: int = 0) -> pathlib.Path:
    path.write_text("running")
    stamp = time.time() - age_minutes * 60
    os.utime(path, (stamp, stamp))
    return path


def dangling(path: pathlib.Path) -> pathlib.Path:
    path.symlink_to(path.parent / "deleted" / "agent-x.jsonl")
    return path


def process(pid: int, ppid: int, cmd: str, stat: str = "S", etime: str = "01:00:00") -> dict:
    return {"pid": pid, "ppid": ppid, "stat": stat, "etime": etime, "rss": 2048, "cmd": cmd, "kids": []}


def broker(pid: int = 500) -> dict:
    return process(pid, 1, f"node app-server-broker.mjs --endpoint unix:{SOCKET} --cwd /work/repo")


def forbid_signals(monkeypatch, sweep) -> None:
    def refuse(pid, sig):
        raise AssertionError(f"a report sent signal {sig} to {pid}")
    monkeypatch.setattr(sweep.os, "kill", refuse)


def test_a_dangling_link_is_skipped_and_the_rest_stay_newest_first(sweep, monkeypatch, tmp_path):
    old, new = task(tmp_path / "old.output", 10), task(tmp_path / "new.output")
    serve_tasks(monkeypatch, [old, dangling(tmp_path / "gone.output"), new])
    assert [path for path, _ in sweep.task_files()] == [str(new.resolve()), str(old.resolve())]


def test_the_hook_exits_clean_and_silent_past_a_dangling_link(sweep, monkeypatch, tmp_path, capsys):
    serve_tasks(monkeypatch, [dangling(tmp_path / "gone.output")])
    monkeypatch.setattr(sweep, "snapshot", dict)
    monkeypatch.setattr(sys, "argv", ["sweep-stale.py", "--json"])
    assert sweep.main() == 0
    assert capsys.readouterr().out == ""


def test_a_file_removed_after_it_was_read_is_still_reported_by_its_recorded_age(sweep, monkeypatch, tmp_path):
    ghost = task(tmp_path / "ghost.output", 10)
    serve_tasks(monkeypatch, [ghost])
    real_open = builtins.open

    class ReadThenRemove:
        def read(self):
            data = ghost.read_bytes()
            ghost.unlink()
            return data

    monkeypatch.setattr(builtins, "open", lambda path, mode="r", *a, **k: ReadThenRemove() if mode == "rb" else real_open(path, mode, *a, **k))
    findings = sweep.find_ghost_tasks({}, hook=False)
    assert len(findings) == 1 and "ghost.output" in findings[0] and "last written 10 min ago" in findings[0]


def test_a_file_with_an_exit_marker_is_not_a_ghost(sweep, monkeypatch, tmp_path):
    done = task(tmp_path / "done.output", 10)
    done.write_text("done\n[exited with code 0]\n")
    os.utime(done, (time.time() - 600, time.time() - 600))
    serve_tasks(monkeypatch, [done])
    assert sweep.find_ghost_tasks({}, hook=False) == []


def test_the_hook_names_a_broker_with_no_client_and_ends_nothing(sweep, monkeypatch, capsys):
    forbid_signals(monkeypatch, sweep)
    monkeypatch.setattr(sweep, "snapshot", lambda: {500: broker()})
    monkeypatch.setattr(sweep, "socket_holders", lambda: {SOCKET: {500}})
    monkeypatch.setattr(sys, "argv", ["sweep-stale.py", "--json"])
    assert sweep.main() == 0
    context = json.loads(capsys.readouterr().out)["hookSpecificOutput"]["additionalContext"]
    assert "stale codex broker 500" in context and "/work/repo" in context


def test_a_broker_with_a_client_outside_its_tree_is_live(sweep, monkeypatch):
    monkeypatch.setattr(sweep, "socket_holders", lambda: {SOCKET: {500, 900}})
    findings, to_end, _ = sweep.find({500: broker()})
    assert findings == [] and to_end == []


def test_a_zombie_is_reported_with_its_parent_and_never_ended(sweep):
    procs = {700: process(700, 600, "defunct", stat="Z"), 600: process(600, 1, "/usr/bin/parent")}
    findings, to_end, _ = sweep.find(procs)
    assert "zombie pid 700" in findings[0] and "/usr/bin/parent" in findings[0]
    assert to_end == []


@pytest.mark.parametrize("cmd", ["/Applications/Foo.app/headless_shell", "/usr/bin/qemu headless_shell", "podman headless_shell"])
def test_the_guard_overrides_the_orphan_finding(sweep, cmd):
    findings, to_end, _ = sweep.find({800: process(800, 1, cmd)})
    assert findings == [] and to_end == []


def test_the_guard_reads_the_named_process_so_a_sweep_ends_its_guarded_child(sweep, monkeypatch):
    """The skill and the docstring promise this behaviour, not protection of every process under /Applications."""
    parent = broker()
    parent["kids"] = [501]
    procs = {500: parent, 501: process(501, 500, "/Applications/Foo.app/helper")}
    assert sweep.protected(procs, 501) and not sweep.protected(procs, 500)
    sent = []

    def record(pid, sig):
        if sig == 0:
            raise ProcessLookupError(pid)
        sent.append(pid)

    monkeypatch.setattr(sweep.os, "kill", record)
    monkeypatch.setattr(sweep.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(sweep, "snapshot", lambda: procs)
    monkeypatch.setattr(sweep, "socket_holders", dict)
    monkeypatch.setattr(sys, "argv", ["sweep-stale.py", "--sweep"])
    assert sweep.main() == 0
    assert sorted(sent) == [500, 501]
    assert "ends the whole tree" in SCRIPT.with_name("SKILL.md").read_text()
    assert "ends the whole tree" in sweep.__doc__


def test_an_orphan_is_ended_only_past_its_grace_period(sweep):
    young, old = process(801, 1, "headless_shell", etime="05:00"), process(802, 1, "headless_shell", etime="25:00")
    _, to_end, _ = sweep.find({801: young, 802: old})
    assert [pid for pid, _ in to_end] == [802]


def test_the_script_never_ends_its_own_ancestors(sweep):
    me, parent = os.getpid(), os.getppid()
    procs = {me: process(me, parent, "python"), parent: process(parent, 1, "shell"), 999: process(999, 1, "other")}
    assert sweep.protected(procs, parent) and sweep.protected(procs, me)
    assert not sweep.protected(procs, 999)


@pytest.mark.parametrize(("etime", "expected"), [("05-15:39:27", 8139), ("10:34:59", 634), ("04:12", 4)])
def test_ps_elapsed_time_becomes_whole_minutes(sweep, etime, expected):
    assert sweep.minutes(etime) == expected
