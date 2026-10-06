# diagram-kit

One renderer, one template and one standard for the figures in our repositories.

Each diagram has a `source.html` page, started by `diagram-template` from the template the kit ships. `diagram-render`
turns every figure on it into a light and a dark PNG, and refuses the defects a review of the SVG text does not see:

- a fallback font;
- a label that runs past its box;
- a dashed arrow with no label beside it;
- text the reader cannot read in one of the two themes;
- a page that scrolls sideways on a phone.

| File | What it is |
|---|---|
| `diagram_kit/render.py` | the renderer (`diagram-render` once installed): PNGs plus the checks in `STANDARD.md` §5 |
| `diagram_kit/template.html` | the page every `source.html` starts from (`diagram-template <path>` writes it, never over an existing page): the palette, `.fig-scroll`, solid and dashed |
| `STANDARD.md` | when to use a page and when Mermaid, the page contract, embedding, the checks, review |
| `TUTORIAL.md` | install, a first figure, render, look, embed, review |
| `RESEARCH.md` | the measurements behind every check, and the prior art |
| `examples/fan-out/` | the connector kinds of `STANDARD.md` §3 on one page (curved fan-out, labelled dashed arrows), with its PNGs |
| `tests/` | one test per check, offline: a stand-in browser for the exit paths, real Chromium on local pages |

## Install and render

```sh
python3 -m venv .venv
.venv/bin/pip install "diagram-kit @ git+https://github.com/ephico2real2/diagram-kit@v0.1.0"
.venv/bin/playwright install chromium
.venv/bin/diagram-template docs/diagrams/<slug>/source.html
.venv/bin/diagram-render docs/diagrams/<slug>/source.html docs/diagrams/<slug> <name-1>,<name-2>
```

The repository is not published yet. Until it is, install from a local clone in place of the second line:
`.venv/bin/pip install <path-to-clone>`.
`TUTORIAL.md` walks the whole path.

## Why a kit

The renderer used to live in three copies with two behaviours. A fix made in one place (#342's failed-font check)
did not reach the others, and one vendored copy still lacks it
(group-sync-dashboard #436). Installing one pinned version replaces the copies.

## Tests

```sh
.venv/bin/pip install ".[test]"
.venv/bin/python -m pytest tests -q
```

No test reaches the network. The browser tests inline a font from `tests/fixtures/fonts/` (Inter, SIL Open Font
License 1.1, `tests/fixtures/fonts/OFL.txt`).

## Prior art

[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) (MIT, Cathryn Lavery) is the same
pattern: self-contained HTML and SVG pages, colour tokens, and a Playwright export. It was there first. This kit was
written independently, and keeps its own page format. From diagram-design it borrows:

- **measuring labels against their boxes.** Its `verify-geometry.py` checks label plates against nodes, and its
  `verify-treemap.py` estimates text width per em. Ours measures the drawn text in the browser;
- **WCAG contrast as a gate.** Its `verify-heatmap.py`, `verify-dumbbell.py` and onboarding rules check contrast;
  ours checks every figure text against the box under it, and the template's tokens;
- **an exactly pinned Playwright**, chosen deliberately, because the output is pixels.

`RESEARCH.md` §1 lists each of its checks and what was taken, adapted or left, and why.

## Licence

| What | Licence | What it means |
|---|---|---|
| the renderer, the tests, the documents | [MPL-2.0](LICENSE) | use it for anything, commercial included; keep the notices; a changed copy of a kit file you distribute stays open under the MPL |
| `diagram_kit/template.html`, `examples/` | [MIT-0](LICENSES/MIT-0.txt) | a page started from the template, and its PNGs, are yours with no obligation |

Credit the kit as `diagram-kit (https://github.com/ephico2real2/diagram-kit), MPL-2.0` and keep `NOTICE` with any
copy. Please send enhancements back as a pull request (`CONTRIBUTING.md`): the licence keeps changed kit files open,
and a pull request is how they reach every project that uses the kit.
