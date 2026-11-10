---
name: issue
description: Write and create one GitHub issue in agile form (user story, acceptance criteria, tasks, definition of done, evidence) for the current repository, grounded in the actual code, commits and measurements. Use when the user types /issue, or asks to create, file or raise an issue, story, task or bug, including issues for work that is already done.
---

# /issue — one issue a team can plan, do and close

`/issue <what the issue is about>` drafts the issue at once from what is in the repository and the
conversation. Ask a question only when the subject is ambiguous or the repository cannot be read.

Creating an issue publishes it. On a public repository anyone can read it, and it may be indexed
even if it is deleted later. So: **show the draft and get a yes before `gh issue create`**, unless
the user has already said to create the issues without asking (for example "create the issues").

## 1. Facts first

1. **Read before writing.** The files, the commits (`git log --oneline -- <path>`), the test or
   measurement output. Every claim in the issue is something you read or measured, with where.
2. **One issue, one outcome.** If the title needs "and", split it. Cross-cutting work is an epic
   (`/epic`), not a long issue.
3. **Work that is already done still gets an issue.** Cite the commits and the evidence, and tick
   each box that is true. Close it only after the work reaches the default branch (section 4).
   Record completed work on another branch as fixed there, with the issue still open.
4. **No secrets, no personal data.** No keys, tokens, passwords, private hostnames or real names.
   Refer to people by role. Use the commit identity the repository already uses.

## 2. Shape

Title: imperative and specific, at most 70 characters. `Add …`, `Fix …`, `Measure …`, `Document …`.
No ticket-speak prefixes unless the repository already uses them.

Body, in this order (leave a section out only if it has nothing true to say):

```markdown
## Story
As a <role>, I want <capability>, so that <outcome>.

## Context
What exists today, with paths and commits. Why this matters now. 3 to 6 lines.

## Acceptance criteria
- [ ] Observable, testable statements. Each says how it is checked (command, test, output).

## Tasks
- [ ] The steps, in order. One line each, starting with a verb.

## Out of scope
- What this issue deliberately does not do.

## Evidence
- For done work: commit hashes, files, the measured result (numbers, dates), links to docs.

## Definition of done
- [ ] Tested as described above
- [ ] Documented where a reader would look for it
- [ ] Committed and pushed
```

For a **bug**, replace Story with: `## What happens`, `## What should happen`, `## How to reproduce`
(exact commands), and keep the rest.

## 3. Labels, type and links

- Type label: one of `feature`, `story`, `task`, `bug`, `spike`, `documentation`. Create a missing label
  first: `gh label create <name> --color <hex> --description "<one line>"`.
- Issue type and parent: `/agile` section 2 maps each item to its GitHub issue type (`Feature`, `Task`,
  `Bug`), and section 4 sets the type and the sub-issue link through the GitHub API.
- Class label: `class:INV` for innovation, `class:TDT` for tech debt, both, or none. `/agile` gives the
  questions that decide it, and `LEGEND.md` beside it is the standard legend. A defect does not get "no class" by
  default: read its fix, because a new control, test method or gate is `INV`.
- Area label if the repository has them (`area:chart`, `area:docs`, `area:lab`, …).
- Milestone, if the repository has milestones: the release or train that ships the work
  (`--milestone "<title>"`). If no release carries it yet, leave it empty and say so in a tracker.
- Status label, if the repository has `status:` labels: exactly one. Change it in one command,
  `gh issue edit <n> --add-label <new> --remove-label <old>`, because `--add-label` alone keeps the
  old status and the issue then has two.
- If the issue belongs to an epic or a feature: put `Part of #<parent>` as the first line of the body,
  add it as a sub-issue of that parent, and add it to the task list of the parent (`/epic` does this).
- Before creating, check for a duplicate: `gh issue list --state all --search "<key words>"`.

## 4. Create, and close what is done

```sh
gh issue create --title "<title>" --body-file <file.md> --label "<type>" --label "<area>"
```

Write the body to a file in the scratchpad directory and pass `--body-file`; never inline a long
body in the shell. For work that reaches the default branch, close it with the evidence.
If the work is only on another branch, keep the issue open. If the repository uses `status:` labels,
set `status:fixed-on-review-branch` in place of the old status. The close command applies only after
that work reaches the default branch:

```sh
gh issue close <number> --reason completed --comment "Done in <commit>. <one line of what was measured>."
```

Report back: the number, the URL, the labels, and open or closed. If creation was refused or
failed, say so with the error; do not retry through another route.

## 5. Defects found during other work

Use the `/fix-defect` skill. It gives the issue form from `ephico2real2/cmapi`, the research mandate, the comment on the parent, and the rule that gaps and owner prerequisites are also filed. For a defect, its form replaces the shape in section 2.

## Anti-patterns

| Don't | Do |
|---|---|
| "Improve the chart" | "Remove the tunnel from the node on helm uninstall" |
| Acceptance criteria that restate the title | Criteria with the command that proves them |
| Ticking boxes for work that was not tested | Leave the box open and say what is missing |
| Pasting logs with tokens, keys or names | Quote the line that matters, redacted |
| One issue for five outcomes | Five issues under one epic |
| Creating without showing the draft | Draft, confirm, create (unless already told to create) |
