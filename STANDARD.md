# The diagram standard

How a figure is made, checked, embedded and reviewed across our repositories. Every rule here is either one the
repositories already follow, and cites where, or one a measured defect on our own figures added, and cites
`RESEARCH.md`. A rule with neither does not belong here.

Where this says "the skill", it means the `/visual` skill that generates the pages. It lives in this repository,
`skill/visual/SKILL.md`, and a Claude Code install links `~/.claude/skills/visual` to it. The kit's
`diagram_kit/template.html`, which `diagram-template` writes to a new page, started as a verbatim copy of the skill's
old `template.html`.

## 1. The core strategy: one generated `source.html` per diagram

Each diagram (one figure, or a set of figures for one document) has its own page, `docs/diagrams/<slug>/source.html`.
The page is **generated** for that diagram from `template.html`, then rendered by `render.py` into a light and a dark
PNG per figure, which are committed beside it. The page is the source; the PNGs are derived from it and are never
edited.

Every `source.html` figure in our repositories is made this way today:

| Repository | Pages | Where |
|---|---|---|
| `group-sync-dashboard` | 1 (4 figures) | `docs/diagrams/remote-cluster-access/source.html` |
| `openshift-ipsec-nas` | 5 (8 figures) | `docs/diagrams/{ipsec-nas,option-c,crc-nat,deploy-flow,lima-lab}/source.html` |
| `envoy-tutorial` | 23 on `main` (34 figures) | `docs/diagrams/<module>/source.html`, one per module |
| `envoy-grpc-modernization` | 1 (3 figures) | `docs/diagrams/modernize-architecture/source.html` |
| `mongodb-poc` | 6 (19 figures) | `docs/diagrams/<topic>/source.html` |

The template fixes the design that all of them share:

- one palette (measured: all 156 pages across these repositories and envoy-tutorial's six branches compute the
  same token values in both themes, see `RESEARCH.md` §2);
- `.fig-scroll` around each figure, so a phone scrolls the figure and never the page;
- solid boxes for shipped, dashed boxes for proposed;
- a light and a dark render of every figure.

## 2. A `source.html` page or a Mermaid block

Both are in use, for different jobs.

**Use a `source.html` page** when the figure has to carry any of these:

- a trust boundary drawn as lanes (HOST | REMOTE, cluster | NAS);
- shipped and proposed in one picture (solid and dashed boxes);
- failure branches in the gap colour, with the fix named;
- numbered steps;
- a picture that must look the same wherever the document is read.

The dashboard's remote-cluster-access figures (policies compared, the decision flow with every refusal), the
IPsec figures (the node, the NAS, the tunnel modes) and the envoy-tutorial module figures are all of this kind.

**Use a Mermaid block** for a flow, a sequence or an entity-relationship diagram taken from the code, in a Markdown
document that GitHub renders. The block is the source, and nothing is committed but the text:

- `group-sync-dashboard` has 31 blocks in 8 files: its reference architecture, designs and specs;
- its `docs/guides/TUTORIAL_mermaid_diagrams.md` is the method, and its required CI job `diagrams` renders every
  block with `@mermaid-js/mermaid-cli@11`;
- `cilium-implementation-poc` (4 blocks in 3 files) and `mongodb-poc` (2 in 2) use a few blocks the same way, and so
  does `rbac-kyverno-ideas` (3 in 1, per #436's inventory of 2026-10-06).

**Mermaid as PNGs.** Where the reader's surface renders no Mermaid (Confluence), `envoy-reference-architecture`
keeps `.mmd` sources and renders them to the PNGs its documents embed (`docs/diagrams/render.sh`). That script fetches
mermaid-cli unpinned. Re-rendered today with 12.0.0, all 5 PNGs differ from the committed ones, in size as well as
in pixels (`RESEARCH.md` §4). A repository that commits Mermaid PNGs pins mermaid-cli to one exact version, such as
`@mermaid-js/mermaid-cli@11.17.0`. A major tag is not a pin: the dashboard's `diagrams` job runs `@11`, which takes the
newest 11.x on each run (16 releases, 11.1.1 to 11.17.0, on 2026-10-06), and that is right for a job that only checks
that every block parses and commits nothing.

**Mermaid text twins.** `openshift-ipsec-nas` keeps a `.mmd` beside each figure (`docs/diagrams/mermaid/`), "kept for
editing and diffs. They are not what the documents display" (its `docs/00-prepare-the-cluster.md`, Diagram sources).
A twin is optional. Where one exists, it changes in the same commit as the page.

## 3. The page contract

These rules come from the skill's mechanics. The pages in §1 follow them, except where `RESEARCH.md` §2 names a
page that does not: `metallb`'s system fonts, `mongot-openshift`'s texts without a fill, `modernize-architecture`'s
label past its box, and the light `--none` of the 30 pages made before this template.

- **One page per diagram** at `docs/diagrams/<slug>/source.html`, rendered PNGs beside it as
  `<name>.light.png` and `<name>.dark.png`.
- **Self-contained.** No relative assets: `render.py` renders a copy of the page from a temporary directory. The only
  remote dependency is Google Fonts: its stylesheet and the font files it names, fetched on every render.
- **Fonts.** IBM Plex Sans for text and IBM Plex Mono for identifiers, loaded from Google Fonts in the weights the page
  uses. Figure text names a family the page loads, or a generic family, first. A system font named first (Arial,
  Menlo) is drawn in whatever the rendering machine has, and `render.py` refuses it (§5).
- **Colour tokens** on `:root`, redefined under `@media (prefers-color-scheme: dark)` guarded by
  `:root:not([data-theme="light"])`, and again under `:root[data-theme="dark"]`. The meanings are fixed:

  | Token | Means | Light | Dark |
  |---|---|---|---|
  | `--host` (+ `-wash`) | the local side; proposed emphasis | `#a55a0b` on `#fbf1e4` | `#f0a53c` on `#2a2014` |
  | `--remote` (+ `-wash`) | the far side; the allowed path | `#0e6f68` on `#e3f3f1` | `#3fcfc0` on `#122a28` |
  | `--gap` (+ `-wash`) | failure, refusal, a finding | `#b3261e` on `#fbe9e7` | `#f2857c` on `#2d1614` |
  | `--none` (+ `-wash`) | no call, denied, not reached | `#5f6a77` on `#eef0f3` | `#9aa5b3` on `#1b232d` |
  | `--ink`, `--muted` | text, secondary text | `#18212c`, `#58636f` | `#e5e9ef`, `#9aa5b3` |

  The light `--none` is `#5f6a77` in this kit's template; the pages generated before it carry `#6b7684`, which is
  4.04:1 on `--none-wash` (`RESEARCH.md` §2).
- **Solid box = shipped, dashed box = proposed.** A proposed box is dashed, and the figure carries a legend line naming
  each one. The skill names a proposal drawn as current as the most common review finding.
- **Connectors.** Every arrow is one of three kinds. A figure that uses more than one says which is which in its
  legend line.
  - *Solid*: traffic or a call that happens, drawn straight or elbowed.
  - *Curved, solid*: traffic from several senders to several receivers. Draw one cubic Bézier per pair,
    `M x1,y1 C mx,y1 mx,y2 x2,y2` with `mx` halfway, so each curve leaves and arrives level. Stroke it in the
    sender's token, so a reader can follow one sender to every receiver. Offset the starts and ends a few units, so
    no two curves merge. `examples/fan-out/` draws two Envoy pods sending to three mongot pods.
  - *Dashed*: a relationship that carries no traffic, such as a DNS lookup, a selector or a watch. Draw it in
    `--muted` with `stroke-dasharray="6 5"`, always with a label beside it that names the relationship. A proposed
    arrow is dashed too, and its label says "proposed". `render.py` refuses a dashed arrow with no label (§5).
- **Arrowheads take their line's colour.** The template's `#ah` is filled with `context-stroke`, so one marker serves
  every token. Measured in the pinned Chromium 153: a red line gets a red head, where `currentColor` gives the text
  colour. The PNGs are drawn by that Chromium; a browser without `context-stroke` draws the head black when the page
  is opened directly.
- **Every text has a fill** (a token or `currentColor`). A text with no fill is black: invisible in the dark render.
- **Text fits its box.** The budget is IBM Plex Sans 12.5 px ≈ 6.3 px per character, so a box of width W holds
  ≈ (W − 32) / 6.3 characters per line, with at most three lines per box. `render.py` measures the real text (§5).
- **The SVG.** A `viewBox` sized to the content, `width:100%; min-width:760px` inside `.fig-scroll` (which has
  `overflow-x: auto`). Arrowheads are a `<marker>` whose id is unique per figure. No `<script>`, `<style>` or
  `<foreignObject>` inside the SVG.
- **Accessibility.** `role="img"` and an `aria-label` that states the same claim as the caption. Measured: every SVG
  of the 156 pages has both.

## 4. Embedding a figure in a document

1. **A `<picture>`** with a dark `<source>`, a light `<source>` and an `<img>` whose `alt` states the figure's claim.
   GitHub then serves the dark render to a reader in dark mode
   ([GitHub changelog, 2021-11-24](https://github.blog/changelog/2021-11-24-specify-theme-context-for-images-in-markdown/)).
   Wrap it in `<!-- markdownlint-disable MD033 -->` / `<!-- markdownlint-enable MD033 -->` where Markdown is linted.
   - `group-sync-dashboard` (2 files) and `openshift-ipsec-nas` (7 files) embed this way
     (`group-sync-dashboard/docs/design/DESIGN_remote_cluster_access.md`, Figure 1).
   - `envoy-tutorial`, `envoy-grpc-modernization` and `mongodb-poc` embed the light PNG alone, with a full-claim
     `alt`, so their dark renders are committed but not shown.
2. **Paths relative to the document**, in every `srcset` and `src`. A `<source>` whose `srcset` does not resolve
   shows a broken image even when the `<img src>` is right, because the browser does not fall back. Check the paths
   with a link test, as `openshift-ipsec-nas/tests/test-doc-links.sh` does for every relative link and image.
3. **An italic caption** that separates what is shipped from what is proposed.
4. **A ```` ```text ```` twin** carrying the same points, for readers who cannot see images, and for diffs.
5. **A "Diagram sources" section** with the exact render command and the rule that picture, twin and page change
   together (the dashboard design document's "Diagram sources" section; `openshift-ipsec-nas/docs/00-prepare-the-cluster.md`).

## 5. The render checks

`diagram-render <page> <out-dir> <name-1>,<name-2>,...` writes `<name>.light.png` and `<name>.dark.png` per
`.fig-scroll`, at 2× pixel density, and exits non-zero on any of:

| Check | Why |
|---|---|
| a page error | the page did not finish what it draws |
| a request that did not load, or an HTTP error | a failed font stylesheet leaves the figure in a fallback face (#342) |
| figure text whose letters or digits no loaded face of its family draws | the same fallback, with every request answered 200 (#436, 2026-09-27), or a face whose `unicode-range` leaves the text out (review, 2026-10-06) |
| figure text crossing the edge of a box | a label longer than its box (one committed figure ships it, `RESEARCH.md` §2) |
| a dashed arrow with no text within 16 px of it other than a box's own (a container around the arrow does not count as a box; a box the arrow starts inside, holding no other box, still does) | a relationship the reader cannot name, or a proposal that reads as traffic (§3, Connectors) |
| figure text under 4.5:1 against the box under it, in either theme | WCAG 2.2 SC 1.4.3; one committed dark render ships black text on the dark ground |
| a name/figure count mismatch | a PNG named for the wrong figure |
| sideways page scroll at 375 px | a figure that widens the page on a phone |
| a page not done in two minutes | a script on the page that never ends: the browser would wait for ever. Each page's browser runs in a process of its own, ended at that limit (0.2.4) |

What the checks do not see, and review must:

- whether a label is true;
- a line crossing a label;
- an arrow into the wrong box;
- the weight drawn (a weight the stylesheet does not load is drawn in the nearest one it does);
- the glyphs of a face declared without `unicode-range`: the face check takes it at its word for every character, so
  a self-hosted file that lacks the text's letters passes while they are drawn in a machine face (Inter's Latin file
  with no `unicode-range` passes "Привет", which Chromium draws in Helvetica). Google Fonts declares a range on every
  face it serves;
- whether the text beside a dashed arrow names it: any text within 16 px counts, a legend line included, unless it is
  a box's own text. A box that holds the arrow's midpoint (a cluster drawn around the arrow, or a chip on the line) is
  a container, and its text can label the arrow;
- `fill-opacity`, or a fill colour with alpha: the contrast check takes the fill as opaque, so a readable label on a
  translucent highlight can fail (light ink over 6 % white in the dark theme measures 1.22:1);
- text on a shape other than a `<rect>`: the contrast check measures it against the rect or ground beneath, so a
  readable label on a filled circle can fail (white on `--remote` measures 1.00:1).

Open the PNGs and read them before anyone else does.

**Renderer version.** Playwright is pinned in `pyproject.toml`, and that pin chooses the Chromium build, so the
browser changes only when the pin moves. The pixels do not follow the pin alone: glyphs outside the IBM Plex subsets
are drawn in the machine's fonts, and a render can differ from the last in a few pixels (`RESEARCH.md` §2, §3).
Committed PNGs change only when their page is re-rendered on purpose (#436, "Must not change").

## 6. Review

A figure is a set of claims about the code, and it is reviewed like code:

- **Two reviewers check every figure in the change against the code.** They get the `source.html`, the PNGs and the
  render output.
- **"No proposal drawn as current" is a numbered claim** in the review brief.
- **What the review does not cover:** the figures were drawn from the documents and code they cite. Where they were not
  measured on a running system, the document says so, as `openshift-ipsec-nas`'s Diagram sources section does.

The origin of this rule is the skill's "Review it like code" section, and group-sync-dashboard #336, where three
figures went through two review rounds by three reviewers.
