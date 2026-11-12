---
name: mockup-to-page-react
description: Translate an app mockup into the real page in React, TypeScript, Vite and PatternFly - the mockup's tabs, state, data and behaviour kept, its look replaced by PatternFly's components and design tokens, typed datasets to API schemas and TanStack Query hooks, each section type to one PatternFly composition, each UI state and permission of the mockup kept - then prove it matches on content, states and behaviour at 390/820/1440 px in both themes, with accessibility and contract tests in CI. Use when the user types /mockup-to-page-react, or asks to build a page, screen or portal from a mockup with React and PatternFly, or for an OpenShift-style console UI.
---

# /mockup-to-page-react — the page, translated from its mockup, on PatternFly

`/mockup-to-page-react <the mockup, the story>` translates a mockup into a real page in React with TypeScript, built
with Vite, using PatternFly as the component library. Use it when the page should look and behave like the OpenShift
console and its family. Use `/mockup-to-page` when the page must look like the mockup.

This skill and `/build-mockup` are one standard: change them together. Section 8 translates the example mockup
`skill/build-mockup/example/workspaces.html` to PatternFly.

## What "matches the mockup" means here

PatternFly draws its own components, so a pixel diff against the mockup can never pass, and a page forced to pass one
would fight the library. The mockup is the contract for what the page **says and does**. PatternFly decides how it
looks.

| Kept from the mockup, and tested | Replaced by PatternFly |
|---|---|
| Tabs, sections and their order | Colours, spacing, type, radii, shadows |
| Every label, value, heading and message | The mockup's CSS and its fonts |
| Data shown, sort order, paging, filters | Control shapes (a pill may become a `Label`) |
| States: empty, error, disabled, read-only | Hover, focus and motion |
| Every action and what it leads to | The exact pixel layout of a section |

Never restyle a PatternFly component to look like the mockup. Never carry the mockup's CSS across. A place where
PatternFly has no fit for what the mockup does is a written decision in the PR, not a hand-built lookalike.

## 0. Inputs

- The mockup: canvas files (`Main.dc.html`) or the repo's `mockups/` HTML, and the running render of it.
- The story with acceptance criteria, and the project's own workflow (issue, branch, failing tests first, gates, PR,
  review).
- **A mockup that follows `/build-mockup`** (`$target: react-pf-ts`, typed datasets, section types) translates directly.
- **A mockup that does not** gets an inventory first, written to `<app>/MOCKUP-CONTRACT.md` and confirmed with the
  owner before any component is written: each tab, its state keys, its datasets with the API behind each, its section
  types, its actions. The mockup's CSS is ignored either way. Don't guess at a tab you have not run.
- **Work from the file, not from memory.** Read each part of the mockup in full, untruncated, before writing it. Copy
  text mechanically. An invented heading or sentence is a defect.

## 1. Stack

Look up current versions with `npm view <package> version peerDependencies` and pin them exactly. Do not name versions
from memory: PatternFly renames tokens and props between major versions.

| Need | Use |
|---|---|
| Build | Vite with `@vitejs/plugin-react`, to static files; no CDN, works offline |
| Language | TypeScript in strict mode; types come from the OpenAPI schema where one exists |
| Components | `@patternfly/react-core`, `@patternfly/react-table`, `@patternfly/react-icons` |
| Charts | `@patternfly/react-charts`, only when a page has charts (it brings its own peers) |
| Server state | TanStack Query (`@tanstack/react-query`), one typed hook per endpoint |
| URL state | The project's router, else `URLSearchParams` and `history.replaceState` |
| Sign-in | The project's OIDC client, with PKCE; none in the page itself |
| Tests | Vitest and Testing Library for components; Playwright with `@axe-core/playwright` for the page |

Import once, in the entry file, in this order: `@patternfly/react-core/dist/styles/base.css`, then
`@patternfly/patternfly/patternfly-addons.css` if utility classes are used, then the app's own small stylesheet.
PatternFly ships its fonts in `assets/fonts`, so the page needs no font CDN.

## 2. Mapping

| Mockup | PatternFly |
|---|---|
| The app shell, `app-header` | `Page`, `Masthead`, `PageSection` |
| Tabs | `Tabs` and `Tab`, or `Nav` with routes when each tab is its own URL |
| `segmented` | `ToggleGroup` and `ToggleGroupItem` (`isSelected`, `onChange`) |
| `row-list`, any table | `Table`, `Thead`, `Tbody`, `Tr`, `Th`, `Td` with `gridBreakPoint="grid-md"` and `dataLabel` on every `Td`, so rows stack on a phone |
| Filters and search above a list | `Toolbar`, `ToolbarContent`, `ToolbarFilter`, `SearchInput`, `Select` |
| Paging | `Pagination` when the API can jump to a page; next and previous `Button`s with the range text when it pages by cursor, since `Pagination` expects any page to be reachable |
| `kpi-tiles`, `card-grid` | `Gallery` of `Card`, or `Grid`; `DescriptionList` for label and value pairs |
| `stat-strip` | One `Card` with `Flex` and `DescriptionList` |
| `bar-list`, a usage meter | `Progress` with its `label`, `value` and `valueText`, in a `Table` or `Stack`. PatternFly hides the visible label from screen readers, so `valueText` carries it |
| `time-series` | `@patternfly/react-charts`, with the values also in a table |
| `heat-grid` | `Table` with `isStickyHeader`; each cell carries its value in text |
| `callout` | `Alert`, with `CodeBlock` for a command |
| Status words, tones, chips | `Label` with `status` or `color`; always with its word |
| A form | `Form`, `FormGroup`, `TextInput`, `FormSelect`, `TextArea`, `DatePicker`, `FormHelperText`. `Form` sets `noValidate`: pass `noValidate={false}` where the mockup relies on `required`, `min`, `max`, `step` or `type="email"` |
| A multi-step flow | `Wizard` only when the steps collect input; a read-only stepper is `ProgressStepper` |
| Code, YAML, a diff | `CodeBlock` |
| Empty, loading, error | `EmptyState`, `Skeleton` or `Spinner`, `Alert`; each list has all three |
| `loading` state | `Skeleton` in the shape of the content, and one line with `role="status"` |
| `empty` state | `EmptyState` with the mockup's words, and its next action as a `Button` |
| `error` state | `Alert variant="danger" isInline`, with an `AlertActionLink` "Try again" |
| `forbidden` state | `EmptyState` with `LockIcon` and the mockup's words. No retry |
| `conflict` state | `Alert variant="warning" isInline`, with an `AlertActionLink` "Reload". The old rows stay |
| `success` state | `Alert variant="success" isInline isLiveRegion`, with the focus moved to it |
| An action that the person cannot do | `Button isAriaDisabled`, with `aria-describedby` on the reason in visible text. A `Tooltip` alone is not enough, because a touch screen does not show it |
| A confirm or a reason | `Modal` |
| A new token, shown one time | `Alert variant="success" isInline` with the focus moved to it, and the token in a `ClipboardCopy isReadOnly`. The token is never in a query key, the URL or a fixture |
| Layout | `Stack`, `Flex`, `Grid`, `Gallery`, `Split`, `Level`; not hand-written CSS grids |

One `data-component` type, or one inventory section, is one `.tsx` component in `components/`. A section with a state
of its own keeps it in that component. Keep the mockup's accessible names; PatternFly brings the keyboard behaviour.

## 3. Colour and theme

- Use PatternFly's semantic tokens, `var(--pf-t--global--...)`. No hex and no palette token in app CSS.
- A mockup colour with a meaning maps to a status or a `Label` colour: success, warning, danger, info. A category
  colour maps to a `Label` `color` and keeps it on every tab.
- Dark theme is the `pf-v6-theme-dark` class on `<html>`, remembered per browser in try/catch, with the configured
  default. A page specified as light only says so in its contract and does not add a switch. Check the class against
  the installed major version when upgrading.

## 4. State

- Each `url=` key, or each state key a person would share, is read on load and written on change with
  `history.replaceState`; an invalid value falls back to the default.
- Server data lives in TanStack Query, not in component state. Selection, an open row and a draft stay local.
- `view` and `role` are preview props of the mockup. The page does not keep them. The query's answer gives the state,
  and the API gives the permissions (`canDelete`, `whyNot`). Do not calculate a permission from a role name.
- Lifted state goes in the app component as props. Add no state library for what the URL and Query already hold.

## 5. Data

- Each dataset is an endpoint with a typed response schema. Write the schema first, with the mockup's sample data as
  the test fixture. The fixture renders the page like the mockup.
- Cursor paging: one query per page keyed on its cursor and filters, keeping the previous page while the next loads.
- Filters, sort and search are server parameters, never filtered only in the browser. Type-ahead debounces and cancels
  the previous call through the signal Query passes in.
- Permissions come only from the API answer (`canDelete`, `whyNot`). Never calculate them from the `role` preview
  prop or from a group name in the browser. The server enforces each permission. A contract test sends the request
  without the permission and gets 403.
- A secret or a token is never in a fixture, a log, a screenshot or the URL. Show a new token one time, then drop it
  from memory. Do not keep it in the Query cache.
- A 401, a 404, a 422 and a 429 get the treatment in `/mockup-to-page` section 4. They get no new state.
- Mock the API at the network layer in tests and local runs (MSW, or the project's fake). Sample data never reaches the
  production bundle: assert it.
- Contract tests: the server's real response matches the schema. If there is no server yet, say so in the PR and mark
  those tests pending; don't let the fixture stand in for them.
- Logic that belongs to the server (approval, placement, validation) goes behind the API. Port it into the page only
  as a test fixture, and name it as such.
- **No API yet, and the owner wants the page now:** the mockup's logic class may stand in for the API behind one
  module, extracted from the mockup at build time so there is still one source. Components take view-model props, so
  query hooks replace the module later. Write down what this leaves undone (sample data in the bundle, no loading or
  error states, no sign-in, browser-side filtering) and that the result must not be deployed as the real page.

## 6. Prove it matches

Run against both the mockup's render and the page, by the method in `/test-ui`. A difference is fixed, or listed and
justified in the PR.

1. **Content parity, per tab and state, in both directions.** Drive the mockup and the page to the same state. Every
   string the mockup shows is on the page, and every string the page shows is in the mockup, or is listed. Text alone is
   not enough: also compare tables cell by cell, status colours, selection, disabled buttons and meter values.
2. **Behaviour parity.** The same scripted walk runs on both: each action, its result, and the states it leads to. No
   console errors.
3. **Layout checks at 390, 820 and 1440 px, in each theme.** No sideways scroll on the page, no leftover placeholders,
   and tables stack at their breakpoint. Screenshots are kept as artifacts and looked at. They are for people to read;
   they are not diffed against the mockup.
4. **Accessibility.** An axe scan with no serious issues on each tab. Keyboard through every control, including a
   `Select`, a `Modal` and the table's sort headers.
5. **PatternFly discipline.** Fail the build on a hex colour in app CSS, on an override of a `.pf-v6-` class, and on
   `!important`. An override the page truly needs is a line in the PR with its reason.
6. **Gates.** `tsc --noEmit`, the unit tests, `vite build`, the page tests. All of it in CI.

## 7. Deliver

One PR per story in the project's flow: an issue, a branch, failing tests first, the smallest change, the gates,
`/adversarial-review`. The PR holds the content-parity table per tab, screenshots per tab and theme, every place the
page differs from the mockup with the reason, and a link to the mockup.

## 8. Example: one section on PatternFly

The example that follows shows the `row-list` section of `skill/build-mockup/example/workspaces.html` on PatternFly.
The `Result`, `Page` and `Workspace` types are the ones in `/mockup-to-page` section 8. They come from the mockup's
`// type` and `// states` lines. The words and the order of the states are the mockup's. PatternFly gives the look.
The code compiles with `tsc --strict` (React 19.3.1, PatternFly 6.7.0, TanStack Query 5.106.0, TypeScript 7.0.2, on
2026-11-05).

```tsx
import { useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Alert, AlertActionLink, Button, EmptyState, EmptyStateBody, Label, Skeleton, Stack } from '@patternfly/react-core';
import { LockIcon } from '@patternfly/react-icons';
import { Table, Tbody, Td, Th, Thead, Tr } from '@patternfly/react-table';
import { getWorkspaces, type Page, type Result, type Workspace } from './workspaces'; // the types and fetch of /mockup-to-page section 8

const TONE = { ready: 'success', pending: 'info', failed: 'danger' } as const;

// api/workspaces.ts: one query per page, keyed on its filters; a network fault is the `error` state, not `loading`
export function useWorkspaces(query: URLSearchParams): Result<Page<Workspace>> {
  const { data, isError } = useQuery({
    queryKey: ['workspaces', query.toString()], queryFn: ({ signal }) => getWorkspaces(query, signal),
    retry: false }); // the "Try again" button is the retry
  if (isError) return { state: 'error', cause: 'The network did not answer.' };
  return data ?? { state: 'loading' };
}

// components/WorkspaceList.tsx: data-component="row-list" data-dataset="workspaces"
export function WorkspaceList({ result, onReload, onDelete }:
  { result: Result<Page<Workspace>>; onReload: () => void; onDelete: (name: string) => void }) {
  const done = useRef<HTMLDivElement>(null);
  useEffect(() => { if (result.state === 'success') done.current?.focus(); }, [result.state]);
  if (result.state === 'loading') return (
    <Stack hasGutter><span role="status">Loading workspaces…</span><Skeleton /><Skeleton /><Skeleton /></Stack>);
  if (result.state === 'error') return (
    <Alert variant="danger" isInline title="The workspaces did not load."
      actionLinks={<AlertActionLink onClick={onReload}>Try again</AlertActionLink>}>
      {result.cause}
    </Alert>);
  if (result.state === 'forbidden') return (
    <EmptyState titleText="You do not have permission to see workspaces." headingLevel="h3" icon={LockIcon}>
      <EmptyStateBody>Ask a workspace admin for the viewer role.</EmptyStateBody>
    </EmptyState>);
  if (result.data.items.length === 0) return <EmptyState titleText="There are no workspaces." headingLevel="h3" />;
  return (<Stack hasGutter>
    {result.state === 'conflict' && (
      <Alert variant="warning" isInline title="This list changed after you opened it."
        actionLinks={<AlertActionLink onClick={onReload}>Reload</AlertActionLink>} />)}
    {result.state === 'success' && (
      <div tabIndex={-1} ref={done}><Alert variant="success" isInline isLiveRegion title={`Workspace ${result.done} is deleted.`} /></div>)}
    <Table aria-label="Workspaces" gridBreakPoint="grid-md">
      <Thead><Tr><Th>Name</Th><Th>State</Th><Th screenReaderText="Actions" /></Tr></Thead>
      <Tbody>{result.data.items.map((w) => (
        <Tr key={w.name}>
          <Td dataLabel="Name">{w.name}</Td>
          <Td dataLabel="State"><Label status={TONE[w.state]}>{w.state}</Label></Td>
          <Td dataLabel="Actions">
            <Button variant="danger" isAriaDisabled={!w.canDelete} aria-label={`Delete ${w.name}`}
              aria-describedby={w.canDelete ? undefined : `why-${w.name}`} onClick={() => onDelete(w.name)}>Delete</Button>
            {!w.canDelete && <div id={`why-${w.name}`}>{w.whyNot}</div>}
          </Td>
        </Tr>))}</Tbody>
    </Table>
  </Stack>);
}
```

`useWorkspaces` gives the section its `result`. A network fault makes the fetch reject. Query then holds no data, so
the hook maps `isError` to `error`. Without the `if (isError)` line, the section stays in `loading`. Query tries a
failed request 3 more times by default, with waits of 1, 2 and 4 seconds. During that time the section shows
`loading`, for about 7 seconds. `retry: false` shows the `error` state at once, and its "Try again" button sends the
request again.
