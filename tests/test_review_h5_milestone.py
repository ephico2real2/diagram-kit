# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Quoted repository paths must not hide commit and push milestones."""
import json
import pytest
from test_handover import project, run


@pytest.mark.parametrize("command", [
    'git -C "repo with spaces" commit -m x',
    "git -C 'repo with spaces' push",
])
def test_quoted_git_repository_paths_keep_the_reminder(project, command):
    result = run(project, "post-tool", hook={"tool_input": {"command": command}})
    assert result.returncode == 0
    assert "record it in the tracker" in json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]


def test_quoted_git_status_stays_quiet(project):
    result = run(project, "post-tool", hook={"tool_input": {"command": 'git -C "repo with spaces" status'}})
    assert (result.returncode, result.stdout) == (0, "")
