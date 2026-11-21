---
name: decide
description: "Research, then ask: the method for a decision that is the user's to make. The agent reads the primary sources and quotes them, reviews the project's own evidence, recommends one option, asks at most 4 self-contained questions with the agent's question tool, and records the answer where the work lives. Use when a decision is the user's to make, for example how to accept a story, which environment may be written, or which of several designs to build. Also use it when the agent is about to ask the user an open question. Use when the user types /decide."
---

# /decide: research, then ask

`/decide <the decision>` is the method for a decision that belongs to the user. The agent does the research first. Then it asks short questions that the user can answer in one click. The user said of this method: "This is how i want you to research and prompt me questions."

Do not use it for a choice that the user has already made, or for a choice that the rules of the project already settle. Read the rules first. A decided point is not asked again.

## 1. Research and fetch

Read the primary sources: the standard, the vendor documentation, the RFC, the source code. A search summary or a model's memory is not a source.

- Fetch each source. Do not only search for it.
- Quote the exact sentence that each point rests on. Give its URL and the date that you read it.
- Say what a source does **not** say. A source that names no environment gives no rule for an environment.
- If a fetched source refutes an earlier claim, retract the claim in so many words.

## 2. Review the project's own evidence

- Quote the rules of the repository with the file and the line.
- Say what is proven, and on which environment it ran.
- Say what is not proven.
- Give the facts that bear on risk. One example is whether an action writes to a shared system.

Pull the facts first. Do not estimate. If a fact is not available, say so.

## 3. Recommend

Name one option. Give its reason, and tie the reason to the sources of step 1 and the evidence of step 2. Do not recommend an option because it is the easy one.

## 4. Ask

Use the question tool of the agent. For example, in Claude Code it is `AskUserQuestion`. Do not ask in plain text when the tool exists.

- Ask at most 4 questions.
- Make each question self-contained. The dialog can hide the text above it, so a question cannot depend on earlier text.
- Name the items that each question is about. Do not write "these" or "the above".
- Put the recommended option first. End its label with "(Recommended)".
- Each option has a description that states its consequence: what happens, and what does not.
- Use multi-select where the choices combine, for example a list of scenarios to run.
- Ask separately before any outward-facing write. The question names which system or repository may be touched. A yes to another question is not a yes to the write.

## 5. Record the answer, then act

Write the answer where the work lives. For example, post a comment on the issue with the answer and the sources of step 1. Then do the work. If the user chose an option other than the recommended one, do that option. Do not argue it again.

## Worked example: cmapi, 2026-11-21

The decision: should a story be accepted on the evidence of a stub API, or on a live run?

**Sources, fetched and quoted:**

| Source | The sentence | What it says |
|---|---|---|
| Scrum Guide 2020 | An increment is "thoroughly verified, ensuring that all Increments work together". Also: "In order to provide value, the Increment must be usable." | The increment must work and be usable. It does not say on which environment. |
| Martin Fowler, *The Practical Test Pyramid* | "How can we ensure that the fake server we set up behaves like the real server?" He says to reduce end-to-end tests "to a bare minimum", on "the high-value interactions users will have". They are "notoriously flaky". | A fake server needs a check against the real one. Keep few live tests, on the high-value paths. |
| Agile Alliance, glossary | "An acceptance test is a formal description of the behavior of a software product." | It names no environment. |

**Project evidence:** the stub had differed from the real router twice in a review. So a green run on the stub did not prove the behavior of the real router.

**Recommendation:** run a live check of the high-value paths before the owner approves the story.

**The four questions asked:**

1. Story acceptance: a live run first (Recommended), approve now, or approve now and check live later.
2. A contract story: approve it after the live write (Recommended), or now.
3. Which live scenarios, multi-select: Submit to In sync, Drift, 412, 409.
4. Which namespace may be written: a new test namespace (Recommended), an existing one reverted, or no writes.

**The answers:** all the recommended options. They were recorded on the issues, with the sources, and then the live run started.

The example shows the method. cmapi is the example, not the rule. Another project has other sources and other questions.

## Anti-patterns

| Do not | Do |
|---|---|
| Ask an open question in plain text | Research first, then ask with the question tool |
| Cite a search summary | Fetch the source and quote the sentence, with URL and date |
| Ask 6 questions in one dialog | At most 4. Combine choices with multi-select |
| Write "the above" or "these" in a question | Name the items in the question |
| Hide the recommendation in the last option | Put it first, marked "(Recommended)" |
| Let an option say only its name | State the consequence of each option |
| Fold a write to a shared system into another question | Ask it alone, naming the system or repository |
| Keep the answer in the chat | Record it on the issue, with the sources, then act |
