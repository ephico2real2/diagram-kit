---
name: adversarial-review
description: The adversarial review of a change before it is called ready. A per-claim brief goes to two reviewers or more from different model families, never the author, at least one with a shell. Every finding comes back with its full fix and a test that fails before and passes after. The orchestrator writes each decision with its reason and applies the accepted fixes. A record and a second pass on the fixed head follow. Use when the user types /adversarial-review, before a pull request is called ready, or when another skill asks for an adversarial pass.
---

# /adversarial-review: two model families attack the change, you decide

`/adversarial-review <pull request, branch or change>` runs one review pass. You are the orchestrator: reviewers
propose, you decide, and every decision is written down with its reason before anything is applied.

The rules come from reviews of real pull requests, where each one was broken at least once. The cases are quoted
where they explain a rule.

## 1. Two roles: orchestrator and surgeon

**Orchestrator.** Work from the source of the change (its issue, its specification, its diff), never from memory.
If the change applies a written specification, apply it block by block, with an exact-match check on each text you
replace. A necessary deviation goes back into that specification, in the same pull request, with its
reason. A real finding in a file that another change owns is routed to that change, not left as a "follow-up".

**Surgeon.** Apply a reviewer's fix only after you traced it yourself. A correct finding does not make its fix
correct. Four cases from one day of reviews:

- The finding "GitHub compares strings case-insensitively" was right. With the proposed comparison, a switch set to
  `False` runs the job that it exists to turn off. The meaning was kept and the words were fixed.
- The finding "an unbalanced backtick breaks the changelog line" was right. The fix escaped every backtick, and that
  breaks the code spans that authors write on purpose. The input was refused instead of rewritten.
- The finding "a fixed sleep can flake" was right. The proposed ready flag fired before the page painted, so the
  test passed before the event that it tests. Rejected: a weaker test that looks stronger.
- The finding "retention with backups off deletes rows that cannot be replaced" was right. The fix reverted a
  default the owner had decided. The interaction was modelled instead.

## 2. The reviewers

- **At least two, from different model families**, and never the seat that wrote the change.
- **At least one of them can run commands.** A reviewer without a shell traces from the source. It marks a claim
  that it did not measure as PLAUSIBLE, never as CONFIRMED.
- **If anything changed (a login, a version, the model list), probe each one before the review.** Send a one-line
  prompt that must answer with the expected words, and read the model and effort back from its output or log.
- **Know where the code goes.** A provider without zero data retention can keep the code and the brief. Weigh that
  before you send sensitive code.

Launch lines that work, with the model and effort you measured in place of `<model>` and `<effort>`:

```sh
# Each reviewer gets its own directory, with an export of the head under review
W="<scratch>/review_<id>_<reviewer>"
mkdir -p "${W}/head"
git archive <sha> | tar -x -C "${W}/head"

# Codex CLI: stdin closed, or it waits for input forever
cd "${W}" && nohup codex exec --skip-git-repo-check -m <model> -c model_reasoning_effort="<effort>" \
  -s workspace-write -C "${W}" "$(cat "${W}/brief.md")" < /dev/null > "${W}/answer.txt" 2> "${W}/answer.err" &

# Cursor agent with a shell, confined to its directory
cd "${W}" && nohup cursor agent -p --force --output-format text --trust --workspace "${W}" \
  --model <model> "$(cat "${W}/brief.md")" < /dev/null > "${W}/answer.txt" 2> "${W}/answer.err" &
```

A Claude Code subagent is the third kind. Launch it with the Agent tool and the brief as its whole prompt. Put one
paragraph before the brief that makes it read-only: no file changes, no git writes, nothing that changes a cluster.

## 3. The brief: never "review this"

Write the brief to a file and give every reviewer the same file. `${CLAUDE_SKILL_DIR}/brief-template.md` is
the skeleton.

- **One numbered claim per thing** to confirm or refute, each with the exact file, symbol and lines, what it
  asserts, and how to measure it.
- **One line per claim back:** `C<n>: CONFIRMED | REFUTED | PLAUSIBLE`, with the artefact (a command and its output,
  `file:line`, a quoted line from the installed source). A bare CONFIRMED counts as nothing.
- **For every finding, the full fix and a test.** The whole function, block or file section as it must read, with
  its path; and a test that fails before the fix and passes after. Say it in the brief in these words: a finding
  without its full snippet and its test is not a finding and will be discarded.
- **The constraints:** no commits and no edits to tracked files. Run the change only in a copy outside the
  repository, create nothing in the tree, and delete every temporary file.
- **What to cover:** the semantics the change relies on (an expression, a default, a version), the off state and
  every switch, fidelity to the specification, what depends on the change, and what goes wrong on the next real
  use.

## 4. Launch, then wait without polling

- Every reviewer writes to its own directory and its own output file. Two reviewers sharing a file clobber each
  other, and a reviewer's exit trap once deleted a whole shared scratch directory.
- A reviewer reads an export or a worktree of the head under review, never the tree you are editing.
- After launching a CLI reviewer, read the first bytes of its error output. A header that names the model means it
  is working. A line saying it is reading stdin means it is stuck: a background `codex exec` without `< /dev/null`
  once waited 4 h 16 min.
- A Cursor run can end with an empty output. Launch it again.
- Arm one waiter. When every reviewer finished, it wakes you. It matches failure as well as success. Each manual
  "is it done yet?" costs a full round trip.
- When all are done, check that no reviewer process is still alive, run `git status`, and remove anything a
  reviewer left in the tree before you run the tests.

## 5. Decide in writing, then apply and validate

1. Re-check every verdict yourself, CONFIRMED included: it is the weakest verdict, because it produces nothing you
   can inspect. For a claim about semantics, measure both the documentation and a real run.
2. Trace the mechanism of each fix: the order of events, the escaping, and the meaning of a flag that is unset.
   Before you trust the proposed test, make it fail against the current code.
3. Write the decision for each finding. It is one of four: accepted, accepted on the fact with the snippet rejected,
   rejected, or routed to the change that owns the file. Give the reason for each rejection.
4. Apply the accepted fixes one at a time. Then run the affected test, the full suite, the build, and the change's
   own verification on the real environment. "Compiles" or "looks right" is not validation.
5. Send each reviewer's accepted fixes to another reviewer to confirm or refute, with a test.

## Agents that save their work

Paste the brief standard of `/agent-report` into each brief, so that a stopped reviewer loses nothing and reads code through the graph if the project has an index. Its audit plants claims with known answers, and shows whether a reviewer did the work. Use it when you doubt a report.

## 6. The record

Write the record in the repository. `${CLAUDE_SKILL_DIR}/record-template.md` is the skeleton. It holds a table of
claims, reviewers and decisions, with each reviewer's model as run. It has one section per finding, with Finding,
Re-check and Decision. It lists what a reviewer volunteered and what happened to it, and it ends with the outcome. A record quotes wrong lines on
purpose, so exclude it from any check of citations. Commit with a message that names the review, and
comment on the pull request with the decisions and the re-validation.

## 7. The second pass

After the fixes, brief the same reviewers on the fixed head. They check that each accepted fix closes its hole and
opens no other, then attack what the first pass did not ask: new inputs, the next real use, two runs in a row. The
second pass is cheap and it still finds things.

## Checklist

1. Tests and CI green before the review. The pull request open, its body naming its issue.
2. The brief in a file, with numbered claims, exact locations, an artefact per verdict, the full fix and a test per
   finding, and the constraints.
3. If anything changed, each reviewer probed. Each one launched into its own directory, CLI reviewers with stdin
   closed.
4. One waiter. All reviewers finished. The tree clean of reviewer files.
5. Every verdict re-checked. Every decision written with its reason.
6. Fixes traced and applied. Tests, build and the change's own verification run again.
7. The record committed and the pull request commented. CI green on that commit.
8. The second pass on the fixed head, and steps 4 to 7 again for what it finds.
9. Merge only by the repository's rule. Where the owner merges, do not merge yourself.
