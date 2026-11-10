# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
from pathlib import Path

def test_hook_output_description_matches_the_active_topic_behavior():
    guide = (Path(__file__).resolve().parents[1] / 'skill/handover/SKILL.md').read_text()
    assert 'If all is well, each one is silent.' not in guide
    assert 'PreCompact and SessionStart\nemit context for an active topic.' in guide
