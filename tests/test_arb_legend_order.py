# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
from pathlib import Path
import subprocess,sys,os
import pytest
ROOT=Path(__file__).resolve().parents[1]
@pytest.mark.parametrize('header',['| Prefix |','| Class |','| Verdict |'])
def test_legend_order_remains_part_of_the_existing_contract(header):
    path=ROOT/'skill/delivery-playbook/PLAYBOOK.md'
    saved=path.read_bytes()
    text=saved.decode()
    section=text.split('## 14. Legend',1)[1]
    block=section.split(header,1)[1].split('\n\n',1)[0]
    lines=block.splitlines()
    assert lines[2].startswith('|') and lines[3].startswith('|')
    changed=lines.copy();changed[2],changed[3]=changed[3],changed[2]
    assert changed!=lines
    replacement='\n'.join(changed)
    try:
        assert text.count(block)==1
        path.write_bytes(text.replace(block,replacement,1).encode())
        cmd=[sys.executable,'-m','pytest','tests/test_agile.py::test_the_playbook_legend_equals_the_standard_legend','-q','-p','no:cacheprovider']
        result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,env={**os.environ,'PYTHONPATH':'.'})
        assert result.returncode==1 and 'failed' in result.stdout,result.stdout+result.stderr
    finally:
        path.write_bytes(saved)
