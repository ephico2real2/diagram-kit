# Issue bodies for gh issue create

Copy the section of the item into a file, fill it, and pass the file with `--body-file`. The first line names the parent. The sections match the issue forms in `ISSUE_TEMPLATE/`, so an issue from the command line and an issue from the browser look the same.

## Epic

```markdown
Part of #<parent, or None yet>

## Goal
What is true when this is finished, and for whom.

## Business value
What the work gives the business, in plain words.

## Why
The problem or the risk today, with where it was seen.

## Scope
-

## Out of scope
-

## Issues
- [ ] #<child>

## Risks and open questions
-

## Exit criteria
- [ ] <the statement>, checked by <the command or the test>
```

## Feature

```markdown
Part of #<epic>

## Capability
Who gets what, and why it matters.

## Business value
What the work gives the business, in plain words.

## Context
What exists today, with the file, the commit or the measurement.

## Acceptance criteria
- [ ] <criterion>, shown by <the test>

## Stories and tasks
- [ ] #<child>

## Out of scope
-

## Class
INV, TDT, both, or no class.
```

## Story

```markdown
Part of #<feature or epic>

## Story
As a <role>, I want <result>, so that <reason>.

## Business value
What the work gives the business, in plain words.

## Context
What is true today, with the file or the measurement.

## Acceptance criteria
- [ ] <criterion>, shown by <the test>

## Tasks
- [ ] <step>

## Out of scope
-

## Evidence
-

## Definition of done
- [ ] Mockup approved, or the work has no screen and no API shape
- [ ] Draft pull request open
- [ ] Build: tests fail before the change and pass after it
- [ ] Documented where a reader looks for it
- [ ] Review ruled
- [ ] Merged with its proof
- [ ] Released on the default branch

## Class
INV, TDT, both, or no class.
```

## Task

```markdown
Part of #<parent>

## Why

## Tasks
- [ ] <step>

## Definition of done
- [ ] <check>

## Class
INV, TDT, both, or no class.
```

## Spike

```markdown
Part of #<parent>

## Question
The one question that this spike answers.

## Options
- <option>, with its source

## How the answer is measured
The test, the data and the limit of time.

## Decision
Written at the end: the choice, the measurements and the sources.
```

## Defect

`/fix-defect` gives the rules. The title starts with the ID, for example `BUG-12: <what is wrong>`.

```markdown
Part of #<the issue under which it was found>

**What is wrong:** the behavior, in plain words.

**Where:** `file:line`, on the commit or pull request.

**How to prove it:** a command or test that fails today.

**Measured or inferred:** which, and from which environment.

**Severity:** Critical, High, Medium or Low. Add the same `sev:` label.

**What must hold after the fix:**

**Research:** primary sources, the options, the choice and why.

**Solution (inline, not applied):**

**Class:** INV if the fix adds a control or a method, or if the defect is in new work. TDT if the cause is debt. Both can apply. No class only if the fix restores existing behavior and adds nothing.
```

## Owner action

The title starts with the ID, for example `OA-07: <the decision or the task>`.

```markdown
Part of #<parent>

## What the owner must do

## Why code cannot do it

## What waits for it
The issues and the milestone that wait.

## Recommendation
The option that the review recommends, with its source.
```
