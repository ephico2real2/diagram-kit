---
name: resume-work
description: "Restart the work after a new session, /resume, /compact, auto-compact or /clear, from the files and not from the conversation. It reads the handover note and the tracker first. Then it makes sure that they agree with the real state: git, CI and pull requests, running services and the environment. Where reality differs, it corrects them. It starts each background job of the note that is not running again, and never a second copy. Then it continues from the next step without questions, unless an open item needs the user. If no note exists, it builds one from the tracker, git and CI. Use when the SessionStart hook prints 'RESUME after', or when the user types /resume-work. Also use it for a request to continue the work after a break."
---

# /resume-work: continue from the files, after any restart

The SessionStart hook of the `handover` skill starts this skill. It fires for `startup`, `resume`, `clear` and
`compact`, so it also fires after an auto-compact. Its text begins with `RESUME after '<source>'` and holds the note, a
tracker summary, git and the state of each Running job. This skill owns no file. It corrects the note through the rules
of `handover`, and the tracker through the rules of `build-tracker`.

## 1. Read, before anything else

1. The handover note, `claude-resumes/HANDOVER-<topic>.md`, in full. The topic is in `claude-resumes/CURRENT`. The hook text can be shorter than the file.
2. The tracker, `claude-resumes/TRACKER-<topic>.md`.
3. If the hook reported a failed check, or the files look wrong, the newest copy in `claude-resumes/.snapshots/`.

Do not change a file, start a job or call a tool that writes before step 2 is done.

## 2. Make sure that the files agree with reality

| Fact | Command |
|---|---|
| Branch, changes and the latest commits of each repository of `- Repos:` | `git -C <repo> status -sb` and `git -C <repo> log --oneline -5` |
| Pull requests and CI | `gh pr list --author @me`, `gh pr checks <n>`, `gh run list -L 5` |
| Running services and dev servers | the probe of each Running line, and `lsof -i :<port>` or the health URL of the service |
| The environment in use | the environment of `## Context`: its configuration file, its current context (`kubectl config current-context`), or its health URL |

Where the note or the tracker differs from reality, trust reality. Correct the note and the tracker at once, and tell
the user in one sentence for each difference: what the note said, what is true, and how you checked it.

## 3. Bring back the jobs

Background tasks of Claude Code can end with /clear, and the docs do not promise that they survive. For each line of
`## Running`:

- `alive`: leave it. Never start a second copy of a job that still operates.
- `NOT RUNNING`: read its output or status file first. If its work is done, record the result in the tracker and remove the line. If not, start it again with its restart command, and write the new probe into the line.
- `task` or `unknown`: look at `/tasks` and at the output file of the job. If neither shows it alive, treat it as not running.

## 4. Continue

Continue from the first item of `## Next steps`, without questions. If an item of `## Open` blocks that step, ask the
user. Ask nothing else. Then follow `handover` (section 3) and `build-tracker` (section 2) as the work goes on.

## 5. If there is no note

Say so in one sentence. Then build the note from the tracker, `git log`, `gh pr list` and `gh run list`. Use the form
of `handover` (section 2), and write the topic into `claude-resumes/CURRENT`. If there is no tracker either, make it
from the open issues and pull requests of the topic (`build-tracker`, section 1). Then continue at section 2 of this
skill.
