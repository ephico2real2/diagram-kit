# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Invalid note timestamps must produce a failure, not crash a hook."""
import pytest
from test_handover import project, run, stamp
import json


@pytest.mark.parametrize("invalid", ["2026-02-30 12:00", "2026-11-07 25:61"])
def test_invalid_timestamp_still_blocks_stop(project, invalid):
    path = project / "claude-resumes" / "HANDOVER-demo.md"
    path.write_text(path.read_text().replace(stamp(), invalid))
    result = run(project, "stop", hook={"stop_hook_active": False})
    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout)["decision"] == "block"
    result = run(project, "check")
    assert result.returncode == 1
    assert result.stderr == ""
    assert "invalid UTC date or time" in result.stdout
