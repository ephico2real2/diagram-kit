# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""PR #38 regression: read-only Git commands are not milestones."""
import json
import pytest
from test_handover import project, run


@pytest.mark.parametrize("command", ["git merge-base A B", "git merge-base --is-ancestor A B"])
def test_read_only_git_commands_do_not_request_tracker_updates(project, command):
    result = run(project, "post-tool", hook={"tool_input": {"command": command}})
    assert result.returncode == 0
    assert result.stdout == ""


@pytest.mark.parametrize("command", ["git push; git status", "git push&&git status", "git push>push.log"])
def test_real_milestones_before_shell_operators_keep_the_reminder(project, command):
    result = run(project, "post-tool", hook={"tool_input": {"command": command}})
    assert result.returncode == 0
    assert "record it in the tracker" in json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
