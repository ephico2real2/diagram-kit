# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The job other repositories call, .github/workflows/check-diagrams.yml: what its defaults take from a repository.

No test runs the workflow: its default pathspec is read from the file and given to git in a repository made here.
"""

from __future__ import annotations

import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "check-diagrams.yml").read_text()


def default_pages() -> str:
    return re.search(r'^        default: "(.*)"$', WORKFLOW[WORKFLOW.index("      pages:"):], flags=re.M).group(1)


def test_the_default_pages_are_the_files_named_source_html_and_no_others(tmp_path):
    # "*source.html" also took docs/datasource.html and docs/resource.html: they hold no figure, and the job failed.
    tracked = ["source.html", "docs/a/source.html", "docs/with space/source.html", "docs/datasource.html",
               "docs/resource.html", "docs/a/source.html.bak"]
    for path in tracked:
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_text("<p>a page</p>")
    subprocess.run(["git", "init", "-q", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "--", *tracked], cwd=tmp_path, check=True)
    listed = subprocess.run(["git", "ls-files", "-z", "--", default_pages()], cwd=tmp_path, capture_output=True,
                            text=True, check=True).stdout.split("\0")
    assert sorted(filter(None, listed)) == ["docs/a/source.html", "docs/with space/source.html", "source.html"]
