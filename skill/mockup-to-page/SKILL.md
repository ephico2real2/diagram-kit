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

## 6. Deliver

One PR per story in the project's flow: an issue, a branch, failing tests first, the smallest change, the gates,
review. Sample data stays in tests only. The PR lists every place the page differs from the mockup and why, and links
the mockup.
