# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""A tracker edit must not hide inside an undocumented grace period."""
import os
from test_handover import project, run, TRACKER, write_note


def test_tracker_changed_seconds_after_note_is_stale(project):
    note = project / "claude-resumes" / "HANDOVER-demo.md"
    tracker = project / "claude-resumes" / "TRACKER-demo.md"
    tracker.write_text(TRACKER.replace("step: the body reader", "step: a new unrecorded action"))
    later = note.stat().st_mtime + 2
    os.utime(tracker, (later, later))
    result = run(project, "check")
    assert result.returncode == 1
    assert "the tracker changed after the note" in result.stdout
    write_note(project)
    later = tracker.stat().st_mtime + 1
    os.utime(note, (later, later))
    assert run(project, "check").returncode == 0
