#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Refuse an agent brief that breaks the brief standard of /agent-report.

A brief passes when:
  1. its first line names the role: IMPLEMENTER, REVIEWER, RESEARCHER or TESTER, alone or after "Role: ";
  2. it holds every line of brief-standard.md, in order, with the placeholders filled in;
  3. no placeholder (<folder>, <job>, <graph_root>) is left outside the instruction line of the standard;
  4. the part above the standard gives a stop point, forbids the browser and forbids env files;
  5. with --plants: the planted answers are in a file outside the job folder, with one CONFIRMED, one REFUTED and one
     NOT REACHED answer at least.

Exit 0 when the brief passes, 1 with one line per problem when it does not, 2 on a usage error.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_STANDARD = HERE.parent / "brief-standard.md"
ROLES = ("IMPLEMENTER", "REVIEWER", "RESEARCHER", "TESTER")
PLACEHOLDERS = ("<folder>", "<job>", "<graph_root>")
INSTRUCTION_PREFIX = "Paste this into the brief of every agent"
VERDICTS = ("CONFIRMED", "REFUTED", "NOT REACHED")


def line_pattern(line: str) -> re.Pattern[str]:
    """A standard line as a pattern: each placeholder matches the text that replaced it."""
    parts = re.split(r"(<folder>|<job>|<graph_root>)", line)
    return re.compile("".join(".+?" if p in PLACEHOLDERS else re.escape(p) for p in parts) + r"\Z")


def standard_lines(standard: str) -> list[str]:
    return [line.rstrip() for line in standard.splitlines() if line.strip()]


def check(brief: str, standard: str, plants: pathlib.Path | None = None,
          job_dir: pathlib.Path | None = None) -> list[str]:
    problems: list[str] = []
    lines = [line.rstrip() for line in brief.splitlines()]
    first = next((line.strip() for line in lines if line.strip()), "")
    role = re.sub(r"^Role:\s*", "", first).split(" ", 1)[0].rstrip(".,:")
    if role not in ROLES:
        problems.append(f"the first line is {first[:40]!r}, and it names no role of {', '.join(ROLES)}")

    wanted = standard_lines(standard)
    heading = wanted[0]
    if heading not in lines:
        problems.append(f"the brief standard is missing: no line {heading!r}")
        head = brief
    else:
        start = lines.index(heading)
        head = "\n".join(lines[:start])
        body = [line for line in lines[start:] if line.strip()]
        at = 0
        for want in wanted:
            pattern = line_pattern(want)
            while at < len(body) and not pattern.match(body[at]):
                at += 1
            if at == len(body):
                problems.append(f"the brief standard is not the current version: no line matches {want[:70]!r}")
                break
            at += 1

    for number, line in enumerate(lines, 1):
        if line.startswith(INSTRUCTION_PREFIX):
            continue
        for placeholder in PLACEHOLDERS:
            if placeholder in line:
                problems.append(f"line {number}: the placeholder {placeholder} is not filled in")

    if not re.search(r"\b(limit|stop after|stop at)\b", head, re.I):
        problems.append("the brief gives no stop point (a limit, or 'stop after')")
    if "browser" not in head.lower():
        problems.append("the brief does not state the browser rule")
    if ".env" not in head:
        problems.append("the brief does not forbid env files")

    if plants is not None:
        if not plants.is_file():
            problems.append(f"the planted answers file {plants} does not exist")
        else:
            text = plants.read_text()
            for verdict in VERDICTS:
                if verdict not in text:
                    problems.append(f"the planted answers have no {verdict} answer")
            if job_dir is not None and plants.resolve().is_relative_to(job_dir.resolve()):
                problems.append("the planted answers are inside the job folder, where the agent reads")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("brief", type=pathlib.Path)
    parser.add_argument("--standard", type=pathlib.Path, default=DEFAULT_STANDARD)
    parser.add_argument("--plants", type=pathlib.Path)
    parser.add_argument("--job-dir", type=pathlib.Path, help="the job folder; the default is the folder of the brief")
    args = parser.parse_args(argv)
    if not args.brief.is_file() or not args.standard.is_file():
        print(f"brief_check: no such file: {args.brief if not args.brief.is_file() else args.standard}", file=sys.stderr)
        return 2
    problems = check(args.brief.read_text(), args.standard.read_text(), args.plants,
                     args.job_dir or args.brief.resolve().parent)
    for problem in problems:
        print(f"{args.brief}: {problem}")
    if not problems:
        print(f"{args.brief}: brief ok")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
