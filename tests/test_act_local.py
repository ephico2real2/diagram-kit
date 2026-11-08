# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""act-ci.sh runs each job of a workflow under act with the settings that measured failures require (skill/act-local).

The tests run the real script with stand-in commands for act, podman and gh, so they need no container engine.
yq, git, perl, tar and shasum are the real tools."""

import hashlib
import io
import os
import pathlib
import platform
import shutil
import subprocess
import tarfile
import textwrap

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "act-local" / "act-ci.sh"
VERSION = "8.30.1"

pytestmark = pytest.mark.skipif(not all(shutil.which(t) for t in ("yq", "git", "perl", "shasum")),
                                reason="act-ci.sh needs yq, git, perl and shasum")


def host_asset() -> str:
    cpu = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "x64"}[platform.machine()]
    return f"gitleaks_{VERSION}_{platform.system().lower()}_{cpu}.tar.gz"


def workflow(pin: str) -> str:
    return textwrap.dedent(f"""\
        name: CI
        on: [pull_request]
        jobs:
          verify:
            runs-on: ubuntu-latest
            steps:
              - run: echo verify
          migrations:
            runs-on: ubuntu-latest
            strategy:
              matrix:
                include:
                  - version: '16.11'
                    image: postgres:16.11-alpine@sha256:{'a' * 64}
                  - version: '18.6'
                    image: postgres:18.6@sha256:{'b' * 64}
            steps:
              - run: echo migrate
          secret-scan:
            runs-on: ubuntu-latest
            steps:
              - name: Install gitleaks
                env:
                  GITLEAKS_SHA256: {pin}
                run: |
                  # The release asset gitleaks_{VERSION}_linux_x64.tar.gz.
                  echo install
              - run: ./gitleaks git --no-banner --redact
        """)


def write_tool(folder: pathlib.Path, name: str, body: str) -> None:
    path = folder / name
    path.write_text("#!/bin/bash\n" + body)
    path.chmod(0o755)


@pytest.fixture
def env(tmp_path):
    """A clone with two commits, stand-in tools on PATH, and a release folder that the stand-in gh serves."""
    calls = tmp_path / "calls"
    calls.mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    release = tmp_path / "release"
    release.mkdir()

    # The release asset: a stand-in gitleaks that records its arguments.
    script = f'#!/bin/bash\necho "$@" >> "{calls}/gitleaks"\necho "no leaks found"\n'.encode()
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        info = tarfile.TarInfo("gitleaks")
        info.size, info.mode = len(script), 0o755
        tar.addfile(info, io.BytesIO(script))
    (release / host_asset()).write_bytes(buf.getvalue())
    x64_pin = "c" * 64
    (release / f"gitleaks_{VERSION}_checksums.txt").write_text(
        f"{x64_pin}  gitleaks_{VERSION}_linux_x64.tar.gz\n"
        f"{hashlib.sha256(buf.getvalue()).hexdigest()}  {host_asset()}\n")

    write_tool(bin_dir, "act", f'echo "$*" >> "{calls}/act"\n')
    write_tool(bin_dir, "podman", textwrap.dedent(f"""\
        echo "$*" >> "{calls}/podman"
        case "$1 $2" in
          "ps -a") printf 'act-CI-left-from-a-failed-job\\nkeep-me\\nact-Other-job\\n' ;;
        esac
        exit 0
        """))
    write_tool(bin_dir, "gh", textwrap.dedent(f"""\
        if [[ "$1 $2" == "auth token" ]]; then echo sample-token; exit 0; fi
        if [[ "$1 $2" == "release download" ]]; then
          shift 2; dest=.
          while [[ $# -gt 0 ]]; do [[ $1 == -D ]] && dest=$2; shift; done
          cp "{release}"/* "$dest"/; exit 0
        fi
        exit 1
        """))

    repo = tmp_path / "clone"
    repo.mkdir()
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.test"]
    subprocess.run([*git[:3], "init", "-q"], check=True)
    (repo / "README.md").write_text("base\n")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", "base"], check=True)
    base = subprocess.run([*git[:3], "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text(workflow(x64_pin))
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", "head"], check=True)

    run_env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "DOCKER_HOST": "unix:///stand-in.sock"}
    return {"repo": repo, "base": base, "calls": calls, "logs": tmp_path / "logs", "env": run_env}


def run(env, *extra):
    return subprocess.run(["bash", str(SCRIPT), "-r", str(env["repo"]), "-b", env["base"], "-o", str(env["logs"]), *extra],
                          env=env["env"], capture_output=True, text=True)


def act_calls(env):
    path = env["calls"] / "act"
    return path.read_text().splitlines() if path.exists() else []


def test_the_script_passes_its_syntax_and_lint_checks():
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)
    if shutil.which("shellcheck"):
        subprocess.run(["shellcheck", "-S", "style", str(SCRIPT)], check=True)


def test_every_act_call_names_the_workflow_and_the_job_and_cleans_up(env):
    result = run(env)
    assert result.returncode == 0, result.stdout + result.stderr
    calls = act_calls(env)
    assert len(calls) == 3
    for call in calls:
        assert call.startswith("pull_request -W .github/workflows/ci.yml -j ")
        for flag in ("--rm", "--pull=false", "--container-daemon-socket -", "-s GITHUB_TOKEN",
                     "-P ubuntu-latest=act-runner:ubuntu-24.04"):
            assert flag in call


def test_each_matrix_entry_runs_alone_selected_by_a_key_without_a_colon(env):
    run(env)
    matrix = [c for c in act_calls(env) if " -j migrations " in c]
    assert [c.split("--matrix ", 1)[1] for c in matrix] == ["version:16.11", "version:18.6"]
    assert not any("image:" in c for c in matrix)


def test_the_gitleaks_job_runs_natively_over_the_pull_request_range(env):
    run(env)
    assert not any(" -j secret-scan " in c for c in act_calls(env))
    head = subprocess.run(["git", "-C", str(env["repo"]), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert (env["calls"] / "gitleaks").read_text().split() == [
        "git", "--no-banner", "--redact", f"--log-opts={env['base']}..{head}", "."]
    assert "secret-scan exit=0 commits=1" in (env["logs"] / "status.txt").read_text()


def test_a_pin_that_is_not_in_the_release_checksum_file_stops_the_scan(env):
    ci = env["repo"] / ".github" / "workflows" / "ci.yml"
    ci.write_text(ci.read_text().replace("c" * 64, "d" * 64))
    subprocess.run(["git", "-C", str(env["repo"]), "-c", "user.name=t", "-c", "user.email=t@example.test",
                    "commit", "-qam", "another pin"], check=True)
    result = run(env, "-j", "secret-scan")
    assert result.returncode != 0
    assert "the workflow pin is not in the release checksum file" in (env["logs"] / "status.txt").read_text()
    assert not (env["calls"] / "gitleaks").exists()


def test_the_cleanup_removes_only_the_containers_of_this_workflow(env):
    run(env, "-j", "verify")
    removed = [line for line in (env["calls"] / "podman").read_text().splitlines() if line.startswith("rm -f")]
    assert removed and all(line == "rm -f act-CI-left-from-a-failed-job" for line in removed)


def test_a_working_tree_with_changes_is_refused_unless_allowed(env):
    (env["repo"] / "README.md").write_text("changed\n")
    result = run(env, "-j", "verify")
    assert result.returncode == 2 and "has changes" in result.stderr
    assert act_calls(env) == []
    assert run(env, "-j", "verify", "-d").returncode == 0


def test_no_arguments_print_the_usage():
    result = subprocess.run(["bash", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 2 and "usage: act-ci.sh" in result.stderr
