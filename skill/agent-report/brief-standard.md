# Brief standard for every background agent: reading code and reporting

Paste this into the brief of every agent, of any kind. Codex does not read `CLAUDE.md`, so the brief must hold it. Replace `<folder>` with a folder outside the session scratchpad. Replace `<job>` with the job name, and `<graph_root>` with each indexed repository path.

---

## How you read code

If the project has `.tokensave/`, use tokensave to read code. If it has `.codegraph/`, use CodeGraph. Use grep and whole-file reads only for what they cannot answer.

1. Start with `tokensave_context` and your question in plain English. Use `tokensave_search` for a symbol, or with `literal: true` for exact text. Use `tokensave_callers`, `tokensave_callees` and `tokensave_impact` to trace code.
2. Pass `graph_root` with the absolute path of the indexed repository: `<graph_root>`. The server can have no default project. Then a call with no `graph_root` has no graph to answer from.
3. A disposable clone has no index. For code that you did not change, query the original repository through `graph_root`. For code that you did change, read the files in your clone.
4. Read only the ranges that a result points to. Call `tokensave_read` with `mode` `lines`, `map` or `signatures`. Its default reads the whole file, and the server cuts the answer at 15,000 characters. Tests, builds and logs stay in the shell, with short output.
5. In a Claude agent, tokensave tools can be deferred. Load them once with `ToolSearch`: `select:mcp__tokensave__tokensave_context,mcp__tokensave__tokensave_search,mcp__tokensave__tokensave_callers,mcp__tokensave__tokensave_callees,mcp__tokensave__tokensave_impact`. In Codex they are `mcp__tokensave__*`.
6. In Codex and in the Cursor CLI, the tools have the same names, with no prefix. No extra flag is necessary. The server lists 12 tools. Use `tokensave_context`, `tokensave_search`, `tokensave_callers`, `tokensave_callees`, `tokensave_impact`, `tokensave_files`, `tokensave_body`, `tokensave_read` and `tokensave_status`. In Codex, call `tokensave_more` with an area to get other tools. In the Cursor CLI, you cannot call other tools. In the Cursor CLI, `tokensave_str_replace` and `tokensave_multi_str_replace` are refused. Edit files in the usual way. In a Cursor job with `CURSOR_CONFIG_DIR=~/.cursor-jobs`, the shell and the native read reach only the job folder and its `--add-dir` folders. Read other code through tokensave.
7. CodeGraph tools take `projectPath`, not `graph_root`. Pass the absolute path of a project that has `.codegraph/`. If a CodeGraph call returns `database is locked` or `unable to open database file`, use tokensave or the shell. Do not remove the lock.
8. If a tool is not available or fails, say so in your report with the exact error, and continue with the shell.
9. Your final message states how many graph calls and how many shell calls you made.

## How you report

Write to `<folder>/<job>/` as you work, so that a stop at any moment loses nothing. Keep research and tests apart from your opinions. An arbiter reads `verdicts.md` first, and opens the other files only for the claim it needs.

| File | Holds | Does not hold |
|---|---|---|
| `plan.md` | The claims or defects, by ID, in your order. Write this first | Results |
| `research.md` | Per ID: each source with its URL or `file:line`, a short quote, what it establishes, and the options you rejected, with why | Your verdict or a fix |
| `tests.md` | Per ID: the exact command, the commit, the environment, the real output, and the exit status. Save long output in `logs/`, and name the file | Interpretation beyond what the output shows |
| `verdicts.md` | One table row per ID: ID, verdict, one-line reason, and links to its research, test and fix sections | Evidence that belongs in the files above |
| `fixes.md` | Only for an ID with a defect: root cause, the full fix code, the test code, and its result before and after. Patches go in `patches/<ID>.patch` | A choice that belongs to the owner |
| `recommendations.md` | Only for an ID with a real choice: suggestions and owner choices, each option with its measured result, and your recommendation. Findings outside the brief go here too | Anything stated as a fact without a link to its evidence |
| `resume.md` | The ID you work on now, what is done, what is next, what is running, and which folders, branches and containers to reuse. Rewrite it after each ID | History |

Rules:

1. After each ID, before you start the next, append to each file that it touches, then rewrite `resume.md`. Do not hold results for the end.
2. Use one heading per ID, in the form `## <ID>`, in each file that has something to say about that ID. Do not write a section that says only that nothing applies.
3. A verdict is one of CONFIRMED, REFUTED, PLAUSIBLE or NOT REACHED. Label each statement MEASURED, READ FROM CODE, WEB RESULT NOT TESTED, or PROPOSAL NOT OPERATED.
4. Do not write a verdict with no test or source behind it. A claim that you did not reach stays NOT REACHED.
5. Your final message is short: the tally of verdicts, and the path of `verdicts.md`.
6. Keep command output short, and send long output to `logs/`.
7. Stop at the limit that the brief gives. If it gives none, stop after the IDs in `plan.md`.
7. Spend your time on the claims. Do not write a program to test the format of these reports.
8. A claim in this brief can be false, and some claims cannot be tested from here. Do not assume that a claim is true because the brief states it.
9. In `tests.md`, give the full path of each tool that a test runs, and its folder. Another person must be able to run it again.
