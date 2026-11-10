# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Escaped Markdown pipes are cell content, not column separators."""
import importlib.util
from test_handover import project, run, SCRIPT, TRACKER, write_note


def test_tracker_preserves_escaped_pipes(project):
    text = TRACKER.replace("Build the parser", r"Build the parser \| CLI").replace(
        "step: the body reader", r"step: `printf x \| cat`")
    (project / "claude-resumes" / "TRACKER-demo.md").write_text(text)
    write_note(project)
    spec = importlib.util.spec_from_file_location("handover", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = module.tracker_rows(text)
    assert len(rows) == 3
    assert rows[1]["unit"] == "Build the parser | CLI"
    assert rows[1]["evidence"] == "step: `printf x | cat`"
    result = run(project, "check")
    assert (result.returncode, result.stdout) == (0, "")
