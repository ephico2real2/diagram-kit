---
name: setup-local-ci
description: Set up and run local CI for a project. It copies act-ci.sh and a pinned runner image into ci/local of the project. Then it runs the jobs of a GitHub Actions workflow on a Mac with act and Podman, with no Docker Desktop. act-ci.sh runs each job and each matrix entry alone, cleans up after a failure, and runs a gitleaks job natively. The skill lists the measured gotchas with their exact errors. Use when the user types /setup-local-ci, /act or /local-ci, or asks to run CI locally or with act. Also use it for CI that GitHub cannot run, for example during a billing block, and for an act run that fails under Podman.
---

# /setup-local-ci: run GitHub Actions jobs locally with act and Podman

act (https://github.com/nektos/act) runs the jobs of a workflow in containers on your computer. This skill runs them under Podman on macOS. Docker Desktop is not necessary. `act-ci.sh`, `Dockerfile.runner` and `setup.sh` are beside this file. `/act` and `/local-ci` are aliases of this skill.

## Set up a project

`setup.sh` copies `act-ci.sh` and `Dockerfile.runner` into `ci/local/` of a project, and prints the next steps:

```sh
~/.claude/skills/setup-local-ci/setup.sh <project folder>
```

If a copy in the project differs from the kit, `setup.sh` keeps it and exits 1. Compare the two files, and pass `-f` only to replace the project copy. Commit `ci/local/` in the project, and add a short section to its README that points to this skill. Then do sections 1 to 4 below.

Measured on 2026-11-08 with act 0.2.97, Podman 6.1.2 (a rootless machine on Apple silicon) and yq 4.53.6.

If GitHub cannot run the jobs, for example during a billing block, use a local run. A local run also finds a CI failure before a push. A local run is not a GitHub run. Section 6 gives the differences. If a local run is the merge gate of a pull request, say so in the pull request. Give the commit and the result of each job.

## 1. Install the tools with Homebrew

```sh
brew install podman act yq gh shellcheck
```

| Tool | Use |
| --- | --- |
| `podman` | The container engine |
| `act` | Runs the jobs of a workflow in containers |
| `yq` | `act-ci.sh` reads the jobs and the matrix entries of the workflow with it. No Python package is necessary |
| `gh` | Gives the token for the actions, and downloads the gitleaks release |
| `shellcheck` | Lints `act-ci.sh` after each change |

## 2. Connect act to Podman

act uses the Docker API at `/var/run/docker.sock`, or at `DOCKER_HOST`. On macOS, the Podman helper makes `/var/run/docker.sock` a link to the socket of the Podman machine. A move to a new Mac does not copy that link, because it is outside the home folder.

1. Make sure that the link is missing:

   ```sh
   ls -l /var/run/docker.sock
   ```

2. Install the helper. It needs the password of an administrator:

   ```sh
   sudo podman-mac-helper install
   ```

3. Before you restart the machine, record the running containers. The restart stops all of them:

   ```sh
   podman ps --format '{{.Names}}' > running-before-restart.txt
   ```

4. Restart the machine, and start the recorded containers again:

   ```sh
   podman machine stop && podman machine start
   podman start $(cat running-before-restart.txt)
   ```

5. Make sure that the link and the API work:

   ```sh
   readlink /var/run/docker.sock
   docker -H unix:///var/run/docker.sock version --format '{{.Server.Version}}'
   ```

If you cannot restart the machine now, set `DOCKER_HOST` instead:

```sh
export DOCKER_HOST="unix://$(podman machine inspect --format '{{.ConnectionInfo.PodmanSocket.Path}}')"
```

## 3. Build the runner image

act uses `catthehacker/ubuntu:act-latest` as the runner. `Dockerfile.runner` pins it by the digest of its multi-arch index, and corrects two differences from the GitHub runner. Build it for the CPU of the host:

```sh
podman build --platform linux/arm64 -t act-runner:ubuntu-24.04 -f Dockerfile.runner .
```

On an Intel Mac, use `--platform linux/amd64`. When the GitHub runner image changes, compare its tool list with the derived image again.

## 4. Run the jobs

Run the jobs in a clone of the branch, not in your working repository. act mounts the folder into the job container, and a job can write into it. Give the clone folder the name of the repository, as GitHub does (G12).

```sh
git clone -q --no-hardlinks -b <branch> <repository> <folder>/<repository name>
git -C <folder>/<repository name> remote remove origin
./act-ci.sh -r <folder>/<repository name> -b <base commit of the pull request>
./act-ci.sh -r <folder>/<repository name> -b <base commit> -j "verify migrations"
```

`act-ci.sh` writes one log for each job, `status.txt` and the copy of the workflow that act ran, to `<folder>/act-logs`, or to the folder of `-o`. When each job exits 0, it exits 0. When the working tree has changes, it stops, but `-d` lets it continue. Never operate `act` with no arguments: it runs every workflow that runs on a push, and that can include a deploy workflow.

To watch the runs in a browser, use `/local-ci-web`. It shows each run of `act-ci.sh` with its jobs, its `act-*` containers and their logs, on `http://127.0.0.1:2026/`.

| Setting or step | Why |
| --- | --- |
| `-W <workflow> -j <job>` on each call | A bare `act` operates every push workflow (G4) |
| `pull_request` and an event file from git | The event names the base commit and `HEAD`. A secret scan reads the commits between them |
| `-P ubuntu-latest=act-runner:ubuntu-24.04` and `--pull=false` | The runner image is local, so act must not pull it (G9) |
| `--container-architecture` of the host CPU | Emulated amd64 code can crash in the Podman machine (G7) |
| `--container-daemon-socket -` | act does not mount the socket into the job container (G1). A job that needs a container engine does not work with this setting |
| `--rm`, and a cleanup of the `act-<run id>-*` containers, networks and volumes before and after each call | A failed job keeps its containers, and its services keep their host ports (G11) |
| A copy of the workflow, `<log folder>/workflow-<run id>.yml`, whose name starts with the run id | act names each container after the workflow name and the job name only, so two runs of workflows with the same name remove each other's containers (G13) |
| One call for each matrix entry, with `--matrix <key>:<value>` | act starts the entries together, and their services collide on one host port (G8) |
| `-s GITHUB_TOKEN`, from `gh auth token` for each call | The actions download tools with it. act masks it in the logs. The script does not print it |
| A job that installs gitleaks runs natively | See section 5 |

## 5. The secret scan

A job that downloads the x64 gitleaks binary crashes in the Podman machine on Apple silicon, because the machine runs amd64 code through qemu (G7). `act-ci.sh` runs the same release natively:

1. It reads the gitleaks version from the asset name `gitleaks_<version>_linux_x64` in the job, and the pin from `GITLEAKS_SHA256`.
2. It downloads the release checksum file and the asset for the host CPU with `gh release download`.
3. When the pin is not the x64 line of that checksum file, the scan stops. Thus the native binary comes from the same release as the pinned one.
4. When the asset fails its checksum, the scan stops.
5. It scans `base..HEAD` with `gitleaks git --no-banner --redact`, as the job does, and records the number of commits.

gitleaks does not scan a merge commit as a patch, so the number of commits is the number of non-merge commits in the range. Compare it with `git rev-list --count --no-merges base..HEAD`. A scan of 0 commits is not a pass.

## 6. Differences from a GitHub run

- The jobs run on the CPU of the host, and the secret scan runs on macOS. GitHub runs them on its own runner.
- The runner image is not the GitHub image. A job that passes here can still fail on GitHub because of a tool that only one image has.
- act gives service containers their own network. A step that connects to a service on `localhost` can behave differently.
- The checkout step copies the local clone. It does not fetch from GitHub.
- The workflow name starts with the run id, for example `r261110071500p4242-CI`. A step that reads `github.workflow` gets that name.

## 7. Gotchas, as measured

| # | Symptom | Exact error | Cause | Fix |
| --- | --- | --- | --- | --- |
| G1 | Each job fails in "Set up job" | `making volume mountpoint for volume <host socket>: mkdir ...: operation not supported` | act mounts the socket path of the host into the job container, and the macOS path does not exist in the Podman machine | `--container-daemon-socket -` |
| G2 | The first action step fails | `failed to copy content to container: ... statat var/run/act: path escapes from parent` | The runner image has `/var/run -> /run`, an absolute link, and the copy API of Podman refuses it | The derived image with `/var/run -> ../run` |
| G3 | A step that calls yarn fails | `spawnSync yarn ENOENT` | The act image has no Yarn, but the GitHub ubuntu-24.04 runner has Yarn 1.22.22 | Install the same version in the derived image |
| G4 | A bare `act` runs each push workflow | none | act runs every workflow that the event starts | Always `-W <workflow>` and `-j <job>` |
| G5 | act does not find Podman | none: act uses `/var/run/docker.sock` | The link of the Podman helper is missing, for example after a move to a new Mac | Section 2, or set `DOCKER_HOST` |
| G6 | A machine restart stops each container | none | A restart of the Podman machine stops all containers | Record `podman ps` first, and `podman start` the list after |
| G7 | An x64 binary crashes in an amd64 job | `fatal error: lfstack.push` (Go runtime) | The Podman machine runs amd64 code through `qemu-x86_64-static`, and the Go runtime fails under it | Run the same release for the host CPU, as in section 5 |
| G8 | One matrix entry fails in "Set up job" | `failed to start container: ... "proxy already running"` | act starts the matrix entries together, and the service of each entry publishes the same host port | One call for each entry, with `--matrix` |
| G9 | Each run pulls the runner image again | none: the log shows `forcePull=true` | act pulls the image by default | A local image and `--pull=false` |
| G10 | An interrupted run leaves a job container | `act-<run id>-...` is `Up` | An interrupted act run does not clean up | When that run has ended, remove its `act-<run id>-*` containers |
| G11 | The next job fails, but not for its own reason | `proxy already running`, and an `act-...` container still holds the port | act removes containers after a failure only with `--rm`, and `--rm` does not remove a container that did not start | `--rm`, and a cleanup before and after each call |
| G12 | A test that finds files by the repository folder fails | for example `path is outside the three repositories: <clone>/docs/...` | GitHub checks out to `<workspace>/<repository>/<repository>`, but act mounts the clone at its own path, with its own folder name | Name the clone folder after the repository |
| G13 | A job of another project fails while a run of this project starts | `can only create exec sessions on running containers: container state improper` | Both workflows are named `CI`. act gives a job the same container name in both projects, and removes the container of the other run when it starts its own | `act-ci.sh` runs a copy of the workflow whose name starts with a run id, and cleans up only `act-<run id>-*` |

Two of these were first read as the wrong cause. The first `proxy already running` came from G11, a service that a failed job left behind, and not from G8. Only a run on a clean engine showed that G8 was also real. Before you name the cause of an act failure, remove the `act-*` containers of runs that have ended, and run the job again. Do not remove the containers of a run that is still active (G13).

## 8. Change the script

After each change of `act-ci.sh` or `setup.sh`, operate `shellcheck -S style act-ci.sh setup.sh` and the tests of this kit (`python -m pytest tests/test_setup_local_ci.py`). The tests run the script with stand-in commands for `act`, `podman` and `gh`, so that they need no container engine.
