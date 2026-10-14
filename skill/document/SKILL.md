---
name: document
description: Make a Word (.docx) document from Markdown with pandoc and the kit's doc-docx command - the Markdown stays the source, the .docx is generated, styled in the kit's palette, its links kept inside the document, byte-reproducible so CI can compare it, and looked at before it is delivered. Use when the user types /document, or asks for a Word document, a .docx, or a document "for people who use Word" made from a guide, a checklist, a runbook or any Markdown in a repository.
---

# /document — a Word document that is the Markdown, never a second copy

`/document <which Markdown, for whom>` builds the Word file from Markdown that already exists. Ask a question only
when it is unclear which files make up the document, or in which order.

Proven on openshift-rbac-automation's developer onboarding guide (2026-10-13). Every rule here exists because breaking
it produced a defect.

## 1. The Markdown is the source

- **Never edit the .docx.** Change the Markdown and build again. A hand-edited Word file drifts from the repository
  the first time anyone fixes a typo in only one of them.
- **One document can be several files.** A guide and its checklist, joined in the order given, each after a page
  break. Each file needs a level-1 heading: it is where links to that file land.
- **Links between the files stay inside the document.** `guide.md#a-heading` becomes a link to that heading, and a
  link whose text is just the file's name takes the file's title (a Word reader never sees `guide.md`). Each file
  keeps its own headings, as on GitHub: a heading two files share is two targets. A link to a `.md` file that is not
  part of the document is refused: in Word it would be a dead link. A link in code is code, and is left alone.
- **Write the Markdown for GitHub first.** Pandoc reads it as GitHub-flavoured Markdown, so a link names a heading by
  the anchor GitHub shows. The two differ on a heading with two spaces in a row or with an emoji; the command refuses
  such a link rather than guess.
- **Images sit beside their file, as PNG or JPEG.** A relative image path is read from the Markdown file's own
  directory, whatever directory the command runs in. Pandoc converts an SVG with `rsvg-convert`, which nothing pins;
  where it is missing, the command refuses the image.

## 2. Build

`doc-docx` is in the kit from 0.2.5 (install it as `/visual` §4 says). Install the pandoc version the repository's
CI pins, because the bytes of the output depend on it; the kit's CI pins **3.12.1**. Take it from pandoc's release page
(macOS: `pandoc-3.12.1-arm64-macOS.pkg`) and check it against the digest GitHub publishes: `brew install pandoc`
installs the newest release, which matches the pin only until the next one.

```sh
~/.local/share/diagram-kit/.venv/bin/doc-docx docs/GUIDE.docx docs/GUIDE.md docs/CHECKLIST.md --date 2026-10-13
```

- `--date` is required. It is stamped on the file (pandoc's `SOURCE_DATE_EPOCH`), and pandoc reads no user data
  directory, so the same Markdown and the same pandoc give the same bytes on any machine. Change it when the content
  changes.
- The look is pandoc's default reference document with the kit's palette (`template.html`): headings (levels 1 to
  5) in `--remote`, tables ruled in `--rule` with a `--ground` header row. It is built at run time; no template is
  committed anywhere.
- The command writes nothing when a check fails or pandoc fails: a link that would lead nowhere, a link to a file it
  was not given, a file without a title, a file that is not UTF-8, an image it cannot find, or a pandoc whose default
  reference changed shape (it says which part).

## 3. Wire it into the repository

- **Generate it from the same script as the Markdown.** If the Markdown is itself rendered (a placeholder such as a
  label domain filled in), build the `.docx` from the rendered files in the same step, so one change reaches both.
- **Commit the .docx beside its Markdown** when people need to download it from the repository.
- **Compare it in CI.** Install the pinned pandoc (the kit's `ci.yml` has the step: download the release `.deb`,
  check it against the digest GitHub publishes, `dpkg -i`), install the kit at a pinned tag, build, and fail on
  `git status --porcelain` for the generated files: a hand edit, a stale build or a deleted file all fail.

## 4. Look before you deliver

- **Read the XML, not a preview, for structure.** Every table carries `<w:tblStyle w:val="Table"/>` and that style
  has `<w:tblBorders>`; every internal `w:anchor` matches a `w:bookmarkStart` (the command checks this itself).
- **QuickLook is not Word.** `qlmanage -t -s 1400 -o <dir> <file>.docx` gives a page-one picture, but it ignores
  table styles and list numbering, so a table without borders there proves nothing about Word.
- **Do not drive Word with AppleScript.** Word acts on the user's *active* document: on 2026-10-13 an export saved
  the user's own open document instead of ours, and a `close every document saving no` aimed at our file would have
  discarded their unsaved work had Word not rejected it. Ask the user to open the file, or skip the visual check and
  say so.
- **Send the file** to the user when it is ready, with what was and was not checked.

## 5. Review it like the Markdown

The `.docx` adds no claim of its own: review the Markdown, and check that the build ran from the reviewed revision.
A reviewer gets the Markdown paths, the command line and the `--date`, and confirms the committed `.docx` is what that
command produces.
