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
