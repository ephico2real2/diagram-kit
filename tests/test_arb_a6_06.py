# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Read the template summary against the actual form metadata."""
from pathlib import Path

import yaml

AGILE = Path(__file__).resolve().parents[1] / "skill/agile"


def test_the_template_summary_covers_actual_statuses_and_epic_type():
    forms = [yaml.safe_load(p.read_bytes()) for p in (AGILE / "templates/ISSUE_TEMPLATE").glob("[0-9]-*.yml")]
    summary = (AGILE / "SKILL.md").read_text().split("## 3. Templates", 1)[1].split("## 4.", 1)[0]
    statuses = {label for form in forms for label in form["labels"] if label.startswith("status:")}
    assert all(f"`{status}`" in summary for status in statuses)
    epic = next(form for form in forms if form["name"] == "Epic")
    assert "type" not in epic
    assert "The Epic form omits `type`" in summary
