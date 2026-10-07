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
import os
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


def test_a_variable_that_asks_prometheus_names_the_datasource_too(grafana, migrated):
    # As percli 0.54.0 wrote a label_values variable on a real dashboard: no datasource.
    migrated["spec"]["variables"].append({"kind": "ListVariable", "spec": {"name": "node", "plugin": {
        "kind": "PrometheusLabelValuesVariable", "spec": {"labelName": "node", "matchers": ["app_up"]}}}})
    spec = perses.finish(grafana, migrated, "app-thanos")
    assert [v["spec"]["name"] for v in spec["variables"]] == ["node"]
    assert spec["variables"][0]["spec"]["plugin"]["spec"]["datasource"] == {
        "kind": "PrometheusDatasource", "name": "app-thanos"}


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
    with pytest.raises(perses.ConversionError, match=r"the table 'Each pod, now': 'purple' is not a hex colour"):
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


def test_two_panels_with_one_title_are_paired_by_their_place(grafana, migrated):
    # A number and the table under it may share a title: seen on a real dashboard, 2026-10-07.
    source(grafana, "Pods up")["title"] = "Each pod, now"
    panel(migrated["spec"], "Pods up")["display"]["name"] = "Each pod, now"
    spec = perses.finish(grafana, migrated, "app-thanos")
    kinds = [p["spec"]["plugin"]["kind"] for p in spec["panels"].values() if p["spec"]["display"]["name"] == "Each pod, now"]
    assert kinds == ["StatChart", "Table"]
    table = next(p["spec"]["plugin"]["spec"] for p in spec["panels"].values() if p["spec"]["plugin"]["kind"] == "Table")
    assert [c["name"] for c in table["columnSettings"]] == ["timestamp", "pod", "value #1", "value #2"]


def test_panels_out_of_the_sources_order_are_refused(grafana, migrated):
    drawn = [p for p in grafana["panels"] if p["type"] != "row"]
    first, second = grafana["panels"].index(drawn[2]), grafana["panels"].index(drawn[3])
    grafana["panels"][first], grafana["panels"][second] = grafana["panels"][second], grafana["panels"][first]
    with pytest.raises(perses.ConversionError, match=r"differ from the Grafana ones, in order: 'Share of requests now"):
        perses.finish(grafana, migrated, "app-thanos")


def test_a_tenth_panel_of_a_section_comes_after_the_ninth():
    assert sorted(["2_10", "2_9", "10_0", "2_0"], key=perses._place) == ["2_0", "2_9", "2_10", "10_0"]


def test_a_stat_whose_legend_names_two_labels_shows_the_second_and_is_named_by_the_first(grafana, migrated):
    # What percli 0.54.0 wrote for the legend "{{node}}: {{version}}" on a real dashboard, 2026-10-07: a label no
    # series has, so the stat showed the info metric's value, 1.
    source(grafana, "Pods up")["targets"][0]["legendFormat"] = "{{node}}: {{version}}"
    panel(migrated["spec"], "Pods up")["plugin"]["spec"]["metricLabel"] = "node}}: {{version"
    stat = panel(perses.finish(grafana, migrated, "app-thanos"), "Pods up")
    assert stat["plugin"]["spec"]["metricLabel"] == "version"
    assert [q["spec"]["plugin"]["spec"]["seriesNameFormat"] for q in stat["queries"]] == ["{{node}}"]


@pytest.mark.parametrize("legend", ["{{a}} {{b}} {{c}}", "node {{a}} runs {{b}}", "{{a}}: {{b}} now", ""])
def test_a_broken_label_from_any_other_legend_is_refused(grafana, migrated, legend):
    source(grafana, "Pods up")["targets"][0]["legendFormat"] = legend
    panel(migrated["spec"], "Pods up")["plugin"]["spec"]["metricLabel"] = "a}} {{b"
    with pytest.raises(perses.ConversionError, match=r"names several labels, and a Perses StatChart shows one"):
        perses.finish(grafana, migrated, "app-thanos")


def stat_showing_its_name(grafana: dict, migrated: dict, legends: list[str]) -> dict:
    """The stat as percli 0.54.0 writes it when it shows its series' name (textMode "name"), one query per legend:
    each legend is the query's name format, and the label is the FIRST legend with the braces trimmed off its ends
    (StatChart 0.13.0, schemas/migrate/migrate.cue: strings.Trim(legendFormat, "{}"); measured 2026-10-07)."""
    wanted, stat = source(grafana, "Pods up"), panel(migrated["spec"], "Pods up")
    wanted["options"]["textMode"] = "name"
    for extra in range(1, len(legends)):
        wanted["targets"].append(dict(wanted["targets"][0], refId="ABCD"[extra], expr=f'sum(up{{job="app{extra}"}})'))
        stat["queries"].append(copy.deepcopy(stat["queries"][0]))
        stat["queries"][extra]["spec"]["plugin"]["spec"]["query"] = f'sum(up{{job="app{extra}"}})'
    for target, query, legend in zip(wanted["targets"], stat["queries"], legends):
        target["legendFormat"] = legend
        query["spec"]["plugin"]["spec"]["seriesNameFormat"] = legend
    stat["plugin"]["spec"]["metricLabel"] = legends[0].strip("{}")
    return stat


def names(stat: dict) -> list[str]:
    return [q["spec"]["plugin"]["spec"]["seriesNameFormat"] for q in stat["queries"]]


@pytest.mark.parametrize(("legend", "label"), [("{{node}}", "node"), ("{{ node }}", "node"), (" {{node}} ", "node"),
                                               ("{{  k8s.version }}", "k8s.version")])
def test_a_stat_whose_legend_is_one_label_shows_that_label(grafana, migrated, legend, label):
    # From "{{ node }}" percli wrote the label " node ", spaces and all: no series has it, and the stat showed 1.
    # From " {{node}} " it wrote the legend itself, braces and all.
    assert stat_showing_its_name(grafana, migrated, [legend])["plugin"]["spec"]["metricLabel"] == legend.strip("{}")
    stat = panel(perses.finish(grafana, migrated, "app-thanos"), "Pods up")
    assert stat["plugin"]["spec"]["metricLabel"] == label
    assert names(stat) == [legend]                                         # one label: the name is left alone


@pytest.mark.parametrize("legends", [["Version"], ["__auto"], ["pods up"], ["{{node}}", "{{pod}}"],
                                     ["{{node}}", "{{pod}}: {{version}}"]])
def test_a_stat_whose_legend_is_not_one_label_for_every_query_is_refused(grafana, migrated, legends):
    # A fixed text and Grafana's "__auto" came over as the label itself; with two queries only the first was read.
    stat_showing_its_name(grafana, migrated, legends)
    refusal = r"is not one label, the same for every query, and a Perses StatChart shows one"
    with pytest.raises(perses.ConversionError, match=refusal):
        perses.finish(grafana, migrated, "app-thanos")


@pytest.mark.parametrize("legend", ["", None])
def test_a_stat_that_shows_its_name_and_has_no_legend_is_refused(grafana, migrated, legend):
    # Grafana 12.3.1 showed the series' own name, 'ob3_one{node="node-a", ...}'. From an empty legend percli wrote the
    # label "", from no legendFormat at all it wrote none, and Perses 0.54.0 showed the value, 42. Measured 2026-10-07.
    stat = stat_showing_its_name(grafana, migrated, [""])
    if legend is None:
        del source(grafana, "Pods up")["targets"][0]["legendFormat"], stat["plugin"]["spec"]["metricLabel"]
        del stat["queries"][0]["spec"]["plugin"]["spec"]["seriesNameFormat"]
    with pytest.raises(perses.ConversionError, match=r"is not one label, the same for every query, and a Perses"):
        perses.finish(grafana, migrated, "app-thanos")


def test_a_label_that_did_not_come_from_the_legend_is_left_alone(grafana, migrated):
    # textMode "auto" on a table query with reduceOptions.fields "/^version$/": percli wrote "version" from the
    # field, whatever the legend says.
    stat_showing_its_name(grafana, migrated, ["{{node}}"])["plugin"]["spec"]["metricLabel"] = "version"
    source(grafana, "Pods up")["options"]["textMode"] = "auto"
    stat = panel(perses.finish(grafana, migrated, "app-thanos"), "Pods up")
    assert stat["plugin"]["spec"]["metricLabel"] == "version" and names(stat) == ["{{node}}"]


def test_two_labels_are_read_as_one_label_is(grafana, migrated):
    # "{{k8s.version}}" alone was one label, and "{{node}}: {{k8s.version}}" was refused with the advice to write it
    # as it was written: "two as '{{who}}: {{what}}'".
    stat_showing_its_name(grafana, migrated, ["{{node}}: {{ k8s.version }}"])
    stat = panel(perses.finish(grafana, migrated, "app-thanos"), "Pods up")
    assert stat["plugin"]["spec"]["metricLabel"] == "k8s.version" and names(stat) == ["{{node}}"]


def test_every_query_of_a_stat_with_two_labels_is_named_by_the_first(grafana, migrated):
    stat_showing_its_name(grafana, migrated, ["{{node}}: {{version}}", "{{ node }} - {{ version }}"])
    stat = panel(perses.finish(grafana, migrated, "app-thanos"), "Pods up")
    assert stat["plugin"]["spec"]["metricLabel"] == "version" and names(stat) == ["{{node}}", "{{node}}"]


@pytest.mark.parametrize("second", ["{{node}}: {{mode}}", "{{pod}}: {{version}}", "{{node}}", ""])
def test_two_labels_on_one_query_and_another_legend_on_the_next_is_refused(grafana, migrated, second):
    stat_showing_its_name(grafana, migrated, ["{{node}}: {{version}}", second])
    with pytest.raises(perses.ConversionError, match=r"names several labels, and a Perses StatChart shows one"):
        perses.finish(grafana, migrated, "app-thanos")


def stat_on_a_table_query(grafana: dict, migrated: dict, fields: str) -> dict:
    """The stat as percli 0.54.0 writes it for a table query whose fields are named (textMode "auto"): the label is
    reduceOptions.fields with "/", "^" and "$" trimmed off its ends (StatChart 0.13.0, schemas/migrate/migrate.cue;
    each case here was run through the real percli on 2026-10-07)."""
    wanted, stat = source(grafana, "Pods up"), panel(migrated["spec"], "Pods up")
    wanted["options"]["textMode"] = "auto"
    wanted["options"]["reduceOptions"]["fields"] = fields
    wanted["targets"][0]["format"] = "table"
    stat["plugin"]["spec"]["metricLabel"] = fields.strip("/^$")
    return stat


@pytest.mark.parametrize(("fields", "label"), [("/^pod$/", "pod"), ("pod", "pod"), ("^pod$", "pod"),
                                               ("/^k8s.version$/", "k8s.version"), ("k8s.version", "k8s.version"),
                                               (r"/^k8s\.version$/", r"k8s\.version")])
def test_a_stat_on_a_table_query_shows_the_field_it_names(grafana, migrated, fields, label):
    # A bare name is one field (Grafana anchors it itself), and so is "/^name$/". The last is a dotted name as
    # Grafana 12.3.1's own Fields picker writes it, escaped: Perses 0.54.0 showed that label's value by it.
    stat_on_a_table_query(grafana, migrated, fields)
    assert panel(perses.finish(grafana, migrated, "app-thanos"), "Pods up")["plugin"]["spec"]["metricLabel"] == label


@pytest.mark.parametrize("fields", ["/.*/", "/^(pod|node)$/", "/^pod.*/", "/^[a-z]+$/",
                                    "/pod/", "/version/", "/^pod/", "/pod$/", "/^pod./", "/./", "//", r"/^pod\d$/"])
def test_a_stat_on_a_table_query_that_names_a_pattern_of_fields_is_refused(grafana, migrated, fields):
    # From "/.*/" percli wrote the label ".*"; Perses 0.54.0 showed the metric's name.
    # Between slashes Grafana searches every field's name for the pattern, and only "/^name$/" is one field. On a
    # series with the labels pod, pod_ip, kernel_version and kubelet_version (Grafana 12.3.1 and Perses 0.54.0,
    # 2026-10-07): "/pod/" and "/^pod/" showed pod and pod_ip in Grafana and pod alone in Perses; "/version/" showed
    # the two versions in Grafana and, as no label is called "version", the sample's value in Perses.
    stat_on_a_table_query(grafana, migrated, fields)
    with pytest.raises(perses.ConversionError, match=r"a pattern and not one field, and a Perses StatChart shows one"):
        perses.finish(grafana, migrated, "app-thanos")


@pytest.mark.parametrize("fields", ["", "Value", "/^Value$/", "Value #A", r"/^Value \#A$/", "/Value/"])
def test_a_stat_on_a_table_query_that_names_no_label_has_no_label(grafana, migrated, fields):
    # percli wrote the label "" for nothing chosen, and "Value" for the field that holds the sample.
    # "/^Value \#A$/" is "Value #A" as Grafana 12.3.1's own Fields picker writes it.
    assert "metricLabel" in stat_on_a_table_query(grafana, migrated, fields)["plugin"]["spec"]
    assert "metricLabel" not in panel(perses.finish(grafana, migrated, "app-thanos"), "Pods up")["plugin"]["spec"]


@pytest.mark.parametrize("fields", ["Value #A", "/^Value #A$/", "/^Value #B$/", r"/^Value \#A$/"])
def test_the_value_of_one_query_among_several_is_refused(grafana, migrated, fields):
    # "Value #A" is a field only when the panel has several queries, and Grafana 12.3.1 then showed that query alone
    # (42). With no label Perses 0.54.0 showed every query's value (42 and 7). Measured 2026-10-07.
    # The last is the one Grafana's own Fields picker writes: it was refused as "a pattern and not one field".
    stat = stat_on_a_table_query(grafana, migrated, fields)
    wanted = source(grafana, "Pods up")
    wanted["targets"].append(dict(wanted["targets"][0], refId="B", expr='sum(up{job="other"})'))
    stat["queries"].append(copy.deepcopy(stat["queries"][0]))
    stat["queries"][1]["spec"]["plugin"]["spec"]["query"] = 'sum(up{job="other"})'
    with pytest.raises(perses.ConversionError, match=r"the value of one query of its 2, and a Perses StatChart shows"):
        perses.finish(grafana, migrated, "app-thanos")


@pytest.mark.parametrize("fields", ["Time", "/^Time$/"])
def test_a_stat_on_a_table_query_that_shows_the_time_of_the_sample_is_refused(grafana, migrated, fields):
    # Grafana 12.3.1 showed "2026-10-07 15:02:30". No series has a label "Time": Perses 0.54.0 showed the value.
    stat_on_a_table_query(grafana, migrated, fields)
    with pytest.raises(perses.ConversionError, match=r"the time of the sample, which is no label"):
        perses.finish(grafana, migrated, "app-thanos")


def test_a_label_percli_did_not_take_from_the_fields_is_left_alone(grafana, migrated):
    # Not a table query: percli wrote no label from the fields, so one that reads like a pattern is not ours to judge.
    stat_on_a_table_query(grafana, migrated, "/.*/")
    source(grafana, "Pods up")["targets"][0]["format"] = "time_series"
    assert panel(perses.finish(grafana, migrated, "app-thanos"), "Pods up")["plugin"]["spec"]["metricLabel"] == ".*"


@pytest.mark.parametrize("text_mode", ["value", "name", "value_and_name", "none"])
def test_the_fields_of_a_stat_that_is_not_in_text_mode_auto_are_not_read(grafana, migrated, text_mode):
    # percli reads reduceOptions.fields in textMode "auto" alone (2 736 panels through percli 0.54.0, 2026-10-07).
    stat_on_a_table_query(grafana, migrated, "/.*/")
    source(grafana, "Pods up")["options"]["textMode"] = text_mode
    assert panel(perses.finish(grafana, migrated, "app-thanos"), "Pods up")["plugin"]["spec"]["metricLabel"] == ".*"


@pytest.mark.parametrize(("fields", "label"), [("/^pod$/", "Value"), ("pod", ".*")])
def test_a_label_that_is_not_the_one_the_fields_give_is_left_alone(grafana, migrated, fields, label):
    # Whatever wrote it, it was not percli reading these fields: it is not ours to drop or to refuse.
    stat_on_a_table_query(grafana, migrated, fields)["plugin"]["spec"]["metricLabel"] = label
    assert panel(perses.finish(grafana, migrated, "app-thanos"), "Pods up")["plugin"]["spec"]["metricLabel"] == label


def test_a_suffix_unit_perses_has_a_word_for_becomes_that_unit(grafana, migrated):
    source(grafana, "Pods up")["fieldConfig"]["defaults"]["unit"] = "suffix: days"
    assert panel(migrated["spec"], "Pods up")["plugin"]["spec"]["format"]["unit"] == "decimal"
    warnings: list[str] = []
    stat = panel(perses.finish(grafana, migrated, "app-thanos", warnings), "Pods up")
    assert stat["plugin"]["spec"]["format"]["unit"] == "days" and warnings == []


def test_a_unit_perses_has_no_word_for_is_a_warning_and_not_a_refusal(grafana, migrated):
    source(grafana, "Pods up")["fieldConfig"]["defaults"]["unit"] = "suffix: widgets"
    warnings: list[str] = []
    stat = panel(perses.finish(grafana, migrated, "app-thanos", warnings), "Pods up")
    assert stat["plugin"]["spec"]["format"]["unit"] == "decimal"
    assert warnings == ["'Pods up': the Grafana unit 'suffix: widgets' became a plain number in Perses"]


@pytest.mark.parametrize("word", ["milliseconds", "seconds", "minutes", "hours", "days", "weeks", "months", "years"])
def test_each_unit_of_time_perses_has_had_since_0_51_is_carried(grafana, migrated, word):
    source(grafana, "Pods up")["fieldConfig"]["defaults"]["unit"] = f"suffix:{word}"
    warnings: list[str] = []
    stat = panel(perses.finish(grafana, migrated, "app-thanos", warnings), "Pods up")
    assert stat["plugin"]["spec"]["format"] == {"unit": word} and warnings == []


@pytest.mark.parametrize("unit", ["suffix: nanoseconds", "suffix: microseconds", "suffix: Days", "suffix: day",
                                  "suffix: days left", "prefix: days"])
def test_a_suffix_that_is_not_one_of_those_words_stays_a_plain_number(grafana, migrated, unit):
    # nanoseconds and microseconds are units of Perses 0.53 and later only.
    source(grafana, "Pods up")["fieldConfig"]["defaults"]["unit"] = unit
    warnings: list[str] = []
    stat = panel(perses.finish(grafana, migrated, "app-thanos", warnings), "Pods up")
    assert stat["plugin"]["spec"]["format"] == {"unit": "decimal"} and len(warnings) == 1


def test_a_time_series_takes_the_unit_on_its_y_axis(grafana, migrated):
    # What percli 0.54.0 writes for a timeseries with the unit "suffix: days" and one decimal, 2026-10-07.
    source(grafana, "Requests per second, per pod")["fieldConfig"]["defaults"]["unit"] = "suffix: days"
    panel(migrated["spec"], "Requests per second, per pod")["plugin"]["spec"]["yAxis"]["format"] = {
        "decimalPlaces": 1, "unit": "decimal"}
    warnings: list[str] = []
    chart = panel(perses.finish(grafana, migrated, "app-thanos", warnings), "Requests per second, per pod")["plugin"]
    assert chart["spec"]["yAxis"]["format"] == {"decimalPlaces": 1, "unit": "days"} and warnings == []
    assert "format" not in chart["spec"]


@pytest.mark.parametrize(("title", "place"), [("Pods up", ("format",)), ("Share of requests now, by pod", ("format",)),
                                              ("Requests per second, per pod", ("yAxis", "format"))])
def test_a_suffix_unit_is_carried_when_percli_wrote_no_format_at_all(grafana, migrated, title, place):
    # Without decimals on the panel, percli 0.54.0 writes no format for a unit it has no word for (2026-10-07):
    # the number then came over bare, with no warning.
    source(grafana, title)["fieldConfig"]["defaults"]["unit"] = "suffix: days"
    holder = panel(migrated["spec"], title)["plugin"]["spec"]
    for key in place[:-1]:
        holder = holder[key]
    del holder[place[-1]]
    warnings: list[str] = []
    found = panel(perses.finish(grafana, migrated, "app-thanos", warnings), title)["plugin"]["spec"]
    for key in place:
        found = found[key]
    assert found == {"unit": "days"} and warnings == []


def test_a_unit_lost_when_percli_wrote_no_format_at_all_is_a_warning_too(grafana, migrated):
    source(grafana, "Pods up")["fieldConfig"]["defaults"]["unit"] = "currencyUSD"
    del panel(migrated["spec"], "Pods up")["plugin"]["spec"]["format"]
    warnings: list[str] = []
    stat = panel(perses.finish(grafana, migrated, "app-thanos", warnings), "Pods up")
    assert "format" not in stat["plugin"]["spec"]
    assert warnings == ["'Pods up': the Grafana unit 'currencyUSD' became a plain number in Perses"]


def test_the_unit_of_a_tables_defaults_that_percli_dropped_is_a_warning(grafana, migrated):
    # percli 0.54.0 carries a table's units column by column, from the overrides: with "bytes" on the defaults and no
    # override it wrote columnSettings [], no unit anywhere (measured 2026-10-07).
    table = source(grafana, "Each pod, now")
    table["fieldConfig"] = {"defaults": {"unit": "bytes"}, "overrides": []}
    for column in panel(migrated["spec"], "Each pod, now")["plugin"]["spec"]["columnSettings"]:
        column.pop("format", None)
    warnings: list[str] = []
    perses.finish(grafana, migrated, "app-thanos", warnings)
    assert warnings == ["'Each pod, now': the Grafana unit 'bytes' of the table's defaults is not carried over: "
                        "give each column its unit, in the Grafana source"]


def test_a_table_whose_columns_each_have_their_unit_has_no_warning(grafana, migrated):
    source(grafana, "Each pod, now")["fieldConfig"]["defaults"]["unit"] = "bytes"
    for column in panel(migrated["spec"], "Each pod, now")["plugin"]["spec"]["columnSettings"]:
        if perses._is_value_column(column["name"]):
            column["format"] = {"unit": "bytes"}
    warnings: list[str] = []
    perses.finish(grafana, migrated, "app-thanos", warnings)
    assert warnings == []


def test_a_dashboard_that_lost_nothing_has_no_warning(grafana, migrated):
    warnings: list[str] = []
    perses.finish(grafana, migrated, "app-thanos", warnings)
    assert warnings == []


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
    # An ordinary file, as a redirect would have made it: not the 0600 of the temporary file it was written to.
    umask = os.umask(0)
    os.umask(umask)
    assert stat.S_IMODE(out.stat().st_mode) == 0o666 & ~umask


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


def convert_kinds(tmp_path: pathlib.Path, out: pathlib.Path) -> int:
    (tmp_path / "plugins").mkdir(exist_ok=True)
    return perses.main([str(FIXTURES / "kinds.grafana.json"), str(out), "--datasource", "app-thanos",
                        "--percli", str(stand_in_percli(tmp_path, FIXTURES / "kinds.percli.json")),
                        "--plugins", str(tmp_path / "plugins")])


@pytest.mark.parametrize("umask", [0o022, 0o002, 0o077])
def test_the_written_file_has_the_mode_of_an_ordinary_file_under_any_umask(tmp_path, monkeypatch, umask):
    # The umask is set here: under 077 the temporary file's own 0600 is also the answer, and proves nothing.
    out, handed, move = tmp_path / "chart" / "dashboard.perses.json", [], os.replace

    def replace(src, dst):
        handed.append(stat.S_IMODE(os.stat(src).st_mode))
        move(src, dst)
    monkeypatch.setattr(perses.os, "replace", replace)
    before = os.umask(umask)
    try:
        status = convert_kinds(tmp_path, out)
    finally:
        after = os.umask(before)
    assert status == 0 and after == umask                                   # the process keeps its umask
    assert stat.S_IMODE(out.stat().st_mode) == 0o666 & ~umask
    assert handed == [0o666 & ~umask]              # set before the move: the file is never 0600 under its own name


def test_a_result_that_cannot_be_moved_into_place_leaves_no_temporary_file(tmp_path, capsys):
    out = tmp_path / "chart" / "dashboard.perses.json"
    out.mkdir(parents=True)                                                 # a directory stands where the file goes
    assert convert_kinds(tmp_path, out) == 1
    assert capsys.readouterr().err.startswith("perses-dashboard: ")
    assert sorted(p.name for p in out.parent.iterdir()) == ["dashboard.perses.json"] and out.is_dir()


def test_an_interrupted_write_leaves_no_temporary_file_either(tmp_path, monkeypatch):
    # Ctrl-C while the result is being written is not an OSError: it goes on to the caller, and nothing stays behind.
    out = tmp_path / "dashboard.json"
    out.write_text("the last good one\n")

    def interrupted(result, stream, **kwargs):
        stream.write('{"half":')
        raise KeyboardInterrupt
    monkeypatch.setattr(perses.json, "dump", interrupted)
    with pytest.raises(KeyboardInterrupt):
        convert_kinds(tmp_path, out)
    monkeypatch.undo()
    assert out.read_text() == "the last good one\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["dashboard.json", "percli", "plugins"]


def test_a_mode_that_cannot_be_set_leaves_no_temporary_file_and_the_old_result(tmp_path, capsys, monkeypatch):
    out = tmp_path / "dashboard.json"
    out.write_text("the last good one\n")
    stand_in_percli(tmp_path, FIXTURES / "kinds.percli.json")               # made executable before chmod is refused

    def refuse(*args, **kwargs):
        raise PermissionError(1, "Operation not permitted")
    monkeypatch.setattr(perses.os, "chmod", refuse)
    monkeypatch.setattr(perses.os, "fchmod", refuse)
    (tmp_path / "plugins").mkdir()
    status = perses.main([str(FIXTURES / "kinds.grafana.json"), str(out), "--datasource", "app-thanos",
                          "--percli", str(tmp_path / "percli"), "--plugins", str(tmp_path / "plugins")])
    monkeypatch.undo()
    assert status == 1 and "Operation not permitted" in capsys.readouterr().err
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
