---
name: local-ci-web
description: Show local CI runs live in a browser. local_ci_web.py finds each running act-ci.sh of /setup-local-ci and reads its status.txt and job logs. It reads the act containers and their logs through the Podman API socket. It serves one page on 127.0.0.1 that refreshes every 3 seconds. Python standard library only. Use when the user types /local-ci-web, or asks to see, watch or open a local CI run or an act job in a browser.
---

# /local-ci-web: watch local CI runs in a browser

`act-ci.sh` of `/setup-local-ci` runs the jobs of a workflow one at a time under act and Podman. It writes a `status.txt`
and one log per job to its log folder. `local_ci_web.py`, beside this file, shows all of that on one page:

- each run, running or ended, with its clone folder, its base commit and its process number.
- the jobs of the run, from `status.txt`, with start and end times (UTC), the result and the note.
- the `act-*` containers of the run (the job container and its services), from the Podman API.
- the log of the job or container that you click. When "follow the running job" is on, the log of the running job.

Measured on 2026-11-13 on macOS with Python 3.15.2, Podman 6.1.2 (a rootless machine, API path `/v5.0.0/libpod`) and
act 0.2.97.

## 1. Set up local CI

The viewer shows the runs of `act-ci.sh`, so local CI must work first. `/setup-local-ci` is the one source of these steps
and of their gotchas. This section gives the order and the short form.

1. If the kit is checked out at `~/gitRepos/diagram-kit`, link both skills once:

   ```sh
   ln -s ~/gitRepos/diagram-kit/skill/setup-local-ci ~/.claude/skills/setup-local-ci
   ln -s ~/gitRepos/diagram-kit/skill/local-ci-web ~/.claude/skills/local-ci-web
   ```

2. Install the tools, and start the Podman machine:

   ```sh
   brew install podman act yq gh shellcheck
   podman machine init      # only once, on a new Mac
   podman machine start
   ```

3. Copy `act-ci.sh` and `Dockerfile.runner` into `ci/local/` of the project. If a copy in the project differs from the
   kit, `setup.sh` keeps it and exits 1:

   ```sh
   ~/.claude/skills/setup-local-ci/setup.sh <project folder>
   ```

4. Connect act to Podman. The permanent link of `/var/run/docker.sock` needs `sudo` and a restart of the machine, so
   do section 2 of `/setup-local-ci` for it. Until then, this line works in the current shell:

   ```sh
   export DOCKER_HOST="unix://$(podman machine inspect --format '{{.ConnectionInfo.PodmanSocket.Path}}')"
   ```

5. Build the runner image in `ci/local/` of the project. On an Intel Mac, use `--platform linux/amd64`:

   ```sh
   podman build --platform linux/arm64 -t act-runner:ubuntu-24.04 -f Dockerfile.runner .
   ```

6. Run the jobs in a clone of the branch with no remote, in a folder with the name of the repository. Give `-o` so that
   each run has its own log folder:

   ```sh
   git clone -q --no-hardlinks -b <branch> <repository> <folder>/<repository name>
   git -C <folder>/<repository name> remote remove origin
   ci/local/act-ci.sh -r <folder>/<repository name> -b <base commit> -o <folder>/act-<run name>
   ```

## 2. Set up the viewer

The script needs no install. It uses only the Python standard library, and `local_ci_web.html` must stay beside it.
Make sure that the Podman machine gives its API socket path:

```sh
podman machine inspect --format '{{.ConnectionInfo.PodmanSocket.Path}}'
```

If the Podman command gives no path, the page still shows the runs and the job logs. It then says
`Podman: no Podman socket` above them. On Linux there is no Podman machine, so give the socket with `--socket`, for
example `/run/user/$(id -u)/podman/podman.sock` after `systemctl --user start podman.socket`. Linux is not measured.

## 3. Start it

Start the server as a background job, so that it outlives the command that starts it:

```sh
python3 ~/.claude/skills/local-ci-web/local_ci_web.py --port 2026
```

Then open `http://127.0.0.1:2026/`. In Claude Code, start it with `run_in_background`, and open the page with Claude in
Chrome or tell the user the address. The server prints one line with the address and the socket it uses.

| Option | Use |
|---|---|
| `--port N` | The loopback port. The default is 2026. If the port is in use, the server stops with `Address already in use`. Then choose another port. Do not stop a server that you did not start |
| `--dir FOLDER` | A log folder to show. If its run ended before the server started, only this option shows it. Give it once for each folder |
| `--socket PATH` | The Podman API socket, instead of the path from `podman machine inspect` |

To stop it, stop the background job, or end the process by its number (`pgrep -f local_ci_web.py`).

## 4. How it finds a run

Every 3 seconds the page asks the server for its state. The server then does these steps:

1. It reads `ps -axo pid=,command=` and keeps each command line that names `act-ci.sh`.
2. It takes `-r` (the clone), `-b` (the base commit) and `-o` (the log folder) from that line. Without `-o`, the log folder
   is `<parent of the clone>/act-logs`, as `act-ci.sh` sets it. A relative path is read from the working folder of that
   process (`lsof -d cwd` on macOS, `/proc/<pid>/cwd` on Linux).
3. It reads `status.txt` of each known log folder. `act-ci.sh` writes `<job> start HH:MM:SS` and
   `<job> exit=N [note] HH:MM:SS` lines there.
4. It lists the containers whose names start with `act-`, and reads each with an inspect call. act sets the working
   folder of the job container and of its service containers to the clone folder, and mounts the workspace there.
   The server puts a container under the run whose clone folder is that working folder or a mount destination.
5. A container that matches no run goes in a separate table, "Act containers with no known run".

A run stays on the page after its process ends, until the server stops. If two runs use one clone folder, the
containers go to the running run, or else to the run with the newest `status.txt`.

## 5. Limits

- The server binds 127.0.0.1 only, and it has no authentication. Do not put it behind a proxy or bind it to another
  address. The logs can hold the output of tests, and the page can read any `act-*` container log.
- It serves a file only from a known log folder, and only a name that matches `^[A-Za-z0-9._-]+\.log$`. It reads a
  container log only for a name that matches `act-[A-Za-z0-9._-]+`. Any other request gets 404.
- A log read shows the last 400 lines on the page. The API takes `tail` up to 2000.
- A run that ended before the server started is shown only with `--dir`.
- The container log comes from Podman. When act removes the container at the end of a job, that log is gone. The job
  log in the log folder stays.
- The page does not stop, start or change a run or a container. It only reads.

## 6. API

| Path | Returns |
|---|---|
| `/` | The page |
| `/api/state` | JSON: `runs` (each with `jobs`, `logs`, `current`, `containers`), `other_containers`, `podman_error`, `now` |
| `/api/log?run=<log folder>&file=<job>.log&tail=N` | The last N lines of a job log |
| `/api/clog?name=<act container>&tail=N` | The last N lines of a container log. Podman sends stdout and stderr in frames with an 8-byte header, and the server joins them |

## 7. Tests

`tests/test_local_ci_web.py` of the kit tests the parsers, the default log folder and relative paths. It also tests the
frame decoder, the container labels, the tie of a container to a run and the log tail. The last tests start the HTTP
server on a free port with no Podman socket. They read the page, the state, a log tail and the refused paths.

```sh
cd ~/gitRepos/diagram-kit && .venv/bin/python -m pytest -q tests/test_local_ci_web.py
```

## Sources

- Podman API reference, container list, inspect and logs: https://docs.podman.io/en/latest/_static/api.html
- The log stream format (8-byte frame header, stream 1 is stdout, stream 2 is stderr):
  https://docs.docker.com/reference/api/engine/version/v1.44/#tag/Container/operation/ContainerAttach
- `podman machine inspect`: https://docs.podman.io/en/latest/markdown/podman-machine-inspect.1.html
