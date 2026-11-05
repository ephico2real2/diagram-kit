# Review: pull request <n>, <title>

Adversarial pass on <date>, on the <k>-claim brief for pull request <n>. Reviewers, as run: <reviewer> (<model>,
<effort>, with a shell) and <reviewer> (<model>, <effort>, <with or without a shell>). Every verdict was checked
again here before a decision.

## Verdicts

| Claim | <reviewer 1> | <reviewer 2> | Decision |
|---|---|---|---|
| C1 <claim> | CONFIRMED | REFUTED | Accepted |
| C2 <claim> | REFUTED | PLAUSIBLE | Accepted on the fact, snippet rejected |
| C3 <claim> | CONFIRMED | CONFIRMED | No change |

## C<n>: <what was found>

**Finding (<reviewer>).** <the claim, the artefact, the proposed fix>.

**Re-check.** <what you measured yourself: the command, the output, the documentation line>.

**Decision.** <accepted, accepted on the fact with the snippet rejected, rejected, or routed to the change that owns
the file, with the reason>. <what was applied, and where a deviation is recorded>.

## Not asked, and what happened to it

- <reviewer>: <the volunteered observation>. <applied, recorded, or no change, and why>.

## Outcome

<claims refuted and accepted, snippets rejected and why in one clause, what ran again after the edits
(tests, suite, build, the change's own verification, CI), and what the second pass on the fixed head found>.
