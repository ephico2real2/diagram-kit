# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""A timestamp prefix is not sufficient for a valid UTC tracker time."""
import pytest
from test_handover import project, run, TRACKER, write_note


@pytest.mark.parametrize("updated", [
    "2026-02-30 20:00", "2026-11-07 25:00", "2026-11-07 20:00 arbitrary suffix",
])
def test_invalid_done_times_are_rejected(project, updated):
    path = project / "claude-resumes" / "TRACKER-demo.md"
    path.write_text(TRACKER.replace("2026-11-07 20:00", updated))
    write_note(project)
    result = run(project, "check")
    assert result.returncode == 1
    assert "a done unit needs its evidence" in result.stdout


@pytest.mark.parametrize("updated", ["2026-11-07 20:00", "2026-11-07 20:00 (14:00 CST)", "2026-11-07 20:00 (17:00 -03)"])
def test_valid_done_times_stay_valid(project, updated):
    path = project / "claude-resumes" / "TRACKER-demo.md"
    path.write_text(TRACKER.replace("2026-11-07 20:00", updated))
    write_note(project)
    assert run(project, "check").returncode == 0
