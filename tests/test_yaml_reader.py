# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Each YAML reader of yaml_reader.py gives the data that PyYAML gives, and a missing reader fails with the fix."""
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = sorted((ROOT / "skill" / "agile" / "templates" / "ISSUE_TEMPLATE").glob("*.yml"))
yaml = pytest.importorskip("yaml", reason="the reference reader is PyYAML (the test extra installs it)")

PROBE = """
import json, pathlib, sys
sys.path.insert(0, sys.argv[1])
import yaml_reader
kind, exe = yaml_reader.reader()
print(json.dumps({"kind": kind, "data": [yaml_reader.safe_load(pathlib.Path(p)) for p in sys.argv[2:]]}))
"""


def read_with(kind):
    """Run the reader in a fresh interpreter with DK_YAML_READER=kind, so the cache of this process does not apply."""
    env = {**os.environ, "DK_YAML_READER": kind}
    return subprocess.run([sys.executable, "-c", PROBE, str(ROOT / "tests"), *map(str, FORMS)],
                          capture_output=True, text=True, env=env)


def test_there_are_forms_to_read():
    assert len(FORMS) >= 8


@pytest.mark.parametrize("kind", ["module", "python", "yq"])
def test_each_reader_gives_the_data_of_pyyaml(kind):
    run = read_with(kind)
    if run.returncode != 0 and "no YAML reader" in run.stderr:
        pytest.skip(f"this machine has no {kind} reader")
    assert run.returncode == 0, run.stderr
    import json
    result = json.loads(run.stdout)
    assert result["kind"] == kind
    assert result["data"] == [yaml.safe_load(f.read_text(encoding="utf-8")) for f in FORMS]


def test_a_forced_reader_that_is_missing_names_the_install_command(tmp_path):
    env = {**os.environ, "DK_YAML_READER": "yq", "PATH": str(tmp_path), "HOME": str(tmp_path)}
    probe = "import sys; sys.path.insert(0, sys.argv[1]); import yaml_reader, pathlib; yaml_reader._yqs = lambda: []; yaml_reader.reader()"
    run = subprocess.run([sys.executable, "-c", probe, str(ROOT / "tests")], capture_output=True, text=True, env=env)
    assert run.returncode != 0
    assert 'pip install ".[test]"' in run.stderr and "DK_YAML_READER=yq found none" in run.stderr
