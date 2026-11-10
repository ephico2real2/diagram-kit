---
name: herdr-jobs
description: Each background agent job (Codex, a test run, a local CI run) runs in its own tab of a Herdr session. The person watches every job live, and the caller still gets the exit code at the end of the job. The skill gives herdr_job.py, the start of the session, the call from a job runner, and the fallback with no Herdr server. Use when the user types /herdr-jobs or asks to see the work of the agents in Herdr. Also use it to start a background job that the person wants to watch.
---

# /herdr-jobs: every background job in its own Herdr tab

[Herdr](https://github.com/herdrdev/herdr) (Apache-2.0) is a terminal workspace for coding agents. Its sidebar shows each tab, and each pane shows the live output of its command. A job that a script starts with `codex exec` or `act` in the background is not visible to the person. `herdr_job.py` starts the same job in its own Herdr tab instead. At the end of the job, it writes one status line. Thus the caller still wakes at the end of the job.

Tested with herdr 0.9.5 on macOS (2026-11-10).

## 1. Start the session once

The person starts a named session in a terminal, and keeps it open:

```sh
brew install herdr              # or the binaries of the release page
herdr session attach jobs       # starts the server of the session "jobs", and shows it
```

A named session keeps the jobs apart from the main Herdr session of the person. Agents never start or stop a Herdr server: only a TUI client of the person starts it. Thus the script never controls a session that the person did not start.

## 2. Start a job

```sh
python3 <kit>/skill/herdr-jobs/herdr_job.py --name <job> --cwd <folder> [--env VAR ...] --wait -- <command> <args>
```

- `--name` is the tab label. It starts with a lower-case letter, then lower-case letters, digits, `.`, `_` or `-`, at most 64 characters in all.
- `--env VAR` passes one variable of the current environment to the job. The value goes into a runner file with mode 0600. At the start of the job, that file deletes itself. The value is never in a command line that `ps` shows.
- With `--wait`, the script returns at the end of the job, with the exit code of the job. Run the whole command in the background (for example a Claude Code background shell), and the caller wakes on the end of the job. If the tab is closed or the server stops, the job ends with HUP or TERM, and the status line gets `exit=129` or `exit=143`. A job ended with SIGKILL writes no line, and `--wait` then does not return.
- `--session` (default `jobs`, or `HERDR_JOBS_SESSION`) and `--workspace` (default `jobs`, or `HERDR_JOBS_WORKSPACE`) name where the tab goes. If the workspace does not exist, the script makes it.
- `--status` (default `~/.local/state/herdr-jobs/status.txt`) gets one line for each job: `<name> <run id> exit=<code> <UTC time>`.

If no server runs for the session, the job runs in the foreground of the caller, and it writes the same status line. With `--no-fallback`, the script stops with exit code 3 instead.

## 3. Use it from a job runner

Add the launcher as a separate script beside the runner, and do not edit a runner that a job uses at that time:

```sh
#!/bin/bash
# run-model-herdr.sh: the same arguments as run-model.sh, in a Herdr tab when a server runs.
here=$(cd "$(dirname "$0")" && pwd)
exec python3 <kit>/skill/herdr-jobs/herdr_job.py --name "$1" --cwd "$here" \
  --env CODEX_MODEL --env CODEX_EXTRA --wait -- "$here/run-model.sh" "$@"
```

Name each variable that the runner needs with `--env`. An `--env` for a variable that is not set stops the script before anything runs.

## 4. Look at the jobs

- In the TUI, the workspace `jobs` has one tab for each job. The tab stays open after the job ends, so the person can read its output.
- The tabs are the record of the person. Do not close a tab that you did not make. If the person asks, close a tab of your own. Otherwise keep it.
- `herdr --session jobs pane read <pane id> --source recent-unwrapped --lines 120` reads the output of a job. At the start of the job, the script prints the pane id.

## Anti-patterns

| Do not | Do |
|---|---|
| Start a Herdr server from a script | The person starts the session with `herdr session attach jobs` |
| Put a secret on the command line of the job | Pass it with `--env`, so it stays out of `ps` and the shell history |
| Wait on the pane output with `pane wait-output` | Wait on the status line: output scrolls, the status file stays |
| Edit a runner script while a job uses it | Add a separate launcher script beside it |
