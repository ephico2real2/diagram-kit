---
name: pull-request
description: "The standard pull request. Its sample template names the milestone, the issues, the class (INV, TDT or none) and the proof. It also names the schema and configuration changes, and has a checklist for each target branch. The skill gives the rules to open, check and merge a pull request with gh. It also says how to set the status of each issue after the merge. Use when the user types /pull-request. Also use it for a pull request template, a PR checklist, and how to open or merge a pull request in the project flow. It follows the legend and the records of /agile."
---

# /pull-request: each change goes in with its record

A pull request is the record of one change. It names what ships it (the milestone), why (the issues), what kind of work it is (the class), and how it was proven. `templates/pull_request_template.md` is the sample. `/agile` gives the legend and the issue records that the pull request refers to.

## 1. Add the template to a repository

1. Copy `templates/pull_request_template.md` to `.github/pull_request_template.md`.
2. Replace `<integration branch>`, `<staging branch>`, `<default branch>` and the names of the deploy workflows with those of the repository. If the repository has no staging branch, remove that part.
3. Keep each heading. A part that does not apply says "Does not apply".
4. Open the change itself through a pull request.

## 2. Open a pull request

From the command line, fill a copy and pass it with `--body-file`. For an interactive draft, `gh pr create --template <file>` uses a template.

```sh
git switch -c work/<topic>
# commit the change, then:
body=$(mktemp) && cp .github/pull_request_template.md "$body"     # fill each part
git push -u origin work/<topic>
gh pr create --base <integration branch> --title "<what changes>" --body-file "$body" \
  --milestone "<milestone title>" --label <type label> --label class:INV
```

- The title says what changes, in the imperative.
- `--milestone` is the release that ships the change. Each issue in `Closes #` has the same milestone.
- `--label` gives the type label of the work, for example `feature`, `story`, `task`, `bug` or `documentation`. Add each class label that the Class part selects. A change with no class gets no class label.
- The proof part holds the commands and their output, and a test that fails before the change and passes after it.

## 3. Merge, and then set the status

1. Merge only after CI passes and each box of the part for the target branch is ticked.
2. `Closes #` closes an issue only on a merge to the default branch. After a merge to another branch, read the current status label of each fixed issue. Use that label for `<old status>` in this command:

   ```sh
   gh issue edit <n> --add-label status:fixed-on-review-branch --remove-label "<old status>"
   ```

3. Update the build tracker in the same pull request as the work. If the merge changed a status, update it in the next pull request.
4. A merge to a deploy branch needs the owner. An agent does not merge to it.

## 4. Rules

- Each change goes from a working branch `work/<topic>` through a pull request. Nobody pushes to the integration, staging or default branch.
- One pull request has one purpose. A refactor and a fix go in separate pull requests.
- The class of the pull request matches the class labels of its issues. If they differ, correct the issue first.
- A pull request with a schema change names the migration, and a pull request with a new configuration value names each value.
- The commit attribution follows the rules of the person who owns the work.

## Anti-patterns

| Do not | Do |
|---|---|
| Open a pull request with an empty template | Fill each part, or write "Does not apply" |
| Use `Closes #` and expect a close on a review branch | Set the status label by hand after the merge |
| Merge before CI passes | Wait for each check |
| Leave the milestone empty | Name the release that ships the change |
