# The IPsec to the NAS dashboard, Grafana and Perses

Copied from [openshift-ipsec-nas](https://github.com/ephico2real2/openshift-ipsec-nas) at commit `80c8041`:

| File here | File there | What it is |
| --- | --- | --- |
| `grafana.json` | `charts/ipsec-nas-option-c-metrics/files/ipsec-nas-option-c.json` | The Grafana dashboard: 16 numbers, 3 tables, 3 line charts and a bar gauge, in sections |
| `perses.json` | `charts/ipsec-nas-option-c-metrics/files/ipsec-nas-option-c.perses.json` | Its Perses form, the `spec.config` of a `PersesDashboard` |
| `grafana.light.png` | `docs/images/crc/48-grafana-ipsec-nas-option-c.light.png` | The Grafana dashboard on OpenShift Local |
| `perses.light.png` | `docs/images/crc/48-console-perses-ipsec-nas-option-c.light.png` | The Perses dashboard in the OpenShift console |

Its metrics come from an exporter that repository wrote, because nothing in the cluster emitted the state of an IPsec
tunnel: `skill/dashboard/COLLECTION.md`, section 2.

## How its Perses file was made, and what the kit's command does with it

That repository converts with its own `scripts/perses-dashboard.sh` and `scripts/perses-dashboard-fix.py`, written
before the kit had a converter. Run on `grafana.json` on 2026-10-07, the kit's `perses-dashboard` refuses it, by
name:

```text
perses-dashboard: the legend ['{{node}}: {{version}}'] of 'libreswan version per node' names several labels, and a
Perses StatChart shows one (percli wrote metricLabel 'node}}: {{version'): give it one label in the Grafana source
```

That is the defect the repository's fixer repairs by hand for two panels. What the fixer does, and where the kit
stands on each:

| The repository's fixer | The kit's `perses-dashboard` |
| --- | --- |
| Refuses placeholders | The same |
| Names the datasource on every query, and on the variable that lists the nodes | The same |
| Rewrites the two stats whose legend names two labels | Refuses them: which label to show is the author's choice, made in the Grafana source |
| Restores the unit `days`, which `percli` turned into a plain number | Warns, and writes the plain number |
| Splits one table in two, because its queries carry different labels | Nothing: specific to this dashboard |
| Finds panels by title | Pairs panels by their place: this dashboard has two panels called *Claims on the NAS* |

Two repositories, two converters with different repairs: the reason the kit has one.
