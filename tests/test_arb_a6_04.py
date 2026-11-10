# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Read the documented edit arguments for every valid previous status."""
from pathlib import Path
import re
import shlex

import pytest

JOB = Path(__file__).parent
ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name", ["fix-defect", "pull-request"])
@pytest.mark.parametrize("old", ["status:open", "status:partly-fixed", "status:owner-action"])
def test_fixed_transition_removes_the_current_status(name, old):
    text = (ROOT / "skill" / name / "SKILL.md").read_text()
    command = re.search(r"gh issue edit <n>[^\n]*", text)[0]
    args = shlex.split(command.replace("<n>", "1").replace("<old status>", old))
    assert args[args.index("--remove-label") + 1] == old
    assert args[args.index("--add-label") + 1] == "status:fixed-on-review-branch"
