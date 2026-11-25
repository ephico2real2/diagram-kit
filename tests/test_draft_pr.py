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


def run(clone, folder, env, **extra):
    return subprocess.run(["zsh", SCRIPT, clone, "owner/repo", "work/fix", "main", folder, "fix: sum"],
                          capture_output=True, text=True, env={**env, "DRY_RUN": "1", **extra})


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


def test_draft_body_counts_kotlin_and_swift_tests(job):
    clone, folder, env = job
    git(clone, "reset", "-q", "--hard", "main", env=env)
    for path in ["shared/src/commonTest/kotlin/a/CopyTest.kt", "shared/src/androidHostTest/kotlin/a/Big.kt",
                 "iosApp/AppTests/ModelTests.swift", "app/src/main/kotlin/a/Copy.kt"]:
        (clone / path).parent.mkdir(parents=True, exist_ok=True)
        (clone / path).write_text("// x\n")
    git(clone, "add", "-A", env=env)
    git(clone, "commit", "-q", "-m", "D1: Kotlin code with its tests", env=env)
    result = run(clone, folder, env)
    assert result.returncode == 0, result.stderr
    assert "3 test files changed." in (folder / "draft-pr.md").read_text()


def test_draft_tally_counts_one_verdict_per_row(job):
    clone, folder, env = job
    (folder / "verdicts.md").write_text(
        "| ID | Verdict | Reason |\n|---|---|---|\n"
        "| C1 | CONFIRMED | MEASURED, not REFUTED by the rerun |\n"
        "| H3 | CONFIRMED on the host; NOT REACHED on Android | |\n"
        "| C3 | NOT REACHED | |\n\nTally: 2 CONFIRMED, 1 NOT REACHED.\n")
    result = run(clone, folder, env)
    assert result.returncode == 0, result.stderr
    assert "Verdicts: 2 CONFIRMED, 1 NOT REACHED." in (folder / "draft-pr.md").read_text()


def test_draft_body_opens_with_the_parent_issue(job):
    clone, folder, env = job
    result = run(clone, folder, env, PART_OF="#307")
    assert result.returncode == 0, result.stderr
    assert (folder / "draft-pr.md").read_text().startswith("Part of #307.\n\nDraft from the agent job")
    assert run(clone, folder, env, PART_OF="owner/repo#9").returncode == 0
    assert (folder / "draft-pr.md").read_text().startswith("Part of owner/repo#9.")


def test_draft_refuses_a_parent_that_is_not_an_issue_reference(job):
    clone, folder, env = job
    (clone / "left.ts").write_text("export {};\n")
    result = run(clone, folder, env, PART_OF="307; rm -rf x")
    assert result.returncode == 1 and "PART_OF must be" in result.stderr
    assert not (folder / "draft-pr.md").exists()
    assert git(clone, "status", "--porcelain", env=env) == "?? left.ts\n"


def test_draft_counts_from_the_remote_base_when_the_local_base_is_behind(job):
    clone, folder, env = job
    # The base moved on the remote (a squash merge) and the work was rebuilt on it, but the local base stayed behind.
    git(clone, "switch", "-q", "--detach", "main", env=env)
    (clone / "merged.md").write_text("merged on the remote\n")
    git(clone, "add", "-A", env=env)
    git(clone, "commit", "-q", "-m", "squash merge on the remote", env=env)
    merged = git(clone, "rev-parse", "HEAD", env=env).strip()
    git(clone, "update-ref", "refs/remotes/origin/main", merged, env=env)
    git(clone, "switch", "-q", "-C", "work/fix", merged, env=env)
    (clone / "fix.ts").write_text("export const fix = 1;\n")
    git(clone, "add", "-A", env=env)
    git(clone, "commit", "-q", "-m", "D2: the fix", env=env)
    result = run(clone, folder, env)
    assert result.returncode == 0, result.stderr
    assert "DRY RUN: 1 new commits" in result.stdout
    assert "squash merge on the remote" not in result.stdout
    assert git(clone, "merge-base", "--is-ancestor", merged, "HEAD", env=env) == ""


def test_draft_refuses_a_branch_with_no_new_commit(job):
    clone, folder, env = job
    git(clone, "reset", "-q", "--hard", "main", env=env)
    result = run(clone, folder, env)
    assert result.returncode == 1 and "no new commit" in result.stderr


def test_draft_refuses_missing_arguments():
    result = subprocess.run(["zsh", SCRIPT, "a"], capture_output=True, text=True)
    assert result.returncode == 2 and "usage" in result.stderr


def test_draft_keeps_an_empty_commit_and_gives_it_the_owner_authorship(job):
    # An agent can record a step with "git commit --allow-empty" when its report stays outside the repository.
    # On 2026-11-12 two such commits stopped the author rewrite: "commit --amend" refuses an empty commit.
    clone, folder, env = job
    git(clone, "commit", "-q", "--allow-empty", "-m", "D2: record research outside the repository", env=env)
    result = run(clone, folder, env)
    assert result.returncode == 0, result.stderr
    subjects = git(clone, "log", "--format=%s", "main..HEAD", env=env).splitlines()
    assert subjects == ["D2: record research outside the repository", "D1: add sum with its test"]
    authors = set(git(clone, "log", "--format=%an <%ae>", "main..HEAD", env=env).splitlines())
    assert authors == {"Owner Person <owner@example.com>"}


def test_draft_refuses_a_commit_with_a_session_trailer(job):
    clone, folder, env = job
    (clone / "src" / "more.ts").write_text("export const more = 2;\n")
    git(clone, "add", "-A", env=env)
    git(clone, "commit", "-q", "-m", "D2: more\n\nClaude-Session: https://claude.ai/code/session_x", env=env)
    result = run(clone, folder, env)
    assert result.returncode == 1 and "Claude-Session" in result.stderr
    assert "D2: more" in git(clone, "log", "-1", "--format=%s", env=env)


def test_draft_keeps_the_shas_when_every_commit_has_the_owner_identity(job):
    clone, folder, env = job
    # On 2026-11-18 the rewrite gave tested commits new SHAs although their author was already the owner.
    git(clone, "reset", "-q", "--hard", "main", env=env)
    (clone / "src").mkdir()
    (clone / "src" / "one.ts").write_text("export const one = 1;\n")
    git(clone, "add", "-A", env=env)
    git(clone, "-c", "user.name=Owner Person", "-c", "user.email=owner@example.com", "commit", "-q", "-m", "D1: one",
        env=env)
    before = git(clone, "rev-parse", "HEAD", env=env)
    result = run(clone, folder, env)
    assert result.returncode == 0, result.stderr
    assert git(clone, "rev-parse", "HEAD", env=env) == before
    assert not (folder / "draft-sha-map.txt").exists()
    assert "no rewrite" in result.stdout


def test_draft_rewrites_when_one_commit_has_another_committer(job):
    clone, folder, env = job
    git(clone, "reset", "-q", "--hard", "main", env=env)
    (clone / "src").mkdir()
    (clone / "src" / "one.ts").write_text("export const one = 1;\n")
    git(clone, "add", "-A", env=env)
    # The author is the owner, but the clone's own identity (codex) commits it.
    git(clone, "commit", "-q", "--author=Owner Person <owner@example.com>", "-m", "D1: one", env=env)
    before = git(clone, "rev-parse", "HEAD", env=env)
    result = run(clone, folder, env)
    assert result.returncode == 0, result.stderr
    assert git(clone, "rev-parse", "HEAD", env=env) != before
    committers = set(git(clone, "log", "--format=%cn <%ce>", "main..HEAD", env=env).splitlines())
    assert committers == {"Owner Person <owner@example.com>"}
    assert len((folder / "draft-sha-map.txt").read_text().splitlines()) == 1
