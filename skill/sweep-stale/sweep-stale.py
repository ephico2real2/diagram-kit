#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Find, and optionally end, the background processes a Claude Code session leaves behind.

Written 2026-09-18 after measuring the real leak on this machine, because the name we had for the problem
was wrong. What the measurement found, and what this therefore looks for:

  * ZERO processes in state Z. A zombie is already dead: it holds a pid slot and nothing else, and it
    cannot be killed — only reaped by its parent. Zombies are reported with their parent named, never
    swept, because ending a live parent to clear a dead child is a human's decision.
  * FOUR orphaned Codex plugin broker trees, four processes deep, ~110 MB apiece, two of them days old —
    one still pointing at a scratchpad from a session that ended five days earlier. That is the leak:
    roughly 450 MB and four idle node runtimes held by reviews that had finished.

The staleness test is a fact, not an age heuristic. A broker's unix socket is read out of lsof, and the
broker is stale when nothing outside its own process tree holds that socket: a broker serving a live task
has a client attached, one whose task ended has none, however recently it started. Age is reported for the
reader; it never decides.

Everything else is matched conservatively — orphaned (parent gone) leftovers of the harnesses this tooling
actually starts, past a grace period.

Never touched, whatever else matches: anything under /Applications or /System, an editor's extension host,
the CRC or container virtual machines, launchd, and this process's own ancestry. The guard is applied last
and beats every detector.

  sweep-stale.py          report, human-readable
  sweep-stale.py --json   report as a Claude Code hook payload; prints nothing when clean
  sweep-stale.py --sweep  end what the report names: TERM, then KILL after a grace
"""
from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import time

ORPHAN_GRACE_MIN = 20
GHOST_WINDOW_H = 3        # a card older than this is a finished task nobody is waiting on
GHOST_MAX = 3             # name the newest few; a wall of them is noise, and this runs every prompt
GHOST_GRACE_MIN = 3       # a file just created has not had time to be opened yet
HOOK_MODE = False          # set in main(); --json is the prompt hook and stays terse
LONG_JOB_MIN = 30         # a live job quiet this long is worth naming, not killing

PROTECT = re.compile(r"/Applications/|/System/|vscode/extensions|\.cursor/extensions|vfkit|qemu|hyperkit"
                     r"|colima|podman|docker|/sbin/launchd|Claude\.app|Cursor\.app|Code Helper")
HARNESS = re.compile(r"headless_shell|playwright.*chromium|/uvicorn|python.* -m pytest|cursor-agent")
BROKER = "app-server-broker.mjs"


def snapshot() -> dict[int, dict]:
    """Every process once. A per-pid `ps` costs 30 s on a busy machine; this costs one fork."""
    out = subprocess.run(["ps", "-eo", "pid=,ppid=,stat=,etime=,rss=,command="],
                         capture_output=True, text=True).stdout
    procs: dict[int, dict] = {}
    for line in out.splitlines():
        parts = line.split(None, 5)
        if len(parts) < 6:
            continue
        pid, ppid, stat, etime, rss, cmd = parts
        try:
            procs[int(pid)] = {"pid": int(pid), "ppid": int(ppid), "stat": stat, "etime": etime,
                               "rss": int(rss), "cmd": cmd}
        except ValueError:
            continue
    for p in procs.values():
        p["kids"] = []
    for p in procs.values():
        parent = procs.get(p["ppid"])
        if parent is not None and parent is not p:
            parent["kids"].append(p["pid"])
    return procs


def minutes(etime: str) -> int:
    """`ps` elapsed time — "05-15:39:27", "10:34:59", "04:12" — as whole minutes."""
    days = 0
    if "-" in etime:
        d, etime = etime.split("-", 1)
        days = int(d)
    bits = [int(b) for b in etime.split(":")]
    h, m = (bits[0], bits[1]) if len(bits) == 3 else (0, bits[0])
    return days * 1440 + h * 60 + m


def tree(procs, root: int) -> list[int]:
    out, stack = [], [root]
    while stack:
        pid = stack.pop()
        if pid in out or pid not in procs:
            continue
        out.append(pid)
        stack.extend(procs[pid]["kids"])
    return out


def rss_mb(procs, root: int) -> int:
    return sum(procs[p]["rss"] for p in tree(procs, root) if p in procs) // 1024


def protected(procs, pid: int) -> bool:
    p = procs.get(pid)
    if p is None or PROTECT.search(p["cmd"]):
        return True
    cur = os.getpid()                      # never end our own ancestry
    seen = set()
    while cur and cur not in seen:
        if cur == pid:
            return True
        seen.add(cur)
        cur = procs.get(cur, {}).get("ppid", 0)
    return False


def socket_holders() -> dict[str, set[int]]:
    out = subprocess.run(["lsof", "-U", "-F", "pn"], capture_output=True, text=True).stdout
    holders: dict[str, set[int]] = {}
    pid = 0
    for line in out.splitlines():
        if line.startswith("p"):
            pid = int(line[1:] or 0)
        elif line.startswith("n"):
            holders.setdefault(line[1:], set()).add(pid)
    return holders


def task_files() -> list[tuple[str, float]]:
    """Every background-task output file this harness has written, as (path, mtime), newest first.

    A file that is gone is skipped. A *.output link dangles once its target's temp directory is deleted
    (measured 2026-11-07: 8 links into removed paperclip-ai-* directories crashed the hook on every prompt).
    """
    import glob
    out = []
    for pat in ("/private/tmp/claude-*/*/*/tasks/*.output",
                os.path.expanduser("~/.claude/projects/*/*/tasks/*.output")):
        out += glob.glob(pat)
    # agent-*.jsonl are subagent transcripts, not background-task cards — they have no timer to go wrong.
    out = [f for f in out if not os.path.basename(f).startswith("agent-")]
    stamped: list[tuple[str, float]] = []
    for f in {os.path.realpath(f) for f in out}:
        try:
            stamped.append((f, os.path.getmtime(f)))
        except OSError:
            continue
    return sorted(stamped, key=lambda s: -s[1])


def writers(paths: list[str]) -> set[str]:
    """Which of these files a live process currently holds open. lsof takes them in one call."""
    if not paths:
        return set()
    held: set[str] = set()
    try:
        out = subprocess.run(["lsof", "-F", "n", "--"] + paths,
                             capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return set(paths)                                       # cannot tell -> assume live, never over-report
    for line in out.splitlines():
        if line.startswith("n"):
            held.add(os.path.realpath(line[1:]))
    return held


def find_ghost_tasks(procs, hook: bool = False) -> list[str]:
    """Background-task cards the harness may still be counting, and live jobs worth naming.

    A finished task's output ends with the harness's own `[exited with code N]` marker. A file with no
    marker AND no live process holding it open is a card whose process is already gone — the timer in the
    UI keeps counting but nothing is running. Measured 2026-09-18: the operator saw an "84 min" job while
    `ps` held no user process older than three minutes.
    """
    findings: list[str] = []
    ghosts: list[tuple[int, str]] = []
    now = time.time()
    recent = [(f, mtime) for f, mtime in task_files() if now - mtime < GHOST_WINDOW_H * 3600]
    if not recent:
        return findings
    held = writers([f for f, _ in recent])
    for f, mtime in recent:
        try:
            tail = open(f, "rb").read()[-400:].decode("utf-8", "replace")
        except OSError:
            continue
        if "[exited with code" in tail:
            continue                                            # the harness recorded its exit
        age = int((now - mtime) / 60)
        if f in held:
            if age >= LONG_JOB_MIN:
                findings.append(f"background job still running, quiet for {age} min — {os.path.basename(f)}. "
                                f"Live, not stale; check it is making progress.")
        elif age >= GHOST_GRACE_MIN:
            ghosts.append((age, os.path.basename(f)))
    if hook:
        return findings                                         # live jobs only; ghosts are report-only
    for age, name in sorted(ghosts)[:GHOST_MAX]:
        findings.append(f"ghost background task {name} — no process holds it open and it records no exit, "
                        f"last written {age} min ago. Nothing is running behind it; if its card still shows "
                        f"a running timer, that timer is counting nothing.")
    if len(ghosts) > GHOST_MAX:
        findings.append(f"({len(ghosts) - GHOST_MAX} older ghost task file(s) not listed.)")
    return findings


def find(procs) -> tuple[list[str], list[tuple[int, str]], list[str]]:
    findings: list[str] = []
    to_end: list[tuple[int, str]] = []

    for p in procs.values():                                    # 1. zombies — reported, never swept
        if p["stat"].startswith("Z"):
            parent = procs.get(p["ppid"], {}).get("cmd", "gone")[:60]
            findings.append(f"zombie pid {p['pid']} — already dead, holding only a pid slot. Its parent "
                            f"({p['ppid']}: {parent}) must reap it; ending a live parent to clear a dead "
                            f"child is your call, not this script's.")

    brokers = [p for p in procs.values() if BROKER in p["cmd"]]
    if brokers:                                                 # 2. brokers with nobody on the socket
        holders = socket_holders()
        for p in brokers:
            if protected(procs, p["pid"]):
                continue
            m = re.search(r"--endpoint unix:(\S+)", p["cmd"])
            if not m:
                continue
            mine = set(tree(procs, p["pid"]))
            outside = holders.get(m.group(1), set()) - mine
            if outside:
                continue
            where = re.search(r"--cwd (\S+)", p["cmd"])
            findings.append(f"stale codex broker {p['pid']} — {p['etime']} old, {rss_mb(procs, p['pid'])} MB "
                            f"across {len(mine)} processes, no client on its socket. "
                            f"Was serving: {where.group(1) if where else 'unknown'}")
            to_end.append((p["pid"], "codex broker with no client"))

    for p in procs.values():                                    # 3. abandoned harness leftovers
        if p["ppid"] != 1 or not HARNESS.search(p["cmd"]) or protected(procs, p["pid"]):
            continue
        if minutes(p["etime"]) < ORPHAN_GRACE_MIN:
            continue
        findings.append(f"orphaned harness process {p['pid']} — {p['etime']} old, "
                        f"{rss_mb(procs, p['pid'])} MB, parent gone: {p['cmd'][:70]}")
        to_end.append((p["pid"], "orphaned harness leftover"))

    stale_dirs: list[str] = []                                  # 4. socket dirs whose broker is gone
    import glob
    # TMPDIR IS /var/folders/<x>/<y>/T on macOS, so these two patterns overlap; realpath + dedupe, or every
    # directory is reported twice (measured 2026-09-18, on this script's own first run).
    candidates = sorted({os.path.realpath(d)
                         for pat in (os.path.join(os.environ.get("TMPDIR", "/tmp"), "cxc-*"),
                                     "/var/folders/*/*/T/cxc-*")
                         for d in glob.glob(pat)})
    for d in candidates:
        if not os.path.isdir(d):
            continue
        pidfile = os.path.join(d, "broker.pid")
        if os.path.exists(pidfile):
            try:
                if int(open(pidfile).read().strip()) in procs:
                    continue
            except (ValueError, OSError):
                pass
        stale_dirs.append(d)
        findings.append(f"leftover socket directory {d} — its broker is gone")

    # 5. Long-running LIVE jobs go to the hook; ghost cards are report-only. A foreground tool call's
    # output file is also a writer-less file with no exit marker, so ghosts carry false positives that
    # are worth seeing on demand but not worth interrupting every prompt with (measured 2026-09-18).
    findings += find_ghost_tasks(procs, hook=HOOK_MODE)
    return findings, to_end, stale_dirs


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--report"
    if mode in ("--help", "-h"):
        print(__doc__)
        return 0
    global HOOK_MODE
    HOOK_MODE = (mode == "--json")
    procs = snapshot()
    findings, to_end, stale_dirs = find(procs)

    if not findings:
        if mode != "--json":
            print("nothing stale: no zombies, no orphaned brokers, no abandoned harness processes.")
        return 0

    if mode == "--json":                                        # a hook must be quiet when there is nothing to say
        reclaim = sum(rss_mb(procs, pid) for pid, _ in to_end)
        text = f"Background-process sweeper: {len(findings)} finding(s)."
        if to_end:
            text += (f" About {reclaim} MB is reclaimable by ending {len(to_end)} stale tree(s) — "
                     f"run `~/.claude/tools/sweep-stale.py --sweep`.")
        text += "\n" + "\n".join(f"  - {f}" for f in findings)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                                 "additionalContext": text}}))
        return 0

    for f in findings:
        print(f"• {f}")

    if mode == "--sweep":
        if not to_end:
            print("\nnothing to end (zombies and leftover directories are reported, not swept).")
        for pid, why in to_end:
            if protected(procs, pid):
                print(f"skipped {pid} — protected")
                continue
            pids = tree(procs, pid)
            print(f"ending {pid} ({why}): {' '.join(str(p) for p in pids)}")
            for p in reversed(pids):                            # children first, so none is re-parented mid-sweep
                try:
                    os.kill(p, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        if to_end:
            time.sleep(3)
            for pid, _ in to_end:
                for p in tree(procs, pid):
                    try:
                        os.kill(p, 0)
                    except OSError:
                        continue
                    print(f"  {p} ignored TERM; KILL")
                    try:
                        os.kill(p, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
        # Re-scan: the directories were owned by living brokers when `find` ran, so the first pass could
        # not call them stale. Their owners are gone now (measured — the first version removed nothing).
        _, _, stale_dirs = find(snapshot())
        for d in stale_dirs:
            subprocess.run(["rm", "-rf", d], check=False)
            print(f"removed {d}")
        print("\nswept. Re-run without --sweep to confirm.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
