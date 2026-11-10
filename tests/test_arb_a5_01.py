# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Compare template guidance with the local gh help saved by this review."""
from pathlib import Path

import pytest

JOB = Path(__file__).parent
ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name", ["fix-defect", "pull-request"])
def test_template_guidance_allows_the_cli(name):
    skill = (ROOT / "skill" / name / "SKILL.md").read_text()
    assert "only for a pull request opened in the browser" not in skill
    assert "--body-file" in skill
