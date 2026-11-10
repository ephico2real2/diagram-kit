# Legend

This is the standard legend. Each report, issue, pull request, tracker and figure uses it. A client report opens with it. Do not change a client copy. Change this file through a pull request, and then each copy.

## ID prefixes

Each finding ID has a prefix and a number, for example `SEC-01`. The prefix gives the category. The number does not give an order of priority. An ID never changes after it is filed.

| Prefix | Category | Meaning |
|---|---|---|
| `SEC` | Security | A person can get data, money or access that they must not have |
| `BUG` | Bug | The code gives an incorrect result |
| `PERF` | Performance | Speed, capacity, scaling or measurement of the service |
| `BP` | Best practice | A gap in how the team builds, tests, deploys or operates the code |
| `UX` | User experience | A defect that a user sees on the screen |
| `OA` | Owner action | Work that needs an account, a key, a plan or a decision that code cannot supply |
| `INV` | Innovation | A new feature, design, idea or method that comes from no finding |
| `TDT` | Tech debt | A debt item that comes from no finding |

## Classes

A class says what kind of work an item is. Each item of any prefix can have one class, both classes or no class. The GitHub label carries the class.

| Class | Label | Meaning |
|---|---|---|
| `INV` | `class:INV` | Innovation: the work adds something new to the product or the delivery. Examples are a feature, a service, a security control, a test method and a CI/CD gate |
| `TDT` | `class:TDT` | Tech debt: the code or the setup works today, but an earlier shortcut makes it cost more to change, operate or upgrade |

If the fix of a defect brings existing behavior back to its intended form and adds nothing, the defect has no class. If the fix adds a new control, such as a webhook signature, a second factor, an allow-list or a scan, the defect is `INV`. A defect in new `INV` work that is not merged yet is also `INV`, because its fix is part of that work. A defect in an unmerged fix that has no class keeps no class. Sweep the classes of all issues at the first classification and after each change of this rule, not only the classes of new issues. A finding keeps its prefix and gets a class label. Only work that comes from no finding gets an `INV` or `TDT` ID.

## Severity

A defect has one `sev:` label.

| Severity | Label | Meaning |
|---|---|---|
| Critical | `sev:critical` | A person with no special access can get money, data or control of a server now |
| High | `sev:high` | If a condition occurs, for example a race or a stolen token, a person can get money, data or access |
| Medium | `sev:medium` | Incorrect data, a weak control or a slow service, with no direct loss |
| Low | `sev:low` | A small defect, a defect that no code path reaches yet, or a cleanup |

## Status

An open issue has exactly one `status:` label.

| Status | Label | Meaning |
|---|---|---|
| Open | `status:open` | No fix yet. A story describes the work |
| Partly fixed | `status:partly-fixed` | Part of the work is fixed. The rest is a story or an owner action |
| Fixed on the review branch | `status:fixed-on-review-branch` | The fix and its test are merged on a branch that is not the default branch. Nothing is deployed |
| Owner action | `status:owner-action` | The work waits for the owner |
| Closed | None: the issue is closed | The fix reached the default branch |

## Progress

The status label says where the fix is. The progress label tells a client how far the work is, while the issues stay open until the default branch. Each open issue has exactly one progress label. An open issue with no progress label is an error. When the owner says "closed", it means the `Done` label.

| Progress | Label | Meaning | The comment gives |
|---|---|---|---|
| Backlog | `Backlog` | The work has not started | No comment |
| Done | `Done` | The work is merged into the integration branch | The pull request and its merge commit, or the fix commit, with the proof |
| In progress | `In-Progress` | The work started and is not complete | The open or draft pull request, the merged parts, or the running build job |
| Blocked | `Blocked` | The work cannot continue | The issue or the owner decision that blocks it, and what unblocks it |

## Item types

| Item | GitHub issue type | Type label |
|---|---|---|
| Epic | `Epic` where the organization has it | `epic` |
| Feature | `Feature` | `feature` |
| Story | `Feature` | `story` |
| Task | `Task` | `task` |
| Spike | `Task` | `spike` |
| Defect | `Bug` | `bug` |
| Owner action | `Task` | `task` |

A milestone is a release train, not an issue. Its title starts with a short code, for example `B1`.

## Verdicts

An agent or a reviewer gives one verdict for each claim.

| Verdict | Meaning |
|---|---|
| CONFIRMED | A test supports the claim |
| REFUTED | A test shows that the claim is false |
| PLAUSIBLE | The evidence supports the claim, but no test proves it |
| NOT REACHED | No test is possible from where the agent operates |

## Figure elements

| Element | Meaning |
|---|---|
| Solid box | Operates today |
| Dashed box | Proposed, not built |
| Solid arrow | Traffic or a call |
| Dashed arrow with a label | A relationship with no traffic |
| Red | A failure, a refusal or a finding |
