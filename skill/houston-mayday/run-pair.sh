#!/bin/zsh
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Round 1 (build), then round 2 (adversarial review), of one mission: one job at a time, in disposable clones.
# usage: run-pair.sh <folder> <job> <effort r1> <effort r2> <source repository> <repository folder name> <work branch> [<base branch>]
# <folder>/<job>-r1/brief.md and <folder>/<job>-r2/brief.md must exist (make_brief.py). CODEX_MODEL names the model.
(( $# >= 7 )) || { print -u2 "usage: run-pair.sh <folder> <job> <effort r1> <effort r2> <source> <name> <branch> [<base>]"; exit 2; }
J=${1:a} job=$2 e1=$3 e2=$4 src=${5:a} name=$6 branch=$7 base=${8:-main}
model=${CODEX_MODEL:?set CODEX_MODEL to the Codex model}

mk() { # clone dir, branch, from
  git clone -q --no-hardlinks -b "$2" "$3" "$1" && git -C "$1" remote remove origin \
    && git -C "$1" config user.name codex && git -C "$1" config user.email codex@example.invalid
}

go() { # round, effort, clone
  local round=$J/$job-$1 effort=$2 wt=$3
  [[ -f $round/brief.md ]] || { print "$job-$1 exit=2 no brief" >> $J/status.txt; return 2; }
  mkdir -p $round/logs
  print "$job-$1 start $(date -u +%H:%M:%S)" >> $J/status.txt
  # macOS has no timeout(1): perl's alarm ends the job after 2 hours.
  perl -e 'alarm 7200; exec @ARGV' codex exec -m $model -c model_reasoning_effort=$effort \
    --sandbox workspace-write --skip-git-repo-check -C $wt --add-dir $round \
    -o $round/final.txt - < $round/brief.md > $round/logs/codex.log 2>&1
  print "$job-$1 exit=$? $(date -u +%H:%M:%S)" >> $J/status.txt
}

r1=$J/wt/$job-r1/$name r2=$J/wt/$job-r2/$name
# ROUNDS=r2 reruns only the review, on the round 1 clone that exists.
if [[ ${ROUNDS:-r1 r2} == *r1* ]]; then
  mkdir -p ${r1:h}
  mk $r1 $base $src && git -C $r1 switch -q -c $branch || exit 2
  go r1 $e1 $r1
fi
# The Codex sandbox keeps .git read-only, so round 1 cannot commit. Commit its work here, so round 2 sees it as commits.
if [[ -n $(git -C $r1 status --porcelain) ]]; then
  git -C $r1 add -A && git -C $r1 commit -q -m "ROUND 1: the uncommitted work of the Codex job" || exit 2
fi
if [[ ${ROUNDS:-r1 r2} == *r2* ]]; then
  mkdir -p ${r2:h}
  mk $r2 $branch $r1 || exit 2
  go r2 $e2 $r2
fi
