# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Read a YAML file in the tests with the first reader that this machine has.

The order: PyYAML in this interpreter, then another Python that has PyYAML, then yq (mikefarah, v4). CI installs PyYAML
with `pip install ".[test]"`. A local venv that was made before PyYAML joined the test extra still runs the tests.
If no reader exists, the tests fail with the install command: a skip would hide them.

DK_YAML_READER=module|python|yq forces one reader, so that a test can compare them.
"""
from __future__ import annotations

import functools
import json
import os
import pathlib
import shutil
import subprocess
import sys

INSTALL = 'no YAML reader: run `python -m pip install ".[test]"` in the kit, or install yq (brew install yq)'
_TO_JSON = "import json, sys, yaml; json.dump(yaml.safe_load(open(sys.argv[1], encoding='utf-8')), sys.stdout)"


def _candidates(name: str, extra: tuple[str, ...]) -> list[str]:
    """Each existing executable of this name: PATH first, then the usual install folders, without duplicates."""
    found = []
    for path in (shutil.which(name), *extra):
        if path and os.access(path, os.X_OK) and os.path.realpath(path) not in map(os.path.realpath, found):
            found.append(path)
    return found


def _pythons() -> list[str]:
    home = pathlib.Path.home()
    extra = ("/opt/homebrew/bin/python3", "/usr/local/bin/python3", "/usr/bin/python3",
             str(home / ".local/share/diagram-kit/.venv/bin/python"))
    return [p for p in _candidates("python3", extra) if os.path.realpath(p) != os.path.realpath(sys.executable)]


def _yqs() -> list[str]:
    extra = ("/opt/homebrew/bin/yq", "/usr/local/bin/yq", "/usr/bin/yq", str(pathlib.Path.home() / ".local/bin/yq"))
    return [p for p in _candidates("yq", extra)
            if "mikefarah" in subprocess.run([p, "--version"], capture_output=True, text=True).stdout]


@functools.cache
def reader() -> tuple[str, str | None]:
    """The reader to use: (kind, executable). The kind is module, python or yq."""
    forced = os.environ.get("DK_YAML_READER")
    if forced in (None, "module"):
        try:
            import yaml  # noqa: F401
            return "module", None
        except ImportError:
            if forced:
                raise RuntimeError(INSTALL) from None
    if forced in (None, "python"):
        for python in _pythons():
            if subprocess.run([python, "-c", "import yaml"], capture_output=True).returncode == 0:
                return "python", python
    if forced in (None, "yq"):
        for yq in _yqs():
            return "yq", yq
    raise RuntimeError(INSTALL + (f" (DK_YAML_READER={forced} found none)" if forced else ""))


def safe_load(path: pathlib.Path):
    """The data of one YAML file, as yaml.safe_load gives it."""
    kind, exe = reader()
    if kind == "module":
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    command = [exe, "-c", _TO_JSON, str(path)] if kind == "python" else [exe, "-o=json", ".", str(path)]
    run = subprocess.run(command, capture_output=True, text=True, check=True)
    return json.loads(run.stdout)
