---
name: envoy
description: Make Envoy the first witness of every request, for logging and tracing. It covers the facts to learn about the app first. Then one trace ID goes from the client through each Envoy to the service, and each access line has two copies. It also covers the Envoy metrics, the masking and sampling in the OpenTelemetry Collector, and the stores VictoriaLogs, VictoriaTraces and VictoriaMetrics. It ends with the read-back by trace ID that proves the work. Use when the user types /envoy. Also use it to add or change Envoy tracing, access logs or Envoy metrics, rate-limit refusals in the logs, or abuse signals from Envoy records. Also use it to join Envoy records to the application logs and spans, or to answer why a request was refused.
---

# /envoy: every request has a witness, and one trace ID joins them

`/envoy <what to build or change>` starts with the app, not with the Envoy configuration. If the app cannot answer a
question of section 1, ask it.

Proven on a mobile and web platform with two Envoys in front of an API (2026-11-16). One run sent 29 sign-ins through
an edge Envoy, an inner Envoy and two API replicas. For each request, one trace ID found the access line of each Envoy,
the API log lines and the span of each hop. Each Envoy added 2 ms or less to 28 of the 29 requests. A search of both
stores for the test password, email address and token found 0 matches. Every rule here comes from that work, or from
a defect that the work found.

## 1. Learn the app first

The Envoy configuration copies facts about the app. If one fact is wrong, a record is wrong or a secret leaks. Find
each fact in the code, with the file and line, before you write any configuration.

| Fact | Why Envoy needs it | Where to find it |
|---|---|---|
| The hops, in order: load balancer, edge Envoy, inner Envoy, service replicas | Each hop makes one server span. On a cloud host with a managed load balancer, there is often no edge Envoy, and the inner Envoy makes the first span | The deploy files of each environment |
| Which hop sees the client address | `xff_num_trusted_hops` on the inner Envoy counts the trusted proxies in `X-Forwarded-For`. One wrong number puts the proxy address in every record | The load balancer configuration |
| Does the client send `traceparent`, and a new one for each attempt? | A client span then becomes the parent of the Envoy span, and a retry gets its own trace | The HTTP client of the app |
| How the service signs its tokens | An asymmetric key with a JWKS route lets Envoy verify a token and record its subject. A shared secret must never be in an Envoy file, so Envoy then cannot know the caller | The auth module of the service |
| The header that names the device | A device key finds abuse from many addresses. Store a keyed pseudonym of it, never the raw value | The HTTP client of the app |
| Which routes carry a secret in the query string | A query can hold a token, so the access line keeps only the path | The routes of the service and its links in emails |
| Which values in a log line are personal data | The collector must mask each kind: email, phone number, card number, national ID numbers of the country | The log calls of the service |
| The business routes and the health routes | Every business call is traced in full. Only a successful health or metrics `GET` can be sampled | The router of the service |
| The routes that Envoy refuses itself | A rate-limit refusal or an auth refusal at Envoy never reaches the service. Only the Envoy record shows it | The Envoy filters and routes |
| Where each container writes stdout | The stdout copy of the access line goes there: a host folder locally, the cloud log service on a host | The compose files or the log driver |

## 2. Trace every request

Put this in each `HttpConnectionManager`. It makes Envoy join the trace that the caller sends, or start one, and send
its own span as the parent of the next hop.

```yaml
generate_request_id: true
request_id_extension:
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.request_id.uuid.v3.UuidRequestIdConfig
    use_request_id_for_trace_sampling: false
tracing:
  random_sampling: { value: 100 }
  provider:
    name: envoy.tracers.opentelemetry
    typed_config:
      "@type": type.googleapis.com/envoy.config.trace.v3.OpenTelemetryConfig
      grpc_service:
        envoy_grpc: { cluster_name: otel_collector_grpc }
        timeout: 1s
      service_name: <one name for each hop>
      sampler:
        name: envoy.tracers.opentelemetry.samplers.trace_id_ratio_based
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.tracers.opentelemetry.samplers.v3.TraceIdRatioBasedSamplerConfig
          sampling_percentage: { numerator: 100, denominator: HUNDRED }
```

- Give each hop its own `service_name`, so that a trace shows which Envoy took how long.
- Keep `use_request_id_for_trace_sampling: false`. In Envoy 1.39, the tracer turns off each span that the connection
  manager did not select, also a span whose `traceparent` has the sampled flag `01`. With this setting the connection
  manager selects every request, and the sampler makes the only decision.
- Sample 100% at Envoy. The collector decides what to drop (section 6), because only it can see the route and the
  status of the whole trace.
- A timeout of 1 s on the collector call means that a collector outage drops spans. It never holds a request.

## 3. Write each access line twice

Each Envoy writes the same fields to two loggers:

- `envoy.access_loggers.stdout` with a `json_format`. If the collector is down, this copy stays. The container log
  driver sends it to the host or to the cloud log service.
- `envoy.access_loggers.open_telemetry` with a `log_name` (for example `envoy-access`) and a `service.name` resource
  attribute. Envoy sets the `trace_id` and `span_id` of this record from the active span. The record is then in the
  same store as the service log lines, and one query finds both.

The fields, the same in both copies:

| Field | Operator | Why |
|---|---|---|
| `time` | `%START_TIME%` | The order of events |
| `request_id` | `%REQ(X-REQUEST-ID)%` | The ID that the service also logs |
| `client` | `%DOWNSTREAM_REMOTE_ADDRESS_WITHOUT_PORT%` | The address after the trusted hops |
| `forwarded_for` | `%REQ(X-FORWARDED-FOR)%` | The chain, for a question about the trusted hops |
| `method`, `path` | `%REQ(:METHOD)%`, `%REQ_WITHOUT_QUERY(:PATH)%` | The path without its query, because a query can hold a token. It needs the `envoy.formatter.req_without_query` formatter |
| `status`, `flags` | `%RESPONSE_CODE%`, `%RESPONSE_FLAGS%` | `RL` is an Envoy rate-limit refusal, `UF` a failed connection to the next hop, `-` no flag |
| `details`, `upstream_failure` | `%RESPONSE_CODE_DETAILS%`, `%UPSTREAM_TRANSPORT_FAILURE_REASON%` | The cause of a 503 or a refusal that Envoy made itself. Three different refusals show three different `details` values |
| `route` | `%ROUTE_NAME%` | It is `-` for a route with no `name`. Name every route |
| `upstream` | `%UPSTREAM_HOST%` | Which replica answered |
| `duration_ms`, `upstream_ms` | `%DURATION%`, `%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%` | The difference is the time of this Envoy |
| `bytes_in`, `bytes_out`, `user_agent` | `%BYTES_RECEIVED%`, `%BYTES_SENT%`, `%REQ(USER-AGENT)%` | Size and client |
| `trace_id`, `span_id` | `%TRACE_ID%`, `%SPAN_ID%` | In the stdout copy only. The OpenTelemetry record has them as its own fields |

Never log a request header that holds a credential: `Authorization`, a cookie, an API key.

### Identity in the record

A record that names only an address cannot find an attack from many addresses. Add identity in this order, and
measure each step before you write it as done:

1. If Envoy verifies the token (`jwt_authn` with the JWKS of the service and `payload_in_metadata`), log the verified
   subject from the dynamic metadata. If the service stays the authority, use `allow_missing_or_failed`. Never put a
   claim from a token that Envoy did not verify in a record. Test the operator on your Envoy version before you rely
   on it.
2. If the app sends a device header, store a keyed pseudonym of it (an HMAC with a key from the secret store), never
   the raw value. A plain hash of a short ID can be reversed by a table of all IDs.
3. Never take a key for a rate limit or a record from a header that the client controls, unless an earlier hop
   verified it.

## 4. Metrics: one scrape for each Envoy

- Scrape the admin `/stats/prometheus` route of every Envoy, the edge too. A filter that refuses calls at the edge
  (`ext_authz`, a local rate limit) counts its refusals only there.
- Keep the admin listener off the public network. Bind it to the container network, and scrape it from the collector.
- Counts for each address or each customer go to the log store, never to the metric store. One series for each
  address fills a time-series store.
- Draw each rate-limit bucket on the dashboard (`/dashboard` skill). A bucket that is not drawn is not watched.

## 5. The stores: VictoriaLogs, VictoriaTraces, VictoriaMetrics

| Signal | Store | Read it with |
|---|---|---|
| Access records and service log lines | VictoriaLogs, OTLP in | LogsQL on `/select/logsql/query`: `_time:30m trace_id:="<id>"` |
| Spans of every hop | VictoriaTraces, OTLP in | The Jaeger query API: `/select/jaeger/api/traces/<id>` |
| Envoy and service counters | VictoriaMetrics, from the collector scrape | PromQL, through Grafana or `/api/v1/query` |

- All three take OTLP from one collector, so each Envoy and each service sends to one address and does not know the
  stores.
- A trace is in VictoriaTraces about 20 seconds after its request. A read-back waits for the last trace first.
- If the cloud provider gives managed stores, send a second copy there by configuration. Keep the self-hosted stores as
  the first copy, so that the queries are the same in every environment.

## 6. The collector masks and samples before any store

Masking runs before each exporter, in every pipeline:

- Spans: replace each query value in `http.url`, `url.full`, `http.target` and `url.query` with `REDACTED`, and keep
  the query keys (the OpenTelemetry URL conventions do the same).
- Log text: an OTTL `transform` with `replace_pattern` for JSON Web Tokens, bearer values, named secrets
  (`password=`, `"token":`), one-time codes in a sentence, email addresses, phone numbers and long numbers.
- Log and span attributes: the `redaction` processor with blocked key patterns and blocked values.
- Telemetry from a client (a phone) is a claim from an untrusted source. The app can mask it first.
  Mask it again in the collector, and mark it with a resource attribute such as `telemetry.source=phone`.

Sampling keeps every business span. Only a successful `GET` or `HEAD` server span of a fixed list of infrastructure
routes (health, metrics) can go to a probabilistic sampler. Keep the fixed list in the source as a safety bound, and
let an environment setting only make it shorter.

## 7. Prove it: read each case back by its trace ID

A configuration that passes `envoy --mode validate` can still lose a trace. The proof is a run:

1. Send one request for each case that the route distinguishes: success, each refusal by the service, each refusal by
   Envoy, a missing field. Save the trace ID of each.
2. For each trace ID, read VictoriaLogs and VictoriaTraces. Each case must show one access line from each Envoy, the
   service lines, and one server span for each hop.
3. Make sure that the parent chain is correct: the first Envoy span is a child of the client span, and each next span is a child of the one
   before it.
4. Read the time of each hop from `duration_ms` minus `upstream_ms`, and from the spans.
5. Search both stores for each secret of the test (the password, the email address, the token). Each search must find 0.
6. Write the commands and their output in the document, so that the next reader can run them again.

```sh
show() {
  curl -s "$LOGS" --data-urlencode "query=_time:30m trace_id:=\"$1\"" | jq -r '
    if .log_name == "envoy-access"
    then "  log   \(."service.name")  \(.method) \(.path) \(.status) flags=\(.flags) total=\(.duration_ms)ms upstream=\(.upstream_ms // "-")ms"
    else "  log   \(."service.name")  \(.severity_text) \(._msg | split("\n")[0] | .[0:110])" end'
  curl -s "$TRACES/$1" | jq -r '(.data // [])[0] // empty | . as $t
    | ($t.spans | sort_by(.startTime)[]
       | select(any(.tags[]; .key == "span.kind" and .value == "server"))
       | "  span  \($t.processes[.processID].serviceName)  \(.operationName)  \(.duration / 1000 | floor)ms"),
      "  spans in all: \($t.spans | length)"'
}
```

## 8. What the work found

Each item was a defect or a gap on the platform where this was built. Look for each one in a new app.

| Found | Fix |
|---|---|
| A sampled `traceparent` from the client still gave no Envoy span | `use_request_id_for_trace_sampling: false` and the sampler at 100% (section 2) |
| A 429 from an Envoy rate limit left a line only in the host files | The OpenTelemetry access logger, so the refusal is in the log store with a trace ID |
| A 503 that Envoy made itself did not say why | `details` and `upstream_failure` in both copies |
| Every edge record showed the route `-` | A `name` on each route |
| The edge Envoy was not scraped, so its refusals were counted nowhere | A scrape job for each Envoy |
| The span URL kept a token from the query string | The query mask in the collector (section 6) |
| A wrong password and an unknown account got the same answer in the same time, but the spans showed different work | Correct by design: the trace store is internal. Keep it off any client network |

## Sources

- Envoy access log operators: https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage
- Envoy OpenTelemetry access logger: https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/access_loggers/open_telemetry/v3/logs_service.proto
- Envoy OpenTelemetry tracer: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/trace/v3/opentelemetry.proto
- Envoy headers (`X-Forwarded-For`, `x-envoy-upstream-service-time`): https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_conn_man/headers
- W3C Trace Context: https://www.w3.org/TR/trace-context/
- OpenTelemetry URL attributes: https://opentelemetry.io/docs/specs/semconv/registry/attributes/url/
- Collector redaction processor: https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/redactionprocessor
- VictoriaLogs LogsQL: https://docs.victoriametrics.com/victorialogs/logsql/
- VictoriaTraces: https://docs.victoriametrics.com/victoriatraces/

## Anti-patterns

| Do not | Do |
|---|---|
| Write the Envoy file before you read the app | Fill the table of section 1 first, with file and line |
| Sample at Envoy | Trace 100% at Envoy, sample infrastructure routes only in the collector |
| Log only to stdout | Write the stdout copy and the OpenTelemetry copy |
| Log `%REQ(:PATH)%` | Log `%REQ_WITHOUT_QUERY(:PATH)%` |
| Put a shared signing secret in Envoy to read the caller | Use an asymmetric key and a JWKS, or leave identity to the service |
| Store a raw device ID or an address count in the metric store | A keyed pseudonym, and counts in the log store |
| Call it done after `envoy --mode validate` | Read each case back by its trace ID, and search for each secret |
