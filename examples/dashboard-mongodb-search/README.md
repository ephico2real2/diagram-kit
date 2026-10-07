# The MongoDB Search dashboard: the worked example of the standard

Copied from [mongodb-poc](https://github.com/ephico2real2/mongodb-poc) at its release `mongodb-search-helm-0.3.2` (commit `d226693`),
2026-10-07. It is the dashboard `skill/dashboard/SKILL.md` calls **[Lab]**: 29 panels in 5 sections, 97 queries.

| File here | File there | What it is |
| --- | --- | --- |
| `grafana.json` | `chart/mongodb-search-helm/files/mongodb-search.json` | The Grafana dashboard, the only file edited. `__NAMESPACE__` and `__SEARCH__` are tokens the chart replaces |
| `perses.json` | `chart/mongodb-search-helm/files/mongodb-search.perses.json` | Its Perses form, generated |
| `console-traffic.light.png`, `console-pods.light.png`, `console-data.light.png` | `docs/screenshots/dashboard-console-*.light.png` | Three sections of the Perses dashboard in the OpenShift console, cut from one capture |
| `grafana.light.png` | `docs/screenshots/dashboard-grafana-sidecar.light.png` | The same dashboard in Grafana 12.3.1 |
| `metrics-inventory-mongot.md` | made here | What `metrics-inventory` printed for the workload, 2026-10-07 |

## Regenerate, and check

```bash
perses-dashboard examples/dashboard-mongodb-search/grafana.json out.json --datasource __SEARCH__-thanos
```

Run with kit 0.2.0 on 2026-10-07, this gives `perses.json` key for key.

## The deep dive behind it

`metrics-inventory-mongot.md` is section 1 of the standard, step 2: every metric mongot emits. 1,024 names in 828
families; 743 of them did not change in an hour. The dashboard draws 22 of them, and 6 of Envoy's 487. What was
chosen, what each reads and what was left out is in that repository's
[chart README](https://github.com/ephico2real2/mongodb-poc/blob/mongodb-search-helm-0.3.2/chart/mongodb-search-helm/README.md#dashboards).

## What to look at in the files

- **One identity, one colour.** In `grafana.json`, every per-pod panel has four queries, each with an override on
  its `refId`: the first pod blue `#4e79a7`, the second red and dashed, the third yellow and dotted, any further
  purple.
- **A pod chosen by its name**: `(<expr>) and on (pod) label_replace(vector(1), "pod", "<name>", "", "")`. Chosen
  through its `up` series, a pod being replaced fell into the query for any further pod and turned purple.
- **The pie read at the end of its range**: every selector carries `@ end()`. Read over the range, it kept showing
  searches that had stopped.
- **Parts of a whole stacked**: the two traffic panels, `stacking.mode: normal`, from 0.
- **A table and a status history** where a line would say nothing: values meant to be equal across pods, and a
  state.
