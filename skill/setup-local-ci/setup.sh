#!/bin/bash
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copy the local CI files of this skill into a project: act-ci.sh and Dockerfile.runner go to <project>/ci/local/.
# A copy that differs from the kit stays as it is, unless -f is given, so that a project change is never lost.
set -uo pipefail

usage() {
  echo "usage: setup.sh [-f] <project folder>" >&2
  echo "  -f  replace a copy that differs from the kit" >&2
  exit 2
}

force=0
while getopts f opt; do
  case $opt in f) force=1 ;; *) usage ;; esac
done
shift $((OPTIND - 1))
[[ $# -eq 1 ]] || usage

kit=$(cd "$(dirname "$0")" && pwd)
project=$(cd "$1" 2>/dev/null && pwd) || { echo "setup.sh: no folder $1" >&2; exit 2; }
git -C "$project" rev-parse --git-dir >/dev/null 2>&1 || { echo "setup.sh: $project is not a git repository" >&2; exit 2; }
target=$project/ci/local
mkdir -p "$target"

status=0
for file in act-ci.sh Dockerfile.runner; do
  if [[ ! -e $target/$file ]]; then
    cp "$kit/$file" "$target/$file"
    echo "added    ci/local/$file"
  elif cmp -s "$kit/$file" "$target/$file"; then
    echo "same     ci/local/$file"
  elif [[ $force -eq 1 ]]; then
    cp "$kit/$file" "$target/$file"
    echo "replaced ci/local/$file"
  else
    echo "differs  ci/local/$file: kept. Compare it with $kit/$file, or pass -f to replace it" >&2
    status=1
  fi
done
chmod +x "$target/act-ci.sh"

cat <<EOF

Next steps:
  podman build --platform linux/$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/') -t act-runner:ubuntu-24.04 -f ci/local/Dockerfile.runner ci/local
  git clone -q --no-hardlinks -b <branch> $project <folder>/$(basename "$project")
  ci/local/act-ci.sh -r <folder>/$(basename "$project") -b <base commit>
EOF
exit $status
