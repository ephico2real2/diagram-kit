# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Installation pins follow the package version; historical feature dates and other tools do not."""
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]
PIN = re.compile(r'(?:diagram-kit(?:/\.github/workflows/[\w.-]+\.ya?ml)?@|\bkit:\s*|\bKIT_REF=)v(\d+\.\d+\.\d+)')


def check_pins(root):
    version = re.search(r'^version = "([^"]+)"', (root / "pyproject.toml").read_text(), re.M).group(1)
    files = [root / "README.md", root / "Containerfile", *sorted((root / ".github/workflows").glob("*.y*ml")),
             *sorted(p for p in (root / "skill").rglob("*") if p.is_file() and p.suffix in {".md", ".yml", ".yaml", ".sh"})]
    found = {}
    for path in files:
        pins = PIN.findall(path.read_text())
        if pins:
            found[str(path.relative_to(root))] = pins
            assert set(pins) == {version}, f"{path.relative_to(root)}: {pins}, package version {version}"
    assert {"README.md", "Containerfile", ".github/workflows/check-diagrams.yml", "skill/visual/SKILL.md"} <= found.keys()


def test_latest_kit_pins_match_the_package_version():
    check_pins(ROOT)


@pytest.mark.parametrize("target", ["README.md", "Containerfile", ".github/workflows/check-diagrams.yml", "skill/visual/SKILL.md",
                                    "skill/example/new-guide.md"])
def test_the_pin_check_rejects_a_stale_pin_in_each_published_location(tmp_path, target):
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "9.8.7"\n')
    contents = {
        "README.md": "since 0.2.5; diagram-kit@v9.8.7\n",
        "Containerfile": "KIT_REF=v9.8.7\n",
        ".github/workflows/check-diagrams.yml": "kit: v9.8.7\n",
        "skill/visual/SKILL.md": "diagram-kit@v9.8.7\n",
        "skill/example/new-guide.md": "diagram-kit@v9.8.7; act v0.2.97\n",
    }
    for name, text in contents.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    check_pins(tmp_path)
    path = tmp_path / target
    path.write_text(path.read_text().replace("v9.8.7", "v9.8.6"))
    with pytest.raises(AssertionError, match=re.escape(target)):
        check_pins(tmp_path)
