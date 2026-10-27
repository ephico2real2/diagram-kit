# Contributing

Enhancements belong here, in this repository, so that every project using the kit gets them. If you change the kit
for your own use, please send the change back as a pull request, even a small one.

## What the licence asks, and what we ask

- **The licence (MPL-2.0).** If you distribute a changed copy of any MPL-covered file (the renderer, the tests, the
  documents), you must make that file's source available under the MPL 2.0, and keep the copyright and licence
  notices. Files you add beside the kit stay yours, under any licence.
- **Our request, beyond the licence.** Open a pull request with the change, so it is reviewed once and merged for
  everyone, rather than kept in a fork. A licence cannot require this: a requirement to send changes to the
  original author would make the kit non-free ("desert island test").
- **Credit.** Keep `NOTICE`, and cite the kit as `diagram-kit (https://github.com/ephico2real2/diagram-kit), MPL-2.0`
  where you describe how your figures are made.

By opening a pull request you agree that your contribution is licensed under the same licence as the file it
changes: MPL-2.0, or MIT-0 for `diagram_kit/template.html` and `examples/`.

## What a pull request carries

- A test that fails before the change and passes after (`tests/`; no test reaches the network).
- `python -m pytest tests -q` green, and the template and every example rendering with exit 0.
- `STANDARD.md` updated when a rule or a check changes, and `RESEARCH.md` when a measurement backs it.

## Running CI in your fork

GitHub turns workflows off in a new fork, so CI does not run there until you turn it on. The first step is a
button in the browser; GitHub has no API or `gh` command for it. Replace `<you>` with your GitHub login and `<n>`
with the pull request number.

1. **Read what will start on its own.** Turning workflows on turns on every one of them. Check each trigger
   (`on:`) and the secrets it uses before you enable them:
   ```sh
   grep -A6 '^on:' .github/workflows/*.yml
   ```
2. **Turn workflows on.** Open `https://github.com/<you>/diagram-kit/actions` and click
   **I understand my workflows, go ahead and enable them**.
3. **Check that they are registered.**
   ```sh
   gh workflow list --all --repo <you>/diagram-kit
   ```
   `CI` must show `active`. If it shows `disabled_manually`, enable it:
   ```sh
   gh workflow enable ci.yml --repo <you>/diagram-kit
   ```
   A workflow in the `disabled_fork` state is one GitHub keeps off in forks. Leave it off unless you need it.
4. **Run CI on a pull request opened before step 2.** That pull request has no run yet. Close and reopen it to
   send a new `pull_request` event:
   ```sh
   gh pr close <n> --repo <you>/diagram-kit && gh pr reopen <n> --repo <you>/diagram-kit
   ```
5. **Watch the checks.**
   ```sh
   gh pr checks <n> --repo <you>/diagram-kit --watch
   ```

The same steps work for any fork: replace `diagram-kit` with the repository's name.
