# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""delivery-page: the page needs all three documents, reads one commit, and treats Markdown as text.

Every test that renders runs pandoc and git on a repository made here, with no network. They are skipped where pandoc
is not installed, except in CI (ci.yml installs it): there a missing pandoc fails them.
"""

from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess

import pytest

from diagram_kit import delivery

needs_pandoc = pytest.mark.skipif(shutil.which("pandoc") is None and not os.environ.get("CI"),
                                  reason="pandoc is not installed")

TRACKER = """# Delivery tracker

The backlog holds 5 stories: 2 done, 1 in progress and 2 planned.

## Waves

### W1: First things (phase 1, 2 of 4 stories done)

| 1 | #12 | open | An issue |
| 2 | #13 | open | Another |

### W2: Beside every phase (phase ongoing, 0 of 0 stories done)

| 1 | #14 | open | Ongoing |

## Stories

Text with `workspace:<id>` in code.
"""
HANDOVER = """# Handover

**As of 2026-11-06.** Staging runs one image.

See [the tracker](backlog/TRACKER.md) and [below](#resume-prompt) and [a site](https://example.org/a).

## Resume prompt

Read the tracker first.

## After

Text.
"""


def commit(repo: pathlib.Path, files: dict[str, str]) -> None:
    for path, text in files.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=a", "-c", "user.email=a@example.org", "commit", "-qm",
                    "the subject", "--allow-empty"], check=True)


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(root), "remote", "add", "origin", "git@github.com:acme/widgets.git"], check=True)
    commit(root, {"docs/backlog/TRACKER.md": TRACKER, "docs/handover.md": HANDOVER})
    return root


def build(repo: pathlib.Path, *args: str) -> tuple[int, pathlib.Path]:
    out = repo.parent / "page.html"
    return delivery.main([str(out), "--repo", str(repo), *args]), out


def sha_of(repo: pathlib.Path) -> str:
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()


@needs_pandoc
class TestThePage:
    def test_holds_all_three_documents_and_names_its_commit(self, repo):
        code, out = build(repo)
        page = out.read_text()
        assert code == 0
        assert "Staging runs one image." in page and "Read the tracker first." in page and "Beside every phase" in page
        assert f"https://github.com/acme/widgets/commit/{sha_of(repo)}" in page
        assert "<title>widgets delivery handover</title>" in page
        assert "Handover dated 2026-11-06." in page
        assert page.startswith("<!doctype html>")

    def test_reads_the_commit_not_the_working_tree(self, repo):
        (repo / "docs/handover.md").write_text(HANDOVER + "\nNot committed.\n")
        (repo / "docs/backlog/TRACKER.md").unlink()
        code, out = build(repo)
        assert code == 0
        assert "Not committed." not in out.read_text()

    def test_reads_the_ref_named(self, repo):
        first = sha_of(repo)
        commit(repo, {"docs/handover.md": HANDOVER + "\nLater.\n"})
        code, out = build(repo, "--ref", first)
        assert code == 0
        assert "Later." not in out.read_text() and first[:12] in out.read_text()

    def test_is_the_same_bytes_from_the_same_commit(self, repo):
        _, out = build(repo)
        first = out.read_bytes()
        out.unlink()
        _, out = build(repo)
        assert out.read_bytes() == first

    def test_a_separate_resume_file_is_rendered_and_linked(self, repo):
        commit(repo, {"docs/resume.md": "# Resume\n\nStart here.\n"})
        code, out = build(repo, "--resume", "docs/resume.md")
        page = out.read_text()
        assert code == 0
        assert '<article id="resume"' in page and "Start here." in page and '<a href="#resume">Resume</a>' in page

    def test_a_resume_section_is_linked_where_it_is(self, repo):
        _, out = build(repo)
        page = out.read_text()
        assert '<a href="#h-resume-prompt">Resume</a>' in page and 'id="h-resume-prompt"' in page
        assert page.count('<article id="resume"') == 0

    def test_a_resume_section_of_the_tracker_is_not_rendered_twice(self, repo):
        commit(repo, {"docs/backlog/TRACKER.md": TRACKER + "\n## Resume\n\nWords.\n"})
        code, out = build(repo, "--resume", "docs/backlog/TRACKER.md#Resume")
        page = out.read_text()
        assert code == 0 and page.count("Words.") == 1 and '<a href="#t-resume">Resume</a>' in page

    def test_a_resume_section_can_be_named_by_its_anchor(self, repo):
        code, out = build(repo, "--resume", "docs/handover.md#resume-prompt")
        assert code == 0 and '<a href="#h-resume-prompt">Resume</a>' in out.read_text()

    def test_title_and_address_can_be_given(self, repo):
        code, out = build(repo, "--title", "Widgets <Delivery>", "--repo-url", "https://code.example.org/w/")
        page = out.read_text()
        assert code == 0
        assert "<title>Widgets &lt;Delivery&gt;</title>" in page and "https://code.example.org/w/commit/" in page

    def test_a_footer_is_dropped_only_when_asked(self, repo):
        commit(repo, {"docs/handover.md": HANDOVER + "\n---\n<!-- nav -->\n[Home](x.md)\n"})
        _, out = build(repo)
        assert ">Home<" in out.read_text()
        _, out = build(repo, "--strip-footer", "<!-- nav -->")
        assert ">Home<" not in out.read_text()


@needs_pandoc
class TestARequiredDocument:
    @pytest.mark.parametrize("path, label", [("docs/backlog/TRACKER.md", "tracker"), ("docs/handover.md", "handover")])
    def test_missing_writes_nothing_and_names_it(self, repo, capsys, path, label):
        (repo / path).unlink()
        commit(repo, {})
        code, out = build(repo)
        assert code == 1 and not out.exists()
        assert f"{label}: {path} is not a file at this commit" in capsys.readouterr().err

    def test_a_missing_resume_file_is_refused(self, repo, capsys):
        code, out = build(repo, "--resume", "docs/resume.md")
        assert code == 1 and not out.exists()
        assert "resume: docs/resume.md is not a file at this commit" in capsys.readouterr().err

    def test_every_one_missing_is_named_at_once(self, repo, capsys):
        code, _ = build(repo, "--tracker", "no/t.md", "--handover", "no/h.md", "--resume", "no/r.md")
        err = capsys.readouterr().err
        assert code == 1
        assert "no/t.md" in err and "no/h.md" in err and "no/r.md" in err

    def test_a_refusal_leaves_an_earlier_page_as_it_was(self, repo):
        _, out = build(repo)
        before = out.read_bytes()
        (repo / "docs/handover.md").unlink()
        commit(repo, {})
        code, out = build(repo)
        assert code == 1 and out.read_bytes() == before

    @pytest.mark.parametrize("text", ["", " \n\n\t\n"])
    def test_empty_is_refused(self, repo, capsys, text):
        commit(repo, {"docs/handover.md": text})
        code, _ = build(repo)
        assert code == 1 and "docs/handover.md is empty" in capsys.readouterr().err

    def test_a_directory_is_refused(self, repo, capsys):
        code, _ = build(repo, "--tracker", "docs/backlog")
        assert code == 1 and "docs/backlog is not a file" in capsys.readouterr().err

    def test_a_file_not_utf8_is_refused(self, repo, capsys):
        (repo / "docs/handover.md").write_bytes(b"\xff\xfe not text")
        commit(repo, {})
        code, _ = build(repo)
        assert code == 1 and "is not UTF-8" in capsys.readouterr().err

    def test_a_file_not_committed_is_not_seen(self, repo, capsys):
        (repo / "docs/resume.md").write_text("# Resume\n\nText.\n")
        code, _ = build(repo, "--resume", "docs/resume.md")
        err = capsys.readouterr().err
        assert code == 1 and "resume: docs/resume.md is not a file" in err and "not committed is not seen" in err

    def test_a_section_that_is_absent_is_refused(self, repo, capsys):
        code, out = build(repo, "--resume", "docs/handover.md#Nothing here")
        assert code == 1 and not out.exists()
        assert 'resume: docs/handover.md has no section "Nothing here"' in capsys.readouterr().err

    def test_a_section_with_nothing_in_it_is_refused(self, repo, capsys):
        commit(repo, {"docs/handover.md": "# H\n\nText.\n\n## Resume prompt\n\n## After\n\nText.\n"})
        code, _ = build(repo)
        assert code == 1 and 'resume: the section "Resume prompt" of docs/handover.md is empty' in capsys.readouterr().err

    def test_a_heading_in_a_code_block_is_not_a_section(self, repo, capsys):
        commit(repo, {"docs/handover.md": "# H\n\n```\n## Resume prompt\n\nText.\n```\n"})
        code, _ = build(repo)
        assert code == 1 and "has no section" in capsys.readouterr().err

    def test_a_section_holding_only_subsections_has_content(self, repo):
        commit(repo, {"docs/handover.md": "# H\n\nText.\n\n## Resume prompt\n\n### Part\n\nWords.\n"})
        assert build(repo)[0] == 0

    def test_the_handover_with_no_section_named_cannot_be_the_resume(self, repo, capsys):
        code, _ = build(repo, "--resume", "docs/handover.md")
        assert code == 1 and "Name its section" in capsys.readouterr().err

    def test_one_file_cannot_be_the_tracker_and_the_handover(self, repo, capsys):
        code, _ = build(repo, "--tracker", "docs/handover.md")
        assert code == 1 and "are one file" in capsys.readouterr().err

    def test_a_footer_marker_no_document_holds_is_refused(self, repo, capsys):
        code, _ = build(repo, "--strip-footer", "<!-- nothing -->")
        assert code == 1 and "no document holds" in capsys.readouterr().err

    @pytest.mark.parametrize("ref", ["no-such-ref", "--output=/tmp/x"])
    def test_a_ref_that_is_no_commit_is_refused(self, repo, capsys, ref):
        code, out = build(repo, f"--ref={ref}")
        assert code == 1 and not out.exists()
        assert capsys.readouterr().err.startswith("delivery-page: git rev-parse")


@needs_pandoc
class TestInit:
    def test_writes_each_missing_document_and_the_render_refuses_it(self, tmp_path, capsys):
        root = tmp_path / "repo"
        root.mkdir()
        subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(root), "remote", "add", "origin", "https://github.com/acme/w"], check=True)
        assert delivery.main(["--init", "--repo", str(root)]) == 0
        assert delivery.STARTER in (root / "docs/handover.md").read_text()
        assert "## Resume prompt" in (root / "docs/handover.md").read_text()
        assert delivery.STARTER in (root / "docs/backlog/TRACKER.md").read_text()
        commit(root, {})
        capsys.readouterr()
        code, out = build(root)
        err = capsys.readouterr().err
        assert code == 1 and not out.exists()
        assert "docs/backlog/TRACKER.md is still the starter text" in err and "docs/handover.md is still the starter" in err

    def test_a_filled_starter_renders(self, tmp_path):
        root = tmp_path / "repo"
        root.mkdir()
        subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(root), "remote", "add", "origin", "https://github.com/acme/w"], check=True)
        assert delivery.main(["--init", "--repo", str(root)]) == 0
        for path in ("docs/handover.md", "docs/backlog/TRACKER.md"):
            target = root / path
            target.write_text(target.read_text().replace(delivery.STARTER, ""))
        commit(root, {})
        code, out = build(root)
        assert code == 0 and "W1" in out.read_text()

    def test_never_overwrites_a_file(self, repo, capsys):
        assert delivery.main(["--init", "--repo", str(repo)]) == 0
        assert (repo / "docs/handover.md").read_text() == HANDOVER
        assert (repo / "docs/backlog/TRACKER.md").read_text() == TRACKER
        assert "kept docs/handover.md" in capsys.readouterr().out

    def test_writes_a_separate_resume_file(self, repo):
        assert delivery.main(["--init", "--repo", str(repo), "--resume", "docs/resume.md#Start"]) == 0
        text = (repo / "docs/resume.md").read_text()
        assert delivery.STARTER in text and "# Start" in text

    def test_outside_a_repository_is_refused(self, tmp_path, capsys):
        assert delivery.main(["--init", "--repo", str(tmp_path)]) == 1
        assert not (tmp_path / "docs").exists()
        assert capsys.readouterr().err.startswith("delivery-page: git rev-parse")

    @pytest.mark.parametrize("argv", [["--init", "page.html"], []])
    def test_takes_a_page_or_init_and_not_both(self, argv):
        with pytest.raises(SystemExit):
            delivery.main(argv)


@needs_pandoc
class TestMarkdownIsText:
    """Raw HTML reaches the page's reader, who is often signed in somewhere, so it is never markup."""

    def page(self, repo, markdown: str) -> str:
        commit(repo, {"docs/handover.md": HANDOVER + "\n" + markdown})
        code, out = build(repo)
        assert code == 0
        return out.read_text()

    def test_a_script_block_is_shown_not_run(self, repo):
        page = self.page(repo, "<script>alert(1)</script>\n")
        assert "<script" not in page and "&lt;script&gt;alert(1)&lt;/script&gt;" in page

    def test_an_event_handler_is_shown_not_run(self, repo):
        page = self.page(repo, 'A <img src=x onerror="alert(1)"> B\n')
        assert "<img src=x" not in page and "&lt;img src=x" in page

    def test_a_word_in_angle_brackets_stays_on_the_page(self, repo):
        # Measured on a real tracker: as raw HTML, pandoc's output holds an unknown tag and the browser hides the word.
        page = self.page(repo, "| a |\n|---|\n| scope=workspace:<id> after |\n")
        assert "workspace:&lt;id&gt; after" in page

    def test_a_comment_is_dropped(self, repo):
        page = self.page(repo, "<!-- secret plan -->\n\nA <!-- inline --> B\n")
        assert "secret plan" not in page and "inline" not in page

    def test_markup_after_a_comment_is_not_dropped_with_it(self, repo):
        page = self.page(repo, "<!-- x --><script>alert(1)</script>\n")
        assert "<script" not in page and "&lt;script&gt;" in page

    @pytest.mark.parametrize("target", ["javascript:alert(1)", "JaVaScRiPt:alert(1)", "data:text/html,x", "vbscript:x",
                                        "file:///etc/passwd"])
    def test_a_link_with_another_scheme_keeps_only_its_words(self, repo, target):
        page = self.page(repo, f"[the words]({target})\n")
        assert "the words" in page and target not in page and target.lower() not in page.lower()

    def test_an_image_with_another_scheme_keeps_only_its_words(self, repo):
        page = self.page(repo, "![the alt](data:image/svg+xml,x)\n")
        assert "the alt" in page and "data:image" not in page

    def test_code_is_left_as_written(self, repo):
        page = self.page(repo, '`<a href="x.md">` and\n\n```\n<table href="y.md">\n```\n')
        # Pandoc leaves a double quote bare in inline code, so a rewrite of its HTML would change this link's text.
        assert '<code>&lt;a href="x.md"&gt;</code>' in page and "&lt;table href=&quot;y.md&quot;&gt;" in page


@needs_pandoc
class TestLinks:
    def page(self, repo, markdown: str) -> tuple[str, str]:
        commit(repo, {"docs/handover.md": HANDOVER + "\n" + markdown})
        _, out = build(repo)
        return out.read_text(), sha_of(repo)

    def test_a_relative_link_points_at_the_commit(self, repo):
        page, sha = self.page(repo, "[a](../src/a.py) [b](backlog/b.md#part) [c](/top.md?x=1)\n")
        base = f"https://github.com/acme/widgets/blob/{sha}"
        assert f'href="{base}/src/a.py"' in page
        assert f'href="{base}/docs/backlog/b.md#part"' in page
        assert f'href="{base}/top.md?x=1"' in page

    def test_a_relative_image_points_at_its_bytes_at_the_commit(self, repo):
        page, sha = self.page(repo, "![f](figures/f.png)\n")
        assert f'src="https://github.com/acme/widgets/raw/{sha}/docs/figures/f.png"' in page

    def test_an_absolute_link_is_left_alone(self, repo):
        page, _ = self.page(repo, "[m](mailto:a@example.org) [s](//example.org/s)\n")
        assert 'href="https://example.org/a"' in page
        assert 'href="mailto:a@example.org"' in page and 'href="https://example.org/s"' in page

    def test_an_anchor_stays_inside_its_own_document(self, repo):
        page, _ = self.page(repo, "")
        assert 'href="#h-resume-prompt">below' in page

    def test_a_link_above_the_repository_keeps_only_its_words(self, repo):
        page, _ = self.page(repo, "[far away](../../../x.md)\n")
        assert "far away" in page and "x.md" not in page

    def test_every_table_scrolls_in_its_own_box(self, repo):
        page, _ = self.page(repo, "| a |\n|---|\n| b |\n")
        assert '<div class="scroll"><table>' in page and page.count("<table") == page.count('<div class="scroll">')


@needs_pandoc
class TestSummary:
    def test_the_tiles_and_the_waves_come_from_the_tracker(self, repo):
        _, out = build(repo)
        page = out.read_text()
        assert "<b>5</b><span>stories</span>" in page and "<b>2</b><span>planned</span>" in page
        assert "2 of 4 stories, 2 open" in page and 'style="width:50%"' in page
        assert "1 open issues" in page and "ongoing" in page

    def test_the_last_wave_counts_only_its_own_issues(self):
        text = "### W1: A (phase 1, 0 of 1 stories done)\n\n| 1 | #1 | x |\n\n## Other\n\n| 1 | #2 | x |\n"
        assert ", 1 open" in delivery.wave_rows(text)

    def test_the_last_wave_of_a_tracker_with_nothing_after_it(self):
        text = "### W1: A (phase 1, 0 of 1 stories done)\n\n| 1 | #1 | x |\n| 2 | #2 | x |\n"
        assert ", 2 open" in delivery.wave_rows(text)

    def test_another_format_renders_with_no_summary(self, repo):
        commit(repo, {"docs/backlog/TRACKER.md": "# Our list\n\nOne thing.\n"})
        code, out = build(repo)
        page = out.read_text()
        assert code == 0 and "One thing." in page
        assert 'class="tiles"' not in page and 'id="waves"' not in page and 'href="#waves"' not in page


class TestThePalette:
    @needs_pandoc
    def test_both_themes_by_default_and_light_when_asked(self, repo):
        _, out = build(repo)
        assert "prefers-color-scheme: dark" in out.read_text()
        _, out = build(repo, "--theme", "light")
        page = out.read_text()
        assert "prefers-color-scheme" not in page and 'data-theme="dark"' not in page

    def test_each_colour_comes_from_the_template(self):
        template = (pathlib.Path(delivery.__file__).with_name("template.html")).read_text()
        for value in re.findall(r"--ground: (#[0-9a-f]+)", template):
            assert value in delivery.palette("both")
        for token in re.findall(r"var\((--[a-z-]+)\)", delivery.LAYOUT):
            assert f"{token}:" in delivery.palette("light"), token


class TestTheAddress:
    @pytest.mark.parametrize("remote, url", [
        ("git@github.com:acme/widgets.git", "https://github.com/acme/widgets"),
        ("github.com:acme/widgets", "https://github.com/acme/widgets"),
        ("https://github.com/acme/widgets.git", "https://github.com/acme/widgets"),
        ("https://github.com/acme/widgets/", "https://github.com/acme/widgets"),
        ("ssh://git@github.com:22/acme/widgets.git", "https://github.com/acme/widgets"),
        ("https://user:s3cret@github.com/acme/widgets.git", "https://github.com/acme/widgets"),
        ("https://x-access-token:ghp_abc@github.com/acme/w", "https://github.com/acme/w"),
    ])
    def test_a_remote_becomes_a_web_address_with_no_credential(self, remote, url):
        assert delivery.web_url(remote) == url

    @pytest.mark.parametrize("remote", ["/srv/git/widgets.git", "../widgets", "file:///srv/widgets.git"])
    def test_a_remote_that_is_no_web_address_asks_for_one(self, remote):
        with pytest.raises(ValueError, match="--repo-url"):
            delivery.web_url(remote)

    @pytest.mark.parametrize("value", ["https://u:p@example.org/w", "ftp://example.org/w", "javascript:alert(1)", "w"])
    def test_a_given_address_must_be_web_with_no_credential(self, value):
        with pytest.raises(ValueError, match="--repo-url"):
            delivery.checked_url(value)

    @needs_pandoc
    def test_a_credential_in_the_remote_never_reaches_the_page(self, repo):
        subprocess.run(["git", "-C", str(repo), "remote", "set-url", "origin", "https://u:s3cret@github.com/acme/w.git"],
                       check=True)
        code, out = build(repo)
        assert code == 0 and "s3cret" not in out.read_text()

    @needs_pandoc
    def test_a_repository_with_no_origin_is_refused(self, repo, capsys):
        subprocess.run(["git", "-C", str(repo), "remote", "remove", "origin"], check=True)
        code, out = build(repo)
        assert code == 1 and not out.exists()
        assert "origin" in capsys.readouterr().err


def test_no_pandoc_is_named(repo, capsys, monkeypatch):
    real = shutil.which
    monkeypatch.setattr(delivery.shutil, "which", lambda name: None if name == "pandoc" else real(name))
    code, out = build(repo)
    assert code == 1 and not out.exists()
    assert "pandoc is not installed" in capsys.readouterr().err
