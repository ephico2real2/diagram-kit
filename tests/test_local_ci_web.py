# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""local_ci_web.py finds act-ci.sh runs, reads their status and logs, ties act containers to a run, and serves them on
loopback. The Podman parts are tested on recorded shapes (a multiplexed log frame, an inspect row); the HTTP server
runs for real, on a free port, with no Podman socket."""

from __future__ import annotations

import json
import os
import struct
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "local-ci-web"))
import local_ci_web as al  # noqa: E402 (the skill folder is not a package)


class StatusTest(unittest.TestCase):
    def test_jobs_with_start_exit_and_a_note(self):
        text = ("verify start 05:51:30\nverify exit=0 05:56:27\n"
                "secret-scan start 06:03:18\nsecret-scan exit=0 commits=3 native gitleaks 8.30.1 darwin/arm64 06:03:19\n"
                "api-contracts start 06:03:20\n")
        jobs = al.parse_status(text)
        self.assertEqual([j["job"] for j in jobs], ["verify", "secret-scan", "api-contracts"])
        self.assertEqual(jobs[0], {"job": "verify", "start": "05:51:30", "end": "05:56:27", "rc": 0, "note": ""})
        self.assertEqual(jobs[1]["note"], "commits=3 native gitleaks 8.30.1 darwin/arm64")
        self.assertEqual(jobs[1]["end"], "06:03:19")
        self.assertIsNone(jobs[2]["rc"])

    def test_a_failure_and_noise(self):
        jobs = al.parse_status("garbage line\napi-contracts start 06:03:20\napi-contracts exit=1 06:04:44\n")
        self.assertEqual(jobs[0]["rc"], 1)


class CommandTest(unittest.TestCase):
    def test_act_ci_command(self):
        cmd = "/bin/bash /home/dev/proj/ci/local/act-ci.sh -r /home/dev/w/app -b 1a2b3c4d -o /home/dev/w/act-1"
        self.assertEqual(al.parse_act_ci(cmd), {"repo": "/home/dev/w/app", "base": "1a2b3c4d", "out": "/home/dev/w/act-1"})

    def test_other_commands(self):
        self.assertIsNone(al.parse_act_ci("act pull_request -W .github/workflows/ci.yml -j verify"))
        self.assertIsNone(al.parse_act_ci("unbalanced 'quote"))
        self.assertIsNone(al.parse_act_ci("/bin/bash act-ci.sh -b abc"))

    def test_without_o_the_logs_go_where_act_ci_puts_them(self):
        # act-ci.sh: logs=${logs:-$(dirname "$repo")/act-logs}
        opts = al.parse_act_ci("/bin/bash act-ci.sh -r /w/proj/app -b b")
        self.assertEqual(opts, {"repo": "/w/proj/app", "base": "b", "out": ""})
        self.assertEqual(al.run_paths(opts, "/")["out"], str(Path("/w/proj/act-logs").resolve()))

    def test_relative_paths_resolve_from_the_process_folder(self):
        with tempfile.TemporaryDirectory() as d:
            cwd = Path(d).resolve()
            opts = al.parse_act_ci("bash ci/local/act-ci.sh -r . -b b -o ../logs-1")
            paths = al.run_paths(opts, str(cwd))
            self.assertEqual((paths["repo"], paths["out"]), (str(cwd), str(cwd.parent / "logs-1")))

    def test_the_working_folder_of_a_live_process(self):
        self.assertEqual(Path(al.process_cwd(os.getpid())).resolve(), Path.cwd().resolve())


class DemuxTest(unittest.TestCase):
    @staticmethod
    def frame(stream: int, payload: bytes) -> bytes:
        return bytes([stream, 0, 0, 0]) + struct.pack(">I", len(payload)) + payload

    def test_frames_from_both_streams_join_in_order(self):
        raw = self.frame(1, b"out one\n") + self.frame(2, b"err two\n") + self.frame(1, b"out three\n")
        self.assertEqual(al.demux(raw), "out one\nerr two\nout three\n")

    def test_tty_stream_is_raw_text(self):
        self.assertEqual(al.demux(b"plain text from a tty\n"), "plain text from a tty\n")

    def test_a_cut_last_frame_keeps_what_arrived(self):
        raw = self.frame(1, b"whole\n") + self.frame(1, b"cut payload")[:12]
        self.assertTrue(al.demux(raw).startswith("whole\n"))


class ContainerTest(unittest.TestCase):
    def test_label_drops_the_hashes(self):
        job = "act-CI-Migrations-PostgreSQL-16-11-19c452ad94df44ad6547d320410ed3ae0b392fa3864f24dfb595e677db264c24"
        service = "act-CI-Migrations-PostgreSQL-16-11-19c452ad94df44ad6547d320410e-8c297ba9e258038752ad330ebad281ca"
        self.assertEqual(al.container_label(job), "CI-Migrations-PostgreSQL-16-11")
        self.assertEqual(al.container_label(service), "CI-Migrations-PostgreSQL-16-11")

    def test_attach_by_working_folder_and_by_mount(self):
        with tempfile.TemporaryDirectory() as d:
            repo = str(Path(d).resolve())
            runs = [{"repo": repo, "out": "/o"}]
            containers = [{"name": "act-a", "workdir": repo, "mounts": []},
                          {"name": "act-b", "workdir": "/elsewhere", "mounts": ["/opt/x", repo]},
                          {"name": "act-c", "workdir": "/elsewhere", "mounts": []}]
            state = al.attach(runs, containers)
            self.assertEqual([c["name"] for c in state["runs"][0]["containers"]], ["act-a", "act-b"])
            self.assertEqual([c["name"] for c in state["other_containers"]], ["act-c"])

    def test_two_runs_of_one_repository_give_containers_to_the_running_one(self):
        with tempfile.TemporaryDirectory() as d:
            repo = str(Path(d).resolve())
            runs = [{"repo": repo, "out": "/new", "running": True}, {"repo": repo, "out": "/old", "running": False}]
            state = al.attach(runs, [{"name": "act-a", "workdir": repo, "mounts": []}])
            self.assertEqual([len(r["containers"]) for r in state["runs"]], [1, 0])


class TailTest(unittest.TestCase):
    def test_last_lines_of_a_large_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "big.log"
            p.write_text("".join(f"line {i}\n" for i in range(50000)))
            self.assertEqual(al.tail_file(p, 3).strip().splitlines(), ["line 49997", "line 49998", "line 49999"])


class RunsTest(unittest.TestCase):
    def test_a_given_folder_is_described(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "status.txt").write_text("verify start 05:51:30\n")
            (Path(d) / "verify.log").write_text("x\n")
            runs = al.Runs([d])
            described = [r for r in runs.refresh() if r["out"] == str(Path(d).resolve())][0]
            self.assertEqual(described["current"], "verify")
            self.assertEqual(described["logs"], ["verify.log"])
            self.assertIsNotNone(runs.folder(str(Path(d).resolve())))
            self.assertIsNone(runs.folder("/etc"))

    def test_a_given_folder_takes_the_repository_of_its_live_process(self):
        with tempfile.TemporaryDirectory() as d:
            out = str(Path(d).resolve())
            runs = al.Runs([out])
            runs._add(out, {"repo": "/r/app", "base": "abc"}, pid=42)
            run = runs._runs[out]
            self.assertEqual((run["repo"], run["base"], run["pid"]), ("/r/app", "abc", 42))

    def test_running_first_then_newest_status(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            import os
            for d, when in ((a, 1000), (b, 2000)):
                (Path(d) / "status.txt").write_text("verify start 05:51:30\n")
                os.utime(Path(d) / "status.txt", (when, when))
            runs = al.Runs([a, b])
            order = [r["out"] for r in runs.refresh() if r["out"] in (str(Path(a).resolve()), str(Path(b).resolve()))]
            self.assertEqual(order, [str(Path(b).resolve()), str(Path(a).resolve())])


class ServerTest(unittest.TestCase):
    """The real handler on a free loopback port, with one run folder and no Podman socket."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.out = Path(self.dir.name).resolve() / "run"
        self.out.mkdir()
        (self.out / "status.txt").write_text("verify start 05:51:30\n")
        (self.out / "verify.log").write_text("".join(f"line {i}\n" for i in range(10)))
        (self.out.parent / "outside.log").write_text("not a run file\n")
        al.Handler.runs, al.Handler.sock = al.Runs([str(self.out)]), None
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), al.Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.dir.cleanup()

    def get(self, path: str) -> tuple[int, bytes]:
        try:
            with urllib.request.urlopen(self.base + path) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as err:
            return err.code, err.read()

    def test_the_page_and_the_state(self):
        code, page = self.get("/")
        self.assertEqual(code, 200)
        self.assertIn(b"<title>Local CI Runs</title>", page)
        code, body = self.get("/api/state")
        state = json.loads(body)
        run = next(r for r in state["runs"] if r["out"] == str(self.out))
        self.assertEqual((run["current"], run["logs"], state["podman_error"]), ("verify", ["verify.log"], "no Podman socket"))

    def test_a_log_tail(self):
        code, body = self.get(f"/api/log?run={self.out}&file=verify.log&tail=2")
        self.assertEqual((code, body.decode().split()), (200, ["line", "8", "line", "9"]))

    def test_only_logs_of_a_known_run_are_served(self):
        for path in (f"/api/log?run={self.out}&file=../outside.log", f"/api/log?run={self.out.parent}&file=outside.log",
                     f"/api/log?run={self.out}&file=status.txt", "/api/clog?name=act-x"):
            self.assertEqual(self.get(path)[0], 404, path)


if __name__ == "__main__":
    unittest.main()
