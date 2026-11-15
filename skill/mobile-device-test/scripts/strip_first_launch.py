#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Copies a folder of Maestro flows and removes the first command of each named flow when that command is a
`launchApp` with `stopApp: false`.

Why: maestro-runner 1.1.29 restarts a running app at `launchApp` with `stopApp: false` on a real iPhone or iPad
(measured 2026-11-11; the fix is in 1.1.30). An app that locks at each start then shows its lock screen, and the
flow fails. The copy keeps every other line, so `runFlow` paths still resolve inside the copied folder.

A `launchApp` with `stopApp: false` later in a flow is kept, and reported, because removing it would change what
the flow tests. Standard library only.

Usage: strip_first_launch.py <flow folder> <output folder> <flow file>...
Prints one line for each named flow: removed, kept, or warn. Exit 2 if a named flow is not in the folder.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

LAUNCH = re.compile(r"^- launchApp\s*:?\s*(?P<inline>\{.*\})?\s*(#.*)?$")
STOP_FALSE = re.compile(r"\bstopApp\s*:\s*false\b")


def commands_start(lines: list[str]) -> int:
    """The index of the first line after the `---` that ends the flow's config, or 0 if the flow has none."""
    for n, line in enumerate(lines):
        if line.strip() == "---":
            return n + 1
    return 0


def block_end(lines: list[str], start: int) -> int:
    """The index after the last line of the command that starts at `start` (its indented lines)."""
    n = start + 1
    while n < len(lines) and (lines[n].startswith((" ", "\t")) or not lines[n].strip()):
        n += 1
    # Blank lines at the end belong to the gap before the next command, not to this block.
    while n > start + 1 and not lines[n - 1].strip():
        n -= 1
    return n


def launch_blocks(lines: list[str], first: int) -> list[tuple[int, int, bool]]:
    """Each top-level launchApp from `first` on: (start, end, has stopApp false)."""
    found = []
    for n in range(first, len(lines)):
        match = LAUNCH.match(lines[n])
        if match:
            end = block_end(lines, n)
            body = (match.group("inline") or "") + "\n".join(lines[n + 1:end])
            found.append((n, end, bool(STOP_FALSE.search(body))))
    return found


def strip(text: str) -> tuple[str, str]:
    """Returns the new text and one word: removed, kept, or warn:<line numbers>."""
    lines = text.splitlines(keepends=False)
    first = commands_start(lines)
    while first < len(lines) and (not lines[first].strip() or lines[first].lstrip().startswith("#")):
        first += 1
    blocks = launch_blocks(lines, first)
    result = "kept"
    if blocks and blocks[0][0] == first and blocks[0][2]:
        start, end, _ = blocks.pop(0)
        del lines[start:end]
        result = "removed"
        blocks = [(s - (end - start), e - (end - start), f) for s, e, f in blocks]
    later = [str(s + 1) for s, _, f in blocks if f]
    if later:
        result += f" warn:{','.join(later)}"
    tail = "\n" if text.endswith("\n") else ""
    return "\n".join(lines) + tail, result


def main(argv: list[str]) -> int:
    if len(argv) < 4:
        print(next(line for line in __doc__.splitlines() if line.startswith("Usage:")), file=sys.stderr)
        return 2
    source, output, names = Path(argv[1]), Path(argv[2]), argv[3:]
    missing = [name for name in names if not (source / name).is_file()]
    if missing:
        print(f"not in {source}: {' '.join(missing)}", file=sys.stderr)
        return 2
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(source, output, ignore=shutil.ignore_patterns("*.png", "__pycache__"))
    for name in names:
        path = output / name
        text, result = strip(path.read_text())
        path.write_text(text)
        print(f"{name}: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
