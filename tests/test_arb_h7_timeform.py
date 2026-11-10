# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
from pathlib import Path

def test_both_guides_state_that_local_time_is_optional():
    root = Path(__file__).resolve().parents[1]
    for name in ('handover', 'build-tracker'):
        text = (root / 'skill' / name / 'SKILL.md').read_text()
        assert 'The local time in parentheses is optional.' in text
