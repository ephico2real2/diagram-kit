#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Generate the Perses form of a Grafana dashboard, so that the Grafana JSON stays the only file edited.

    perses-dashboard <grafana.json> <out.json> --datasource <name>      (installed)
    python diagram_kit/perses.py <grafana.json> <out.json> --datasource <name>

It runs `percli migrate` (from --percli with its unpacked --plugins, or from --image with podman or docker), then
adds what the migration leaves out and refuses what it gets wrong:
  - a panel that became a placeholder (a kind Perses does not convert, or percli's plugins not unpacked);
  - a stat that shows a label takes it from its legend: one label, "{{node}}", is that label; two,
    "{{who}}: {{what}}", shows the second and is named by the first; a legend of more labels, of none, or of another
    shape, is refused: Perses shows one label;
  - a stat on a table query takes its label from the field it names ("/^version$/"); a pattern of several fields
    ("/.*/") is refused, and the field that holds the value is no label;
  - a Grafana unit "suffix: days" (or another unit of time Perses has a word for) becomes that unit, whether or not
    the panel sets decimals;
  - a panel, section or query that differs from the Grafana source, taken in order;
  - every query, a variable's included, names the datasource given (a namespace may hold several, and its default
    need not be ours);
  - a pie takes its colours by position: the list follows the order of the queries;
  - a table shows its label columns first, colours a cell matched by pattern, and gets readable text on a
    coloured cell;
  - an open-ended range mapping loses its null bound, which Perses refuses.

It warns, and still writes, when a Grafana unit became a plain number it has no word for. <out.json> is the dashboard's spec, the value of a PersesDashboard's `spec.config`; --whole keeps percli's
`kind` and `metadata` around it. Nothing is written when a check fails. skill/dashboard/SKILL.md, section 8.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time

IMAGE = "docker.io/persesdev/perses:v0.54.0"
# What percli writes in place of a panel it cannot convert (percli 0.54.0).
PLACEHOLDER = "Migration from Grafana not supported"
# The image unpacks its plugins when its server starts; until then every panel comes out a placeholder.
UNPACK_SECONDS = 60


class ConversionError(Exception):
    """The Grafana source and the Perses result disagree, or the source asks for something Perses cannot draw."""


def grafana_panels(dashboard: dict) -> list[dict]:
    """Every panel that draws, in order: a collapsed row keeps its panels inside itself."""
    out = []
    for panel in dashboard.get("panels", []):
        if panel.get("type") == "row":
            out += panel.get("panels", [])
        else:
            out.append(panel)
    return out


def _luminance(colour: str) -> float:
    if re.fullmatch("#[0-9a-fA-F]{3}", colour):
        colour = "#" + "".join(c * 2 for c in colour[1:])
    if not re.fullmatch("#[0-9a-fA-F]{6}", colour):
        raise ConversionError(f"{colour!r} is not a hex colour: a Perses cell takes #rgb or #rrggbb only")
    channels = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(one: str, other: str) -> float:
    """WCAG 2 contrast ratio of two hex colours."""
    light, dark = sorted((_luminance(one), _luminance(other)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def _readable_on(background: str) -> str:
    return max("#000000", "#ffffff", key=lambda text: contrast(text, background))


def _finish_pie(chart: dict, source: dict) -> None:
    # A Perses pie has no colour per query: it gives a list out by position. The list follows the order of the
    # queries, so a source that keeps each pie query to one series keeps each colour on its owner.
    by_ref = {o["matcher"]["options"]: prop["value"]["fixedColor"]
              for o in source.get("fieldConfig", {}).get("overrides", []) if o["matcher"]["id"] == "byFrameRefID"
              for prop in o["properties"] if prop["id"] == "color" and "fixedColor" in prop["value"]}
    if by_ref:
        refs = [t["refId"] for t in source.get("targets", [])]
        missing = [r for r in refs if r not in by_ref]
        if missing:
            raise ConversionError(f"the pie {source['title']!r} fixes a colour for some queries and not for "
                                  f"{missing}: a Perses pie takes one per query, in order")
        chart["spec"]["colorPalette"] = [by_ref[r] for r in refs]
    # percli writes showLabels: true for any displayLabels, an empty list included.
    if "displayLabels" in source.get("options", {}):
        chart["spec"]["showLabels"] = bool(source["options"]["displayLabels"])


def _is_value_column(name: str) -> bool:
    return name == "value" or name.startswith("value #")


def _finish_table(chart: dict, source: dict) -> None:
    columns = chart["spec"].get("columnSettings", [])
    ordered_by_source = any(t.get("id") == "organize" and t.get("options", {}).get("indexByName")
                            for t in source.get("transformations", []))
    if not ordered_by_source:
        # As Grafana shows a merged table: what each row is about first, then the values. percli puts a renamed
        # column after the others. A hidden column (the sample time) stays, out of the way at the front.
        columns.sort(key=lambda c: (not c.get("hide", False), _is_value_column(c["name"])))
    by_header = {c.get("header", c["name"]): c for c in columns}
    for override in source.get("fieldConfig", {}).get("overrides", []):
        mappings = [m for prop in override["properties"] if prop["id"] == "mappings" for m in prop["value"]]
        patterns = [m for m in mappings if m["type"] == "regex"]
        if not patterns:
            continue                    # percli carried the mappings by value over itself
        name = override["matcher"]["options"]
        column = by_header.get(name)
        if column is None:
            raise ConversionError(f"the table {source['title']!r} maps values of {name!r}, which no column is "
                                  f"called: {sorted(by_header)}")
        for m in patterns:
            cell = {"condition": {"kind": "Regex", "spec": {"expr": m["options"]["pattern"]}}}
            if "text" in m["options"]["result"]:
                cell["text"] = m["options"]["result"]["text"]
            if "color" in m["options"]["result"]:
                cell["backgroundColor"] = m["options"]["result"]["color"]
            column.setdefault("cellSettings", []).append(cell)
    # Perses keeps the theme's text colour on a coloured cell, white on yellow in the dark theme.
    for cell in [*chart["spec"].get("cellSettings", []), *(c for col in columns for c in col.get("cellSettings", []))]:
        if "backgroundColor" in cell and "textColor" not in cell:
            try:
                cell["textColor"] = _readable_on(cell["backgroundColor"])
            except ConversionError as error:
                raise ConversionError(f"the table {source['title']!r}: {error}") from None


def _finish_status_history(chart: dict) -> None:
    # An open-ended range comes over with "to": null, which Perses refuses: an absent bound is the open one.
    for mapping in chart["spec"].get("mappings", []):
        mapping["spec"] = {k: v for k, v in mapping["spec"].items() if v is not None}


# Grafana units that mean a plain number: for these, Perses's "decimal" is the same thing and no unit was lost.
PLAIN_UNITS = {None, "", "none", "short", "decimal", "locale"}
# The units of time Perses has had a word for since 0.51 (ui/core/src/model/units/time.ts). 0.53 adds nanoseconds
# and microseconds, which an older console plugin does not know. Grafana's "suffix: days" says the number counts days.
TIME_UNITS = {"milliseconds", "seconds", "minutes", "hours", "days", "weeks", "months", "years"}
# Where each kind keeps the unit of its values (the plugins' migrate.cue, Perses 0.54.0). A table has one per column.
UNIT_AT = {"StatChart": ("format",), "BarChart": ("format",), "GaugeChart": ("format",), "PieChart": ("format",),
           "TimeSeriesChart": ("yAxis", "format")}
# A legend of one label, "{{node}}" or "{{ node }}", and of exactly two, "{{node}}: {{version}}": who it is, then
# what is shown.
ONE_LABEL = re.compile(r"\{\{\s*([^{}\s](?:[^{}]*[^{}\s])?)\s*\}\}")
TWO_LABELS = re.compile(r"\{\{\s*(\w+)\s*\}\}[^{}]*\{\{\s*(\w+)\s*\}\}")
# What makes reduceOptions.fields a pattern and not the name of one field. A dot is left out: a label may hold one.
PATTERN_CHARS = set("\\^$|?*+()[]{}")
# The field of a table query that holds the sample: "Value", or "Value #A" when the panel has several queries.
VALUE_FIELD = re.compile(r"Value( #\w+)?")


def _repair_what_percli_wrote(name: str, panel: dict, source: dict, warnings: list[str]) -> None:
    chart = panel["plugin"]
    spec = chart["spec"]
    # A Perses stat shows ONE label of each series (metricLabel) and names the series by its format. For a stat that
    # shows its series' name (textMode "name"), percli 0.54.0 takes the first query's legend and trims the braces
    # off its two ends: "{{node}}" becomes the label "node", but "{{ node }}" becomes " node ",
    # "{{node}}: {{version}}" becomes "node}}: {{version", and a fixed text or Grafana's "__auto" stays as it is.
    # No series has such a label, and the stat shows the metric's value, 1. Seen on a real dashboard, 2026-10-07.
    # So a label that came from the legend is read from the legends again. One label is that label. Exactly two are
    # not in doubt either: the first names the series and the second is what is shown. Any other legend is the
    # author's to decide, in the Grafana source.
    label = spec.get("metricLabel", "")
    legends = [t.get("legendFormat", "") for t in source.get("targets", [])]
    several = "{{" in label or "}}" in label
    from_legend = (source.get("options", {}).get("textMode") == "name" and bool(legends)
                   and label == legends[0].strip("{}"))
    if label and (several or from_legend):
        for shape in (ONE_LABEL, TWO_LABELS):
            found = [shape.fullmatch(legend.strip()) for legend in legends]
            if legends and None not in found and len({match.groups() for match in found}) == 1:
                break
        else:
            wrong = "names several labels" if several else "is not one label, the same for every query"
            raise ConversionError(f"the legend {legends} of {name!r} {wrong}, and a Perses "
                                  f"{chart['kind']} shows one (percli wrote metricLabel {label!r}): give it one "
                                  "label, or two as '{{who}}: {{what}}', in the Grafana source")
        *who, what = found[0].groups()
        spec["metricLabel"] = what
        for query in panel.get("queries", []) if who else []:
            query["spec"]["plugin"]["spec"]["seriesNameFormat"] = "{{" + who[0] + "}}"
    # A stat on a table query (textMode "auto") shows the fields that reduceOptions.fields names, and percli makes
    # that the label, trimmed of "/", "^" and "$" at its two ends: "/^version$/" is the label "version". Three
    # things come over that are not a label. Nothing chosen, "", is the label "". The field that holds the sample,
    # "Value", is no label: without one a Perses stat shows the value, which is what Grafana shows. And a pattern
    # ("/.*/", every field) stays a pattern: Perses matches it against the names of the labels and shows the first
    # that fits, the metric's own name. Measured with percli 0.54.0, 2026-10-07.
    options, targets = source.get("options", {}), source.get("targets", [])
    fields = options.get("reduceOptions", {}).get("fields")
    if (options.get("textMode") == "auto" and targets and targets[0].get("format") == "table"
            and fields is not None and spec.get("metricLabel") == fields.strip("/^$")):
        if not fields or VALUE_FIELD.fullmatch(spec["metricLabel"]):
            del spec["metricLabel"]
        elif set(spec["metricLabel"]) & PATTERN_CHARS:
            raise ConversionError(f"the stat {name!r} shows the fields matching {fields!r}, a pattern and not one "
                                  f"field, and a Perses {chart['kind']} shows one label (percli wrote metricLabel "
                                  f"{spec['metricLabel']!r}): name the field, as '/^version$/', in the Grafana source")
    # percli has no word for a Grafana unit like "suffix: days". When the panel sets decimals it writes "decimal";
    # when it does not, it writes no format at all. It says nothing either way.
    asked = source.get("fieldConfig", {}).get("defaults", {}).get("unit")
    form = spec.get("format") or spec.get("yAxis", {}).get("format") or {}
    at = UNIT_AT.get(chart["kind"])
    if asked not in PLAIN_UNITS and (form.get("unit") == "decimal" or (at and not form)):
        suffix = re.fullmatch(r"suffix:\s*(\w+)", asked)
        if suffix and suffix.group(1) in TIME_UNITS:
            if not form:
                holder = spec
                for key in at[:-1]:
                    holder = holder.setdefault(key, {})
                form = holder.setdefault(at[-1], {})
            form["unit"] = suffix.group(1)
        else:
            warnings.append(f"{name!r}: the Grafana unit {asked!r} became a plain number in Perses")


def _place(key: str) -> tuple[int, ...]:
    """A panel key as its section and its place in it: "2_10" comes after "2_9"."""
    return tuple(int(part) for part in key.split("_")) if re.fullmatch(r"\d+(_\d+)*", key) else (10**9,)


def finish(grafana: dict, migrated: dict, datasource: str, warnings: list[str] | None = None) -> dict:
    """Check percli's result against the Grafana source and return the dashboard spec, completed.

    What is lost without being wrong (a unit Perses has no word for) is added to `warnings`, one line each.
    """
    warnings = [] if warnings is None else warnings
    spec = migrated["spec"]
    sources = grafana_panels(grafana)
    titles = [p.get("title", "") for p in sources]
    # Panels are paired by place, not by title: two panels may share a title (a number and the table under it).
    # percli keys each panel "<section>_<place>", in the order of the Grafana file.
    panels = [spec["panels"][key] for key in sorted(spec["panels"], key=_place)]
    names = [p["spec"]["display"]["name"] for p in panels]
    if names != titles:
        differing = next((f"{t!r} became {n!r}" for t, n in zip(titles, names) if t != n),
                         f"{len(titles)} panels became {len(names)}")
        raise ConversionError(f"the converted panels differ from the Grafana ones, in order: {differing}")

    # percli exits 0 even when it converted nothing: a kind Perses does not draw, or plugins not unpacked.
    lost = [(n, s["type"]) for n, p, s in zip(names, panels, sources)
            if p["spec"]["plugin"]["kind"] == "Markdown" and s.get("type") != "text"]
    if lost:
        raise ConversionError(f"panels {[n for n, _ in lost]} became placeholders: Perses does not convert the kind "
                              f"{sorted({k for _, k in lost})}, or percli ran without its plugins unpacked")

    for name, panel, source in zip(names, panels, sources):
        want = [t["expr"] for t in source.get("targets", [])]
        got = [q["spec"]["plugin"]["spec"]["query"] for q in panel["spec"].get("queries", [])]
        if got != want:
            raise ConversionError(f"the queries of {name!r} differ from the Grafana ones")
    rows = [p["title"] for p in grafana.get("panels", []) if p.get("type") == "row"]
    sections = [layout["spec"].get("display", {}).get("title") for layout in spec["layouts"]]
    if rows and [s for s in sections if s] != rows:
        raise ConversionError(f"the sections {sections} differ from the Grafana rows {rows}")

    for panel, source in zip(panels, sources):
        for query in panel["spec"].get("queries", []):
            if query["spec"]["plugin"]["kind"].startswith("Prometheus"):
                query["spec"]["plugin"]["spec"]["datasource"] = {"kind": "PrometheusDatasource", "name": datasource}
        chart = panel["spec"]["plugin"]
        _repair_what_percli_wrote(panel["spec"]["display"]["name"], panel["spec"], source, warnings)
        if chart["kind"] == "PieChart":
            _finish_pie(chart, source)
        elif chart["kind"] == "Table":
            _finish_table(chart, source)
        elif chart["kind"] == "StatusHistoryChart":
            _finish_status_history(chart)
    # Grafana's datasource picker chooses nothing once every query names its datasource. A variable that asks
    # Prometheus for its values (the nodes, the namespaces) is a query too, and percli leaves it without one.
    spec["variables"] = [v for v in spec.get("variables", [])
                         if v["spec"].get("plugin", {}).get("kind") != "DatasourceVariable"]
    for variable in spec["variables"]:
        plugin = variable["spec"].get("plugin", {})
        if plugin.get("kind", "").startswith("Prometheus"):
            plugin.setdefault("spec", {})["datasource"] = {"kind": "PrometheusDatasource", "name": datasource}
    return spec


def _converted(text: str) -> int:
    """How many panels of a percli result are not placeholders; -1 when it is not a result at all."""
    try:
        panels = json.loads(text)["spec"]["panels"].values()
    except (ValueError, KeyError, TypeError):
        return -1
    return sum(PLACEHOLDER not in json.dumps(p["spec"]["plugin"]) for p in panels)


def migrate(source: pathlib.Path, image: str, percli: str | None, plugins: pathlib.Path | None) -> dict:
    """Run percli migrate on the Grafana file and return its result."""
    arguments = ["migrate", "--format", "native", "--use-default-datasource", "-o", "json"]
    if percli:
        if not plugins or not plugins.is_dir() or list(plugins.glob("*.tar.gz")):
            raise ConversionError(f"--percli needs --plugins, a directory of unpacked Perses plugins: {plugins}")
        run = subprocess.run([percli, *arguments, "-f", str(source), "--plugin.path", str(plugins)],
                             capture_output=True, text=True)
        if run.returncode or _converted(run.stdout) < 0:
            raise ConversionError(f"percli failed: {run.stderr.strip()[-400:]}")
        return json.loads(run.stdout)

    engine = shutil.which("podman") or shutil.which("docker")
    if not engine:
        raise ConversionError("no podman or docker to run percli from the Perses image; or give --percli and --plugins")
    name = f"perses-dashboard-{os.getpid()}"          # its own name: two runs at once must not remove each other's
    with tempfile.TemporaryDirectory() as work:
        shutil.copy(source, pathlib.Path(work, "dashboard.json"))
        os.chmod(work, 0o755)
        os.chmod(pathlib.Path(work, "dashboard.json"), 0o644)
        started = subprocess.run([engine, "run", "-d", "--name", name, "-v", f"{work}:/work", image],
                                 capture_output=True, text=True)
        if started.returncode:
            raise ConversionError(f"{engine} could not start {image}: {started.stderr.strip()[-400:]}")
        try:
            best, text, deadline = -1, "", time.monotonic() + UNPACK_SECONDS
            while time.monotonic() < deadline:
                run = subprocess.run([engine, "exec", name, "/bin/percli", *arguments, "-f", "/work/dashboard.json",
                                      "--plugin.path", "/etc/perses/plugins"], capture_output=True, text=True)
                now = _converted(run.stdout)
                # The plugins unpack one after another: the result is complete once it stops improving.
                if now > 0 and now == best:
                    break
                best, text = max(best, now), run.stdout if now >= best else text
                time.sleep(1)
            if best < 0:
                raise ConversionError(f"percli gave no dashboard within {UNPACK_SECONDS} s: {run.stderr.strip()[-400:]}")
            return json.loads(text)
        finally:
            subprocess.run([engine, "rm", "-f", name], capture_output=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="perses-dashboard", description=__doc__.splitlines()[0])
    parser.add_argument("grafana", type=pathlib.Path, help="the Grafana dashboard JSON, the only file edited")
    parser.add_argument("out", type=pathlib.Path, help="where to write the Perses dashboard")
    parser.add_argument("--datasource", required=True, help="the PersesDatasource every query names")
    parser.add_argument("--whole", action="store_true", help="keep percli's kind and metadata around the spec")
    parser.add_argument("--image", default=IMAGE, help=f"the Perses image percli runs from (default {IMAGE})")
    parser.add_argument("--percli", help="a percli binary to use in place of the image, with --plugins")
    parser.add_argument("--plugins", type=pathlib.Path, help="the directory of unpacked plugins for --percli")
    args = parser.parse_args(argv)
    warnings: list[str] = []
    try:
        grafana = json.loads(args.grafana.read_text())
        migrated = migrate(args.grafana, args.image, args.percli, args.plugins)
        spec = finish(grafana, migrated, args.datasource, warnings)
    except (ConversionError, OSError, ValueError) as error:
        print(f"perses-dashboard: {error}", file=sys.stderr)
        return 1
    for warning in warnings:
        print(f"perses-dashboard: warning: {warning}", file=sys.stderr)
    result = dict(migrated, spec=spec) if args.whole else spec
    # Written beside the target and moved into place: a failed run leaves no half-written file for a chart to ship,
    # and no temporary file beside it either.
    umask = os.umask(0)
    os.umask(umask)
    temporary = None
    try:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=args.out.parent, suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            json.dump(result, stream, indent=2)
            stream.write("\n")
        # A temporary file is its owner's alone (0600); the result is an ordinary file of a repository.
        os.chmod(temporary, 0o666 & ~umask)
        os.replace(temporary, args.out)
    except OSError as error:
        if temporary:
            pathlib.Path(temporary).unlink(missing_ok=True)
        print(f"perses-dashboard: {error}", file=sys.stderr)
        return 1
    print(f"wrote {args.out} ({len(spec['panels'])} panels)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
