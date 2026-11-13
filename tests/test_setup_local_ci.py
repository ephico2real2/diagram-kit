# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""act-ci.sh runs each job of a workflow under act with the settings that measured failures require (skill/setup-local-ci).

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
SCRIPT = ROOT / "skill" / "setup-local-ci" / "act-ci.sh"
SETUP = ROOT / "skill" / "setup-local-ci" / "setup.sh"
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
          contract:
            runs-on: ubuntu-24.04
            steps:
              - run: echo contract
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
    digest = hashlib.sha256(buf.getvalue()).hexdigest()
    x64_asset = f"gitleaks_{VERSION}_linux_x64.tar.gz"
    # On an x64 Linux host the native asset is the pinned asset, so the pin is its real hash and the file has one line.
    x64_pin = digest if host_asset() == x64_asset else "c" * 64
    lines = {x64_asset: x64_pin, host_asset(): digest}
    (release / f"gitleaks_{VERSION}_checksums.txt").write_text("".join(f"{h}  {n}\n" for n, h in lines.items()))

    # The stand-in act: it runs a job only when a -P names the job's runs-on label, as act does. A job on a label with no -P
    # is skipped with act's own line and exit 0. ACT_SILENT=1 makes it exit 0 with no job line at all.
    write_tool(bin_dir, "act", textwrap.dedent(f"""\
        echo "$*" >> "{calls}/act"
        [[ -n ${{ACT_SILENT:-}} ]] && exit 0
        args=("$@"); workflow= job= platforms=
        for ((i = 0; i < ${{#args[@]}}; i++)); do
          case ${{args[i]}} in
            -W) workflow=${{args[i+1]}} ;; -j) job=${{args[i+1]}} ;; -P) platforms+=" ${{args[i+1]%%=*}} " ;;
          esac
        done
        label=$(awk -v job="  $job:" '$0 == job {{found = 1}} found && /runs-on:/ {{print $2; exit}}' "$workflow")
        if [[ $platforms == *" $label "* ]]; then
          echo "[$job] 🏁  Job succeeded"
        else
          echo "[$job] 🚧  Skipping unsupported platform -- Try running with \`-P $label=...\`"
        fi
        exit 0
        """))
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
    return {"repo": repo, "base": base, "calls": calls, "logs": tmp_path / "logs", "env": run_env, "pin": x64_pin}


def run(env, *extra):
    return subprocess.run(["bash", str(SCRIPT), "-r", str(env["repo"]), "-b", env["base"], "-o", str(env["logs"]), *extra],
                          env=env["env"], capture_output=True, text=True)


def act_calls(env):
    path = env["calls"] / "act"
    return path.read_text().splitlines() if path.exists() else []


def test_the_scripts_pass_their_syntax_and_lint_checks():
    for path in (SCRIPT, SETUP):
        subprocess.run(["bash", "-n", str(path)], check=True)
        if shutil.which("shellcheck"):
            subprocess.run(["shellcheck", "-S", "style", str(path)], check=True)


def test_every_act_call_names_the_workflow_and_the_job_and_cleans_up(env):
    result = run(env)
    assert result.returncode == 0, result.stdout + result.stderr
    calls = act_calls(env)
    assert len(calls) == 4
    for call in calls:
        assert call.startswith(f"pull_request -W {env['logs']}/workflow-r") and ".yml -j " in call
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
    ci.write_text(ci.read_text().replace(env["pin"], "d" * 64))
    subprocess.run(["git", "-C", str(env["repo"]), "-c", "user.name=t", "-c", "user.email=t@example.test",
                    "commit", "-qam", "another pin"], check=True)
    result = run(env, "-j", "secret-scan")
    assert result.returncode != 0
    assert "the workflow pin is not in the release checksum file" in (env["logs"] / "status.txt").read_text()
    assert not (env["calls"] / "gitleaks").exists()


def test_the_cleanup_removes_only_the_containers_of_this_run(env):
    """Two projects often both name their workflow CI (#53). The cleanup of one run must not remove the containers of
    another run: neither those that act names after the workflow alone, nor those of another act-ci.sh run."""
    logs = env["logs"]
    write_tool(env["repo"].parent / "bin", "podman", textwrap.dedent(f"""\
        echo "$*" >> "{env['calls']}/podman"
        if [[ "$1 $2" == "ps -a" ]]; then
          printf 'act-CI-verify-of-another-project\\nact-r261110000000p1-CI-verify-of-another-run\\nkeep-me\\n'
          for copy in "{logs}"/workflow-*.yml; do
            [[ -e $copy ]] && echo "act-$(basename "$copy" .yml | sed 's/^workflow-//')-CI-verify-of-this-run"
          done
        fi
        exit 0
        """))
    assert run(env, "-j", "verify").returncode == 0
    removed = [line for line in (env["calls"] / "podman").read_text().splitlines() if line.startswith("rm -f")]
    assert removed and all(line.startswith("rm -f act-r") and line.endswith("-CI-verify-of-this-run") for line in removed)
    assert not any("another" in line for line in removed)


def test_each_run_names_its_workflow_copy_so_act_names_its_containers_apart(env):
    """act names a container act-<workflow name>-<job>-<hash of both> (act v0.2.97, createContainerName), so two runs
    of workflows with the same name share container names unless each run gives its copy a name of its own."""
    run(env, "-j", "verify")
    run(env, "-j", "verify")
    copies = [call.split(" -W ", 1)[1].split(" ", 1)[0] for call in act_calls(env)]
    assert len(copies) == 2 and copies[0] != copies[1]
    original = (env["repo"] / ".github" / "workflows" / "ci.yml").read_text()
    for copy in map(pathlib.Path, copies):
        run_id = copy.stem.removeprefix("workflow-")
        assert copy.parent == env["logs"] and run_id.startswith("r")
        assert copy.read_text() == original.replace("name: CI\n", f"name: {run_id}-CI\n", 1)


def test_a_working_tree_with_changes_is_refused_unless_allowed(env):
    (env["repo"] / "README.md").write_text("changed\n")
    result = run(env, "-j", "verify")
    assert result.returncode == 2 and "has changes" in result.stderr
    assert act_calls(env) == []
    assert run(env, "-j", "verify", "-d").returncode == 0


def test_no_arguments_print_the_usage():
    result = subprocess.run(["bash", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 2 and "usage: act-ci.sh" in result.stderr


@pytest.fixture
def project(tmp_path):
    folder = tmp_path / "service"
    folder.mkdir()
    subprocess.run(["git", "-C", str(folder), "init", "-q"], check=True)
    return folder


def setup(*args):
    return subprocess.run(["bash", str(SETUP), *map(str, args)], capture_output=True, text=True)


def test_setup_copies_the_script_and_the_image_into_the_project(project):
    result = setup(project)
    assert result.returncode == 0, result.stderr
    for name in ("act-ci.sh", "Dockerfile.runner"):
        assert (project / "ci" / "local" / name).read_bytes() == (SETUP.parent / name).read_bytes()
    assert os.access(project / "ci" / "local" / "act-ci.sh", os.X_OK)
    assert "act-ci.sh -r <folder>/service -b <base commit>" in result.stdout
    again = setup(project)
    assert again.returncode == 0 and again.stdout.count("same     ci/local/") == 2


def test_setup_keeps_a_project_copy_that_differs_unless_forced(project):
    setup(project)
    copy = project / "ci" / "local" / "act-ci.sh"
    copy.write_text(copy.read_text() + "# a change of the project\n")
    kept = setup(project)
    assert kept.returncode == 1 and "differs  ci/local/act-ci.sh" in kept.stderr
    assert copy.read_text().endswith("# a change of the project\n")
    forced = setup("-f", project)
    assert forced.returncode == 0 and copy.read_bytes() == (SETUP.parent / "act-ci.sh").read_bytes()


def test_setup_refuses_a_folder_that_is_not_a_git_repository(tmp_path):
    result = setup(tmp_path)
    assert result.returncode == 2 and "is not a git repository" in result.stderr
    assert not (tmp_path / "ci").exists()


def test_the_gitleaks_job_runs_natively_when_more_steps_follow_the_scan(env):
    # `yq ... | grep -q` under pipefail: grep exits at the first match, yq gets SIGPIPE on its next line, and the
    # pipeline fails, so the job went to act. More steps after the match make that near certain.
    git = ["git", "-C", str(env["repo"]), "-c", "user.name=t", "-c", "user.email=t@example.test"]
    ci = env["repo"] / ".github" / "workflows" / "ci.yml"
    ci.write_text(ci.read_text() + "".join(f"      - run: echo after {n}\n" for n in range(200)))
    subprocess.run([*git, "commit", "-qam", "more steps"], check=True)
    for _ in range(5):
        result = run(env, "-j", "secret-scan")
        assert result.returncode == 0, result.stdout + result.stderr
        assert act_calls(env) == []


def status_of(env, job):
    lines = [line for line in (env["logs"] / "status.txt").read_text().splitlines() if line.startswith(f"{job} ") and " start " not in line]
    assert len(lines) == 1, lines
    return lines[0]


def test_each_runs_on_label_of_the_workflow_maps_to_the_runner_image(env):
    """cmapi #169: only ubuntu-latest was mapped, so act skipped a job on ubuntu-24.04 and the run still said exit=0."""
    result = run(env)
    assert result.returncode == 0, result.stdout + result.stderr
    for call in act_calls(env):
        assert "-P ubuntu-latest=act-runner:ubuntu-24.04" in call and "-P ubuntu-24.04=act-runner:ubuntu-24.04" in call, call
    assert status_of(env, "contract").startswith("contract exit=0 ")
    assert "Job succeeded" in (env["logs"] / "contract.log").read_text()


def test_a_job_that_act_skips_is_a_failure(env):
    """A label that the script cannot map: an expression. act skips the job and exits 0, and the run must not pass."""
    path = env["repo"] / ".github" / "workflows" / "ci.yml"
    path.write_text(path.read_text().replace("runs-on: ubuntu-24.04", "runs-on: ${{ matrix.os }}"))
    git = ["git", "-C", str(env["repo"]), "-c", "user.name=t", "-c", "user.email=t@example.test"]
    subprocess.run([*git, "commit", "-qam", "an expression as the label"], check=True)
    result = run(env, "-j", "contract verify")
    assert result.returncode != 0
    assert "skipped" in status_of(env, "contract") and "exit=0" not in status_of(env, "contract")
    assert status_of(env, "verify").startswith("verify exit=0 ")


def test_an_act_call_that_exits_0_with_no_job_succeeded_is_a_failure(env):
    env["env"]["ACT_SILENT"] = "1"
    result = run(env, "-j", "verify")
    assert result.returncode != 0
    assert "exit=0" not in status_of(env, "verify") and "no job succeeded" in status_of(env, "verify")
