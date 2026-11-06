#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Show, from the log of an agent, whether it read code through tokensave and whether it read a whole file.

An agent's own report cannot prove this, and a call to `tokensave_read` does not prove it either: that tool reads the
whole file by default, up to the response cap of the server. The input is the output of `codex exec --json` or of
`cursor-agent -p --output-format stream-json`. Operate the agent from an empty folder, so that each read of the project
must name the project root. The exit status is 0 for PASS, 1 for FAIL and 2 for a log that this script cannot read.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import pathlib
import re
import sys

# These two tools report on the server and read no code, so a call to them shows nothing about how the agent read.
NOT_READING_CODE = {"tokensave_status", "tokensave_more"}
# Cursor's call that fetches a tool's schema names the tool, but does not call it.
NOT_A_CALL = {"getMcpToolsToolCall"}
SHELL_READER = re.compile(r"(?:^|[\s;&|(\"'])(rg|ag|grep|cat|sed|awk|head|tail|less|more|nl|bat)\s")
TRUNCATED = "[... truncated at "
# macOS writes this when a sandbox refuses a read. The exit status cannot show it: `cat file | wc -c` exits 0.
SANDBOX_REFUSAL = "Operation not permitted"


@dataclasses.dataclass
class Call:
    kind: str  # graph, shell, read or other
    name: str
    args: dict
    state: str  # ok, refused or failed
    text: str = ""


def text_of(value: object) -> str:
    """Join each string under a `text` key. Codex and Cursor nest the answer of a tool differently."""
    if isinstance(value, list):
        return "".join(text_of(item) for item in value)
    if isinstance(value, dict):
        return "".join(item if key == "text" and isinstance(item, str) else text_of(item) for key, item in value.items())
    return ""


def codex_call(record: dict) -> Call | None:
    item = record.get("item", {})
    if record.get("type") != "item.completed":
        return None
    if item.get("type") == "mcp_tool_call":
        kind = "graph" if item.get("server") == "tokensave" else "other"
        state = "ok" if item.get("status") == "completed" and not item.get("error") else "failed"
        return Call(kind, item.get("tool", ""), item.get("arguments") or {}, state, text_of(item.get("result") or {}))
    if item.get("type") == "command_execution":
        # A command with a nonzero exit still ran, so only a declined command read nothing.
        output = item.get("aggregated_output", "")
        state = "refused" if item.get("status") == "declined" or SANDBOX_REFUSAL in output else "ok"
        return Call("shell", "shell", {"command": item.get("command", "")}, state, output)
    return None


def cursor_call(record: dict) -> Call | None:
    if record.get("type") != "tool_call" or record.get("subtype") != "completed":
        return None
    tool_call = record.get("tool_call", {})
    key = next((name for name in tool_call if name.endswith("ToolCall")), None)
    if key is None or key in NOT_A_CALL:
        return None
    args, result = tool_call[key].get("args") or {}, tool_call[key].get("result") or {}
    success = result.get("success")
    failed = success is None or (isinstance(success, dict) and success.get("isError"))
    state = "refused" if "rejected" in result else "failed" if failed else "ok"
    if key == "mcpToolCall":
        server, _, tool = args.get("name", "").partition("-")
        return Call("graph" if server == "tokensave" else "other", tool, args.get("args") or {}, state, text_of(success or {}))
    if key == "shellToolCall":
        output = str((success or {}).get("stderr", "")) if isinstance(success, dict) else ""
        return Call("shell", "shell", args, "refused" if SANDBOX_REFUSAL in output else state, output)
    if key == "readToolCall":
        return Call("read", "read", args, state)
    # No log showed another tool's shape, so the audit judges any other tool only by whether its args name the project.
    return Call("other", key, args, state)


def load_calls(log: pathlib.Path) -> list[Call]:
    calls = []
    for number, line in enumerate(log.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            print(f"{log}:{number}: not JSON ({error}). Use codex exec --json or cursor-agent --output-format stream-json.",
                  file=sys.stderr)
            sys.exit(2)
        call = codex_call(record) or cursor_call(record)
        if call:
            calls.append(call)
    return calls


def line_range(args: dict, total: int) -> range:
    """The 1-based lines that a `mode: lines` call asks for."""
    if args.get("lines"):
        first, _, last = str(args["lines"]).partition("-")
        return range(int(first), min(int(last or first), total) + 1)
    return range(int(args.get("start", 1)), min(int(args.get("end", total)), total) + 1)


def audit(calls: list[Call], root: pathlib.Path) -> tuple[list[str], list[str]]:
    """Return the facts to print and the problems. Any problem is a FAIL."""
    facts, problems = [], []
    seen: dict[str, set[int]] = {}
    totals: dict[str, int] = {}
    for call in calls:
        where = json.dumps(call.args)
        if call.kind == "graph":
            size = f"{len(call.text)} chars" + (", truncated by the server" if TRUNCATED in call.text else "")
            facts.append(f"{call.name}: {call.state}, {size}")
            if call.name == "tokensave_read" and call.state == "ok":
                name = call.args.get("file") or call.args.get("path") or ""
                mode = call.args.get("mode", "full")
                if mode == "full":
                    problems.append(f"tokensave_read of {name} with mode {mode} asks for the whole file")
                elif mode == "lines" and (root / name).is_file():
                    totals[name] = len((root / name).read_text(errors="replace").splitlines())
                    seen.setdefault(name, set()).update(line_range(call.args, totals[name]))
        elif call.kind == "shell":
            command = str(call.args.get("command", ""))
            facts.append(f"shell: {call.state}: {command[:100]}")
            if call.state == "ok" and str(root) in command and SHELL_READER.search(command):
                problems.append(f"the shell read the project: {command[:100]}")
        elif call.kind == "read":
            facts.append(f"native read: {call.state}: {call.args.get('path', '')}")
            if call.state == "ok" and pathlib.Path(str(call.args.get("path", ""))).is_relative_to(root):
                problems.append(f"the native read tool read {call.args['path']}")
        else:
            facts.append(f"{call.name}: {call.state}")
            if call.state == "ok" and str(root) in where:
                problems.append(f"{call.name} reached the project outside tokensave")
    for name, lines in seen.items():
        facts.append(f"{name}: {len(lines)} of {totals[name]} lines through tokensave_read")
        if len(lines) >= totals[name]:
            problems.append(f"slices of {name} cover the whole file")
    if not any(c.kind == "graph" and c.state == "ok" and c.name not in NOT_READING_CODE for c in calls):
        problems.append("no tokensave tool that reads code answered")
    return facts, problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("log", type=pathlib.Path, help="the output of codex exec --json or cursor-agent stream-json")
    parser.add_argument("--root", type=pathlib.Path, required=True, help="the absolute path of the indexed project")
    arguments = parser.parse_args()
    facts, problems = audit(load_calls(arguments.log), arguments.root.expanduser().resolve())
    for fact in facts:
        print(f"  {fact}")
    for problem in problems:
        print(f"  PROBLEM: {problem}")
    print("FAIL" if problems else "PASS")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
