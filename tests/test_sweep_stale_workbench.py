# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The --workbench mode removes only the scratch of a pull request or issue that is done, and keeps the rest.

A stub `gh` on PATH answers from a table, so no test reaches GitHub. The folders and git repositories are real, in a
temporary directory. A folder is removable only when GitHub says MERGED or CLOSED; a `gh` that fails, or is absent,
leaves the folder unknown and in place. A worktree's uncommitted change is saved as a patch before it is removed."""

from __future__ import annotations

import glob
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import textwrap
import time

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "skill" / "sweep-stale" / "sweep-stale.py"
REMOTE = "git@github.com:acme/widgets.git"
REPO = "github.com/acme/widgets"


@pytest.fixture
def sweep(monkeypatch):
    spec = importlib.util.spec_from_file_location("sweep_stale_workbench", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "open_paths"):
        monkeypatch.setattr(module, "open_paths", list)            # no live process holds a test folder
    return module


@pytest.fixture
def gh(tmp_path, monkeypatch):
    """A stub gh on PATH. `gh.answer(key, value)` sets what it prints; every call is logged as JSON."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    table, log = tmp_path / "gh-answers.json", tmp_path / "gh-calls.jsonl"
    table.write_text("{}")
    stub = bin_dir / "gh"
    stub.write_text(textwrap.dedent(f"""\
        #!{sys.executable}
        import json, sys
        args = sys.argv[1:]
        with open({str(log)!r}, "a") as f:
            f.write(json.dumps(args) + "\\n")
        table = json.load(open({str(table)!r}))
        if args[:2] == ["pr", "list"]:
            key = "pr list " + args[args.index("--head") + 1]
        else:
            key = " ".join(args[:3])
        answer = table.get(key, "missing")
        if answer == "fail":
            sys.stderr.write("HTTP 401: Bad credentials (https://api.github.com/graphql)\\n")
            sys.exit(1)
        if answer == "missing":
            sys.stderr.write("GraphQL: Could not resolve to a PullRequest with the number of 0.\\n")
            sys.exit(1)
        print(json.dumps(answer))
        """))
    stub.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")

    class Stub:
        def answer(self, key, value):
            data = json.loads(table.read_text())
            data[key] = value
            table.write_text(json.dumps(data))

        def calls(self):
            return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []

    return Stub()


def git(*args, cwd) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
    return subprocess.run(["git", *args], cwd=cwd, env=env, check=True, capture_output=True, text=True).stdout


@pytest.fixture
def source(tmp_path) -> pathlib.Path:
    """A repository whose origin names acme/widgets on GitHub. Nothing is ever fetched from it."""
    repo = tmp_path / "src" / "widgets"
    repo.mkdir(parents=True)
    git("init", "-q", "-b", "main", cwd=repo)
    (repo / "app.txt").write_text("one\n")
    git("add", "app.txt", cwd=repo)
    git("commit", "-q", "-m", "first", cwd=repo)
    git("remote", "add", "origin", REMOTE, cwd=repo)
    return repo


def folder(root: pathlib.Path, name: str, size: int = 4096) -> pathlib.Path:
    path = root / name
    path.mkdir(parents=True)
    (path / "data.bin").write_bytes(b"x" * size)
    return path


def run(sweep, monkeypatch, capsys, *args) -> tuple[int, str]:
    monkeypatch.setattr(sys, "argv", ["sweep-stale.py", *args])
    code = sweep.main()
    return code, capsys.readouterr().out


def line_for(out: str, name: str) -> str:
    """The report line of one folder: its verdict, its name, its size and its detail."""
    lines = [line for line in out.splitlines() if line.split()[:1] in (["removable"], ["keep"], ["unknown"])
             and line.split()[1] == name]
    assert len(lines) == 1, f"{name}: {lines!r} in\n{out}"
    return lines[0]


@pytest.fixture
def bench(tmp_path, gh) -> pathlib.Path:
    """Merged and closed pull requests, a closed and an open issue, and a folder tied to nothing."""
    root = tmp_path / "workbench"
    for name in ("review-11", "review_12_codex", "wt-13-outputs", "wt-14-outputs", "shared-venv"):
        folder(root, name)
    gh.answer("issue view 11", {"state": "MERGED"})
    gh.answer("issue view 12", {"state": "CLOSED"})
    gh.answer("issue view 13", {"state": "CLOSED"})
    gh.answer("issue view 14", {"state": "OPEN"})
    return root


def test_the_report_marks_merged_and_closed_removable_and_deletes_nothing(sweep, monkeypatch, capsys, bench, gh):
    code, out = run(sweep, monkeypatch, capsys, "--workbench", str(bench), "--repo", "acme/widgets")
    assert code == 0
    for name, state in (("review-11", "MERGED"), ("review_12_codex", "CLOSED"), ("wt-13-outputs", "CLOSED")):
        assert line_for(out, name).startswith("removable") and state in line_for(out, name)
    assert line_for(out, "wt-14-outputs").startswith("keep") and "OPEN" in line_for(out, "wt-14-outputs")
    assert "shared-venv" not in out and "1 other folder" in out
    assert sorted(p.name for p in bench.iterdir()) == ["review-11", "review_12_codex", "shared-venv", "wt-13-outputs",
                                                       "wt-14-outputs"]
    calls = gh.calls()
    assert len(calls) == 4 and all(c[c.index("--repo") + 1] == "acme/widgets" for c in calls)
    assert sorted(c[2] for c in calls) == ["11", "12", "13", "14"] and {tuple(c[:2]) for c in calls} == {("issue", "view")}


def test_sweep_removes_only_what_the_report_marked_and_prints_what_it_freed(sweep, monkeypatch, capsys, bench):
    code, out = run(sweep, monkeypatch, capsys, "--workbench", str(bench), "--repo", "acme/widgets", "--sweep")
    assert code == 0
    assert sorted(p.name for p in bench.iterdir()) == ["shared-venv", "wt-14-outputs"]
    assert "removed 3 folder(s)" in out and "freed" in out


@pytest.mark.parametrize("answer", ["fail", "missing", {"state": "SOMETHING"}, {"number": 15}])
def test_a_gh_failure_is_unknown_and_never_removed(sweep, monkeypatch, capsys, tmp_path, gh, answer):
    root = tmp_path / "workbench"
    folder(root, "review-15")
    gh.answer("issue view 15", answer)
    code, out = run(sweep, monkeypatch, capsys, "--workbench", str(root), "--repo", "acme/widgets", "--sweep")
    assert code == 0
    assert line_for(out, "review-15").startswith("unknown")
    assert (root / "review-15").is_dir()


def test_no_gh_on_the_path_is_unknown_and_never_removed(sweep, monkeypatch, capsys, tmp_path):
    root = tmp_path / "workbench"
    folder(root, "review-16")
    only_git = tmp_path / "only-git"
    only_git.mkdir()
    (only_git / "git").symlink_to(shutil.which("git"))
    monkeypatch.setenv("PATH", str(only_git))
    code, out = run(sweep, monkeypatch, capsys, "--workbench", str(root), "--repo", "acme/widgets", "--sweep")
    assert code == 0
    assert line_for(out, "review-16").startswith("unknown") and (root / "review-16").is_dir()


def test_a_folder_with_no_repository_is_unknown(sweep, monkeypatch, capsys, tmp_path, gh):
    root = tmp_path / "workbench"
    folder(root, "review-17")
    code, out = run(sweep, monkeypatch, capsys, "--workbench", str(root), "--sweep")
    assert line_for(out, "review-17").startswith("unknown") and "--repo" in line_for(out, "review-17")
    assert (root / "review-17").is_dir() and gh.calls() == []


def test_a_worktree_change_is_archived_before_the_worktree_is_removed(sweep, monkeypatch, capsys, tmp_path, gh, source):
    root = tmp_path / "workbench"
    root.mkdir()
    tree = root / "wt-21"
    git("worktree", "add", "-q", "-b", "fix/21", str(tree), cwd=source)
    (tree / "app.txt").write_text("one\ntwo\n")                     # a tracked change
    (tree / "new.txt").write_text("not added yet\n")                 # an untracked file
    gh.answer("issue view 21", {"state": "CLOSED"})

    code, out = run(sweep, monkeypatch, capsys, "--workbench", str(root), "--sweep")
    assert code == 0, out
    assert not tree.exists()
    assert str(tree) not in git("worktree", "list", "--porcelain", cwd=source)
    assert "fix/21" in git("branch", "--list", "fix/21", cwd=source)    # the branch and its commits stay
    patches = glob.glob(str(root / "worktree-archive-*" / "wt-21*.patch"))
    assert len(patches) == 1, out
    patch = pathlib.Path(patches[0]).read_text()
    assert "+two" in patch and "+not added yet" in patch
    git("apply", "--check", patches[0], cwd=source)                  # the saved change applies to its base
    assert patches[0] in out
    assert gh.calls()[0][gh.calls()[0].index("--repo") + 1] == REPO   # read from the worktree's remote


def test_the_report_alone_does_not_archive_or_remove_a_worktree(sweep, monkeypatch, capsys, tmp_path, gh, source):
    root = tmp_path / "workbench"
    root.mkdir()
    tree = root / "wt-22"
    git("worktree", "add", "-q", "-b", "fix/22", str(tree), cwd=source)
    (tree / "app.txt").write_text("changed\n")
    gh.answer("issue view 22", {"state": "CLOSED"})
    code, out = run(sweep, monkeypatch, capsys, "--workbench", str(root))
    assert line_for(out, "wt-22").startswith("removable")
    assert tree.is_dir() and (tree / "app.txt").read_text() == "changed\n"
    assert glob.glob(str(root / "worktree-archive-*")) == []


def test_the_repo_argument_owns_the_number_and_the_folder_remote_stands_in_for_it(sweep, monkeypatch, capsys, tmp_path,
                                                                                  gh, source):
    """The shape measured on 2026-11-25: a numbered folder held a clone of a second repository; the number was the project's."""
    root = tmp_path / "workbench"
    root.mkdir()
    git("worktree", "add", "-q", "-b", "fix/23", str(root / "wt-23" / "widgets"), cwd=source)
    gh.answer("issue view 23", {"state": "OPEN"})
    run(sweep, monkeypatch, capsys, "--workbench", str(root), "--repo", "acme/project")
    run(sweep, monkeypatch, capsys, "--workbench", str(root))
    assert [c[c.index("--repo") + 1] for c in gh.calls()] == ["acme/project", REPO]


def test_a_review_folder_named_for_an_issue_is_read(sweep, monkeypatch, capsys, tmp_path, gh):
    root = tmp_path / "workbench"
    folder(root, "review-28-fable")
    gh.answer("issue view 28", {"state": "OPEN"})
    _, out = run(sweep, monkeypatch, capsys, "--workbench", str(root), "--repo", "acme/widgets")
    assert line_for(out, "review-28-fable").startswith("keep") and "#28 OPEN" in out


def test_a_worktree_whose_branch_merged_is_removable(sweep, monkeypatch, capsys, tmp_path, gh, source):
    root = tmp_path / "workbench"
    root.mkdir()
    for name, branch in (("feature-w", "feature/w"), ("feature-x", "feature/x"), ("feature-y", "feature/y"),
                         ("feature-z", "feature/z")):
        git("worktree", "add", "-q", "-b", branch, str(root / name), cwd=source)
    gh.answer("pr list feature/w", [{"number": 29, "state": "CLOSED"}])         # closed without a merge
    gh.answer("pr list feature/x", [{"number": 30, "state": "MERGED"}])
    gh.answer("pr list feature/y", [{"number": 31, "state": "CLOSED"}, {"number": 32, "state": "OPEN"}])
    gh.answer("pr list feature/z", [])
    code, out = run(sweep, monkeypatch, capsys, "--workbench", str(root), "--sweep")
    assert line_for(out, "feature-x").startswith("removable") and "#30 MERGED" in line_for(out, "feature-x")
    assert line_for(out, "feature-y").startswith("keep") and "#32 OPEN" in line_for(out, "feature-y")
    assert line_for(out, "feature-z").startswith("keep")
    assert line_for(out, "feature-w").startswith("keep") and "#29 CLOSED" in line_for(out, "feature-w")
    left = sorted(p.name for p in root.iterdir() if not p.name.startswith("worktree-archive"))
    assert left == ["feature-w", "feature-y", "feature-z"]
    listed = git("worktree", "list", "--porcelain", cwd=source)
    assert str(root / "feature-x") not in listed and str(root / "feature-y") in listed


def test_a_locked_worktree_is_kept(sweep, monkeypatch, capsys, tmp_path, gh, source):
    root = tmp_path / "workbench"
    root.mkdir()
    git("worktree", "add", "-q", "-b", "fix/24", str(root / "wt-24"), cwd=source)
    git("worktree", "lock", "--reason", "on a removable drive", str(root / "wt-24"), cwd=source)
    gh.answer("issue view 24", {"state": "CLOSED"})
    _, out = run(sweep, monkeypatch, capsys, "--workbench", str(root), "--sweep")
    assert line_for(out, "wt-24").startswith("keep") and "locked" in line_for(out, "wt-24")
    assert (root / "wt-24").is_dir()


def test_a_clone_with_unpushed_commits_is_kept(sweep, monkeypatch, capsys, tmp_path, gh, source):
    root = tmp_path / "workbench"
    root.mkdir()
    clone = root / "wt-25"
    git("clone", "-q", str(source), str(clone), cwd=tmp_path)
    git("remote", "set-url", "origin", REMOTE, cwd=clone)
    (clone / "app.txt").write_text("local only\n")
    git("commit", "-q", "-am", "not pushed", cwd=clone)
    gh.answer("issue view 25", {"state": "CLOSED"})
    _, out = run(sweep, monkeypatch, capsys, "--workbench", str(root), "--sweep")
    assert line_for(out, "wt-25").startswith("keep") and "not pushed" in line_for(out, "wt-25")
    assert clone.is_dir()


def test_a_clone_that_other_worktrees_use_is_kept(sweep, monkeypatch, capsys, tmp_path, gh, source):
    root = tmp_path / "workbench"
    root.mkdir()
    clone = root / "wt-27"
    git("clone", "-q", str(source), str(clone), cwd=tmp_path)
    git("remote", "set-url", "origin", REMOTE, cwd=clone)
    git("worktree", "add", "-q", "-b", "side", str(tmp_path / "elsewhere"), cwd=clone)
    gh.answer("issue view 27", {"state": "CLOSED"})
    _, out = run(sweep, monkeypatch, capsys, "--workbench", str(root), "--sweep")
    assert line_for(out, "wt-27").startswith("keep") and "linked worktrees" in line_for(out, "wt-27")
    assert clone.is_dir()


def test_a_clone_not_tied_to_a_number_is_not_judged(sweep, monkeypatch, capsys, tmp_path, gh, source):
    root = tmp_path / "workbench"
    root.mkdir()
    git("clone", "-q", str(source), str(root / "cj-topic"), cwd=tmp_path)
    _, out = run(sweep, monkeypatch, capsys, "--workbench", str(root), "--sweep")
    assert "cj-topic" not in out and "1 other folder" in out and gh.calls() == []
    assert (root / "cj-topic").is_dir()


def test_a_project_prefix_is_read_only_when_it_is_named(sweep, monkeypatch, capsys, tmp_path, gh):
    root = tmp_path / "workbench"
    for name in ("fix-40", "ccfg-41"):
        folder(root, name)
    gh.answer("issue view 40", {"state": "CLOSED"})
    gh.answer("issue view 41", {"state": "CLOSED"})
    _, out = run(sweep, monkeypatch, capsys, "--workbench", str(root), "--repo", "acme/widgets")
    assert line_for(out, "fix-40").startswith("removable") and "ccfg-41" not in out
    _, out = run(sweep, monkeypatch, capsys, "--workbench", str(root), "--repo", "acme/widgets", "--prefix", "ccfg")
    assert line_for(out, "ccfg-41").startswith("removable")
    code, out = run(sweep, monkeypatch, capsys, "--workbench", str(root), "--prefix", "a|b")
    assert code == 2 and (root / "fix-40").is_dir()


def test_a_folder_a_live_process_holds_is_kept(sweep, monkeypatch, capsys, bench):
    held = str((bench / "review-11").resolve() / "data.bin")
    monkeypatch.setattr(sweep, "open_paths", lambda: [held])
    _, out = run(sweep, monkeypatch, capsys, "--workbench", str(bench), "--repo", "acme/widgets", "--sweep")
    assert line_for(out, "review-11").startswith("keep") and "in use" in line_for(out, "review-11")
    assert (bench / "review-11").is_dir() and not (bench / "wt-13-outputs").exists()


def test_when_lsof_cannot_tell_nothing_is_removable(sweep, monkeypatch, capsys, bench):
    monkeypatch.setattr(sweep, "open_paths", lambda: None)
    _, out = run(sweep, monkeypatch, capsys, "--workbench", str(bench), "--repo", "acme/widgets", "--sweep")
    assert sorted(p.name for p in bench.iterdir()) == ["review-11", "review_12_codex", "shared-venv", "wt-13-outputs",
                                                       "wt-14-outputs"]
    assert "lsof" in out


@pytest.mark.skipif(shutil.which("lsof") is None, reason="needs lsof")
def test_lsof_sees_a_process_whose_working_directory_is_in_the_folder(monkeypatch, capsys, bench):
    """The real lsof, not the fixture's stand-in: a process whose cwd is inside a folder keeps it."""
    spec = importlib.util.spec_from_file_location("sweep_stale_real_lsof", SCRIPT)
    real = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(real)
    sleeper = subprocess.Popen(["sleep", "60"], cwd=bench / "review-11")
    try:
        time.sleep(0.2)
        _, out = run(real, monkeypatch, capsys, "--workbench", str(bench), "--repo", "acme/widgets")
    finally:
        sleeper.kill()
        sleeper.wait()
    assert line_for(out, "review-11").startswith("keep") and "in use" in line_for(out, "review-11")


def test_a_directory_inside_a_git_repository_is_refused(sweep, monkeypatch, capsys, source, gh):
    folder(source, "review-26")
    gh.answer("issue view 26", {"state": "MERGED"})
    code, out = run(sweep, monkeypatch, capsys, "--workbench", str(source), "--repo", "acme/widgets", "--sweep")
    assert code == 2 and "git" in out
    assert (source / "review-26").is_dir() and gh.calls() == []


def test_the_process_report_is_unchanged_without_the_workbench_flag(sweep, monkeypatch, capsys):
    monkeypatch.setattr(sweep, "snapshot", dict)
    monkeypatch.setattr(sweep, "task_files", list)
    monkeypatch.setattr(glob, "glob", lambda pattern: [])
    code, out = run(sweep, monkeypatch, capsys)
    assert code == 0 and out.startswith("nothing stale")


def test_the_skill_documents_the_workbench_mode():
    skill = SCRIPT.with_name("SKILL.md").read_text()
    for words in ("--workbench <dir>", "--repo", "unknown", "--sweep", "worktree-archive-"):
        assert words in skill, words
