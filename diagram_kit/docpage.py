# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""doc-page: one light HTML page from one Markdown document.

The Markdown in the repository stays the source, and the page is made from it, never edited by hand. Figures are
the light PNGs that diagram-render writes. pandoc turns the Markdown into HTML. Each picture with the italic caption
after it becomes a <figure>, a wide table scrolls in its own box, and the contents list is made from the H2
headings. Images keep their relative paths, so they are published next to the page at the same paths.

The page is light only, on a white background, like the light figures it shows.

usage: doc-page SOURCE.md OUT.html --eyebrow TEXT --title NAME [--figures N] [--band H2-ID] [--standalone]
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATE = Path(__file__).with_name("docpage.html")

# A picture paragraph, then a paragraph that is all italic: the caption.
FIGURE = re.compile(r'<p><img ([^>]*?)\s*/?></p>\s*<p><em>(.*?)</em>\.?</p>', re.S)
HEADER = re.compile(r'\s*<h1 id="[^"]*">(.*?)</h1>\s*<p>(.*?)</p>\s*', re.S)
H2 = re.compile(r'<h2 id="([^"]+)">(.*?)</h2>', re.S)
TAG = re.compile(r"<[^>]+>")
# A private page link in repository text leaks it to every reader of the page.
PRIVATE_LINK = "claude.ai/"
# A page served beside the main page is not wrapped by the host, so it carries its own doctype and charset.
STANDALONE_HEAD = ('<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n'
                   '<meta name="viewport" content="width=device-width,initial-scale=1">\n')


class PageError(Exception):
    """The document breaks a rule of the page; nothing is written."""


def to_html(source: Path) -> str:
    if shutil.which("pandoc") is None:
        raise PageError("pandoc is not installed (README, 'Prerequisite for documents')")
    return subprocess.run(
        ["pandoc", source.name, "-f", "gfm", "-t", "html5", "--syntax-highlighting=none", "--wrap=none"],
        check=True, capture_output=True, text=True, cwd=source.parent,
    ).stdout


def caption(text: str) -> str:
    """End a caption with one stop. Markdown puts the period inside or outside the italics, so add one only
    when the text has no end mark of its own."""
    text = text.rstrip()
    return text if text.endswith((".", "!", "?")) else text + "."


def build(body: str, eyebrow: str, title: str, figures: int | None = None, band: str | None = None,
          standalone: bool = False) -> tuple[str, int, int]:
    """Return the page, the number of figures and the number of sections.

    `title` is the name in the browser tab, two to four words; the H1 of the document stays the heading."""
    if not 2 <= len(title.split()) <= 4:
        raise PageError(f"the title must be two to four words, got {title!r}")
    header = HEADER.match(body)
    if not header:
        raise PageError("the document does not open with an H1 and a byline paragraph")
    heading, byline = header.group(1), header.group(2)
    body = body[header.end():]

    count = len(FIGURE.findall(body))
    body = FIGURE.sub(lambda f: f'<figure><div class="shot"><img loading="lazy" {f.group(1)}></div>'
                                f'<figcaption>{caption(f.group(2))}</figcaption></figure>', body)
    if figures is not None and count != figures:
        raise PageError(f"expected {figures} pictures with captions, found {count}")
    if re.search(r'<img (?!loading="lazy")', body):
        raise PageError("a picture has no italic caption paragraph after it")

    # Wide content scrolls inside its own box, never the page.
    body = body.replace("<table>", '<div class="scroll"><table>').replace("</table>", "</table></div>")

    if band:
        parts = re.split(r'(?=<h2 id=")', body)
        if not any(p.startswith(f'<h2 id="{band}"') for p in parts):
            raise PageError(f"no H2 with the id {band}")
        body = "".join(f'<section class="story">{p}</section>' if p.startswith(f'<h2 id="{band}"') else p
                       for p in parts)

    sections = H2.findall(body)
    toc = "".join(f'<li><a href="#{i}">{TAG.sub("", t)}</a></li>' for i, t in sections)
    values = {
        "TAB_TITLE": html.escape(title, quote=False),
        "EYEBROW": html.escape(eyebrow, quote=False),
        "TITLE": heading, "BYLINE": byline, "TOC": toc, "BODY": body,
    }
    # One pass, so that text inside a value is never read as a placeholder.
    template = TEMPLATE.read_text().replace("<title>{{TITLE}}</title>", "<title>{{TAB_TITLE}}</title>", 1)
    page = re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: values[m.group(1)], template)
    if standalone:
        page = STANDALONE_HEAD + page
    if PRIVATE_LINK in page:
        raise PageError(f"the page holds '{PRIVATE_LINK}': a link to a private page must not be in repository text")
    return page, count, len(sections)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="doc-page", description=__doc__.split("\n\n")[0])
    ap.add_argument("source", type=Path, help="the Markdown document")
    ap.add_argument("out", type=Path, help="the HTML page to write")
    ap.add_argument("--eyebrow", required=True, help="the small line above the title")
    ap.add_argument("--title", required=True, help="the name in the browser tab, two to four words")
    ap.add_argument("--figures", type=int, help="the number of captioned pictures the document must hold")
    ap.add_argument("--band", help="the id of an H2 section drawn as a tinted band: the story, else the summary")
    ap.add_argument("--standalone", action="store_true",
                    help="a page published beside the main page: add the doctype and the charset")
    a = ap.parse_args(argv)
    try:
        page, count, sections = build(to_html(a.source.resolve()), a.eyebrow, a.title, a.figures, a.band, a.standalone)
    except (PageError, subprocess.CalledProcessError) as e:
        print(f"doc-page: {getattr(e, 'stderr', None) or e}", file=sys.stderr)
        return 1
    a.out.write_text(page)
    print(f"doc-page: {len(page)} bytes, {count} figures, {sections} sections, from {a.source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
