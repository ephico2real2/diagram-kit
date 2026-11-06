#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Add tokensave's read tools to the Cursor CLI allow list, and leave every other key of the file alone.

A headless `cursor-agent` turns a missing approval into `User rejected MCP`, and `tokensave install` writes no allow
entry. The list comes from the server itself, so it follows the installed version: `tokensave_more` and each tool that
declares `readOnlyHint`. A tool that edits a file, records session data or runs tests stays out.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import select
import subprocess
import sys
import time

TIMEOUT_SECONDS = 15


def read_tools(binary: str) -> list[str]:
    """Ask the server for every tool, and return the names that are safe for a headless reader."""
    server = subprocess.Popen(
        [binary, "serve"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1
    )

    def send(message: dict) -> None:
        server.stdin.write(json.dumps(message) + "\n")
        server.stdin.flush()

    def answer(request_id: int) -> dict:
        deadline = time.monotonic() + TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            if select.select([server.stdout], [], [], 1)[0]:
                line = server.stdout.readline()
                if not line:
                    break
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if message.get("id") == request_id:
                    return message
        raise SystemExit(f"{binary} serve gave no answer to request {request_id} in {TIMEOUT_SECONDS} seconds")

    try:
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "cursor-allow", "version": "1"}}})
        answer(1)
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        # The default list holds only the core tools, so ask for the rest first.
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
            "name": "tokensave_more", "arguments": {"area": "all"}}})
        answer(2)
        send({"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {}})
        tools = answer(3)["result"]["tools"]
    finally:
        server.kill()
    names = {tool["name"] for tool in tools if tool.get("annotations", {}).get("readOnlyHint") is True}
    return sorted(names | {"tokensave_more"})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tokensave", default=str(pathlib.Path.home() / ".cargo/bin/tokensave"), help="the binary to ask")
    parser.add_argument("--server", default="tokensave", help="the server name in mcp.json")
    parser.add_argument("--config", default=str(pathlib.Path.home() / ".cursor/cli-config.json"))
    args = parser.parse_args()

    if not pathlib.Path(args.tokensave).is_file():
        print(f"no binary at {args.tokensave}: build the fork first, or pass --tokensave", file=sys.stderr)
        return 1
    config_path = pathlib.Path(args.config)
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    allow = config.setdefault("permissions", {}).setdefault("allow", [])
    config["permissions"].setdefault("deny", [])
    entries = [f"Mcp({args.server}:{name})" for name in read_tools(args.tokensave)]
    added = [entry for entry in entries if entry not in allow]
    allow.extend(added)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    print(f"{config_path}: {len(entries)} read tools, {len(added)} added")
    return 0


if __name__ == "__main__":
    sys.exit(main())
