---
name: agent-report
description: How a background agent of any kind reads code, logs its research as it works, and proves that the work is real. It holds the brief standard to paste and the structure of the report files. Its audit with planted claims shows whether an agent did more than fill in a structure. Use when the user types /agent-report, before you start any background agent, or when you judge the report of one.
---

# /agent-report: agents that save their work, and an audit of that work

A stopped agent loses all that it did not write to a file. An agent that reports only as its last step loses everything. A neat report also proves nothing about the work behind it. This skill addresses both problems.

Paste `${CLAUDE_SKILL_DIR}/brief-standard.md` into the brief of each agent, of any kind. Codex and Cursor do not read `CLAUDE.md`, so the brief must hold the text. Split a brief with many claims, and operate heavy agents one at a time.

## 1. What the agent does

The agent tests claims. It does not decide for the owner, and it changes no branch.

1. It writes `plan.md` first, with the claims by ID.
2. If the project has an index, it reads code through the graph. The `/tokensave-fork` skill gives the permissions for each agent.
3. For each ID, it finds sources, operates a test, and gives a verdict that the evidence supports.
4. After each ID, before the next one, it appends to the files and rewrites `resume.md`.
5. Its final message is short: the tally, the path of `verdicts.md`, and its graph and shell call counts.

## 2. How the agent logs

| File | Holds |
|---|---|
| `plan.md` | The claims by ID, in order |
| `research.md` | Sources, quotes, what each one establishes, and rejected options |
| `tests.md` | The exact command, the commit, the environment, the output and the exit status |
| `logs/` | Long output, named from `tests.md` |
| `verdicts.md` | One row per ID: CONFIRMED, REFUTED, PLAUSIBLE or NOT REACHED |
| `fixes.md` | Only for a defect: the root cause, the full fix, the test, and its result before and after |
| `recommendations.md` | Only for a real choice: each option with its measured result |
| `resume.md` | The current ID, what is next, and what is in operation |

The research and tests stay apart from the opinions. The arbiter reads `verdicts.md` first, and opens the other files only for the ID that it needs.

## 3. Confirm that the work is real

A correct structure is easy to write. Do these steps yourself, because a report cannot prove its own work.

1. Plant claims with known answers. Before you start the agent, include at least one true claim, one false claim and one claim that it cannot test from where it runs. Find the answers yourself first, and keep them out of the brief. A false claim marked CONFIRMED, or a claim with no possible test marked CONFIRMED, fails the job.
2. Operate the tests again. Take each command and folder from the agent's records, and compare the output with the record. Use the recorded folder, because two tests in the pilot failed from another folder and passed from the recorded one. Install the tools first: the agent's Codex shell had `rg`, and the auditor needed `brew install ripgrep`.
3. Count the calls in the agent's own session log, and compare them with its final message. For Claude, Codex or Cursor, `tool-use-audit.py` of `/tokensave-fork` also shows whether the agent read through the graph and whether it read a whole file.
4. Read the files during the run, at least once. An agent can rewrite all files at its end, and then the file times show nothing. The times of its log files show the order of the work.
5. Measure the time after the last claim. Compare the end of the job with the time of the last evidence file. A large share means that the agent worked on the report and not on the claims.
6. Look for filler. A section that says only that nothing applies shows structure with no content.
7. Make sure that each proof covers the claim. A pin in a local file does not establish what production runs.
8. For a fix, apply the patch to a fresh clone. The test must fail before the patch and pass after it.
9. File the defects. Read `verdicts.md`, `fixes.md` and `research.md` for each defect. Add each fault that your audit found, in the application or in the work of the agent. Search for a duplicate first. Each one gets an issue through `/fix-defect`. The audit is not finished until each defect has its issue number.
10. For a job that tests an app, make sure that it followed the test loop in `/fix-defect`. After each fix, its log must show a restart from the first step. Its last full run on the final code must have 0 failures. Operate that last run again yourself. A job that fixed a defect and did not restart has not finished.

Any failed step puts the whole report in doubt, and not only that claim. These steps do not measure the depth of a hard investigation, so read the research of the claims that matter.

## 4. What a pilot measured

One Codex job on 2026-11-06, with five claims about a private NestJS repository. The claims were easy on purpose.

| Item | Result |
|---|---|
| Planted answers | 5 of 5 correct: 2 true claims CONFIRMED, 2 false claims REFUTED, 1 claim with no possible test NOT REACHED |
| Tests operated again | 5 of 5 gave the same output. One needed `rg`, so it passed only after the auditor installed ripgrep |
| Call counts | 25 graph and 11 shell stated, and the same counts in the session log |
| Time after the last claim | 151 of 555 seconds (27%), while the agent wrote an 89-line program to check its report format |
| Filler | `fixes.md` and `recommendations.md` held 3.4 KB, largely that nothing applies, for claims with no defect |
| Cost | 65,420 tokens, for 21 KB of reports |

The answers were right, and the agent did real work. It also spent real time on structure, as the owner suspected. The brief standard now has rules against that filler and that program, and against a tool with no full path. These three rules are not tested yet, because the pilot came before them.

## 5. In an agent definition

Add this section to the definition of each agent that reads code:

```markdown
## 6. Check each brief before the agent starts

A pasted standard drifts. On 2026-11-08, a sweep of 48 briefs found 2 with no standard, 3 with placeholders left, and copies of an older text in briefs written after the final version. Thus a script checks each brief before the agent starts:

```sh
python3 ~/.claude/skills/agent-report/scripts/brief_check.py <job>/brief.md --plants ~/.claude/plants/<job>.md
```

It refuses a brief in these cases:

- The first line names no role: `IMPLEMENTER`, `REVIEWER`, `RESEARCHER` or `TESTER`, alone or after `Role: `.
- A line of `brief-standard.md` is missing or out of order, so the copy is not the current version.
- A placeholder `<folder>`, `<job>` or `<graph_root>` is left, outside the instruction line of the standard.
- The part above the standard gives no stop point, no browser rule or no rule against env files.
- The planted answers do not have one `CONFIRMED`, one `REFUTED` and one `NOT REACHED` answer, or they are inside the job folder.

Keep the planted answers in a folder outside the job folders, for example `~/.claude/plants/<job>.md`. A hook of the project can run the script before each agent or `codex exec` start, and refuse the start on exit 1.

## Let a Codex job commit in its clone

The test loop of the brief standard asks for one commit for each defect. Codex `--sandbox workspace-write` lets a job
write files in its clone, but it keeps the `.git` folder of the clone read-only. Then `git add` fails with "Unable to
create '.git/index.lock'", and the job leaves its work uncommitted.

Give the job write access to that one folder:

```sh
codex exec --sandbox workspace-write --skip-git-repo-check -C <clone> --add-dir <clone>/.git --add-dir <report folder> - < brief.md
```

On 2026-11-08 (codex-cli 0.166.0), a job with no such access wrote its files but made no commit. A probe with
`--add-dir <clone>/.git` made the commit. Nothing else outside the clone becomes writable, so do not use
`danger-full-access` for this. If a later step clones the result of a job, commit what the job left first. If you do
not, the next job reads an empty branch. The `approval_mode` settings of `~/.codex/config.toml` approve MCP tools only.
They do not change this rule.

## 7. The arbiter's own research

Research that the arbiter does without an agent follows the same structure, because the next reader cannot tell a fact from an impression in a chat reply. Write it to `<topic>/arbiter/`: `research.md`, `tests.md` and `verdicts.md`, one heading per ID. Label each statement MEASURED, READ FROM CODE, WEB RESULT NOT TESTED or PROPOSAL NOT OPERATED. A short lookup by a fetch agent is a source of the arbiter: quote it with its URL and the date read. A source counts only if it was read in full: a search result summary is not a source. Before you repeat a claim from an agent report, make sure that the agent read its source. If it did not, write an arbiter note and do not relay the claim.

## Read code through the graph

If the project has `.tokensave/` or `.codegraph/`, read code through it, not through grep and whole files.
Pass an absolute `graph_root`, because a disposable clone has no index.
Report the graph calls and the shell calls in your final message.
```

## Anti-patterns

| Do not | Do |
|---|---|
| Tell an agent to report as its last step | Tell it to write after each ID |
| Accept a report because it has the right files | Plant answers, and operate the tests again |
| Trust the call counts of the final message | Count the calls in the session log |
| Ask a Codex job to commit with no write access to `.git` | Pass `--add-dir <clone>/.git` |
| Ask for a section per ID in each file | Ask for a section only where there is something to say |
