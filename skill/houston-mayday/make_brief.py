#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Join a mission head and the kit brief standard into <folder>/<job>/brief.md.

usage: make_brief.py <folder> <job> <graph_root>

<folder>/heads/<job>.md is the head that Claude writes. The brief standard of /agent-report follows it, with <folder>,
<job> and <graph_root> filled in, except on its instruction line, which brief_check.py expects as it is.
"""
import pathlib
import sys

if len(sys.argv) != 4:
    sys.exit(__doc__.strip().splitlines()[2])
folder, job, roots = pathlib.Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
standard = pathlib.Path(__file__).resolve().parent.parent / "agent-report" / "brief-standard.md"
lines = []
for line in standard.read_text().splitlines():
    if not line.startswith("Paste this into the brief of every agent"):
        line = line.replace("<folder>", str(folder)).replace("<job>", job).replace("<graph_root>", roots)
    lines.append(line)
head = (folder / "heads" / f"{job}.md").read_text().rstrip()
(folder / job).mkdir(parents=True, exist_ok=True)
brief = folder / job / "brief.md"
brief.write_text(head + "\n\n" + "\n".join(lines) + "\n")
print(brief)
