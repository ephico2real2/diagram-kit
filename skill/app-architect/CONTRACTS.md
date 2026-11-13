# Contracts first: what an application defines on day 1

Read this file for section 0 of `SKILL.md`, at the start of each design and each review. A contract is a statement
that two parties rely on: a client and the API, the API and its identity provider, the code and its database, a screen
and its endpoint. An application writes its contracts down before its code, and CI keeps each one true.

Each contract below has four parts:

- **The rule**, with the open standard that states it.
- **The check** that fails CI when the rule breaks. A contract with no check is a document, and a document drifts.
- **The artifact** and where it is in the repository.
- **The example**: the file of cmapi that does it, with the commit that added the file.

The example is [cmapi](https://github.com/ephico2real2/cmapi), read at commit `933274a` of `main` on 2026-11-13. cmapi
is the example, not the rule. Where cmapi differs from the standard, or has no check, the section says so.

Each standard and each tool was read on 2026-11-13. Section 16 lists the sources. Read each link again before a
recommendation depends on it, because the versions change.

## 1. The contract set

| No. | Contract | Open standard | The check | The artifact |
| --- | --- | --- | --- | --- |
| 3 | The API document | OpenAPI 3.1 or later, JSON Schema 2020-12 | The committed document is the served one. An undocumented route stops startup | `contract/openapi.json` |
| 4 | The breaking-change gate | The API document of the base branch and of the last release | A breaking change fails. The gate has its own test | `contract/gate.sh`, `contract/accepted-breaking.txt` |
| 5 | The changelog | The same comparison, between releases | The committed changelog is the one that the tool writes | `contract/released/<version>.json`, `changelog.json` |
| 6 | Recorded payloads | The `example` fields of OpenAPI | Each operation has a sample from a run, and its shape did not change | `contract/samples.json`, the examples document |
| 7 | The error registry | RFC 9457 | A route cannot declare or return a problem that is not registered | The registry in code, the problem responses in the API document |
| 8 | Write semantics | RFC 9110 and RFC 6585; the Idempotency-Key draft | A test for each refusal: 400, 409 or 422, 412, 428 | Shared parameters in the API document |
| 9 | Authorization | The security requirement of OpenAPI, or an `x-` extension | The declared permission is the enforced one, for each route | The role table in code, the permission on each operation |
| 10 | The identity provider | OpenID Connect, RFC 9068, RFC 8725, RFC 9700 | The shipped realm on a real identity provider gives each test identity the expected token | The realm as code, the claims table |
| 11 | The data model | The migrations and the catalog of the database | The data-model document is the schema of the migrated database | The migrations, the data-model document |
| 12 | The UI-to-API map | The mockup and the API document | Each row that says "built" names an operation of the API document | The map, one row for each action |
| 13 | Outbound integrations | The public documents of each provider | Contract tests against the mock and the sandbox | One port for each provider, one mock (`/mock-app`) |
| 14 | Events and webhooks | AsyncAPI, CloudEvents, the `webhooks` field of OpenAPI | The same gate as the API document | `contract/asyncapi.yaml` |

The number is the section of this file.

<!-- markdownlint-disable MD033 -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/contracts.dark.png">
  <source srcset="figures/contracts.light.png">
  <img alt="The contract set in four lanes. In the interface lane, the mockup gives the UI-to-API map, and the map, the error registry and the write rules give the API document. The gate, the changelog and the recorded payloads come from the API document. In the access lane, groups give roles, roles give permissions, and each operation of the API document has one permission. In the data lane, the migrations give the migrated database, and its catalog gives the data-model document. Outside, the documents of each provider define a port and a mock, and events have an AsyncAPI document." src="figures/contracts.light.png">
</picture>
<!-- markdownlint-enable MD033 -->

*The contract set in four lanes. The API document is the centre: the UI map, the problems and the write rules feed
it, each operation has one permission, and the gate, the changelog and the recorded payloads come from it. The figure
shows the standard, not one application.*

```text
The interface lane
  mockup --each action--> UI-to-API map --each endpoint--> API document (OpenAPI)
  API document --compared with the base branch and the last release--> breaking-change gate (accepted-breaking file)
  API document --one file for each release--> changelog
  API document + a run of the test suite --> recorded payloads --> examples in the API document and in the guide
  error registry (RFC 9457) --the problems of each operation--> API document
  write rules (Idempotency-Key, If-Match, dry run) --shared parameters--> API document

The access lane
  identity provider: users --> groups --> roles          (the provider owns these)
  application: roles --> permissions --> one permission for each operation --> API document
  provider contract: issuer, keys, audience, claims, clients, lifetimes --the token--> permissions

The data lane
  migrations --applied--> migrated database --read from the catalog--> data-model document
  data-model document: what each table holds, the rules that the schema holds, what the database does not hold, the caches

The outside lane
  each provider: its public documents --> port --> mock (/mock-app) --> contract tests
  events and webhooks, when the application has them: AsyncAPI document --> the same gate
```

## 2. Which comes first: the document or the code

The OpenAPI Initiative gives the rule for both cases on its best-practices page.

**A new application: design first.** Write the API document before the code. The page says: "in the opinion of the
OpenAPI Initiative (OAI), the importance of using Design-first cannot be stressed strongly enough. The reason is simple:
The number of APIs that can be created in code is far superior to what can be described in OpenAPI." On day 1, in this
order:

1. Write the UI-to-API map from the mockup (section 12). It gives the list of endpoints.
2. Write the API document by hand, with the problems, the write rules and the permission of each operation.
3. Lint the document, and commit it with the gate of section 4.
4. Start a mock server from the document, so that the UI and the clients build against it (`/mock-app` lists the tools).
5. Write the code. A test compares what the code serves with the document, and fails on a difference.

**An existing application: code first, with a committed and compared document.** The code generates the document. The
generated document is committed, a test keeps it equal to what the code serves, and the gate compares it with the base
branch. The same page permits this: "Regardless of your design approach (design-first or code-first) always keep a
single source of truth", and for two copies, "you can use a Continuous Integration test to ensure that the two sources
stay consistent."

**In both cases the document is a source file.** "OADs should be committed to source control, and, in fact, they should
be among the first files to be committed. From there, they should also participate in Continuous Integration
processes."

Code first has one known risk, which the same page states: the code can make an API that OpenAPI cannot describe. So
a code-first application refuses to start when a route has no full description (section 3), and the review reads the
generated document, not only the code.

**Example.** cmapi is code first. Its design is prose (`docs/01-design-and-architecture.md`, section "API
documentation": "The OpenAPI document is generated from the running code"). FastAPI generates the document,
`cmapi/contract/openapi.json` holds it (commit `3ea7aa1`), and the test
`test_the_committed_contract_is_the_document_this_code_serves` fails when the two differ
(`cmapi/tests/service/test_api_docs.py`, commit `3ea7aa1`).

## 3. The API document

**The rule.** One OpenAPI document describes each HTTP API. Each operation has an `operationId`, a summary, a
description, its parameters with a description and an example, its request and response schemas, its security
requirement and each error response. The schemas are JSON Schema: in OpenAPI 3.1 the Schema Object "is a superset of
the JSON Schema Specification Draft 2020-12". Use OpenAPI 3.1 or later. Version 3.2.1 (10 September 2026) is the latest.
Choose the newest version that each tool in the chain reads: the generator, the gate, the linter and the documentation
pages. The application serves the document, and the repository holds the same document.

**The check.**

- A test compares the committed document with the served one, and fails on a difference.
- The application refuses to start when a route has no summary, no description or no response model, when a parameter
  has no description or no example, or when a field of a model has no description.
- A linter (Spectral, with a ruleset of the project) fails on a rule of style: an operation with no `operationId`, a
  schema with no example, an inline schema.

**The artifact.** `contract/openapi.json` beside the code of the service, and the served copies at `/openapi.json` and
`/openapi.yaml`.

**Example.** cmapi's document is OpenAPI 3.1.0 with 31 operations (`cmapi/contract/openapi.json`, commit `3ea7aa1`).
Routes register through `DocumentedRouter`, and `check_documented` stops startup on a route that is not fully
described (`cmapi/src/cmapi/core/docs.py:115-171` and `:205-226`, commit `fd36e66`; called at
`cmapi/src/cmapi/main.py:88`). The tests are `test_an_undocumented_route_stops_startup`
(`cmapi/tests/service/test_api_contract.py`) and `test_a_parameter_without_a_description_or_an_example_stops_startup`
(`test_api_docs.py`). **Not done in cmapi:** the Spectral lint. `docs/01` designs it, and `.github/workflows/ci.yml`
has no step for it.

## 4. The breaking-change gate and the accepted-break file

**The rule.** A change must not break a client of the base branch, or a client of the last released version. A tool
decides what breaks, not a reviewer. An accepted break is one line in a file, with its reason and its issue number on
the line above. The gate has its own test: a known breaking change must fail, and a known added endpoint must pass. A
gate that passes each change proves nothing. Remove a field or an endpoint in two steps. First mark it
`deprecated: true` and send the `Deprecation` header (RFC 9745) and the `Sunset` header (RFC 8594). Remove it after the
sunset date.

**The tool.** oasdiff (Apache-2.0, v1.37.0 on 2026-11-08) has three levels: "`ERR` - Errors are definite breaking
changes which should be avoided", `WARN` for changes that it cannot confirm as breaking, and `INFO`. It reads OpenAPI
3.1: "oasdiff supports OpenAPI 3.1 specs across its commands." The gate is one command:

```sh
oasdiff breaking --fail-on ERR --err-ignore contract/accepted-breaking.txt <base document> <head document>
```

**The check.** The CI job runs the gate's own test, then the gate against the last released document, then, on a pull
request, the gate against the document of the base branch. Pin the tool by version and by SHA-256.

**The artifact.** `contract/gate.sh`, `contract/gate-test.sh` and `contract/accepted-breaking.txt`.

**Example.** `cmapi/contract/gate.sh` is the command above. `cmapi/contract/gate-test.sh` changes the committed
document three ways that must fail (a response loses a required field, an endpoint goes, a request body gains a
required field) and one way that must pass (a new endpoint and a new optional response field). The CI job
`api-contract` runs both, with oasdiff 1.37.0 checked against its SHA-256 (`.github/workflows/ci.yml:90-132`). All
three files came with commit `3ea7aa1`. `cmapi/contract/accepted-breaking.txt` holds no accepted change: its two lines
are comments.

## 5. The changelog

**The rule.** Each released version keeps its API document. The changelog is the difference between each release and
the release before it, written by the same tool as the gate, so that the two cannot disagree. Nobody writes the
changelog by hand. The application serves it to its users.

**The check.** CI writes the changelog again from the released documents and fails when the committed file differs.

**The artifact.** `contract/released/<version>.json`, one for each release, and the generated `changelog.json`.

**Example.** `cmapi/contract/changelog.py` writes `cmapi/src/cmapi/contract/changelog.json` with
`oasdiff changelog --format json`, and `--check` fails when the file is not current (commit `3ea7aa1`; the CI step is
"The changelog that /docs/changelog serves is current"). `gate-test.sh` tests the writer on two documents. **State on
2026-11-13:** cmapi has no released version. `cmapi/contract/released/` holds only `.gitkeep`, and `changelog.json`
is `{"releases": []}`.

## 6. Payloads recorded from a real run

**The rule.** No example in the API document or in a guide is written by hand. One scenario of the test suite calls
each operation on a running instance. A recorder keeps one request and one response for each operation, and one for
each problem code that the run meets. The samples go into the API document as its `example` fields, and a script
writes the examples guide from them. So the documentation pages, the guide and the tests show the same payloads. The
guide says where the run was: which database, which stand-ins, which date.

**The check.**

- The test fails when an operation has no sample.
- The test compares the shape of each sample (the keys and the types) with the committed file. Values such as IDs,
  times and entity tags change at each run, so the test does not compare them.
- The test fails when an operation returns a problem that its part of the document does not declare.
- The test fails when a sample holds a token. The recorder writes `Bearer $TOKEN` in its place.
- CI fails when the guide is not what the script writes.

**The artifact.** `contract/samples.json`, the `example` fields of the API document, and the generated part of the
examples guide between two marker lines.

**Example.** `cmapi/tests/service/test_api_samples.py` is the scenario and the recorder (commit `bcb8b9d`).
`cmapi/src/cmapi/contract/samples.json` holds 31 samples, for 30 of the 31 operations and one dry run, and 10
problems. The operation with no successful sample, `requests_revert`, has a recorded problem. `add_recorded_examples`
puts the samples into the document (`cmapi/src/cmapi/core/docs.py:353-377`). `scripts/api-examples-doc.py --check`
runs in the job `api-contract`, and `docs/04-api-examples.md` is its output. **The limits that cmapi states:** the run
used the test instance of the service suite, with a fake Git host and a fake cluster, on macOS. `docs/04` says: "No
payload here is from CRC or from kind yet." The run met 10 of the 48 registered problems.

A property-based tester such as Schemathesis generates requests from the document and finds the answers that the
document does not describe. It adds to the recorded run, and does not replace it. cmapi does not use one.

## 7. The error registry (RFC 9457)

**The rule.** Each refusal is a problem details object with the media type `application/problem+json`. One registry in
the code lists each problem type: its code, its status and an example. A route declares the problems that it can
return, and each one goes into the API document with its example. RFC 9457 gives the rules for the members:

- "Consumers MUST use the "type" URI (after resolution, if necessary) as the problem type's primary identifier."
- "If the type URI is a locator (e.g., those with an "http" or "https" scheme), dereferencing it SHOULD provide
  human-readable documentation for the problem type".
- The title "SHOULD NOT change from occurrence to occurrence of the problem".
- "Problem type definitions MAY extend the problem details object with additional members that are specific to that
  problem type." Put data for a program in an extension member, not in the text of `detail`.

**The check.**

- Registration fails when a route declares a problem that is not in the registry.
- A test fails when a run meets a problem that the operation does not declare (section 6).
- A test reads each entry of the registry: a status from 400 to 599, and an example.

**The artifact.** The registry in code, and the problem responses of each operation in the API document.

**Example.** cmapi's registry is `PROBLEMS`, with 48 codes (`cmapi/src/cmapi/core/docs.py:34-84`, commit `fd36e66`).
`DocumentedRouter._register` raises on an unregistered problem (`docs.py:132-134`). The class `Problem` writes the
body: `type`, `title`, `status`, `detail`, and the extension members `code` and `errors`
(`cmapi/src/cmapi/core/errors.py`, commit `72d082b`). **Where cmapi differs:** the `type` URI has a placeholder host
(`errors.py:9`), so it gives no documentation when a person opens it.

## 8. Write semantics: idempotency, conditional requests and the dry run

**The rule.** Three rules apply to each write, and the API document declares their headers and parameters once, as
shared parameters.

1. **A retry is safe.** Each write that is not idempotent takes an `Idempotency-Key` header. The same key with the same
   payload returns the first response again. The source is an IETF draft, not an RFC:
   `draft-ietf-httpapi-idempotency-key-header-08` (22 October 2026, expires 25 April 2027). It says: the key "MUST be
   unique and MUST NOT be reused with another request with a different request payload"; without the header "the
   resource SHOULD reply with an HTTP 400 status code"; for a key with a different payload "the resource SHOULD reply
   with an HTTP 422 status code"; for a retry "while the original request is still being processed, the resource
   SHOULD reply with an HTTP 409 status code"; and the resource "SHOULD define such expiration policy and publish it in
   the documentation." Read the draft again before each design, because a draft can change.
2. **A change does not overwrite a change that the caller did not see.** A read returns an `ETag`. A change sends it in
   `If-Match`. RFC 9110, section 13.1.1: "An origin server MUST use the strong comparison function when comparing
   entity tags for If-Match". An old tag gets 412 (RFC 9110, section 15.5.13). No `If-Match` gets 428. RFC 6585,
   section 3: "The 428 status code indicates that the origin server requires the request to be conditional. Its typical
   use is to avoid the "lost update" problem".
3. **A caller can ask what a write would do.** A dry run does each check and writes nothing. No IETF standard defines
   it. The Kubernetes API is the model: "Dry-run is triggered by setting the dryRun query parameter", and "dry-run
   requests will not be persisted in storage or have any other side effects."

**The check.** One test for each refusal: no key, a key with another payload, no `If-Match`, an old `If-Match`. One
test that a dry run writes nothing. One test that each curl sample of the document has the headers that its operation
declares.

**The artifact.** The shared parameters in the API document, and the rows of the examples guide that state each rule.

**Example.** cmapi declares the three once (`cmapi/src/cmapi/routers/__init__.py:19-65`). A write with no key gets 400
`idempotency-key-required`, and a dry run needs no key (`cmapi/src/cmapi/plugins/namespaces/router.py:41-48`). A key
is held for 24 hours by the clock of the database (`cmapi/src/cmapi/core/db/repo.py:49` and `:114-123`), and a unique
index holds one request for each key of a caller (`docs/16-data-model.md`, "The rules that the schema holds"). No
`If-Match` gets 428 and an old one gets 412 (`cmapi/src/cmapi/core/pipeline.py:184-188`). The recorded samples hold
the 400, the 412 and the 428. **Where cmapi differs:** a key with another payload gets 409 `idempotency-replay`
(`router.py:59-61`), and the draft says 422.

## 9. Authorization: group, role, permission, route

**The rule.** Access is one chain with four links, and each link has one owner and one file.

| Link | Owner | Where it is |
| --- | --- | --- |
| A user is in a group | The identity provider, from the directory | The directory |
| A group gives a role | The identity provider | The realm, as code |
| A role gives permissions | The application | One table in code, and a configuration file for each instance |
| A route needs one permission | The application | The route, and its operation in the API document |

Each operation of the API document carries its permission. OpenAPI has a field for it, the Security Requirement
Object: for OAuth 2 "the value is a list of scope names required for the execution", and "For other security scheme
types, the array MAY contain a list of role names which are required for the execution". Use it when the permission is
a scope of the token. When the application gets the permission from a role, the token has no such scope, so carry the
permission in an extension field: "The field name MUST begin with `x-`". The description of the operation says the
same thing in words.

**The check.**

- One test reads each route. It compares the permission that the document declares with the permission that the code
  enforces. It calls the route with no token (401) and with a role that lacks the permission (403).
- Startup fails when the configuration names a permission that the code does not know.
- A test for each limit that is not a permission: an environment, the caller's own request, a second approval.

**The artifact.** The role table in code, the permission on each operation, and one document with the chain, the table
of roles and permissions, and each 401 and 403.

**Example.** cmapi's roles and permissions are `ROLE_PERMISSIONS` (`cmapi/src/cmapi/core/authz.py:21-41`, commit
`72d082b`). `DocumentedRouter` writes `x-cmapi-permission` and a "Requires" line on each operation
(`cmapi/src/cmapi/core/docs.py:143-148`): 29 of the 31 operations have a permission, and 2 have none. The test
`test_declared_permission_is_the_enforced_one_and_every_route_answers` is the check
(`cmapi/tests/service/test_review_c_authz.py:39`, commit `88ab538`). An unknown permission stops startup
(`authz.py:115-117`). `docs/14-authorization.md` is the document, with the owner's rule: "cmapi must define the groups
contract but keycloak has the user and group role that is mapped to cmapi roles". The security scheme of the document
is OAuth 2 with no scopes, which is why the permission is in the extension.

## 10. The identity provider contract

**The rule.** The application and its identity provider agree in writing on these items, and the realm is code in the
repository:

- The issuer, and where the signing keys are. OpenID Connect Discovery: the `jwks_uri` "contains the signing key(s) the
  RP uses to validate signatures from the OP", and the issuer "MUST also be identical to the iss Claim value".
- The audience of the API. RFC 8725, section 3.9: when one issuer serves more than one application, "the JWT MUST
  contain an "aud" (audience) claim", and the application validates it.
- The algorithm. RFC 8725, section 3.1: "Libraries MUST enable the caller to specify a supported set of algorithms and
  MUST NOT use any other algorithms".
- Each claim that the application reads, the mapper that writes it, and what the application does with it.
- Each client and its flow. RFC 9700: "Public clients MUST use PKCE", and "The resource owner password credentials
  grant [RFC6749] MUST NOT be used."
- The lifetime of each token, and what the application does when the provider does not answer.
- For access tokens that are JWTs, RFC 9068 is the profile. It includes a check of the header: "The resource server
  MUST verify that the "typ" header value is "at+jwt" or "application/at+jwt"". If the provider does not send that
  header, record the difference and the check that replaces it.

**The check.**

- A test imports the realm file that ships into a real identity provider in a container, gets a token for each test
  identity, and compares it with a table that does not come from the realm under test.
- A unit test for each refusal of a token: no token, a wrong signature, a wrong audience, a wrong issuer, an expired
  token, a key that is not known.

**The artifact.** The realm as code, and one document with the clients, the claims, the lifetimes and the URLs.

**Example.** `docs/15-keycloak-integration.md` is the document (commit `65bd329`), and `docs/14-authorization.md`,
"Step 1: the token", lists each check with its `file:line`. `deploy/tests/realm-test.py` runs the shipped realm on
Keycloak 26.6.4 in a container, with an LDAP stand-in, and reads the expected token of each identity from
`examples/cmapi-sso/ldap/test-identities.tsv` (commit `ba76718`; it runs in the CI job `manifests`). **Where cmapi
differs:** the client `cmapi-automation` takes the password grant (`docs/15`, "The clients"), and cmapi checks the
`typ` claim of Keycloak, not the `typ` header of RFC 9068 (`cmapi/src/cmapi/core/auth.py:168-170`). **Not proven on
2026-11-13:** `docs/15`, "Proof", marks the three results on the deployment cluster as "Not run yet".

## 11. The data model

**The rule.** The migrations are the only source of the schema. The data-model document has two parts.

- **A generated part.** A script reads each table, column, constraint and index from the catalog of a database at the
  head of the migrations. Nobody copies the schema from the model code.
- **A written part**, with four subjects. What one row of each table is, and which code writes and reads it. The rules
  that the schema holds: each unique index, check and foreign key that the code relies on for correctness. What the
  database does not hold: secrets, tokens, and state that another system owns. The caches: which state the replicas
  share, where it is, and when it expires.

A rule that only the code holds breaks when two replicas run. So a rule such as one open request for each object is
an index in the schema, and the document names it. A change that is not compatible goes in three steps. Fowler's
`ParallelChange`: "Parallel change, also known as expand and contract, is a pattern to implement backward-incompatible
changes to an interface in a safe manner, by breaking the change into three distinct phases: expand, migrate, and
contract."

**The check.**

- A test writes the generated part again from the migrated test database, and fails when the document differs. So a
  migration without its document fails.
- A check that the models and the migrations agree. With Alembic it is `alembic check`, which "returns an error code
  plus a message if it is detected that new operations would be rendered into a new revision".
- A test for each rule that the schema holds: two concurrent writes, and the index refuses one.

**The artifact.** The migrations, and the data-model document with its generated part between two marker lines.

**Example.** `scripts/db-schema-doc.py` writes the part "The tables" of `docs/16-data-model.md` from the test database,
and `cmapi/tests/service/test_data_model_doc.py` fails when the two differ (commit `b9e7912`). The document has the
four subjects: "What each table holds", "The rules that the schema holds" (six rules, each with its index or check and
its migration), "What the database does not hold", and "Caches, and why cmapi has no Redis or Valkey". The migration
head is `0003`, with nine tables. **Not done in cmapi:** no step runs `alembic check`.

## 12. The UI-to-API map

**The rule.** The mockup file and the API document are the two sources. The map has one row for each action of each
screen: the action, the endpoint that it calls, whether the endpoint is built, and a note. It also has the two lists
that show a gap in the design:

- the actions that have no endpoint in the design;
- the built endpoints that no action calls.

The map gives the counts: actions, endpoints that the actions need, built, not built. The page code takes its types
from the API document (for TypeScript, `openapi-typescript` reads OpenAPI 3.0 and 3.1), so that a call that the
document does not have fails the type check.

**The check.** A test reads the map and the API document. It fails when a row says "built" and the document has no such
operation, and when the document has an operation that is in neither the rows nor the list of endpoints with no action.
A second test fails when the page has a state or a dataset that the map does not name.

**The artifact.** The map beside its figures, and the list of what the page takes from the mockup.

**Example.** `docs/diagrams/portal-architecture/README.md` is cmapi's map (commit `3cad6ed`): 64 actions in 9 tabs, 26
endpoints that the actions need, 13 built and 11 not built, 17 actions that make no call, and 18 built operations that
no action calls. `cmapi-portal-ui/MOCKUP-CONTRACT.md` lists the state and the datasets of each tab (commit `12f6d7b`),
and `cmapi-portal-ui/tests/contract.test.mjs` fails when the mockup has a state key that the list does not name.
**Not done in cmapi:** no test compares the map with `cmapi/contract/openapi.json`, so the "built" column is kept by
hand. The page makes no API call yet (`MOCKUP-CONTRACT.md`: "The API is built for a part of the mockup, and this app
calls none of it").

## 13. Outbound integrations, each with its mock

**The rule.** Each system that the application calls is behind one port: a typed interface in the code. The inventory
of section 1 of `SKILL.md` has one row for each provider: the calls, the authentication, the timeouts, the retries, and
whether a sandbox exists. The public documents of the provider define the contract, not the calls of the client. A
provider with no sandbox gets a mock, planned with `/mock-app`: the same paths, errors and authentication as the
documents of the provider. Where the team owns both sides, a consumer-driven contract fits. Pact "is a code-first
consumer-driven contract testing tool", and "The contract is generated during the execution of the automated consumer
tests."

**The check.** One suite of contract tests runs against the mock, and against the sandbox when one exists. The adapter
tests run with no outbound network. A fake that implements the port proves the application's own logic. It does not
prove the adapter, so it is not the contract test.

**The artifact.** The ports file, one adapter for each provider, the mock, and the plan from `/mock-app` with its table
"The client against the documents".

**Example.** cmapi's ports are typed Protocols in `cmapi/src/cmapi/core/ports.py`, and the Git adapters are
`core/git/gitea.py` and `core/git/github.py`. The service suite uses in-memory fakes that implement the ports:
`FakeGit`, `FakeKube` and `FakeValidator` (`cmapi/tests/service/conftest.py:80`, `:198` and `:259`). The GitHub
adapter has tests on a transport "shaped by GitHub's REST docs (2026-11)", and its file says "No test here reaches
GitHub" (`cmapi/tests/service/test_github_check_runs.py:1-4`). The identity provider is the one integration that
cmapi tests against the real software (section 10). **Not done in cmapi:** no mock follows a provider's published
OpenAPI document, and no `/mock-app` plan exists for the Git host.

## 14. Events and webhooks, when the application has them

**The rule.** An application that publishes or receives events has a second contract document, with the same gate as
the first.

- **The document.** AsyncAPI (v3.1.0 on 2026-11-13) "is a project used to describe message-driven APIs in a
  machine-readable format. It's protocol-agnostic". It describes each channel, each message and its schema.
- **The envelope.** CloudEvents 1.0 has four required attributes: `id`, `source`, `specversion` and `type`. "Producers
  MUST ensure that `source` + `id` is unique for each distinct event", so a consumer can drop a duplicate.
- **A webhook that the application sends.** OpenAPI 3.1 has the `webhooks` field: "The incoming webhooks that MAY be
  received as part of this API and that the API consumer MAY choose to implement." Sign each one. The Standard Webhooks
  specification uses three headers, `webhook-id`, `webhook-timestamp` and `webhook-signature`, and tells the receiver
  to "Use the `webhook-id` header as an idempotency key".
- **A webhook that the application receives.** It is an outbound integration in reverse: `/mock-app` records how the
  provider signs it, and the application checks each signature on the raw body.

**The check.** The same three as for the API document: the committed document is the one that the code publishes, a
comparison with the base branch fails on a removed channel or a removed required field, and each message example comes
from a run. A tool for the comparison of two AsyncAPI documents was not read for this file: **research item**.

**The artifact.** `contract/asyncapi.yaml`, and a `webhooks` part in the OpenAPI document.

**Example.** cmapi is not an example here. Its events are designed and off: `docs/01-design-and-architecture.md`,
"Optional integrations", has "Outbound events | Off | Signed webhook or Kafka topic, from a transactional outbox".
cmapi has no AsyncAPI document, and its figure of the portal lists "webhooks" and `outbox_publish` under "not built"
(`docs/diagrams/portal-architecture/README.md`, the text twin of figure 1).

## 15. The contracts scorecard

A review and a design both deliver this scorecard. One row for each contract. The state is one of four:

- **checked**: the artifact exists and a CI check fails when it breaks;
- **defined**: the artifact exists and no check holds it;
- **absent**: the application needs the contract and does not have it;
- **not applicable**: with the reason.

Each row names the file of the artifact and the job or test of the check. A row with no file is "absent". Each
difference from the standard is a finding, with its fix and its test, as for each other finding of the review.

The scorecard of cmapi at commit `933274a`, as the example:

| Contract | State | The artifact | The check | Open on 2026-11-13 |
| --- | --- | --- | --- | --- |
| The API document | checked | `cmapi/contract/openapi.json` | `test_the_committed_contract_is_the_document_this_code_serves`, `check_documented` | No lint step |
| The breaking-change gate | checked | `cmapi/contract/gate.sh`, `accepted-breaking.txt` | The job `api-contract`, with `gate-test.sh` | None |
| The changelog | checked | `cmapi/contract/changelog.py`, `changelog.json` | `changelog.py --check` | No version is released |
| Recorded payloads | checked | `cmapi/src/cmapi/contract/samples.json`, `docs/04` | `test_api_samples.py`, `api-examples-doc.py --check` | No payload from a cluster; 10 of 48 problems recorded |
| The error registry | checked | `PROBLEMS` in `core/docs.py` | `_register`, `test_api_samples.py` | The `type` host is a placeholder |
| Write semantics | checked | `routers/__init__.py`, `docs/04` "Rules for each call" | The recorded 400, 412 and 428 | 409 where the draft says 422 |
| Authorization | checked | `core/authz.py`, `x-cmapi-permission`, `docs/14` | `test_review_c_authz.py` | The 13 test users on the deployment cluster: not run |
| The identity provider | checked | The realm import, `docs/15` | `deploy/tests/realm-test.py`, `test_auth.py` | The password grant; the proof on the deployment cluster |
| The data model | checked | The migrations, `docs/16` | `test_data_model_doc.py` | No `alembic check` |
| The UI-to-API map | defined | `docs/diagrams/portal-architecture/README.md` | None for the "built" column | The page calls no API |
| Outbound integrations | defined | `core/ports.py`, the fakes | The adapter tests, with no provider document | No `/mock-app` plan |
| Events and webhooks | not applicable | None | None | Designed and off |

## 16. Rejected options, and the sources

| Option | Decision | Why |
| --- | --- | --- |
| A document written by hand beside code that also generates one, with no test between them | Rejected | Two sources. The OpenAPI Initiative: "newcomers to the project will not know which one is actually in use and mistakes will be made" |
| A code-first document that is served and not committed | Rejected | Nothing to compare a pull request with, so no gate |
| A comparison script of the project | Rejected | oasdiff has hundreds of checks in three levels, and a test of the gate proves it. cmapi's own research rejected the same option (`ob1-run/research.md`, D1) |
| OpenAPITools/openapi-diff 2.1.7 | Rejected for a 3.1 document | Its README says "Supports OpenAPI spec v3.0", and it needs Java |
| opticdev/optic | Rejected | The repository is archived (GitHub API, 2026-11-13) |
| pb33f/openapi-changes | Not chosen, kept as the alternative | Active, Apache-2.0, with configurable breaking rules. One tool for the gate and the changelog is simpler, and oasdiff does both |
| OpenAPI 3.0 | Rejected for a new document | Version 3.1 made the Schema Object a superset of JSON Schema 2020-12. Version 3.0 has its own subset |
| OpenAPI 3.2.1 now | Not rejected | Use it when each tool in the chain reads it. oasdiff says "3.2 specs are read too", and Spectral lists v3.2 |
| Examples written by hand | Rejected | They drift from the code. A recorded sample cannot |
| A byte comparison of the recorded payloads | Rejected | IDs, times and entity tags change at each run. Compare the keys and the types |
| An error body of the project | Rejected | RFC 9457 is the standard, with a media type that clients know |
| `Last-Modified` as the validator of a change | Rejected | RFC 9110, section 8.8.2.2: "A Last-Modified time, when used as a validator in a request, is implicitly weak unless it is possible to deduce that it is strong". An entity tag has no such limit |
| The password grant for a script | Rejected | RFC 9700: it "MUST NOT be used". Use client credentials for a service |
| A fake that implements the port as the contract test of a provider | Rejected | `/mock-app`: "The documents of the provider define the contract, not the client" |
| A data-model document written from the model code | Rejected | The catalog of the migrated database is what runs |
| Pact as the gate of an API with clients that the team does not own | Not chosen | A consumer-driven contract needs the tests of each consumer. The gate on the document needs none |

All sources were read on 2026-11-13.

| Subject | Source |
| --- | --- |
| Design first, one source of truth, the document in source control | [OpenAPI best practices](https://learn.openapis.org/best-practices.html) |
| OpenAPI 3.1: the Schema Object, the security requirement, `x-` extensions, `webhooks`, `example` | [OpenAPI 3.1.2](https://spec.openapis.org/oas/v3.1.2.html) |
| The latest OpenAPI version | [OpenAPI 3.2.1](https://spec.openapis.org/oas/v3.2.1.html) |
| JSON Schema: "The current version is 2020-12" | [JSON Schema specification](https://json-schema.org/specification) |
| Problem details | [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html) |
| `ETag`, `If-Match`, 412 | [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html), sections 8.8.3, 13.1.1 and 15.5.13 |
| 428 | [RFC 6585](https://www.rfc-editor.org/rfc/rfc6585.html), section 3 |
| `Idempotency-Key` | [draft-ietf-httpapi-idempotency-key-header-08](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/) |
| The dry run | [Kubernetes API concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/) |
| `Deprecation` and `Sunset` | [RFC 9745](https://www.rfc-editor.org/rfc/rfc9745.html), [RFC 8594](https://www.rfc-editor.org/rfc/rfc8594.html) |
| The issuer and the keys | [OpenID Connect Discovery 1.0](https://openid.net/specs/openid-connect-discovery-1_0.html), [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html) |
| JWT access tokens | [RFC 9068](https://www.rfc-editor.org/rfc/rfc9068.html), section 4 |
| JWT checks | [RFC 8725](https://www.rfc-editor.org/rfc/rfc8725.html), sections 3.1, 3.8 and 3.9 |
| PKCE, the password grant | [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html), sections 2.1.1 and 2.4 |
| The gate and the changelog | [oasdiff: breaking changes](https://github.com/oasdiff/oasdiff/blob/main/docs/BREAKING-CHANGES.md), [OpenAPI 3.1 support](https://github.com/oasdiff/oasdiff/blob/main/docs/OPENAPI-31.md) |
| The alternatives | [openapi-diff](https://github.com/OpenAPITools/openapi-diff), [optic](https://github.com/opticdev/optic), [openapi-changes](https://github.com/pb33f/openapi-changes) |
| The lint | [Spectral](https://github.com/stoplightio/spectral) |
| Tests from the document | [Schemathesis](https://github.com/schemathesis/schemathesis) |
| Expand and contract | [ParallelChange](https://martinfowler.com/bliki/ParallelChange.html) |
| Models against migrations | [Alembic: autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html) |
| Types from the document | [openapi-typescript](https://github.com/openapi-ts/openapi-typescript) |
| Consumer-driven contracts | [Pact](https://docs.pact.io/) |
| Events | [AsyncAPI 3.1.0](https://www.asyncapi.com/docs/reference/specification/latest), [CloudEvents 1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md) |
| Webhook signatures | [Standard Webhooks](https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md) |

## Diagram sources

The figure is `figures/source.html`, drawn to the `/visual` standard of this kit. Render it again from this folder:

```sh
diagram-render figures/source.html figures contracts
```

The picture, its text twin in section 1 and the page change together.
