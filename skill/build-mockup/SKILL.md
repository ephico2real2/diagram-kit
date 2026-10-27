---
name: build-mockup
description: Build an app mockup (a design-canvas artboard) as the contract for the real page - the target framework declared first, one interactive app with preview frames, every colour a named token in one table, shared state declared once, sample data as typed datasets with their API source, every section one of a fixed set of types, fitting 390/820/1440 px, accessible markup, and rendered and checked before it is published. Use when the user types /build-mockup, or asks for a mockup, a wireframe, a UI design or a screen design of a page or app that will be built later.
---

# /build-mockup — a mockup the page can be built from mechanically

`/build-mockup <the page, for which project>` builds the mockup so `/mockup-to-page` can translate it mechanically into
the **target framework**: one source of colours, one source of state, typed data, a fixed set of section types. If a
mockup breaks a rule below, fix the mockup, not the translation.

This skill and `/mockup-to-page` are one standard: change them together. Proven on Inkcast, where the standard was
decided (ADR-0016, issue #235) and a copy lives in `docs/tooling/mockup-standard.md`, and on the tokensave dashboard
design (2026-10-26).

## Tooling

The tools live in Inkcast's `scripts/mockups/` (both need Node; `check.py` also needs Playwright with Chromium):

| Script | What it does |
|---|---|
| `render.js` | Renders a design-canvas artboard (`.dc.html`) to one self-contained HTML page, for given props: `node scripts/mockups/render.js Main.dc.html out.html '{"theme":"dark","tab":"agents"}'` |
| `check.py` | Renders every variant (each combination of the artboard's enum tweaks: theme, tab, range...) and opens it at 390, 820 and 1440 px. It fails on a leftover placeholder, a page that scrolls sideways, or a background that stops short. `--export <dir>` then writes one HTML page and PNG per tab for the repo (light by default). |

## 0. Declare the target first

Before any markup, settle and record it (in the issue, the canvas notes, and `data-props` as `"$target"`):

| Field | Values used today |
|---|---|
| `framework` | `react-ts`: a full web app (Inkcast's, React + TypeScript). `preact-ts`: small pages embedded in a binary, e.g. the tokensave dashboard (Preact + TypeScript, owner's choice 2026-10-26). |
| `styling` | CSS custom properties from `tokens.css` (always) |
| `state` | URL query parameters for shareable state; browser storage for the theme |
| `data` | the API the page will call (REST paths) |

Both targets share one component model (function components, hooks, JSX), so one mockup can feed either. If a new
project hasn't chosen, ask the owner before building.

## 1. Shape: one app, many frames

- **One interactive app artboard** (`Main.dc.html`) holds every tab or screen as an `<sc-if>` branch of one component,
  with all shared state in that component. Never one artboard per tab joined by links: their state drifts apart.
- **Preview frames** import the same app: one per tab (`<dc-import name="Main" tab="agents" theme="dark">`), a tablet
  frame (820 px) and a phone frame (390 px). They never copy markup.
- **A theme tokens sheet** (`Colors.dc.html`) lists every token with its light and dark value and contrast.
- Launch on the app; the canvas title says "sample data".

## 2. Colours: one token table

- `renderVals()` builds `T`, the token object for the active theme, from two tables (dark, light) defined once. Markup
  uses only `{{c.<token>}}`; no hex in markup outside the tables (except a wrapper frame's own background).
- Required names, which become the CSS variables one-to-one: `bg surface raised border track control text muted accent
  accentFg`, series tokens (e.g. `spent saved`), states `okFg okBg warnFg warnBg infoFg infoBg stopFg stopBg`,
  categories `cat.emerald cat.sky cat.amber cat.violet cat.coral cat.pink cat.teal cat.slate`.
- Category colours mark what a thing is (a tool, a role, a model) and keep their colour on every tab: map once
  (`TOOL`, `ROLE`, `MODEL`) and look up; never pick a colour inline. Icon tiles: the category colour tinted over
  `surface` (12% light, 16% dark).
- Contrast, checked by script before publishing: text ≥ 4.5:1, big numbers and chart marks ≥ 3:1, both themes. Two
  series differ in lightness, not hue alone; similar hues in one theme (e.g. amber vs coral) are adjusted until they
  read apart. Never colour alone: every badge carries its word.
- Modes: Dark, Light, Auto (`prefers-color-scheme`). The default is the owner's (tokensave dashboard: Dark). A
  project's own product docs and screenshots follow its rule (Inkcast: light only unless the owner says otherwise).

## 3. State: declared once, owned once

- Global state keys (e.g. `theme`, `tab`, `range`, `from`, `to`, filters) are initialised in the constructor, accepted
  as props (so preview frames open on a tab), and listed in `data-props` as enum tweaks.
- Above the constructor, a comment block declares each key: owner, type, default, persistence, e.g.
  `// state range: owner=App type='7'|'30'|'45'|'60'|'90'|'custom' default='30' url=?range=`
  `// state theme: owner=App type='dark'|'light'|'auto' default='dark' storage=theme`
- Local UI state (an open menu) is declared the same way on the section that owns it.
- Date ranges: presets (7, 30, 45, 60, 90 days) plus Custom (From/To bounded by today); the header states the range in
  words; every figure and list follows it.

## 4. Data: typed datasets with their source

- All sample data is returned from `renderVals()` as named datasets (`tiles`, `days`, `runs`, `repos`…), never typed
  into markup.
- Each dataset gets a TypeScript type and its source in comments right above it. These are the API contract and become
  `types.ts`:
  `// dataset runs: GET /api/runs?range&repo&tool → Run[]`
  `// type Run = { name: string; role: Role; tool: Tool; model: string; io: string; cost: string; state: 'finished'|'running'|'stopped'|'partial' }`
- Values that follow the range or filters are computed from them, so the mockup behaves like the page.
- Sample data is labelled ("Sample data · mockup"). Public repos get generic sample names: never a real person, a
  client, or the owner's other projects.

## 5. Sections: a fixed vocabulary = the component library

Every section is one of these, with `data-component="<type>"` and `data-dataset="<name>"` on its root. Each type becomes
exactly one component in the target, so its props are the dataset plus labels:

| type | what it is | props |
|---|---|---|
| `app-header` | logo, sample pill, workspace, theme, filters, range, tabs | the global state |
| `kpi-tiles` | grid of label / big number / note | `tiles: Tile[]` |
| `time-series` | bars per day, legend, date ticks; scrolls in its card on a phone | `days: Day[], series: Series[], ticks: string[]` |
| `bar-list` | label, value, bar and category dot per row | `rows: BarRow[]` |
| `row-list` | rows that stack into cards on a phone (instead of wide tables) | `rows: T[], columns` |
| `heat-grid` | 2-D grid, sticky first column | `rows: HeatRow[], columns: string[]` |
| `card-grid` | cards with icon tile, status badge, details | `cards: Card[]` |
| `callout` | warning or tip, often with a `<code>` command | `tone, title, body, command?` |
| `stat-strip` | one card: a heading figure with its note, and a few labelled numbers beside it | `title, value, note, stats: Stat[]` |
| `segmented` | button group (theme, range, measure) with `aria-pressed` | `options, value, onChange` |

Each section starts with an eyebrow (small upper-case letter-spaced `accent`) and an `h2`. A new type is added to this
table, and to `/mockup-to-page`, in the same change.

## 6. Fits every screen

- Fluid root (`width: 100%`, `min-height: 100vh`), content max 1440 px, flex-wrap or `repeat(auto-fit, minmax(…))`,
  wide content in its own `overflow-x: auto` box, numbers in `clamp()`.
- Breakpoints (the page uses the same): phone < 640, tablet 640–1024, desktop, wide > 1440. Phone: one column; filters
  fold into a "Filters" button (helmet media query on `.ts-filters` / `.ts-filterbtn`, with `!important` since inline
  styles win otherwise); tabs and segmented groups scroll sideways; `row-list` rows stack. Touch targets ≥ 44 px.

## 7. Accessibility in the markup

Real `<button>`, `<a href>`, `<label>` + inputs; `aria-current` on the active tab; `aria-pressed` on segmented buttons;
`aria-label` on icon-only controls; decorative SVG `aria-hidden`.

## 8. Review before publishing (always)

1. Render every tab × both themes × every range preset to static HTML with the converter (sc-for, sc-if, holes,
   `renderVals` with props).
2. In headless Chromium at 390, 820 and 1440 px, fail on any leftover `{{`, `sc-`, `undefined`, `NaN`; page width >
   viewport; background shorter than the viewport.
3. Screenshot a sample per theme and width and look: colours consistent across tabs, categories distinct, nothing cut
   off.
4. Fix, re-run, publish, and report what was checked.

## 9. Into the repo

When accepted, export each tab to self-contained HTML plus a PNG under the feature's `mockups/` folder (Inkcast:
`docs/<area>/mockups/`, light screenshots unless the owner says), link them from the design doc with the `$target`
table, and keep the canvas link in the issue.
