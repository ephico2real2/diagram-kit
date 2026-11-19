# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Python source must compile without syntax warnings on the interpreter running CI."""
from pathlib import Path
import warnings


def test_python_sources_compile_without_syntax_warnings():
    root = Path(__file__).resolve().parents[1]
    paths = sorted(p for folder in ("tests", "diagram_kit") for p in (root / folder).rglob("*.py"))
    assert paths
    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        for path in paths:
            compile(path.read_bytes(), str(path), "exec")
