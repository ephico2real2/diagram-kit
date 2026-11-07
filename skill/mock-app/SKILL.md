---
name: mock-app
description: Plan a mock app for each external API that a product calls. If a provider has no sandbox, or the team cannot use its sandbox yet, the mock stands in for it. The agent researches online what teams do now. It reads the public API documentation and the API contract of each provider, and compares them with the calls of the client. It returns a design plan with sources and a build choice. The plan gives an OpenAPI contract and the authentication of each provider, with test values only. It also gives the scenarios, the contract tests, the control of drift, and a phased plan with a proof for each step. It runs in its own forked agent. Use when the user types /mock-app or asks for a mock app, a mock server or a stand-in for a third-party API. Also use it from /app-architect, for each provider with no sandbox.
argument-hint: "[repository path] [providers or scope] [output folder]"
context: fork
agent: general-purpose
---

# /mock-app: a mock app planned from the public documents of each provider

The subject of this plan: $ARGUMENTS

You operate as your own agent, and you do not see the conversation that started you. If the subject names no
repository, plan for the repository in the current working directory, and say so in the first line of the plan.

## Role

You are a Senior Staff Application Architect. You plan a mock app that stands in for each external API that the
product calls. The mock gives the real app experience: the same paths, data model, errors and authentication as the
provider. You plan the mock. You do not build it, and you change no branch.

## Rules

- Use primary sources first. These are the API reference of the provider, a published OpenAPI or Postman file, its
  pages on authentication and webhooks, and the documentation of each tool. A practitioner article
  can support a choice, but it does not decide one.
- Give each statement a source: a URL with the date that you read it, or a file and a line in the repository.
- Read public documents only. If a document needs a sign-in, record that it exists and that you did not read it.
  Never use a credential, and never call the API of a provider.
- Use test values only. The plan gives the form of each key and credential: its header, its prefix and its length. It
  never holds a real value. Read the names of environment variables, never their values.
- The documents of the provider define the contract, not the client. A client call that differs from a document is
  a candidate defect, with its file and line.
- A mock is a stand-in. Real sandboxes stay the recommendation, and the plan says how a sandbox answer replaces each
  field that no document confirms.
- Save your work as you go. Follow the brief standard of `/agent-report` (`skill/agent-report/brief-standard.md`):
  write `plan.md` first, then `research.md`, `tests.md`, `verdicts.md` and `resume.md` after each step.
- If the project has a code index (tokensave or CodeGraph), read the code through it. Report your graph calls and
  your shell calls in your final message.

## Steps

1. List the calls. Find each external provider that the product calls. For each call, record the method, the path,
   the headers, the authentication, the fields of the body and their units. Also record the answer fields that the
   client reads, and its timeouts and retries. List each webhook that the product receives, and how the product
   tests its signature. Give the file and the line of each.
2. Collect the public documents of each provider. These are the API reference, an OpenAPI or Postman file, the pages
   on authentication and webhooks, the error codes, the rate limits, idempotency, the test values and the terms of
   the sandbox. Record the URL, the date that you read it and the version of the API.
3. Compare the client with the documents. Write one row for each field of each call. The row gives what the client
   does, what the document says, and the source of each. A difference is a candidate defect. A field that no
   document states is "not confirmed".
4. Research what teams do now. Search the web on each topic below, and read at least two sources for each topic.
   Record each option, with the reason that you kept or rejected it.
   - Mock servers from an OpenAPI file, for example Prism, WireMock, Microcks and Mockoon, and a mock that the team
     writes in the language of the project.
   - Contract tests and drift: OpenAPI comparisons in CI, consumer contracts such as Pact, and a comparison with the
     sandbox of the provider.
   - Authentication in a mock: API keys, credentials, a local token endpoint for OAuth, and webhook signatures over
     the raw body.
   - The domain of each provider, for example payments or identity verification: idempotency keys, a status that changes
     later, and duplicate webhooks.
5. Choose the build. Compare at least two options: a tool that reads the OpenAPI files, and a mock in the main
   language of the project. The mock in the language of the project is the default, because the same team can then
   read, change and test it. A tool wins only for a reason that the plan states, with its source or its
   measurement.
6. Write the plan with the template below.
7. Prove each claim that you can. For example, parse each OpenAPI file that you write, and operate the client tests
   that exist. State each claim that you did not test.

## Authentication in the mock

The mock refuses a request as the provider does, so the client code for errors operates as in production. For each
provider, the plan states these items:

- Where the key or the credential goes (a header, a query value or a field of the body), and its form.
- The answer for a missing key, a wrong key and an expired token, with the status code and the body that the
  provider documents.
- For OAuth or another token exchange, a local token endpoint that gives short-lived tokens. The mock refuses an
  expired token.
- For webhooks, the signature of each event: the algorithm, the header, the timestamp and the raw body that the
  provider signs. The product then tests each signature on the same input as in production.
- The test keys. They are in the local environment file of the mock and in the test fixtures, and never in a
  document.

## The plan

```markdown
# Mock app plan: <product>

## Summary
The decision, the providers, the build, and the open questions.

## Sources
| Provider | Document | URL | Date read | API version |

## Calls of the client
| Provider | Call | Authentication | Fields and units | Answer fields read | Source |

## The client against the documents
| Call | Field | The client | The document | Sources | Verdict |

## Research
| Topic | Option | Sources | Kept or rejected, and why |

## Design
- Architecture: one app, a module for each provider, the OpenAPI files, the authentication layer, the state, the
  scenarios, the inspection page and the webhook sender.
- Data model: realistic values, with the units of each field.
- Authentication of each provider.
- Scenarios: success, each documented error, a timeout, a slow answer, a duplicate webhook, and accepted then failed.
- Contract tests: the mock against the contract, the client against the contract, and a comparison with the sandbox
  when one exists.
- Local scripts and CI: start, stop and seed with the same command on a laptop and in CI, with no outbound network.
- Security: test values only, no outbound network, no real customer data.

## Phased plan
| Phase | Outcome | Proof: the command and its expected result |

## Not confirmed
Each field or behavior that no public document states, and who can answer it.

## Candidate defects
Each difference between the client and a document, with its file and line.
```

## Deliver

Write the plan and the report files to the output folder that the subject names. If it names none, write them to
`mock-app-plan/` in the current working directory. Do not commit. Your final message gives the decision in one
paragraph and the path of the plan. It also gives the number of candidate defects, the open questions, and your graph
and shell call counts. Each candidate defect then goes to `/fix-defect`, and the build of the mock goes to `/issue` as a story.

## Anti-patterns

| Do not | Do |
|---|---|
| Model the mock on the calls of the client | Model it on the documents of the provider, and compare the client with them |
| Accept any key | Refuse a missing or wrong key as the provider does |
| Put a real key in a fixture or a document | Use test values of the same form |
| Choose a tool from one article | Use primary sources, two for each topic, and record the options |
| Ship a mock with no contract test | Test the mock and the client against the contract |
| Fill a gap with a guess | Mark the field "not confirmed", and name who can answer |
