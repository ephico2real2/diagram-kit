---
name: handover
description: "Record the state of a long piece of work so that a new session, after /clear or a context reset, resumes it alone. It updates the handover and status documents in the repository, the resume note in memory and RESUME-PROMPT.md, saves unfinished work in commits, checks each path and number, and gives the resume prompt in the reply. Use when the user types /handover, asks to update the handover, the status or the resume documents, asks for a resume prompt, or says that they will clear the session. Also use it before a long stop of autonomous work."
---

# /handover: a new session resumes the work with no help

`/handover` records where the work stands and gives the user one prompt to paste after `/clear`. The new session knows only what the files and the prompt tell it. Write each item so that a reader with no memory of this session can act on it.

## 1. Collect the state from facts

Do not write the state from memory of the conversation. Get each fact from a command, and keep the output.

```sh
git -C <repo> status -sb                       # branch, ahead or behind, changes not committed
git -C <repo> log --oneline -1                 # head of each branch that the work uses
gh pr list -R <owner>/<repo> --author @me      # open pull requests and their CI
gh issue list -R <owner>/<repo> --label <set>  # new issues, their milestone and status label
date -u +%H:%M                                 # the time of the state, in UTC
```

Also list:

- Each background job or agent that operates now, with its folder and how to read its result.
- For a project that numbers its findings: the next free ID of each prefix.
- Each decision that the user made in this session, in the user's words.
- What is done but not pushed, and what is pushed but not merged.

## 2. Save the work that is not committed

A cleared session loses each change that is only in a scratch folder. It also loses each idea that is only in the chat.

- Commit unfinished work on its working branch, with a message that says what is still to do. If the project rules do not allow the push, do not push it.
- Copy each draft from the session scratchpad into the project handoff folder. The scratchpad of the next session is a different folder.
- Never commit a secret, a private host name or an artifact URL. An artifact URL goes only into memory.

## 3. Update the documents of the repository

The repository documents are the record that other people read. Use the change flow of the project, for example a pull request with its template, milestone and labels.

1. Handover document: add a section `State on <date>, <time> UTC` at the top of its "Start here" part. Change the "state is from" line at the top too.
2. In that section, write what changed since the last state section. Then write the next steps as a numbered list, in order. Each step names its file, branch, issue or job, and the command to start it.
3. Say that this section replaces the next steps of the older sections. Old steps that are done or dropped stay below as history.
4. Status document or build tracker: add the new issues with their milestone and status. Add a row for each piece of work in progress. Change its state time.
5. If the project keeps the same file in more than one repository, copy it and compare the copies with `cmp`.
6. Lint the changed files with the rules of the project. Compare the count with the count before the change, and fix each new hit.

## 4. Update memory

1. Append a block `## LATEST STATE <date> <time> UTC (read this first)` to the resume note. Do not edit the older blocks: they are the history. If an older block is wrong, say so in the new block.
2. The block holds the heads, the open pull requests and how to finish them, and the jobs in operation. It also holds the next free IDs, what is not pushed, and the next steps in short form.
3. Put each decision of the user into the note of its subject, not only into the resume note. Add the link with `[[name]]`.
4. Update the line of each changed note in `MEMORY.md`, for example the time of the last block.

## 5. Write RESUME-PROMPT.md

Write it in the project handoff folder, and replace the old text. Use this shape:

```text
Resume <the work> in <absolute project path> and work autonomously.

Read these first, in this order:

1. The LATEST STATE block at the end of the memory note <resume note>.
2. The section "State on <date>, <time> UTC" in <handover path>, on the branch <branch>. Its numbered steps are the work, in order.
3. The memory notes <names>, for <the decisions they hold>.

Check before you start: <each item that was pending at the handover, such as a pull request whose CI was running, or a job that was operating>. If <its condition>, <the action>.

Rules for this run:

- <the change flow: branches, pull requests, milestones, labels, what to update in the same change>
- <what must never be touched or called: branches, hosts, cloud accounts, secrets>
- <who writes code, who reviews, who rules, and which models are not used>
- <the defect and test loop>
- <the commit attribution rule>
- <each action that needs the user's yes first>

First tell me in 3 lines where things stand. Then start <step 1, named>.
```

Rules for the prompt:

- Take the rules from the memory notes and the instruction files of the project. Do not take them from the memory of this session. A rule that the user gave only in the chat goes into a memory note first.
- Write each pending item as a condition, because the next session does not know its result.
- Name files by their absolute path or by their path from the project root.
- Do not put an artifact URL or a secret in the prompt. Name the memory note that holds the URL.
- Keep the prompt short. The handover and memory hold the detail, and the prompt only points to them.

## 6. Check the handover before you report it

- Each path in the prompt and in the new handover section exists: `ls` each one.
- Each pull request and issue number resolves: `gh pr view <n>` and `gh issue view <n>`.
- The commits of step 2 exist on their branches, and the working tree has no change left that matters.
- The resume note ends with the new block, and `MEMORY.md` names its time.
- Read the prompt once, as a new session reads it. Each "read", "check" and "start" must point to something that exists.

## 7. Report

Give the prompt in a code block, so the user can copy it. Give the absolute path of RESUME-PROMPT.md too. Say what is still pending, such as CI that operates or a merge that waits for the user. If the session continues, finish the pending items. If a later step changes the state, update the handover again before the session ends.

## Why each rule exists

These cases come from a client review on 2026-11-07.

| What happened | Rule |
|---|---|
| The handover document was 9 hours older than the work, because each update went only to the tracker | Step 3 updates the handover in each change of state |
| The old resume prompt told the next session to ask a question that the user had already answered | Step 5 replaces the whole prompt each time |
| A helper script was first written in the session scratchpad | Step 2 copies each draft and script to the handoff folder |
| The handover went out while CI still operated on its own pull requests | Each pending item is a condition in the prompt |
| The owner rule says that an artifact URL is never committed | The URL goes only into memory, and the prompt names that note |
