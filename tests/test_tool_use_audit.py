# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""The audit passes an agent that read slices through tokensave, and fails each way to read a whole file. The records
have the shapes that `codex exec --json` and `cursor-agent --output-format stream-json` wrote on 2026-11-06."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "skill" / "tokensave-fork" / "tool-use-audit.py"
FILE = "src/big.py"


def codex_graph(tool: str, arguments: dict, text: str = "answer", status: str = "completed") -> dict:
    return {"type": "item.completed", "item": {"type": "mcp_tool_call", "server": "tokensave", "tool": tool, "arguments": arguments,
                                               "status": status, "result": {"content": [{"type": "text", "text": text}]}}}


def codex_shell(command: str, status: str = "completed") -> dict:
    return {"type": "item.completed", "item": {"type": "command_execution", "command": command, "status": status,
                                               "aggregated_output": "output", "exit_code": 0}}


def cursor(kind: str, args: dict, result: dict) -> dict:
    return {"type": "tool_call", "subtype": "completed", "tool_call": {kind: {"args": args, "result": result}}}


def cursor_graph(tool: str, args: dict) -> dict:
    success = {"success": {"content": [{"text": {"text": "answer"}}]}}
    return cursor("mcpToolCall", {"name": f"tokensave-{tool}", "args": args}, success)


def claude(name: str, arguments: dict, text: str = "answer", is_error: bool = False, use_id: str = "use-1") -> list[dict]:
    use = {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": use_id, "name": name, "input": arguments}]}}
    result = {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": use_id, "is_error": is_error,
                                                       "content": [{"type": "text", "text": text}]}]}}
    return [use, result]


@pytest.fixture
def project(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / "src").mkdir()
    (tmp_path / FILE).write_text("line\n" * 10)
    return tmp_path


def operate(project: pathlib.Path, *records: dict) -> subprocess.CompletedProcess:
    log = project / "agent.jsonl"
    log.write_text("".join(json.dumps(record) + "\n" for record in records))
    return subprocess.run([sys.executable, str(SCRIPT), str(log), "--root", str(project)], capture_output=True, text=True)


def test_codex_with_a_slice_passes_and_the_lines_are_counted(project):
    result = operate(project, codex_graph("tokensave_read", {"file": FILE, "mode": "lines", "lines": "2-4"}))
    assert result.returncode == 0, result.stdout
    assert f"{FILE}: 3 of 10 lines" in result.stdout


def test_cursor_with_a_slice_passes(project):
    assert operate(project, cursor_graph("tokensave_read", {"file": FILE, "mode": "lines", "lines": "2-4"})).returncode == 0


def test_a_read_that_names_no_mode_fails_because_the_default_is_the_whole_file(project):
    result = operate(project, codex_graph("tokensave_read", {"file": FILE}, text="body\n\n[... truncated at 15000 chars]"))
    assert result.returncode == 1
    assert "with mode full asks for the whole file" in result.stdout
    assert "truncated by the server" in result.stdout


def test_slices_that_together_cover_the_file_fail(project):
    result = operate(project, codex_graph("tokensave_read", {"file": FILE, "mode": "lines", "lines": "1-5"}),
                     codex_graph("tokensave_read", {"file": FILE, "mode": "lines", "start": 6}))
    assert result.returncode == 1
    assert "cover the whole file" in result.stdout


def test_a_map_reads_no_source_and_passes(project):
    assert operate(project, codex_graph("tokensave_read", {"file": FILE, "mode": "map"})).returncode == 0


@pytest.mark.parametrize("command", ["rg -n name {root}/src", "cat {root}/src/big.py", "cd {root} && sed -n 1,9p src/big.py"])
def test_a_shell_read_of_the_project_fails_even_after_a_graph_call(project, command):
    result = operate(project, codex_graph("tokensave_search", {"query": "name"}), codex_shell(command.format(root=project)))
    assert result.returncode == 1
    assert "the shell read the project" in result.stdout


def test_a_shell_command_that_reads_no_code_passes(project):
    result = operate(project, codex_graph("tokensave_search", {"query": "name"}), codex_shell(f"test -d {project}/.tokensave"))
    assert result.returncode == 0, result.stdout


def test_a_refused_shell_read_read_nothing(project):
    refused = cursor("shellToolCall", {"command": f"rg name {project}"}, {"rejected": {"reason": ""}})
    assert operate(project, cursor_graph("tokensave_search", {"query": "name"}), refused).returncode == 0


def test_a_read_that_the_sandbox_refused_read_nothing_although_the_pipe_exits_0(project):
    blocked = {"stdout": "0\n", "stderr": f"cat: {project}/{FILE}: Operation not permitted\n", "exitCode": 0}
    refused = cursor("shellToolCall", {"command": f"cat {project}/{FILE} | wc -c"}, {"success": blocked})
    assert operate(project, cursor_graph("tokensave_search", {"query": "name"}), refused).returncode == 0


def test_the_native_read_of_cursor_fails_inside_the_project_only(project):
    inside = cursor("readToolCall", {"path": str(project / FILE)}, {"success": {"fileSize": 50}})
    outside = cursor("readToolCall", {"path": "/elsewhere/SKILL.md"}, {"success": {"fileSize": 50}})
    sibling = cursor("readToolCall", {"path": f"{project}2/src/big.py"}, {"success": {"fileSize": 50}})
    graph = cursor_graph("tokensave_search", {"query": "name"})
    assert operate(project, graph, inside).returncode == 1
    assert operate(project, graph, outside).returncode == 0
    assert operate(project, graph, sibling).returncode == 0


def test_an_unknown_tool_that_reaches_the_project_fails(project):
    other = cursor("grepToolCall", {"path": str(project), "pattern": "name"}, {"success": {}})
    assert operate(project, cursor_graph("tokensave_search", {"query": "name"}), other).returncode == 1


@pytest.mark.parametrize("records", [
    [],
    [codex_graph("tokensave_status", {})],
    [codex_graph("tokensave_search", {"query": "name"}, status="failed")],
    [cursor("getMcpToolsToolCall", {"server": "tokensave", "toolName": "tokensave_read"}, {"success": {}})],
], ids=["no calls", "status only", "failed call", "schema fetch only"])
def test_a_log_with_no_answer_from_a_code_tool_fails(project, records):
    result = operate(project, *records)
    assert result.returncode == 1
    assert "no tokensave tool that reads code answered" in result.stdout


def test_a_log_that_is_not_json_stops_with_its_line_number(project):
    log = project / "agent.jsonl"
    log.write_text("plain text\n")
    result = subprocess.run([sys.executable, str(SCRIPT), str(log), "--root", str(project)], capture_output=True, text=True)
    assert result.returncode == 2
    assert "agent.jsonl:1: not JSON" in result.stderr


def test_claude_with_a_slice_passes_and_a_schema_load_is_not_a_call(project):
    records = claude("ToolSearch", {"query": "select:mcp__tokensave__tokensave_read"}, use_id="load")
    records += claude("mcp__tokensave__tokensave_read", {"file": FILE, "mode": "lines", "lines": "2-4"})
    result = operate(project, *records)
    assert result.returncode == 0, result.stdout
    assert f"{FILE}: 3 of 10 lines" in result.stdout
    assert "ToolSearch" not in result.stdout


def test_a_claude_schema_load_alone_fails(project):
    result = operate(project, *claude("ToolSearch", {"query": "select:mcp__tokensave__tokensave_read"}))
    assert "no tokensave tool that reads code answered" in result.stdout


def test_claude_with_no_mode_fails(project):
    result = operate(project, *claude("mcp__tokensave__tokensave_read", {"file": FILE}))
    assert "with mode full asks for the whole file" in result.stdout


@pytest.mark.parametrize("name, arguments", [
    ("Bash", {"command": "grep -n name {root}/src/big.py"}),
    ("Read", {"file_path": "{root}/src/big.py"}),
    ("Grep", {"pattern": "name", "path": "{root}/src"}),
], ids=["shell", "native read", "native search"])
def test_claude_reading_the_project_outside_tokensave_fails(project, name, arguments):
    filled = {key: value.format(root=project) for key, value in arguments.items()}
    graph = claude("mcp__tokensave__tokensave_search", {"query": "name"}, use_id="graph")
    assert operate(project, *graph, *claude(name, filled)).returncode == 1


def test_a_claude_call_that_a_hook_refused_read_nothing(project):
    graph = claude("mcp__tokensave__tokensave_search", {"query": "name"}, use_id="graph")
    denied = claude("Bash", {"command": f"rg name {project}"}, text="STOP: use tokensave_search", is_error=True)
    assert operate(project, *graph, *denied).returncode == 0


def test_a_claude_report_that_only_mentions_the_project_is_not_a_read(project):
    graph = claude("mcp__tokensave__tokensave_search", {"query": "name"}, use_id="graph")
    report = claude("Write", {"file_path": "/elsewhere/verdicts.md", "content": f"Found in {project}/src/big.py"})
    assert operate(project, *graph, *report).returncode == 0


def test_a_claude_write_inside_the_project_still_fails(project):
    graph = claude("mcp__tokensave__tokensave_search", {"query": "name"}, use_id="graph")
    write = claude("Write", {"file_path": f"{project}/src/big.py", "content": "changed"})
    assert operate(project, *graph, *write).returncode == 1
