# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""doc-docx OUT.docx IN.md [IN.md ...] --date YYYY-MM-DD: one Word document from Markdown, with pandoc.

The Markdown stays the source; the .docx is generated and never edited by hand. The files are joined in the order
given, each after a page break, as GitHub-flavoured Markdown. A link from one of them to another (`guide.md`,
`guide.md#a-heading`) is pointed at that heading inside the document, and the command refuses to write a file in
which an internal link would lead nowhere, or a link to a `.md` file that is not part of it. The date is stamped on
the file (SOURCE_DATE_EPOCH), so the same input and the same pandoc give a byte-identical file on every machine and a
CI job can compare it with the committed one.

The look comes from a reference document built at run time from pandoc's own default, with the kit's palette
applied: headings in --remote, tables ruled in --rule with a --ground header row. Nothing binary is committed.
"""

from __future__ import annotations

import argparse
import io
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import date, datetime, timezone

# The kit's light palette (template.html :root), so a document and its figures read as one family.
REMOTE, RULE, GROUND = "0E6F68", "D7DCE3", "F5F6F8"

PAGE_BREAK = '\n\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n\n'
# Inline links only; a link target never contains spaces or a closing parenthesis.
LINK = re.compile(r"\[([^\]]*)\]\(([^()\s]+)\)")


def github_slug(heading: str) -> str:
    """The anchor GitHub gives a heading, which pandoc's gfm reader reproduces (gfm_auto_identifiers)."""
    text = re.sub(r"[`*_~]|<[^>]+>", "", heading).strip().lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def first_heading(markdown: str) -> str:
    """The text of the file's level-1 heading: a file joined into a document needs one, so links to it land."""
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError("no level-1 heading: a file joined into a document needs one, so links to it have a target")


def join(sources: list[pathlib.Path]) -> str:
    """The files as one Markdown text, with every link between them turned into a link inside the document. A link
    whose text is just the file's name (`[guide.md](guide.md)`) takes the file's title instead, since a reader of
    the document never sees the file."""
    texts = {path.name: path.read_text(encoding="utf-8") for path in sources}
    titles = {name: first_heading(text) for name, text in texts.items()}

    def relink(match: re.Match[str]) -> str:
        label, target = match.groups()
        path, _, anchor = target.partition("#")
        if not path.endswith(".md"):
            return match.group(0)
        name = pathlib.PurePosixPath(path).name
        if name not in texts:
            raise ValueError(f"link to {target}, which is not part of this document")
        if label.strip("`") == path:
            label = titles[name]
        return f"[{label}](#{anchor or github_slug(titles[name])})"

    return PAGE_BREAK.join(LINK.sub(relink, texts[path.name]) for path in sources)


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
    output with their timestamps, so a reference made 'now' would make every build differ from the last."""
    env = {**os.environ, "SOURCE_DATE_EPOCH": str(epoch)}
    default = subprocess.run([pandoc, "--print-default-data-file", "reference.docx"],
                             check=True, capture_output=True, env=env).stdout
    stamp = datetime.fromtimestamp(epoch, timezone.utc).timetuple()[:6]
    with zipfile.ZipFile(io.BytesIO(default)) as src, zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "word/styles.xml":
                data = _restyle(data.decode("utf-8")).encode("utf-8")
            item.date_time = stamp
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
    markdown = join(sources)
    epoch = int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp())
    with tempfile.TemporaryDirectory() as tmp:
        ref, joined = pathlib.Path(tmp) / "reference.docx", pathlib.Path(tmp) / "document.md"
        reference_docx(pandoc, ref, epoch)
        joined.write_text(markdown, encoding="utf-8")
        partial = out.with_name(out.name + ".tmp")
        subprocess.run([pandoc, "--from", "gfm+raw_attribute", "--to", "docx", "--reference-doc", str(ref),
                        "--output", str(partial), str(joined)],
                       check=True, env={**os.environ, "SOURCE_DATE_EPOCH": str(epoch)})
    try:
        check_links(partial)
    except ValueError:
        partial.unlink()
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
        print("doc-docx: pandoc is not installed (macOS: brew install pandoc; see the document skill)", file=sys.stderr)
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
