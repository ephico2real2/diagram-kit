# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Local zones emitted by the documented date command must parse."""
import subprocess
from test_handover import project, run


def test_numeric_local_zone_from_date_is_valid(project):
    zone = subprocess.run(["/bin/date", "+%Z"], env={"TZ": "Etc/GMT+3", "PATH": "/usr/bin:/bin"},
                          capture_output=True, text=True, check=True).stdout.strip()
    assert zone == "-03"
    note = project / "claude-resumes" / "HANDOVER-demo.md"
    note.write_text(note.read_text().replace("16:12 CST", "16:12 " + zone))
    result = run(project, "check")
    assert (result.returncode, result.stdout) == (0, "")
