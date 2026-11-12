# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""draft_pr.sh keeps the work of an agent job: it commits what the job left, gives the owner the authorship, and
writes a draft body that states the commits, the test count and the report files. DRY_RUN makes no push and no gh call."""
import os
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skill" / "agent-report" / "scripts" / "draft_pr.sh"
pytestmark = pytest.mark.skipif(shutil.which("zsh") is None, reason="draft_pr.sh is a zsh script")


def git(repo, *args, env=None):
    return subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True, text=True, env=env).stdout


@pytest.fixture
def job(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    (home / ".gitconfig").write_text("[user]\n\tname = Owner Person\n\temail = owner@example.com\n")
    env = {**os.environ, "HOME": str(home), "GIT_CONFIG_NOSYSTEM": "1"}
    clone = tmp_path / "clone"
    clone.mkdir()
    git(clone, "init", "-q", "-b", "main", env=env)
    git(clone, "config", "user.name", "codex", env=env)
    git(clone, "config", "user.email", "codex@example.invalid", env=env)
    (clone / "README.md").write_text("base\n")
    git(clone, "add", "-A", env=env)
    git(clone, "commit", "-q", "-m", "base", env=env)
    git(clone, "switch", "-q", "-c", "work/fix", env=env)
    (clone / "src").mkdir()
    (clone / "src" / "sum.ts").write_text("export const sum = (a: number, b: number) => a + b;\n")
    (clone / "src" / "sum.spec.ts").write_text("test('sum', () => expect(1 + 1).toBe(2));\n")
    git(clone, "add", "-A", env=env)
    git(clone, "commit", "-q", "-m", "D1: add sum with its test", env=env)
    folder = tmp_path / "jobs" / "demo-r1"
    folder.mkdir(parents=True)
    (folder / "verdicts.md").write_text("| D1 | CONFIRMED |\n| Q2 | REFUTED |\n| Q3 | NOT REACHED |\n")
    return clone, folder, env


def run(clone, folder, env):
    return subprocess.run(["zsh", SCRIPT, clone, "owner/repo", "work/fix", "main", folder, "fix: sum"],
                          capture_output=True, text=True, env={**env, "DRY_RUN": "1"})


def test_draft_commits_leftovers_and_gives_the_owner_the_authorship(job):
    clone, folder, env = job
    (clone / "src" / "left.ts").write_text("export const left = 1;\n")
    result = run(clone, folder, env)
    assert result.returncode == 0, result.stderr
    assert git(clone, "status", "--porcelain", env=env) == ""
    subjects = git(clone, "log", "--format=%s", "main..HEAD", env=env).splitlines()
    assert subjects == ["WIP demo-r1: the uncommitted work of the agent job", "D1: add sum with its test"]
    authors = set(git(clone, "log", "--format=%an <%ae>", "main..HEAD", env=env).splitlines())
    assert authors == {"Owner Person <owner@example.com>"}
    assert len((folder / "draft-sha-map.txt").read_text().splitlines()) == 2


def test_draft_body_states_commits_tests_and_verdicts(job):
    clone, folder, env = job
    result = run(clone, folder, env)
    assert result.returncode == 0, result.stderr
    body = (folder / "draft-pr.md").read_text()
    assert "D1: add sum with its test" in body
    assert "1 test files changed." in body
    assert "1 CONFIRMED, 1 NOT REACHED, 1 REFUTED" in body
    assert "Report files in the repository" not in body


def test_draft_body_flags_no_tests_and_report_files_in_the_repository(job):
    clone, folder, env = job
    git(clone, "reset", "-q", "--hard", "main", env=env)
    (clone / "tests.md").write_text("report\n")
    (clone / "app.ts").write_text("export {};\n")
    git(clone, "add", "-A", env=env)
    git(clone, "commit", "-q", "-m", "D1: code with no test", env=env)
    result = run(clone, folder, env)
    assert result.returncode == 0, result.stderr
    body = (folder / "draft-pr.md").read_text()
    assert "No test file changed." in body
    assert "Report files in the repository (move them out before ready): tests.md" in body


def test_draft_refuses_a_branch_with_no_new_commit(job):
    clone, folder, env = job
    git(clone, "reset", "-q", "--hard", "main", env=env)
    result = run(clone, folder, env)
    assert result.returncode == 1 and "no new commit" in result.stderr


def test_draft_refuses_missing_arguments():
    result = subprocess.run(["zsh", SCRIPT, "a"], capture_output=True, text=True)
    assert result.returncode == 2 and "usage" in result.stderr
