---
name: sweep-stale
description: Watch for stale background agents and the processes that a Claude Code session leaves behind, and end them on request. It reports stale Codex brokers, orphaned processes, zombies, leftover socket directories and quiet background jobs. Its prompt hook is silent on a clean machine. Its --workbench mode reports, and on request removes, the scratch folders and worktrees of pull requests and issues that are merged or closed. Use when the user types /sweep-stale, when a machine is slow or short of memory or disk after agent runs, when the hook reports a finding, or to clean up after a merge.
---

# /sweep-stale: watch for stale background agents

`sweep-stale.py`, beside this file, reports stale background agents and the processes that outlive the work that started them. Only `--sweep` ends them.

The script comes from a measurement on 2026-09-18. That machine had no processes in state Z. The leak was four orphaned Codex plugin broker trees, four processes deep, and two of them were days old.

## Run it

```sh
skill/sweep-stale/sweep-stale.py           # report, as text
skill/sweep-stale/sweep-stale.py --json    # report, as a Claude Code hook payload; prints nothing when clean
skill/sweep-stale/sweep-stale.py --sweep   # end what the report names: TERM, then KILL after 3 seconds
```

## Run it on every prompt

Add this hook to `~/.claude/settings.json`. Replace `<clone>` with the path of your clone. One run took 1.2 seconds on the machine that it was written on, on 2026-11-07.

```json
{"hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "<clone>/skill/sweep-stale/sweep-stale.py --json", "timeout": 10}]}]}}
```

The hook only reports. It never ends a process.

## What it reports

| Finding | The test | `--sweep` |
|---|---|---|
| Zombie process | State Z. The report names the parent. | Not ended. A zombie is already dead, and only its parent can clear it. |
| Stale Codex broker | Nothing outside the broker's own process tree holds its Unix socket, read from `lsof`. Age is reported, but it does not decide. | Ended |
| Orphaned test or browser process | The parent is gone, the command matches headless_shell, Playwright Chromium, uvicorn, pytest or cursor-agent, and it is older than 20 minutes. | Ended |
| Leftover socket directory | A `cxc-*` directory whose broker is gone. | Removed |
| Long-running background job | A live process holds the task's `.output` file, the file has no exit marker, and it is quiet for 30 minutes. | Not ended |
| Ghost background task, in the text report only | No process holds the task's `.output` file, and the file has no exit marker. | Not ended. Foreground tool calls cause false positives. |

## How it sees a background agent

A background agent's task file is a `*.output` link to its `agent-*.jsonl` transcript. Measured on 2026-11-07, no process held either of the 2 such files in the 3-hour window, and neither had an exit marker. One of them was written 1 minute earlier.

So an agent appears as a ghost, in the text report only, whether it is stale or still running. Read the age of each ghost before you act. The prompt hook does not name agents, because it leaves out ghosts. Run the text report to see them. It names the 3 newest ghosts.

## What the guard protects

If the command of a process matches this list, the script does not end that process:

- a command under `/Applications` or `/System`
- editor extension hosts
- the Claude, Cursor and VS Code apps wherever they are installed (`Claude.app`, `Cursor.app`, `Code Helper`)
- CRC and container virtual machines (vfkit, qemu, hyperkit, colima, podman, docker)
- launchd
- the script and its ancestors

The guard reads only the process that a finding names. `--sweep` ends the whole tree of that process, so a child that matches the guard also ends. On 2026-11-07, a sweep ended helpers under `/Applications/ChatGPT.app` because they were children of a stale broker. The ChatGPT app kept running.

## Before you sweep

1. Run the report and read each finding.
2. Ask the user before you run `--sweep`, because it sends KILL to a process that ignores TERM, and it deletes socket directories.
3. Run the report again to make sure that the findings are gone.

A task file can be a link to a transcript in a temporary directory. When that directory is deleted, the link dangles. The script skips a file that is gone, so a link like this cannot stop the hook.

## The workbench: scratch of work that is done

Reviews and fix runs leave folders on disk: a review export (a full copy of the repository for each reviewer), the output folder of an implementer, and a git worktree. On 2026-11-25, these folders used 45 GB in one project's workbench, and the Mac became slow. The `--workbench <dir>` mode reports them. It is a separate report on disk, not on processes. The `/fix-defect` step "Clean up after the merge" uses it.

```sh
skill/sweep-stale/sweep-stale.py --workbench <dir>                        # report only; deletes nothing
skill/sweep-stale/sweep-stale.py --workbench <dir> --repo <owner>/<repo>  # the repository that the numbers belong to
skill/sweep-stale/sweep-stale.py --workbench <dir> --prefix <prefix>      # also read <prefix>-<N>, a project's own name
skill/sweep-stale/sweep-stale.py --workbench <dir> --sweep                # remove what the report marks removable
```

`<dir>` is the scratch root of the project, with one folder for each job, for example `$HOME/gitRepos/workbench/<project>` of `/workbench`. The script refuses a `<dir>` inside a git repository, because there the folders are source and not scratch.

The report has one line for each folder that it can tie to a pull request, an issue or a worktree branch:

| A top-level folder | Tied to | `gh` command |
|---|---|---|
| `review-<N>`, `review_<N>_<reviewer>`, `pr-<N>`, `wt-<N>`, `wt-<N>-outputs`, `issue-<N>`, `fix-<N>`, and `<prefix>-<N>` for each `--prefix <prefix>` | issue or pull request `<N>` | `gh issue view <N> --repo <repo> --json state` |
| a linked git worktree, or a folder that holds one at its top level | the branch of each worktree | `gh pr list --repo <repo> --head <branch> --state all --json number,state` |

Each line gives the verdict, the name, the disk use and the state that GitHub gave. The verdicts are these:

| Verdict | When |
|---|---|
| `removable` | A numbered folder whose pull request is `MERGED` or `CLOSED`, or whose issue is `CLOSED`. A worktree folder only when each branch has a `MERGED` pull request and none is `OPEN`. In both cases, nothing in the next row applies. |
| `keep` | The pull request or issue is `OPEN`, or a branch has no merged pull request. Or a live process holds a file or the working directory in the folder, or `lsof` cannot tell. Or a worktree is locked or has a detached HEAD, or a clone has commits not pushed, a stash or linked worktrees of its own. |
| `unknown` | `gh` failed: it is not installed, it has no network or no login, the number does not exist, or the answer has no known state. Or the script found no repository for the folder. An `unknown` folder is never removed. |

The number in a folder name belongs to the project of the workbench, so `--repo` gives its repository. On 2026-11-25, in a real workbench, 6 numbered folders held clones of a second repository of the project, and each number was an issue of the main repository. Without `--repo`, the `origin` remote of the git checkouts in the folder gives the repository. If the folder has no GitHub remote, as with a review export from `git archive`, or its checkouts name different repositories, the folder is `unknown`.

A worktree branch always belongs to the repository of its own `origin` remote. `--repo` stands in only for a worktree with no GitHub remote.

`gh issue view` also answers for a pull request number. Measured on 2026-11-25 with gh 2.101.0, it gave `MERGED` for a merged pull request. `gh pr view` fails on an issue number, and a project can name a review folder for an issue, for example `review-<N>` for the design review of issue `<N>`. Thus the script asks `gh issue view` for every number.

The report counts the folders that it cannot tie to anything, such as a shared virtual environment or a run record, and keeps them.

### What --sweep does

`--sweep` removes only the folders that the same run marks `removable`. For each folder, in this order:

1. For each git checkout in the folder, it saves the uncommitted change as one patch in `--archive`. The default is `<dir>/worktree-archive-<date>/`. The patch also holds untracked files. It does not hold ignored files, because a build makes them again. The patch starts with the branch and the commit, and `git apply` takes it on that commit.
2. It removes each linked worktree with `git worktree remove --force`, so that the main repository forgets it. The branch and its commits stay in the main repository.
3. It removes the folder, and prints the disk use that it freed, as `du` counts it. A file that is also hard-linked from outside the folder stays on disk.

If git cannot make the patch, or `git worktree remove` fails, the folder stays, and the script exits 1. A locked worktree stays, because `git worktree remove` needs `--force` two times for it, and the lock has a reason.

### Before you sweep the workbench

1. Run the report and read each line.
2. Make sure that no running agent's brief names a path that the report marks `removable`. The script sees open files and working directories. It cannot see a path that a brief names for later use.
3. Run `--sweep`, then run the report again.

## Platform

The script was written and run on macOS. The task-file search uses `/private/tmp` and `~/.claude/projects`, and the socket search uses `$TMPDIR` and `/var/folders`, so a Linux machine gets a smaller search. The script needs `ps` and `lsof`. The `--workbench` mode also needs `git` and `gh`, and without `lsof` it marks no folder removable.
