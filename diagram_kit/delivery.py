# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""delivery-page OUT.html [--repo DIR] [--ref REF]: one page from a repository's tracker, handover and resume documents.

The Markdown stays the source; the page is generated and never edited by hand. The three documents are required. If
one is missing, empty or still the starter text, the command names each one that fails and writes nothing, because a
page with a part missing can look like a complete account of the delivery. The resume document is a file, or a section
of a file: `docs/handover.md#Resume prompt`.

The page reads only from the commit named, and says which commit, so it never claims a state that the commit does not
hold. Work on a branch or in the working tree does not appear. The same commit and the same pandoc give the same bytes.

Markdown is treated as text from a contributor, not as code. Raw HTML in it is shown as text, an HTML comment is
dropped, and a link or an image with a scheme other than the few below keeps only its words.

`delivery-page --init` writes a starter for each document that does not exist, and never overwrites a file. The render
refuses a starter until a person fills it in.
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import posixpath
import re
import shutil
import subprocess
import sys
from typing import Any, NamedTuple
from urllib.parse import urlsplit

TRACKER, HANDOVER, RESUME = "docs/backlog/TRACKER.md", "docs/handover.md", "docs/handover.md#Resume prompt"
STARTER = "<!-- delivery-page: starter. Fill in this file, then delete this line. -->"

# The tracker's summary. A tracker in another format still renders, with no summary.
TOTALS = re.compile(r"The backlog holds (\d+) stories: (\d+) done, (\d+) in progress and (\d+) planned\.")
WAVE = re.compile(r"^### (W\d+): (.+) \(phase (\w+), (\d+) of (\d+) stories done\)$", re.M)
OPEN_ISSUE = re.compile(r"^\| \d+ \| #\d+ ", re.M)
AS_OF = re.compile(r"\*\*As of (\d{4}-\d{2}-\d{2})\.\*\*")

COMMENT = re.compile(r"\s*<!--(?:(?!-->).)*-->\s*", re.S)
HEADING = re.compile(r'<h([1-6])(?: id="([^"]*)")?[^>]*>(.*?)</h\1>', re.S)
TAG = re.compile(r"<[^>]+>")
DROP = object()  # A dropped node. None cannot say so: pandoc's JSON holds null where a table has no short caption.

LINK_SCHEMES = {"http", "https", "mailto"}
IMAGE_SCHEMES = {"http", "https"}
WEB_REMOTE_SCHEMES = {"http", "https", "ssh", "git"}

FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700"
         "&family=IBM+Plex+Mono:wght@400;500;600&display=swap")

LAYOUT = """
* { box-sizing: border-box; }
body { background: var(--ground); color: var(--ink); font: 15px/1.55 var(--font-body); margin: 0; }
.page { max-width: 1040px; margin: 0 auto; padding: 28px 16px 64px; }
.masthead { display: grid; gap: 6px; padding-bottom: 18px; border-bottom: 2px solid var(--ink); }
.masthead h1 { font-size: clamp(26px, 4vw, 36px); line-height: 1.15; font-weight: 700; margin: 0; text-wrap: balance; }
.source { color: var(--muted); font-size: 14px; }
nav.jump { display: flex; flex-wrap: wrap; gap: 6px 18px; padding: 12px 0; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin: 14px 0 22px; }
.tile { background: var(--surface); border: 1px solid var(--rule); padding: 10px 14px; }
.tile b { display: block; font-size: 26px; line-height: 1.2; font-weight: 700; font-variant-numeric: tabular-nums; }
.tile span { color: var(--muted); font-size: 14px; }
.waves { display: grid; gap: 2px; margin: 0 0 8px; padding: 0; list-style: none; }
.wave { display: grid; grid-template-columns: 3.2em minmax(0, 1fr) 5.5em minmax(70px, 150px) 9.5em; gap: 10px;
  align-items: center; padding: 5px 8px; background: var(--surface); }
.wave .id { font: 600 13px var(--font-mono); }
.wave .phase, .wave .count { color: var(--muted); font-size: 14px; font-variant-numeric: tabular-nums; }
.bar { height: 7px; background: var(--rule); }
.bar i { display: block; height: 100%; background: var(--remote); }
@media (max-width: 640px) {
  .wave { grid-template-columns: 3.2em minmax(0, 1fr); }
  .wave .phase, .wave .bar, .wave .count { grid-column: 2; }
}
.doc { min-width: 0; }
.doc h1 { font-size: 26px; line-height: 1.2; font-weight: 700; margin: 44px 0 10px; padding-top: 14px;
  border-top: 2px solid var(--ink); }
.doc h2 { font-size: 20px; line-height: 1.25; font-weight: 600; margin: 30px 0 8px; text-wrap: balance; }
.doc h3 { font-size: 16.5px; line-height: 1.3; font-weight: 600; margin: 22px 0 6px; text-wrap: balance; }
.doc p, .doc li { max-width: 72ch; overflow-wrap: anywhere; }
.doc .wave { max-width: none; overflow-wrap: normal; }
.doc img { max-width: 100%; height: auto; }
a { color: var(--remote); }
a:focus-visible { outline: 2px solid var(--remote); outline-offset: 2px; }
code { font: 0.88em var(--font-mono); background: var(--none-wash); padding: 0.05em 0.3em; overflow-wrap: anywhere; }
pre { background: var(--none-wash); padding: 12px 14px; overflow-x: auto; }
pre code { padding: 0; background: none; overflow-wrap: normal; }
blockquote { margin: 12px 0; padding: 4px 14px; background: var(--remote-wash); }
.scroll { overflow-x: auto; margin: 10px 0 18px; }
table { border-collapse: collapse; width: 100%; font-size: 14.5px; background: var(--surface); }
th, td { border: 1px solid var(--rule); padding: 5px 9px; text-align: left; vertical-align: top; }
th { background: var(--remote-wash); font-weight: 600; }
td { font-variant-numeric: tabular-nums; }
"""


class Document(NamedTuple):
    """One required document, as named on the command line."""

    label: str
    path: str
    section: str
    prefix: str


def document(label: str, value: str, prefix: str) -> Document:
    path, _, section = value.partition("#")
    return Document(label, path, section.strip(), prefix)


def palette(theme: str) -> str:
    """The kit's palette, read from the template, so that a colour has one home. 'light' leaves dark mode out, for a
    repository whose rule is that its pages are light only."""
    template = pathlib.Path(__file__).with_name("template.html").read_text(encoding="utf-8")
    light = re.search(r"^:root \{.*?^\}", template, re.S | re.M)
    dark = re.search(r'^@media \(prefers-color-scheme: dark\) \{.*?^\}\n:root\[data-theme="dark"\] \{.*?^\}', template,
                     re.S | re.M)
    if light is None or dark is None:
        raise RuntimeError("template.html no longer holds the palette in the shape this command reads")
    return light.group(0) if theme == "light" else f"{light.group(0)}\n{dark.group(0)}"


def web_url(remote: str) -> str:
    """The web address of a git remote, for links. A credential or a port in the remote never reaches the page."""
    remote = remote.strip()
    if "://" in remote:
        parts = urlsplit(remote)
        if parts.scheme not in WEB_REMOTE_SCHEMES or not parts.hostname:
            raise ValueError(f"the remote is not a web address: {parts.scheme}://{parts.hostname or ''}. Pass --repo-url")
        host, path = parts.hostname, parts.path
    else:
        scp = re.fullmatch(r"(?:[^@/\s]+@)?([^:/\s]+):(?!/)(.+)", remote)
        if scp is None:
            raise ValueError("the remote is not a web address. Pass --repo-url")
        host, path = scp.group(1), "/" + scp.group(2)
    return f"https://{host}{path.rstrip('/').removesuffix('.git')}"


def checked_url(value: str) -> str:
    parts = urlsplit(value)
    if parts.scheme not in ("http", "https") or not parts.hostname or parts.username or parts.password:
        raise ValueError("--repo-url must be an http or https address with no credential in it")
    return value.rstrip("/")


def git(repo: pathlib.Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, encoding="utf-8")
    if done.returncode != 0:
        raise ValueError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout.strip()


def read_at(repo: pathlib.Path, sha: str, doc: Document) -> tuple[str | None, str | None]:
    """The document's text at this commit and no problem, or no text and the problem. A directory is a tree to git,
    which `git show` would print with exit 0, so the object's type is read first."""
    kind = subprocess.run(["git", "-C", str(repo), "cat-file", "-t", f"{sha}:{doc.path}"], capture_output=True, text=True)
    if kind.returncode != 0 or kind.stdout.strip() != "blob":
        return None, f"{doc.label}: {doc.path} is not a file at this commit"
    raw = subprocess.run(["git", "-C", str(repo), "show", f"{sha}:{doc.path}"], capture_output=True, check=True).stdout
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None, f"{doc.label}: {doc.path} is not UTF-8"
    if not text.strip():
        return None, f"{doc.label}: {doc.path} is empty"
    if STARTER in text:
        return None, f"{doc.label}: {doc.path} is still the starter text"
    return text, None


class Rewriter:
    """Makes a document's parsed form safe and correct on the page.

    A relative link is made absolute at the commit, because it otherwise resolves against the page's own address. The
    two link rules run on pandoc's parsed form, not on its HTML, so text in code is never touched."""

    def __init__(self, repo_url: str, sha: str, source: str) -> None:
        self.repo_url, self.sha, self.source = repo_url, sha, source

    def target(self, target: str, view: str, schemes: set[str]) -> str | None:
        """Where a link or an image points on the page, or None when it may not point anywhere."""
        try:
            parts = urlsplit(target.strip())
        except ValueError:
            return None
        if parts.scheme:
            return target if parts.scheme in schemes else None
        if parts.netloc:
            return f"https:{target}"
        if not parts.path:
            return target
        folder = "" if parts.path.startswith("/") else posixpath.dirname(self.source)
        path = posixpath.normpath(posixpath.join(folder, parts.path.lstrip("/")))
        if path.startswith(".."):
            return None
        query = f"?{parts.query}" if parts.query else ""
        fragment = f"#{parts.fragment}" if parts.fragment else ""
        return f"{self.repo_url}/{view}/{self.sha}/{path}{query}{fragment}"

    def walk(self, node: Any) -> Any:
        if isinstance(node, list):
            kept = (self.walk(item) for item in node)
            return [item for item in kept if item is not DROP]
        if not isinstance(node, dict):
            return node
        kind = node.get("t")
        if kind in ("RawBlock", "RawInline") and node["c"][0] == "html":
            text = node["c"][1]
            if COMMENT.fullmatch(text):
                return DROP
            return ({"t": "CodeBlock", "c": [["", [], []], text]} if kind == "RawBlock" else {"t": "Str", "c": text})
        if kind in ("Link", "Image"):
            attr, inlines, (target, title) = node["c"]
            view, schemes = ("blob", LINK_SCHEMES) if kind == "Link" else ("raw", IMAGE_SCHEMES)
            where = self.target(target, view, schemes)
            if where is None:
                return {"t": "Span", "c": [["", [], []], self.walk(inlines)]}
            return {"t": kind, "c": [attr, self.walk(inlines), [where, title]]}
        return {key: self.walk(value) for key, value in node.items()}


def run_pandoc(pandoc: str, args: list[str], text: str, source: str) -> str:
    done = subprocess.run([pandoc, *args], input=text, capture_output=True, encoding="utf-8")
    if done.returncode != 0:
        raise RuntimeError(f"pandoc failed on {source}: {done.stderr.strip()}")
    return done.stdout


def to_html(markdown: str, doc: Document, repo_url: str, sha: str, pandoc: str) -> str:
    """The document's body. A table gets a scrolling box of its own, so that the page never scrolls sideways."""
    tree = json.loads(run_pandoc(pandoc, ["-f", "gfm", "-t", "json"], markdown, doc.path))
    tree["blocks"] = Rewriter(repo_url, sha, doc.path).walk(tree["blocks"])
    body = run_pandoc(pandoc, ["-f", "json", "-t", "html", "--wrap=none", "--id-prefix", doc.prefix], json.dumps(tree),
                      doc.path)
    return re.sub(r"<table\b[^>]*>", '<div class="scroll"><table>', body).replace("</table>", "</table></div>")


def section_anchor(body: str, doc: Document) -> tuple[str | None, str | None]:
    """The anchor of the named section and no problem, or no anchor and the problem. The rendered HTML is what is read,
    so a heading shown in a code block is not a section, as it is not on the page."""
    heads = list(HEADING.finditer(body))
    for i, head in enumerate(heads):
        anchor = head.group(2) or ""
        title = html.unescape(TAG.sub("", head.group(3))).strip().casefold()
        if doc.section.casefold() not in (title, anchor.removeprefix(doc.prefix)):
            continue
        level = int(head.group(1))
        end = next((h.start() for h in heads[i + 1:] if int(h.group(1)) <= level), len(body))
        if not TAG.sub("", body[head.end():end]).strip():
            return None, f'{doc.label}: the section "{doc.section}" of {doc.path} is empty'
        return anchor, None
    return None, f'{doc.label}: {doc.path} has no section "{doc.section}"'


def wave_rows(tracker: str) -> str:
    """One row per wave, its bar drawn to the scale of its stories. A wave holds open issues too, which the tracker's
    heading does not count, so they are counted from its rows."""
    heads = list(WAVE.finditer(tracker))
    rows = []
    for i, head in enumerate(heads):
        following = tracker.find("\n## ", head.end())
        end = heads[i + 1].start() if i + 1 < len(heads) else (following if following != -1 else len(tracker))
        issues = len(OPEN_ISSUE.findall(tracker, head.end(), end))
        wave, title, phase, done, total = head.group(1), head.group(2), head.group(3), int(head.group(4)), int(head.group(5))
        share = 100 * done / total if total else 0
        count = (f"{done} of {total} stories" + (f", {issues} open" if issues else "")) if total else f"{issues} open issues"
        rows.append(f'<li class="wave"><span class="id">{wave}</span><span>{html.escape(title)}</span>'
                    f'<span class="phase">{"ongoing" if phase == "ongoing" else f"phase {html.escape(phase)}"}</span>'
                    f'<div class="bar" role="img" aria-label="{done} of {total} stories done">'
                    f'<i style="width:{share:.0f}%"></i></div><span class="count">{count}</span></li>')
    return "\n".join(rows)


def summary(tracker: str) -> tuple[str, str]:
    """The tiles and the wave rows, each empty when the tracker does not use the format."""
    totals = TOTALS.search(tracker)
    tiles = ""
    if totals:
        cells = "".join(f'<div class="tile"><b>{value}</b><span>{name}</span></div>'
                        for value, name in zip(totals.groups(), ("stories", "done", "in progress", "planned")))
        tiles = f'<section class="tiles" aria-label="Stories in the backlog">{cells}</section>'
    rows = wave_rows(tracker)
    waves = (f'<section id="waves" class="doc"><h2>Waves, in the order they are worked</h2>\n'
             f'<ul class="waves">\n{rows}\n</ul></section>') if rows else ""
    return tiles, waves


def render(repo: pathlib.Path, ref: str, title: str | None, docs: dict[str, Document], repo_url: str | None,
           strip_footer: str | None, theme: str, pandoc: str) -> tuple[str, str]:
    """The page and its commit. Raises ValueError that names every document that fails, before anything is written."""
    sha = git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}")
    subject = git(repo, "log", "-1", "--format=%cs %s", sha)
    url = checked_url(repo_url) if repo_url else web_url(git(repo, "remote", "get-url", "origin"))
    name = title or f"{url.rsplit('/', 1)[-1]} delivery handover"

    tracker, handover, resume = docs["tracker"], docs["handover"], docs["resume"]
    problems = []
    if tracker.path == handover.path:
        problems.append(f"the tracker and the handover are one file: {tracker.path}")
    on_the_page = resume.path in (tracker.path, handover.path)
    if on_the_page and not resume.section:
        problems.append(f"resume: {resume.path} is already on the page. Name its section: {resume.path}#<heading>")

    # A file named twice is read and rendered once, with the identifiers of the first name.
    distinct: dict[str, Document] = {}
    for doc in docs.values():
        distinct.setdefault(doc.path, doc)
    texts: dict[str, str] = {}
    for doc in distinct.values():
        text, problem = read_at(repo, sha, doc)
        if problem:
            problems.append(problem)
        else:
            texts[doc.path] = text
    if strip_footer and texts and not any(strip_footer in text for text in texts.values()):
        problems.append(f"--strip-footer: no document holds {strip_footer}")
    if problems or len(texts) != len(distinct):
        raise ValueError(_refusal(sha, problems))

    if strip_footer:
        footer = re.compile(r"\n---\n\s*" + re.escape(strip_footer) + r".*\Z", re.S)
        texts = {path: footer.sub("\n", text) for path, text in texts.items()}

    bodies = {path: to_html(text, distinct[path], url, sha, pandoc) for path, text in texts.items()}
    resume_link = "#resume"
    if resume.section:
        anchor, problem = section_anchor(bodies[resume.path], resume._replace(prefix=distinct[resume.path].prefix))
        if problem:
            raise ValueError(_refusal(sha, [problem]))
        resume_link = f"#{anchor}"

    tiles, waves = summary(texts[tracker.path])
    as_of = AS_OF.search(texts[handover.path])
    dated = f" Handover dated {as_of.group(1)}." if as_of else ""
    separate = "" if on_the_page else f'<article id="resume" class="doc">{bodies[resume.path]}</article>\n'
    places = [("#handover", "Handover"), (html.escape(resume_link), "Resume"), ("#tracker", "Tracker")]
    jump = "".join(f'<a href="{href}">{text}</a>' for href, text in ([("#waves", "Waves")] if waves else []) + places)
    named = resume.path + (f"#{resume.section}" if resume.section else "")
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(name)}</title>
<link rel="stylesheet" href="{html.escape(FONTS)}">
<style>
{palette(theme)}
{LAYOUT}</style>
</head>
<body>
<div class="page">
<header class="masthead">
  <h1>{html.escape(name)}</h1>
  <div class="source">Rendered from <code>{html.escape(tracker.path)}</code>, <code>{html.escape(handover.path)}</code> and
    <code>{html.escape(named)}</code> at
    <a href="{html.escape(url)}/commit/{sha}"><code>{sha[:12]}</code></a> ({html.escape(subject)}).{dated}
    Work that is not in this commit does not appear.</div>
</header>
<nav class="jump" aria-label="On this page">{jump}</nav>
{tiles}
{waves}
<article id="handover" class="doc">{bodies[handover.path]}</article>
{separate}<article id="tracker" class="doc">{bodies[tracker.path]}</article>
</div>
</body>
</html>
"""
    return page, sha


def _refusal(sha: str, problems: list[str]) -> str:
    lines = "\n".join(f"  {problem}" for problem in problems)
    return (f"nothing written. A delivery page needs a tracker, a handover and a resume document, read at {sha[:12]}:\n"
            f"{lines}\nA file that is not committed is not seen. --init writes a starter for a file that does not exist.")


def starters(docs: dict[str, Document]) -> dict[str, str]:
    """The starter text of each file. The heading of a resume section sits in the handover's starter, so that the two
    documents hold together from the first commit."""
    tracker, handover, resume = docs["tracker"], docs["handover"], docs["resume"]
    heading = resume.section or "Resume prompt"
    resume_text = "Write what a new session reads first, to pick up the work: its goal, its rules, what to check first.\n"
    texts = {
        tracker.path: f"""{STARTER}

# Delivery tracker

The backlog holds 0 stories: 0 done, 0 in progress and 0 planned.

## Waves

### W1: Name the first wave (phase 1, 0 of 0 stories done)

| # | Item | Status | Title |
|---|---|---|---|
""",
        handover.path: f"""{STARTER}

# Delivery handover

**As of YYYY-MM-DD.** Write the commit each environment runs, what is in flight, and what comes next.
""",
    }
    if resume.path == handover.path:
        texts[handover.path] += f"\n## {heading}\n\n{resume_text}"
    else:
        texts[resume.path] = f"{STARTER}\n\n# {heading}\n\n{resume_text}"
    return texts


def init(repo: pathlib.Path, docs: dict[str, Document]) -> None:
    root = pathlib.Path(git(repo, "rev-parse", "--show-toplevel"))
    for path, text in starters(docs).items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            # 'x' fails on any existing file, so that this command can never overwrite one.
            with target.open("x", encoding="utf-8") as out:
                out.write(text)
        except FileExistsError:
            print(f"kept {path}: it exists")
        else:
            print(f"wrote {path}: fill it in, delete its first line, and commit it")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="delivery-page", description=__doc__.splitlines()[0])
    parser.add_argument("out", type=pathlib.Path, nargs="?", help="the .html to write")
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path("."), help="the checkout (default: here)")
    parser.add_argument("--ref", default="HEAD", help="the commit to read, as a git ref (default: HEAD)")
    parser.add_argument("--tracker", default=TRACKER, help=f"the tracker file (default: {TRACKER})")
    parser.add_argument("--handover", default=HANDOVER, help=f"the handover file (default: {HANDOVER})")
    parser.add_argument("--resume", default=RESUME, help=f"the resume file or FILE#SECTION (default: {RESUME})")
    parser.add_argument("--title", help="the page's name (default: from the repository's name)")
    parser.add_argument("--repo-url", help="the repository's web address (default: from the origin remote)")
    parser.add_argument("--strip-footer", metavar="MARKER",
                        help="drop a generated footer: the '---' line before MARKER, to the end of the document")
    parser.add_argument("--theme", choices=("both", "light"), default="both", help="the palette (default: both)")
    parser.add_argument("--init", action="store_true", help="write a starter for each document that does not exist")
    args = parser.parse_args(argv)
    if args.init == (args.out is not None):
        parser.error("name the page to write, or pass --init, and not both")

    docs = {"tracker": document("tracker", args.tracker, "t-"), "handover": document("handover", args.handover, "h-"),
            "resume": document("resume", args.resume, "r-")}
    if shutil.which("git") is None:
        print("delivery-page: git is not installed", file=sys.stderr)
        return 1
    try:
        if args.init:
            init(args.repo, docs)
            return 0
        pandoc = shutil.which("pandoc")
        if pandoc is None:
            print("delivery-page: pandoc is not installed (the README's prerequisite for documents)", file=sys.stderr)
            return 1
        page, sha = render(args.repo, args.ref, args.title, docs, args.repo_url, args.strip_footer, args.theme, pandoc)
    except (ValueError, RuntimeError) as error:
        print(f"delivery-page: {error}", file=sys.stderr)
        return 1
    args.out.write_text(page, encoding="utf-8")
    print(f"wrote {args.out}: {len(page.encode('utf-8'))} bytes, from {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
