---
name: build-tracker
description: "Own the progress of a topic: a feature, story, issue or release. Each topic has one tracker file at claude-resumes/TRACKER-<topic>.md. It lists each unit of work with its SDLC phase and its status: todo, in progress, blocked or done. A done unit has its evidence (commit SHA, pull request, test or CI result, deploy) and a UTC time from git, CI or a log. Exactly one unit is in progress at a time, and it names its current step. For a project with a published tracker, it refreshes that file in the same change as the work. Use when the user types /build-tracker or asks for the status of the work. Also use it for each change of the status of a unit, and after a commit, a pull request, a CI run or a deploy. Use it after a failed tracker rule of the handover check."
---

# /build-tracker: the progress of a topic, with its evidence

This skill owns progress. The `handover` skill owns the current working state and the hooks, and `resume-work` owns
the restart. The three share the folder `claude-resumes/` (see `handover`, section 1).

## 1. The file

One tracker per topic, at `claude-resumes/TRACKER-<topic>.md`. The topic is the name in `claude-resumes/CURRENT`. The
handover self-check reads the units table, so keep its six columns exactly:

```markdown
# Tracker: <topic>

Goal: <one line>. Ticket: <link or number>. Published tracker: <path in the repository, or "none">.

| # | Unit | Phase | Status | Step or evidence | Updated (UTC) |
|---|---|---|---|---|---|
| 1 | Write the contract of the payment API | design | done | commit 3f2a9c1, PR #41, CI run 812 passed | 2026-11-07 20:14 (14:14 CST) |
| 2 | Build the client | build | in progress | step: the retry on 429, `src/client.ts` | 2026-11-07 21:02 |
| 3 | Review by a second model | review | blocked | waits for the owner: which provider sandbox | 2026-11-07 21:05 |
| 4 | Deploy to staging | deploy | todo | | |
```

- **Unit**: one piece of work that ends in something that can be shown: a merged change, a passed test, a deploy.
- **Phase**: one of the SDLC phases `plan`, `design`, `build`, `test`, `review`, `release`, `deploy`.
- **Status**: `todo`, `in progress`, `blocked` or `done`. Nothing else.
- **Step or evidence**: for `in progress`, the current step. For `blocked`, the blocker and who can remove it. For `done`, the evidence.
- **Updated (UTC)**: `YYYY-MM-DD HH:MM`, then the local time in parentheses, as `(HH:MM <zone>)`. Take the UTC time from git (`git log -1 --format=%cI`), CI (`gh run view <id> --json updatedAt`) or a log. Not from memory.

## 2. The rules

1. Exactly one unit is `in progress` while work goes on, and it names its current step. When the work stops, none is.
2. A `done` unit has evidence that someone can open: a commit SHA, a pull request or issue number, a CI run, a test result with its count, a deploy, or a URL. The self-check refuses a done row without one of these, or without a UTC time.
3. Update the tracker at the moment that a status changes. Then rewrite line 2 of the handover note (`handover`, section 3). If the tracker is newer than the note, the Stop hook blocks.
4. If new work appears, add a unit for it. For example, a review finds a defect. Never delete a unit: a dropped unit becomes `done` with the reason and the decision as its evidence.
5. A unit that waits for a person is `blocked`, and the `Open` section of the note names the question.

## 3. The published tracker

Some projects publish a tracker in the repository for people to read, for example a build tracker in the docs. The
file in `claude-resumes/` is the working source, and it changes at once. The published file changes with the work:

- Refresh it in the same commit as the work that changes a status, through the change flow of the project (branch, pull request, labels).
- If the project keeps the same file in more than one repository, copy it and compare the copies with `cmp`.
- Change its "state is from" time, and lint it with the rules of the project.

## 4. Report the status

When the user asks for the status, read the tracker, not the conversation. Give the counts by status, and the unit in
progress with its step. Give each blocked unit with its blocker, and the evidence of the units done since the last report.
