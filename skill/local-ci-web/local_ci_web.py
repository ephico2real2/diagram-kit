#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""local-ci-web: a live view of local CI runs (act-ci.sh of /setup-local-ci, under Podman), served on loopback.

It finds each running `act-ci.sh` process and its log folder (`-o`, or `<clone>/../act-logs` as act-ci.sh does),
reads the folder's `status.txt` and job logs, and reads the `act-*` containers and their logs through the Podman
socket. A run stays in the list after its process ends, until the server stops. Folders given with `--dir` are
shown too.

    python3 local_ci_web.py [--port 2026] [--dir <act output folder>]...

Only 127.0.0.1 is bound. A file is served only from a known run folder, and a container log only for a name that
starts with `act-`. The Podman socket path comes from `podman machine inspect`, or from `--socket`.
"""
from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import shlex
import socket
import struct
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

API = "/v5.0.0/libpod"
LOG_NAME = re.compile(r"^[A-Za-z0-9._-]+\.log$")
STATUS_LINE = re.compile(r"^(?P<job>\S+) (?P<event>start|exit=(?P<rc>-?\d+))(?P<rest>.*?) (?P<time>\d\d:\d\d:\d\d)$")
MAX_TAIL = 2000
HERE = Path(__file__).resolve().parent


# ---------------------------------------------------------------- run folders and their status

def parse_status(text: str) -> list[dict]:
    """The jobs of a status.txt, in order: name, start, end, rc (None while it runs) and any note."""
    jobs: dict[str, dict] = {}
    for line in text.splitlines():
        m = STATUS_LINE.match(line.strip())
        if not m:
            continue
        job = jobs.setdefault(m["job"], {"job": m["job"], "start": None, "end": None, "rc": None, "note": ""})
        if m["event"] == "start":
            job["start"] = m["time"]
        else:
            job["end"], job["rc"], job["note"] = m["time"], int(m["rc"]), m["rest"].strip()
    return list(jobs.values())


def parse_act_ci(command: str) -> dict | None:
    """The -r, -b and -o values of an act-ci.sh command line, or None if the line is not one. A value can be
    relative to the working folder of the process; `out` is empty when -o is not given."""
    try:
        words = shlex.split(command)
    except ValueError:
        return None
    if not any(w.endswith("act-ci.sh") for w in words):
        return None
    opts = {"repo": "", "base": "", "out": ""}
    for flag, key in (("-r", "repo"), ("-b", "base"), ("-o", "out")):
        if flag in words and words.index(flag) + 1 < len(words):
            opts[key] = words[words.index(flag) + 1]
    return opts if opts["out"] or opts["repo"] else None


def run_paths(opts: dict, cwd: str) -> dict:
    """Absolute repo and out folders. act-ci.sh writes to <dirname of the clone>/act-logs without -o."""
    def absolute(path: str) -> str:
        p = Path(path).expanduser()
        return str((p if p.is_absolute() else Path(cwd) / p).resolve())
    repo = absolute(opts["repo"]) if opts["repo"] else ""
    out = absolute(opts["out"]) if opts["out"] else str(Path(repo).parent / "act-logs")
    return {**opts, "repo": repo, "out": out}


def process_cwd(pid: int) -> str:
    """The working folder of a process (lsof on macOS, /proc on Linux), or "/" if it cannot be read."""
    proc = Path(f"/proc/{pid}/cwd")
    if proc.exists():
        return os.readlink(proc)
    out = subprocess.run(["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"], capture_output=True, text=True,
                         check=False).stdout
    return next((line[1:] for line in out.splitlines() if line.startswith("n")), "/")


class Runs:
    """The run folders known to this server. Running ones come from `ps`; ended ones stay listed."""

    def __init__(self, dirs: list[str]):
        self._lock = threading.Lock()
        self._runs: dict[str, dict] = {}
        for d in dirs:
            self._add(str(Path(d).expanduser().resolve()), {"repo": "", "base": ""}, pid=None)

    def _add(self, out: str, opts: dict, pid: int | None) -> None:
        run = self._runs.setdefault(out, {"out": out, "repo": "", "base": "", "pid": None,
                                          "first_seen": time.time()})
        # A folder given with --dir has no repository until its process shows up in ps.
        for key in ("repo", "base"):
            if opts.get(key):
                run[key] = opts[key]
        run["pid"] = pid

    def refresh(self) -> list[dict]:
        ps = subprocess.run(["ps", "-axo", "pid=,command="], capture_output=True, text=True, check=False).stdout
        live = {}
        for line in ps.splitlines():
            pid, _, command = line.strip().partition(" ")
            opts = parse_act_ci(command)
            if opts:
                relative = any(v and not Path(v).expanduser().is_absolute() for v in (opts["repo"], opts["out"]))
                paths = run_paths(opts, process_cwd(int(pid)) if relative else "/")
                live[paths["out"]] = (int(pid), paths)
        with self._lock:
            for run in self._runs.values():
                run["pid"] = None
            for out, (pid, opts) in live.items():
                self._add(out, opts, pid)
            described = [self._describe(r) for r in self._runs.values()]
        # Running runs first, then the most recent status.txt.
        return sorted(described, key=lambda r: (not r["running"], -r["updated"]))

    def folder(self, out: str) -> Path | None:
        with self._lock:
            return Path(out) if out in self._runs else None

    @staticmethod
    def _describe(run: dict) -> dict:
        out = Path(run["out"])
        status = out / "status.txt"
        jobs = parse_status(status.read_text(errors="replace")) if status.is_file() else []
        logs = sorted(p.name for p in out.glob("*.log")) if out.is_dir() else []
        current = next((j["job"] for j in jobs if j["start"] and j["rc"] is None), None)
        updated = status.stat().st_mtime if status.is_file() else run["first_seen"]
        return {**run, "running": run["pid"] is not None, "jobs": jobs, "logs": logs, "current": current,
                "updated": updated}


def tail_file(path: Path, lines: int) -> str:
    """The last `lines` lines of a file, read from its end so a large log costs little."""
    with path.open("rb") as f:
        f.seek(0, os.SEEK_END)
        size, block, data = f.tell(), 65536, b""
        while size > 0 and data.count(b"\n") <= lines:
            step = min(block, size)
            size -= step
            f.seek(size)
            data = f.read(step) + data
    return b"\n".join(data.split(b"\n")[-lines - 1:]).decode("utf-8", "replace")


# ---------------------------------------------------------------- Podman over its unix socket

class UnixHTTPConnection(http.client.HTTPConnection):
    def __init__(self, path: str, timeout: float = 5):
        super().__init__("localhost", timeout=timeout)
        self._path = path

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self._path)


def podman_socket() -> str:
    out = subprocess.run(["podman", "machine", "inspect", "--format", "{{.ConnectionInfo.PodmanSocket.Path}}"],
                         capture_output=True, text=True, check=False)
    path = out.stdout.strip()
    if out.returncode != 0 or not path:
        raise RuntimeError(f"podman machine inspect gave no socket path: {out.stderr.strip()}")
    return path


def podman_get(sock: str, path: str) -> bytes:
    conn = UnixHTTPConnection(sock)
    try:
        conn.request("GET", API + path)
        resp = conn.getresponse()
        body = resp.read()
        if resp.status != 200:
            raise RuntimeError(f"Podman {path}: HTTP {resp.status} {body[:200]!r}")
        return body
    finally:
        conn.close()


def demux(raw: bytes) -> str:
    """Join a multiplexed log stream: each frame is an 8-byte header (stream byte, 3 zero bytes, a big-endian
    size), then the payload. A stream that does not start with a valid header (a TTY container) is raw text."""
    if len(raw) < 8 or raw[0] not in (0, 1, 2) or raw[1:4] != b"\0\0\0":
        return raw.decode("utf-8", "replace")
    out, i = [], 0
    while i + 8 <= len(raw):
        size = struct.unpack(">I", raw[i + 4:i + 8])[0]
        out.append(raw[i + 8:i + 8 + size])
        i += 8 + size
    return b"".join(out).decode("utf-8", "replace")


def act_containers(sock: str) -> list[dict]:
    """Each act container, newest first, with the metadata that ties it to a run. act sets the working folder of
    the job container and of its service containers to the repository folder (the -r of act-ci.sh), and mounts
    the workspace there. The job container runs the runner image; a service runs its own image."""
    filters = quote(json.dumps({"name": ["^act-"]}))
    rows = json.loads(podman_get(sock, f"/containers/json?all=true&filters={filters}"))
    result = []
    for c in sorted(rows, key=lambda c: -int(c.get("StartedAt") or 0)):
        name = c["Names"][0]
        if not name.startswith("act-"):
            continue
        try:
            info = json.loads(podman_get(sock, f"/containers/{quote(name)}/json"))
        except RuntimeError:  # it ended between the list and the inspect
            continue
        config = info.get("Config") or {}
        mounts = [m.get("Destination", "") for m in info.get("Mounts") or []]
        image = c.get("Image", "")
        result.append({"name": name, "label": container_label(name), "state": c.get("State", ""),
                       "status": c.get("Status", ""), "image": image,
                       "role": "job" if "act-runner" in image else "service",
                       "workdir": config.get("WorkingDir", ""), "mounts": mounts,
                       "started": int(c.get("StartedAt") or 0)})
    return result


def container_label(name: str) -> str:
    """The workflow and job part of an act container name: act-<workflow>-<job>-<hash>[-<service hash>]."""
    return re.sub(r"(-[0-9a-f]{20,})+$", "", name[4:])


def attach(runs: list[dict], containers: list[dict]) -> dict:
    """Put each container under the run whose repository folder is its working folder or a mount destination."""
    # Two runs can share one repository folder (a new run from the same clone). The containers belong to the
    # running one; runs come in display order (running first, then newest), so the first run per folder wins.
    by_repo: dict[str, dict] = {}
    for r in runs:
        if r.get("repo"):
            by_repo.setdefault(str(Path(r["repo"]).expanduser().resolve()), r)
    for run in runs:
        run["containers"] = []
    other = []
    for c in containers:
        run = by_repo.get(c["workdir"]) or next((by_repo[m] for m in c["mounts"] if m in by_repo), None)
        (run["containers"] if run else other).append(c)
    return {"runs": runs, "other_containers": other}


# ---------------------------------------------------------------- HTTP

class Handler(BaseHTTPRequestHandler):
    runs: Runs
    sock: str | None

    def log_message(self, fmt, *args):  # one line per error only; the page polls every 3 s
        pass

    def _send(self, code: int, body: bytes, kind: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data, code: int = 200) -> None:
        self._send(code, json.dumps(data).encode(), "application/json")

    def do_GET(self) -> None:  # noqa: N802 (the stdlib name)
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        lines = max(1, min(int(q.get("tail", "200") or 200), MAX_TAIL))
        try:
            if url.path == "/":
                self._send(200, (HERE / "local_ci_web.html").read_bytes(), "text/html; charset=utf-8")
            elif url.path == "/api/state":
                runs = self.runs.refresh()
                containers, error = [], None
                if self.sock:
                    try:
                        containers = act_containers(self.sock)
                    except (OSError, RuntimeError) as err:
                        error = str(err)
                else:
                    error = "no Podman socket"
                self._json({**attach(runs, containers), "podman_error": error,
                            "now": time.strftime("%H:%M:%S", time.gmtime())})
            elif url.path == "/api/log":
                folder = self.runs.folder(q.get("run", ""))
                name = q.get("file", "")
                if folder is None or not LOG_NAME.match(name) or not (folder / name).is_file():
                    return self._json({"error": "unknown run or log"}, 404)
                self._send(200, tail_file(folder / name, lines).encode(), "text/plain; charset=utf-8")
            elif url.path == "/api/clog":
                name = q.get("name", "")
                if not self.sock or not re.fullmatch(r"act-[A-Za-z0-9._-]+", name):
                    return self._json({"error": "unknown container"}, 404)
                raw = podman_get(self.sock, f"/containers/{quote(name)}/logs?stdout=true&stderr=true&tail={lines}")
                self._send(200, demux(raw).encode(), "text/plain; charset=utf-8")
            else:
                self._json({"error": "not found"}, 404)
        except (OSError, RuntimeError, ValueError) as error:
            # A container that ends between the list and the log read gives 404 from Podman: say so, keep serving.
            print(f"local-ci-web: {url.path}: {error}", file=sys.stderr)
            self._json({"error": str(error)}, 502)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--port", type=int, default=2026)
    ap.add_argument("--dir", action="append", default=[], help="an act output folder to show, also after its run")
    ap.add_argument("--socket", help="the Podman API socket (default: podman machine inspect)")
    args = ap.parse_args()
    Handler.runs = Runs(args.dir)
    try:
        Handler.sock = args.socket or podman_socket()
    except RuntimeError as error:
        print(f"local-ci-web: {error}; containers are not shown", file=sys.stderr)
        Handler.sock = None
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"local-ci-web: http://127.0.0.1:{args.port}/ (Podman socket: {Handler.sock or 'none'})", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
