---
name: dashboard
description: Design, build, recolour, convert and validate a metrics dashboard - Grafana, and its Perses form for the OpenShift console - to one standard, starting from an inventory of every metric the workload emits and how it is collected (ServiceMonitor or PodMonitor, TLS, an exporter of its own), then the few metrics that answer a reader's question, the chart chosen by the kind of data, one fixed colour per identity from the Tableau 10 palette, words on every panel, and proof from the data source and from screenshots in both themes. Use when the user types /dashboard or /grafana, or asks to create, change, review, recolour or convert a dashboard or a panel, to choose which metrics to show, or to get a workload's metrics scraped.
---

# /dashboard — a dashboard a stranger can read, the same in Grafana and in Perses

`/dashboard <what to build or change>` starts from the data: what the workload emits, how it is collected, and which
few metrics answer a reader's question. Ask a question only when the subject is ambiguous; everything else has a
default below.

Two commands come with the kit (`README.md`, Install):

| Command | What it does |
| --- | --- |
| `metrics-inventory --prometheus <url> --match '<selector>'` | Lists every metric a workload emits, with the kind of data each is (section 1) |
| `perses-dashboard <grafana.json> <out.json> --datasource <name>` | Generates the Perses form of a Grafana dashboard and refuses what the conversion gets wrong (section 8) |

`COLLECTION.md`, beside this file, is the part to read when a workload's metrics are not scraped yet.

This standard combines research with what was built and measured. Every rule carries the tag of its
source, so a reader can tell a published finding from a measurement from a matter of taste.

| Tag | Source | What it is |
| --- | --- | --- |
| **[T§n]** | [cilium-implementation-poc, demo 38](https://github.com/ephico2real2/cilium-implementation-poc/blob/main/demos/38-grafana-visual-grammar/README.md), section n | The tutorial: six generated dashboards, measured on Grafana 13.2.1, 2026-09-17. Read it before a first dashboard |
| **[Lab]** | [mongodb-poc](https://github.com/ephico2real2/mongodb-poc): `chart/mongodb-search-helm/files/mongodb-search.json`, `test/chart.sh`, `docs/grafana-to-perses-conversion.md`, and the chart's README | The worked example: 29 panels, measured 2026-10-06 and 07 on Grafana 12.3.1, in the OpenShift 4.22.7 console (COO 1.5.3: PieChart 0.13.1, Table 0.11.2, TimeSeriesChart 0.13.0-beta.0) and in the `perses:v0.54.0` image that `percli` runs from (PieChart 0.14.0, Table 0.13.0, TimeSeriesChart 0.13.0) |
| **[Owner]** | the same work | A look the owner accepted or rejected from a screenshot. Taste, recorded so it is not argued twice |
| **[Stone]** | Maureen Stone, *How we designed the new color palettes in Tableau 10*, 2016, <https://www.tableau.com/blog/colors-upgrade-tableau-10-56782> | How the palette was designed and tested |
| **[Few]** | Stephen Few, *Save the Pies for Dessert*, 2007, <https://www.perceptualedge.com/articles/visual_business_intelligence/save_the_pies_for_dessert.pdf> | What a pie, a bar, a line, a table and a stacked area are each good and bad at |
| **[Grafana]** | <https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/visualizations/> and its pie chart page | What Grafana says each visualization is for |
| **[SRE]** | Google, *Site Reliability Engineering*, ch. 6, <https://sre.google/sre-book/monitoring-distributed-systems/> | The four golden signals; the tail of a latency |

A version named in a rule is where it was measured. On another version, measure again before relying on it.

## 1. The metrics deep dive: plan first, measure first

A dashboard shows the few metrics that answer a reader's question, not the hundreds a workload emits. Do this for
every workload, before any panel, and keep the result in the repository.

1. **Make sure the metrics are collected.** `COLLECTION.md`: does the workload emit what the question needs, does
   it need an exporter of its own, a ServiceMonitor or a PodMonitor, a scrape over TLS or with a credential, and
   what the platform needs first.
2. **Take the whole inventory.**
   `metrics-inventory --prometheus <url> --match '{namespace="…",job="…"}' > docs/metrics-inventory-<workload>.md`
   (or `--text` on a saved `/metrics` page). One row per metric name: its declared type, its series, the labels
   that tell them apart, how many series changed in the last hour, how many distinct values they hold now, and
   the kind of data that makes it. On the worked example, 2026-10-07: mongot emits 1,024 names in 828 families
   (465 gauges, 209 counters, 141 summaries, 5 histograms, 8 undeclared), 5,489 series, and 743 of the names did
   not change in an hour; Envoy emits 487 names, of which 374 did not change. [Lab]
3. **Start from the reader's questions, not from the list.** What would an ordinary user of the service ask: is it
   up, is my traffic spread, is it slow, is it failing, is it full, does every replica hold the same data? Find
   in the inventory the metric that answers each. [Owner] The four golden signals are the checklist: traffic
   ("how much demand"), errors ("the rate of requests that fail"), latency ("the time it takes to service a
   request", successes and failures apart), saturation ("How 'full' your service is", the most constrained
   resource first). [SRE]
4. **Keep few.** A metric that answers no question a reader asks is left out, however interesting. The worked
   example draws 22 of mongot's 1,024 names and 6 of Envoy's 487, with `up` and `kube_pod_start_time`. [Owner]
   [Lab]
5. **Let the kind of data decide what a metric can be**, before choosing a chart in section 2:

   | The data | How the inventory shows it | The query | What it can be |
   | --- | --- | --- | --- |
   | A counter | type `counter`, a name ending `_total` | its `rate()` over a stated window; never the raw number | a line over time; bands when the series are parts of a whole; a number for the rate now |
   | A distribution | type `histogram`, `_bucket` | `histogram_quantile` over `sum by (le)`, across instances | a line of a percentile |
   | A summary | type `summary`: `_sum`, `_count`, a `quantile` label | an average, `rate(_sum) / rate(_count)`; its own quantiles per instance only, they do not combine | a line, said to be an average |
   | A level that moves | a gauge whose series changed | as it is | a line; a number for now; a gauge only with a real ceiling |
   | A constant, the same everywhere | a gauge, 0 series changed, 1 distinct value | the last value | a number or a table row, not a line |
   | A constant that differs by series | a gauge, 0 series changed, several distinct values | the last value, by the label that differs | a table or sorted bars, not a line |
   | Values meant to be equal across replicas | the same reading expected on every instance | the last value per instance | a table of "now", and one line with one shade that shows when they part (section 5) |
   | A state | a label with a closed set of values, each series 0 or 1 | the sum per instance of the states that matter | a status history |
   | Facts | a name ending `_info`, value 1 | the last value | a table |
   | Parts of a whole | series that add up to a total | each part over the sum | one pie for now, bands stacked to 100% over time |

   [Lab], with [T§1] for the charts.
6. **Run every query against the real data source before it goes in a file**, and record what came back: series,
   labels, a warning. A panel designed on a metric's name instead of its values is the usual source of a
   retraction (a "refused searches" counter that counted work run on the caller's thread; a "JVM limit" that
   summed non-heap pools and a `-1`). [Lab]
7. **Record the choice** where the dashboard lives: the inventory, the short list with the question each metric
   answers and what it reads, the readings taken, and what was looked at and left out, with the reason. [Lab]
8. **One section per question** ("Is search up?", "Is traffic spread across the pods?"). A Grafana row becomes a
   Perses section. List the panels before building any: the question, the query, the chart. Existing panels stay
   unless the owner says otherwise: panels are added, not replaced. [Owner] [Lab]

## 2. The question decides the chart

A panel is a query, a reduction and a visualization; most mistakes are a mismatch between two of the
three. [T§0]

| The question | The chart | Source |
| --- | --- | --- |
| What is it now? | Stat, "for big stats and optional sparkline" | [T§1] [Grafana] |
| How far from a limit? | Gauge, only with a real ceiling; without one it is decoration | [T§1] |
| What happened, and when? | Time series. "Nothing shows change through time better than a line" | [T§1] [Few] |
| What share of a whole, now? | One pie, few slices that matter | [T§1] [Grafana], with [Few]'s limits below |
| What share of a whole, over time? | A time series stacked to 100% | [Lab], with [Few]'s limits below |
| Who is biggest? | Bars sorted, one colour, on an instant query (on a range query the sort did not hold) | [T§1] [Few] |
| Which state, for how long? | Status history, "for periodic state over time" (a state timeline does not convert to Perses) | [Grafana] [Lab] |
| The facts, side by side? | Table. A chart whose values must all be labelled is "an awkwardly arranged equivalent of a table" | [T§1] [Few] |
| How are values distributed? | Histogram or heatmap, in Grafana only: both become a placeholder in Perses 0.54.0 | [Grafana] [Lab] |

**The limits of a pie** [Few]: its one built-in message is part-to-whole. A slice is easy to read only
"when it is close to 0%, 25%, 50%, 75%, or 100%"; eyes compare position and length well, "but not 2-D
areas and angles". So: at most one pie for a question, never several side by side to compare ("the only
worse design than a pie chart is several of them", Tufte in [Few]), always beside a number or a table
that states the values, no 3-D and no gloss. Grafana 12.3.1 shades its pie with a gradient; whether that
can be turned off was not looked up.

**The limits of a stacked area** [Few]: only the bottom band has a flat baseline; every other band is
read by its height, "which is more difficult to judge". Stack only parts of a whole, state the share as
a percentage when the share is the question, and keep each series' own value one hover away.

**Kinds that convert to Perses 0.54.0** [Lab]: `timeseries`, `stat`, `gauge`, `piechart`, `table`,
`status-history`, and `bargauge` (as a bar chart). `barchart`, `histogram`, `heatmap` and
`state-timeline` become a placeholder that says the migration is not supported.

## 3. The query and its reduction

- **The reducer is part of the question.** Last, mean or max give different numbers the moment
  something changes (a mean of 2.02 where the last value said 2). Say which one a panel shows. [T§2]
- **A pie or a legend takes one series per slice**: a range query reduced to its last value, not an
  instant table with *All values*, where equal counts share a colour. [T§2]
- **A latency is a percentile from buckets, not a mean**: collect "request counts bucketed by
  latencies"; an average hides the slow tail. [SRE] Draw an average only when the source exposes no
  buckets, and say so in the description. mongot exposes none: `_sum`, `_count`, `_max`, and its own
  quantiles (0.5, 0.75, 0.9, 0.99) per pod, which can be drawn per pod but not combined across pods. [Lab]
- **The rate window.** In a Grafana-only dashboard use `$__rate_interval`: a fixed `[1m]` turns spiky
  and gappy when the panel is zoomed out. [T§2] In a dashboard that also ships to Perses the worked
  example uses a fixed `[5m]` (20 scrapes at 15 s) and states the window in the description of each
  of its 15 rate panels; whether
  `$__rate_interval` works in Perses 0.54.0 was not measured. [Lab]
- **One query per line when the dashboard ships to Perses.** Perses 0.54.0 fixes a colour per query, not
  per series, in a time series chart. For pods with stable names, one query per pod and one for any further pod,
  each choosing its pod by name: `(<expr>) and on (pod) label_replace(vector(1), "pod", "<name>-0", "", "")` …
  `(<expr>) unless on (pod) (label_replace(vector(1), "pod", "<name>-0", "", "") or …)`, each coloured by an
  override on its `refId`. Do not choose a pod through its `up` series: while a pod is replaced its `up` is gone
  and its last minutes are still in the rates, so it fell into the query for any further pod and was drawn in that
  colour, in seven charts. Cost measured: 97 queries a refresh instead of 27, 0.45 s in all through Thanos
  Querier. [Lab]
- **A Perses pie has no colour per query.** Its `colorPalette` is taken by position (PieChart 0.13.1 and
  0.14.0): give each pie query exactly one series, sum the open-ended rest into one, and return nothing
  when the whole is zero, or the colours leave their owners and zeros are drawn as equal slices. [Lab]
- **A pie of "now" is read at the end of its range.** A pie draws the last value of each query; read over the
  whole range it kept showing searches that had stopped, for as long as the range reached back to them, in
  Grafana 12.3.1 and in Perses 0.54.0. Put `@ end()` on every selector of the pie, and check the drawn panel a
  few minutes after the traffic stops, not only the queries. [Lab]
- **Generated names** (a Deployment's pods) have no stable name to match: rank them by
  `kube_pod_start_time` with `topk(1|2|3, …)`. Ordering by the process's own uptime flipped between
  steps. [Lab]
- **A counter whose name does not end in `_total`** draws a warning sign through Thanos Querier (0.41.0,
  over Prometheus 3.9.1). Rename
  it at the scrape (`metricRelabelings`); do not hide the sign. [Lab]

## 4. Colour carries one thing

Identity, a quantity on a scale, or nothing. Never two of them in one panel. [T§3]

**Identity: six colours of the Tableau 10 palette, fixed, in this order.**

| Order | Colour | Use |
| --- | --- | --- |
| 1 | Blue `#4e79a7` | the first of a set |
| 2 | Red `#e15759` | the second; also "bad" |
| 3 | Yellow `#edc948` | the third |
| 4 | Purple `#b07aa1` | any further one |
| | Green `#59a14f` | "good": a healthy state, a 2xx, the base of a threshold |
| | Orange `#f28e2b` | "warning": the middle threshold, a 4xx |

The palette's other four (teal `#76b7b2`, pink `#ff9da7`, brown `#9c755f`, grey `#bab0ac`) are free for
a fifth to eighth identity; not yet used on a dashboard. d3's `schemeTableau10` gives four of the ten
one unit apart (`f28e2c`, `edc949`, `af7aa1`, `bab0ab`), which the eye cannot tell.

Why this palette:

- It is "a full-hue circle", "a good default because the colors are visually very distinct and
  correspond to simple color names like red, blue, purple, and brown", and it is "softer, more
  sophisticated, less 'Crayola bright'" than what it replaced. [Stone] The owner rejected saturated
  blue, red and yellow as too bold, and blue beside green as too alike. [Owner]
- It was tested the ways a dashboard uses colour: as legend squares, as small marks, under text, and
  "stacked to simulate the appearance of stacked bars or area charts". [Stone]
- Distance in CIELAB is perceived difference: "colors that are close together are similar". [Stone]
  So measure it: the closest two pod colours here are blue and purple, CIE76 ΔE 34; the generated
  colours they replaced had a pair at ΔE 26, which the owner reported as too alike. [Lab] [Owner]

The rules:

- **One identity, one colour, in every panel and both forms**: the line, the band, the pie slice and
  the table cell of the first pod are the same blue, in Grafana and in Perses, light and dark. Set it
  with an override per name or per query; never rely on palette position for something people
  recognise. [T§3] [Lab]
- **A small, known set takes fixed colours; nothing is left to a palette.** [Lab] Grafana's by-name
  palette keeps a colour per name on a time series, and is the fallback for an open-ended set there,
  but it paints a whole pie, stat or bar gauge one colour (grafana#73275). [T§3] Perses 0.54.0 makes
  a colour from each series' name by default, and that default gave the colours that were too alike.
  [Lab]
- **A quantity takes thresholds**, green, orange, red from the same palette; a threshold on a category
  is noise. [T§3] For a continuous scale use one hue from light to dark; Tableau moved its own
  quantity defaults off red-green as "much more friendly to our users with common forms of
  color-vision deficiencies". [Stone]
- **Colour is never the only carrier of a state.** Green and red are kept for good and bad by
  convention, so the number, the state's name in the legend, or the dashed line says it too. [Stone]
  [Lab]
- **Nothing: one colour** for a ranking; a colour per item there changes with every new item and means
  nothing. [T§3]
- **Know the weak spot.** Contrast against the console's backgrounds: yellow 1.6:1 on white and 9.0:1
  on dark `#292929`; blue 4.5:1 and 3.2:1; red 3.7:1 and 4.0:1; purple 3.4:1 and 4.3:1. The third
  line is faint in the light theme. Text on a coloured cell is black or white, whichever contrasts
  more (WCAG); black wins on all four, by 4.6 to 4.5 on blue. That is the Perses form: Grafana 12.3.1
  chooses the text itself. [Lab]

## 5. Lines, shades, stacking

"A large area of any color looks brighter and more colorful than a small one." [Stone] So a thin line
takes the full colour and an area takes the same colour much lighter.

- **Line width 1.** Width 3 was rejected as too bold. [Owner]
- **A shade under every line, the line's colour at 10% opacity** (`custom.fillOpacity: 10` on the
  query's override). No shade was rejected; one shade for the whole panel was rejected ("I only see
  blue"). [Owner]
- **Second line dashed, third dotted**, so that three lines on each other all show. [Lab]
- **Parts of a whole are stacked** (`stacking.mode: normal`, 30% opacity, axis from 0, and 0 to 1 for a
  share). Unstacked, even traffic is three lines on each other and three shades that blend to brown;
  stacked, it is three equal bands. The tooltip still shows each series' own value (read in Perses
  0.54.0). Mind [Few]'s limits in section 2. [Lab] [Owner]
- **Where every series reads the same by design** (index size on every replica, uptime), three shades
  are one brown block: keep one, the first colour at 15%, and put a table of the latest readings beside
  such panels, so that "the same" reads as equal rows. [Lab] [Owner]
- **Axes**: from 0 for a count, a per-second rate, uptime and anything stacked; 0 to 1 for a share of a fixed
  whole, so that a tenth of a percent is not drawn as a cliff. Left to itself, Grafana 12.3.1 drew a steady rate
  on an axis from 0.725 to 0.85, its shade starting there. [Lab]

## 6. Layout, legends, numbers

- **Legend below the chart, never beside it**: at the side it squeezed the chart into a strip. [Owner]
- **Two panels to a row** (12 of 24 wide, 8 high) is the default. A panel a third of the page wide
  needs two legend lines for three names, and the console draws the second line only from a height of
  11 (cut at 8, 9 and 10; the legend's `size` made no difference). Measured on a page 1600 pixels wide
  with names of 17 characters; longer names or a narrower page were not measured. [Lab]
- **A stat shows a number, and the title carries the unit**: a long unit after the value
  ("1.59 requests/sec") made Perses shrink it to a quarter of its neighbours. [Lab]
- **A table's first column is what each row is about**, on its colour; hide the time column. [Lab]
- **A status history names its states** with value mappings and a fixed colour mode; with thresholds
  Grafana 12.3.1's legend read "< 1" and "1+". [Lab]

## 7. Words: a panel that needs a hover is unfinished [T§4]

- The title says what, and the unit.
- The unit is set, so the tool scales it and the reader stops counting zeros.
- The legend names the series (`{{pod}}`), not the metric, and shows the calculation that matters.
- The description says the source, the window, what normal looks like and what an empty panel means.
- **A caption under the panel** (a transparent text panel in markdown) repeats what matters, because
  "the reader who needs it most never hovers". A marker comment on the same line as the text makes the
  markdown render raw: put it on its own line.
- Say plainly what a panel does not show ("every pod holds the same data, not how queries are
  spread"). [Lab]

The worked example has a description on all 29 panels and no captions. `percli` 0.54.0 converts a Grafana text
panel to a Perses Markdown panel with its text (measured 2026-10-07), and `perses-dashboard` keeps it: it refuses a
Markdown panel only where the Grafana panel was not a text panel.

## 8. Grow it, and keep one source [T§5]

- **Add a variable, not a copy** (`cluster`, then `namespace`), repeat a row per value, link the
  dashboards together. A dashboard shipped by a Helm chart for one release instead carries tokens
  (`__NAMESPACE__`, `__SEARCH__`) that the chart replaces. [Lab]
- **Generate, do not hand-edit.** A generator (`build.py` in the tutorial) is idempotent, diffable and
  reviewable; a JSON export from the UI is none of those. The worked example has one Grafana JSON as
  its source, edited by hand and reviewed as a diff. [Lab]
- **Provision as code**: a ConfigMap labelled `grafana_dashboard: "1"` for the sidecar; a
  `PersesDashboard` for the console.
- **Version it** beside the code that produces the data, in the same pull request.

**Two forms from one source** [Lab]:

- The Grafana JSON is the only file edited. `perses-dashboard <grafana.json> <out.json> --datasource <name>`
  generates the Perses file: it runs `percli migrate` from the Perses image (`--image`, default
  `docker.io/persesdev/perses:v0.54.0`; use the Perses version inside the cluster's operator) with podman or
  docker, or a `--percli` binary with its unpacked `--plugins`. It writes the dashboard's spec, the value of a
  `PersesDashboard`'s `spec.config`, and writes nothing when a check fails. Both files are committed together.
- It refuses: a panel that became a placeholder; a panel, section or query that differs from the source, taken
  in order; a stat that shows its series' name and whose legend is neither one label (`{{node}}`) nor two as
  `{{who}}: {{what}}`, the same on every query (a fixed text, `__auto`, three labels: Perses shows one label); a
  stat on a table query whose `reduceOptions.fields` is not one field (`version` or `/^version$/`) but a pattern
  (`/.*/`, or `/version/`, which Grafana searches every field's name for), the time, or the value of one query among
  several; a stat that shows its series' name with no legend to take it from; a pie with a colour for some of its queries only; a colour Perses cannot take. It warns when a Grafana unit became
  a plain number, and when a table's default unit was dropped (`percli` carries a table's units column by column).
- **Write the source so that it converts** (measured on a second dashboard, `examples/dashboard-ipsec-nas/`):
  a stat that shows a label takes the legend `{{what}}`, or `{{who}}: {{what}}`, which becomes the series name
  and the label shown; a count of days takes the unit `suffix: days`, which becomes the Perses unit `days`
  (likewise `milliseconds`, `seconds`, `minutes`, `hours`, `weeks`, `months` and `years`, spelled so); and a table of several queries gives every query the **same labels** (`max by (node) (...)`):
  a Perses table joins rows by all their labels, so one query labelled `node, pod` splits each node into two
  rows. What carries other labels goes in a table of its own.
- The command reproduces the worked example's committed Perses file from its Grafana file, key for key
  (2026-10-07).
- `percli` 0.54.0 carries over, measured by running it alone: each query's fixed colour, fill opacity
  and line style (as `querySettings`), stacking, an axis minimum and maximum, units, and value mappings
  on a table column.
- The command adds: the datasource name on every query and on every variable that asks Prometheus; from the
  Grafana source, a pie's `colorPalette` in the
  order of its queries, its labels off, and a table's mappings by pattern; a table's text colour, and its label
  columns before its value columns; a stat's label from its legend, and its series name when the legend has two
  labels; a unit of time from `suffix: <unit>`, whether or not the panel sets decimals; and it drops the `null` bound of an open-ended range. (`percli` hides the time column
  itself.)

## 9. Prove it, then show it

1. **Tests beside the chart**: panel and section counts, the first panels still present, every colour,
   shade, line style, legend position and table cell, in both files. Mutate one value and watch the
   test fail before trusting it. [Lab]
2. **Every query through the real data source, not your eyes**: all `success`, no warning or notice,
   the series count, the time one refresh takes. List the queries that return nothing and say why each
   is expected. "A dashboard that says No data in a screenshot nobody looked at is a dashboard that
   lies." [T§5] [Lab]
3. **Where the reader looks**: the OpenShift console as a viewer holding only the viewer roles, in both
   themes, and a Grafana that loads the ConfigMap through its sidecar, installed for the measurement and
   removed after. No "No data", "NaN", "Forbidden", warning sign or panel error. The worked example's
   [`scripts/capture-console-dashboard.py`](https://github.com/ephico2real2/mongodb-poc/blob/main/scripts/capture-console-dashboard.py)
   and [`test/grafana-sidecar/`](https://github.com/ephico2real2/mongodb-poc/tree/main/test/grafana-sidecar) do both; they are not in
   the kit yet. [Lab]
4. **Open the captures and read them.** A cut legend, a brown block, a tiny number and a fractional
   axis on a count were each found only there. Then check that the object on the cluster equals the
   chart's rendering: a trial `oc patch` leaves fields behind. [Lab]
5. **Send the owner a screenshot after every visual change**, the dark console first, a crop of what
   changed and the whole page. Taste is decided from the picture, not from a description. [Owner]
6. **Documents** embed the light capture, as a few section pictures cut from one capture of the whole
   page; the alt text states the readings in it; every number quoted (queries, seconds, contrast) was
   measured, with the date. [Owner] [Lab]

## 10. Where the sources pull apart, and what this standard does

| Question | One source | Another | This standard |
| --- | --- | --- | --- |
| Is a pie ever right? | [Grafana]: "ideal when you have data that adds up to a total" | [Few]: "by far the least effective"; bars compare magnitudes better | One pie for "share now", few slices, always beside the number and the share over time (section 2) |
| A share over time | [Few]: a line of percentages; a stacked area is hard to read above the bottom band | [Owner]: unstacked, even traffic is one line and a brown shade | Stack to 100%, values on hover (section 5) |
| Green and red | [T§3] and convention: Running green, Failed red | [Stone]: off red-green for colour-vision deficiencies | Keep them for states, never as the only carrier (section 4) |
| A palette by name | [T§3]: the right default for a time series whose series come and go | [Lab]: the colours Perses made from the names were too alike | Fixed colours for a small known set; by-name only in Grafana, for an open-ended one |
| The rate window | [T§2]: `$__rate_interval` | [Lab]: a fixed `[5m]`, not measured in Perses otherwise | Section 3 |
| Captions | [T§4]: a caption under every panel | [Lab]: descriptions only | Captions in Grafana; measure the conversion before a dual dashboard (section 7) |
| The source of a dashboard | [T§5]: a generator | [Lab]: one Grafana JSON, edited by hand | Either; never an export from the UI, never the generated file (section 8) |
| A state over time | [T§1]: a state timeline | [Lab]: a state timeline becomes a placeholder in Perses 0.54.0 | Status history (section 2) |
