---
name: agile
description: "The standard for agile records on GitHub. It says how milestones, epics, features, stories, tasks, spikes, defects and owner actions relate, and gives the issue form and the body of each. It says how to create each one with gh and the GitHub API, with its issue type and its parent. It maps each item to the legend: the ID prefix, the INV and TDT classes, the severity and one status label. Use when the user types /agile. Also use it for agile templates, a backlog structure, issue or milestone templates, and how issues, epics, features and milestones relate. /issue, /epic, /fix-defect and /pull-request follow it."
---

# /agile: one record from the idea to the release

`/agile` gives one structure for the work of a project on GitHub. Each item has a place, a template, a GitHub issue type, labels and a link to its parent. `LEGEND.md` beside this file is the standard legend. A client report, the Delivery Playbook and each issue use the same legend.

## 1. The items and how they relate

```text
Milestone      a release train: what ships together, with a purpose, a date and a rollback
               (each issue names the one milestone that ships it; a milestone is not a parent)

Epic           a goal with exit criteria                                   label: epic
  Feature      a capability that a user sees               type: Feature   label: feature
    Story      one slice of the feature for one role       type: Feature   label: story
    Task       one job with no user story                  type: Task      label: task
    Spike      a time-boxed question with a measured answer type: Task     label: spike
  Defect       a fault, a failed test or a proof gap       type: Bug       label: bug
  Owner action work that needs an account, a key or a decision  type: Task  label: task
```

- The parent link is a GitHub sub-issue. The first line of the body also says `Part of #<parent>`, because an export or a search shows text, not the link.
- A milestone names what ships. It is never the parent of an issue. An epic can span milestones, and each child has exactly one milestone.
- A feature is optional. A small epic holds its stories directly.
- A defect found under an issue becomes a sub-issue of that issue. `/fix-defect` gives its form.
- A sub-issue and its parent have the same owner. A parent in another repository of the same owner is permitted.

## 2. Map each item to the legend

| Item | Issue type | Type label | ID in the title | Class labels | Severity | Status label |
|---|---|---|---|---|---|---|
| Epic | `Epic` where the organization has it, otherwise none | `epic` | None | None | None | One |
| Feature | `Feature` | `feature` | The finding ID, or `INV-nn` | `class:INV`, and `class:TDT` for paid-back debt | None | One |
| Story | `Feature` | `story` | The finding ID, `INV-nn`, `TDT-nn`, or none | As the work | None | One |
| Task | `Task` | `task` | The finding ID, `TDT-nn`, or none | As the work | None | One |
| Spike | `Task` | `spike` | None | As the work | None | One |
| Defect | `Bug` | `bug` | `SEC`, `BUG`, `PERF` or `UX` | As the work, including inherited classes | One `sev:` label | One |
| Owner action | `Task` | `task` | `OA-nn` | None | None | `status:owner-action` |
| Milestone | Not an issue | None | A short code, for example `B1` | None | None | Open or closed |

Rules for the legend:

- An ID never changes after it is filed, because commits, pull requests and documents refer to it. To correct a category, add a class label or a note. Do not rename the ID.
- Take the next free number of the prefix from the issue list. Never reuse a number.
- An `INV` or `TDT` ID is only for work that comes from no finding. A finding keeps its own prefix and gets a class label.
- Each issue has exactly one `status:` label. Change it with `--add-label` and `--remove-label` in one command.

Decide the class with these questions, in this order:

1. Does the work add something new to the product or the delivery? Examples are a feature, a service, a security control, a test method and a CI/CD gate. Then it is `INV`.
2. Does the work pay back an earlier shortcut in code or a setup that works today? Examples are an old dependency, a weak test, a hand step, dead code or a document that drifted. Then it is `TDT`.
3. If both answers are yes, it has both labels. If both are no, it has no class label. If the fix of a defect brings existing behavior back to its intended form and adds nothing, the defect has no class. If the fix adds a new control, such as a webhook signature, a second factor, an allow-list or a scan, the defect is `INV`. A defect in new `INV` work that is not merged yet is also `INV`, because its fix is part of that work. A defect in an unmerged fix that has no class keeps no class. Owner actions, epics and milestones have no class.

## 3. Templates

| File | Use |
|---|---|
| `LEGEND.md` | The standard legend: prefixes, classes, severity, status, verdicts and figure elements |
| `templates/ISSUE_TEMPLATE/*.yml` | GitHub issue forms for each item. Copy them into `.github/ISSUE_TEMPLATE/` of a repository |
| `templates/bodies.md` | The body of each item, for `gh issue create --body-file` |
| `templates/milestone.md` | The description of a milestone |

Each form sets its type label and one status label. The owner action form sets `status:owner-action`. The other forms set `status:open`. The Epic form omits `type`, because an organization can lack that type. The other forms use the top-level `type` key.

A form cannot set a milestone or a parent. Each form asks for a parent. Forms for work that ships also ask for a milestone. The filer sets those values after creation. In a client copy, replace the milestone options with the milestones of the client.

## 4. Create the records, in this order

Write each body to a file and use `--body-file`. Never put a long body inline in the shell.

1. Create the labels once for each repository. If a label exists, `gh label create` fails with a clear message and changes nothing.

   ```sh
   gh label create epic                --color 5319e7 --description "A body of work tracked by child issues"
   gh label create feature             --color 0e8a16 --description "A capability that a user sees"
   gh label create story               --color 1d76db --description "One slice of a feature for one role"
   gh label create task                --color fbca04 --description "A unit of work with no user story"
   gh label create spike               --color c2e0c6 --description "A time-boxed question with a measured answer"
   gh label create bug                 --color d73a4a --description "A fault, a failed test or a proof gap"
   gh label create class:INV           --color 1d76db --description "Innovation: a new feature, design, idea or method"
   gh label create class:TDT           --color c5a3ff --description "Tech debt: works today, but costs more to change, operate or upgrade"
   gh label create status:open         --color ededed --description "No fix yet"
   gh label create status:owner-action --color d93f0b --description "Waits for the owner"
   ```

   Add the other `status:` and `sev:` labels of `LEGEND.md` the same way.

2. Create the milestone, with the description from `templates/milestone.md`:

   ```sh
   gh api repos/<owner>/<repo>/milestones -f title="<code>: <what ships>" -F description=@milestone.md -f due_on=<YYYY-MM-DDT00:00:00Z>
   ```

3. Create the epic, then each feature, then each story, task or spike. Each child gets its milestone:

   ```sh
   gh issue create --title "<title>" --body-file story.md --label story --label status:open --milestone "<milestone title>"
   ```

4. Set the issue type and the parent. The GraphQL schema has `updateIssueIssueType(issueId, issueTypeId)` and `addSubIssue(issueId, subIssueId, replaceParent)`. Both take node IDs, not issue numbers:

   ```sh
   q='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){issue(number:$n){id} issueTypes(first:20){nodes{id name}}}}'
   gh api graphql -f query="$q" -f o=<owner> -f r=<repo> -F n=<child number>    # the child id and the type ids
   gh api graphql -f query='mutation($i:ID!,$t:ID!){updateIssueIssueType(input:{issueId:$i,issueTypeId:$t}){issue{number issueType{name}}}}' -f i=<child id> -f t=<type id>
   gh api graphql -f query='mutation($p:ID!,$c:ID!){addSubIssue(input:{issueId:$p,subIssueId:$c}){issue{number}}}' -f p=<parent id> -f c=<child id>
   ```

   A repository of a personal account has no issue types. Then the type label carries the type.

5. Update the task list of the epic with the real numbers, and tick each closed child.
6. Add the new items to the build tracker of the project in the same change.

## 5. Waves, stages and the timeline

A milestone says what ships. A wave gives the dates of the work on it. A stage says how far each item is.

- Each milestone has a due date: the date that it ships. Its open and closed counts show its progress.
- One GitHub Project holds the items of all repositories of the product. Its iteration field `Wave` holds the waves, each with a start date and a length. Each item gets one wave.
- Its single-select field `Stage` shows how far each item is. Each stage has an exit rule:

| Stage | Exit rule |
|---|---|
| Mockup | The owner approves the mockup (`/build-mockup`). Work with no screen and no API shape starts at Draft |
| Draft | A draft pull request holds the design or the first code |
| Build | The tests that fail before the change pass after it |
| Review | The reviewers report, and the arbiter rules on each finding |
| Merged | The pull request is merged into the integration branch, with its proof |
| Released | The change is on the default branch, and the issue is closed |

- The `status:` labels stay on each defect. `status:open` covers Mockup to Review, `status:fixed-on-review-branch` is Merged, and a closed issue is Released.
- The Project has 3 views: a board by Stage, a table by Wave, and a roadmap by Wave with the milestone dates.

Create the Project and its fields. `gh project field-create` has no iteration type, so the iteration field comes from the GraphQL mutation `createProjectV2Field`:

```sh
gh project create --owner <owner> --title "<product> delivery"
gh project field-create <number> --owner <owner> --name Stage --data-type SINGLE_SELECT \
  --single-select-options "Mockup,Draft,Build,Review,Merged,Released"
pid=$(gh project view <number> --owner <owner> --format json --jq .id)
gh api graphql -f query='mutation($p:ID!){createProjectV2Field(input:{projectId:$p,dataType:ITERATION,name:"Wave",
  iterationConfiguration:{startDate:"<YYYY-MM-DD>",duration:14,iterations:[{title:"W1",startDate:"<YYYY-MM-DD>",duration:14}]}})
  {projectV2Field{... on ProjectV2IterationField{id name}}}}' -f p="$pid"
gh project item-add <number> --owner <owner> --url <issue URL>
gh api -X PATCH repos/<owner>/<repo>/milestones/<milestone number> -f due_on=<YYYY-MM-DDT00:00:00Z>
```

The token needs the `project` scope: `gh auth refresh -s project`. Dates come from the owner. Do not invent a due date or a wave length.

## 6. Keep the records true

- A pull request names its milestone, its issues, its class and its type label. `/pull-request` gives the template.
- After a merge to a branch that is not the default branch, `Closes #` closes nothing. Set the status label by hand.
- Close an issue only through a merged fix on the default branch, with the proof cited.
- Sweep the classes of all issues, not only the new ones. Do it at the first classification, after each change of the class rule, and before each tracker update. List each issue with no class label, read its fix, and add the class that the questions of section 2 give. Report the count: the issues read, the classes added and the issues that keep no class. Record the reason for each issue, also for each issue that keeps no class, so that the next sweep starts from the record.

  ```sh
  gh issue list --state all --limit 500 --json number,title,labels \
    --jq '.[] | select([.labels[].name | select(startswith("class:"))] | length == 0) | "\(.number) \(.title)"'
  ```

  On 2026-11-07, a narrow reading of question 1 left 102 issues of one client with no `INV` label. They held security controls, emulator tests, CI/CD gates and admin portal features. A sweep of all issues found them.
- Count the issues with more than one status label after each change of status:

  ```sh
  gh issue list --state all --limit 500 --json number,labels \
    --jq '[.[] | select(([.labels[].name | select(startswith("status:"))] | length) > 1) | .number]'
  ```

## 7. Show the class of each issue

Each report and each build tracker shows the class of all issues, by category. The table shows the result of the sweep of section 6 to the owner and to the client. In a report, put it in the summary, under the table of findings by severity.

- The columns do not overlap: `INV only`, `TDT only`, `Both`, `No class`, then `Total`. Each row adds up to its total.
- There is one row for each prefix of the legend, in the order of the legend, then "Other work" and "Total". "Other work" is a story, a task, a spike or an epic with no finding ID. A prefix with no issue gets no row.
- The table counts all issues of all repositories, open and closed. Its totals can differ from a table of findings, so say so under the table.
- Give the date and the time of the read. Under the table, give the number of `INV` issues and `TDT` issues, and the kinds of issues with no class.
- Make the table again after each sweep, in the same commit as the tracker.

Replace the repositories in the first line, then paste the output into the document:

```sh
for r in <owner>/<repository-1> <owner>/<repository-2>; do
  gh issue list -R "$r" --state all --limit 1000 --json title,labels
done | jq -rs '
  def order: ["SEC", "BUG", "PERF", "BP", "UX", "OA", "INV", "TDT", "Other work"];
  def category: (.title | capture("^(?<p>SEC|BUG|PERF|BP|UX|OA|INV|TDT)-[0-9]+").p) // "Other work";
  def classes: [.labels[].name | select(. == "class:INV" or . == "class:TDT")] | sort;
  def row($name; $items): [$name,
    ($items | map(select(classes == ["class:INV"])) | length),
    ($items | map(select(classes == ["class:TDT"])) | length),
    ($items | map(select(classes == ["class:INV", "class:TDT"])) | length),
    ($items | map(select(classes == [])) | length),
    ($items | length)];
  add as $all
  | (["Category", "INV only", "TDT only", "Both", "No class", "Total"], ["---", "---", "---", "---", "---", "---"],
     (order[] as $c | row($c; $all | map(select(category == $c))) | select(.[5] > 0)), row("Total"; $all))
  | "| " + (map(tostring) | join(" | ")) + " |"'
```

### Highlight the innovations

A report for a client is also a business document, so it shows the innovations of the work, built and proposed. In the summary, under the class table, add two tables:

1. A table of themes. Put each `INV` issue in one business theme, such as new services, the admin portal, security controls, test methods or CI/CD. Count its state from its status label: Built (`status:fixed-on-review-branch`), Partly built (`status:partly-fixed`), Proposed (`status:open`, or no status label) and Owner decision (`status:owner-action`). Each issue is in exactly one theme, and the total equals the number of `INV` issues.
2. A table of the main innovations, with the columns Innovation, What it gives the business, State and Where. Take the business result from the Business value field of the issue, in plain words, not the code change. Name the issue numbers, the design or the proof branch of each row.

A proposed innovation is never shown as built. If an innovation has a design but no issue yet, say so in its row. This command lists each `INV` issue with its status, to start the themes:

```sh
gh issue list -R <owner>/<repository> --state all --limit 1000 --json number,title,labels \
  --jq '.[] | select([.labels[].name] | index("class:INV")) | "\(.number) [\([.labels[].name | select(startswith("status:"))] | join(","))] \(.title)"'
```

## 8. Show progress to the client: work tags and deploy tags

A client sees the work in the issues, so the issues stay open until the default branch. When the owner says that an issue is closed, it means that the issue has the `Done` label. It does not mean a closed GitHub issue. Report progress by the count of `Done` labels, never by the count of closed issues.

The labels of `LEGEND.md` show how far each issue is, in two kinds:

- Work tags: `Backlog`, `In-Progress`, `Blocked`, `In-QA` and `Done`. Each open issue has exactly one. An issue with no work tag is an error, not a state, so a check can find a missed update.
- Deploy tags: `Local-Deploy`, `Sbx-Deploy` and `Go-Live`. They come after `Done`. An issue has at most one, the furthest environment that the change reached, and only when its work tag is `Done`. A closed issue with `Go-Live` needs no work tag.

Each label except `Backlog` comes with one comment that gives the evidence. `Backlog` has no comment, because it has no evidence to give. Create the labels once in each repository:

```sh
gh label create Backlog     --color c5def5 --description "Not started: the work waits in the backlog"
gh label create Done        --color 0e8a16 --description "Work merged into the integration branch; the comment gives the pull request, the merge and the proof"
gh label create In-Progress --color fbca04 --description "Work started and not complete; the comment gives the pull request or the job"
gh label create Blocked     --color b60205 --description "Work cannot continue; the comment names the blocker and what unblocks it"
gh label create In-QA        --color d4c5f9 --description "Pull request open to the integration branch: review rounds, ruling and CI running"
gh label create Local-Deploy --color bfdadc --description "Done, and passed a walk on the local deploy, with screenshots"
gh label create Sbx-Deploy   --color 5ebeff --description "Done, and running on the sandbox; a deploy log or the owner's word is the evidence"
gh label create Go-Live      --color 0e8a16 --description "Running in production from the default branch; the issue closes"
```

Give each open issue its label by these rules, in this order. The first rule that matches gives the label.

1. Blocked: the issue waits for the owner (`status:owner-action`), or the owner named its blocker.
2. Done: the issue has `status:fixed-on-review-branch`, and evidence is found. Look for the evidence in this order. First, a merged pull request that closes it, or a fix commit in the catalogue. Then a merged pull request or a commit on the integration branch that names it. If no evidence is found, the issue keeps its earlier label, and you find the evidence by hand.
3. In-QA: an open pull request that is ready for review closes the issue. The review rounds, the ruling and CI run before the merge.
4. In-Progress: a draft pull request closes the issue, or an open pull request carries part of it (`Part of #N`). A build job for it, a merged part, or `status:partly-fixed` also gives In-Progress.
5. Blocked: GitHub lists an open issue that blocks it, and no rule above matched.
6. Backlog: the work has not started. When you file a new issue, give it `Backlog`.

Give a deploy tag only with evidence, by hand:

1. Local-Deploy: the change runs on the local deploy, and a walk through it passed: device tests for a mobile app, browser tests for a portal, or the owner's own test. The evidence is the run and its screenshots, each marked as taken on the local deploy.
2. Sbx-Deploy: the change runs on the sandbox. The evidence is a deploy log, a CI run or the owner's word. Do not call the sandbox to prove it unless the owner allows it.
3. Go-Live: the change runs in production from the default branch. Close the GitHub issue at this point, and only at this point.

If a walk or a test on an environment fails, file the defect, remove the deploy tag, and move the issue back to In-Progress.

An epic takes its label from its children. If each child is Done, the epic is Done. If at least one child is Done, In-QA or In-Progress, the epic is In-Progress. Otherwise the epic is Backlog. A new child of a Done epic moves the epic back to In-Progress.

Rules for the labels and the comments:

- Make a dry run first. Show the owner the counts by repository and by reason, and sample comments, before any label or comment reaches the client.
- Each comment says why the label applies and gives each pull request with its merge commit, each commit, or each blocker. A Blocked comment names the blocker and what unblocks it.
- Read every time in a comment from the clock, git or CI. Never write a time from memory.
- Apply in a way that a second run is safe: add the label, remove the other labels of its kind, and skip a comment that is already posted.
- Never move an issue back to an earlier label without evidence. A rerun that proposes Backlog for an issue with another work tag keeps the tag it has. The only move back is a failed test, with its defect filed.
- After each change, count the open issues that do not have exactly one work tag, and the issues with a deploy tag that are not Done, other than a closed issue with `Go-Live`. Both counts must be 0.
- Keep the GitHub dependencies true. Read them with `blockedBy` and `blocking`. If a link no longer blocks the work, remove it with the owner's yes, and say why in a comment.

  ```sh
  gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){issue(number:$n){id
    blockedBy(first:20){nodes{number state repository{name}}} blocking(first:20){nodes{number state repository{name}}}}}}' \
    -f o=<owner> -f r=<repo> -F n=<number>
  gh api graphql -f query='mutation($i:ID!,$b:ID!){addBlockedBy(input:{issueId:$i,blockingIssueId:$b}){issue{number}}}' -f i=<issue id> -f b=<blocker id>
  gh api graphql -f query='mutation($i:ID!,$b:ID!){removeBlockedBy(input:{issueId:$i,blockingIssueId:$b}){issue{number}}}' -f i=<issue id> -f b=<blocker id>
  gh issue list --state all --limit 1000 --json number,labels,state \
    --jq '[.[] | select(.state == "OPEN") | select(([.labels[].name | select(IN("Backlog", "In-Progress", "Blocked", "In-QA", "Done"))] | length) != 1) | .number]'
  gh issue list --state all --limit 1000 --json number,labels,state \
    --jq '[.[] | select(([.labels[].name] | any(IN("Local-Deploy", "Sbx-Deploy", "Go-Live"))) and (([.labels[].name] | index("Done")) | not) and ((.state == "CLOSED" and ([.labels[].name] | index("Go-Live"))) | not)) | .number]'
  ```

- Update the labels after each merge, each new pull request and each owner decision, in the same work as the change. The build tracker shows a progress table by repository and a Blocked section with each blocker and what unblocks it.

## Anti-patterns

| Do not | Do |
|---|---|
| Use a milestone for a theme | A theme is a label. A body of work is an epic |
| Rename an ID to correct its category | Add a class label or a note |
| Leave the parent only in the text | Add the sub-issue link, and keep `Part of #` |
| Add a second status label | Replace the status in one command |
| File a feature with no acceptance criteria | Each criterion says how a test shows it |
| Give a defect no class by default | Read its fix. A new control, test method or gate is `INV` |
| Classify only the new issues | Sweep the classes of all issues after each change of the rule |
| Close an issue to show the client that it is done | Keep it open until the default branch, and add `Done` with its evidence |
| Tag an issue Done with no evidence | Find the pull request or the commit first, or keep its earlier label |
| Leave an open issue with no progress label | When you file an issue, give it `Backlog` |
| Count closed issues as the progress | Count the `Done` labels |
| Call merged work tested on a deployed stack | Add `Local-Deploy` only after a walk on the local deploy passed, with its screenshots |
| Keep a blocker link after the work moved on | Remove it with the owner's yes, and say why in a comment |
