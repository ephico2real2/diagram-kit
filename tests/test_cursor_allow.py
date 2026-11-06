# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The allow list gets the read tools and no tool that writes, and the rest of Cursor's file stays. No test reaches the
network: a stand-in plays the tokensave server."""

from __future__ import annotations

import json
import pathlib
import stat
import subprocess
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "tokensave-fork" / "cursor-allow.py"

STAND_IN = textwrap.dedent(f"""\
    #!{sys.executable}
    import json, sys
    tools = [{{"name": "tokensave_search", "annotations": {{"readOnlyHint": True}}}},
             {{"name": "tokensave_node", "annotations": {{"readOnlyHint": True}}}},
             {{"name": "tokensave_str_replace", "annotations": {{"readOnlyHint": False}}}},
             {{"name": "tokensave_session_start"}}]
    for line in sys.stdin:
        message = json.loads(line)
        if "id" not in message:
            continue
        result = {{"tools": tools}} if message["method"] == "tools/list" else {{}}
        print(json.dumps({{"jsonrpc": "2.0", "id": message["id"], "result": result}}), flush=True)
""")


def stand_in(tmp_path: pathlib.Path) -> pathlib.Path:
    binary = tmp_path / "tokensave"
    binary.write_text(STAND_IN)
    binary.chmod(binary.stat().st_mode | stat.S_IEXEC)
    return binary


def run(binary: pathlib.Path, config: pathlib.Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), "--tokensave", str(binary), "--config", str(config)],
                          capture_output=True, text=True, timeout=60)


def test_only_the_read_tools_are_allowed(tmp_path):
    config = tmp_path / "cli-config.json"
    result = run(stand_in(tmp_path), config)
    assert result.returncode == 0, result.stderr
    assert json.loads(config.read_text())["permissions"]["allow"] == [
        "Mcp(tokensave:tokensave_more)", "Mcp(tokensave:tokensave_node)", "Mcp(tokensave:tokensave_search)"]


def test_the_rest_of_the_file_stays_and_a_second_run_adds_nothing(tmp_path):
    config = tmp_path / "cli-config.json"
    config.write_text(json.dumps({"model": "x", "permissions": {"allow": ["Shell(ls)"], "deny": ["Shell(rm)"]}}))
    binary = stand_in(tmp_path)
    run(binary, config)
    first = json.loads(config.read_text())
    assert first["model"] == "x"
    assert first["permissions"]["deny"] == ["Shell(rm)"]
    assert first["permissions"]["allow"][0] == "Shell(ls)"
    assert "0 added" in run(binary, config).stdout
    assert json.loads(config.read_text()) == first


def test_a_missing_binary_is_named_and_the_file_is_not_touched(tmp_path):
    config = tmp_path / "cli-config.json"
    result = run(tmp_path / "absent", config)
    assert result.returncode == 1
    assert "build the fork first" in result.stderr
    assert not config.exists()
