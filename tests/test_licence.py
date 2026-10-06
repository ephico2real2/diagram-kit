# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Every file says which licence it is under: MPL-2.0 for the kit, MIT-0 for the template and the examples, whose
copies become other people's diagram pages (NOTICE)."""

from __future__ import annotations

import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MPL_FILES = sorted([*ROOT.glob("diagram_kit/*.py"), *ROOT.glob("tests/*.py")])
MIT0_FILES = sorted([ROOT / "diagram_kit" / "template.html", *ROOT.glob("examples/*/source.html")])


@pytest.mark.parametrize("path", MPL_FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_kit_files_carry_the_mpl_notice(path):
    head = path.read_text().splitlines()[:4]
    assert "# SPDX-License-Identifier: MPL-2.0" in head
    assert any("https://mozilla.org/MPL/2.0/" in line for line in head)


@pytest.mark.parametrize("path", MIT0_FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_template_and_examples_carry_the_mit0_notice(path):
    assert path.read_text().startswith("<!-- SPDX-License-Identifier: MIT-0.")


def test_the_licence_texts_are_present():
    assert (ROOT / "LICENSE").read_text().startswith("Mozilla Public License Version 2.0")
    assert (ROOT / "LICENSES" / "MIT-0.txt").read_text().startswith("MIT No Attribution")
