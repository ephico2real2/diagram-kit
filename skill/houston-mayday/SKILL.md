---
name: houston-mayday
description: Low-token mode, for a time with almost no Claude tokens. Claude only writes each mission and its definition of done, and rules at the end. Codex does all research, build and code at high effort, or at extra-high effort for work that crosses layers. A second Codex job reviews each result adversarially in a clone of its own. Opus at high effort is the final arbiter. Work built from scratch gets review labels for a later deep review by Opus at extra-high effort and by Fable. Use when the user types /houston-mayday. If Claude tokens are low, also use it. If the user asks Codex to research, build and code with Claude as the arbiter, also use it.
---

# /houston-mayday: Codex builds, Codex attacks, Opus rules

Claude tokens are scarce, so Claude spends them only on three things: the mission, the definition of done, and the
final ruling. Codex does the research, the build, the code and the first review. The real repository changes only
after the ruling.

## 1. Who does what

| Step | Who | Effort | Output |
|---|---|---|---|
| Mission and definition of done | Claude | - | `heads/<job>-r1.md` and `heads/<job>-r2.md`, the planted answers |
| Round 1: research, build, code | Codex | `high`, or `xhigh` for work across layers | Commits in a disposable clone, and the report files |
| Round 2: adversarial review | Codex, a separate job | `high` | Verdicts, fixes and tests, in a clone of round 1's result |
| Round 3: ruling | Opus at high effort (the main session) | high | One ruling per finding, applied and tested |
| Later: the deep review | Opus at extra-high effort and Fable | xhigh | Issues for each finding |

If a job changes more than one of these, it crosses layers: the schema, the API, the service code, the UI, the mobile
app, the infrastructure. Round 1 of such a job uses `xhigh`.

## Briefs: the existing standard, with no new format

This skill changes who does the work, not the brief. Each Codex job gets the same agent brief as every other agent:

- The brief standard of `/agent-report` follows the mission head, unchanged.
- `brief_check.py` checks each brief, with the planted answers in a file outside the job folder.
- If the project has a brief gate, the gate checks each start. A refusal stands: fix the brief.
- `/codex-arbiter` gives the rules for the clones. `/fix-defect` gives the form of each defect that a round finds.

The mission head below is the project part of that brief, above the standard.

## 2. Write the mission (Claude)

Each round has one head file. The kit brief standard of `/agent-report` follows it unchanged. A head has these parts,
in this order:

1. The first line names the role: `IMPLEMENTER` for round 1, `REVIEWER` for round 2.
2. Mission: one paragraph. It names the clone, the branch and the base commit.
3. Inputs: each file with its lines, each issue saved as a file, each rule that the text must follow. Never "review this".
4. Claims: three or more, each with the command that tests it. At least one claim is true, one is false and one cannot be
   reached from the sandbox. The planted answers go in a file outside the job folder.
5. Deliverables (round 1) or claims to attack (round 2), each with the file it changes.
6. Definition of done: each item says how a test or a command shows it.
7. Limits: a stop point (`stop after` the IDs, or a time limit), no browser, no `.env` file, no secret, no push, no
   `gh` write, no install, no lockfile change, keep the line endings. The sandbox keeps `.git` read-only, so the job
   leaves its changes uncommitted and saves each fix as `patches/<ID>.patch`. `run-pair.sh` commits round 1 before round 2.

Save each issue body to `inputs/` with `gh issue view <n> --json number,title,body > inputs/<repo>-<n>.json`, so that
Codex needs no network and Claude does not read the body twice. Lint the head with the project's writing check, then
build and check the brief:

```sh
python3 <kit>/skill/houston-mayday/make_brief.py <folder> <job>-r1 <indexed repository path>
python3 <kit>/skill/agent-report/scripts/brief_check.py <job>-r1/brief.md --plants <plants folder>/<job>-r1.md
```

`make_brief.py` joins the head and the brief standard, and fills `<folder>`, `<job>` and `<graph_root>`.

## 3. Run both rounds as one background job

`run-pair.sh` clones the source repository for round 1, runs Codex, clones round 1's result for round 2,
and runs the reviewer. Each clone has no remote. The folder of the clone has the name of the repository, because some
builds read it.

```sh
CODEX_MODEL=<model> <kit>/skill/houston-mayday/run-pair.sh <folder> <job> <effort r1> <effort r2> \
  <source repository> <repository folder name> <work branch> <base branch>
```

Start it with `run_in_background`, and wait for the one wake-up. Do not poll and do not read the Codex logs. Run one heavy
job at a time. First probe the model: `printf 'Reply with the single word READY.' | codex exec -m <model> --sandbox
read-only --skip-git-repo-check -`.

## 4. Rule (Opus at high effort)

1. Read `status.txt`, then round 2's `verdicts.md`. Open other files only for the ID that you rule on.
2. Audit each round against its planted answers. A wrong planted answer means the report is not trusted. Read more of it.
3. For each finding: read the cited code, accept it, accept it in part, or refuse it, with the reason.
4. Apply what survives to the real work branch, one commit for each, and run the tests yourself.
5. Open the pull request in the project flow. File an issue for each defect that stays open.

## 5. Mark the work for the deep review

When the work builds a service, an API contract or a data exchange from scratch, add two labels to its epic and stories:

```sh
gh label create review:opus-xhigh --color 0b3d91 --description "Waits for an Opus extra-high review when Claude service is back"
gh label create review:fable --color 6f42c1 --description "Waits for a Fable review of API contracts, data exchange and security"
gh issue edit <n> --add-label review:opus-xhigh --add-label review:fable
```

The deep review tests every API contract, every data exchange and the security of the service. After its review is done and each
finding has an issue, remove the label.

## Anti-patterns

| Do not | Do |
|---|---|
| Write code or research in the main session | Write the mission, and let Codex do it |
| Give Codex a vague mission | Name each file, line, claim and the command that tests it |
| Read the Codex log while it runs | Wait for the wake-up, then read `verdicts.md` |
| Trust round 1 because round 2 found nothing | Audit both against their planted answers |
| Merge work built from scratch with no label | Add `review:opus-xhigh` and `review:fable` |
