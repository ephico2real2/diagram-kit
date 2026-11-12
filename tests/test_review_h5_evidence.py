# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Done evidence needs an identifier or a counted test result."""
import pytest
from test_handover import project, run, TRACKER, write_note


@pytest.mark.parametrize("evidence", ["passed", "failed", "deployed", "https://"])
def test_bare_evidence_keywords_are_not_results(project, evidence):
    path = project / "claude-resumes" / "TRACKER-demo.md"
    path.write_text(TRACKER.replace("commit abc1234, PR #11, CI run 77 passed", evidence))
    write_note(project)
    result = run(project, "check")
    assert result.returncode == 1
    assert "a done unit needs its evidence" in result.stdout


@pytest.mark.parametrize("evidence", [
    "4 passed", "2 failed", "deployed release-42", "https://example.org/runs/42",
    "CI run 42", "PR #42", "commit abc1234",
])
def test_identifiable_evidence_stays_valid(project, evidence):
    path = project / "claude-resumes" / "TRACKER-demo.md"
    path.write_text(TRACKER.replace("commit abc1234, PR #11, CI run 77 passed", evidence))
    write_note(project)
    result = run(project, "check")
    assert (result.returncode, result.stdout) == (0, "")
