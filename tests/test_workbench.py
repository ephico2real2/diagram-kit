# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""move.sh moves work folders into the workbench, keeps their worktrees working, and skips a folder in use."""
import os
import pathlib
import shutil
import subprocess
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
MOVE = ROOT / "skill" / "workbench" / "move.sh"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    main = tmp_path / "main"
    main.mkdir()
    git("init", "-q", "-b", "main", cwd=main)
    git("-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "--allow-empty", "-m", "base", cwd=main)
    return main


def move(tmp_path, *folders):
    env = {**os.environ, "WORKBENCH": str(tmp_path / "workbench")}
    return subprocess.run(["bash", str(MOVE), "demo", *map(str, folders)], capture_output=True, text=True, env=env)


def test_the_script_passes_shellcheck():
    if not shutil.which("shellcheck"):
        pytest.skip("this machine has no shellcheck")
    subprocess.run(["shellcheck", str(MOVE)], check=True)


def test_a_moved_worktree_still_works_and_the_main_repository_knows_its_new_path(tmp_path, repo):
    job = tmp_path / "tmp" / "cj-topic"
    job.mkdir(parents=True)
    git("worktree", "add", "-q", "-b", "topic", str(job / "backend"), cwd=repo)

    run = move(tmp_path, job)

    assert run.returncode == 0, run.stderr
    new = tmp_path / "workbench" / "demo" / "cj-topic" / "backend"
    assert not job.exists()
    assert pathlib.Path(git("rev-parse", "--show-toplevel", cwd=new)).resolve() == new.resolve()
    assert str(new.resolve()) in git("worktree", "list", cwd=repo).replace(str(new), str(new.resolve()))
    assert "REPAIRED worktree" in run.stdout


def test_a_plain_clone_moves_and_keeps_its_unpushed_commit(tmp_path, repo):
    clone = tmp_path / "tmp" / "cj-clone"
    git("clone", "-q", str(repo), str(clone), cwd=tmp_path)
    git("-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "--allow-empty", "-m", "unpushed",
        cwd=clone)

    run = move(tmp_path, clone)

    assert run.returncode == 0, run.stderr
    assert git("log", "-1", "--format=%s", cwd=tmp_path / "workbench" / "demo" / "cj-clone") == "unpushed"


def test_an_existing_target_is_not_overwritten(tmp_path):
    src = tmp_path / "tmp" / "cj-same"
    src.mkdir(parents=True)
    (tmp_path / "workbench" / "demo" / "cj-same").mkdir(parents=True)

    run = move(tmp_path, src)

    assert run.returncode == 1
    assert src.exists() and "exists" in run.stderr


def test_a_folder_that_a_process_keeps_open_is_skipped(tmp_path):
    if not shutil.which("lsof"):
        pytest.skip("this machine has no lsof")
    src = tmp_path / "tmp" / "cj-busy"
    src.mkdir(parents=True)
    held = src / "held.log"
    held.write_text("x\n")
    holder = subprocess.Popen(["tail", "-f", str(held)], stdout=subprocess.DEVNULL)
    try:
        time.sleep(0.5)
        run = move(tmp_path, src)
    finally:
        holder.kill()
        holder.wait()

    assert run.returncode == 1
    assert src.exists() and "open in" in run.stderr
