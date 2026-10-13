# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""doc-docx: the joined Markdown links inside itself, and the Word file is styled, linked and reproducible.

The joining tests need no pandoc. The end-to-end tests run pandoc and are skipped where it is not installed; CI
installs it, so they always run there.
"""

from __future__ import annotations

import pathlib
import re
import shutil
import zipfile
from datetime import date

import pytest

from diagram_kit import docx

GUIDE = """# A guide for developers

See the [checklist.md](checklist.md) and [step two](checklist.md#before-you-ask).

## 2. Before you start

Text with an ![image](figure.png) and a [site](https://example.org).
"""
CHECKLIST = """# The checklist

## Before you ask

- [ ] I read [§2](guide.md#2-before-you-start) of the [guide](guide.md).
"""


@pytest.fixture
def sources(tmp_path: pathlib.Path) -> list[pathlib.Path]:
    guide, checklist = tmp_path / "guide.md", tmp_path / "checklist.md"
    guide.write_text(GUIDE)
    checklist.write_text(CHECKLIST)
    return [guide, checklist]


def test_github_slug_matches_githubs_anchors() -> None:
    assert docx.github_slug("2. Before you start") == "2-before-you-start"
    assert docx.github_slug("Step 1: the groups, in each environment's directory") == \
        "step-1-the-groups-in-each-environments-directory"
    assert docx.github_slug("The `pay` example") == "the-pay-example"


def test_links_between_the_files_point_inside_the_document(sources: list[pathlib.Path]) -> None:
    joined = docx.join(sources)
    assert "[The checklist](#the-checklist)" in joined          # a file-name label takes the file's title
    assert "[step two](#before-you-ask)" in joined
    assert "[§2](#2-before-you-start)" in joined
    assert "[guide](#a-guide-for-developers)" in joined
    assert "](figure.png)" in joined and "](https://example.org)" in joined   # other links are left alone
    assert ".md" not in re.sub(r"\]\([^)]*\)", "", joined).replace("checklist.md", "")
    assert joined.count('<w:br w:type="page"/>') == 1


def test_a_link_to_a_file_outside_the_document_is_refused(sources: list[pathlib.Path]) -> None:
    sources[1].write_text(CHECKLIST + "\nSee [the design](DESIGN.md).\n")
    with pytest.raises(ValueError, match="DESIGN.md, which is not part of this document"):
        docx.join(sources)


def test_a_file_without_a_title_is_refused(sources: list[pathlib.Path]) -> None:
    sources[1].write_text("No heading here.\n")
    with pytest.raises(ValueError, match="no level-1 heading"):
        docx.join(sources)


needs_pandoc = pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc is not installed")


@needs_pandoc
def test_the_document_is_reproducible_styled_and_linked(sources: list[pathlib.Path], tmp_path: pathlib.Path) -> None:
    first, second = tmp_path / "a.docx", tmp_path / "b.docx"
    docx.build(first, sources, date(2026, 10, 13))
    docx.build(second, sources, date(2026, 10, 13))
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


@needs_pandoc
def test_a_different_date_changes_only_the_stamp(sources: list[pathlib.Path], tmp_path: pathlib.Path) -> None:
    docx.build(tmp_path / "a.docx", sources, date(2026, 10, 13))
    docx.build(tmp_path / "b.docx", sources, date(2026, 10, 14))
    with zipfile.ZipFile(tmp_path / "a.docx") as a, zipfile.ZipFile(tmp_path / "b.docx") as b:
        assert a.read("word/document.xml") == b.read("word/document.xml")
        assert {i.date_time for i in b.infolist()} == {(2026, 10, 14, 0, 0, 0)}
