---
name: mockup-to-page
description: Translate a /build-mockup mockup into the real page in the framework its $target declares (react-ts or preact-ts) - tokens to tokens.css, declared state to URL or storage, typed datasets to API schemas and fetch hooks, each section type to one component - then prove it matches the mockup at 390/820/1440 px in both themes, with accessibility and contract tests in CI. Use when the user types /mockup-to-page, or asks to build, implement or code a page, screen or dashboard from an approved mockup.
---

# /mockup-to-page — the page, translated from its mockup

`/mockup-to-page <the mockup, the story>` translates a `/build-mockup` mockup into the real page in the framework its
`$target` declares. Tokens, state keys, typed datasets and section types map one-to-one. If the mockup doesn't follow
`/build-mockup` (no `$target`, hex in markup, untyped datasets, unknown section types), fix the mockup first and say
so; don't guess.

This skill and `/build-mockup` are one standard: change them together. Proven on Inkcast, where the standard was
decided (ADR-0016, issue #235) and a copy lives in `docs/tooling/mockup-standard.md`.

## 0. Inputs

- The mockup: canvas files (`Main.dc.html`, tokens sheet) or the repo's `mockups/` HTML, plus its `$target`.
- The story with acceptance criteria, and the project's own workflow (Inkcast: issue, branch, failing tests first,
  gates, PR, review).
- Use the libraries the project already has. Add a dependency only if the project's rules allow it, pinned.

## 1. Framework mapping

Both targets use function components, hooks and JSX, so components written for one move to the other by changing
imports.

| Mockup | `react-ts` (a full web app, e.g. Inkcast's) | `preact-ts` (embedded page, e.g. tokensave dashboard) |
|---|---|---|
| imports | `react` | `preact`, `preact/hooks`; `preact/compat` only for a React-only library |
| token tables | `tokens.css` with CSS variables, imported once | the same `tokens.css`, linked from `index.html` |
| theme state | context setting `data-theme` on `<html>`; storage in try/catch | the same, with `preact/hooks` (or `@preact/signals` if the project uses it) |
| URL state (`url=`) | the router's search params | `URLSearchParams` + `history.replaceState` in the app component |
| `owner=App` state | lifted to the app component, passed as props | the same |
| local section state | `useState` in that component | `useState` from `preact/hooks` |
| dataset + `// dataset` source | typed fetch hook per endpoint (the project's data library, else `fetch`), schema in `api/` | one typed `fetch` module per endpoint, a small `useResource` hook |
| each `data-component` type | one `.tsx` component in `components/` | one `.tsx` component in `components/` (`jsxImportSource: "preact"`) |
| `<sc-for>` | `.map()` with a stable `key` | the same |
| `<sc-if>` | conditional render | the same |
| handler props (`onClick="{{x}}"`) | `onClick` | `onClick` |
| helmet media queries | media queries in the component's CSS (the project's way), at the mockup's breakpoints | one stylesheet or CSS modules via Vite, same breakpoints |
| build | the project's existing bundler | Vite + `@preact/preset-vite` to static files (one JS bundle, `tokens.css`, `index.html`) embedded in the binary at compile time; no CDN, works offline; Node only at build |
| tests | the project's runner + Testing Library | Vitest + `@testing-library/preact` |

Types come straight from the mockup's `// type` comments into `types.ts`, shared by the API layer and the components.
Keep the mockup's markup structure and accessibility attributes (buttons, `aria-current`, `aria-pressed`, labels);
charts get text values (a tooltip and a table view).

## 2. Tokens

- Generate `tokens.css` from the two tables: `:root[data-theme=dark]`, `:root[data-theme=light]`, and
  `:root[data-theme=auto]` resolved with `@media (prefers-color-scheme: …)`. Categories become `--cat-<name>`.
  Components use only `var(--token)`: no hex anywhere else.
- The page sets `data-theme` from the user's choice, remembered per browser, falling back to the configured default.
- A contrast test reads `tokens.css` and checks every pair the mockup's rules name, in both themes.

## 3. State

Each `url=` key is read on load and written on change (`history.replaceState`); invalid values fall back to the
default. The theme uses storage, never the URL. Defaults come from the project's config (e.g. `dashboard.toml`), else
the mockup's.

## 4. Data

- Each `// dataset` becomes an endpoint with a typed response schema. Write the schema first, with the mockup's sample
  data as the test fixture; the fixture renders the page like the mockup.
- Contract tests: the server's real response matches the schema. Everything that followed `range` or a filter is a
  server-side parameter, never filtered only in the browser.
- Add loading, empty and error states to every section, in the same section type (the mockup shows the full state).

## 5. Prove it matches the mockup

1. Render the page with the fixture at 390, 820 and 1440 px in both themes; compare to the mockup's screenshots with a
   pixel diff and a small tolerance. Larger differences are fixed, or listed and justified in the PR.
2. The `/build-mockup` checks: no sideways scroll, background fills, no leftover placeholders.
3. Accessibility scan (axe or equivalent) with no serious issues; keyboard through every control.
4. All of it in CI (Playwright), with screenshots kept as artifacts.
5. After the merge, capture the page on the deployed local stack with real data, and add the pictures with the stage
   `deployed-local` (section 7). A render with the fixture is `built-mocked`.

## 6. Deliver

One PR per story in the project's flow: an issue, a branch, failing tests first, the smallest change, the gates,
review. Sample data stays in tests only. The PR lists every place the page differs from the mockup and why, and links
the mockup.

## 7. Label the stage of each picture

Each picture tells the reader what it shows: a design, the real code with mocked data, or the deployed product. Each
picture has one stage:

| Stage | What made it |
|---|---|
| `mockup` | The design canvas of `/build-mockup` |
| `built-mocked` | The real page code, with mocked or fixture replies (a dev server with route mocks, a unit render) |
| `deployed-local` | The real stack on the local machine, behind its real edge, with data from the seed and a load run |

A picture with mocked replies is never called deployed. A later stage for a shared environment uses its own name.

1. The path names the stage: `<feature>/<stage>/<state>-<width or device>.png`.
2. Each PNG has a JSON file beside it, with the same name:

   ```json
   {
     "stage": "deployed-local",
     "commits": {"api": "d118c21", "web": "ce28850"},
     "stack": "the compose project and the start command",
     "data": {"seed": "<hash of the seed file>", "load_run": "<id of the load run>"},
     "width": 1440,
     "captured_utc": "2026-11-09T23:30:00Z",
     "command": "node scripts/capture-deployed.mjs --feature <feature>",
     "test_case": "TC-<story>-<nn>"
   }
   ```

   `captured_utc` comes from the clock (`date -u`), never from memory. A mobile picture names `device` in place of
   `width`.
3. Before a `deployed-local` capture, fill the screens with data. Operate the seed and a load run (for example a k6
   profile) on the local stack. A screen with no data source is a defect to file, never a fake row.
4. For each `deployed-local` picture, keep the API reply and the edge access log line of the same request. They prove
   that the picture came from the deployed stack.
5. The README of the mockups opens with a stage table: feature, design, mockup approved, built (pull request),
   deployed locally (date and commits), and the newest picture with its stage.
6. A history document (for example `UI-PROGRESS.md`) shows every picture of a feature in stage order: `mockup`, then
   `built-mocked`, then `deployed-local`. It never deletes an old picture. Each picture has a caption with its stage,
   its commits and its date.
7. A check in the repository's CI finds each picture with no JSON file, with an unknown stage, or in the folder of
   another stage. Each such picture makes the check fail.
