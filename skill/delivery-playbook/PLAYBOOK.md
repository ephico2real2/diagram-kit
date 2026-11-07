---
title: Delivery Playbook
subtitle: Human-guided and AI-guided engineering, from a local copy to production
author: "[Author], [Role], [Firm]"
date: "Version [version], [date]"
---

## 1. What this playbook is

This playbook states how we review, design, build, test and deliver software. It is the same for each client. A client copy adds the facts of that client: what operates today, what is proposed, and the proof of each step.

We work as one team of people and AI agents. A senior architect sets the technical vision, writes each brief and makes each decision. This is human-guided engineering. AI agents from more than one vendor do the review, the analysis, the code and the tests. This is AI-guided engineering. The architect audits each agent result before the team accepts it.

The playbook has three parts:

- Sections 2 to 4 give the principles, the services and the lifecycle of an engagement.
- Sections 5 to 13 give the standard for each area of the work, with a figure where the order matters.
- Section 14 gives the legend that every report, issue and figure uses.

With this playbook, each client gets a detailed document: the Adversarial Review, Architecture and Implementation Report. It holds the findings and their proof, the current and the target architecture, the work that was built and tested, and a phased roadmap. It uses the legend of section 14.

## 2. Principles

| Principle | What it means | How we prove it |
|---|---|---|
| Local first | A well-built application operates on a developer machine. This local copy is the base of each stage of the software development life cycle (SDLC). The same scripts build, deploy and test it locally, and then in a real environment, on-premises or in a cloud | A full proof from an empty machine, with exit 0 at each stage |
| Evidence first | Each claim, number and status comes from a command, a test or a record that the document names | The source of each statement is in the document |
| Adversarial by default | Each claim about the code is attacked. Only what a test supports stays | A test that fails before a fix and passes after it |
| People decide, agents execute | The architect decides. Agents test claims, write code and report. No agent merges a change | A written ruling for each agent job |
| No vendor lock-in | Open standards and portable containers. A managed service is an option behind an interface, not a dependency | The same image operates on a virtual machine, a cloud virtual machine and Kubernetes |
| Contract first | Each API has an OpenAPI contract and a data model. A mock follows the contract | Contract tests on the client side and on the server side |
| Secure by design | Standard identity, short-lived credentials, encryption in transit and no secret in code | Security tests in CI and an adversarial audit |
| Observable by design | Open formats for traces, metrics and logs. Alerts on measured values | A dashboard and an alert for each key performance indicator (KPI) |
| Traceable delivery | Each change has an issue, a milestone, a pull request and a tracker row | The tracker reads its values from the issue system |

## 3. Services

| Service | What the client gets |
|---|---|
| Adversarial security audit | Findings with a severity, a test, a fix and a user story. Reviewers from different model families attack each claim |
| Architecture and modernization | The current and the target architecture, a pluggable design with no vendor lock-in, refactoring, and new functions that are secure and scale |
| Identity and secrets | OpenID Connect (OIDC) sign-in, JSON Web Token (JWT) rules, mutual TLS where it is necessary, and secret management with workload identity |
| CI/CD and the software supply chain | Pipelines with tests, scans, a software bill of materials (SBOM), image signatures and deploy by digest |
| Observability, APM and KPIs | OpenTelemetry instrumentation, application performance monitoring (APM), dashboards, and alerts on system and business KPIs |
| Runtime and scaling | Containers that operate on virtual machines, cloud virtual machines or Kubernetes, with autoscaling on measured load |
| Local product copy and API mocks | The full product on one machine, with provider sandboxes or a mock of each external API |
| Automated testing | Unit, integration, contract, API, browser, mobile, load and mutation tests, on a laptop and in CI |
| Agile delivery | Epics, milestones, features, stories, tasks and defects, linked to each pull request and to a build tracker |
| Documentation and diagrams | The Adversarial Review, Architecture and Implementation Report, guides, runbooks, figures and dashboards, made from the code at a named commit |

## 4. The engagement lifecycle

<!-- markdownlint-disable MD033 -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/lifecycle.dark.png">
  <img src="figures/lifecycle.light.png" alt="Figure 1. The engagement lifecycle. Eight stages, from discovery to hand-over. The product operates locally at stage 2, before the review. A failed test at stage 6 sends the work back to stage 5.">
</picture>
<!-- markdownlint-enable MD033 -->

*Figure 1. The engagement lifecycle. Eight stages, from discovery to hand-over. The product operates locally at stage 2, before the review. A failed test at stage 6 sends the work back to stage 5.*

| Stage | What happens | What it delivers |
|---|---|---|
| 1. Discover | Read the code, the pipelines, the infrastructure and the business functions | Inventories and the list of claims to test |
| 2. Operate locally | Make the product operate on one machine, with sandboxes or mocks | The local copy and its proof |
| 3. Review | Attack the claims with agents of different model families | Findings, each with a test |
| 4. Plan | Design the target and order the work in release trains | The architecture, the roadmap, the epics and the milestones |
| 5. Build | Agents write the code from briefs. The architect audits and rules | Commits with tests |
| 6. Prove | Operate the tests locally, in CI and in a sandbox | Test records with 0 failures |
| 7. Deliver | Merge through pull requests with milestones, and release in order | Releases with a rollback |
| 8. Hand over | Give the documents, the dashboards and the open items | Guides, runbooks and the tracker |

If a test fails at stage 6, the work goes back to stage 5. Each defect gets an issue at once.

## 5. The review and build loop

<!-- markdownlint-disable MD033 -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/review-loop.dark.png">
  <img src="figures/review-loop.light.png" alt="Figure 2. The review and build loop. The architect writes the brief, audits the result and rules. Agents from several vendors do the work in isolated copies. Money, security and migration fixes get three reviews.">
</picture>
<!-- markdownlint-enable MD033 -->

*Figure 2. The review and build loop. The architect writes the brief, audits the result and rules. Agents from several vendors do the work in isolated copies. Money, security and migration fixes get three reviews.*

1. The architect writes a brief. The brief gives the numbered claims, the scope, the limits and the report standard.
2. The brief has three planted claims with answers that only the architect knows: one true, one false and one that the agent cannot test.
3. The architect chooses the agent for each job: the vendor, the model and the reasoning effort. Heavy jobs operate one at a time.
4. The agent works in an isolated copy with no remote and no secret. It writes its plan, research, tests, verdicts and fixes to files as it works.
5. The architect audits the job. The audit compares the planted answers and operates each test again. It adds mutants, which are deliberate faults that a good test must catch. It also counts the calls in the agent log.
6. The architect writes a ruling for each finding. A new defect gets an issue at once.
7. A fix to money, security or a database migration gets three reviews from different model families.
8. The change goes through a pull request from a working branch, with its milestone and labels. CI must pass before the merge.
9. The tracker changes in the same pull request.

The test loop: operate the whole test from its first step. At the first failure, file the issue, fix the cause, and start again from step 1. Only one full run with 0 failures ends the loop.

## 6. Local first

<!-- markdownlint-disable MD033 -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/local-first.dark.png">
  <img src="figures/local-first.light.png" alt="Figure 3. One build, the same scripts, four environments. The product operates on a laptop first. The same image and scripts then operate in CI, in a sandbox and in production, on-premises or in a cloud.">
</picture>
<!-- markdownlint-enable MD033 -->

*Figure 3. One build, the same scripts, four environments. The product operates on a laptop first. The same image and scripts then operate in CI, in a sandbox and in production, on-premises or in a cloud.*

A well-built application operates locally. The team proves an idea on the local copy before it pays for an environment. The same container image and the same scripts then operate in CI, in a sandbox and in production, on-premises or in a cloud. Only the configuration changes between environments.

The local copy has stand-ins for each platform service:

| Platform service | Local stand-in |
|---|---|
| Database | The same engine and major version as production, in a container |
| Cache and queues | The same protocol, in a container |
| Object storage | An S3-compatible server |
| Email | A mail catcher |
| Identity provider | Keycloak |
| Telemetry | An OpenTelemetry collector, Prometheus and Grafana |
| Edge proxy | The same proxy as production, for example Envoy |

If an external provider has a sandbox, use the sandbox. If it has no sandbox, build a mock of its API:

- The mock uses the main programming language of the project, so the same team can read, change and test it.
- Each provider has an OpenAPI contract with its paths, its data model and the units of each field.
- Each answer has realistic values, so the product operates end to end.
- Scenarios give failures on demand: a timeout, an error code, a slow answer and a duplicate webhook.
- An inspection page shows the request log and the state.
- Contract tests compare the mock answers and the client calls with the contract.
- The contract marks each field that no provider document states. A sandbox answer removes the mark.

A mock is a stand-in. The recommendation for real sandboxes stays.

## 7. CI/CD for a web application or an API

<!-- markdownlint-disable MD033 -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/pipeline-web.dark.png">
  <img src="figures/pipeline-web.light.png" alt="Figure 4. The pipeline for a web application or an API. Five stages. The image is built and signed once, and the same digest moves to staging and to production. Each stage names what stops it.">
</picture>
<!-- markdownlint-enable MD033 -->

*Figure 4. The pipeline for a web application or an API. Five stages. The image is built and signed once, and the same digest moves to staging and to production. Each stage names what stops it.*

| Stage | Steps | What stops the pipeline |
|---|---|---|
| Pull request gate | Lint, type check, unit tests, integration tests on the real database engine, contract tests and a build | Any failed test |
| Security gate | A secret scan of the new commits, a dependency audit and static analysis | A new secret, or a new advisory over the agreed level |
| Release build | Build the container image once. Scan it. Write its SBOM. Sign it. Push it by digest, with a provenance attestation | A critical vulnerability that has a fix |
| Staging | Deploy the digest. Apply migrations by one tested method. Operate smoke and browser tests | A failed health check or test |
| Production | Promote the same digest. Roll out in steps with health checks | A failed health check starts the rollback to the last digest |

The pipeline gets cloud access through OIDC federation, with no stored key. Each action and tool is pinned to a version and a checksum. A merge to a deploy branch needs a reviewed pull request and passed checks.

## 8. CI/CD for a mobile application

<!-- markdownlint-disable MD033 -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/pipeline-mobile.dark.png">
  <img src="figures/pipeline-mobile.light.png" alt="Figure 5. The pipeline for a mobile application. Six stages. Device flows operate on emulators and simulators before the build and again on the release build. A person approves each store submission.">
</picture>
<!-- markdownlint-enable MD033 -->

*Figure 5. The pipeline for a mobile application. Six stages. Device flows operate on emulators and simulators before the build and again on the release build. A person approves each store submission.*

| Stage | Steps | What stops the pipeline |
|---|---|---|
| Pull request gate | Type check, lint and unit tests | Any failed test |
| Security gate | A secret scan of the new commits and a dependency audit | A new secret, or a new advisory over the agreed level |
| Device tests | Flows on an Android emulator and on iPhone and iPad simulators, with no outbound network except the local machine | A failed flow |
| Signed build | A build service or the native tools make signed builds. Signing keys stay in the build service or a secret manager | A build or signing failure |
| Internal release | An internal track and TestFlight. The device flows operate on the release build | A failed flow on the release build |
| Store release | A person approves the submission. Over-the-air updates pass the same gates and have a rollback | No approval |

A store submission never starts from a push with no approval.

## 9. Identity, transport security and secrets

| Area | Standard |
|---|---|
| Sign-in | OIDC with the authorization code flow and PKCE (proof key for code exchange). Keycloak is the standard identity provider. A cloud provider, for example Amazon Cognito or Microsoft Entra ID, is an option behind the same OIDC interface. Administrators use a second factor |
| Tokens | Each API checks the JWT signature against the published keys, and the issuer, audience, expiry and algorithm. Access tokens are short-lived. Refresh tokens rotate, and a sign-out revokes them |
| Service to service | Mutual TLS where services share a network that the client does not fully control, or where a regulator requires it. Certificates rotate automatically |
| Secrets | No secret in code, in an image or in a log. A workload gets its cloud access from its identity, not from a stored key. Secrets come from a secret manager, through External Secrets on Kubernetes. Secrets rotate, and CI scans each commit |

## 10. Observability, APM and KPIs

| Area | Standard |
|---|---|
| Instrumentation | The OpenTelemetry SDK in each service, and the OpenTelemetry collector. Traces, metrics and logs use OTLP, the open OpenTelemetry protocol |
| Back ends | Open source back ends, for example Prometheus, Grafana, Tempo and Loki, or a managed APM service through the same collector. A change of back end needs no change of code |
| Service metrics | RED for each service: rate, errors and duration. USE for each resource: the share in use, the saturation and the errors |
| KPIs | System KPIs, for example availability and latency, each with a service level objective. Business KPIs come from a review of the business functions, for example completed payments or new sign-ups |
| Alerts | Each alert starts from a measured baseline and has a runbook. An alert names the KPI and the threshold |
| Admin portal | The admin portal shows the KPIs and the RED metrics from end to end |

A dashboard starts with an inventory of each metric that the workload emits. The dashboard then shows only the metrics that answer a question that a user asks.

## 11. Runtime and scaling

- Each service is an OCI container image. The same image operates on a virtual machine, on a cloud virtual machine with Compose, or on Kubernetes with Helm.
- On Kubernetes, Argo CD deploys from Git. KEDA scales each workload on a measured signal, for example the request rate or the queue depth.
- The capacity follows the measured load. A managed service is an option, not a requirement.

## 12. Testing

| Level | Tools | Where it operates |
|---|---|---|
| Unit | The test runner of the language | Laptop and CI |
| Integration | The real database engine and cache, in containers | Laptop and CI |
| Contract | OpenAPI contracts and the mock app | Laptop and CI |
| API | HTTP tests against the local stack | Laptop and CI |
| Browser | Playwright with Chromium | Laptop, CI and staging |
| Mobile | Maestro on Android emulators and iOS simulators | Laptop and CI where the runner permits |
| Load | k6 | Laptop and staging |
| Mutation | Deliberate faults that the tests must catch | During each audit |
| Security | Scanners in CI, and the adversarial audit | CI and each review |

## 13. Agile delivery

Each piece of work has one record on GitHub, from the idea to the release. The `/agile` skill gives the template of each item, its issue type and the commands that create it. The `/pull-request` skill gives the template of each change.

| Item | Meaning | GitHub issue type | Parent |
|---|---|---|---|
| Milestone | A release train: the set of changes that ships together, with a date and a rollback | Not an issue | None. Each issue names one milestone |
| Epic | A goal with child issues and exit criteria | `Epic` where the organization has it | None |
| Feature | A capability that a user sees | `Feature` | An epic |
| Story | One slice of a feature for one role, with acceptance criteria | `Feature` | A feature or an epic |
| Task and spike | A step of work, or a time-boxed question with a measured answer | `Task` | A feature or an epic |
| Defect | A fault, filed at once with how to prove it | `Bug` | The issue under which it was found |
| Owner action | Work that needs an account, a key, a plan or a decision that code cannot supply | `Task` | The issue that waits for it |

The parent link is a GitHub sub-issue, and the body also says `Part of #<parent>`. A milestone is never a parent. Each issue has one type label, one `status:` label, and the class labels of section 14.

Each pull request uses the template of its repository. It names its milestone, its issues and its class. The build tracker shows the milestone, the class and the status of each issue, and it changes in the same pull request as the work.

## 14. Legend

Every report, issue, pull request and figure uses this legend. `skill/agile/LEGEND.md` holds the same legend with its labels. Each finding ID has a prefix and a number. The prefix gives the category. The number does not give an order of priority. An ID never changes after it is filed.

| Prefix | Category | Meaning |
|---|---|---|
| `SEC` | Security | A person can get data, money or access that they must not have |
| `BUG` | Bug | The code gives an incorrect result |
| `PERF` | Performance | Speed, capacity, scaling or measurement of the service |
| `BP` | Best practice | A gap in how the team builds, tests, deploys or operates the code |
| `UX` | User experience | A defect that a user sees on the screen |
| `OA` | Owner action | Work that needs an account, a key, a plan or a decision that code cannot supply |
| `INV` | Innovation | A new feature, design, idea or method that comes from no finding |
| `TDT` | Tech debt | A debt item that comes from no finding |

A class says what kind of work an item is. Each item of any prefix can have one class, both classes or no class. A finding keeps its ID and gets a class label. A defect that restores the intended behavior usually has no class.

| Class | Label | Meaning |
|---|---|---|
| `INV` | `class:INV` | Innovation: the work adds something that does not exist today, such as a feature, a screen, a design, a service or a method |
| `TDT` | `class:TDT` | Tech debt: the code or the setup works today, but an earlier shortcut makes it cost more to change, operate or upgrade |

| Severity | Meaning |
|---|---|
| Critical | A person with no special access can get money, data or control of a server now |
| High | If a condition occurs, for example a race or a stolen token, a person can get money, data or access |
| Medium | Incorrect data, a weak control or a slow service, with no direct loss |
| Low | A small defect, a defect that no code path reaches yet, or a cleanup |

| Status | Meaning |
|---|---|
| Open | No fix yet. A story describes the work |
| Fixed on the review branch | The fix and its test are merged on the review branch. Nothing is deployed |
| Partly fixed | Part of the work is fixed. The rest is a story or an owner action |
| Owner action | The work waits for the owner |
| Closed | The fix reached the default branch |

| Verdict | Meaning |
|---|---|
| CONFIRMED | A test supports the claim |
| REFUTED | A test shows that the claim is false |
| PLAUSIBLE | The evidence supports the claim, but no test proves it |
| NOT REACHED | No test is possible from where the agent operates |

| Figure element | Meaning |
|---|---|
| Solid box | Operates today |
| Dashed box | Proposed, not built |
| Solid arrow | Traffic or a call |
| Dashed arrow with a label | A relationship with no traffic |
| Red | A failure, a refusal or a finding |
