# diagram-kit

One renderer, one template and one standard for the figures in our repositories; and, since 0.2.0, one standard and
two commands for their dashboards, the figures that move.

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
| `skill/visual/SKILL.md` | the `/visual` Claude Code skill that designs the pages; link `~/.claude/skills/visual` to this directory |
| `skill/dashboard/SKILL.md` | the `/dashboard` Claude Code skill: the dashboard standard, every rule with its source; link `~/.claude/skills/dashboard` to this directory |
| `skill/dashboard/COLLECTION.md` | how a workload's metrics get collected before any panel: an exporter of its own, ServiceMonitor or PodMonitor, a scrape over TLS |
| `diagram_kit/metrics.py` | `metrics-inventory`: every metric a workload emits, with the kind of data each is |
| `diagram_kit/perses.py` | `perses-dashboard`: the Perses form of a Grafana dashboard, and the checks the conversion needs |
| `STANDARD.md` | when to use a page and when Mermaid, the page contract, embedding, the checks, review |
| `TUTORIAL.md` | install, a first figure, render, look, embed, review |
| `RESEARCH.md` | the measurements behind every check, and the prior art |
| `examples/fan-out/` | the connector kinds of `STANDARD.md` §3 on one page (curved fan-out, labelled dashed arrows), with its PNGs |
| `examples/` | real pages and dashboards copied from the repositories they were made in, each with where it came from (`examples/README.md`): a rendered diagram page, and a Grafana dashboard with its Perses form |
| `tests/` | one test per check, offline: a stand-in browser for the exit paths, real Chromium on local pages |

## Install and render

```sh
python3 -m venv .venv
.venv/bin/pip install "diagram-kit @ git+https://github.com/ephico2real2/diagram-kit@v0.2.0"
.venv/bin/playwright install chromium
.venv/bin/diagram-template docs/diagrams/<slug>/source.html
.venv/bin/diagram-render docs/diagrams/<slug>/source.html docs/diagrams/<slug> <name-1>,<name-2>
```

The repository is not published yet. Until it is, install from a local clone in place of the second line:
`.venv/bin/pip install <path-to-clone>`.
`TUTORIAL.md` walks the whole path.

## Dashboards

A dashboard is a figure that moves, and it goes wrong the same way: built from memory, coloured by a palette nobody
chose, never looked at. `skill/dashboard/SKILL.md` is the standard, and two commands do the parts a person should not
do by hand:

```sh
# every metric a workload emits, with the kind of data each is: the list a dashboard is chosen from
.venv/bin/metrics-inventory --prometheus <url> --match '{namespace="app",job="app"}' > docs/metrics-inventory-app.md

# the Perses form of a Grafana dashboard, the Grafana JSON staying the only file edited (needs podman or docker)
.venv/bin/perses-dashboard dashboards/app.json dashboards/app.perses.json --datasource app-thanos
```

`metrics-inventory` reads a Prometheus-compatible API (a bearer token from the environment variable
`PROMETHEUS_TOKEN`, never from the command line) or a saved `/metrics` page (`--text`). `perses-dashboard` runs
`percli migrate` from the Perses image and refuses a panel that became a placeholder or a query that differs from
the source; it writes nothing when a check fails. `RESEARCH.md` §7 has what both were measured on.

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
License 1.1, `tests/fixtures/fonts/OFL.txt`). The dashboard tests run no container and ask no Prometheus: they use a
saved `percli` result (`tests/fixtures/dashboard/`) and an API answered from a table.

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
