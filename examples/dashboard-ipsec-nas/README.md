# The IPsec to the NAS dashboard, Grafana and Perses

Copied from [openshift-ipsec-nas](https://github.com/ephico2real2/openshift-ipsec-nas) at commit `e6ec027`:

| File here | File there | What it is |
| --- | --- | --- |
| `grafana.json` | `charts/ipsec-nas-option-c-metrics/files/ipsec-nas-option-c.json` | The Grafana dashboard: 16 numbers, 4 tables, 3 line charts and a bar gauge, in six sections |
| `perses.json` | `charts/ipsec-nas-option-c-metrics/files/ipsec-nas-option-c.perses.json` | Its Perses form, the `spec.config` of a `PersesDashboard` |
| `grafana.light.png` | `docs/images/crc/61-grafana-two-tables.light.png` | The Grafana dashboard on OpenShift Local |
| `perses.light.png` | `docs/images/crc/61-console-perses-two-tables.light.png` | The Perses dashboard in the OpenShift console |

Its metrics come from an exporter that repository wrote, because nothing in the cluster emitted the state of an IPsec
tunnel: `skill/dashboard/COLLECTION.md`, section 2.

## The kit makes its Perses file

```sh
perses-dashboard grafana.json out.json --datasource ipsec-nas-thanos
```

Run with kit 0.2.1 on 2026-10-07, this gives `perses.json` byte for byte. That repository's
`scripts/perses-dashboard.sh` runs the same command for both of its charts.

## What it took: a second dashboard found what the first did not

Until that day the repository converted with a fixer of its own, written before the kit had a converter, and kit
0.2.0 refused its Grafana file by name:

```text
perses-dashboard: the legend ['{{node}}: {{version}}'] of 'libreswan version per node' names several labels, and a
Perses StatChart shows one (percli wrote metricLabel 'node}}: {{version'): give it one label in the Grafana source
```

What the fixer did, and where each thing went:

| The repository's fixer | Now |
| --- | --- |
| Refused placeholders | The kit, since 0.2.0 |
| Named the datasource on every query, and on the variable that lists the nodes | The kit, since 0.2.0 |
| Found panels by title | The kit pairs panels by their place: this dashboard has two panels called *Claims on the NAS* |
| Rewrote the two stats whose legend names two labels | The kit, since 0.2.1: `{{node}}: {{version}}` is the series name and the label shown |
| Restored the unit `days`, which `percli` turned into a plain number | The kit, since 0.2.1: Grafana's `suffix: days` is the Perses unit |
| Split one table in two, because its queries carried different labels | The Grafana file: two tables, in Grafana as in Perses. A decision about a dashboard belongs in its source |

The last row is the rule worth keeping (`skill/dashboard/SKILL.md`, section 8): every query of a table with several
queries carries the same labels. A Perses table joins rows by all their labels, so one query labelled `node, pod`
among nine labelled `node` gave each node a second row.

Two repositories, two converters with different repairs: the reason the kit has one.
