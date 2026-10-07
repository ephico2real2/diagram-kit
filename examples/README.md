# Examples

Real pages and dashboards, copied from the repositories they were made in, so that the kit shows its own results.
Each row names where the files came from; the copies here are frozen at that commit, and the originals move on.

| Example | What it shows | Copied from |
| --- | --- | --- |
| [`fan-out/`](fan-out/) | The connector kinds of `STANDARD.md` §3 on one page: a curved fan-out, labelled dashed arrows | Written for the kit |
| [`perses-converter/`](perses-converter/) | A diagram page started from the kit's template and rendered by it: how a browser reaches the page that converts a Grafana dashboard to Perses | [openshift-coo-helm](https://github.com/ephico2real2/openshift-coo-helm), `docs/diagrams/converter/`, commit `68c0deb` |
| [`dashboard-ipsec-nas/`](dashboard-ipsec-nas/) | A Grafana dashboard and its Perses form, 23 panels fed by an exporter of the repository's own, with a picture of each | [openshift-ipsec-nas](https://github.com/ephico2real2/openshift-ipsec-nas), `charts/ipsec-nas-option-c-metrics/files/` and `docs/images/crc/`, commit `80c8041` |

Not copied, and worth opening where they live:

- **The worked example of the dashboard standard**: the MongoDB Search dashboard, 29 panels, in
  [mongodb-poc](https://github.com/ephico2real2/mongodb-poc/tree/main/chart/mongodb-search-helm): `files/mongodb-search.json` (Grafana, the
  source), `files/mongodb-search.perses.json` (generated), and the captures under
  [`docs/screenshots/`](https://github.com/ephico2real2/mongodb-poc/tree/main/docs/screenshots). It is still changing; a copy comes here with
  its next release.
- **How per-node metrics are collected**, as a figure: the fourth figure of
  [openshift-ipsec-nas's diagram page](https://github.com/ephico2real2/openshift-ipsec-nas/blob/main/docs/diagrams/ipsec-nas/perses-dashboard.light.png),
  which `skill/dashboard/COLLECTION.md` section 2 describes in words.
- **The tutorial's six dashboards** and the script that generates them:
  [cilium-implementation-poc, demo 38](https://github.com/ephico2real2/cilium-implementation-poc/tree/main/demos/38-grafana-visual-grammar).

## Licence

The source repositories carry no licence file of their own. Their owner, who is also the kit's, copied these files
here, where `examples/` is under MIT No Attribution (`LICENSES/MIT-0.txt`, `NOTICE`).
