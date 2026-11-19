# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""doc-page makes one light page from one Markdown document, or writes nothing.

The tests that run pandoc are skipped where pandoc is not installed, except in CI (ci.yml installs it): there a
missing pandoc fails them. The tests of `build` give it the HTML that pandoc makes, so they need no pandoc."""
import os
import re
import shutil
from pathlib import Path

import pytest

from diagram_kit import docpage

needs_pandoc = pytest.mark.skipif(shutil.which("pandoc") is None and not os.environ.get("CI"),
                                  reason="pandoc is not installed")

HEAD = '<h1 id="the-title">The <code>title</code></h1>\n<p>A. Writer, Engineer.</p>\n'
FIG = '<p><img src="diagrams/a/a.light.png" alt="The claim." /></p>\n<p><em>Figure 1. The claim</em>.</p>\n'


def page(body, **kw):
    return docpage.build(HEAD + body, kw.pop("eyebrow", "Docs"), kw.pop("title", "The Guide"), **kw)


def test_a_picture_and_its_caption_become_one_figure():
    html, count, _ = page('<h2 id="one">One</h2>\n' + FIG, figures=1)
    assert count == 1
    assert ('<figure><div class="shot"><img loading="lazy" src="diagrams/a/a.light.png" alt="The claim.">'
            '</div><figcaption>Figure 1. The claim.</figcaption></figure>') in html


def test_a_caption_that_ends_in_a_period_gets_no_second_one():
    # The period can sit inside the italics. The page then showed "the claim.." before this fix.
    inside = '<p><img src="a.png" alt="x" /></p>\n<p><em>Figure 1. The claim.</em></p>\n'
    html, _, _ = page(inside, figures=1)
    assert "<figcaption>Figure 1. The claim.</figcaption>" in html
    assert "..</figcaption>" not in html


def test_a_picture_with_no_caption_is_refused():
    with pytest.raises(docpage.PageError, match="no italic caption"):
        page('<p><img src="a.png" alt="x" /></p>\n<p>Plain text.</p>\n')


def test_the_figure_count_is_checked_when_given():
    with pytest.raises(docpage.PageError, match="expected 2 pictures with captions, found 1"):
        page(FIG, figures=2)


def test_the_document_must_open_with_a_title_and_a_byline():
    with pytest.raises(docpage.PageError, match="H1 and a byline"):
        docpage.build("<p>No title.</p>\n", "Docs", "The Guide")


def test_the_contents_list_the_h2_headings_and_the_tab_title_is_the_short_name():
    html, _, sections = page('<h2 id="one">One <code>x</code></h2>\n<h2 id="two">Two</h2>\n')
    assert sections == 2
    assert '<li><a href="#one">One x</a></li><li><a href="#two">Two</a></li>' in html
    assert "<title>The Guide</title>" in html
    assert "<h1>The <code>title</code></h1>" in html


def test_a_table_scrolls_in_its_own_box():
    html, _, _ = page("<table><tr><td>1</td></tr></table>\n")
    assert '<div class="scroll"><table><tr><td>1</td></tr></table></div>' in html


def test_the_band_wraps_its_section_and_must_exist():
    html, _, _ = page('<h2 id="story">Story</h2>\n<p>a</p>\n<h2 id="next">Next</h2>\n', band="story")
    assert '<section class="story"><h2 id="story">Story</h2>\n<p>a</p>\n</section><h2 id="next">' in html
    with pytest.raises(docpage.PageError, match="no H2 with the id missing"):
        page('<h2 id="story">Story</h2>\n', band="missing")


def test_a_link_to_a_private_page_is_refused():
    with pytest.raises(docpage.PageError, match="claude.ai/"):
        page('<p><a href="https://claude.ai/artifact/x">the page</a></p>\n')


def test_placeholder_text_in_the_document_is_left_as_written():
    html, _, _ = page("<p><code>{{TOC}}</code> and {{BODY}}</p>\n")
    assert "<p><code>{{TOC}}</code> and {{BODY}}</p>" in html


def test_the_eyebrow_is_text():
    html, _, _ = page("", eyebrow="A & B <i>")
    assert '<span class="eyebrow">A &amp; B &lt;i&gt;</span>' in html


def test_the_page_is_light_on_white():
    html, _, _ = page("")
    assert "color-scheme: light;" in html and "--bg: #ffffff;" in html
    assert "prefers-color-scheme: dark" not in html


@needs_pandoc
def test_the_command_builds_from_markdown_and_reads_images_beside_the_source(tmp_path, capsys):
    src = tmp_path / "docs" / "GUIDE.md"
    src.parent.mkdir()
    src.write_text("# A guide\n\nA. Writer, Engineer.\n\n## One\n\n![The claim.](diagrams/a/a.light.png)\n\n"
                   "*Figure 1. The claim.*\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    out = tmp_path / "guide.html"
    assert docpage.main([str(src), str(out), "--eyebrow", "Docs", "--title", "A Guide", "--figures", "1"]) == 0
    html = out.read_text()
    assert '<img loading="lazy" src="diagrams/a/a.light.png" alt="The claim.">' in html
    assert '<div class="scroll"><table>' in html
    assert "1 figures, 1 sections" in capsys.readouterr().out


@needs_pandoc
def test_the_command_writes_nothing_when_a_check_fails(tmp_path, capsys):
    src = tmp_path / "GUIDE.md"
    src.write_text("# A guide\n\nA. Writer.\n\n![x](a.png)\n\nNo caption.\n")
    out = tmp_path / "guide.html"
    assert docpage.main([str(src), str(out), "--eyebrow", "Docs", "--title", "A Guide"]) == 1
    assert not out.exists()
    assert "no italic caption" in capsys.readouterr().err


def test_a_title_of_one_word_or_of_five_words_is_refused():
    for title in ("Guide", "A guide to the whole platform"):
        with pytest.raises(docpage.PageError, match="two to four words"):
            page("", title=title)


def test_the_tab_title_is_text_and_the_heading_keeps_its_markup():
    html, _, _ = page("", title="Trace & Logs")
    assert "<title>Trace &amp; Logs</title>" in html
    assert "<h1>The <code>title</code></h1>" in html


def test_only_a_standalone_page_carries_its_own_doctype_and_charset():
    beside, _, _ = page("", standalone=True)
    assert beside.startswith('<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n')
    main_page, _, _ = page("")
    assert "<!doctype" not in main_page.lower()


SKILL = Path(__file__).resolve().parents[1] / "skill" / "document" / "SKILL.md"


def test_the_template_colours_are_the_look_that_the_document_skill_records():
    # The skill holds the table of the page look; the template must use exactly those values.
    rows = re.findall(r"^\| `(--[a-z-]+)` \| `(#[0-9a-f]{6})` \|", SKILL.read_text(), re.M)
    assert len(rows) >= 8, "the page look table is missing from skill/document/SKILL.md"
    template = docpage.TEMPLATE.read_text()
    for token, value in rows:
        assert f"{token}: {value};" in template, f"{token} is not {value} in docpage.html"


@needs_pandoc
@pytest.mark.parametrize("payload", [
    '<script>alert(1)</script>',
    '<img src="x" onerror="alert(1)">',
    '<a href="javascript:alert(1)">click</a>',
])
@pytest.mark.parametrize("location", ["heading", "section", "caption", "body"])
def test_markdown_html_is_text_in_every_page_slot(tmp_path, payload, location):
    from html.parser import HTMLParser

    class Elements(HTMLParser):
        def __init__(self):
            super().__init__()
            self.tags = []

        def handle_starttag(self, tag, attrs):
            self.tags.append((tag, dict(attrs)))

    src = tmp_path / 'a"&<guide>.md'
    title = payload if location == "heading" else "A guide"
    section = payload if location == "section" else "Summary"
    caption = payload if location == "caption" else "A figure"
    body = payload if location == "body" else "Text"
    src.write_text(f"# {title}\n\nA. Writer.\n\n## {section}\n\n{body}\n\n"
                   f"![An image](images/a.png)\n\n*{caption}*\n")
    out = tmp_path / "page.html"
    assert docpage.main([str(src), str(out), "--eyebrow", "A <script>",
                         "--title", "A </title><script>alert(1)</script>", "--figures", "1"]) == 0
    parsed = Elements()
    parsed.feed(out.read_text())
    assert not any(tag == "script" or "onerror" in attrs or
                   attrs.get("href", "").startswith("javascript:") for tag, attrs in parsed.tags)
    assert sum(tag == "img" for tag, _ in parsed.tags) == 1


@needs_pandoc
@pytest.mark.parametrize("target", ["javascript:alert(1)", "JaVaScRiPt:alert(1)",
                                    "java&#x09;script:alert(1)", "data:text/html,hello", "vbscript:msgbox(1)"])
@pytest.mark.parametrize("image", [False, True])
def test_unsafe_markdown_urls_write_nothing(tmp_path, capsys, target, image):
    src = tmp_path / "guide.md"
    src.write_text(f"# A guide\n\nA. Writer.\n\n{'!' if image else ''}[click]({target})\n\n*Caption.*\n")
    out = tmp_path / "page.html"
    assert docpage.main([str(src), str(out), "--eyebrow", "Docs", "--title", "A Guide"]) == 1
    assert not out.exists()
    assert "unsafe" in capsys.readouterr().err
