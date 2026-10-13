# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""doc-docx OUT.docx IN.md [IN.md ...] --date YYYY-MM-DD: one Word document from Markdown, with pandoc.

The Markdown stays the source; the .docx is generated and never edited by hand. Pandoc reads each file as
GitHub-flavoured Markdown, and the files are joined in the order given, each after a page break. A link from one of
them to another (`guide.md`, `../docs/guide.md#a-heading`), or to a heading of its own file (`#a-heading`), is pointed
at that heading inside the document, each file keeping its headings apart from the others'. The command refuses to
write a file in which a link would lead nowhere, a link to a `.md` file that is not part of it, or an image it cannot
find. The date is stamped on the file (SOURCE_DATE_EPOCH) and pandoc reads no user data directory, so the same input
and the same pandoc give a byte-identical file on every machine and a CI job can compare it with the committed one.

The look comes from a reference document built at run time from pandoc's own default, with the kit's palette
applied: headings in --remote, tables ruled in --rule with a --ground header row. Nothing binary is committed.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import zipfile
from datetime import date, datetime, timezone

# The kit's light palette (template.html :root), so a document and its figures read as one family.
REMOTE, RULE, GROUND = "0E6F68", "D7DCE3", "F5F6F8"

PAGE_BREAK = {"t": "RawBlock", "c": ["openxml", '<w:p><w:r><w:br w:type="page"/></w:r></w:p>']}
# A link with a scheme (https:, mailto:) leads out of the repository, whatever its file name ends with.
SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")


def elements(node: object, kind: str) -> list[dict]:
    """Every element of one kind ("Header", "Link") in a pandoc JSON AST, in document order."""
    if isinstance(node, list):
        return [found for item in node for found in elements(item, kind)]
    if isinstance(node, dict):
        return ([node] if node.get("t") == kind else []) + elements(node.get("c"), kind)
    return []


def label_text(inlines: list[dict]) -> str | None:
    """The text of a link label that is one word or one code span (`guide.md`), else None."""
    if len(inlines) == 1 and inlines[0]["t"] == "Str":
        return inlines[0]["c"]
    if len(inlines) == 1 and inlines[0]["t"] == "Code":
        return inlines[0]["c"][1]
    return None


def read(pandoc: str, path: pathlib.Path) -> dict:
    """One file as pandoc's AST. Its headings carry the anchors GitHub gives them (gfm_auto_identifiers); a warning
    (a file that is not UTF-8) is a failure."""
    return json.loads(subprocess.run([pandoc, "--from", "gfm", "--to", "json", "--fail-if-warnings", str(path)],
                                     check=True, stdout=subprocess.PIPE).stdout)


def join(sources: list[pathlib.Path], pandoc: str = "pandoc") -> dict:
    """The files as one pandoc document, each after a page break. Pandoc reads them, so a link in code stays code
    and a reference-style link is a link. Each file's heading anchors get the prefix `fN-` (N its place in the
    order), so a heading two files share stays two targets, and every link to a file of the document, or to a
    heading of its own file, is pointed at its target. A link whose text is just the file's name
    (`[guide.md](guide.md)`) takes the file's title instead, since a reader of the document never sees the file."""
    files = [path.resolve() for path in sources]
    if len(set(files)) < len(files):
        raise ValueError("a file is given twice")
    docs = {path: read(pandoc, path) for path in files}
    prefix = {path: f"f{n}-" for n, path in enumerate(files, 1)}
    headings = {path: {h["c"][1][0]: h for h in elements(doc["blocks"], "Header") if h["c"][1][0]}
                for path, doc in docs.items()}
    titles = {path: next((h for h in found.values() if h["c"][0] == 1), None) for path, found in headings.items()}
    for path, title in titles.items():
        if title is None:
            raise ValueError(f"{path.name} has no level-1 heading: a file joined into a document needs one, "
                             "so links to it have a target")
    for path, doc in docs.items():
        for link in elements(doc["blocks"], "Link"):
            url = link["c"][2][0]
            if SCHEME.match(url):
                continue
            target, _, anchor = url.partition("#")
            linked = (path.parent / urllib.parse.unquote(target)).resolve() if target else path
            if linked not in docs:
                if target.endswith(".md"):
                    raise ValueError(f"{path.name}: link to {url}, which is not part of this document")
                continue
            heading = headings[linked].get(anchor) if anchor else titles[linked]
            if heading is None:
                raise ValueError(f"{path.name}: link to {url}, but {linked.name} has no heading with that anchor")
            link["c"][2][0] = "#" + prefix[linked] + heading["c"][1][0]
            if target and label_text(link["c"][1]) == target:
                link["c"][1] = titles[linked]["c"][2]
    # Renamed only now: every link above was matched against the anchors GitHub shows.
    for path, found in headings.items():
        for anchor, heading in found.items():
            heading["c"][1][0] = prefix[path] + anchor
    blocks = []
    for path in files:
        blocks += ([PAGE_BREAK] if blocks else []) + docs[path]["blocks"]
    return {**docs[files[0]], "blocks": blocks}


def _restyle(styles: str) -> str:
    """Pandoc's default styles, with the kit's palette. Each edit must match exactly once, whitespace aside, so a
    pandoc whose default reference changed shape fails loudly instead of producing an unstyled document.

    Element order inside a table style follows the OOXML schema (ECMA-376 CT_TblPrBase, CT_TcPr, CT_TblStylePr):
    tblBorders after tblInd, shd after tcBorders, rPr first in a tblStylePr; Word drops elements out of order."""
    borders = "".join(f'<w:{side} w:val="single" w:sz="4" w:space="0" w:color="{RULE}"/>'
                      for side in ("top", "left", "bottom", "right", "insideH", "insideV"))
    edits = [
        # Every table ruled.
        (r'(<w:tblInd w:w="0" w:type="dxa" />)', rf'\1<w:tblBorders>{borders}</w:tblBorders>'),
        # A little air above and below each cell's text.
        (r'(<w:tblCellMar>\s*)<w:top w:w="0" w:type="dxa" />', r'\1<w:top w:w="60" w:type="dxa" />'),
        (r'(<w:left w:w="108" w:type="dxa" />\s*)<w:bottom w:w="0" w:type="dxa" />',
         r'\1<w:bottom w:w="60" w:type="dxa" />'),
        # The header row: bold, on the ground colour, over a heavier rule.
        (r'(<w:tblStylePr w:type="firstRow">)', r'\1<w:rPr><w:b/></w:rPr>'),
        (r'<w:tcBorders>\s*<w:bottom w:val="single"/>\s*</w:tcBorders>',
         f'<w:tcBorders><w:bottom w:val="single" w:sz="8" w:space="0" w:color="{RULE}"/></w:tcBorders>'
         f'<w:shd w:val="clear" w:color="auto" w:fill="{GROUND}"/>'),
    ]
    for pattern, replacement in edits:
        styles, count = re.subn(pattern, replacement, styles)
        if count != 1:
            raise RuntimeError(f"pandoc's default reference.docx changed shape: {pattern!r} matched {count} times")
    # Headings in --remote instead of the theme's accent.
    styles, count = re.subn(r'<w:color\s+w:val="[0-9A-F]{6}"\s+w:themeColor="accent1"\s+w:themeShade="BF"\s*/>',
                            f'<w:color w:val="{REMOTE}" />', styles)
    if count < 2:
        raise RuntimeError("pandoc's default heading colours were not found")
    return styles


def reference_docx(pandoc: str, target: pathlib.Path, epoch: int) -> None:
    """The reference document, stamped with the document's own date: pandoc copies the reference's parts into the
    output with their timestamps, so a reference made 'now' would make every build differ from the last. It does
    not recompress them either, so they are stored: deflated here, they would carry the bytes of this Python's zlib
    (zlib-ng on Windows), not pandoc's."""
    env = {**os.environ, "SOURCE_DATE_EPOCH": str(epoch)}
    default = subprocess.run([pandoc, "--print-default-data-file", "reference.docx"],
                             check=True, capture_output=True, env=env).stdout
    stamp = datetime.fromtimestamp(epoch, timezone.utc).timetuple()[:6]
    with zipfile.ZipFile(io.BytesIO(default)) as src, zipfile.ZipFile(target, "w") as out:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "word/styles.xml":
                data = _restyle(data.decode("utf-8")).encode("utf-8")
            item.date_time, item.compress_type = stamp, zipfile.ZIP_STORED
            out.writestr(item, data)


def check_links(docx: pathlib.Path) -> None:
    """Every internal hyperlink in the written file lands on a bookmark that exists."""
    with zipfile.ZipFile(docx) as z:
        body = z.read("word/document.xml").decode("utf-8")
    anchors = set(re.findall(r'w:anchor="([^"]+)"', body))
    marks = set(re.findall(r'<w:bookmarkStart [^>]*w:name="([^"]+)"', body))
    missing = sorted(anchors - marks)
    if missing:
        raise ValueError(f"{len(missing)} internal link(s) lead nowhere: {missing}")


def build(out: pathlib.Path, sources: list[pathlib.Path], day: date, pandoc: str = "pandoc") -> None:
    document = join(sources, pandoc)
    epoch = int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp())
    # Images are found beside the file that shows them, from any working directory.
    images = os.pathsep.join(dict.fromkeys(str(path.resolve().parent) for path in sources))
    partial = out.with_name(out.name + ".tmp")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            ref, joined, data = (pathlib.Path(tmp) / name for name in ("reference.docx", "document.json", "data"))
            data.mkdir()
            reference_docx(pandoc, ref, epoch)
            joined.write_text(json.dumps(document), encoding="utf-8")
            # An empty data directory, so a template in ~/.local/share/pandoc cannot change the file; a warning
            # (an image not found) fails the build instead of leaving a hole in the document.
            subprocess.run([pandoc, "--from", "json", "--to", "docx", "--data-dir", str(data), "--reference-doc",
                            str(ref), "--resource-path", images, "--fail-if-warnings", "--output", str(partial),
                            str(joined)],
                           check=True, env={**os.environ, "SOURCE_DATE_EPOCH": str(epoch)})
        check_links(partial)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    partial.replace(out)


def main() -> int:
    parser = argparse.ArgumentParser(prog="doc-docx", description=__doc__.splitlines()[0])
    parser.add_argument("out", type=pathlib.Path, help="the .docx to write")
    parser.add_argument("sources", type=pathlib.Path, nargs="+", help="Markdown files, in document order")
    parser.add_argument("--date", required=True, type=date.fromisoformat,
                        help="the date stamped on the file (YYYY-MM-DD); fixed, so the file is reproducible")
    args = parser.parse_args()
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        print("doc-docx: pandoc is not installed (the version your CI pins; see the document skill)", file=sys.stderr)
        return 1
    try:
        build(args.out, args.sources, args.date, pandoc)
    except (ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"doc-docx: {error}", file=sys.stderr)
        return 1
    version = subprocess.run([pandoc, "--version"], check=True, capture_output=True, text=True).stdout.split("\n")[0]
    print(f"wrote {args.out} from {len(args.sources)} file(s) with {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
