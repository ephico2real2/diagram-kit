# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Repeated compaction must retain every snapshot."""
import datetime as dt
import importlib.util
import pytest
from test_handover import project, SCRIPT, write_note


@pytest.mark.parametrize("seconds_later", [0, 1])
def test_compactions_keep_distinct_snapshots(project, monkeypatch, seconds_later):
    spec = importlib.util.spec_from_file_location("handover", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    instant = dt.datetime.now(dt.timezone.utc).replace(second=0, microsecond=0)
    monkeypatch.setattr(module, "utcnow", lambda: instant)
    monkeypatch.setattr(module, "read_hook", lambda: {"trigger": "auto"})
    note = project / "claude-resumes" / "HANDOVER-demo.md"
    first = note.read_text()
    assert module.cmd_precompact() == 0
    write_note(project, extra="\n- The second snapshot has new state.")
    second = note.read_text()
    instant += dt.timedelta(seconds=seconds_later)
    assert module.cmd_precompact() == 0
    copies = list((project / "claude-resumes" / ".snapshots").glob("*-auto/HANDOVER-demo.md"))
    assert len(copies) == 2
    assert {copy.read_text() for copy in copies} == {first, second}
