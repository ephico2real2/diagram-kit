---
name: epic
description: Write and create a GitHub epic (goal, scope, child issues as a tracked task list, risks, exit criteria) for the current repository and link its child issues, grounded in the actual code, commits and measurements. Use when the user types /epic, or asks for an epic, a breakdown of work into issues, or a backlog for a body of work, including work that is already done.
---

# /epic — a body of work, broken into issues that can each be closed

`/epic <the goal>` drafts the epic and the list of its child issues at once. An epic is an issue
with the label `epic` whose body tracks its children; each child is written with the `/issue`
skill's shape. Ask a question only when the goal itself is ambiguous.

Creating issues publishes them. **Show the epic and the list of children (titles, types, open or
done) and get a yes before creating anything**, unless the user has already said to create them.

## 1. Facts first

1. **Read the work.** The repository, its documents and its history (`git log --oneline`). For
   work that is already done, the children are what was actually built and measured, in the order
   it happened; for planned work, what is needed to reach the goal.
2. **Slice by outcome, not by file or by person.** Each child ends in something that can be
   demonstrated: a tunnel that carries traffic, a chart that installs, a guide a new engineer can
   follow. Five to twelve children is the usual size; more means two epics.
3. **Say what is done and what is not.** Close a child only after its work reaches the default
   branch, with its commits and measurements. Keep work on another branch open and name that branch.
   If the repository uses `status:` labels, give that work `status:fixed-on-review-branch`.
4. **No secrets, no personal data.** Same rule as `/issue`.

## 2. Shape of the epic

Title: the outcome, not the activity. `Encrypt NFS between OpenShift nodes and the NAS with IPsec`,
not `IPsec work`.

```markdown
## Goal
One paragraph: what will be true when this is finished, and for whom.

## Why
The problem or the risk today, with where it was seen.

## Scope
- What is included.

## Out of scope
- What is deliberately left out, and where it goes instead.

## Issues
- [ ] #<n> <title>
- [x] #<n> <title>

## Risks and open questions
- What could still go wrong, what is not tested, what needs a decision.

## Exit criteria
- [ ] The statements that must all be true to close the epic, each with how it is checked.
```

## 3. Create, in this order

1. Make sure the labels exist: `epic`, and the type labels `/issue` uses.
   `gh label create epic --color 5319e7 --description "A body of work tracked by child issues"`
2. Create the epic first, with the Issues section still listing the planned titles as plain text:
   `gh issue create --title "<title>" --body-file <epic.md> --label epic`
3. Create each child with the `/issue` shape, `Part of #<epic>` as its first line, and its labels.
   If the repository has milestones, give each child the milestone of the release that ships it;
   the epic itself gets no milestone when its children ship in different releases. If the
   repository has `status:` labels, each child has exactly one.
   Close only the children whose work reaches the default branch, with their evidence
   (`gh issue close <n> --reason completed --comment "…"`). Keep the other children open.
4. Rewrite the epic's Issues section as a task list of the real numbers, ticked where the child
   is closed: `gh issue edit <epic> --body-file <epic.md>`. GitHub then shows the progress.
5. Close the epic only when every exit criterion is met. If some children stay open, the epic
   stays open and its Risks section says why.

Write every body to a file in the scratchpad directory and use `--body-file`.

## 4. Report back

A table: number, title, type, state, URL; then the epic's URL and what is still open. If any
creation was refused or failed, say which one and stop there; do not retry through another route.

## Anti-patterns

| Don't | Do |
|---|---|
| An epic that is one big issue | A goal, plus children that each end in a demonstration |
| Children named after files or meetings | Children named after outcomes |
| Marking the epic done because the code is written | Exit criteria with how each was checked |
| Hiding what is not tested | A Risks section that lists it |
| Creating twenty issues without showing them | Show the list, confirm, create |
