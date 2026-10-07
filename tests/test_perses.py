# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""perses-dashboard: what it adds to percli's result, and what it refuses.

The fixtures are a Grafana dashboard with one panel of each kind (`kinds.grafana.json`) and what percli 0.54.0
answered for it (`kinds.percli.json`, from the image docker.io/persesdev/perses:v0.54.0, 2026-10-07); the
`placeholder.*` pair adds a heatmap, which that percli does not convert. No test runs percli or a container:
`finish` is given the saved result, and `main` a stand-in percli that prints it.
"""

from __future__ import annotations

import copy
import json
import pathlib
import stat

import pytest

from diagram_kit import perses

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "dashboard"
BLUE, RED, YELLOW, PURPLE = "#4e79a7", "#e15759", "#edc948", "#b07aa1"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture
def grafana() -> dict:
    return load("kinds.grafana.json")


@pytest.fixture
def migrated() -> dict:
    return load("kinds.percli.json")


def panel(spec: dict, title: str) -> dict:
    return next(p["spec"] for p in spec["panels"].values() if p["spec"]["display"]["name"] == title)


def source(grafana: dict, title: str) -> dict:
    return next(p for p in grafana["panels"] if p.get("title") == title)


def test_every_query_names_the_datasource_and_the_picker_is_gone(grafana, migrated):
    spec = perses.finish(grafana, migrated, "app-thanos")
    queries = [q for p in spec["panels"].values() for q in p["spec"].get("queries", [])]
    assert len(queries) == 8          # 1 stat, 2 lines, 2 slices, 2 table columns, 1 state
    assert all(q["spec"]["plugin"]["spec"]["datasource"] == {"kind": "PrometheusDatasource", "name": "app-thanos"}
               for q in queries)
    assert spec["variables"] == []


def test_a_text_panel_is_a_markdown_panel_and_not_a_placeholder(grafana, migrated):
    spec = perses.finish(grafana, migrated, "app-thanos")
    assert panel(spec, "How to read this page")["plugin"] == {
        "kind": "Markdown", "spec": {"text": "Each pod has **one colour** on every panel."}}


def test_a_kind_perses_does_not_convert_is_refused_by_name():
    with pytest.raises(perses.ConversionError, match=r"Latency, as a heatmap.*placeholders.*heatmap"):
        perses.finish(load("placeholder.grafana.json"), load("placeholder.percli.json"), "app-thanos")


def test_the_pie_takes_its_colours_in_the_order_of_its_queries(grafana, migrated):
    spec = perses.finish(grafana, migrated, "app-thanos")
    pie = panel(spec, "Share of requests now, by pod")["plugin"]["spec"]
    assert pie["colorPalette"] == [BLUE, RED]
    # percli wrote showLabels: true for the source's empty displayLabels.
    assert panel(migrated["spec"], "Share of requests now, by pod")["plugin"]["spec"]["showLabels"] is False
    assert pie["showLabels"] is False


def test_a_pie_with_a_colour_for_some_queries_only_is_refused(grafana, migrated):
    source(grafana, "Share of requests now, by pod")["fieldConfig"]["overrides"].pop()
    with pytest.raises(perses.ConversionError, match=r"fixes a colour for some queries and not for \['B'\]"):
        perses.finish(grafana, migrated, "app-thanos")


def test_a_pie_with_no_fixed_colour_keeps_what_percli_wrote(grafana, migrated):
    source(grafana, "Share of requests now, by pod")["fieldConfig"]["overrides"] = []
    spec = perses.finish(grafana, migrated, "app-thanos")
    assert "colorPalette" not in panel(spec, "Share of requests now, by pod")["plugin"]["spec"]


def test_the_table_shows_what_a_row_is_about_first_and_colours_its_cells(grafana, migrated):
    before = [c["name"] for c in panel(migrated["spec"], "Each pod, now")["plugin"]["spec"]["columnSettings"]]
    assert before == ["value #1", "value #2", "pod", "timestamp"]          # percli: the renamed column after the others
    columns = panel(perses.finish(grafana, migrated, "app-thanos"), "Each pod, now")["plugin"]["spec"]["columnSettings"]
    assert [c["name"] for c in columns] == ["timestamp", "pod", "value #1", "value #2"]
    assert columns[0] == {"name": "timestamp", "hide": True}
    cells = columns[1]["cellSettings"]
    assert [(c["condition"]["kind"], c["backgroundColor"]) for c in cells] == [
        ("Value", BLUE), ("Value", YELLOW), ("Regex", PURPLE)]
    assert cells[2]["condition"]["spec"]["expr"] == "^app-([2-9]|[1-9][0-9]+)$"
    assert all(c["textColor"] == "#000000" for c in cells)                  # black is further from all three


def test_an_order_set_in_the_source_is_left_alone(grafana, migrated):
    organize = source(grafana, "Each pod, now")["transformations"][1]["options"]
    organize["indexByName"] = {"Value #A": 0, "Value #B": 1, "pod": 2}
    columns = panel(perses.finish(grafana, migrated, "app-thanos"), "Each pod, now")["plugin"]["spec"]["columnSettings"]
    assert [c["name"] for c in columns] == ["value #1", "value #2", "pod", "timestamp"]


def test_a_mapping_on_a_column_that_does_not_exist_is_refused(grafana, migrated):
    source(grafana, "Each pod, now")["fieldConfig"]["overrides"][0]["matcher"]["options"] = "the node"
    with pytest.raises(perses.ConversionError, match=r"maps values of 'the node', which no column is called"):
        perses.finish(grafana, migrated, "app-thanos")


def test_a_colour_perses_cannot_take_is_refused(grafana, migrated):
    mapping = source(grafana, "Each pod, now")["fieldConfig"]["overrides"][0]["properties"][1]["value"][1]
    mapping["options"]["result"]["color"] = "purple"
    with pytest.raises(perses.ConversionError, match=r"'purple' is not a hex colour"):
        perses.finish(grafana, migrated, "app-thanos")


def test_an_open_ended_range_loses_its_null_bound(grafana, migrated):
    raw = panel(migrated["spec"], "Items not ready, per pod")["plugin"]["spec"]["mappings"][1]["spec"]
    assert raw["to"] is None
    spec = perses.finish(grafana, migrated, "app-thanos")
    mapping = panel(spec, "Items not ready, per pod")["plugin"]["spec"]["mappings"][1]["spec"]
    assert mapping == {"from": 1, "result": {"color": RED, "value": "not ready"}}


def test_what_percli_carries_over_itself_is_untouched(grafana, migrated):
    untouched = copy.deepcopy(panel(migrated["spec"], "Requests per second, per pod")["plugin"])
    chart = panel(perses.finish(grafana, migrated, "app-thanos"), "Requests per second, per pod")["plugin"]
    assert chart == untouched
    assert chart["spec"]["visual"]["stack"] == "all" and chart["spec"]["yAxis"]["min"] == 0
    assert chart["spec"]["querySettings"] == [
        {"areaOpacity": 0.3, "colorMode": "fixed", "colorValue": BLUE, "queryIndex": 0},
        {"areaOpacity": 0.3, "colorMode": "fixed", "colorValue": RED, "lineStyle": "dashed", "queryIndex": 1}]


def test_a_query_that_differs_from_the_source_is_refused(grafana, migrated):
    source(grafana, "Pods up")["targets"][0]["expr"] = 'sum(up{job="other"})'
    with pytest.raises(perses.ConversionError, match=r"the queries of 'Pods up' differ"):
        perses.finish(grafana, migrated, "app-thanos")


def test_two_panels_with_one_title_are_refused(grafana, migrated):
    source(grafana, "Pods up")["title"] = "Each pod, now"
    with pytest.raises(perses.ConversionError, match=r"share a title.*Each pod, now"):
        perses.finish(grafana, migrated, "app-thanos")


def test_a_section_that_differs_from_the_rows_is_refused(grafana, migrated):
    next(p for p in grafana["panels"] if p["type"] == "row")["title"] = "Is it down?"
    with pytest.raises(perses.ConversionError, match=r"the sections .* differ from the Grafana rows"):
        perses.finish(grafana, migrated, "app-thanos")


def test_the_panels_of_a_collapsed_row_are_found():
    dashboard = {"panels": [{"type": "row", "title": "Folded", "panels": [{"type": "stat", "title": "Inside"}]},
                            {"type": "stat", "title": "Outside"}]}
    assert [p["title"] for p in perses.grafana_panels(dashboard)] == ["Inside", "Outside"]


@pytest.mark.parametrize(("one", "other", "ratio"), [("#000000", "#ffffff", 21.0), ("#4e79a7", "#ffffff", 4.549),
                                                     ("#edc948", "#292929", 9.040), ("#fff", "#000", 21.0)])
def test_the_contrast_ratio_is_wcags(one, other, ratio):
    assert perses.contrast(one, other) == pytest.approx(ratio, abs=0.001)


def stand_in_percli(directory: pathlib.Path, result: pathlib.Path) -> pathlib.Path:
    """A percli that answers every migrate with a saved result, so that main runs without a container."""
    script = directory / "percli"
    script.write_text(f"#!/bin/sh\ncat {result}\n")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script


def test_the_command_writes_the_spec_and_says_how_many_panels(tmp_path, capsys):
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    out = tmp_path / "chart" / "dashboard.perses.json"
    status = perses.main([str(FIXTURES / "kinds.grafana.json"), str(out), "--datasource", "app-thanos",
                          "--percli", str(stand_in_percli(tmp_path, FIXTURES / "kinds.percli.json")),
                          "--plugins", str(plugins)])
    assert status == 0
    assert capsys.readouterr().out == f"wrote {out} (6 panels)\n"
    written = json.loads(out.read_text())
    assert set(written) == set(load("kinds.percli.json")["spec"])                 # the spec, with no kind or metadata
    assert "panels" in written and "kind" not in written
    assert sorted(p.name for p in out.parent.iterdir()) == ["dashboard.perses.json"]


def test_whole_keeps_the_kind_and_metadata(tmp_path):
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    out = tmp_path / "dashboard.json"
    perses.main([str(FIXTURES / "kinds.grafana.json"), str(out), "--datasource", "app-thanos", "--whole",
                 "--percli", str(stand_in_percli(tmp_path, FIXTURES / "kinds.percli.json")), "--plugins", str(plugins)])
    written = json.loads(out.read_text())
    assert written["kind"] == "Dashboard" and written["metadata"]["name"] == "kit-kinds"


def test_a_refused_dashboard_writes_nothing_and_leaves_the_old_file(tmp_path, capsys):
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    out = tmp_path / "dashboard.json"
    out.write_text("the last good one\n")
    status = perses.main([str(FIXTURES / "placeholder.grafana.json"), str(out), "--datasource", "app-thanos",
                          "--percli", str(stand_in_percli(tmp_path, FIXTURES / "placeholder.percli.json")),
                          "--plugins", str(plugins)])
    assert status == 1
    assert "became placeholders" in capsys.readouterr().err
    assert out.read_text() == "the last good one\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["dashboard.json", "percli", "plugins"]


def test_percli_without_unpacked_plugins_is_refused(tmp_path, capsys):
    packed = tmp_path / "plugins"
    packed.mkdir()
    (packed / "Table-0.13.0.tar.gz").write_bytes(b"")
    status = perses.main([str(FIXTURES / "kinds.grafana.json"), str(tmp_path / "out.json"), "--datasource", "x",
                          "--percli", str(stand_in_percli(tmp_path, FIXTURES / "kinds.percli.json")),
                          "--plugins", str(packed)])
    assert status == 1
    assert "a directory of unpacked Perses plugins" in capsys.readouterr().err
