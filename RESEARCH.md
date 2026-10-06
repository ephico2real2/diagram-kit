# Research behind the kit (2026-10-06)

Group-sync-dashboard #436, step 1. Every number below comes from a command run on 2026-10-06. Where a claim was not
measured, it says so.

**Scope.** Every `source.html` page with a `.fig-scroll` in our repositories:

- `openshift-ipsec-nas`;
- `envoy-grpc-modernization`;
- `envoy-tutorial`: `main` plus six local branch checkouts (`module-17-corp`, `module-18-keycloak-ldap`,
  `module-19-shop`, `module-20-shop-envoy`, `metallb-ingress-shard`, `permanent-lab`);
- `group-sync-dashboard`;
- `mongodb-poc`.

That is 156 pages and 254 figures, found with `grep -rl 'fig-scroll' --include='*.html'` over every git checkout under
the home directory.

**The core strategy is fixed.** One generated `source.html` per diagram, from the template, rendered to light and dark
PNGs by `render.py` (the operator, 2026-10-06). The prior art below is therefore read only for checks and ideas to
borrow into our renderer and standard, never as a replacement format.

## 1. Prior art: cathrynlavery/diagram-design

**What was read.** The repository is MIT-licensed, by Cathryn Lavery, created 2026-04-16. It was read at commit
`a05a7d9` (2026-10-06, "bump plugin manifests to 2.6.63"), from a sparse clone of its `scripts/`,
`skills/diagram-design/scripts/`, `docs/adr/` and `.github/workflows/`. Its checks are Python scripts run in its CI.
The table names each check, how it works, and our verdict.

| Its check (file) | How it works | Verdict for our pages | Why |
|---|---|---|---|
| Clipping by paint (`scripts/lint-render.py`, docstring and `clipping_findings`) | Screenshots each SVG as authored, then again with `overflow` released stage by stage, and diffs them. New ink outside the box was being clipped. | **Not adopted** | Its geometric stand-in on our pages is text whose box spills outside its SVG's `viewBox`, and we measured that: 0 texts on 156 pages, in both themes. The pixel-diff machinery is about 1,500 lines, with no defect on our pages to catch. |
| Sideways page overflow (`lint-render.py`, `PAGE_OVERFLOW_JS`) | `scrollWidth − clientWidth` beyond 1 px | **Already ours** | `render.py` fails a page whose `scrollWidth` exceeds 375 at a 375 px viewport (#342). All 156 pages measure 375. |
| Collapsed SVG (`lint-render.py`, `svg-collapsed`) | An SVG that renders 0 wide or 0 high | **Not adopted** | Measured 0 collapsed SVGs on 156 pages. Our count check plus the screenshot of each `.fig-scroll` already fails a page whose figures are missing. |
| Missing local asset, page error (`lint-render.py`, `watch`) | `requestfailed` for `file://` URLs, plus `pageerror` | **Already ours, stricter** | Ours fails on any request that did not load, local or remote, on an HTTP status ≥ 400, and on `pageerror`, on all three pages it opens. |
| Console errors (`lint-render.py`, `watch`) | Any `console.error` except resource failures | **Not adopted** | Measured 0 console errors on 156 pages in both themes. |
| Network cut at the resolver, fallback faces by default; `--fonts` allows exactly Google Fonts (`lint-render.py`, `resolver_rule`, `block_network`) | The linter measures layout in fallback faces, deterministically. Its README: "not what your reader sees". | **Not adopted for renders; idea borrowed for tests** | Our PNGs are what the reader sees, so they must be drawn in the real face, and we fail when it is not. Our tests take the determinism idea: no test reaches the network, because the face is a local OFL font inlined as a `data:` URL. |
| Pinned Playwright and Chromium (`.github/workflows/ci.yml`, `PLAYWRIGHT_VERSION: "1.62.0"`) | "the oracle is pixels", so the browser is bumped deliberately | **Adopted** | `pyproject.toml` pins `playwright==1.63.0`, the version our renders ran on. |
| Label mask under a later node (`scripts/verify-geometry.py`; ADR 0005) | Parses `<rect>`s from the source. A label plate (20–200 × 8–14) that overlaps a node (≥ 60×40) declared later in the document is clipped by that node's fill. | **Its idea adapted; its check not adopted** | It depends on its own convention, a mask plate behind each label plus a fixed paint order, which our pages do not use. The same assurance on our format is figure text whose box crosses a `<rect>`'s edge. Measured on 156 pages: 1 hit, a true defect (§2), and 0 false hits. `render.py` now fails on it. |
| Connector routing (`verify-geometry.py`) | Diagonal segments, segments along a node border, endpoints within 8 px of a corner, ports closer than 12 px, stacked trunks | **Not adopted** | Built on its path conventions. Not measured on our pages; review covers arrows (`STANDARD.md` §5). |
| Text width from font metrics (`scripts/verify-treemap.py` `estimated_advance`, `MONO_ADVANCE = 0.62`, `SANS_ADVANCE = 0.60`; the same in `verify-marimekko.py`) | Estimates a label's width without a browser and fails a label wider than its cell | **Idea adopted, measured instead of estimated** | Our template budgets 6.3 px per character. `render.py` measures the drawn text after the fonts load (`getBoundingClientRect`), which is the same question answered exactly. This is the crossing check above. |
| WCAG contrast (`skills/diagram-design/references/onboarding.md` line 121: AA for `ink` and `muted` on `paper`; `scripts/verify-heatmap.py` line 441: focal cell text 4.5:1; `scripts/verify-dumbbell.py` line 60: non-text 3:1; `scripts/verify-skin-polarity.py`: tone claims against luminance) | Per-type scripts compute WCAG ratios from known colours; onboarding is a rule the agent applies | **Adopted, on our format** | We measured every figure text against the filled `<rect>` under it, per theme: 343 texts on 30 pages fall under 4.5:1 (§2). Two checks now cover it: `render.py` measures every page as drawn, and `tests/test_template.py` measures the template's token pairs. |
| Accessible-SVG contract (`scripts/lint-skin.py` `lint_accessible_svgs`; `skills/diagram-design/scripts/self_check.py` `check_svgs`) | `role="img"`, a `viewBox`, `<title>` first, a `<desc>`, `aria-labelledby` naming both | **Not adopted as a check** | Ours is `role="img"` plus `aria-label` (the skill's rule). Measured: every SVG in the 156 pages has both. It stays a rule in `STANDARD.md` §3, for review. |
| Palette and font allow-list, no external assets (`lint-skin.py`, `ALLOWED_FONTS`, `external-asset`) | Every hex must be in its style guide, and no remote `src`, `@import` or `<link>` | **Not adopted** | Our pages load Google Fonts on purpose. All 156 pages compute one palette (measured: one distinct table of token values in both themes), and the template test now guards that palette. |
| Motion and script contract (`self_check.py` `check_scripts`, `check_motion`) | At most one script, which must be its canonical controller, plus step markup | **Not applicable** | Our pages have no scripts and no motion. |
| Legend tone polarity (`verify-skin-polarity.py`) | "darker is larger" checked against an opacity ramp | **Not applicable** | We have no opacity ramps. |

**Contributing upstream.** Not proposed. Its checks are built around its own format (mask plates, a single
pinned controller, its palette roles, network blocked by default), and ours around ours. The ideas cross over; the
code does not.

**Our own candidate, rejected on measurement.** We also tried text boxes overlapping each other within one SVG. It
had 1 hit on 156 pages, `envoy-grpc-modernization`'s "the catalogue — …" over "which is what makes the backends…".
The rendered PNG shows two lines 14 px apart that do not touch. The glyph boxes include ascent and descent, so the
hit was false. Not adopted.

## 2. Our renderer on our figures

Each page was rendered into a scratch directory with generic names (`fig1`…`figN`), never into a repository:

1. with the stricter `render.py`, group-sync-dashboard's `docs/diagrams/render.py` at `665b7334` (md5 `3d533bd6`),
   as the brief asks;
2. with the kit's, to measure the three new checks.

Each written PNG was compared by sha256 with every committed PNG beside its page. No committed PNG was changed.

### Per repository

| Repository | Pages | Figures | Stricter `render.py`: exit 0 / non-zero | 375 px `scrollWidth` | Seconds per page (min / median / max) | Re-render byte-identical to a committed PNG | Kit `render.py`: exit 0 / non-zero |
|---|---|---|---|---|---|---|---|
| openshift-ipsec-nas | 5 | 8 | 5 / 0 | 375 | 2.49 / 2.54 / 3.09 | 10 of 16 | 1 / 4 |
| envoy-grpc-modernization | 1 | 3 | 1 / 0 | 375 | 2.93 / 2.93 / 2.93 | 6 of 6 | 0 / 1 |
| envoy-tutorial @ main | 23 | 34 | 23 / 0 | 375 | 2.20 / 2.59 / 2.84 | 65 of 68 | 19 / 4 |
| envoy-tutorial @ module-19-shop | 21 | 32 | 21 / 0 | 375 | 2.49 / 2.55 / 2.85 | 59 of 64 | 18 / 3 |
| envoy-tutorial @ module-20-shop-envoy | 22 | 33 | 22 / 0 | 375 | 2.51 / 2.56 / 2.85 | 61 of 66 | 19 / 3 |
| envoy-tutorial @ metallb-ingress-shard | 20 | 31 | 20 / 0 | 375 | 2.48 / 2.55 / 2.89 | 57 of 62 | 17 / 3 |
| envoy-tutorial @ module-18-keycloak-ldap | 19 | 30 | 19 / 0 | 375 | 2.49 / 2.55 / 2.87 | 55 of 60 | 16 / 3 |
| envoy-tutorial @ module-17-corp | 19 | 30 | 19 / 0 | 375 | 2.47 / 2.62 / 2.87 | 56 of 60 | 16 / 3 |
| envoy-tutorial @ permanent-lab | 19 | 30 | 19 / 0 | 375 | 2.48 / 2.64 / 3.77 | 57 of 60 | 16 / 3 |
| group-sync-dashboard | 1 | 4 | 1 / 0 | 375 | 3.11 / 3.11 / 3.11 | 2 of 8 | 0 / 1 |
| mongodb-poc | 6 | 19 | 6 / 0 | 375 | 2.50 / 2.78 / 4.07 | 38 of 38 | 4 / 2 |
| **all** | **156** | **254** | **156 / 0** | | total 411 s | **466 of 508** | **126 / 30** |

**Stricter `render.py`: 156 of 156 pages exit 0, with no failures.**

- Every page measures `scrollWidth` 375 at 375 px.
- A page takes 2.20–4.07 s (median 2.58 s); all 156 take 411 s in total, one at a time, on an Apple M5 Pro with
  the network up.

**Re-renders against the committed PNGs (a fact, not a verdict):**

- 466 of 508 PNGs are byte-identical to a committed one.
- 2 have no committed PNG of the same size: group-sync-dashboard's first figure, light and dark.
- 20 differ in at most 735 pixels.
- The other 20 differ in 4,993–203,449 pixels:
  - `openshift-ipsec-nas` figures 1 and 2 of `ipsec-nas`;
  - envoy-tutorial's `12-gateway-api` figure 3, on all seven trees;
  - the dashboard's figure 4.

Why they differ (a page edited after its PNGs, or a font or Chromium difference) was not investigated. One cause is
the renderer itself: the same page (envoy-tutorial `08-tls-on-envoy`, `module-18-keycloak-ldap`) rendered six times
gave one run whose two light PNGs differ from the other five in 24 and 101 pixels, by at most 5 of 255.

**Kit `render.py`: 126 pages exit 0, 30 exit 1.** Every failure is one of the three new checks:

| Check | Pages | What it found |
|---|---|---|
| contrast under 4.5:1 | 30 | 329 texts in `--none` `#6b7684` on `--none-wash` `#eef0f3`, light theme, all at 4.04:1. One token pair, on 30 pages across 5 repositories (envoy-tutorial's trees counted once); no other pair fails. |
| text crosses a box edge | 1 | `envoy-grpc-modernization` `modernize-architecture`, figure 2: "NOT_FOUND → 404, ALREADY_EXISTS → 409", whose "409" runs out of its box into the arrow. The committed PNG is byte-identical to the re-render, so it ships that way. |
| fallback face | 1 | envoy-tutorial `metallb` (on `main`; the page is not on the branches): its tokens name Arial and Menlo, system fonts the page does not load (§3). |

**One more defect that this run does not show.** `render.py` stops at the first theme that fails. So
`mongodb-poc` `mongot-openshift`, which fails the light contrast check, never reaches its dark checks.

- The contrast survey that preceded the check measured 14 texts there with no `fill`, so they are black in the dark
  theme, at 1.22–1.39:1. Its "Ownership" legend title is near-invisible in the committed dark PNG, which is
  byte-identical to the re-render.
- With the page's light `--none` set to the template's `#5f6a77` (a scratch copy), the kit renderer exits 1 on exactly
  those 14 dark texts.

**With the template's grey token.** The 156 pages were also rendered as scratch copies with the one token changed (light `--none` `#6b7684` → `#5f6a77`). With the kit renderer, 153 pages exit 0 and 3 exit 1:

- envoy-grpc-modernization modernize-architecture: crosses a box ×1;
- envoy-tutorial metallb: fallback face ×2;
- mongodb-poc mongot-openshift: contrast (dark) ×14.

These are the pages a consumer must change before it renders through the kit.

**The survey.** Before any check was written, one Playwright pass over all 156 pages in both themes measured each
candidate check (scratch tools, not shipped):

| Candidate | Result |
|---|---|
| a family named first with no loaded face | 1 page (metallb) |
| text spilling outside its SVG's `viewBox` | 0 |
| text crossing a `<rect>` edge | 1 page, a true defect |
| text boxes overlapping | 1 page, false (§1) |
| SVGs without `role="img"` and `aria-label` | 0 |
| console errors | 0 |
| collapsed SVGs | 0 |
| distinct palettes | 1 (all pages compute the same token values) |
| texts under 4.5:1 against the rect under them | 343 texts on 30 pages (329 light, 14 dark) |

The as-drawn contrast pass covered 8,163 figure texts per theme.

**Each check fails its tests when it is removed.** A mutation run removed one check at a time from a copy of the kit
and ran the suite:

| Removed | Tests that fail |
|---|---|
| face check | stand-in `fallback-face`; browser: undeclared family, face that does not decode, face whose subset leaves the label out (added on review) |
| `pageerror` | stand-in `pageerror`, `phone-pageerror`; browser: page error |
| `requestfailed` | stand-in `offline`, `phone-requestfailed`; browser: stylesheet that does not load |
| HTTP ≥ 400 | stand-in `404`, `phone-404` |
| count check | stand-in `mismatch`; browser: name count |
| 375 px check | stand-in `scroll`; browser: sideways scroll |
| contrast check | stand-in `low-contrast`; browser: no fill on a dark figure |
| crossing check | stand-in `crossing`; browser: label past its box |
| watching the 375 px page | stand-in `phone-requestfailed`, `phone-404`, `phone-pageerror` |

The template palette test was also run against the commit before the palette change. It fails there with
"light: --none #6b7684 on --none-wash #eef0f3 is 4.04:1" and passes after.

## 3. The font-face gap

**The gap, reproduced.** The dashboard's page was copied with `IBM+Plex+Sans:` changed to
`IBM+Plex+Sans+DoesNotExist:`:

- Google Fonts answers that stylesheet with **200** (curl);
- the stricter `render.py` exits **0** and writes all 8 PNGs;
- the kit's exits **1**: `FAIL: light: figure text in a fallback face: no loaded @font-face declares 'IBM Plex Sans'`.

**Two designs were measured on the real page and on the broken one.**

| Design | Real page | Broken page | Verdict |
|---|---|---|---|
| CDP `CSS.getPlatformFontsForNode` on each figure `<text>`: the face Chromium actually drew | IBM Plex Sans 3,966 glyphs, IBM Plex Mono 76, IBM Plex Mono Medium 195, **Lucida Grande 7, Hiragino Sans 6** | Helvetica 3,963 glyphs where Plex Sans was | Rejected. It sees the face exactly, but on the real page it also reports per-glyph fallbacks for symbols Plex lacks (①, →), which the template uses on purpose. Those fallbacks depend on the operating system, so a rule built on them is either noisy or loose. |
| `document.fonts`: the first family each figure text asks for (computed `font-family`) must be a generic family or a face whose status is `loaded` | no hits | `IBM Plex Sans` (139 texts) | **Adopted.** It is the gap exactly ("the stylesheet never declares the family"): deterministic, no CDP, 11 lines of JavaScript. |

**On our pages: 1 hit, envoy-tutorial `metallb`.** Its tokens are `--font-body: Arial, Helvetica, sans-serif` and
`--font-mono: Menlo, monospace`, and it loads no web font. On this Mac, CDP reports Arial (1,949 glyphs) and Menlo
(530) drawn, as intended. On a machine without those fonts, such as a Linux CI runner, the figure falls back; that
was not measured here. The check's rule is that figure text names a face the page loads, or a generic family. That
keeps a system font from being named first; it does not make the PNG independent of the machine (Limits, below).
The page needs its two tokens set to the template's to pass.

**Limits, measured.**

- **The weight drawn is not checked.** The template asks for IBM Plex Mono at weight 600 in its lane headers, and
  its stylesheet loaded only 400 and 500, so Chromium drew IBM Plex Mono Medium (CDP). The kit's template now loads
  600, and CDP reports IBM Plex Mono SemiBold.
- **A family that loads only a `unicode-range` subset other than the text's** passed the check as first built. Not
  seen on our pages; closed on review (below).
- **A face declared without `unicode-range` is taken at its word.** `document.fonts.load()` answers it for any
  character, so Inter's Latin file with no range passes "Привет" while CDP reports Helvetica drawing it. Not seen on
  our pages: Google Fonts declares a range on every face, and no figure text has a letter outside Latin-1 (review,
  2026-10-06).
- **Glyphs outside the loaded subsets are drawn in the machine's fonts.** The template's Google Fonts request carries
  no U+2190–21FF or U+2460–24FF, so → ← ⇄ ①–⑪ ✕ come from the machine (Lucida Grande, Hiragino Sans, Menlo here):
  812 of 8,170 figure texts on 125 of the 156 pages. A generic family named first is a machine face as well. The
  verdicts hold: with DejaVu Sans arrows (Ubuntu's usual fallback), all 156 pages check the same.

**Revised after review (2026-10-06).** Codex showed the adopted check proves only that some face of the family
loaded, not that it drew the text: a face loaded for `unicode-range: U+0041` passes "A Ownership". The check now
asks `document.fonts.load()` for each letter and decimal digit the figure text draws, in its style, weight and size,
and fails unless a loaded face of the first family answers. Two defects in the fix as proposed were measured before
it was applied: a spec carrying computed `font-stretch` (`100%`) is refused by the `font` shorthand with a
`SyntaxError`, which the proposed `catch` turned into "every page fails"; and `\p{N}` takes in ①, which the IBM Plex
subsets do not carry. Symbols stay out of the check (Limits, above). A face that does not decode makes the load reject
with `NetworkError`; that is reported, not swallowed. On the 159 pages of 2026-10-06 the revised kit gives the same
verdict and the same failure lines as before on every page (128 pass, 31 fail, counting mongodb-poc
`mongot-runbooks` rendered from its branch, exit 0 under both); the only face failures are still `metallb`'s Arial
and Menlo. Total time 381.5 s against 384.4 s.

## 4. Which Mermaid sources are live

**`openshift-ipsec-nas`: 8 `.mmd` in `docs/diagrams/mermaid/`. They are text twins, not the source of any PNG.**

- Its documents say so: "The Mermaid files are plain-text versions of the same flows, kept for editing and diffs.
  They are not what the documents display" (`docs/00-prepare-the-cluster.md`, Diagram sources). The same holds for
  `nat-tunnel-mode.mmd`, `gitops-deploy-flow.mmd` (`docs/40-lab-crc-and-nas.md`) and `lab-checks.mmd`
  (`docs/lab/lima-lab.md`).
- Every `.mmd` was added in the same commit as its `source.html` and PNGs (`git log --diff-filter=A`: `45fa3e0`,
  `1126789`, `2038422`, `677c1a3`, `c8ca930`, `3b5cee1`).
- Two pages changed after their twins, in `7095828`. Both changes are to the page's lede (a renamed document link),
  not to a figure.
- No CI renders them.
- All 8 render with `@mermaid-js/mermaid-cli@11` (exit 0).

They are live in the sense the repository means: maintained beside each figure, changed together.

**`envoy-reference-architecture`: 5 `.mmd` in `docs/diagrams/`. They are the live sources of the PNGs its documents
embed.**

- `docs/diagrams/render.sh` renders each `.mmd` to the PNG of the same name. README.md, `docs/proposal.md` and the
  Confluence export embed the PNGs, "because Confluence renders no Mermaid at all" (`render.sh` header).
- The script runs `npx -p @mermaid-js/mermaid-cli` unpinned. Re-rendered today with its exact config, mermaid-cli
  12.0.0, into a scratch directory, all 5 differ from the committed PNGs, and in size too:
  - `01-architecture`: 2004×3660, committed 2139×3045;
  - `02-shared-service`: 2352×651, committed 2352×609;
  - `03-request-flow`: 2352×2037, committed 2352×1920;
  - `04-resource-model`: 2352×690, committed 2352×747;
  - `05-rollout-phases`: 2352×177, committed 2352×174.

  `STANDARD.md` §2 therefore asks for a pinned mermaid-cli wherever Mermaid PNGs are committed.

## 5. How consumers take the kit

| Model | What the data says |
|---|---|
| Vendor a pinned copy (one file and its test) | This is how the drift happened. `envoy-grpc-modernization` still carries the old copy (md5 `3f784aa1`, without #342's checks), and the skill's copy drifted until 2026-09-27. A vendored copy stays right only with a further check that it still matches the tag. |
| The skill points at a pinned copy | Works on one workstation and in no CI. `mongodb-poc` removed every reference to the workstation path (`a918536`: "specific to one workstation and does not belong in a shared repository"). |
| **An installable package, pinned by git tag** | One source. Each consumer pins one line (`diagram-kit @ git+https://github.com/ephico2real2/diagram-kit@v0.1.0`), and its CI installs and runs `diagram-render`. The Playwright pin travels with the package, so a consumer cannot render with a different Chromium by accident. No copy can drift, and no index such as PyPI is needed. |

**Recommendation: the installable package, pinned by tag.**

- It is the standard way to ship a Python command, and the one where "which version renders our figures" is a line
  in the repository.
- The kit carries the minimum for it: `pyproject.toml` (20 lines) and the renderer as `diagram_kit/render.py`.
- `python diagram_kit/render.py` still works from a clone.
- The `/visual` skill then names the command, not a private copy.

It needs the repository public (step 3), because `pip` fetches the tag anonymously. The tutorial walk installed it
from a local clone (`TUTORIAL.md`).

## 6. Connectors: curves, dashed arrows, one arrowhead

Asked for on 2026-10-06: curved arrows to show traffic from every Envoy pod reaching every mongot pod, and dashed
arrows for a linkage. Measured before the rules in `STANDARD.md` §3 were written:

- **No figure draws a fan-out.** The seven Envoy and mongot pages in mongodb-poc and envoy-tutorial's `metallb`
  contain 0 curved paths (no `C` or `Q` command). envoy-flow's `headless-vs-clusterip` states "all three pods serve
  traffic" as text in a box.
- **A marker filled with `currentColor` takes the text colour, not its line's.** The first prototype drew every
  arrowhead black on teal and amber curves: a marker's properties come from where it is defined. Filled with
  `context-stroke` (SVG 2), it takes its line's stroke. Measured in the pinned Chromium 153.0.8010.12, sampling a
  pixel inside the head of a red line: `[255, 0, 0, 255]` with `context-stroke`, `[0, 0, 0, 255]` with
  `currentColor`. Lines stroked in `currentColor` look exactly as before.
- **Dashed meant "proposed" for boxes and arrows alike.** A dashed arrow now means a relationship, always labelled,
  and a dashed box still means proposed (the operator's decision, 2026-10-06). `render.py` refuses a dashed arrow
  with no `<text>` outside every box within 16 px of it.
- **On the 159 pages,** the check adds 8 lines on 3 pages, and no other failure line changes: 126 pages pass and 33
  fail, against 128 and 31.
  - openshift-upgrade `disconnected-update-problem` figure 2: 4 short arrows between planned hops, read through the
    legend "Dashed = planned, not done". Each needs a label that says planned.
  - mongodb-poc `grpc-through-envoy` figure 1: the reverse leg from a mongot pod to mongod. Its name, "⑧ the reverse
    leg", sits far from the arrow, and the legend's "Dashed = present but carrying no traffic" does not fit it.
  - mongodb-poc `mongot-openshift` figures 5, 9 and 10, a page that already failed on its unfilled text.
- **Revised in 0.1.1, on the rollout (2026-10-06).** `mongot-openshift`'s three sync legs were labelled ("sync leg …
  does NOT cross Envoy") but 27 px or more from the line, and figure 5's label sits inside the cluster box the arrow
  starts in (it holds the arrow's start and midpoint; the arrow ends at mongod, outside it), which 0.1.0 took for a
  box's own text. The page now sets each label against its line, and the check takes a box that holds the arrow's
  midpoint as a container, whose text can label the arrow. A box that holds one end of the arrow and no other box is
  still the arrow's end box, so its own text never labels it (OB1-lite's review: an arrow drawn from inside its start
  box passed otherwise). Four browser tests; on the 158 pages, the rule changes exactly this one arrow.

## Appendix: every page

Repository, page, and the two renders. "Identical PNGs" counts the re-rendered PNGs byte-identical to a committed PNG beside the page.

| Repository | Page | Figures | Stricter: exit | 375 px | Seconds | Identical PNGs | Kit: exit, failures |
|---|---|---|---|---|---|---|---|
| openshift-ipsec-nas | `crc-nat` | 1 | 0 | 375 | 2.53 | 2/2 | 1, contrast (light) ×1 |
| openshift-ipsec-nas | `deploy-flow` | 1 | 0 | 375 | 2.55 | 2/2 | 1, contrast (light) ×2 |
| openshift-ipsec-nas | `ipsec-nas` | 4 | 0 | 375 | 3.09 | 2/8 | 1, contrast (light) ×5 |
| openshift-ipsec-nas | `lima-lab` | 1 | 0 | 375 | 2.49 | 2/2 | 0 |
| openshift-ipsec-nas | `option-c` | 1 | 0 | 375 | 2.54 | 2/2 | 1, contrast (light) ×1 |
| envoy-grpc-modernization | `modernize-architecture` | 3 | 0 | 375 | 2.93 | 6/6 | 1, contrast (light) ×4; crosses a box ×1 |
| envoy-tutorial @ main | `00-prerequisites` | 1 | 0 | 375 | 2.50 | 2/2 | 0 |
| envoy-tutorial @ main | `01-what-is-envoy` | 2 | 0 | 375 | 2.66 | 4/4 | 0 |
| envoy-tutorial @ main | `02-the-config-file` | 1 | 0 | 375 | 2.50 | 2/2 | 0 |
| envoy-tutorial @ main | `03-listeners-and-filter-chains` | 1 | 0 | 375 | 2.53 | 2/2 | 0 |
| envoy-tutorial @ main | `04-routing` | 2 | 0 | 375 | 2.65 | 4/4 | 1, contrast (light) ×36 |
| envoy-tutorial @ main | `05-clusters-and-load-balancing` | 3 | 0 | 375 | 2.84 | 6/6 | 0 |
| envoy-tutorial @ main | `06-http-filters` | 1 | 0 | 375 | 2.49 | 2/2 | 0 |
| envoy-tutorial @ main | `07-modernising-grpc` | 2 | 0 | 375 | 2.62 | 3/4 | 0 |
| envoy-tutorial @ main | `08-tls-on-envoy` | 2 | 0 | 375 | 2.70 | 4/4 | 0 |
| envoy-tutorial @ main | `09-grpc-end-to-end` | 2 | 0 | 375 | 2.70 | 4/4 | 0 |
| envoy-tutorial @ main | `10-observability` | 1 | 0 | 375 | 2.54 | 2/2 | 0 |
| envoy-tutorial @ main | `11-resilience` | 2 | 0 | 375 | 2.69 | 4/4 | 0 |
| envoy-tutorial @ main | `12-gateway-api` | 3 | 0 | 375 | 2.83 | 4/6 | 1, contrast (light) ×2 |
| envoy-tutorial @ main | `13-httproute-traffic` | 2 | 0 | 375 | 2.67 | 4/4 | 1, contrast (light) ×3 |
| envoy-tutorial @ main | `14-gateway-policies` | 1 | 0 | 375 | 2.51 | 2/2 | 0 |
| envoy-tutorial @ main | `15-backend-tls-policy` | 1 | 0 | 375 | 2.51 | 2/2 | 0 |
| envoy-tutorial @ main | `16-keycloak` | 1 | 0 | 375 | 2.58 | 2/2 | 0 |
| envoy-tutorial @ main | `17-keycloak-jwt` | 1 | 0 | 375 | 2.57 | 2/2 | 0 |
| envoy-tutorial @ main | `18-keycloak-ldap` | 1 | 0 | 375 | 2.57 | 2/2 | 0 |
| envoy-tutorial @ main | `19-shop-gateway` | 1 | 0 | 375 | 2.60 | 2/2 | 0 |
| envoy-tutorial @ main | `20-shop-envoy` | 1 | 0 | 375 | 2.62 | 2/2 | 0 |
| envoy-tutorial @ main | `ingress-shard` | 1 | 0 | 375 | 2.59 | 2/2 | 0 |
| envoy-tutorial @ main | `metallb` | 1 | 0 | 375 | 2.20 | 2/2 | 1, fallback face ×2; contrast (light) ×2 |
| envoy-tutorial @ module-19-shop | `00-prerequisites` | 1 | 0 | 375 | 2.52 | 2/2 | 0 |
| envoy-tutorial @ module-19-shop | `01-what-is-envoy` | 2 | 0 | 375 | 2.66 | 4/4 | 0 |
| envoy-tutorial @ module-19-shop | `02-the-config-file` | 1 | 0 | 375 | 2.50 | 2/2 | 0 |
| envoy-tutorial @ module-19-shop | `03-listeners-and-filter-chains` | 1 | 0 | 375 | 2.55 | 2/2 | 0 |
| envoy-tutorial @ module-19-shop | `04-routing` | 2 | 0 | 375 | 2.71 | 4/4 | 1, contrast (light) ×36 |
| envoy-tutorial @ module-19-shop | `05-clusters-and-load-balancing` | 3 | 0 | 375 | 2.83 | 6/6 | 0 |
| envoy-tutorial @ module-19-shop | `06-http-filters` | 1 | 0 | 375 | 2.51 | 2/2 | 0 |
| envoy-tutorial @ module-19-shop | `07-modernising-grpc` | 2 | 0 | 375 | 2.64 | 1/4 | 0 |
| envoy-tutorial @ module-19-shop | `08-tls-on-envoy` | 2 | 0 | 375 | 2.70 | 4/4 | 0 |
| envoy-tutorial @ module-19-shop | `09-grpc-end-to-end` | 2 | 0 | 375 | 2.66 | 4/4 | 0 |
| envoy-tutorial @ module-19-shop | `10-observability` | 1 | 0 | 375 | 2.51 | 2/2 | 0 |
| envoy-tutorial @ module-19-shop | `11-resilience` | 2 | 0 | 375 | 2.67 | 4/4 | 0 |
| envoy-tutorial @ module-19-shop | `12-gateway-api` | 3 | 0 | 375 | 2.85 | 4/6 | 1, contrast (light) ×2 |
| envoy-tutorial @ module-19-shop | `13-httproute-traffic` | 2 | 0 | 375 | 2.64 | 4/4 | 1, contrast (light) ×3 |
| envoy-tutorial @ module-19-shop | `14-gateway-policies` | 1 | 0 | 375 | 2.52 | 2/2 | 0 |
| envoy-tutorial @ module-19-shop | `15-backend-tls-policy` | 1 | 0 | 375 | 2.49 | 2/2 | 0 |
| envoy-tutorial @ module-19-shop | `16-keycloak` | 1 | 0 | 375 | 2.50 | 2/2 | 0 |
| envoy-tutorial @ module-19-shop | `17-keycloak-jwt` | 1 | 0 | 375 | 2.52 | 2/2 | 0 |
| envoy-tutorial @ module-19-shop | `18-keycloak-ldap` | 1 | 0 | 375 | 2.54 | 2/2 | 0 |
| envoy-tutorial @ module-19-shop | `19-shop-gateway` | 1 | 0 | 375 | 2.58 | 2/2 | 0 |
| envoy-tutorial @ module-19-shop | `ingress-shard` | 1 | 0 | 375 | 2.54 | 2/2 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `00-prerequisites` | 1 | 0 | 375 | 2.51 | 2/2 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `01-what-is-envoy` | 2 | 0 | 375 | 2.73 | 4/4 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `02-the-config-file` | 1 | 0 | 375 | 2.55 | 2/2 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `03-listeners-and-filter-chains` | 1 | 0 | 375 | 2.51 | 2/2 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `04-routing` | 2 | 0 | 375 | 2.68 | 4/4 | 1, contrast (light) ×36 |
| envoy-tutorial @ module-20-shop-envoy | `05-clusters-and-load-balancing` | 3 | 0 | 375 | 2.85 | 6/6 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `06-http-filters` | 1 | 0 | 375 | 2.51 | 2/2 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `07-modernising-grpc` | 2 | 0 | 375 | 2.67 | 3/4 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `08-tls-on-envoy` | 2 | 0 | 375 | 2.68 | 4/4 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `09-grpc-end-to-end` | 2 | 0 | 375 | 2.66 | 4/4 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `10-observability` | 1 | 0 | 375 | 2.53 | 2/2 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `11-resilience` | 2 | 0 | 375 | 2.67 | 4/4 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `12-gateway-api` | 3 | 0 | 375 | 2.85 | 4/6 | 1, contrast (light) ×2 |
| envoy-tutorial @ module-20-shop-envoy | `13-httproute-traffic` | 2 | 0 | 375 | 2.67 | 2/4 | 1, contrast (light) ×3 |
| envoy-tutorial @ module-20-shop-envoy | `14-gateway-policies` | 1 | 0 | 375 | 2.57 | 2/2 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `15-backend-tls-policy` | 1 | 0 | 375 | 2.54 | 2/2 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `16-keycloak` | 1 | 0 | 375 | 2.52 | 2/2 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `17-keycloak-jwt` | 1 | 0 | 375 | 2.54 | 2/2 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `18-keycloak-ldap` | 1 | 0 | 375 | 2.54 | 2/2 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `19-shop-gateway` | 1 | 0 | 375 | 2.56 | 2/2 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `20-shop-envoy` | 1 | 0 | 375 | 2.59 | 2/2 | 0 |
| envoy-tutorial @ module-20-shop-envoy | `ingress-shard` | 1 | 0 | 375 | 2.54 | 2/2 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `00-prerequisites` | 1 | 0 | 375 | 2.54 | 2/2 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `01-what-is-envoy` | 2 | 0 | 375 | 2.66 | 4/4 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `02-the-config-file` | 1 | 0 | 375 | 2.52 | 2/2 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `03-listeners-and-filter-chains` | 1 | 0 | 375 | 2.48 | 2/2 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `04-routing` | 2 | 0 | 375 | 2.66 | 4/4 | 1, contrast (light) ×36 |
| envoy-tutorial @ metallb-ingress-shard | `05-clusters-and-load-balancing` | 3 | 0 | 375 | 2.86 | 6/6 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `06-http-filters` | 1 | 0 | 375 | 2.50 | 2/2 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `07-modernising-grpc` | 2 | 0 | 375 | 2.68 | 3/4 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `08-tls-on-envoy` | 2 | 0 | 375 | 2.66 | 2/4 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `09-grpc-end-to-end` | 2 | 0 | 375 | 2.66 | 4/4 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `10-observability` | 1 | 0 | 375 | 2.50 | 2/2 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `11-resilience` | 2 | 0 | 375 | 2.66 | 4/4 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `12-gateway-api` | 3 | 0 | 375 | 2.89 | 4/6 | 1, contrast (light) ×2 |
| envoy-tutorial @ metallb-ingress-shard | `13-httproute-traffic` | 2 | 0 | 375 | 2.69 | 4/4 | 1, contrast (light) ×3 |
| envoy-tutorial @ metallb-ingress-shard | `14-gateway-policies` | 1 | 0 | 375 | 2.52 | 2/2 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `15-backend-tls-policy` | 1 | 0 | 375 | 2.51 | 2/2 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `16-keycloak` | 1 | 0 | 375 | 2.49 | 2/2 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `17-keycloak-jwt` | 1 | 0 | 375 | 2.55 | 2/2 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `18-keycloak-ldap` | 1 | 0 | 375 | 2.55 | 2/2 | 0 |
| envoy-tutorial @ metallb-ingress-shard | `ingress-shard` | 1 | 0 | 375 | 2.53 | 2/2 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `00-prerequisites` | 1 | 0 | 375 | 2.55 | 2/2 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `01-what-is-envoy` | 2 | 0 | 375 | 2.65 | 4/4 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `02-the-config-file` | 1 | 0 | 375 | 2.49 | 2/2 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `03-listeners-and-filter-chains` | 1 | 0 | 375 | 2.49 | 2/2 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `04-routing` | 2 | 0 | 375 | 2.68 | 4/4 | 1, contrast (light) ×36 |
| envoy-tutorial @ module-18-keycloak-ldap | `05-clusters-and-load-balancing` | 3 | 0 | 375 | 2.81 | 6/6 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `06-http-filters` | 1 | 0 | 375 | 2.52 | 2/2 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `07-modernising-grpc` | 2 | 0 | 375 | 2.65 | 3/4 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `08-tls-on-envoy` | 2 | 0 | 375 | 2.67 | 2/4 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `09-grpc-end-to-end` | 2 | 0 | 375 | 2.66 | 4/4 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `10-observability` | 1 | 0 | 375 | 2.50 | 2/2 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `11-resilience` | 2 | 0 | 375 | 2.66 | 4/4 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `12-gateway-api` | 3 | 0 | 375 | 2.87 | 4/6 | 1, contrast (light) ×2 |
| envoy-tutorial @ module-18-keycloak-ldap | `13-httproute-traffic` | 2 | 0 | 375 | 2.72 | 4/4 | 1, contrast (light) ×3 |
| envoy-tutorial @ module-18-keycloak-ldap | `14-gateway-policies` | 1 | 0 | 375 | 2.53 | 2/2 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `15-backend-tls-policy` | 1 | 0 | 375 | 2.49 | 2/2 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `16-keycloak` | 1 | 0 | 375 | 2.52 | 2/2 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `17-keycloak-jwt` | 1 | 0 | 375 | 2.50 | 2/2 | 0 |
| envoy-tutorial @ module-18-keycloak-ldap | `18-keycloak-ldap` | 1 | 0 | 375 | 2.55 | 2/2 | 0 |
| envoy-tutorial @ module-17-corp | `00-prerequisites` | 1 | 0 | 375 | 2.52 | 2/2 | 0 |
| envoy-tutorial @ module-17-corp | `01-what-is-envoy` | 2 | 0 | 375 | 2.69 | 4/4 | 0 |
| envoy-tutorial @ module-17-corp | `02-the-config-file` | 1 | 0 | 375 | 2.51 | 1/2 | 0 |
| envoy-tutorial @ module-17-corp | `03-listeners-and-filter-chains` | 1 | 0 | 375 | 2.48 | 2/2 | 0 |
| envoy-tutorial @ module-17-corp | `04-routing` | 2 | 0 | 375 | 2.69 | 4/4 | 1, contrast (light) ×36 |
| envoy-tutorial @ module-17-corp | `05-clusters-and-load-balancing` | 3 | 0 | 375 | 2.83 | 6/6 | 0 |
| envoy-tutorial @ module-17-corp | `06-http-filters` | 1 | 0 | 375 | 2.51 | 2/2 | 0 |
| envoy-tutorial @ module-17-corp | `07-modernising-grpc` | 2 | 0 | 375 | 2.67 | 3/4 | 0 |
| envoy-tutorial @ module-17-corp | `08-tls-on-envoy` | 2 | 0 | 375 | 2.68 | 4/4 | 0 |
| envoy-tutorial @ module-17-corp | `09-grpc-end-to-end` | 2 | 0 | 375 | 2.67 | 4/4 | 0 |
| envoy-tutorial @ module-17-corp | `10-observability` | 1 | 0 | 375 | 2.47 | 2/2 | 0 |
| envoy-tutorial @ module-17-corp | `11-resilience` | 2 | 0 | 375 | 2.66 | 4/4 | 0 |
| envoy-tutorial @ module-17-corp | `12-gateway-api` | 3 | 0 | 375 | 2.87 | 4/6 | 1, contrast (light) ×2 |
| envoy-tutorial @ module-17-corp | `13-httproute-traffic` | 2 | 0 | 375 | 2.70 | 4/4 | 1, contrast (light) ×3 |
| envoy-tutorial @ module-17-corp | `14-gateway-policies` | 1 | 0 | 375 | 2.51 | 2/2 | 0 |
| envoy-tutorial @ module-17-corp | `15-backend-tls-policy` | 1 | 0 | 375 | 2.62 | 2/2 | 0 |
| envoy-tutorial @ module-17-corp | `16-keycloak` | 1 | 0 | 375 | 2.58 | 2/2 | 0 |
| envoy-tutorial @ module-17-corp | `17-keycloak-jwt` | 1 | 0 | 375 | 2.54 | 2/2 | 0 |
| envoy-tutorial @ module-17-corp | `18-keycloak-ldap` | 1 | 0 | 375 | 2.57 | 2/2 | 0 |
| envoy-tutorial @ permanent-lab | `00-prerequisites` | 1 | 0 | 375 | 3.77 | 2/2 | 0 |
| envoy-tutorial @ permanent-lab | `01-what-is-envoy` | 2 | 0 | 375 | 2.71 | 4/4 | 0 |
| envoy-tutorial @ permanent-lab | `02-the-config-file` | 1 | 0 | 375 | 2.53 | 2/2 | 0 |
| envoy-tutorial @ permanent-lab | `03-listeners-and-filter-chains` | 1 | 0 | 375 | 2.48 | 2/2 | 0 |
| envoy-tutorial @ permanent-lab | `04-routing` | 2 | 0 | 375 | 2.69 | 4/4 | 1, contrast (light) ×36 |
| envoy-tutorial @ permanent-lab | `05-clusters-and-load-balancing` | 3 | 0 | 375 | 2.81 | 6/6 | 0 |
| envoy-tutorial @ permanent-lab | `06-http-filters` | 1 | 0 | 375 | 2.50 | 2/2 | 0 |
| envoy-tutorial @ permanent-lab | `07-modernising-grpc` | 2 | 0 | 375 | 2.64 | 3/4 | 0 |
| envoy-tutorial @ permanent-lab | `08-tls-on-envoy` | 2 | 0 | 375 | 2.69 | 4/4 | 0 |
| envoy-tutorial @ permanent-lab | `09-grpc-end-to-end` | 2 | 0 | 375 | 2.67 | 4/4 | 0 |
| envoy-tutorial @ permanent-lab | `10-observability` | 1 | 0 | 375 | 2.48 | 2/2 | 0 |
| envoy-tutorial @ permanent-lab | `11-resilience` | 2 | 0 | 375 | 2.65 | 4/4 | 0 |
| envoy-tutorial @ permanent-lab | `12-gateway-api` | 3 | 0 | 375 | 2.84 | 4/6 | 1, contrast (light) ×2 |
| envoy-tutorial @ permanent-lab | `13-httproute-traffic` | 2 | 0 | 375 | 2.65 | 4/4 | 1, contrast (light) ×3 |
| envoy-tutorial @ permanent-lab | `14-gateway-policies` | 1 | 0 | 375 | 2.51 | 2/2 | 0 |
| envoy-tutorial @ permanent-lab | `15-backend-tls-policy` | 1 | 0 | 375 | 2.49 | 2/2 | 0 |
| envoy-tutorial @ permanent-lab | `16-keycloak` | 1 | 0 | 375 | 2.51 | 2/2 | 0 |
| envoy-tutorial @ permanent-lab | `17-keycloak-jwt` | 1 | 0 | 375 | 2.53 | 2/2 | 0 |
| envoy-tutorial @ permanent-lab | `18-keycloak-ldap` | 1 | 0 | 375 | 2.56 | 2/2 | 0 |
| group-sync-dashboard | `remote-cluster-access` | 4 | 0 | 375 | 3.11 | 2/8 | 1, contrast (light) ×5 |
| mongodb-poc | `envoy-flow` | 2 | 0 | 375 | 2.88 | 4/4 | 0 |
| mongodb-poc | `grpc-through-envoy` | 2 | 0 | 375 | 2.85 | 4/4 | 0 |
| mongodb-poc | `mongot-openshift` | 10 | 0 | 375 | 4.07 | 20/20 | 1, contrast (light) ×20 |
| mongodb-poc | `route-tls-options` | 2 | 0 | 375 | 2.69 | 4/4 | 1, contrast (light) ×2 |
| mongodb-poc | `search-and-sync` | 2 | 0 | 375 | 2.70 | 4/4 | 0 |
| mongodb-poc | `storage-nfs` | 1 | 0 | 375 | 2.50 | 2/2 | 0 |

