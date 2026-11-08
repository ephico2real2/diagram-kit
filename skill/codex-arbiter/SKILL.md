---
name: codex-arbiter
description: Review pending patches with many background Codex agents before any commit or apply. Each agent works in a disposable clone with no remote, and returns a report and a code fix for each bug, debt or security issue. Claude keeps the inventory, rules on each change fully or in part, and tests it. All agents run as one background job that wakes Claude once. Use when the user types /codex-arbiter, or asks for a Codex review that returns fixes, or for a review of patches that are not applied.
---

# /codex-arbiter: Codex finds and fixes, Claude rules and verifies

Nothing gets a commit or an apply before this review. Codex writes only in a disposable clone. Only Claude changes
the real repository, and only after it tests the change itself.

These rules are defaults. When the work needs it, the owner and Claude can override a rule of this skill. Say which rule
changes and why, in the brief and in the report. An override of this skill does not change a standing owner
constraint, such as a branch that must not be touched.

## 1. Inventory first

Write one page that lists each patch that is not applied: path, repository, content, added lines, the result of
`git apply --check`, and a review state (Pending, Accepted with the commit, Refused with the cause). Separate
candidates to apply from options of an owner decision. Keep the page current. Do not apply an option of an open
owner decision: review its code, and leave the choice with the owner.

Copy the pending diffs out of the session scratchpad before the review starts.

## 2. Confirm the model

Read the model list in `~/.codex/models_cache.json`, then run a real probe. Use the model that the user named.
If stdin stays open, `codex exec` waits on it, so pipe the prompt in. An open stdin gives only the line
`Reading additional input from stdin...`, and that line proves nothing.

```sh
printf 'Reply with the single word READY.' | codex exec -m gpt-6.1-sol --sandbox read-only --skip-git-repo-check -
```

## 3. One disposable clone per reviewer

```sh
git clone -q --no-hardlinks -b <branch> <repo> "$C/wt/<id>"
git -C "$C/wt/<id>" remote remove origin          # it cannot push
ln -s <repo>/node_modules "$C/wt/<id>/node_modules"
printf 'node_modules\n.tokensave\n' >> "$C/wt/<id>/.git/info/exclude"
git -C "$C/wt/<id>" config user.name reviewer
git -C "$C/wt/<id>" config user.email reviewer@example.com
# Pending work under review becomes one commit, so that the diff of the reviewer shows only its own fixes.
git -C "$C/wt/<id>" apply --binary <pending.diff> && git -C "$C/wt/<id>" add -A \
  && git -C "$C/wt/<id>" commit -q -m 'BASELINE: pending change under review'
```

Use a clone, not a `git worktree`: a worktree shares `.git`, its remotes and its refs with the real repository.
Put `$C` in a folder that outlives the session. If tests need a database, give each reviewer one empty database, with
the URL in the environment. Never print the URL, and do not ask the reviewer to use the docker socket, because the
sandbox blocks it.

## 4. Precise briefs

One shared brief, plus one short brief for each reviewer. "Review this" is not acceptable. Each item names the exact
file, the lines or the patch path, and what the reviewer must confirm or refute.

The shared brief states:

- Find real defects only: bugs, money or data loss, races, security holes, added debt, wrong or missing tests.
- Each defect needs a fix as a unified diff and a test that fails before the fix and passes after it, with both results.
- The clone is the only writable code tree. No push, no install, no lockfile change, no reformat. Keep the line
  endings of each file. Do not print secrets. Do not use the real network.
- A test failure counts only with evidence of whether it fails without the patch too.
- The verdict for each patch is APPLY, APPLY WITH FIX, DO NOT APPLY or OWNER DECISION.
- Save the report to `$C/reports/<id>.md` and each corrected patch to `$C/fixed/`. Leave fixes uncommitted.
  The sandbox keeps `.git` read-only, so this rule also matches what the sandbox allows. A job that must commit needs
  `--add-dir <clone>/.git` (see `/agent-report`, "Let a Codex job commit in its clone").
- The final chat message is at most 5 lines, so that a report costs Claude few tokens.

## 5. One job, one wake-up

Start all reviewers from one script with the Bash tool and `run_in_background: true`. When all reviewers end, the script
ends, so the session wakes once. Do not poll, and do not read the logs while they run. macOS has no
`timeout` by default, so the script uses `alarm` from Perl as the limit for each reviewer.

```zsh
#!/bin/zsh
C=${0:a:h}
go() { id=$1; brief=$2; shift 2
  ( print -r -- "$(cat $C/briefs/common.md)

$(cat $C/briefs/$brief.md)" | perl -e 'alarm 7200; exec @ARGV' codex exec -m gpt-6.1-sol \
      --sandbox workspace-write --skip-git-repo-check \
      -c sandbox_workspace_write.network_access=true \
      --add-dir $C/reports --add-dir $C/fixed "$@" -o $C/logs/$id.final.txt - > $C/logs/$id.log 2>&1
    print "$id exit=$? $(date -u +%H:%M:%S)" >> $C/logs/status.txt ) &
}
: > $C/logs/status.txt
go a1 a1 -C $C/wt/a1-backend
go a2 a2 -C $C/wt/a2-portal
wait
cat $C/logs/status.txt
```

`network_access=true` is for a local database in the sandbox. If no test needs a database, omit it. A reviewer with
two clones takes `-C` for the first and `--add-dir` for the second. A tokensave MCP error in the log of a clone that
has no index is not a failure.

## 6. Arbitrate

After the wake-up, read the status and the reports only. Then, for each finding:

1. Read the cited code in the real repository. A report is a claim, not a fact.
2. Accept it fully, accept it in part, or refuse it. Give the cause of each ruling.
3. Apply an accepted change surgically to the real tree. Keep the line endings.
4. Run the test yourself: it fails before and passes after. Run the suites of the repository and the type check.
5. Make one commit for each finding. Update the inventory, the tracker of the project and the issue.

Lessons of the first run, on 2026-11-06, with 6 reviewers and 24 patches:

- Test the corrected fix too. A reviewer's fix compared with `===`. A foreign-user path then compared `undefined` with a stored NULL. The arbiter found this defect with a new test.
- Before you call a test failure a proof, read the rejection reason. The first failure of that new test came from its setup.
- Look at the diff of each mutation. A `sed` that matches nothing leaves the code as it was, and the green run proves nothing.
- Read the bytes or the commits that a scan read. `no leaks found` with 0 bytes scanned is not a pass.
- Refuse a test that fixes an implementation detail, such as an exact count of SQL statements.
- Before you keep a new test, compare it with the existing tests. One spec was 98.15% the same text as an existing suite.

Tell the owner what was refused, and what stays open after a partial fix. After the work is committed and the owner has the result, remove the clones and the databases.

**Save as you go, in a set structure.** Paste the brief standard of `/agent-report` into each brief. The agent writes research, tests, verdicts, fixes and recommendations to separate files, per ID, after each ID. A stop then loses nothing, and the arbiter reads `verdicts.md` first.

**Read code through the graph.** If the project has an index, each brief tells the agent to use tokensave or CodeGraph, with the `graph_root` of each repository. The brief standard of `/agent-report` holds the text, and it works from a Codex sandbox (tested 2026-11-06). The agent reports its graph and shell call counts. The server must be the fork: see `/tokensave-fork` for the binary, the permissions of each agent and the test.
