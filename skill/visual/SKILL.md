---
name: visual
description: Design an enterprise-grade technical diagram page — hand-authored inline SVG, light and dark themes, rendered to PNG — for a mechanism, a flow, a trust boundary or a decision, grounded in the actual code and data. Use when the user types /visual, or asks for a visual, a diagram or a picture of how something works.
---

# /visual — a diagram that is true, readable and publishable

`/visual <what to draw>` starts designing at once. Ask a question only when the subject itself is
ambiguous (two systems with the same name, no repository to read); everything else has a default below.

Proven on group-sync-dashboard #336 (2026-09-23): three figures, two review rounds by three reviewers.
Every rule here exists because breaking it produced a finding.

## 1. Facts first — the picture is a claim

1. **Read the thing you are drawing.** The code path (function by function, in order), the config
   defaults, the RBAC objects, the log line. Measure on a live system when one is available
   (`oc auth can-i`, `kubectl get -o json`, a curl). Never draw from memory or from a spec's intent.
2. **Every label must be true today, or be marked proposed.** Solid boxes = shipped behaviour.
   **Dashed boxes = proposed / not built**, and the figure carries a legend line saying so. A dashed
   *arrow* is a relationship, not a proposal (§2). The single most common defect in review: a proposal
   drawn or captioned as current behaviour ("is gated twice" for something not built; an example
   cluster that cannot run the flow today).
3. **Draw what the code does, in the code's order** — including the steps that are easy to forget:
   the switch checked before the secret is read, the gate before the login, the cleanup that is
   *attempted* (and what happens when it fails), the branch for every outcome the code distinguishes
   (a 401 is not a 403; an unexpected exception is not a transport failure).
4. **Name the example honestly.** If the example instance (a cluster, a user) cannot take the path
   drawn, draw a generic one ("a remote-sar cluster") or say the limit in the caption.

## 2. What to draw

- **The mechanism, not its name.** The path a request takes, the boundary it crosses, the credential
  that crosses it, the arrow that disappears when an option is removed.
- **Lanes for trust boundaries** (HOST | REMOTE, browser | server, cluster A | cluster B), separated by
  a dashed rule; time flows down.
- **Comparisons put the difference in one row** (three columns, only the middle row differs).
- **Failure branches** go sideways in the gap colour and name the fix (`a 403 is fixed by: list groups`).
- **Label arrows** (`yes`, `sent once, over TLS`, `the token, in memory`). Numbered steps ①–⑥ when the
  order is the point.
- **Three connector kinds** (diagram-kit `STANDARD.md` §3, Connectors):
  - *solid*: traffic or a call that happens;
  - *curved, solid*: many senders to many receivers (two Envoy pods to three mongot pods), one cubic
    Bézier per pair, `M x1,y1 C mx,y1 mx,y2 x2,y2` with `mx` halfway, stroked in the sender's token and
    offset a few units so no two curves merge (`examples/fan-out/` in the kit);
  - *dashed*: a relationship that carries no traffic (a DNS lookup, a selector, a watch), `--muted`,
    always labelled beside the line. A proposed arrow is dashed and its label says "proposed". The
    renderer refuses a dashed arrow with no label within 16 px.
- One figure, one claim. A footer line in the figure may state the takeaway; a second, amber, line
  states what is proposed.

## 3. Mechanics (start from the kit's template: `diagram-template docs/diagrams/<slug>/source.html`)

This skill lives in diagram-kit (`skill/visual/SKILL.md`), the one home of the template, the renderer
and the standard (https://github.com/ephico2real2/diagram-kit). `~/.claude/skills/visual` is a link to
it, so a change to the skill is a pull request to the kit. Install the kit once (§4).

- **Tokens on `:root`**, redefined under `@media (prefers-color-scheme: dark)` guarded by
  `:root:not([data-theme="light"])` and again under `:root[data-theme="dark"]`. The palette's
  meanings are fixed: `--host` amber (the local side / proposed emphasis), `--remote` teal (the far
  side / the allowed path), `--gap` red (failure, refusal, a finding), `--none` grey (no call, denied),
  each with a `-wash` fill.
- **SVG:** `viewBox` sized to the content, `width:100%; min-width:760px` inside a horizontally
  scrolling `.fig-scroll` (so phones scroll the figure, never the page); strokes and text in
  `currentColor` or a token; one arrowhead `<marker>` per figure (`ah`, `ah2`, …) filled with
  `context-stroke`, so it takes each line's colour;
  no `<script>`, `<style>` or `<foreignObject>` inside the SVG.
- **Text budget:** IBM Plex Sans 12.5 px ≈ 6.3 px per character, so a box of width W holds
  ≈ (W − 32) / 6.3 characters per line; at most three lines per box (title 600 weight, detail,
  muted note). Identifiers in IBM Plex Mono 12 px. Align to a grid: shared x for a column, 26–28 px
  between boxes, arrows from box edge to box edge.
- **Accessibility:** `role="img"` and an `aria-label` that states the same claim as the caption.

## 4. Render and look — before anyone else does

Install the kit once, in its own venv (a pinned tag, so every machine renders with the same checks):

```sh
python3 -m venv ~/.local/share/diagram-kit/.venv
~/.local/share/diagram-kit/.venv/bin/pip install -q "diagram-kit @ git+https://github.com/ephico2real2/diagram-kit@v0.1.0"
~/.local/share/diagram-kit/.venv/bin/playwright install chromium
```

Then:

```sh
~/.local/share/diagram-kit/.venv/bin/diagram-render <page.html> <out-dir> <name-1>,<name-2>,…
```

Renders every `.fig-scroll` in order to `<out-dir>/<name>.light.png` and `.dark.png` at 2× pixel
density, and writes nothing unless every check passes. The checks (`STANDARD.md` §5): a page error, a
request that did not load, figure text in a fallback face, a label past its box, text under 4.5:1
contrast in either theme, a dashed arrow with no label, a name/figure count mismatch, and sideways
scroll at 375 px. **Open the PNGs and read them**: a line crossing a label and an arrow into the wrong
box are only visible there.

## 5. Deliver

- **As a page:** publish with the Artifact tool. Load the `artifact-design` and `artifact-diagramming`
  skills first (the tool's contract), give the page a two-to-four word `<title>`, republish the same
  file path to keep the URL.
- **Into a repository document** (the enterprise form):
  - commit the page as `docs/diagrams/<slug>/source.html` and the PNGs beside it;
  - embed each figure with `<picture>` — a `<source media="(prefers-color-scheme: dark)">`, a light
    `<source>`, and an `<img alt="…the figure's claim…">` — wrapped in
    `<!-- markdownlint-disable MD033 -->` / `<!-- markdownlint-enable MD033 -->` when the repo lints
    Markdown (GitHub deprecated the `#gh-dark-mode-only` fragments);
  - follow each figure with an italic caption and a ```` ```text ```` twin that carries the same
    points for readers who cannot see images and for diffs;
  - end the document with a "Diagram sources" section saying how to re-render and that picture, twin
    and page change together;
  - never put a claude.ai artifact URL in the repository.
- **Review it like code.** In a PR the figures are part of the change: the reviewers get the SVG text
  (`source.html`) and the PNGs, and "no proposal drawn as current" is a numbered claim in the brief.
