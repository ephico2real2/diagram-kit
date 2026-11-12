# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Read the closure condition in both skills against the default-branch rule."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name", ["issue", "epic"])
def test_completed_work_waits_for_the_default_branch(name):
    text = (ROOT / "skill" / name / "SKILL.md").read_text()
    assert "default branch" in text
    assert "status:fixed-on-review-branch" in text
    assert "close it straight away" not in text
    assert "Close the ones that are already done" not in text
    assert "gh issue close" in text
