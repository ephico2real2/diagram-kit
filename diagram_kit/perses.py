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
  - a panel, section or query that differs from the Grafana source;
  - every query names the datasource given (a namespace may hold several, and its default need not be ours);
  - a pie takes its colours by position: the list follows the order of the queries;
  - a table shows its label columns first, colours a cell matched by pattern, and gets readable text on a
    coloured cell;
  - an open-ended range mapping loses its null bound, which Perses refuses.

<out.json> is the dashboard's spec, the value of a PersesDashboard's `spec.config`; --whole keeps percli's
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
            cell["textColor"] = _readable_on(cell["backgroundColor"])


def _finish_status_history(chart: dict) -> None:
    # An open-ended range comes over with "to": null, which Perses refuses: an absent bound is the open one.
    for mapping in chart["spec"].get("mappings", []):
        mapping["spec"] = {k: v for k, v in mapping["spec"].items() if v is not None}


def finish(grafana: dict, migrated: dict, datasource: str) -> dict:
    """Check percli's result against the Grafana source and return the dashboard spec, completed."""
    spec = migrated["spec"]
    sources = grafana_panels(grafana)
    titles = [p.get("title", "") for p in sources]
    repeated = sorted({t for t in titles if titles.count(t) > 1})
    if repeated:
        raise ConversionError(f"panels share a title, and panels are matched by title: {repeated}")
    by_title = dict(zip(titles, sources))
    panels = list(spec["panels"].values())
    names = [p["spec"]["display"]["name"] for p in panels]
    if sorted(names) != sorted(titles):
        raise ConversionError(f"the converted panels differ from the Grafana ones: {sorted(set(names) ^ set(titles))}")

    # percli exits 0 even when it converted nothing: a kind Perses does not draw, or plugins not unpacked.
    lost = [n for n, p in zip(names, panels)
            if p["spec"]["plugin"]["kind"] == "Markdown" and by_title[n].get("type") != "text"]
    if lost:
        kinds = sorted({by_title[n]["type"] for n in lost})
        raise ConversionError(f"panels {lost} became placeholders: Perses does not convert the kind {kinds}, "
                              "or percli ran without its plugins unpacked")

    for name, panel in zip(names, panels):
        want = [t["expr"] for t in by_title[name].get("targets", [])]
        got = [q["spec"]["plugin"]["spec"]["query"] for q in panel["spec"].get("queries", [])]
        if got != want:
            raise ConversionError(f"the queries of {name!r} differ from the Grafana ones")
    rows = [p["title"] for p in grafana.get("panels", []) if p.get("type") == "row"]
    sections = [layout["spec"].get("display", {}).get("title") for layout in spec["layouts"]]
    if rows and [s for s in sections if s] != rows:
        raise ConversionError(f"the sections {sections} differ from the Grafana rows {rows}")

    for name, panel in zip(names, panels):
        for query in panel["spec"].get("queries", []):
            if query["spec"]["plugin"]["kind"].startswith("Prometheus"):
                query["spec"]["plugin"]["spec"]["datasource"] = {"kind": "PrometheusDatasource", "name": datasource}
        chart, source = panel["spec"]["plugin"], by_title[name]
        if chart["kind"] == "PieChart":
            _finish_pie(chart, source)
        elif chart["kind"] == "Table":
            _finish_table(chart, source)
        elif chart["kind"] == "StatusHistoryChart":
            _finish_status_history(chart)
    # Grafana's datasource picker chooses nothing once every query names its datasource.
    spec["variables"] = [v for v in spec.get("variables", [])
                         if v["spec"].get("plugin", {}).get("kind") != "DatasourceVariable"]
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
    try:
        grafana = json.loads(args.grafana.read_text())
        migrated = migrate(args.grafana, args.image, args.percli, args.plugins)
        spec = finish(grafana, migrated, args.datasource)
    except (ConversionError, OSError, ValueError) as error:
        print(f"perses-dashboard: {error}", file=sys.stderr)
        return 1
    result = dict(migrated, spec=spec) if args.whole else spec
    # Written beside the target and moved into place: a failed run leaves no half-written file for a chart to ship.
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=args.out.parent, suffix=".tmp", delete=False) as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    os.replace(stream.name, args.out)
    print(f"wrote {args.out} ({len(spec['panels'])} panels)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
