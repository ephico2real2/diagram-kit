# Tutorial: a first figure, from install to review

You will install the kit, generate a page from the template, render it, look at it, break it on purpose to see a
check refuse it, embed it in a document, and get it reviewed. It takes about ten minutes. Every output below was
recorded by walking this file from a fresh clone (see "Walked" at the end).

You need Python 3.10 or newer and git.

## 1. Install

The kit installs from a pinned tag, with Chromium beside it:

```sh
mkdir my-docs && cd my-docs && git init -q
python3 -m venv .venv
.venv/bin/pip install -q "diagram-kit @ git+https://github.com/ephico2real2/diagram-kit@v0.2.0"
.venv/bin/playwright install chromium
```

Until the repository is published, install a clone in place of the third line, then install Chromium (the
`playwright` command comes with the kit). `../diagram-kit` below is that clone:

```sh
git clone -q <where-the-kit-is> ../diagram-kit
.venv/bin/pip install -q ../diagram-kit
.venv/bin/playwright install chromium
```

Check it:

```sh
.venv/bin/diagram-render
```

Result: the usage text, and exit status 2.

## 2. Generate a first page from the template

A diagram's page lives at `docs/diagrams/<slug>/source.html`. Start it from the template the kit ships:

```sh
.venv/bin/diagram-template docs/diagrams/first/source.html
```

Result: `wrote docs/diagrams/first/source.html`. Run it again and it refuses (`refusing to overwrite …`, exit 1):
an existing page is never replaced.

Then make it say something. In the page:

- the `<title>` is a name of two to four words;
- the lede states the facts;
- each `<text>` in the figure is a label that is true today;
- a proposed step is drawn dashed.

For this walk, change the title and the first box's title:

```sh
sed -i.bak -e 's|<title>Replace With Two To Four Words</title>|<title>First Figure</title>|' \
           -e 's|>step one<|>the caller signs in<|' docs/diagrams/first/source.html
rm docs/diagrams/first/source.html.bak
```

## 3. Render

One name per `.fig-scroll` on the page, in document order. The template has one figure:

```sh
.venv/bin/diagram-render docs/diagrams/first/source.html docs/diagrams/first sign-in
```

Result:

```text
wrote …/docs/diagrams/first/sign-in.light.png (…bytes)
wrote …/docs/diagrams/first/sign-in.dark.png (…bytes)
375 px viewport: scrollWidth 375
```

and exit status 0. Every render reaches the network for the Google Fonts stylesheet and the font files it names.

## 4. Look at it

```sh
open docs/diagrams/first/sign-in.light.png docs/diagrams/first/sign-in.dark.png    # xdg-open on Linux
```

Read both PNGs. The checks cannot see these, so you look for them:

- clipped text;
- a line crossing a label;
- an arrow into the wrong box;
- a dashed shape that is in fact shipped.

## 5. Break it once, on purpose

Make the first box's label longer than its box (200 px wide holds about 26 characters):

```sh
sed -i.bak 's|>the caller signs in<|>the caller signs in with a token that the proxy checks first<|' docs/diagrams/first/source.html
.venv/bin/diagram-render docs/diagrams/first/source.html docs/diagrams/first sign-in; echo "exit $?"
```

Result:

```text
375 px viewport: scrollWidth 375
FAIL: text crosses the edge of a box in figure 1: "the caller signs in with a token that the proxy checks first"
exit 1
```

A render that fails writes no PNG, whichever check failed: the PNGs of the last good render stay as they were.
Put the label back, or split it over two `<text>` lines, and render again:

```sh
mv docs/diagrams/first/source.html.bak docs/diagrams/first/source.html
.venv/bin/diagram-render docs/diagrams/first/source.html docs/diagrams/first sign-in; echo "exit $?"
```

Result: the two `wrote` lines, then `exit 0`. `STANDARD.md` §5 lists every check and what each one means.

## 6. Embed it in a document

Create a Markdown document, `docs/first.md`, holding the picture, an italic caption, a text twin, and a "Diagram
sources" section. Write this into it:

````markdown
<!-- markdownlint-disable MD033 -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="diagrams/first/sign-in.dark.png">
  <source media="(prefers-color-scheme: light)" srcset="diagrams/first/sign-in.light.png">
  <img alt="The caller signs in on the host; the remote step runs only after it." src="diagrams/first/sign-in.light.png">
</picture>
<!-- markdownlint-enable MD033 -->

*Figure 1. The caller signs in on the host; the remote step runs only after it. The dashed gate is proposed.*

```text
HOST: the caller signs in -> (proposed) a gate, D1
REMOTE: (1) the remote step
```

## Diagram sources

Figure 1 is rendered from `docs/diagrams/first/source.html`:
`diagram-render docs/diagrams/first/source.html docs/diagrams/first sign-in`.
The picture, its text twin and the page change together.
````

Every path in `srcset` and `src` is relative to the document. Check that each one exists:

```sh
for f in $(grep -o 'diagrams/first/[a-z.-]*\.png' docs/first.md | sort -u); do test -f "docs/$f" && echo "ok $f"; done
```

Result: `ok diagrams/first/sign-in.dark.png` and `ok diagrams/first/sign-in.light.png`.

## 7. Get it reviewed

The figures are part of the change. Give two reviewers:

- the `source.html`;
- the PNGs;
- the render output;
- numbered claims, one per thing the figure asserts. One of them is always "no proposal is drawn as current".

Each reviewer checks the claims against the code. `STANDARD.md` §6 has the rule.

## Walked

Walked on 2026-10-06 at kit commit `b9c9b2f`, from a fresh `git clone`, a fresh venv and an empty Chromium cache
(`PLAYWRIGHT_BROWSERS_PATH` pointed at a new directory), on macOS 26.5.2 (Darwin 25.5.0), Python 3.14.7, Playwright
1.63.0. Every command above ran as written, from step 1's clone install to step 6's path check (step 4's `open` is
the one look by eye), and every result matched: step 2's second run refused with exit 1, and step 5's failed render
left the PNGs of step 3 byte for byte. Installing from the tag is the one command not walked, because the repository
is not published yet.
