#!/usr/bin/env bash
# Move work folders into the workbench, and keep each git worktree inside them working.
# usage: move.sh <project> <folder>...
# WORKBENCH sets the root. The default is $HOME/gitRepos/workbench.
set -euo pipefail

root=${WORKBENCH:-$HOME/gitRepos/workbench}
[[ $# -ge 2 ]] || { echo "usage: move.sh <project> <folder>..." >&2; exit 2; }
project=$1; shift
dest=$root/$project
mkdir -p "$dest"

# A process that keeps a file open in the folder would lose it. watchman only watches, so it does not count.
users_of() {
  command -v lsof >/dev/null || return 0
  lsof -Fpcn 2>/dev/null | awk -v dir="$1/" '
    /^p/ { pid = substr($0, 2) } /^c/ { cmd = substr($0, 2) }
    /^n/ { if (index(substr($0, 2) "/", dir) == 1 && cmd != "watchman") print pid " " cmd }' | sort -u
}

# A container with a bind mount of the folder would lose it.
mounted_in() {
  local engine
  for engine in podman docker; do
    command -v "$engine" >/dev/null || continue
    "$engine" ps --format '{{.Names}} {{.Mounts}}' 2>/dev/null | grep -F "$1" || true
  done
}

# Each linked worktree in the folder: its .git is a file that names the main repository.
worktrees_in() {
  find "$1" -maxdepth 3 -name .git -type f -not -path '*/node_modules/*' 2>/dev/null
}

status=0
for src in "$@"; do
  src=${src%/}
  name=$(basename "$src")
  target=$dest/$name
  if [[ ! -d $src ]]; then echo "SKIP $src: no such folder" >&2; status=1; continue; fi
  if [[ -e $target ]]; then echo "SKIP $src: $target exists" >&2; status=1; continue; fi
  busy=$(users_of "$src")
  if [[ -n $busy ]]; then echo "SKIP $src: open in $busy" >&2; status=1; continue; fi
  mounts=$(mounted_in "$src")
  if [[ -n $mounts ]]; then echo "SKIP $src: mounted in $mounts" >&2; status=1; continue; fi

  mains=()
  while IFS= read -r dotgit; do
    gitdir=$(sed -n 's/^gitdir: //p' "$dotgit")
    # .../<main>/.git/worktrees/<id> -> <main>
    mains+=("$(dirname "$(dirname "$(dirname "$gitdir")")")|${dotgit#"$src"}")
  done < <(worktrees_in "$src")

  mv "$src" "$target"
  echo "MOVED $src -> $target"

  for entry in "${mains[@]+"${mains[@]}"}"; do
    main=${entry%%|*}; rel=${entry#*|}; tree=$target$(dirname "$rel")
    git -C "$main" worktree repair "$tree" 2>/dev/null || true
    if [[ $(git -C "$tree" rev-parse --show-toplevel 2>/dev/null) -ef $tree ]]; then
      echo "REPAIRED worktree $tree of $main"
    else
      echo "BROKEN worktree $tree of $main: run git -C $main worktree repair $tree" >&2; status=1
    fi
  done
done
exit $status
