# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Literal password assignments do not require a digit."""
import pytest
from test_handover import project, run, write_note


@pytest.mark.parametrize("quotes", ["", "'", '"'])
def test_alphabetic_password_assignment_is_rejected_without_echoing_value(project, quotes):
    value = "a" * 12  # Synthetic input only.
    write_note(project, extra="\n- password=" + quotes + value + quotes)
    result = run(project, "check")
    assert result.returncode == 1
    assert "looks like a credential value" in result.stdout
    assert value not in result.stdout + result.stderr


@pytest.mark.parametrize("reference", [
    "password=$PASSWORD", "password=store/path", "password: store/path",
    "password=$PASSWORD2", "password=${PASSWORD2}", "token=$API_TOKEN2",
])
def test_password_locations_and_environment_references_stay_allowed(project, reference):
    write_note(project, extra="\n- " + reference)
    assert run(project, "check").returncode == 0


def test_long_password_store_path_stays_allowed(project):
    write_note(project, extra="\n- password=" + "a" * 20000 + "/item")
    assert run(project, "check").returncode == 0
