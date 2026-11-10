# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""skill/screenshot/verify.py gates a capture on its border. Without PIL that check cannot run, so the file is not ok."""

from __future__ import annotations

import importlib.util
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERIFY = ROOT / "skill" / "screenshot" / "verify.py"
PNG = ROOT / "examples" / "fan-out" / "envoy-fan-out.light.png"


@pytest.mark.skipif(importlib.util.find_spec("PIL") is not None, reason="this test needs a Python without PIL")
def test_a_capture_whose_border_check_did_not_run_is_not_ok():
    # PIL_BOOTSTRAPPED stops the re-exec into a skill venv that may exist on this machine.
    result = subprocess.run([sys.executable, str(VERIFY), str(PNG)], capture_output=True, text=True,
                            env={**os.environ, "PIL_BOOTSTRAPPED": "1"})
    assert result.returncode == 1, result.stdout
    assert "0 ok, 1 need attention" in result.stdout
    assert "border check NOT RUN" in result.stdout
