<!-- Keep each heading. If a part does not apply, write "Does not apply". -->

## Release milestone or hotfix

Select a release milestone or a dedicated hotfix milestone. Set that milestone in the Milestone box of this pull request.

- [ ] Release milestone: <!-- the short code, for example R1 -->
- [ ] Hotfix milestone: <!-- the short code and why this cannot wait for the next scheduled release -->

## Issues

Closes #
Part of #

<!-- "Closes #" closes an issue only on a merge to the default branch. On another branch, set the status label by hand after the merge. -->

## Class

Select each that applies. Add the same `class:` labels to this pull request. They match the labels of its issues.

- [ ] INV: innovation. The change adds something new to the product or the delivery. Examples are a feature, a service, a security control, a test method and a CI/CD gate.
- [ ] TDT: tech debt. The change pays back an earlier shortcut in code or setup that works today.
- [ ] No class: the change only restores existing behavior and adds nothing, or it changes only records.

## What changes, and why

## Proof

<!-- The commands that you operated, and their output. A test that fails before the change and passes after it. -->

## Schema and configuration

- [ ] This change has no schema change, or the migration is named here:
- [ ] This change has no new configuration value, or each value is named here:

## Security and data

- [ ] This change adds no secret, no key and no personal data to the repository.
- [ ] This change sends no new data to a third party, or the data and the party are named here:

## Before the merge to the integration branch

Use this part for a pull request from a working branch to `<integration branch>`. This merge starts CI and no deploy.

- [ ] The base is `<integration branch>`, and the head is a working branch.
- [ ] The Milestone box names the release that ships this change. Each issue in `Closes #` has the same milestone.
- [ ] After the merge, each fixed issue has one status label: `status:fixed-on-review-branch`.
- [ ] The build tracker names the milestone, the class and the status of each issue.
- [ ] CI passes on this pull request.

## Before the merge to `<staging branch>`

A merge to `<staging branch>` starts `<staging deploy workflow>`.

- [ ] The description and the proof above are complete.
- [ ] The milestone, the type label and the class labels are correct.
- [ ] Tests are added, and they pass.
- [ ] All status checks pass.
- [ ] The documents and the build tracker are up to date.

## Before the merge to `<default branch>`

A merge to `<default branch>` starts `<production deploy workflow>`.

- [ ] Someone tested the change on the staging environment.
- [ ] The rollback is named here:
- [ ] The owner accepts the change.
- [ ] Someone reviewed the code at each stage, and all status checks pass.
