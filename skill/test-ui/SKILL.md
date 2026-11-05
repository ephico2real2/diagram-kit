---
name: test-ui
description: Test a web UI against the thing it must match - a reference runtime, a mockup or a design file - with evidence instead of impressions. Compares canonical DOM and pixels with the real reference, walks every interaction recording DOM, focus and caret at each step, checks content in both directions so nothing is missing or invented, proves each check can fail by mutating the code, scans layout and accessibility at phone and desktop widths, and repeats it all in the installed browser. Use when the user types /test-ui, asks how to test or verify a UI, or before calling a page, renderer or mockup translation done.
---

# /test-ui — prove a UI matches, and show the evidence

`/test-ui <the page, what it must match>` tests a UI against its reference and reports what was measured. "Looks right"
is not a result, and neither is a test that has never failed.

The method comes from the cmapi portal, where a small renderer had to match a design runtime and a PatternFly app had
to match a mockup. Each rule below names what it caught there.

## 0. Know what you are matching, from the file

- Read the reference in full, not truncated output and not memory. A paraphrase from a cut-off line shipped an invented
  sentence and an invented column heading in the portal; re-reading found both.
- Name the oracle and how strong it is, and say so in the report:

| Oracle | Strength | Allows the claim |
|---|---|---|
| The real runtime or the deployed page | Strongest: compare DOM and pixels | "Matches" |
| Screenshots of the real thing | Pixels only, one state each | "Matches at these views" |
| The real runtime's code, run locally | Strong, but not the deployment | "Matches the runtime", never "matches production" |
| A different design system on purpose | Content and behaviour only | "Says and does the same", never a pixel claim |

- Look for the real runtime before writing a test. The portal's published canvas shipped `dc-runtime.js`, and running it
  locally beat any screenshot set. Reading it also gave the rules a guess would have missed: loops add no wrapper
  element, text holes render in a `span`, and a whitespace run is kept only if it holds a space.
- Never claim more than the oracle allows. If the owner asked for a comparison you cannot make, say what you ran instead
  and ask for what is missing.

## Set up first

Install what the suites need, and tell an environment failure from a test failure before reporting either.

- **Node:** `npm install`, then `npx playwright install chromium`, in each folder with a `package.json` of tests.
- **Python:** a virtualenv per clone, then run its own `pytest`, never one from the PATH:
  `python3 -m venv .venv`, `.venv/bin/pip install ".[test]"`, `.venv/bin/playwright install chromium`,
  `.venv/bin/python -m pytest tests -q`.
- `ModuleNotFoundError` at collection means the environment is not set up. Install it and run again; do not report it as
  a result, and do not call it harmless and move on. Running only the tests that happen to import proves nothing about
  the rest.
- A skip is not a pass. Read the reason (`-rs`), then install what it needs or name it in the report.

## 1. Compare DOM and pixels, and read them together

Capture each view from both sides with one driver, reaching views by clicking the UI's own controls, so the same script
runs on both.

- **Canonical DOM.** Walk the tree to a string: attributes sorted, the reference's bookkeeping attributes dropped,
  styles read through `el.style.cssText`, and live properties included (`.value`, `.disabled`), because attributes do
  not show them.
- **Pixels.** One viewport, `deviceScaleFactor: 1`, fonts awaited, animations disabled, caret hidden. Screenshot the
  content element, not the page, so your own chrome is outside it.

The two answer different questions. **DOM identical with pixels different means the cause is outside the tree.** In the
portal every view had identical DOM and up to 1.4% pixel difference; measuring found the artboard at y = 32.1875, because
the page's own bar had a fractional height. Fixed, all 13 views went to 0.000%. A pixel threshold alone would have passed
some views and hidden the cause.

## 2. Walk every interaction, recording each step

Script what a person does, and record at every step: the canonical DOM, which element has focus, and the caret position.

- Cover each path to its end: every scenario on every instance, paging forward to the last page and all the way back,
  each filter and sort, type-ahead, each form, approve, reject, and the refusals (an empty required reason).
- Assert behaviour by name in the walk: the caret after typing in the middle of a field, not only at the end.
- Run the same walk on the reference, save the transcript, and compare per step. In the portal 178 of 180 steps matched
  at once; the other two showed the reference mirroring a textarea's value into its text child.
- Fail on console errors. Keep the walk deterministic: test a timer in a separate check, not in the transcript.

When a walk fails, check your assumption before the code. Two walk failures in the portal were the test's: instance
buttons labelled differently from what was assumed, and requests the user could not act on.

## 3. Check content in both directions

When the look legitimately differs, compare text. Drive both sides to the same state, normalize whitespace away, and at
every state check:

- **Nothing missing:** every string the reference shows is on the page. Skip `aria-hidden` decoration.
- **Nothing invented:** every string the page shows is in the reference, apart from a short, exact list of what the
  library adds for screen readers. A forward check alone passes an invented sentence. Keep that list exact: a pattern like
  `(Open|Close) .*` would hide invented text.

Include input values and option text. Report the states and strings compared, not only that it passed.

## 4. Prove the checks can fail

A check that has never failed proves nothing. Before trusting a suite, change one real thing and watch it fail, then
restore it and confirm green.

- Change one heading on the page: the check must report it as missing and as added.
- Confirm the source is restored with a grep, and rebuild, before going on.

## 5. Layout and accessibility, at more than one width

- Check 1440, 820 and 390 px on every view: no sideways scroll on the document and on the app's main scroller (a framework
  may scroll an inner element, which `documentElement` never shows), and no leftover `{{`, `undefined` or `NaN`.
- Run axe at desktop and phone width on every view; fail on serious and critical. A portal card with one long token
  overflowed and became a scrollable region no keyboard could reach.
- Check that every control stays reachable at each width. An overflow menu folded a tab out of the page at 820 px.
- Save the screenshots and look at them. They are how you judge the result, and a test cannot tell you it looks wrong.

## 6. Repeat in the installed browser

Bundled test browsers are not what people run. Open the page in the real browser, then run every suite there with the
window visible:

```js
chromium.launch({ channel: process.env.PW_CHANNEL, headless: !process.env.PW_HEADED })
```

```sh
PW_CHANNEL=chrome PW_HEADED=1 node <suite>
```

Record the browser version. Installed Chrome found what bundled Chromium did not: a `/favicon.ico` 404 reported as a
console error. Serve through a strict static server, not a dev server that answers every path with the page, which hid
the same 404. Report the failing URL in the error message, so you read it rather than guess it.

## 7. Test logic with no browser, where you can

Load the logic alone and assert what the UI depends on: scenarios end where they should, paging visits every row once
and returns to the same pages, each role is refused what it should be. It runs in under a second and names the defect
directly. Also check what the build promises: a generated file is up to date (`--check`), and code parses at the
language level you claimed.

## 8. Fix at the right layer

Diagnose from the measurement, then fix where the cause is: the test when the test is wrong, the page's chrome when the
offset is there, and the runtime rather than the source when the source is meant to stay unchanged. After any fix, run
everything again, not only what failed.

## 9. Report

- A table per view: size, percent different, pass or fail, DOM identical or not.
- The counts: steps walked, states and strings compared, widths, axe findings, browser and version.
- What the oracle was, and what it does not prove.
- What was not tested, and why. A skipped check said out loud is worth more than a green run that hides it.
- Where the page differs from the reference on purpose, with the reason.

## Checklist

1. Reference read in full. Oracle named, with what it allows you to claim.
2. DOM and pixels captured by one driver from both sides.
3. Every interaction walked, with DOM, focus and caret per step, and compared.
4. Content checked in both directions at every state.
5. Each check seen to fail by a mutation, and the mutation reverted.
6. Three widths: scroll, placeholders, reachability. Axe at two. Screenshots looked at.
7. All suites repeated in the installed browser, with its version recorded.
8. Everything re-run after the last fix, from a set-up environment. The report says what was skipped or not tested.
