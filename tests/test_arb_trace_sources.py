# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
from pathlib import Path
import pytest

@pytest.mark.parametrize('name', ['app-architect/SKILL.md', 'delivery-playbook/PLAYBOOK.md'])
def test_trace_link_instructions_have_direct_sources(name):
    text = (Path(__file__).resolve().parents[1] / 'skill' / name).read_text()
    assert 'https://grafana.com/docs/tempo/latest/set-up-for-tracing/' in text
    assert 'https://grafana.com/docs/grafana/latest/datasources/prometheus/configure/#exemplars' in text
