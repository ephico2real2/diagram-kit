# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""doc-docx: the Word file is styled, linked inside itself and reproducible.

Every test runs pandoc, which reads the Markdown. They are skipped where pandoc is not installed, except in CI
(ci.yml installs it): there a missing pandoc fails them, so they cannot be skipped without anyone seeing it.
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile
import zlib
from datetime import date
from xml.etree import ElementTree

import pytest

from diagram_kit import docx

pytestmark = pytest.mark.skipif(shutil.which("pandoc") is None and not os.environ.get("CI"),
                                reason="pandoc is not installed")

DAY = date(2026, 10, 13)
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
GUIDE = """# A guide for developers

See the [checklist.md](checklist.md) and [step two](checklist.md#before-you-ask).

## 2. Before you start

Text with an ![image](figure.png) and a [site](https://example.org).
"""
CHECKLIST = """# The checklist

## Before you ask

- [ ] I read [§2](guide.md#2-before-you-start) of the [guide](guide.md).
"""
# The anchor GitHub gives each heading (POST /markdown, mode=markdown, measured 2026-10-13).
GITHUB = {
    "2. Before you start": "2-before-you-start",
    "Step 1: the groups, in each environment's directory": "step-1-the-groups-in-each-environments-directory",
    "The `pay` example": "the-pay-example",
    "Don't panic — it's fine": "dont-panic--its-fine",
    "The `MAX_RETRIES` setting": "the-max_retries-setting",
    "Café & crème brûlée": "café--crème-brûlée",
    "Overview": "overview",
    "Overview!": "overview-1",
}


# A one-pixel PNG, as bytes: made here with zlib, it would carry this machine's zlib into every file built with it.
PNG = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de0000000c49444154789c6360606000"
                    "0000040001f61738550000000049454e44ae426082")


def write(root: pathlib.Path, files: dict[str, str]) -> list[pathlib.Path]:
    paths = []
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text, encoding="utf-8")
        paths.append(root / name)
    return paths


def text(element: ElementTree.Element) -> str:
    return "".join(t.text or "" for t in element.iter(W + "t"))


def landings(path: pathlib.Path) -> dict[str, str | None]:
    """Each link's text, and where it lands: the paragraph holding its bookmark (None: no such bookmark), or the
    address of a link that leads out of the document."""
    with zipfile.ZipFile(path) as z:
        body = ElementTree.fromstring(z.read("word/document.xml"))
        rels = ElementTree.fromstring(z.read("word/_rels/document.xml.rels"))
    external = {rel.get("Id"): rel.get("Target") for rel in rels if rel.get("TargetMode") == "External"}
    marks = {mark.get(W + "name"): text(p) for p in body.iter(W + "p") for mark in p.iter(W + "bookmarkStart")}
    return {text(link): marks.get(link.get(W + "anchor")) if link.get(W + "anchor") else external[link.get(R + "id")]
            for link in body.iter(W + "hyperlink")}


@pytest.fixture
def sources(tmp_path: pathlib.Path) -> list[pathlib.Path]:
    (tmp_path / "figure.png").write_bytes(PNG)
    return write(tmp_path, {"guide.md": GUIDE, "checklist.md": CHECKLIST})


def test_links_between_the_files_land_on_their_headings(sources: list[pathlib.Path], tmp_path: pathlib.Path) -> None:
    docx.build(tmp_path / "doc.docx", sources, DAY)
    assert landings(tmp_path / "doc.docx") == {
        "The checklist": "The checklist",              # a file-name label takes the file's title
        "step two": "Before you ask",
        "§2": "2. Before you start",
        "guide": "A guide for developers",
        "site": "https://example.org",
    }
    with zipfile.ZipFile(tmp_path / "doc.docx") as z:
        assert z.read("word/document.xml").decode().count('<w:br w:type="page"/>') == 1
        assert [name for name in z.namelist() if name.startswith("word/media/")]


def test_links_use_the_anchors_github_shows(tmp_path: pathlib.Path) -> None:
    headings = "".join(f"## {heading}\n\n" for heading in GITHUB)
    links = " ".join(f"[{n}](b.md#{anchor})" for n, anchor in enumerate(GITHUB.values()))
    paths = write(tmp_path, {"a.md": f"# Alpha\n\n{links} [title](b.md)\n",
                             "b.md": f"# The `group_sync` runbook\n\n{headings}"})
    docx.build(tmp_path / "doc.docx", paths, DAY)
    assert landings(tmp_path / "doc.docx") == {**{str(n): heading.replace("`", "") for n, heading in enumerate(GITHUB)},
                                               "title": "The group_sync runbook"}


def test_a_heading_two_files_share_is_two_targets(tmp_path: pathlib.Path) -> None:
    paths = write(tmp_path, {
        "a.md": "# Alpha\n\n## Setup\n\n## Beta\n\nSee [their setup](b.md#setup) and [the beta file](b.md).\n",
        "b.md": "# Beta!\n\nJump to [my setup](#setup).\n\n## Setup!\n\nTheir setup.\n",
    })
    docx.build(tmp_path / "doc.docx", paths, DAY)
    assert landings(tmp_path / "doc.docx") == {"their setup": "Setup!", "the beta file": "Beta!", "my setup": "Setup!"}


def test_every_kind_of_markdown_link_is_followed(tmp_path: pathlib.Path) -> None:
    paths = write(tmp_path, {
        "a.md": '# Alpha\n\n[ref][r], [angle](<b.md#sec>), [titled](b.md "Beta"), [dotted](./b.md).\n\n[r]: b.md#sec\n',
        "b.md": "# Beta\n\n## Sec\n",
    })
    docx.build(tmp_path / "doc.docx", paths, DAY)
    assert landings(tmp_path / "doc.docx") == {"ref": "Sec", "angle": "Sec", "titled": "Beta", "dotted": "Beta"}


def test_links_in_code_are_code(tmp_path: pathlib.Path) -> None:
    paths = write(tmp_path, {
        "a.md": "# Alpha\n\nWrite `[x](b.md)` to link.\n\n```markdown\n[y](b.md#sec) or [z](elsewhere.md)\n```\n",
        "b.md": "# Beta\n\n## Sec\n",
    })
    docx.build(tmp_path / "doc.docx", paths, DAY)
    with zipfile.ZipFile(tmp_path / "doc.docx") as z:
        body = text(ElementTree.fromstring(z.read("word/document.xml")))
    assert "[x](b.md)" in body and "[y](b.md#sec) or [z](elsewhere.md)" in body
    assert landings(tmp_path / "doc.docx") == {}


def test_files_of_the_same_name_in_two_directories(tmp_path: pathlib.Path) -> None:
    paths = write(tmp_path, {"api/README.md": "# The API\n\nSee the [CLI](../cli/README.md).\n",
                             "cli/README.md": "# The CLI\n\nBack to the [API](../api/README.md).\n"})
    docx.build(tmp_path / "doc.docx", paths, DAY)
    assert landings(tmp_path / "doc.docx") == {"CLI": "The CLI", "API": "The API"}


def test_a_link_is_resolved_from_its_own_file(tmp_path: pathlib.Path) -> None:
    a, b, _ = write(tmp_path, {"a.md": "# Alpha\n\nSee [x](sub/b.md).\n", "b.md": "# Beta\n",
                               "sub/b.md": "# Another\n"})
    with pytest.raises(ValueError, match="sub/b.md, which is not part of this document"):
        docx.build(tmp_path / "doc.docx", [a, b], DAY)


@pytest.mark.parametrize("link", ["See [the design](DESIGN.md).", "See [the design][d].\n\n[d]: DESIGN.md"])
def test_a_link_to_a_file_outside_the_document_is_refused(sources: list[pathlib.Path], tmp_path: pathlib.Path,
                                                          link: str) -> None:
    sources[1].write_text(CHECKLIST + "\n" + link + "\n")
    with pytest.raises(ValueError, match="DESIGN.md, which is not part of this document"):
        docx.build(tmp_path / "doc.docx", sources, DAY)
    assert not (tmp_path / "doc.docx").exists()


def test_a_markdown_file_on_the_web_is_an_ordinary_link(tmp_path: pathlib.Path) -> None:
    paths = write(tmp_path, {
        "a.md": "# Alpha\n\n[upstream](https://github.com/o/r/blob/main/CONTRIBUTING.md), "
                "[theirs](https://github.com/o/r/blob/main/b.md).\n",
        "b.md": "# Beta\n",
    })
    docx.build(tmp_path / "doc.docx", paths, DAY)
    assert landings(tmp_path / "doc.docx") == {"upstream": "https://github.com/o/r/blob/main/CONTRIBUTING.md",
                                               "theirs": "https://github.com/o/r/blob/main/b.md"}


def test_a_link_to_a_heading_that_does_not_exist_is_refused(sources: list[pathlib.Path],
                                                            tmp_path: pathlib.Path) -> None:
    sources[1].write_text(CHECKLIST + "\nSee [§9](guide.md#9-nowhere).\n")
    with pytest.raises(ValueError):
        docx.build(tmp_path / "doc.docx", sources, DAY)
    assert not (tmp_path / "doc.docx").exists() and not (tmp_path / "doc.docx.tmp").exists()


def test_a_file_without_a_title_is_refused(sources: list[pathlib.Path], tmp_path: pathlib.Path) -> None:
    sources[1].write_text("No heading here.\n\n```sh\n# not a heading\n```\n")
    with pytest.raises(ValueError, match="no level-1 heading"):
        docx.build(tmp_path / "doc.docx", sources, DAY)


def test_the_document_is_reproducible_styled_and_linked(sources: list[pathlib.Path], tmp_path: pathlib.Path) -> None:
    first, second = tmp_path / "a.docx", tmp_path / "b.docx"
    docx.build(first, sources, DAY)
    docx.build(second, sources, DAY)
    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as z:
        styles = z.read("word/styles.xml").decode()
        body = z.read("word/document.xml").decode()
        stamps = {info.date_time for info in z.infolist()}
    assert stamps == {(2026, 10, 13, 0, 0, 0)}
    table = re.search(r'<w:style w:type="table" w:default="1" w:styleId="Table">.*?</w:style>', styles, re.S).group(0)
    assert "<w:tblBorders>" in table and docx.RULE in table and docx.GROUND in table
    assert f'<w:color w:val="{docx.REMOTE}"' in styles
    docx.check_links(first)                                   # raises if an internal link leads nowhere
    assert len(re.findall(r'w:anchor="', body)) == 4


def test_a_different_date_changes_only_the_stamp(sources: list[pathlib.Path], tmp_path: pathlib.Path) -> None:
    docx.build(tmp_path / "a.docx", sources, DAY)
    docx.build(tmp_path / "b.docx", sources, date(2026, 10, 14))
    with zipfile.ZipFile(tmp_path / "a.docx") as a, zipfile.ZipFile(tmp_path / "b.docx") as b:
        assert a.read("word/document.xml") == b.read("word/document.xml")
        assert {i.date_time for i in b.infolist()} == {(2026, 10, 14, 0, 0, 0)}


def test_a_template_in_the_users_pandoc_directory_changes_nothing(sources: list[pathlib.Path], tmp_path: pathlib.Path,
                                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    docx.build(tmp_path / "plain.docx", sources, DAY)
    template = subprocess.run(["pandoc", "-D", "openxml"], check=True, capture_output=True, text=True).stdout
    templates = tmp_path / "home/.local/share/pandoc/templates"
    templates.mkdir(parents=True)
    marker = "<w:body><w:p><w:r><w:t>HOME</w:t></w:r></w:p>"
    (templates / "default.openxml").write_text(template.replace("<w:body>", marker, 1))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    docx.build(tmp_path / "home.docx", sources, DAY)
    assert (tmp_path / "home.docx").read_bytes() == (tmp_path / "plain.docx").read_bytes()


def test_the_file_does_not_depend_on_pythons_zlib(sources: list[pathlib.Path], tmp_path: pathlib.Path,
                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    docx.build(tmp_path / "a.docx", sources, DAY)
    deflate = zlib.compressobj
    # Another deflate implementation (zlib-ng, which CPython uses on Windows) gives other bytes for the same data;
    # another level stands in for it here.
    monkeypatch.setattr(zlib, "compressobj", lambda level=-1, *rest: deflate(1, *rest))
    docx.build(tmp_path / "b.docx", sources, DAY)
    assert (tmp_path / "a.docx").read_bytes() == (tmp_path / "b.docx").read_bytes()


def test_an_image_is_found_beside_its_file_from_any_directory(tmp_path: pathlib.Path,
                                                              monkeypatch: pytest.MonkeyPatch) -> None:
    paths = write(tmp_path / "repo", {"docs/GUIDE.md": "# Guide\n\n![How it works](img/figure.png)\n"})
    (tmp_path / "repo/docs/img").mkdir()
    (tmp_path / "repo/docs/img/figure.png").write_bytes(PNG)
    monkeypatch.chdir(tmp_path / "repo")
    docx.build(tmp_path / "doc.docx", paths, DAY)
    with zipfile.ZipFile(tmp_path / "doc.docx") as z:
        assert [name for name in z.namelist() if name.startswith("word/media/")]


def test_an_image_that_is_not_there_is_refused(tmp_path: pathlib.Path) -> None:
    paths = write(tmp_path, {"GUIDE.md": "# Guide\n\n![gone](nowhere.png)\n"})
    with pytest.raises(subprocess.CalledProcessError):
        docx.build(tmp_path / "doc.docx", paths, DAY)
    assert not (tmp_path / "doc.docx").exists() and not (tmp_path / "doc.docx.tmp").exists()


def test_a_pandoc_that_dies_while_writing_leaves_no_partial_file(sources: list[pathlib.Path],
                                                                 tmp_path: pathlib.Path) -> None:
    # On 2026-10-13 a pandoc stopped by a file-size limit (SIGXFSZ) left 200 KB of OUT.docx.tmp behind.
    fake = tmp_path / "pandoc"
    fake.write_text(f"""#!{sys.executable}
import subprocess, sys
args = sys.argv[1:]
code = subprocess.run([{shutil.which("pandoc")!r}, *args]).returncode
if code == 0 and "docx" in args:
    with open(args[args.index("--output") + 1], "r+b") as out:
        out.truncate(100)
    code = 1
sys.exit(code)
""")
    fake.chmod(0o755)
    out = tmp_path / "doc.docx"
    out.write_bytes(b"the last good build")
    with pytest.raises(subprocess.CalledProcessError):
        docx.build(out, sources, DAY, pandoc=str(fake))
    assert out.read_bytes() == b"the last good build" and not (tmp_path / "doc.docx.tmp").exists()


def test_pandoc_3_12_1_gives_these_bytes_on_every_machine(sources: list[pathlib.Path], tmp_path: pathlib.Path) -> None:
    """The hash with pandoc 3.12.1, the version ci.yml pins, measured on macOS with Homebrew's build and with the
    release's own (2026-10-13); ci.yml checks it on Linux with the release's .deb. Another hash on a machine means the
    same pandoc gives other bytes there, and a repository's CI comparison would fail for whoever builds on it."""
    version = subprocess.run(["pandoc", "--version"], check=True, capture_output=True, text=True).stdout.split()[1]
    if version != "3.12.1":
        pytest.skip(f"the hash is pandoc 3.12.1's, not pandoc {version}'s")
    docx.build(tmp_path / "doc.docx", sources, DAY)
    assert hashlib.sha256((tmp_path / "doc.docx").read_bytes()).hexdigest() == \
        "13f455470f5d8eacc5c46d5059a8bd33fb51b17d93c6caf1587e31e2764c8ec4"
