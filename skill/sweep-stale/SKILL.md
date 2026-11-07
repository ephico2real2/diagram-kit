---
name: sweep-stale
description: Watch for stale background agents and the processes that a Claude Code session leaves behind, and end them on request. It reports stale Codex brokers, orphaned processes, zombies, leftover socket directories and quiet background jobs. Its prompt hook is silent on a clean machine. Use when the user types /sweep-stale, when a machine is slow or short of memory after agent runs, or when the hook reports a finding.
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

## What it never touches

The guard is applied last and overrides every finding. It protects these processes:

- anything under `/Applications` or `/System`
- editor extension hosts
- CRC and container virtual machines (vfkit, qemu, hyperkit, colima, podman, docker)
- launchd
- the ancestors of the script

## Before you sweep

1. Run the report and read each finding.
2. Ask the user before you run `--sweep`, because it sends KILL to a process that ignores TERM, and it deletes socket directories.
3. Run the report again to make sure that the findings are gone.

A task file can be a link to a transcript in a temporary directory. When that directory is deleted, the link dangles. The script skips a file that is gone, so a link like this cannot stop the hook.

## Platform

The script was written and run on macOS. The task-file search uses `/private/tmp` and `~/.claude/projects`, and the socket search uses `$TMPDIR` and `/var/folders`, so a Linux machine gets a smaller search. The script needs `ps` and `lsof`.
