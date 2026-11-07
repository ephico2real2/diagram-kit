---
name: fix-defect
description: How each defect is handled, in the form used on ephico2real2/cmapi. A defect gets a GitHub issue at once. The issue has what is wrong, where, how to prove it, measured or inferred, a research mandate and its parent. An agent researches the fix, reviewers attack it, and the arbiter tests it before it is applied. Use when a defect, bug, failed test, proof gap or required configuration is found by anyone, at any stage, also in a review, in CI or on work that is not merged. Also use it when the user types /fix-defect.
---

# /fix-defect: every defect is logged, researched, reviewed and proven

The owner's rule, 2026-11-06. No defect is fixed or dropped without an issue, however small and whoever found it. That includes a reviewer's finding on unmerged work, and a CI failure. A repository with its own `fix-defect` skill (cmapi) uses that copy.

The main session is the arbiter. It files, briefs, validates, tests, decides and merges or applies. It does not write the fix.

Do not hand the owner a chat list to track. A proof gap, a required configuration and an owner prerequisite are also filed, as tasks. The report names issue numbers.

## What counts as a defect

Owner rule, 2026-11-07: "file issues for all defects". Each of these gets its own issue:

- A fault in the application, whatever the tests say.
- A fault in a test, a test flow or a test script, including a test that passes by chance.
- A step in a guide or a document that fails as written, and a wrong file, line or source in a document.
- A fault in an agent's patch or script, or in a tool that the project uses, including work that is not merged.
- A fault that an audit finds in the work of an agent, and a regression that a fix causes.
- A behavior difference between platforms that a test works around. A workaround in a test does not close the question of whether the app is wrong.
- A proof gap: something that a result seems to prove and does not.

Search for a duplicate before you file. If the defect has an issue, comment there with the new measurement. On 2026-11-07 this search found that a birth date failure was an open issue. The comment on that issue added a table of 3 fixes in 3 time zones.

State who measured it in each issue. An agent's result that the arbiter did not operate says so.

After each agent job, read `verdicts.md`, `fixes.md` and `research.md` for defects, and add the faults of your own audit. The audit is not finished until each defect has an issue number. A claim that says "this is only a test detail" gets a filed issue that says so, not a line in chat.

## The test loop

Owner rule, 2026-11-07: "all defect found during app testing are file as issues and then resolved immediatly and restart again until all error are fixed". This applies to each test of an app, a function or a mobile app. A test run is not finished while it has a failure.

1. Operate the whole test from its first step, on a clean state.
2. At the first failure, stop the run. Find the cause from the data, not from a guess.
3. File the issue at once, with the form in section 1. Search for a duplicate first.
4. Fix the cause in the isolated clone, in one commit for each defect. Add a test that fails before the fix and passes after it.
5. Restart from step 1, from the first step of the test and not from the failed step, because a fix can break an earlier step.
6. Finish only when one full run has 0 failures and 0 skipped steps on the final code.

These rules keep the loop honest:

- Never make a test pass by removing it, by weakening its assertion, or by adding a retry that hides a race. A test changes only if the evidence shows that the test is wrong. The commit then states that evidence.
- A flow that works around an app behavior needs its own issue for that behavior. The workaround does not resolve it.
- If a defect needs an owner decision, a real provider or a store account, file it, say what it needs, and continue with the rest. The final report names it as open. It does not count as fixed.
- If 3 different fixes fail for one defect, stop the work on that defect and report the data from each attempt.
- "Resolved" means fixed and retested in the clone. A fix reaches the review branch only after the arbiter rules on it. Money, security and migration fixes also get the 3 reviews. An issue closes only through a merged fix, so it stays open with the label `status:fixed-on-review-branch` until then.

## 1. Log it, at once

File the issue as soon as the defect is seen, before fixing anything. The owner's yes is not needed for a defect, unless the owner held that specific filing back. The title states what is wrong, not the work to do.

```markdown
**What is wrong:** the behavior, in plain words.

**Where:** `file:line`, on the commit or pull request.

**How to prove it:** a command or test that fails today.

**Measured or inferred:** which, and from which environment. Say so if nobody reproduced it. Say what has not run.

**Research:** search the primary sources, compare the options, choose the industry best practice, fix the cause rather than the symptom, and record the choice and its sources.

Part of #N.
```

Then comment on each parent with the new issue numbers: `Defects found under this issue: #A, #B.` Add the issue to the open bugs in `build-tracker.md` at the next update, in the same commit as the state change.

Project rules still apply to the issue: its language mode, its label set and its ID prefixes, if the repository has them.

If the repository tracks releases with milestones, set the milestone of the release that carries the fix. A milestone names a thing that ships, such as a release or a train. A theme is a label, and a body of work is a parent issue. If the carrying release is not known yet, leave it empty and set it when the research names it. A defect found in a patch takes the milestone of the issues that the patch fixes, because it ships in the same change.

Set the class with the questions of `/agile`. A defect does not get "no class" by default. If its fix adds a new control, the defect is `INV`. A defect in new work that is not merged is also `INV`. If its cause is an earlier shortcut, it is also `TDT`.

### One status label for each issue

If the repository has `status:` labels, each issue has exactly one. On 2026-11-07, 16 issues had 2 status labels, because `--add-label` added the new status and kept `status:open`. Then the tracker did not show which status was true. Change a status in one command, and then count the issues with more than one:

```sh
gh issue edit <n> --add-label status:fixed-on-review-branch --remove-label status:open
gh issue list --state all --limit 500 --json number,labels \
  --jq '[.[] | select(([.labels[].name | select(startswith("status:"))] | length) > 1) | .number]'
```

The count must be an empty list. Do this in each repository after each change of status.

### The tracker shows the milestone and the status

The table of open defects in `build-tracker.md` has the columns `| ID | Issue | Milestone | Status | Defect |`. Read both values from GitHub, not from memory. The milestone is its short name, or "None yet". The status is the one `status:` label. A row with 0 or 2 status labels is a fault of the issue. Fix the labels and read the table again. State the time of the read above the table.

## 2. Research and fix, in a background agent

Start a fresh agent in the background, on the model the project names. Related defects can share one agent, with one issue per defect. Its brief:

- The issue numbers, and an isolated clone or export with no remote.
- The research mandate: primary sources first, and the options it rejected, with why.
- A test that fails before the fix and passes after. The test exercises real behavior. A search of a file for a string does not count.
- The limits of the project: what it must not touch, no secrets, and that a permission refusal stands.
- Report the solution, its sources, each test before and after, and what is measured, inferred and not tested.

Write the result inline in the issue under `**Solution (inline, not applied):**`, with the code and the test. If the project moves work by patch, keep it inline until it moves to the parent issue as a patch. Then replace the section with a link.

**Save as you go, in a set structure.** Paste the brief standard of `/agent-report` (`brief-standard.md` beside its `SKILL.md`) into each brief. Replace `<folder>` with the parent of the job folders and `<job>` with the job name, so that `<folder>/<job>/` is the job folder. On 2026-11-07 a brief replaced `<folder>` with the job folder itself, and the pasted text then named `<job>/<job>/`. The agent writes research, tests, verdicts, fixes and recommendations to separate files, per ID, after each ID. A stop then loses nothing, and the arbiter reads `verdicts.md` first.

**Read code through the graph.** If the project has an index, each brief tells the agent to use tokensave or CodeGraph, with the `graph_root` of each repository. The brief standard holds the text, and it works from a Codex sandbox (tested 2026-11-06). The agent reports its graph and shell call counts. See `/tokensave-fork` for the binary, the permissions of each agent and the test.

## 3. Review, the same way as all reviews

On exports, never in a repository, with the reviewers the project names:

1. Reviewer 1: a narrow brief of exact files and claims, returning the full code of each fix and test.
2. Reviewer 2, not the author: checks each snippet of reviewer 1 against the design and the code, updates them, and reports with full code what reviewer 1 missed.

Anything new that a reviewer finds goes back to step 1 and gets its own issue.

## 4. Arbitrate: validate and test

Reports are claims until tested. Before accepting anything, the main session:

- Reproduces the failure, and reads every line that a patch removes from a test.
- Applies the patches to a fresh export, with no fuzz, and operates the full suites itself, mutants included.
- Decides each fix with its reason. A failing test stands unless it is shown to be wrong, and a finding with one is never dismissed by opinion.
- Applies accepted patches unchanged, one commit each. A patch that does not fit goes back to reviewer 2.

## 5. Close it

- A pull request says `Closes #N` for each defect, `Part of #parent`, and who wrote what.
- A fix reaches a long-lived branch, such as a review branch, only through a pull request from a working branch. Owner rule, 2026-11-07. Fill a copy of the pull request template, and give it with `--body-file`. GitHub reads the template only for a pull request opened in the browser. Set `--milestone` to the train of the fix and `--label` to its type. Each issue in `Closes #` has the same milestone as the pull request.
- `Closes #N` closes an issue only in a pull request to the default branch. After a merge to another branch, set the status label by hand, as in section 1.
- Merge only after CI passes on the pull request, and tick the checklist of the template part for that branch.
- Save the review record where the project keeps it.
- Close a defect only through its merged fix, with the proof cited. A fix on a review branch does not close it.

## A permission refusal stands

If Claude Code refuses an action, do not route around it, and do not edit the permission configuration to get past it. File an issue with the exact command, do everything else, and put the command in the report.

## Report faithfully

Tell the owner what was found, what was fixed and how it was proven, and what is not proven yet. A defect that cannot be fixed yet stays open and is named as open.
