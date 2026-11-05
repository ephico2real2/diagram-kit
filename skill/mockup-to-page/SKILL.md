---
name: mockup-to-page
description: Translate a /build-mockup mockup into the real page in the framework its $target declares (react-ts or preact-ts) - tokens to tokens.css, declared state to URL or storage, typed datasets to API schemas and fetch hooks, each section type to one component - then prove it matches the mockup at 390/820/1440 px in both themes, with every UI state the mockup shows and its actions that obey permissions, and accessibility and contract tests in CI. Use when the user types /mockup-to-page, or asks to build, implement or code a page, screen or dashboard from an approved mockup.
---

# /mockup-to-page — the page, translated from its mockup

`/mockup-to-page <the mockup, the story>` translates a `/build-mockup` mockup into the real page in the framework its
`$target` declares. Tokens, state keys, typed datasets and section types map one-to-one. If the mockup doesn't follow
`/build-mockup` (no `$target`, hex in markup, untyped datasets, unknown section types), fix the mockup first and say
so; don't guess.

This skill and `/build-mockup` are one standard: change them together. Proven on Inkcast, where the standard was
decided (ADR-0016, issue #235) and a copy lives in `docs/tooling/mockup-standard.md`. Section 7 translates the
example mockup `skill/build-mockup/example/workspaces.html` to `react-ts`. A mockup whose `$target` is `react-pf-ts`
goes to `/mockup-to-page-react` instead.

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
- Each name on a dataset's `// states` line becomes one branch of its section component, with the words and the
  `role` of the mockup. A dataset without that line still gets `loading`, `empty` and `error`, because each request
  can cause them. Tell the mockup's owner, so that the mockup gets the line.

| Mockup state | What causes it on the page | `react-ts` and `preact-ts` |
|---|---|---|
| `loading` | The request did not answer yet. | A skeleton with `aria-hidden`, and one `<p role="status">` line |
| `empty` | A 200 answer with no rows. It is not a request state. Use the number of rows to find it. | The words of the mockup, and its next action |
| `error` | A 5xx answer, or a network fault. | `role="alert"`, and a "Try again" button that sends the request again |
| `forbidden` | A 403 answer. | The words of the mockup. No retry, and no data of the section |
| `conflict` | A 409 or a 412 answer to a change, or a version older than the server's. | `role="alert"`, and a "Reload" button. The old rows stay until the person reloads |
| `success` | A 2xx answer to an action. | One `role="status"` line, with the focus moved to it, and the new data |

- Other answers do not get a state of their own in the section, because the six states are the whole list:
  - 401: the session ended. The app shell signs the person in again and then sends the request again. The section
    does not show it.
  - 404 to a read of one object: the object is not there. Show it as `empty`, with the words of the mockup.
  - 422 to a change: the form shows each field error under its input, as `/build-mockup` section 8 says. The section
    keeps its data.
  - 429: show it as `error`. When `Retry-After` gives a number of seconds, the cause says how long to wait.
- If the mockup needs words for one of these answers, the mockup's owner adds them, and the mockup shows them.
- Permissions come from the API answer (`canDelete`, `whyNot`). Do not calculate a permission in the browser from a
  role name. The server enforces each permission. A contract test sends a request without the permission. The
  answer is 403.
- A secret or a token is never in a fixture, a log, a screenshot or the URL. The page shows a new token one time.

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

## 7. Example: one section in `react-ts`

The example that follows translates the `row-list` section of `skill/build-mockup/example/workspaces.html`. The types
come from its `// type` lines. The `Result` union comes from its `// states` line. The fetch comes from its
`// dataset` line, and its HTTP answers from section 4. `signIn` comes from the app shell. The words, the `role` attributes and the disabled action with its reason come from its markup. The
code compiles with `tsc --strict` (React 19.3.1, TypeScript 7.0.2, on 2026-11-05).

```tsx
import { useEffect, useRef } from 'react';
import { signIn } from './session'; // the app shell's sign-in, from the project's OIDC client

// types.ts: from the `// type` and `// states` lines of the mockup
export type Workspace = {
  name: string; team: 'Payments' | 'Data' | 'Web'; state: 'ready' | 'pending' | 'failed';
  cpuUsed: number; cpuQuota: number; canDelete: boolean; whyNot?: string;
};
export type Page<T> = { items: T[]; next?: string };
export type Result<T> =
  | { state: 'loading' } | { state: 'error'; cause: string } | { state: 'forbidden' }
  | { state: 'conflict' | 'ready'; data: T } | { state: 'success'; data: T; done: string };

// api/workspaces.ts: from `// dataset workspaces: GET /api/workspaces?cursor&team → Page<Workspace>`.
// A network fault rejects the promise: the caller shows it as `error` (see the Query hook in /mockup-to-page-react).
// The other answers follow section 4. This is a list, so a 404 is a fault, not one object that is not there.
export async function getWorkspaces(query: URLSearchParams, signal: AbortSignal): Promise<Result<Page<Workspace>>> {
  const response = await fetch(`/api/workspaces?${query}`, { signal });
  if (response.status === 401) { signIn(); return { state: 'loading' }; } // the shell signs in; the section waits
  if (response.status === 403) return { state: 'forbidden' };
  if (response.status === 429) {
    const wait = Number(response.headers.get('Retry-After')); // seconds; an HTTP date gives NaN and no wait
    return { state: 'error', cause: Number.isInteger(wait) && wait > 0
      ? `The server is busy. Try again in ${wait} seconds.` : 'The server is busy.' };
  }
  if (!response.ok) return { state: 'error', cause: `The server sent HTTP ${response.status}.` };
  return { state: 'ready', data: (await response.json()) as Page<Workspace> };
}

// components/RowList.tsx: data-component="row-list" data-dataset="workspaces"
export function WorkspaceList({ result, onReload, onDelete }:
  { result: Result<Page<Workspace>>; onReload: () => void; onDelete: (name: string) => void }) {
  const done = useRef<HTMLParagraphElement>(null);
  useEffect(() => { if (result.state === 'success') done.current?.focus(); }, [result.state]);
  if (result.state === 'loading') return <p role="status">Loading workspaces…</p>;
  if (result.state === 'error') return (
    <div role="alert" className="banner stop">
      <p>The workspaces did not load. {result.cause}</p>
      <button type="button" onClick={onReload}>Try again</button>
    </div>);
  if (result.state === 'forbidden') return (
    <p className="banner stop">You do not have permission to see workspaces. Ask a workspace admin for the viewer role.</p>);
  if (result.data.items.length === 0) return <p className="banner info">There are no workspaces.</p>;
  return (<>
    {result.state === 'conflict' && (
      <div role="alert" className="banner warn">
        <p>This list changed after you opened it. Reload the list to see the current workspaces.</p>
        <button type="button" onClick={onReload}>Reload</button>
      </div>)}
    {result.state === 'success' && (
      <p role="status" className="banner ok" tabIndex={-1} ref={done}>Workspace {result.done} is deleted.</p>)}
    <table>
      <thead><tr><th scope="col">Name</th><th scope="col">State</th><th scope="col"><span className="sr">Actions</span></th></tr></thead>
      <tbody>{result.data.items.map((w) => (
        <tr key={w.name}>
          <td data-label="Name">{w.name}</td>
          <td data-label="State"><span className={`badge ${w.state}`}>{w.state}</span></td>
          <td data-label="Actions">{w.canDelete
            ? <button type="button" className="danger" aria-label={`Delete ${w.name}`} onClick={() => onDelete(w.name)}>Delete</button>
            : <><button type="button" aria-disabled="true" aria-label={`Delete ${w.name}`} aria-describedby={`why-${w.name}`}>Delete</button>
                <span className="why" id={`why-${w.name}`}>{w.whyNot}</span></>}</td>
        </tr>))}</tbody>
    </table>
  </>);
}
```

For `preact-ts`, import the hooks from `preact/hooks`. Then set `jsxImportSource: "preact"` (section 1). Nothing else
changes. The code compiles the same way with Preact 11.1.1. `/mockup-to-page-react` translates the same section to
PatternFly.
