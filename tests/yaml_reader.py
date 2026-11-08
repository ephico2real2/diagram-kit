# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Read a YAML file in the tests with Homebrew's yq first, then with PyYAML.

On a Mac the tools come from Homebrew, and Homebrew has yq (mikefarah, v4) but no PyYAML formula. CI on Linux has no
Homebrew, and installs PyYAML with `pip install ".[test]"`. If neither reader exists, the tests fail and print the
install command, so that you install it and run the tests again. A skip would hide the tests.

DK_YAML_READER=yq|module forces one reader, so that a test can compare them.
"""
from __future__ import annotations

import functools
import json
import os
import pathlib
import shutil
import subprocess

INSTALL = 'no YAML reader. On a Mac: brew install yq. Elsewhere: python -m pip install ".[test]". Then run the tests again'
STANDARD_PREFIXES = ("/opt/homebrew", "/usr/local", "/home/linuxbrew/.linuxbrew")


def brew_prefixes() -> list[str]:
    """The Homebrew prefixes to search: the one that `brew --prefix` names, then the standard ones."""
    prefixes = []
    brew = shutil.which("brew") or next((f"{p}/bin/brew" for p in STANDARD_PREFIXES if os.access(f"{p}/bin/brew", os.X_OK)), None)
    if brew:
        run = subprocess.run([brew, "--prefix"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if run.returncode == 0 and run.stdout.strip():
            prefixes.append(run.stdout.strip())
    return prefixes + [p for p in STANDARD_PREFIXES if p not in prefixes]


def brew_yq() -> str | None:
    """Homebrew's yq, if it is installed and is mikefarah yq."""
    for prefix in brew_prefixes():
        yq = f"{prefix}/bin/yq"
        if os.access(yq, os.X_OK):
            version = subprocess.run([yq, "--version"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
            if "mikefarah" in version.stdout:
                return yq
    return None


@functools.cache
def reader() -> tuple[str, str | None]:
    """The reader to use: ("yq", path) or ("module", None)."""
    forced = os.environ.get("DK_YAML_READER")
    if forced in (None, "yq"):
        yq = brew_yq()
        if yq:
            return "yq", yq
    if forced in (None, "module"):
        try:
            import yaml  # noqa: F401
            return "module", None
        except ImportError:
            pass
    raise RuntimeError(INSTALL + (f" (DK_YAML_READER={forced} found none)" if forced else ""))


def safe_load(path: pathlib.Path):
    """The data of one YAML file, as yaml.safe_load gives it."""
    kind, yq = reader()
    if kind == "module":
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    run = subprocess.run([yq, "-o=json", ".", str(path)], capture_output=True, text=True, check=True,
                         stdin=subprocess.DEVNULL)
    return json.loads(run.stdout)
