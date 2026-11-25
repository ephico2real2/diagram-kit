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

The guard: this script does not end a process whose own command is under /Applications or /System, an editor's
extension host, the Claude, Cursor or VS Code app, the CRC or container virtual machines, launchd, or this
process's own ancestry. It reads only the process that a finding names. --sweep ends the whole tree of that
process, so a child that matches the guard also ends (measured 2026-11-07: helpers under
/Applications/ChatGPT.app ended with their stale broker).

The --workbench mode is a separate report, on disk and not on processes: the scratch folders of pull requests and
issues that are done. It asks GitHub with `gh` for the state of each one, and a folder is removable only when GitHub
answers MERGED or CLOSED. An item that `gh` cannot answer is unknown, and never removable.

  sweep-stale.py          report, human-readable
  sweep-stale.py --json   report as a Claude Code hook payload; prints nothing when clean
  sweep-stale.py --sweep  end what the report names: TERM, then KILL after a grace
  sweep-stale.py --workbench <dir> [--repo [HOST/]OWNER/REPO] [--prefix NAME] [--archive <dir>] [--sweep]
                          report the folders under <dir> of merged or closed pull requests and issues, and the
                          worktrees whose branch merged; --sweep removes what the report marks removable
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
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


# --workbench: the scratch of pull requests and issues that are done.
#
# Written 2026-11-25, after the review exports, implementer output folders and worktrees of one project's workbench
# grew to 45 GB and slowed the machine. Every folder this mode removes ties to a pull request or an issue that GitHub
# says is MERGED or CLOSED, or is a worktree whose branch has a MERGED pull request. Anything it cannot prove is kept.

PREFIXES = ("review", "pr", "wt", "issue", "fix")
DONE = {"MERGED", "CLOSED"}
STATES = {"OPEN", *DONE}
GH_TIMEOUT_S = 30
GH_WORKERS = 8
# git@host:owner/repo.git, ssh://git@host:22/owner/repo.git, https://host/owner/repo. A local path does not match.
REMOTE = re.compile(r"(?:[a-z][a-z0-9+.-]*://)?(?:[^@/]+@)?(?P<host>[A-Za-z0-9][^:/@]*\.[^:/@]+)(?::\d+)?[:/]"
                    r"(?P<owner>[^/]+)/(?P<name>[^/]+?)(?:\.git)?/?")


def gh_json(args: list[str]) -> tuple[object, str]:
    """Run gh and parse its JSON: (value, "") or (None, why). No network, no auth or no gh is a why, never a raise."""
    try:
        r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=GH_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError) as e:
        return None, f"gh did not run ({e.__class__.__name__})"
    if r.returncode != 0:
        return None, (r.stderr.strip().splitlines() or [f"gh exited {r.returncode}"])[0][:120]
    try:
        return json.loads(r.stdout), ""
    except ValueError:
        return None, "gh printed no JSON"


def number_state(repo: str, number: str) -> tuple[str, str]:
    """(OPEN | CLOSED | MERGED | unknown, detail) of the issue or pull request that a folder name gives.

    `gh issue view` answers for both: measured 2026-11-25 with gh 2.101.0, it gave MERGED for a merged pull request.
    `gh pr view` fails on an issue number, and a project can name a review folder for an issue (review-<N> for issue N).
    """
    value, why = gh_json(["issue", "view", number, "--repo", repo, "--json", "state"])
    state = value.get("state") if isinstance(value, dict) else None
    if state in STATES:
        return state, f"{repo}#{number} {state}"
    return "unknown", f"{repo}#{number}: {why or f'gh answered state {state!r}'}"


def branch_state(repo: str, branch: str) -> tuple[str, str]:
    """(OPEN | MERGED | CLOSED | none | unknown, detail) of the pull requests from a branch. An open one wins."""
    value, why = gh_json(["pr", "list", "--repo", repo, "--head", branch, "--state", "all",
                          "--json", "number,state"])
    if not isinstance(value, list) or not all(isinstance(p, dict) and p.get("state") in STATES for p in value):
        return "unknown", f"{repo} branch {branch}: {why or 'gh answered no list of pull requests'}"
    for state in ("OPEN", "MERGED", "CLOSED"):
        hits = [p for p in value if p["state"] == state]
        if hits:
            return state, f"{repo}#{hits[0].get('number')} {state}, branch {branch}"
    return "none", f"{repo}: no pull request from branch {branch}"


def git_out(path: str, *args: str) -> str | None:
    """stdout of a git command in `path`, or None when git fails."""
    try:
        r = subprocess.run(["git", "-C", path, *args], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def remote_repo(path: str) -> str | None:
    """HOST/OWNER/REPO of the checkout's origin, the form `gh --repo` takes. The URL itself is never printed."""
    m = REMOTE.fullmatch((git_out(path, "config", "--get", "remote.origin.url") or "").strip())
    return f"{m['host']}/{m['owner']}/{m['name']}" if m else None


def worktree_locked(path: str) -> bool | None:
    """Whether `git worktree list --porcelain` marks this worktree `locked`; None when git cannot tell."""
    out = git_out(path, "worktree", "list", "--porcelain")
    if out is None:
        return None
    target = os.path.realpath(path)
    for record in out.split("\n\n"):
        lines = record.splitlines()
        if lines and lines[0].startswith("worktree ") and os.path.realpath(lines[0][len("worktree "):]) == target:
            return any(line == "locked" or line.startswith("locked ") for line in lines[1:])
    return None


def checkout(path: str) -> dict:
    """A git checkout inside a folder: a linked worktree or a clone, and what its removal would lose.

    `git worktree remove` keeps the branch and its commits in the main repository, so a linked worktree loses only
    its uncommitted change, which the sweep saves first. A clone also loses commits not pushed and its stashes, so
    either one blocks its removal.
    """
    git_dir = git_out(path, "rev-parse", "--absolute-git-dir")
    common = git_out(path, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if git_dir is None or common is None:
        return {"path": path, "linked": False, "branch": "", "repo": None, "blocks": ["git cannot read it"]}
    linked = os.path.realpath(git_dir.strip()) != os.path.realpath(common.strip())
    c = {"path": path, "linked": linked, "common": common.strip(), "repo": remote_repo(path), "blocks": [],
         "branch": (git_out(path, "symbolic-ref", "--short", "-q", "HEAD") or "").strip()}
    if linked:
        locked = worktree_locked(path)
        if locked is not False:
            c["blocks"].append("worktree is locked" if locked else "git cannot tell whether the worktree is locked")
    else:
        unpushed = git_out(path, "log", "--branches", "--not", "--remotes", "--oneline", "-1")
        if unpushed is None or unpushed.strip():
            c["blocks"].append("clone has commits not pushed" if unpushed else "git cannot list unpushed commits")
        stashes = git_out(path, "stash", "list")
        if stashes is None or stashes.strip():
            c["blocks"].append("clone has a stash" if stashes else "git cannot list the stashes")
        trees = git_out(path, "worktree", "list", "--porcelain")
        if trees is None or trees.count("\nworktree ") > 0:     # its linked worktrees would lose their repository
            c["blocks"].append("clone has linked worktrees" if trees else "git cannot list its worktrees")
    return c


def scan(top: str) -> tuple[int, list[str]]:
    """Disk use of a folder in bytes, as `du` counts it, and the outermost git checkouts inside it."""
    size, repos, seen, stack = os.lstat(top).st_blocks * 512, [], set(), [top]
    while stack:
        d = stack.pop()
        try:
            entries = list(os.scandir(d))
        except OSError:
            continue
        for e in entries:
            try:
                st = e.stat(follow_symlinks=False)
            except OSError:
                continue
            if st.st_nlink > 1 and not stat.S_ISDIR(st.st_mode):
                if (st.st_dev, st.st_ino) in seen:              # a hard link is counted once
                    continue
                seen.add((st.st_dev, st.st_ino))
            size += st.st_blocks * 512
            if e.name == ".git":
                repos.append(d)
            if e.is_dir(follow_symlinks=False):
                stack.append(e.path)
    outer: list[str] = []
    for r in sorted(repos, key=len):                            # a submodule is part of its parent's checkout
        if not any(r == o or r.startswith(o + os.sep) for o in outer):
            outer.append(r)
    return size, outer


def shallow_checkouts(top: str) -> list[str]:
    """Checkouts at the folder itself or one level down, the workbench layout `<topic>/<repository>`. No full walk."""
    found = [top] if os.path.lexists(os.path.join(top, ".git")) else []
    try:
        found += [e.path for e in os.scandir(top)
                  if e.is_dir(follow_symlinks=False) and os.path.lexists(os.path.join(e.path, ".git"))]
    except OSError:
        pass
    return found


def open_paths() -> list[str] | None:
    """Every path a live process holds open, working directories included, or None when lsof cannot tell."""
    try:
        r = subprocess.run(["lsof", "-n", "-P", "-F", "n"], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if not r.stdout:                                            # lsof exits 1 on a partial read; no output is no answer
        return None
    return [line[1:] for line in r.stdout.splitlines() if line.startswith("n")]


def human(size: int) -> str:
    for unit, scale in (("GB", 1024 ** 3), ("MB", 1024 ** 2), ("KB", 1024)):
        if size >= scale:
            return f"{size / scale:.1f} {unit}"
    return f"{size} B"


def numbered(prefixes: tuple[str, ...]) -> re.Pattern:
    """`<prefix>-<N>` or `<prefix>_<N>`, alone or with `-` or `_` and more: review_12_codex, wt-12-outputs."""
    return re.compile(rf"(?:{'|'.join(map(re.escape, prefixes))})[-_](?P<number>\d+)(?:[-_].*)?")


def survey(root: str, repo_arg: str | None, prefixes: tuple[str, ...] = PREFIXES) -> tuple[list[dict], int]:
    """Each folder under `root` tied to a pull request, an issue or a branch, with its verdict; and the rest's count."""
    items, others, pattern = [], 0, numbered(prefixes)
    for e in sorted(os.scandir(root), key=lambda e: e.name):
        if not e.is_dir(follow_symlinks=False):
            continue
        m = pattern.fullmatch(e.name)
        shallow = [] if m else shallow_checkouts(e.path)
        if not m and (not shallow or not all(checkout(p)["linked"] for p in shallow)):
            others += 1                                         # a clone or a plain folder: not a worktree to judge
            continue
        size, repos = scan(e.path)
        item = {"name": e.name, "path": e.path, "size": size, "checkouts": [checkout(r) for r in repos],
                "blocks": [], "queries": []}
        if m:
            # The number is the project's. Measured 2026-11-25: 6 numbered folders of a real workbench held clones of
            # a second repository, and each number was an issue of the main one. The folder's remote stands in only
            # when there is no --repo.
            named = {c["repo"] for c in item["checkouts"] if c["repo"]}
            if repo_arg:
                item["queries"].append((number_state, (repo_arg, m["number"])))
            elif len(named) == 1:
                item["queries"].append((number_state, (named.pop(), m["number"])))
            elif named:
                item["unknown"] = f"#{m['number']}: its checkouts name {', '.join(sorted(named))}; pass --repo"
            else:
                item["unknown"] = f"#{m['number']}: no GitHub remote in the folder; pass --repo"
        else:
            for c in item["checkouts"]:
                if not c["linked"]:
                    item["blocks"].append(f"{os.path.relpath(c['path'], root)} is a clone, not a worktree")
                elif not c["branch"]:
                    item["blocks"].append(f"{os.path.relpath(c['path'], root)} has a detached HEAD")
                elif c["repo"] or repo_arg:
                    item["queries"].append((branch_state, (c["repo"] or repo_arg, c["branch"])))
                else:
                    item["unknown"] = f"branch {c['branch']}: no GitHub remote in the worktree; pass --repo"
        item["worktree"] = not m
        for c in item["checkouts"]:
            item["blocks"] += [f"{os.path.relpath(c['path'], root)}: {b}" for b in c["blocks"]]
        items.append(item)

    calls = [(item, q) for item in items if "unknown" not in item for q in item["queries"]]
    with concurrent.futures.ThreadPoolExecutor(GH_WORKERS) as pool:
        answers = list(pool.map(lambda iq: iq[1][0](*iq[1][1]), calls))
    for item in items:
        item["answers"] = []
    for (item, _), answer in zip(calls, answers):
        item["answers"].append(answer)

    held = open_paths()
    held_real = None if held is None else [os.path.realpath(p) for p in held]
    for item in items:
        judge(item, held_real)
    return items, others


def judge(item: dict, held: list[str] | None) -> None:
    """Set the verdict: removable only when every answer says done and nothing blocks; unknown when any answer is."""
    states = [state for state, _ in item["answers"]]
    item["detail"] = "; ".join(detail for _, detail in item["answers"])
    if "unknown" in item or "unknown" in states:
        item["verdict"] = "unknown"
        item["detail"] = "; ".join(filter(None, [item.get("unknown", ""), item["detail"]]))
        return
    done = {"MERGED"} if item["worktree"] else DONE              # a worktree's branch must have merged
    if not states or any(s not in done for s in states):
        item["verdict"] = "keep"
        item["detail"] = "; ".join(filter(None, [item["detail"], *item["blocks"]]))
        return
    real = os.path.realpath(item["path"])
    if held is None:
        item["blocks"].append("lsof cannot tell whether a process holds it")
    elif any(p == real or p.startswith(real + os.sep) for p in held):
        item["blocks"].append("in use by a live process")
    item["verdict"] = "keep" if item["blocks"] else "removable"
    item["detail"] = "; ".join([item["detail"], *item["blocks"]])


def archive_changes(path: str, dest: str, label: str) -> str:
    """Save a checkout's uncommitted change as one patch, untracked files included, and return its path ("" if clean).

    A throwaway index keeps the checkout's own index untouched. Ignored files are not saved: they are rebuilt, not
    written. Raises RuntimeError when git cannot produce the patch, so the caller keeps the checkout.
    """
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": os.path.join(tmp, "index")}

        def git(*args: str) -> bytes:
            r = subprocess.run(["git", "-C", path, *args], capture_output=True, env=env, timeout=600)
            if r.returncode != 0:
                raise RuntimeError(f"git {args[0]} failed in {path}: "
                                   f"{r.stderr.decode('utf-8', 'replace').strip()[:200]}")
            return r.stdout

        git("read-tree", "HEAD")
        git("add", "-A")
        diff = git("diff", "--cached", "--binary", "HEAD")
        head = git("rev-parse", "HEAD").decode().strip()
    if not diff.strip():
        return ""
    os.makedirs(dest, exist_ok=True)
    target, n = os.path.join(dest, f"{label}.patch"), 1
    while os.path.exists(target):
        n += 1
        target = os.path.join(dest, f"{label}-{n}.patch")
    branch = (git_out(path, "symbolic-ref", "--short", "-q", "HEAD") or "").strip() or "a detached HEAD"
    header = (f"# Uncommitted change of {path}, on {branch} at {head},\n"
              f"# saved by sweep-stale.py --workbench on {time.strftime('%Y-%m-%d %H:%M')}.\n"
              f"# Apply it on that commit with: git apply <this file>\n\n")
    with open(target, "wb") as f:
        f.write(header.encode() + diff)
    return target


def remove(item: dict, root: str, archive_dir: str) -> tuple[bool, list[str]]:
    """Save, then remove one removable folder. Any failure before the removal keeps the whole folder."""
    notes: list[str] = []
    try:
        for c in item["checkouts"]:
            label = os.path.relpath(c["path"], root).replace(os.sep, "__")
            patch = archive_changes(c["path"], archive_dir, label)
            if patch:
                notes.append(f"saved the uncommitted change of {label} to {patch}")
    except (OSError, RuntimeError, subprocess.SubprocessError) as e:
        return False, notes + [f"kept: {e}"]
    for c in item["checkouts"]:
        if c["linked"]:                                         # so that the main repository forgets the worktree
            r = subprocess.run(["git", f"--git-dir={c['common']}", "worktree", "remove", "--force", c["path"]],
                               capture_output=True, text=True)
            if r.returncode != 0:
                return False, notes + [f"kept: git worktree remove failed: {r.stderr.strip()[:200]}"]
    shutil.rmtree(item["path"], ignore_errors=True)
    if os.path.lexists(item["path"]):
        return False, notes + ["part of the folder could not be removed"]
    return True, notes


def workbench(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="sweep-stale.py --workbench",
                                 description="Report, and with --sweep remove, the scratch of pull requests and "
                                             "issues that are done.")
    ap.add_argument("--workbench", required=True, metavar="DIR", help="the scratch root, one folder per job")
    ap.add_argument("--repo", metavar="[HOST/]OWNER/REPO",
                    help="the repository that the numbers in folder names belong to; "
                         "without it, each folder's own remote")
    ap.add_argument("--archive", metavar="DIR",
                    help="where uncommitted changes are saved (default: DIR/worktree-archive-<date>)")
    ap.add_argument("--prefix", action="append", default=[], metavar="NAME",
                    help=f"another folder prefix that a number follows (built in: {', '.join(PREFIXES)})")
    ap.add_argument("--sweep", action="store_true", help="remove what the report marks removable")
    args = ap.parse_args(argv)
    if any(not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", x) for x in args.prefix):
        print("A --prefix is letters and digits, starting with a letter.")
        return 2

    root = os.path.abspath(args.workbench)
    if not os.path.isdir(root):
        print(f"{root} is not a directory.")
        return 2
    if git_out(root, "rev-parse", "--is-inside-work-tree") is not None:
        # Each top-level folder must be one job's scratch. Inside a repository, they are its source.
        print(f"{root} is inside a git repository. Point --workbench at the scratch root that holds the jobs.")
        return 2
    archive_dir = os.path.realpath(args.archive or os.path.join(root, f"worktree-archive-{time.strftime('%Y-%m-%d')}"))
    items, others = survey(root, args.repo, PREFIXES + tuple(args.prefix))
    print(f"Workbench {root}, read {time.strftime('%Y-%m-%d %H:%M %Z')}.")
    width = max([len(i["name"]) for i in items] + [10])
    for i in items:
        print(f"{i['verdict']:<9}  {i['name']:<{width}}  {human(i['size']):>9}  {i['detail']}")
    removable = [i for i in items if i["verdict"] == "removable"]
    unknown = sum(i["verdict"] == "unknown" for i in items)
    print(f"\n{len(removable)} removable, {human(sum(i['size'] for i in removable))}. "
          f"{unknown} unknown, never removed. {others} other folder(s) are not tied to a pull request, an issue or "
          f"a worktree branch, and stay.")
    if not args.sweep:
        if removable:
            print("Nothing was deleted. Add --sweep to remove the removable folders.")
        return 0

    if any(archive_dir == os.path.realpath(i["path"]) or archive_dir.startswith(os.path.realpath(i["path"]) + os.sep)
           for i in removable):
        print(f"{archive_dir} is inside a folder to remove. Choose another --archive.")
        return 2
    freed, removed, failed = 0, 0, 0
    for i in removable:
        ok, notes = remove(i, root, archive_dir)
        for note in notes:
            print(f"  {i['name']}: {note}")
        if ok:
            removed, freed = removed + 1, freed + i["size"]
            print(f"removed {i['name']} ({human(i['size'])})")
        else:
            failed += 1
    print(f"\nremoved {removed} folder(s), freed {human(freed)}." + (f" {failed} kept on an error." if failed else ""))
    return 1 if failed else 0


def main() -> int:
    if "--workbench" in sys.argv[1:]:
        return workbench(sys.argv[1:])
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
                     f"run `{os.path.abspath(__file__)} --sweep`.")      # the copy that ran, as invoked
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
