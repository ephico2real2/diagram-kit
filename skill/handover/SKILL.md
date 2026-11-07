---
name: handover
description: "Keep the working state of a piece of work on disk at all times, so that /compact, auto-compact and /clear lose nothing. It owns the note claude-resumes/HANDOVER-<topic>.md, the pointer claude-resumes/CURRENT and the self-check scripts/handover.py. It also owns the four Claude Code hooks that make it automatic: Stop, PreCompact, SessionStart and PostToolUse. For a long stop, it also writes the handover document of the repository, the resume note in memory and RESUME-PROMPT.md. Use when the user types /handover, or asks to update the handover or the resume documents. Also use it for a resume prompt, and before a /clear or a /compact. Use it after a failed check of the Stop hook. Use it for the hooks of a new project."
---

# /handover: the working state is always on disk

The files are the source of truth, not the conversation. /compact, auto-compact and /clear can happen at any time. So
each fact that the next context needs must be on disk before they happen. The hooks below make this automatic: they do
not depend on the model remembering it, or on the user asking for it.

## 1. The three skills and their files

Each skill owns one job. They know each other by name and share one folder, `claude-resumes/` at the project root. Keep
the folder out of git: add it to `.gitignore`, or use a project root that is not a repository.

| Skill | Owns | Files |
|---|---|---|
| `handover` (this skill) | The current working state, and the hooks | `claude-resumes/CURRENT`, `claude-resumes/HANDOVER-<topic>.md`, `scripts/handover.py`, `claude-resumes/.snapshots/` |
| `build-tracker` | Progress: each unit of work, its status and its evidence | `claude-resumes/TRACKER-<topic>.md`. Also the published tracker of a project that has one |
| `resume-work` | The restart after a new session, /compact, auto-compact or /clear | No file of its own. It reads the other files and corrects them through the other two skills |

A topic is one feature, story, issue or release. `CURRENT` holds one line: the name of the active topic. The hooks read
it to find the note and the tracker. To change topic, write the new name into `CURRENT`.

## 2. The note

Path: `claude-resumes/HANDOVER-<topic>.md`. Line 2 has a fixed form, because the self-check reads it:

```text
# Handover: <topic>
Last update: item <n> of <total> (<what>), <YYYY-MM-DD HH:MM> UTC (<HH:MM> <local zone>). Next: <the exact next step>.
```

`<n>` is the number of the unit in progress in the tracker. If no unit is in progress, it is the number of done units.
`<total>` is the number of units in the tracker. UTC is the standard: git, CI and the hooks use it, and it has no
daylight saving change. Take it from `date -u +"%Y-%m-%d %H:%M"`. The local time in parentheses is for the reader,
from `date +"%H:%M %Z"` (for example `16:12 CST`). The self-check compares only the UTC time.

Then these sections, in this order:

| Section | Holds |
|---|---|
| `## Context` | The goal, the ticket or story links and their acceptance criteria. Then one line each: `- Repos: <path>, <path>`, `- Branch:`, `- Environment:`, `- Tracker: claude-resumes/TRACKER-<topic>.md`. Name access by path or by name only: never a secret, a token or a password |
| `## Done` | A short summary. The tracker holds the details |
| `## Now` | The current state, and what was checked and how (the command and its result) |
| `## Next steps` | The exact next command or action, with file paths. The next step comes first |
| `## Running` | One line per background job, watcher, dev server or CI run: `- <id> \| <probe> \| <purpose> \| restart: <command>` |
| `## Temporary changes` | Debug code, flags, mocks, skipped tests, local configuration, test data, stashes, scratch branches: what each one is, where it is, and how to undo it |
| `## Open` | Decisions that wait for the user, blockers, risks and questions |

The probe of a Running line tells the hooks how to see whether the job is alive:

- `pid <n>`: a process.
- `pidfile <path>`: a file that holds the process ID. A long job writes it first, for example `echo $$ > claude-resumes/.pids/<id>; exec bash run.sh`.
- `task`: a background task of Claude Code. No hook except Stop can see these tasks, so prefer a pidfile for a job that must survive /clear.

A short, current note is better than a full, stale one. Keep it under 6,000 characters, because the SessionStart hook
puts it into a context that takes at most 10,000.

## 3. When to write it

Write the note at each point where a lost conversation loses work:

- After each unit of work, together with the tracker (`build-tracker`).
- Before and after a long or risky step: a migration, a deploy, a force push, a long test run.
- When a background job starts or stops.
- When a decision is made, in the words of the person who made it.
- When a temporary change is made or undone.

Each time, rewrite line 2 and the sections that changed. Do not append a history: the tracker and git hold it.

## 4. The self-check

```sh
python3 ~/.claude/skills/handover/scripts/handover.py check [<topic>]
```

It reads only and prints one line for each failure. If there is a failure, it exits 1. It fails in these conditions:

- Line 2 is missing or has the wrong form, or its time is older than `HANDOVER_MAX_AGE_MIN` minutes (default 30).
- A repository of `- Repos:` has a commit that is newer than line 2.
- A section is missing, or the sections are not in the order above.
- The tracker changed after the note, or line 2 does not agree with the tracker (the total, or the item in progress).
- The tracker breaks a rule of `build-tracker`: a status or a phase that is not allowed, two units in progress, a done unit with no evidence or no UTC time.
- The note holds what looks like a secret: a token shape, a private key, `password=<value>`, or a password in a URL.

## 5. The hooks

Put them in the project configuration file, `.claude/settings.json`, with the `update-config` skill, and show the diff to the
user before you save it. The hooks run `scripts/handover.py`, through the link `~/.claude/skills/handover`.

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [{ "type": "command", "command": "\"$HOME/.claude/skills/handover/scripts/handover.py\" stop", "timeout": 10 }] }
    ],
    "PreCompact": [
      { "matcher": "manual|auto",
        "hooks": [{ "type": "command", "command": "\"$HOME/.claude/skills/handover/scripts/handover.py\" precompact", "timeout": 10 }] }
    ],
    "SessionStart": [
      { "matcher": "startup|resume|clear|compact",
        "hooks": [{ "type": "command", "command": "\"$HOME/.claude/skills/handover/scripts/handover.py\" session-start", "timeout": 10 }] }
    ],
    "PostToolUse": [
      { "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "\"$HOME/.claude/skills/handover/scripts/handover.py\" post-tool", "timeout": 5 }] }
    ]
  }
}
```

| Hook | What it does |
|---|---|
| Stop | After each turn, it operates the self-check. It also makes sure that each live background task of the `background_tasks` input is in Running. If one fails, it prints `{"decision": "block", "reason": ...}`, and the model updates the note and the tracker, then stops. If `stop_hook_active` is true, it lets the turn stop. Thus it blocks once and never loops |
| PreCompact | For `manual` and `auto`, it copies the note and the tracker to `claude-resumes/.snapshots/<UTC time>-<trigger>/`. Claude Code uses the stdout of this hook as instructions for the summary. So the hook prints the topic, the paths and each failure of the check there. It never blocks the compaction |
| SessionStart | For `startup`, `resume`, `clear` and `compact`, it prints JSON with `additionalContext`: the note, a tracker summary, the branch, changes and head of each repository, the state of each Running job, and any failure of the check. That text starts the `resume-work` skill in the new context |
| PostToolUse | It reads each Bash call. After a commit, a push, a merge, a pull request or a deploy, it tells the model to record the evidence |

Each hook reads only, except for the snapshot copy. Each one takes well under a second (the kit test asserts under
two). If all is well, each one is silent. Each one is also silent in a project that has no `claude-resumes/` folder.

Facts from the Claude Code hooks reference (https://code.claude.com/docs/en/hooks, read on 2026-11-07):

- Stop input has `stop_hook_active` and `background_tasks`. Claude Code also stops a stop hook after 8 continuations in a row.
- PreCompact input has `trigger` (`manual` or `auto`). The stdout of exit 0 becomes the summary instructions, at most 10,000 characters, and a `systemMessage` is dropped.
- SessionStart sources are `startup`, `resume`, `clear`, `compact` and `fork`. Text over 10,000 characters goes to a file with a preview of 2,000.
- Edits of a configuration file are normally picked up by the file watcher. If `/hooks` does not show the change, start a new session.
- The docs do not say whether background tasks survive /clear or /compact. So the SessionStart hook reports each Running job with its probe, and `resume-work` starts each job that is not running again.

## 6. A long stop, or a handover to a person

The note is for the next context. A person, or a session on another day, also needs the record of the repository:

1. Collect the state from commands, not from memory: `git status -sb`, `git log --oneline -1`, `gh pr list`, `gh issue list`, `date -u`.
2. Commit unfinished work on its working branch, with a message that says what is still to do. Copy each draft from the session scratchpad into the project handoff folder. Never commit a secret, a private host name or an artifact URL.
3. Add a section `State on <date>, <time> UTC` at the top of the handover document of the repository, with what changed and the numbered next steps. Use the change flow of the project.
4. Append a block `## LATEST STATE <date> <time> UTC (read this first)` to the resume note in memory. It points to the note and the tracker, and does not copy them.
5. Replace `RESUME-PROMPT.md` in the handoff folder: what to read first, the pending items as conditions, and the rules of the run. Name an artifact URL only by the memory note that holds it.
6. Make sure that each path, pull request and issue in the prompt exists (`ls`, `gh pr view`, `gh issue view`). Give the prompt to the user in a code block.

## Why each rule exists

| What happened | Rule |
|---|---|
| A handover document was 9 hours older than the work, because each update went only to the tracker | If the note is older than the tracker or the newest commit, the Stop hook blocks |
| A resume prompt told the next session to ask a question that the user had already answered | Each decision goes into the note at once, and each handover replaces the whole prompt |
| A helper script was first written in the session scratchpad, which the next session cannot see | Drafts and scripts go to the handoff folder |
| A handover went out while CI still operated on its own pull requests | Each CI run is a Running line, and each pending item is a condition |
| A handover that depends on the model remembering it is skipped under load | Four hooks make it automatic, and the self-check is a script |
