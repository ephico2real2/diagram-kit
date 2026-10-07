# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""metrics-inventory: every metric a workload emits, with the kind of data each is.

No test reaches a Prometheus: the API is a function handed in, answered here from a table. The shapes are the ones
a Thanos Querier 0.41 gave for a real workload on 2026-10-07 (1,024 names, 5,489 series), cut down to five names.
"""

from __future__ import annotations

import pytest

from diagram_kit import metrics

MATCH = '{namespace="app",job="app"}'


def vector(counts: dict[str, int], label: str = "__name__") -> dict:
    return {"resultType": "vector", "result": [{"metric": {label: name}, "value": [0, str(count)]}
                                                 for name, count in counts.items()]}


SERIES = {"app_requests_total": 3, "app_latency_seconds_bucket": 36, "app_latency_seconds_count": 3,
          "app_index_size_bytes": 15, "app_uptime_seconds": 3, "app_build_info": 3, "app_wait_seconds": 12}
CHANGED = {"app_requests_total": 3, "app_latency_seconds_bucket": 30, "app_latency_seconds_count": 3,
           "app_uptime_seconds": 3, "app_wait_seconds": 12}
DISTINCT = {"app_requests_total": 3, "app_latency_seconds_bucket": 20, "app_latency_seconds_count": 3,
            "app_index_size_bytes": 5, "app_uptime_seconds": 3, "app_build_info": 1, "app_wait_seconds": 9}
METADATA = {"app_requests_total": [{"type": "counter", "help": "Requests served."}],
            "app_latency_seconds": [{"type": "histogram", "help": "Request latency."}],
            "app_index_size_bytes": [{"type": "gauge", "help": "Size of an index."}],
            "app_uptime_seconds": [{"type": "gauge", "help": "Seconds since start."}],
            "app_build_info": [{"type": "gauge", "help": "Build facts."}],
            "app_wait_seconds": [{"type": "summary", "help": "Time waiting."}],
            "other_workload_total": [{"type": "counter", "help": "Not ours."}]}
LABELLED = [{"__name__": "app_index_size_bytes", "namespace": "app", "pod": f"app-{pod}", "job": "app",
             "index": f"index-{index}", "shard": "0"} for pod in range(3) for index in range(5)]
LABELLED += [{"__name__": "app_requests_total", "namespace": "app", "pod": f"app-{pod}", "job": "app",
              "user": f"user-{user}"} for pod in range(3) for user in range(60)]


def api(path: str, params: dict[str, str]) -> dict:
    if path == "/api/v1/metadata":
        return METADATA
    if path == "/api/v1/series":
        assert params == {"match[]": MATCH}
        return LABELLED
    query = params["query"]
    if "changes(" in query:
        # changes() drops the metric name: the name must have been copied to a label, over a subquery.
        assert query == (f'count by (metric) (changes(label_replace({MATCH}, "metric", "$1", "__name__", "(.+)")'
                         "[1h:1m]) > 0)")
        return vector(CHANGED, "metric")
    if "count_values" in query:
        return vector(DISTINCT)
    assert query == f"count by (__name__) ({MATCH})"
    return vector(SERIES)


@pytest.fixture
def rows() -> dict[str, dict]:
    return {row["name"]: row for row in metrics.inventory_from_api(api, MATCH, "1h")}


def test_one_row_per_name_the_selector_matches_and_no_other(rows):
    assert sorted(rows) == sorted(SERIES)                       # other_workload_total is declared and not matched


def test_a_sample_name_takes_the_type_of_its_family(rows):
    assert rows["app_latency_seconds_bucket"]["family"] == "app_latency_seconds"
    assert {rows[name]["type"] for name in ("app_latency_seconds_bucket", "app_latency_seconds_count")} == {"histogram"}
    assert rows["app_requests_total"]["type"] == "counter" and rows["app_wait_seconds"]["type"] == "summary"


@pytest.mark.parametrize(("name", "words"), [
    ("app_requests_total", "a counter: its rate over time"),
    ("app_latency_seconds_bucket", "a distribution: a percentile from its buckets"),
    ("app_wait_seconds", "its own quantiles do not combine across instances"),
    ("app_uptime_seconds", "a level that moves: a line over time"),
    ("app_index_size_bytes", "constant, differing by series: a table or sorted bars, not a line"),
    ("app_build_info", "facts as labels: a table"),
])
def test_the_kind_of_data_decides_what_a_metric_can_be(rows, name, words):
    assert words in rows[name]["kind"]


def test_a_gauge_that_never_moves_and_reads_the_same_everywhere_is_a_number():
    assert metrics.kind_of("app_replicas", "gauge", 3, 0, 1).startswith("constant, the same on every series")


def test_labels_are_counted_without_the_ones_every_target_carries(rows):
    assert rows["app_index_size_bytes"]["labels"] == {"index": 5, "shard": 1}
    assert rows["app_requests_total"]["labels"] == {"user": 60}


def test_the_report_states_the_totals_and_marks_a_label_with_many_values(rows):
    report = metrics.render(list(rows.values()), f"`{MATCH}`", "1h")
    assert "7 metric names in 6 families, 75 series." in report
    assert "2 of the 7 names did not change on any series in the last 1h." in report
    assert "| histogram | 1 |" in report and "| gauge | 3 |" in report
    assert "## app_index (1)" in report
    assert "| `app_requests_total` | counter | 3 | 3 | 3 | user (60 !) |" in report
    assert "| `app_index_size_bytes` | gauge | 15 | 0 | 5 | index (5), shard (1) |" in report


def test_labels_can_be_left_out_on_a_large_selector():
    asked = []

    def counting(path, params):
        asked.append(path)
        return api(path, params)

    found = metrics.inventory_from_api(counting, MATCH, "1h", labels=False)
    assert "/api/v1/series" not in asked and all(row["labels"] == {} for row in found)


PAGE = """\
# HELP app_requests_total Requests served.
# TYPE app_requests_total counter
app_requests_total{code="200",pod="app-0"} 12
app_requests_total{code="500",pod="app-0"} 1
# HELP app_latency_seconds Request latency.
# TYPE app_latency_seconds histogram
app_latency_seconds_bucket{le="0.1"} 3
app_latency_seconds_bucket{le="+Inf"} 4
app_latency_seconds_sum 0.42
app_latency_seconds_count 4
# TYPE app_note gauge
app_note{text="a \\"quoted\\" word, and a comma"} 1
untyped_thing 7
"""


def test_a_saved_page_gives_names_types_and_series_and_no_measurement_it_cannot_make():
    found = {row["name"]: row for row in metrics.inventory_from_text(PAGE)}
    assert sorted(found) == ["app_latency_seconds_bucket", "app_latency_seconds_count", "app_latency_seconds_sum",
                             "app_note", "app_requests_total", "untyped_thing"]
    assert found["app_requests_total"]["series"] == 2 and found["app_requests_total"]["labels"] == {"code": 2}
    assert found["app_latency_seconds_sum"]["type"] == "histogram"
    assert found["app_note"]["labels"] == {"text": 1}
    assert found["untyped_thing"]["type"] == "unknown"
    assert all(row["changing"] is None and row["distinct"] is None for row in found.values())
    report = metrics.render(list(found.values()), "the page `metrics.txt`", None)
    assert "Changed" not in report and "did not change" not in report
    assert "6 metric names in 4 families, 8 series." in report


def test_the_command_reads_a_page_from_a_file(tmp_path, capsys):
    page = tmp_path / "metrics.txt"
    page.write_text(PAGE)
    assert metrics.main(["--text", str(page)]) == 0
    assert capsys.readouterr().out.startswith("# Metrics inventory\n\nSource: the page `metrics.txt`\n")


def test_an_api_needs_a_selector(capsys):
    with pytest.raises(SystemExit):
        metrics.main(["--prometheus", "http://localhost:9090"])
    assert "an inventory of every metric of a cluster is not a workload's" in capsys.readouterr().err


def test_an_api_that_cannot_be_reached_is_an_error_and_not_an_empty_inventory(capsys):
    assert metrics.main(["--prometheus", "http://127.0.0.1:1", "--match", MATCH]) == 1
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err.startswith("metrics-inventory: ")
