# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Task IDs must match the first Running column exactly."""
import json
import pytest
from test_handover import project, run, write_note


@pytest.mark.parametrize("running", [
    "- b70 | task | another job | restart: make",
    "- other | task | purpose mentions b7 | restart: make",
])
def test_stop_requires_an_exact_task_id(project, running):
    hook = {"background_tasks": [{"id": "b7", "status": "running", "description": "build"}]}
    write_note(project, running=running)
    result = run(project, "stop", hook=hook)
    assert result.returncode == 0
    assert json.loads(result.stdout)["decision"] == "block"
    write_note(project, running="- b7 | task | the actual job | restart: make")
    assert run(project, "stop", hook=hook).stdout == ""
