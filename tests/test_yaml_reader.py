# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Homebrew's yq and PyYAML give the same data, and a missing reader prints the install command."""
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = sorted((ROOT / "skill" / "agile" / "templates" / "ISSUE_TEMPLATE").glob("*.yml"))

PROBE = """
import json, pathlib, sys
sys.path.insert(0, sys.argv[1])
import yaml_reader
kind, _ = yaml_reader.reader()
print(json.dumps({"kind": kind, "data": [yaml_reader.safe_load(pathlib.Path(p)) for p in sys.argv[2:]]}))
"""


def read_with(kind):
    """Run the reader in a fresh interpreter with DK_YAML_READER=kind, so that the cache of this process does not apply."""
    env = {**os.environ, "DK_YAML_READER": kind, "PYTHONDONTWRITEBYTECODE": "1"}
    run = subprocess.run([sys.executable, "-c", PROBE, str(ROOT / "tests"), *map(str, FORMS)],
                         capture_output=True, text=True, env=env)
    if run.returncode != 0 and "no YAML reader" in run.stderr:
        pytest.skip(f"this machine has no {kind} reader")
    assert run.returncode == 0, run.stderr
    result = json.loads(run.stdout)
    assert result["kind"] == kind
    return result["data"]


def test_there_are_forms_to_read():
    assert len(FORMS) >= 8


def test_each_form_has_a_name_with_either_reader():
    for kind in ("yq", "module"):
        try:
            data = read_with(kind)
        except pytest.skip.Exception:
            continue
        # config.yml is the issue-chooser settings of GitHub, with no name. The numbered files are the forms.
        forms = [d for f, d in zip(FORMS, data) if f.name[0].isdigit()]
        assert len(forms) == 8 and all(isinstance(d, dict) and d.get("name") for d in forms), kind


def test_yq_and_pyyaml_give_the_same_data():
    assert read_with("yq") == read_with("module")


def test_a_missing_reader_prints_the_brew_command():
    probe = ("import sys; sys.path.insert(0, sys.argv[1]); import yaml_reader; "
             "yaml_reader.brew_yq = lambda: None; yaml_reader.reader()")
    env = {**os.environ, "DK_YAML_READER": "yq", "PYTHONDONTWRITEBYTECODE": "1"}
    run = subprocess.run([sys.executable, "-c", probe, str(ROOT / "tests")], capture_output=True, text=True, env=env)
    assert run.returncode != 0
    assert "brew install yq" in run.stderr and "Then run the tests again" in run.stderr
