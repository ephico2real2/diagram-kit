#!/bin/zsh
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Keep the work of an agent job: commit what it left, push its branch, and open a draft pull request (owner mandate
# 2026-11-12). The runner calls this after each round, never the agent: an agent sandbox has no push and no gh write.
#
# usage: draft_pr.sh <clone> <owner/repo> <branch> <base> <job folder> <title>
#   <base>   the base branch, as a local branch of the clone (the clone was made from it)
#   DRY_RUN=1          write the body and the plan to stdout; no push, no gh call
#   LABELS="a b"       labels for a new draft;  MILESTONE="name"  its milestone
#   PART_OF="#123"     the parent issue: the body opens with "Part of #123.", as the project flow asks of each PR
#   KEEP_AUTHOR=1      keep the agent's author; by default the new commits take the global git identity
(( $# == 6 )) || { print -u2 "usage: draft_pr.sh <clone> <owner/repo> <branch> <base> <job folder> <title>"; exit 2; }
C=${1:a} slug=$2 branch=$3 base=$4 J=${5:a} title=$6
job=${J:t}
fail() { print -u2 "draft_pr: $*"; exit 1; }
[[ -z $PART_OF || $PART_OF =~ '^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#[0-9]+$' ]] || fail "PART_OF must be #<n> or owner/repo#<n>"
git -C $C rev-parse --git-dir >/dev/null 2>&1 || fail "$C is not a git clone"
git -C $C rev-parse --verify -q "$base" >/dev/null || fail "base $base is not a branch of $C"
[[ $(git -C $C branch --show-current) == $branch ]] || fail "the clone is not on $branch"

# 1. Nothing stays uncommitted. The WIP prefix tells the arbiter that the job did not commit this itself.
if [[ -n $(git -C $C status --porcelain) ]]; then
  git -C $C add -A && git -C $C commit -q -m "WIP $job: the uncommitted work of the agent job" || fail "commit failed"
fi

# 2. The new commits: those above the remote branch when a draft exists, otherwise those above the base.
url=https://github.com/$slug.git
from=$(git -C $C merge-base HEAD "$base")
if [[ -z $DRY_RUN ]] && git -C $C fetch -q $url "refs/heads/$branch" 2>/dev/null; then
  git -C $C merge-base --is-ancestor FETCH_HEAD HEAD || fail "the remote $branch is not an ancestor of HEAD; no force push"
  from=$(git -C $C rev-parse FETCH_HEAD)
fi
count=$(git -C $C rev-list --count $from..HEAD)
(( count > 0 )) || fail "no new commit on $branch above $from"

# 3. The person who owns the work is the author, unless KEEP_AUTHOR is set. The map keeps the SHAs of the report usable.
if [[ -z $KEEP_AUTHOR ]]; then
  name=$(git config --global user.name) email=$(git config --global user.email)
  [[ -n $name && -n $email ]] || fail "no global git identity; set it or KEEP_AUTHOR=1"
  old=($(git -C $C rev-list --reverse $from..HEAD))
  git -C $C -c user.name="$name" -c user.email="$email" rebase -q --rebase-merges --exec \
    "git -c user.name='$name' -c user.email='$email' commit -q --amend --no-edit --reset-author" $from \
    || { git -C $C rebase --abort 2>/dev/null; fail "author rewrite failed"; }
  new=($(git -C $C rev-list --reverse $from..HEAD))
  for i in {1..$#old}; do print "${old[$i]:0:8} -> ${new[$i]:0:8}"; done > $J/draft-sha-map.txt
fi

# 4. The body. It states facts that a command measured; the arbiter rewrites it in the project template before ready.
files=$(git -C $C diff --name-only $(git -C $C merge-base HEAD "$base")..HEAD)
tests=$(print -r -- $files | grep -cE '(^|/)(test|tests|__tests__|e2e|spec)/|\.(test|spec|pg-spec|e2e-spec)\.[cm]?[jt]sx?$|_test\.(py|go)$|(^|/)test_[^/]+\.py$')
reports=$(print -r -- $files | grep -E '(^|/)(plan|research|tests|verdicts|fixes|recommendations|resume)\.md$' | grep -v '^docs/')
tally=$( [[ -f $J/verdicts.md ]] && grep -oE '\b(CONFIRMED|REFUTED|PLAUSIBLE|NOT REACHED)\b' $J/verdicts.md | sort | uniq -c | awk '{c=$1; $1=""; printf "%s%s %s", sep, c, substr($0,2); sep=", "}')
body=$J/draft-pr.md
{
  [[ -n $PART_OF ]] && { print "Part of $PART_OF."; print; }
  print "Draft from the agent job \`$job\`. Nobody reviewed it yet."
  print
  print "The arbiter rules on each finding, runs the tests and local CI, and then marks it ready, asks for another round, or closes it."
  print
  print "## Commits"
  print
  git -C $C log --reverse --format='- `%h` %s' $(git -C $C merge-base HEAD "$base")..HEAD
  print
  print "## Tests"
  print
  if (( tests > 0 )); then print "$tests test files changed."
  else print "No test file changed. The arbiter adds the tests, or states why no test applies, before ready."; fi
  print
  print "## Report"
  print
  print "Job folder: \`${J/#$HOME/~}\`. Verdicts: ${tally:-no verdicts.md}."
  if [[ -n $reports ]]; then
    print
    print "Report files in the repository (move them out before ready): $(print -r -- $reports | tr '\n' ' ')"
  fi
} > $body

if [[ -n $DRY_RUN ]]; then
  print "DRY RUN: $count new commits on $branch, base $base"
  cat $body
  exit 0
fi

# 5. Push without force, then open the draft once. A later round only pushes to it.
git -C $C push -q $url "HEAD:refs/heads/$branch" || fail "push failed"
pr=$(gh pr list -R $slug --head $branch --state open --json url --jq '.[0].url')
if [[ -z $pr ]]; then
  args=(--draft -R $slug -B $base -H $branch --title "$title" --body-file $body)
  [[ -n $MILESTONE ]] && args+=(--milestone "$MILESTONE")
  for l in ${=LABELS}; do args+=(--label $l); done
  pr=$(gh pr create $args) || fail "gh pr create failed; the branch is pushed"
else
  gh pr comment $pr -R $slug --body "Round \`$job\` pushed $count commits. See the job folder \`${J/#$HOME/~}\`." >/dev/null
fi
print "draft $pr ($count new commits)" | tee -a $J/draft-pr.txt
