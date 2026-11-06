---
name: fix-defect
description: How each defect is handled, in the form used on ephico2real2/cmapi. A defect gets a GitHub issue at once. The issue has what is wrong, where, how to prove it, measured or inferred, a research mandate and its parent. An agent researches the fix, reviewers attack it, and the arbiter tests it before it is applied. Use when a defect, bug, failed test, proof gap or required configuration is found, or when the user types /fix-defect.
---

# /fix-defect: every defect is logged, researched, reviewed and proven

The owner's rule, 2026-11-06. No defect is fixed or dropped without an issue, however small and whoever found it. That includes a reviewer's finding on unmerged work, and a CI failure. A repository with its own `fix-defect` skill (cmapi) uses that copy.

The main session is the arbiter. It files, briefs, validates, tests, decides and merges or applies. It does not write the fix.

Do not hand the owner a chat list to track. A proof gap, a required configuration and an owner prerequisite are also filed, as tasks. The report names issue numbers.

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

Project rules still apply to the issue. If the repository has a language mode, a label set or ID prefixes, use them.

If the repository tracks releases with milestones, set the milestone of the release that carries the fix. A milestone names a thing that ships, such as a release or a train. A theme is a label, and a body of work is a parent issue. If the carrying release is not known yet, leave it empty and set it when the research names it.

## 2. Research and fix, in a background agent

Start a fresh agent in the background, on the model the project names. Related defects can share one agent, with one issue per defect. Its brief:

- The issue numbers, and an isolated clone or export with no remote.
- The research mandate: primary sources first, and the options it rejected, with why.
- A test that fails before the fix and passes after. The test exercises real behavior. A search of a file for a string does not count.
- The limits of the project: what it must not touch, no secrets, and that a permission refusal stands.
- Report the solution, its sources, each test before and after, and what is measured, inferred and not tested.

Write the result inline in the issue under `**Solution (inline, not applied):**`, with the code and the test. If the project moves work by patch, keep it inline until it moves to the parent issue as a patch. Then replace the section with a link.

**Save as you go, in a set structure.** Paste `the brief standard of `/agent-report`` into each brief. The agent writes research, tests, verdicts, fixes and recommendations to separate files, per ID, after each ID. A stop then loses nothing, and the arbiter reads `verdicts.md` first.

**Read code through the graph.** If the project has an index, each brief tells the agent to use it, with the `graph_root` of each repository. The brief standard of `/agent-report` holds the text. The `/tokensave-fork` skill gives the binary and the permissions of each agent.

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
- Save the review record where the project keeps it.
- Close a defect only through its merged fix, with the proof cited. A fix on a review branch does not close it.

## A permission refusal stands

If Claude Code refuses an action, do not route around it, and do not edit the permission configuration to get past it. File an issue with the exact command, do everything else, and put the command in the report.

## Report faithfully

Tell the owner what was found, what was fixed and how it was proven, and what is not proven yet. A defect that cannot be fixed yet stays open and is named as open.
