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
.venv/bin/pip install -q "diagram-kit @ git+https://github.com/ephico2real2/diagram-kit@v0.1.0"
.venv/bin/playwright install chromium
```

Until the repository is published, clone it and install the clone. `../diagram-kit` below is that clone:

```sh
git clone -q <where-the-kit-is> ../diagram-kit
.venv/bin/pip install -q ../diagram-kit
```

Check it:

```sh
.venv/bin/diagram-render
```

Result: the usage text, and exit status 2.

## 2. Generate a first page from the template

A diagram's page lives at `docs/diagrams/<slug>/source.html`. Start it as a copy of the template:

```sh
mkdir -p docs/diagrams/first
cp ../diagram-kit/template.html docs/diagrams/first/source.html
```

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

and exit status 0. The first render needs the network once, for the Google Fonts stylesheet.

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
FAIL: text crosses the edge of a box in figure 1: "the caller signs in with a token that the proxy checks first"
375 px viewport: scrollWidth 375
exit 1
```

No PNG is written for a page that fails. Put the label back, or split it over two `<text>` lines, and render again:

```sh
mv docs/diagrams/first/source.html.bak docs/diagrams/first/source.html
.venv/bin/diagram-render docs/diagrams/first/source.html docs/diagrams/first sign-in; echo "exit $?"
```

Result: the two `wrote` lines, then `exit 0`. `STANDARD.md` §5 lists every check and what each one means.

## 6. Embed it in a document

In a Markdown document, here `docs/first.md`: the picture, an italic caption, a text twin, and a "Diagram sources"
section.

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

Walked on 2026-10-06 from a fresh `git clone` of the kit, on macOS 26 (Darwin 25.5.0), Python 3.14.7, Playwright
1.63.0. Every command above ran as written, from step 1's clone install to step 6's path check, and every result
matched; the record is in the kit's first report. Installing from the tag is the one command not walked, because
the repository is not published yet.
