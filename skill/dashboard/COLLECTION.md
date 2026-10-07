# Where the metrics come from: the layout before any panel

A panel can only draw what a Prometheus has scraped. Before the inventory of `SKILL.md` section 1 there is a
shorter question: is the workload's data collected at all, and what does it take? Work down this page in order;
each step ends in something you can measure.

| Tag | Source |
| --- | --- |
| **[PO]** | Prometheus Operator: [design](https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/getting-started/design.md), and the field descriptions of its CRDs, read with `oc explain` on OpenShift 4.22.7 (operator 0.90.1), 2026-10-07 |
| **[OCP]** | Red Hat, [Configuring user workload monitoring](https://docs.redhat.com/en/documentation/monitoring_stack_for_red_hat_openshift/4.18/html-single/configuring_user_workload_monitoring/index), 4.18, sections 1.2.1 and 4.3. The quotes are from the source of those pages in [openshift-docs](https://github.com/openshift/openshift-docs/tree/main/modules), read 2026-10-07: `monitoring-specifying-how-a-service-is-monitored.adoc`, `monitoring-example-service-endpoint-authentication-settings.adoc`, `customize-certificates-add-service-serving.adoc` |
| **[Prom]** | Prometheus, [Writing exporters](https://prometheus.io/docs/instrumenting/writing_exporters/) |
| **[ipsec]** | [openshift-ipsec-nas](https://github.com/ephico2real2/openshift-ipsec-nas): the chart `charts/ipsec-nas-option-c-metrics`, `docs/60-monitoring-per-node.md`, `docs/61-perses-dashboard-review.md`. Measured on OpenShift Local 4.22.7, one node |
| **[gsd]** | [group-sync-dashboard](https://github.com/ephico2real2/group-sync-dashboard): `charts/group-sync-dashboard/templates/monitoring.yaml`, `report-networkpolicy.yaml`, `charts/openshift-grafana/templates/21-datasource.yaml` |
| **[mongo]** | [mongodb-poc](https://github.com/ephico2real2/mongodb-poc): `chart/mongodb-search-helm/templates/30-monitoring.yaml`, `values.yaml`, the chart's README |
| **[cilium]** | [cilium-implementation-poc](https://github.com/ephico2real2/cilium-implementation-poc): `demos/18-obi/30-podmonitor.yaml`, `demos/20-springboot/40-monitoring.yaml`, `docs/GOTCHAS.md` |
| **[coo]** | [openshift-coo-helm](https://github.com/ephico2real2/openshift-coo-helm): `docs/manual-install-findings.md`, the chart's README and values |

A version named is where the statement was read or measured.

## 1. Does the workload emit what the question needs?

Read its metrics page before anything else: `curl` it from a pod in the namespace or through a port-forward, save
it, and run `metrics-inventory --text <the page>`. Three outcomes:

- **It emits it.** Go to section 3. Most servers do: mongot serves 1,024 names on its own port, Envoy 487 on its
  admin port. [mongo]
- **It emits it under a name or a type that will mislead.** A counter without `_total`, a label holding a user
  name. Fix it at the scrape, section 7.
- **It emits nothing, because nothing in the cluster knows the answer.** The state lives in the node's kernel, in a
  host file, or behind a command line. You need an exporter of your own: section 2.

## 2. An exporter of your own, when nothing emits the answer

The case in hand is IPsec between nodes and a NAS. Its state is in the host's libreswan, its NSS database and the
kernel, and "Option C itself installs no pod, so without it there are no metrics." [ipsec] What that repository
built, and what to copy from it:

- **Two containers in one pod, one privilege each.** A `collector` that reads the host: privileged, root, the
  host's `/` mounted read-only at `/host`; "It only reads: nothing on the host is changed." It writes a metrics
  file every 30 seconds. A `metrics` container that serves that file on port 9754: "Unprivileged: the only network
  listener in this pod has no access to the host." [ipsec]
- **A DaemonSet when the state is per node**, so every node reports its own, under its own name. [ipsec]
- **Fail the scrape when there is no data.** The server answers 503 when the file cannot be read: "503 makes the
  scrape fail, which is what should happen while there is no data". A page of stale or empty numbers answered 200
  would look healthy. [ipsec]
- **Say when the data was taken.** `ipsec_nas_collect_success` and `ipsec_nas_collect_timestamp_seconds` report
  the collector itself. This matters because the collector runs on its own timer, where Prometheus asks that
  "Metrics should only be pulled from the application when Prometheus scrapes them, exporters should not perform
  scrapes based on their own timers." [Prom] A file written by a privileged reader and served by an unprivileged
  one is the reason for the timer; the timestamp is what makes its staleness visible.
- **Name the metrics as Prometheus asks** [Prom]: one prefix for the exporter (`ipsec_nas_`); `snake_case`; base
  units ("Metrics must use base units (e.g. seconds, bytes)"); `_total` on counters (`ipsec_nas_tunnel_in_bytes_total`);
  a time as `_timestamp_seconds`; facts as an `_info` series (`ipsec_nas_tunnel_info`); few labels
  ("every extra label is one more that users need to consider when writing their PromQL").
- **Let Prometheus name the node**, not the exporter: a relabelling copies `__meta_kubernetes_pod_node_name` to
  `exporter_node`, "set by Prometheus and not by the collector", and an alert compares the two. [ipsec]
- **What it costs.** The privileged SecurityContextConstraint for the collector's ServiceAccount, and a namespace
  labelled `pod-security.kubernetes.io/enforce=privileged`. Ask whether an unprivileged read would do before
  taking this shape. [ipsec]
- **Prove the alerts without a cluster**: `promtool test rules` on the rule file, with the rule "Every alert must
  fire for its node and only that node". [ipsec]
- **Measured**: on OpenShift Local 4.22.7, "first up=1 … (80 s after install)", 41 series. Not validated there: a
  cluster with several nodes, and a tunnel actually down. [ipsec]

Before writing one, check that no maintained exporter already reads the same state; the repositories above record
no such search for IPsec, so that question is open there.

## 3. A ServiceMonitor or a PodMonitor

Both tell a Prometheus what to scrape. What differs is what they select:

- "The `ServiceMonitor` CRD defines how a dynamic set of services should be monitored. A `Service` object
  discovers pods by a label selector and adds those to the `EndpointSlice` or `Endpoints` object. The
  `ServiceMonitor` object discovers those `EndpointSlice` or `Endpoints` objects". [PO]
- "The `PodMonitor` CRD defines how a dynamic set of pods should be monitored. The `PodMonitor` object discovers
  these pods". [PO]
- "The former requires a `Service` object, while the latter does not, allowing Prometheus to directly scrape
  metrics from the metrics endpoint exposed by a pod." [OCP], of the ServiceMonitor and the PodMonitor

Either way **each pod is its own target**: "A ServiceMonitor scrapes endpoints, not the Service's address, so each
pod is its own series." [mongo] A scrape is never load-balanced across replicas, which is what a per-pod panel
needs.

| Use | When | Seen in |
| --- | --- | --- |
| **ServiceMonitor**, the default | A Service for the metrics port exists, or adding one is harmless | [mongo], [ipsec], [gsd] |
| **PodMonitor** | No Service makes sense: "hostNetwork pods, no Service needed"; or several workloads share one monitor by a pod label | [cilium] demos 18 and 20 |

What to get right:

- **Ports are named.** A ServiceMonitor's `port` is "the name of the Service port"; a PodMonitor's is the pod's
  port name, and "If the pod doesn't expose a port with the same name, it will result in no targets being
  discovered." [PO] A monitor that names a port nothing declares is created without error and scrapes nothing.
- **A Service only for metrics is fine, and stays inside.** Envoy's admin port got a ClusterIP Service for its
  ServiceMonitor: "ClusterIP only; never give it a Route." [mongo] For one endpoint per node, a headless Service:
  "one endpoint per node; nothing load-balances metrics". [ipsec]
- **Same namespace on OpenShift.** "A `ServiceMonitor` resource in a user-defined namespace can only discover
  services in the same namespace. That is, the `namespaceSelector` field of the `ServiceMonitor` resource is
  always ignored." [OCP]
- **The path and the interval are part of the contract**: `/metrics` by default, `/stats/prometheus` for Envoy,
  `/actuator/prometheus` for Spring Boot; 15 or 30 seconds in every chart here. A rate window must cover at least
  four scrapes (`SKILL.md` section 3).

## 4. Does the scrape need TLS, or a credential?

Find out what the metrics port speaks before writing the monitor: `curl` it both ways from inside the namespace.

**Plain HTTP, nothing to set.** mongot's port, Envoy's admin port and the IPsec exporter's are HTTP: their monitors
set no `scheme` and no `tlsConfig`, and are scraped. [mongo] [ipsec]

**The port speaks TLS only.** This is the case that fails without a sign. A Service port that leads to an
oauth-proxy, or to a server with a serving certificate, answers TLS; and "the default `http` scheme fails the
handshake on EVERY scrape — silently, while the Service and the ServiceMonitor both look correct." [gsd] What it
takes on OpenShift:

```yaml
endpoints:
  - port: http
    scheme: https
    tlsConfig:
      ca:
        configMap:
          name: openshift-service-ca.crt     # in every namespace, key service-ca.crt
          key: service-ca.crt
      serverName: <service>.<namespace>.svc  # the name on the certificate
```

- **The certificate** comes from the service CA: annotate the Service with
  `service.beta.openshift.io/serving-cert-secret-name`, and "The generated certificate is only valid for the
  internal service DNS name `<service.name>.<service.namespace>.svc`". [OCP]
- **`serverName` is not optional.** Prometheus dials the pod's IP, and the certificate names the Service.
  "`serverName` sets the name that is VERIFIED independently of the address dialled, which is what it is for."
  Measured there with `curl --cacert … --resolve <service>:8443:<pod IP>`: 200 with the CA, refused without. [gsd]
- **The CA is already in the namespace.** The ConfigMap `openshift-service-ca.crt`, key `service-ca.crt`, exists
  in every namespace (read on the lab namespace, annotated `service.beta.openshift.io/inject-cabundle: "true"`),
  and "the Prometheus Operator resolves a configMap reference against the ServiceMonitor's OWN namespace", so
  nothing is copied. [gsd]
- **Not `insecureSkipVerify`**, which "defines how to disable target certificate validation" [PO]: the block above
  verifies.
- **A headless Service changes the certificate**: it "also contains a wildcard subject", and "you must not use the
  service Certificate Authority (CA) if your client must differentiate between individual pods." [OCP]
- **This block is OpenShift's.** A cluster without the service CA has neither that ConfigMap nor the certificate:
  there the CA comes from wherever the server's certificate does, as a ConfigMap or a Secret in the monitor's
  namespace. [gsd]

**The endpoint asks for a credential.** [OCP] gives three ways, each from a Secret in the monitor's namespace:
`authorization.credentials` for a bearer token, `basicAuth`, `oauth2`. And one prohibition: "Do not use
`bearerTokenFile` to configure bearer token. If you use the `bearerTokenFile` configuration, the `ServiceMonitor`
resource is rejected." The same reasoning applies to `tlsConfig.caFile`, which is "the path to the CA cert in the
Prometheus container" [PO]: name a ConfigMap or a Secret, not a file. A client certificate for the scrape is
`tlsConfig.cert` and `tlsConfig.keySecret`. [PO]

**Or leave metrics outside the login, and keep them harmless.** With an oauth-proxy in front, the metrics path was
put in its skip list, so "No credential is needed", which "is also why the exporter emits counts and states only,
never a group or user name." [gsd] Whatever is scraped without a credential must be safe to read.

Not measured in any repository above: a scrape with a bearer token, with Basic authentication, with OAuth 2.0 or
with a client certificate. The fields are documented; measure before relying on them.

## 5. What the platform needs first

- **OpenShift: user workload monitoring on.** `enableUserWorkload: true` in the ConfigMap
  `cluster-monitoring-config`, namespace `openshift-monitoring`. [OCP] Without it "the objects are created and
  nothing scrapes them." [mongo] Check: pods in `openshift-user-workload-monitoring`.
- **The right to create a monitor**: `cluster-admin` or the `monitoring-edit` role in the namespace. [OCP]
- **A NetworkPolicy must let Prometheus in.** Admit the Prometheus pods of `openshift-user-workload-monitoring`
  (and `openshift-monitoring` when the platform Prometheus scrapes), by namespace and by pod label together: "a
  namespaceSelector alone would admit EVERY pod in those namespaces". [gsd]
- **The platform's own Prometheus** scrapes a namespace only when it is labelled
  `openshift.io/cluster-monitoring: "true"`: for operators, not for applications. [coo]
- **Another Prometheus Operator** selects monitors by label. With kube-prometheus-stack's default, monitors without
  the release's label "would have appeared in `kubectl get servicemonitor` and never in Targets"; the fix there was
  `serviceMonitorSelectorNilUsesHelmValues: false` and its PodMonitor twin. [cilium]
- **The CRDs must exist** before a chart renders a monitor; a chart applied to a cluster without them fails with
  "no matches for kind PodMonitor". [cilium]

## 6. Who can read what was collected

Collection is half of it; a dashboard reads through a query endpoint, with someone's credential.

- **Perses and Grafana send the viewer's own token** to Thanos Querier, so "Every viewer sees exactly what
  OpenShift lets them see." [coo]
- **Port 9091 is cluster-wide** and needs `cluster-monitoring-view`. **Port 9092 is per namespace**, and it "checks
  a `POST` as `create pods` in the namespace": a reader with `view` is refused on every panel, because the Perses
  UI posts its queries. [ipsec] In Grafana the same port works with `httpMethod: GET` and a `namespace` parameter.
  [gsd]
- **The data source needs the CA.** A Perses datasource must name the secret that holds it: "Without it: `x509:
  certificate signed by unknown authority`." [coo]
- Decide this with the data in mind: the IPsec dashboard chose 9091 because its metrics "contain **no PHI and no
  PII**". [ipsec]

## 7. Names and labels, fixed at the scrape

- **A counter ends in `_total`.** Through Thanos Querier, `rate()` on another name is answered with the notice
  "metric might not be a counter, name does not end in _total/_sum/_count/_bucket", and the panel shows a warning
  sign. Rename it with `metricRelabelings`, and know the cost: "those two panels start again from the upgrade: the
  earlier samples stay under the old names". [mongo]
- **Labels a dashboard needs are stamped at the scrape**: the node, the cluster. [ipsec] [cilium]
- **A label the workload sets can collide with a target's**: Micrometer's `application` "becomes
  exported_application, honor_labels is off". [cilium]
- **A restart starts a new series**: "a collector pod restart starts a new series, and changes() counts within one
  series only". Write alerts and panels that survive it. [ipsec]
- **Identities stay out**: counts and states, never a user or a group name. [gsd]

## 8. Prove the collection before drawing

1. `up{namespace="…",job="…"}` is 1 for every pod, and how long after install the first one came (80 s on the
   lab). [ipsec] Targets that "read `0` for a while" after a rollout are not a fault. [mongo]
2. `count({namespace="…",job="…"})`: the number of series is the one the metrics page has.
3. With TLS: the same `curl` Prometheus makes, to the pod's IP with the Service's name and the CA, answers 200; and
   without the CA it is refused. [gsd]
4. Then the inventory: `metrics-inventory --prometheus <url> --match '{namespace="…",job="…"}'`.
