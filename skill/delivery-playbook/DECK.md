---
title: Delivery Playbook
subtitle: Human-guided and AI-guided engineering, from a local copy to production
author: "[Author], [Role], [Firm]"
date: "[date]"
---

## What we do

- We review, design, build, test and deliver software with one team of people and AI agents.
- A senior architect sets the technical vision and makes each decision.
- AI agents from more than one vendor do the review, the analysis, the code and the tests.
- The architect audits each agent result before the team accepts it.
- Each claim and each number has a source that a person can read.

## Principles

- Local first: the product operates on a laptop, and the same scripts then deploy it anywhere.
- Evidence first: each claim comes from a command, a test or a record.
- Adversarial by default: each claim about the code is attacked.
- People decide, agents execute: no agent merges a change.
- No vendor lock-in: open standards and portable containers.
- Contract first, secure by design, observable by design, traceable delivery.

## Services

- Adversarial security audit
- Architecture and modernization, with no vendor lock-in
- Identity and secrets: OIDC, JWT, mutual TLS, workload identity
- CI/CD and the software supply chain: scans, SBOM, signatures
- Observability, APM and KPIs, in open formats
- Runtime and scaling: virtual machines, cloud or Kubernetes, with KEDA
- Local product copy and API mocks, automated testing, agile delivery

## The engagement lifecycle

![Eight stages, from discovery to hand-over. A failed test at stage 6 sends the work back to stage 5.](figures/lifecycle.light.png)

## The review and build loop

![The architect briefs, audits and rules. Agents work in isolated copies.](figures/review-loop.light.png)

## Local first

![One image, built once, moves with the same digest from local to CI, to a sandbox and to production.](figures/local-first.light.png)

## API mocks when a provider has no sandbox

- The mock uses the main programming language of the project.
- Each provider has an OpenAPI contract, a data model and the unit of each field.
- Each answer has realistic values, so the product operates end to end.
- Scenarios give failures on demand: a timeout, an error code, a slow answer.
- Contract tests compare the mock and the client with the contract.
- A real sandbox stays the recommendation.

## CI/CD for a web application or an API

![Five stages, each with what stops the pipeline.](figures/pipeline-web.light.png)

## CI/CD for a mobile application

![Six stages. A person approves each store submission.](figures/pipeline-mobile.light.png)

## Identity, transport security and secrets

- Sign-in: OIDC with PKCE. Keycloak is the standard. A cloud provider, for example Amazon Cognito, is an option.
- Tokens: each API checks the JWT signature, issuer, audience, expiry and algorithm.
- Service to service: mutual TLS where it is necessary, with automatic rotation.
- Secrets: workload identity, a secret manager, External Secrets on Kubernetes, and no secret in code.

## Observability, APM and KPIs

- OpenTelemetry in each service. Traces, metrics and logs in OTLP.
- Open source back ends, or a managed APM through the same collector.
- RED metrics for each service, USE metrics for each resource.
- System KPIs with service level objectives. Business KPIs from a review of the business functions.
- Alerts start from a measured baseline, and each alert has a runbook.
- The admin portal shows the KPIs from end to end.

## Runtime and scaling

- One OCI image operates on a virtual machine, a cloud virtual machine or Kubernetes.
- Compose on virtual machines. Helm and Argo CD on Kubernetes.
- KEDA scales each workload on a measured signal.
- Capacity follows the measured load. Managed services are an option.

## Testing

- Unit, integration on the real database engine, contract and API tests.
- Browser tests with Playwright. Mobile flows with Maestro on emulators and simulators.
- Load tests with k6. Mutation tests during each audit.
- The same tests operate on a laptop and in CI.
- Each failure gets an issue, and the test starts again from step 1.

## Agile delivery

- Epics, milestones as release trains, features, stories, tasks and defects.
- Each pull request names its milestone and its issues.
- Each issue has one status label.
- The build tracker shows the milestone and the status of each issue.

## Legend: findings

| Prefix | Category |
|---|---|
| `SEC` | Security |
| `BUG` | Bug |
| `PERF` | Performance |
| `BP` | Best practice |
| `UX` | User experience |
| `OA` | Owner action |

## Legend: severity, status and verdicts

| Severity | Status | Verdict |
|---|---|---|
| Critical | Open | CONFIRMED |
| High | Fixed on the review branch | REFUTED |
| Medium | Partly fixed | PLAUSIBLE |
| Low | Owner action, Closed | NOT REACHED |

## What the client gets

- A report with findings, tests, fixes and a phased roadmap.
- Issues, epics and milestones that match the roadmap.
- The product on a laptop, with sandboxes or API mocks.
- Pipelines, test suites, dashboards and alerts.
- Figures, guides and runbooks made from the code at a named commit.
