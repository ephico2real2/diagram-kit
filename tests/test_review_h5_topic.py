# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""CURRENT must contain one raw topic name."""
import pytest
from test_handover import project, run


@pytest.mark.parametrize("topic", ["demo/", "demo/.", "demo\nsecond"])
def test_topic_validation_does_not_normalize_or_ignore_input(project, topic):
    (project / "claude-resumes" / "CURRENT").write_text(topic + "\n")
    result = run(project, "check")
    assert result.returncode == 1
    assert "must hold one topic name" in result.stdout
