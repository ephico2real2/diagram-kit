---
name: workbench
description: The fixed place for clones, worktrees, agent clones and work files that must outlive a session. The place is $HOME/gitRepos/workbench/<project>/, never /private/tmp, /tmp or a session scratchpad. The skill gives the layout, the names and the files that stay temporary. It moves a folder in safely with move.sh: open files, container mounts and git worktree repair. It also gives the rule to remove a folder. Use when the user types /workbench or its short alias /bench. Before you clone a repository, add a worktree or name a clone path in an agent brief, also use it. If you find a folder of work under /private/tmp, /tmp or a scratchpad, also use it.
---

# /workbench (alias /bench): one fixed place for work that must last

macOS removes old files from `/private/tmp` and `/tmp`, and a restart can empty them. A session scratchpad is also under `/private/tmp`. Thus a clone, a worktree or a report that lives there can disappear, and unpushed commits go with it. On 2026-11-08, 21 unpushed commits of a design and 36 folders of clones and worktrees were only under `/private/tmp`.

## 1. Where things go

```text
$HOME/gitRepos/workbench/                 # WORKBENCH: the root
  <project>/                              # one folder for each project
    cj-<topic>/                           # a clone or a worktree for one job or one topic
    <worktree-name>/                      # a worktree of a real repository
  <tool or kit>/<branch-name>/            # a worktree of a shared repository, such as a kit
```

- The root is `$HOME/gitRepos/workbench`. Set `WORKBENCH` to use another root.
- Use the name of the project folder under `$HOME/gitRepos` as `<project>`.
- Name a clone for an agent or a job `cj-<topic>`, and a worktree for its branch.
- The workbench is not a git repository. Do not commit it, and do not index it as a project.

## 2. What stays temporary

Only a file that you can make again in one step stays in the scratchpad or `/tmp`. Examples are a rendered PNG that is not committed yet, a probe output, or a body file for one `gh` command. These go to the workbench:

- each clone, worktree or export that holds a commit, a patch or a report.
- each folder that an agent brief names as the place of its work.
- each browser profile that holds a sign-in for a capture.

## 3. Start work in the workbench

```sh
W=${WORKBENCH:-$HOME/gitRepos/workbench}/<project>
mkdir -p "$W"
git -C <repository> worktree add -b <branch> "$W/<branch-name>" <base>
git clone -q --no-hardlinks -b <branch> <repository> "$W/cj-<topic>"
```

An agent brief names the workbench path, never a scratchpad path.

## 4. Move a folder in

Use `move.sh` beside this file. It moves each folder to `$WORKBENCH/<project>/`:

```sh
skill/workbench/move.sh <project> /private/tmp/cj-<topic> ...
```

For each folder, the script does these checks, in this order:

1. If the target exists, it skips the folder.
2. If a process keeps a file open in the folder, it skips the folder. `watchman` only watches, so it does not count.
3. If a running Podman or Docker container mounts the folder, it skips the folder.
4. It finds each linked worktree (a `.git` file, not a folder) and the main repository that it names.
5. It moves the folder. On one volume, this is a rename and takes no time.
6. It runs `git worktree repair` for each worktree, and makes sure that `git rev-parse --show-toplevel` gives the new path.

If a worktree is not repaired, the script names the command to run, and exits 1. After the move, update each note, tracker and brief that names the old path:

```sh
grep -rlF '/private/tmp/cj-' <notes> <briefs>
```

A file that a merged commit holds is a record. Do not change it.

## 5. Remove a folder

When its work is merged or pushed, and the owner says yes, you can remove a folder. Before you remove it, make sure that `git status --porcelain` is empty and that `git log @{u}..` shows no commit. A worktree is removed with `git worktree remove`, so that its main repository forgets it.

## Anti-patterns

| Do not | Do |
|---|---|
| Clone into `/private/tmp` or a scratchpad for work that lasts | Clone into `$WORKBENCH/<project>/` |
| Move a worktree with `mv` alone | Use `move.sh`, or move it and run `git worktree repair` |
| Remove a folder with unpushed commits | Push or copy the branch, then remove it with the owner's yes |
| Write a scratchpad path in an agent brief | Write the workbench path |
