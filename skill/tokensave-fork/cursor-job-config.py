#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Make a second Cursor CLI configuration folder for agent jobs, with reads limited to the folder of the job.

`sandbox.readBoundary` is a global setting with no flag, and it also limits a call that has no sandbox, so in the main
file it would limit each Cursor session of the user. A separate folder limits only the call that selects it with
`CURSOR_CONFIG_DIR`. Operate this script again after each change to the allow list, because this file is a copy.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib

LINKED = ("mcp.json", "hooks.json")


def build(source: pathlib.Path, target: pathlib.Path) -> None:
    configuration = json.loads((source / "cli-config.json").read_text())
    # A job logged in with this key removed (2026-11-06), so the copy keeps no account data.
    configuration.pop("authInfo", None)
    configuration.setdefault("sandbox", {})["readBoundary"] = "workspace"
    target.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = target / "cli-config.json"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w") as file:
        json.dump(configuration, file, indent=2)
    for name in LINKED:
        link = target / name
        if link.is_symlink():
            link.unlink()
        if (source / name).exists():
            link.symlink_to(source / name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=pathlib.Path, default=pathlib.Path.home() / ".cursor")
    parser.add_argument("--target", type=pathlib.Path, default=pathlib.Path.home() / ".cursor-jobs")
    arguments = parser.parse_args()
    build(arguments.source, arguments.target)
    print(f"{arguments.target}: sandbox.readBoundary is workspace; {arguments.source}/cli-config.json did not change")


if __name__ == "__main__":
    main()
