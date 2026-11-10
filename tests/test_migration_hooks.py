# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
from pathlib import Path

def test_selective_sync_does_not_run_migration_hooks():
    text = (Path(__file__).resolve().parents[1] / 'skill/delivery-playbook/PLAYBOOK.md').read_text()
    section = text.split('### Schema migrations, backups and the move to new environments', 1)[1].split('\n## ', 1)[0]
    assert 'Hooks do not run during a selective sync.' in section
