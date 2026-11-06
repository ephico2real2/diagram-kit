---
name: tokensave-fork
description: Install and operate the tokensave2 fork beside upstream tokensave. It tells which build an agent runs and how to point Codex, Cursor or Copilot at the fork. It gives the permissions for the graph tools and the update steps. It also gives a test with a real query and an audit of the log of the agent. Use when the user types /tokensave-fork, or before `tokensave doctor`, `install`, `reinstall` or `upgrade`. Also use it for a new agent, and for a graph tool that Codex or Cursor refuses.
---

# /tokensave-fork: the graph tools for each agent

The fork [ephico2real2/tokensave2](https://github.com/ephico2real2/tokensave2) adds token accounting for more agents and a local dashboard. Its guide is `docs/FORK-GUIDE.md`. Read the guide before you change an install.

| Item | Value |
|---|---|
| Checkout | `~/gitRepos/tokensave` |
| Fork binary | `~/.cargo/bin/tokensave` |
| Upstream binary | `/opt/homebrew/bin/tokensave`, from the tap `aovestdipaperino/tap` |

Do not run `tokensave upgrade`. The command writes the upstream release over the binary that runs it, and this replaces the fork.

## Install from nothing

These steps are for macOS. Each step has a check.

1. Install the dependencies. The fork needs git and rustup. Node is not necessary. `brew install ripgrep` gives `rg`. Tokensave does not operate `rg`. You need it because an agent can record a test that uses `rg`, and an auditor must operate that test again. On 2026-11-06, one test of a Codex agent failed for the auditor until this install.

   ```sh
   brew install git rustup ripgrep
   rustup toolchain install 1.98.1
   rustup toolchain list
   ```

2. Clone the fork.

   ```sh
   git clone https://github.com/ephico2real2/tokensave2.git ~/gitRepos/tokensave
   ```

3. Build it from inside the checkout. The build took 3 minutes on an M-series Mac. Homebrew's rustup is keg-only, so `cargo` is not on `PATH`, and `ls ~/.rustup/toolchains` gives the name of the folder. Two warnings about `rust-objcopy` are harmless.

   ```sh
   cd ~/gitRepos/tokensave
   PATH="$HOME/.rustup/toolchains/1.98.1-aarch64-apple-darwin/bin:$PATH" cargo install --locked --path .
   ~/.cargo/bin/tokensave dashboard --help > /dev/null && echo 'fork: ok'
   ```

4. Operate `sh scripts/fork-path.sh`, and operate the shell commands that it prints.
5. Connect the agents. If an agent already names another build, use section 2.

   ```sh
   ~/.cargo/bin/tokensave install --agent claude --agent codex --agent cursor --git-hook no
   ```

6. Add the Cursor approvals, and make the configuration folder for Cursor jobs. The first script asks the server for its read tools, and it keeps the other keys of the file. Section 3 gives the use of the second script.

   ```sh
   python3 "${CLAUDE_SKILL_DIR}/cursor-allow.py"
   python3 "${CLAUDE_SKILL_DIR}/cursor-job-config.py"
   ```

7. Index each project. Git does not track `.tokensave/`.

   ```sh
   cd <project> && tokensave init
   ```

8. Do the test in section 4.

Steps 3 to 7 passed on 2026-11-06, in a scratch folder and a throwaway `HOME`, for Codex and Cursor. In step 1, only `brew install ripgrep` was operated. A clean Mac is not tested.

These two items are optional:

- `codex features enable mcp_tool_list_changed`. Tokensave works with no feature. Section 3 says what it adds.
- `brew install ast-grep`. It adds one edit tool, `tokensave_ast_grep_rewrite`. The other tools do not need it.

## 1. Tell the builds apart

`tokensave --version` prints the same version for both builds. Use these commands:

```sh
sh ~/gitRepos/tokensave/scripts/fork-path.sh
~/.cargo/bin/tokensave dashboard --help > /dev/null && echo 'fork: ok'
```

The script changes no file. It prints the binary that each agent configuration names. Only the fork has the `dashboard` command.

Use the full path for `~/.cargo/bin/tokensave doctor`, because a plain `tokensave` can find Homebrew first. The Homebrew `doctor` reported the rules of the fork as drifted. Each report and test must name the binary that it used.

## 2. Point an agent at the fork

1. Wait until no agent job that uses that configuration is in operation.
2. Copy the configuration files of the agent to a backup.
3. Operate the commands that `fork-path.sh` prints. They have this form:

```sh
"$HOME/.cargo/bin/tokensave" uninstall --agent codex --keep-git-hooks
"$HOME/.cargo/bin/tokensave" install --agent codex --git-hook no
```

4. Compare the configuration with the backup by its meaning. The Codex commands write `config.toml` through a TOML parser, so comments and order can change. On 2026-11-06, only `tokensave` `command` values changed. The rules block moved in `~/.codex/AGENTS.md`.
5. Operate `fork-path.sh` again. Each agent must show `runs the fork`.
6. Do the test in section 4.

`tokensave reinstall` is not sufficient, because it keeps an MCP command that still works. A session that is already open keeps its old build until it starts again.

## 3. The permissions that an install does not write

An agent with no approval has the tools in its list, but each call fails. A permission error does not show a dead server.

| Agent | File | Entry | Error with no entry |
|---|---|---|---|
| Cursor CLI | `~/.cursor/cli-config.json`, `permissions.allow` | `Mcp(tokensave:tokensave_<tool>)` for each read tool, and `Mcp(codegraph:*)` | `User rejected MCP: tokensave-tokensave_search` |
| Codex | `~/.codex/config.toml` | `[mcp_servers.codegraph.tools.codegraph_<tool>]` with `approval_mode = "approve"` | `MCP tool call requires approval, but approval policy is never` |

The tokensave install writes the approvals for tokensave in the Codex file. It writes no Cursor allow entry, so operate `cursor-allow.py`.

In 7.16.0, the Cursor list has 74 entries: `tokensave_more` and the 73 tools that declare `readOnlyHint`. Section 8 of the fork guide holds the list. Do not allow the 13 other tools, because they edit files, record session data or operate tests. Do not use `Mcp(tokensave:*)` or `--force` to get past a refusal.

If the server is in `~/.cursor/mcp.json`, Cursor needs no extra flag. A server in a project `.cursor/mcp.json` needs an approval once for each folder, with `--approve-mcps` or `cursor-agent mcp enable tokensave`.

### Give a Cursor job its shell, and limit it to one folder

A headless Cursor call in allowlist mode refuses each shell command that is not in the list, also `echo hello`. Do not add shell commands to the list one by one, and do not use `--force`. Use the sandbox, and choose the folder in each call:

```sh
python3 "${CLAUDE_SKILL_DIR}/cursor-job-config.py"
CURSOR_CONFIG_DIR=~/.cursor-jobs cursor-agent -p --trust --sandbox enabled --workspace <job folder> \
  --add-dir <report folder> --output-format stream-json "$(cat prompt.txt)" > job.jsonl
```

The script copies the main configuration to `~/.cursor-jobs` with `sandbox.readBoundary` set to `workspace`, and with no account data. Operate it again after each change to the allow list.

| Action in the job, on 2026-11-06 | Result |
|---|---|
| `git`, `python3` and `rg` in the job folder | Ran with no prompt |
| Native write tool in the job folder | Wrote the file, with no `--force` |
| Shell write and read in the `--add-dir` folder | Worked |
| Shell write outside these folders | `Operation not permitted`, and no file |
| `cat` and `rg` on the indexed project | `Operation not permitted` |
| Native read of the indexed project | `Permission denied` |
| `tokensave_read` and `tokensave_search` on the indexed project | Answered |

Do not set `sandbox.readBoundary` in `~/.cursor/cli-config.json`. A plain call with no sandbox then also got `Permission denied` outside its folder, so the setting limits each Cursor session. A plain call with the main file still reads the whole project, so a job must use both the variable and the flag.

- Put a disposable clone in the job folder, because the agent can read and test only there. A symlink that points out of the folder is not tested.
- The exit status does not show a refusal in a pipe: `cat <file> | wc -c` exits 0 and prints 0. Read stderr.
- `curl https://example.com` was refused with the sandbox and no read boundary. This setup does not give network access, and a way to grant it is not tested.

### Do you need the Codex feature?

No. By default, the server lists 12 tools, and 10 of them read code. These tools work from Codex and from Cursor with no feature. With the prefix `tokensave_`, they are `context`, `search`, `callers`, `callees`, `impact`, `files`, `body`, `read`, `status` and `more`.

The feature matters only for the other tools. After a call to `tokensave_more`, `cursor-agent` and `codex exec` do not act on `notifications/tools/list_changed`, so the other tools stay out of reach. Cursor answers `Tool tokensave-tokensave_node was not found`. Two ways past it were tested on 2026-11-06:

- Set `TOKENSAVE_TOOLS` to `full` in the `env` of the server. The README gives about 89 KB of schema for each turn.
- For Codex only, operate `codex features enable mcp_tool_list_changed`. `codex features list` shows this feature as under development. A Codex agent then calls `tokensave_more` with an area, and the tools of that area are available. To remove it, operate `codex features disable mcp_tool_list_changed`.

If the 10 read tools are sufficient, keep the default.

## 4. Prove it with a real query

Operate each test from an empty folder, as an agent in a disposable clone does. Replace `<root>` with the absolute path of an indexed project.

```sh
P='Call the MCP tool tokensave_search with query "main" and graph_root "<root>". Use no other tool. Print the file path of the first result, or the exact error.'
cursor-agent -p --trust --workspace "$PWD" "$P"
printf %s "$P" | codex exec --sandbox workspace-write --skip-git-repo-check -C "$PWD" -
```

While the test is in operation, read the binary with `ps -axo command= | grep '[t]okensave serve'`.

Also ask Cursor to call `tokensave_str_replace` on a scratch file. The result must be a refusal, and the file must not change.

### Prove that the agent uses tokensave and reads slices

The test above names the tool, so it proves only that the tool answers. It does not show what an agent does with an open question. A call to `tokensave_read` also proves nothing alone, because its default mode is `full`. After you connect an agent or change the brief standard, do this test.

1. Choose a symbol in an indexed file of more than 15,000 characters. Find the answer yourself first.
2. Make `prompt.txt` from the section "How you read code" of the brief standard and one open question. Name no tool in the question:

   ```text
   What does <Class.method> in <file> do, and which code calls it?
   Answer in three sentences, with file and line numbers. Change no file.
   ```

3. Operate each agent from an empty folder, so that each read of the project must name its root.

   ```sh
   CURSOR_CONFIG_DIR=~/.cursor-jobs cursor-agent -p --trust --sandbox enabled --workspace "$PWD" --output-format stream-json "$(cat prompt.txt)" > cursor.jsonl
   codex exec --json --sandbox workspace-write --skip-git-repo-check -C "$PWD" - < prompt.txt > codex.jsonl
   ```

4. Audit each log. The script reads these JSON streams, and not the session files in `~/.codex/sessions`. For a real job, add the same flags to audit it.

   ```sh
   python3 "${CLAUDE_SKILL_DIR}/tool-use-audit.py" codex.jsonl --root <root>
   python3 "${CLAUDE_SKILL_DIR}/tool-use-audit.py" cursor.jsonl --root <root>
   ```

   A PASS needs an answer from a tool that reads code, no `tokensave_read` in mode `full`, and no slices that cover a whole file. It also needs no shell reader such as `rg` or `cat` that names the root, and no native read inside the root.

5. Compare the answer of the agent with yours. The audit shows how the agent read, and not whether the answer is correct.
6. Operate one control. Ask the agent to call `tokensave_read` with only `file` and `graph_root`. The audit must print FAIL. If it prints PASS, the test proves nothing.

Results on 2026-11-06, for a file of 927 lines and 69,921 bytes:

| Run | Audit | What the log shows |
|---|---|---|
| Codex, open question | PASS | 7 graph calls, 1 shell call that read no code, 47 of 927 lines of the file |
| Cursor, open question | PASS | 7 graph calls, no shell call, 20 of 927 lines of the file |
| Codex and Cursor, `tokensave_read` with no `mode` | FAIL | 15,298 characters, and the file stops at line 234 with `[... truncated at 15000 chars]` |
| Codex, told to operate `rg` and `cat` | FAIL | Both ran, and `cat` returned all 69,921 bytes |
| Cursor, told to use its native read | FAIL | The read succeeded, on the whole file |
| Cursor, told to operate `rg` | FAIL | No graph call, and each shell call was refused, also `echo hello` |
| Cursor job in its own folder, open question | PASS | 5 graph calls, no shell call, and the shell and native read cannot reach the project |

Both open answers named the correct method and call site. One run shows that an agent can follow the brief, and it does not show a rate. Audit real jobs too.

## 5. How agents call the tools

- Tokensave takes `graph_root`. CodeGraph takes `projectPath`. Give an absolute path, because a disposable clone has no index.
- Codex and the Cursor CLI use the same tool names, with no prefix.
- If you give no `mode`, `tokensave_read` reads the whole file. The server stops each answer at 15,000 characters and writes `[... truncated at 15000 chars]`. The agent then pays for a large read and sees only the start. Pass `mode` `lines`, `map` or `signatures`, or call `tokensave_body` for one symbol.
- The hook `hook-pre-tool-use` does not hold an agent to the graph by itself. Pipe `rg <name> src` to the hook from a folder in the project. A name in the index gets `deny`, and a name that is not gets `allow`. From an empty folder, each name gets `allow`. Cursor names this hook, but `rg` still ran in one Cursor job with the project as its workspace. The cause is not proved. Codex names no such hook, and it operated `rg` and `cat` with no refusal.
- The job folder holds a Cursor job to the graph. For Codex, only the brief and the audit do so. Codex can still read the whole file with `cat`.
- The brief standard of `/agent-report` holds this text for each brief. Paste it, because Codex does not read `CLAUDE.md`.

## 6. CodeGraph

Use tokensave for agents. These are the results on one Mac with CodeGraph 0.6.8, on 2026-11-06:

- The native `better-sqlite3` module is absent, so CodeGraph uses a WASM SQLite backend.
- After an agent run, `.codegraph/codegraph.db.lock` stayed with no process that held it. Each client then failed with `database is locked` until the lock was removed. This occurred on 2 different indexes. The cause is not proved.
- An index with WAL journal mode, written by an earlier version, failed with `unable to open database file`. The cause is not proved.
- npm shows version 1.6.2. An upgrade is not tested.

Do not remove a lock in a project that another agent uses. `.codegraph/` stays out of git.

## 7. Update the fork

```sh
cd ~/gitRepos/tokensave
git pull --ff-only
cargo install --locked --path .
```

Then restart the agent sessions, and do the test in section 4.
