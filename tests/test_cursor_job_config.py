# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The job folder limits reads, keeps the allow list and drops the login, and the main configuration does not change."""

from __future__ import annotations

import json
import pathlib
import stat
import subprocess
import sys

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "skill" / "tokensave-fork" / "cursor-job-config.py"


def build(tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, bytes]:
    source, target = tmp_path / "cursor", tmp_path / "jobs"
    source.mkdir()
    main = {"permissions": {"allow": ["Mcp(tokensave:tokensave_search)"], "deny": []}, "authInfo": {"email": "someone"},
            "sandbox": {"mode": "disabled"}}
    (source / "cli-config.json").write_text(json.dumps(main))
    (source / "mcp.json").write_text("{}")
    before = (source / "cli-config.json").read_bytes()
    subprocess.run([sys.executable, str(SCRIPT), "--source", str(source), "--target", str(target)], check=True, capture_output=True)
    return source, target, before


def test_the_copy_limits_reads_keeps_the_allow_list_and_drops_the_login(tmp_path):
    _, target, _ = build(tmp_path)
    copy = json.loads((target / "cli-config.json").read_text())
    assert copy["sandbox"] == {"mode": "disabled", "readBoundary": "workspace"}
    assert copy["permissions"]["allow"] == ["Mcp(tokensave:tokensave_search)"]
    assert "authInfo" not in copy
    assert stat.S_IMODE((target / "cli-config.json").stat().st_mode) == 0o600


def test_the_main_configuration_does_not_change_and_the_servers_are_linked(tmp_path):
    source, target, before = build(tmp_path)
    assert (source / "cli-config.json").read_bytes() == before
    assert (target / "mcp.json").resolve() == (source / "mcp.json").resolve()
    assert not (target / "hooks.json").exists()


def test_a_second_operation_replaces_the_copy_and_the_links(tmp_path):
    source, target, _ = build(tmp_path)
    (source / "hooks.json").write_text("{}")
    subprocess.run([sys.executable, str(SCRIPT), "--source", str(source), "--target", str(target)], check=True, capture_output=True)
    assert (target / "hooks.json").is_symlink()
