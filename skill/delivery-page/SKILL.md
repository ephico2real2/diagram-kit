---
name: delivery-page
description: Render a repository's tracker, handover and resume documents at one commit into one page, with the delivery-page command. If one of the three documents fails, the command writes nothing. Use when the user types /delivery-page. Use when the user asks for a page or a status view of a tracker, a backlog or a handover. Use when the user asks to publish one again after the Markdown changed.
---

# /delivery-page: one page from the tracker, the handover and the resume document

`/delivery-page [repository]` builds one HTML page from three Markdown documents that the repository holds. A reader
sees the state of the delivery, and a new session sees how to pick up the work. If the repository does not make the paths
of the documents clear, ask for them.

## 1. The three documents are required

A delivery page needs all three documents. If one fails, the command names each one that fails and writes nothing.
An earlier page stays as it was.

| Document | Default path | Holds |
|---|---|---|
| Tracker | `docs/backlog/TRACKER.md` | The work, in the order it is done, with the status of each item |
| Handover | `docs/handover.md` | The state at a date: what runs where, what is in flight, and what comes next |
| Resume | `docs/handover.md#Resume prompt` | What a new session reads first. It is a file, or a section of a file: `FILE#Heading` or `FILE#anchor` |

The command refuses a document in these cases:

- The file is not in the commit. A file that is not committed is not seen.
- The file is empty, or holds only white space.
- The file is not UTF-8.
- The file still holds the starter line that `--init` wrote.
- The resume section does not exist, or has no text in it. A heading in a code block is not a section.
- One file is named as both the tracker and the handover, or as the resume document with no section.

If the repository has none of these documents, write the starters, fill them in, and commit them. Never fill them with
text you did not check, because the page then shows that text as the state of the delivery.

```sh
~/.local/share/diagram-kit/.venv/bin/delivery-page --init --repo .
```

`--init` never overwrites a file. If the paths are not the default paths, give it `--tracker`, `--handover` and
`--resume`.

## 2. Render

`delivery-page` is in the kit from 0.2.6 (install it as `/visual` §4 says). Install pandoc as the kit's README says. The page reads only from the commit you name, so name the commit the reader
expects. For the state of the default branch, fetch it first and name the remote's ref.

```sh
git fetch origin main
~/.local/share/diagram-kit/.venv/bin/delivery-page delivery.html --repo . --ref refs/remotes/origin/main
```

| Option | Use it when |
|---|---|
| `--tracker`, `--handover`, `--resume` | A document is not at its default path |
| `--title "Two To Four Words"` | The repository's name does not name the page well |
| `--repo-url https://host/owner/name` | The origin remote is a local path or an SSH host alias |
| `--strip-footer MARKER` | A generator adds a footer to each document. It removes the `---` line before MARKER, to the end |
| `--theme light` | The repository's rule is that its pages are light only. The default holds both themes |

## 3. What the page does with the Markdown

- It shows raw HTML as text, and it drops an HTML comment. A `<details>` block therefore shows as text. The reader of
  this page is often signed in somewhere, and Markdown in a repository can come from any contributor.
- A link keeps only its words if its scheme is not `http`, `https` or `mailto`.
- An image keeps only its words if its scheme is not `http` or `https`.
- It makes a relative link absolute at the commit (`/blob/<sha>/`), and a relative image too (`/raw/<sha>/`). An image
  in a private repository does not load for a reader who is not signed in to it.
- It removes any credential that the origin remote holds, so that it cannot reach the page.
- The same commit and the same pandoc give the same bytes. The page holds no date of its own.

## 4. The summary at the top

If the tracker uses this format, the summary comes from it. A tracker in another format renders with no summary, and
that is not a failure.

```markdown
The backlog holds 310 stories: 89 done, 3 in progress and 218 planned.

### W1: Finish what is in flight (phase 1, 5 of 7 stories done)

| 1 | #123 | open | The title of an open issue |
```

The first line gives the four tiles. Each `###` line gives one row with a bar. A table row that starts with a number and
an issue number counts as an open issue of that wave. The handover's date comes from `**As of YYYY-MM-DD.**`.

## 5. Look at it, then publish it

1. Open the page in a browser. Read the source line under the title: it names the commit.
2. Make sure that the page does not scroll sideways at 390 px, and that the links under the title reach their sections.
3. If you changed the Markdown or the command, look at both themes.
4. Publish the file. In Claude Code, the Artifact tool publishes it privately. In the same session, publish the same
   `file_path`. In a new session, read the existing URL with `action: read`, then publish with `url`, or the tool makes
   a second page.

Render and publish again after each merge that changes one of the three documents. Never edit the page by hand. A hand
edit is lost at the next render, and the page then disagrees with its commit.

## Anti-patterns

| Do not | Do |
|---|---|
| Render from a working tree | Name a commit, and fetch first |
| Remove a starter line to make the command pass | Fill in the document, then remove the line |
| Copy this command into a repository | Install the kit at a pinned tag |
| Add a date or a live status to the page | Keep the state in the Markdown, at a commit |
