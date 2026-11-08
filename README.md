# diagram-kit

One renderer, one template and one standard for the figures in our repositories; since 0.2.0, one standard and
two commands for their dashboards, the figures that move; and, since 0.2.5, one command for a Word document made from
Markdown.

Each diagram has a `source.html` page, started by `diagram-template` from the template the kit ships. `diagram-render`
turns every figure on it into a light and a dark PNG, and refuses the defects a review of the SVG text does not see:

- a fallback font;
- a label that runs past its box;
- a dashed arrow with no label beside it;
- text the reader cannot read in one of the two themes;
- a page that scrolls sideways on a phone.

| File | What it is |
|---|---|
| `diagram_kit/render.py` | the renderer (`diagram-render` once installed): PNGs plus the checks in `STANDARD.md` §5 |
| `diagram_kit/template.html` | the page every `source.html` starts from (`diagram-template <path>` writes it, never over an existing page): the palette, `.fig-scroll`, solid and dashed |
| `skill/visual/SKILL.md` | the `/visual` Claude Code skill that designs the pages; link `~/.claude/skills/visual` to this directory |
| `skill/dashboard/SKILL.md` | the `/dashboard` Claude Code skill: the dashboard standard, every rule with its source; link `~/.claude/skills/dashboard` to this directory |
| `skill/dashboard/COLLECTION.md` | how a workload's metrics get collected before any panel: an exporter of its own, ServiceMonitor or PodMonitor, a scrape over TLS |
| `diagram_kit/metrics.py` | `metrics-inventory`: every metric a workload emits, with the kind of data each is |
| `diagram_kit/perses.py` | `perses-dashboard`: the Perses form of a Grafana dashboard, and the checks the conversion needs |
| `diagram_kit/docx.py` | `doc-docx`: one Word document from Markdown files, with pandoc, the kit's palette, links kept inside the document, byte-reproducible |
| `skill/document/SKILL.md` | the `/document` Claude Code skill: when a Word file is made, from what, and how it is checked; link `~/.claude/skills/document` to this directory |
| `diagram_kit/delivery.py` | `delivery-page`: one page from a repository's tracker, handover and resume documents at one commit; it writes nothing when one of the three is missing, empty or still starter text |
| `skill/delivery-page/SKILL.md` | the `/delivery-page` Claude Code skill: the three required documents, the render, and how the page is checked and published; link `~/.claude/skills/delivery-page` to this directory |
| `skill/build-mockup/SKILL.md` | the `/build-mockup` Claude Code skill: an app mockup built as the contract for its page (target, tokens, state, typed data, section types, checks); link `~/.claude/skills/build-mockup` to this directory |
| `skill/mockup-to-page/SKILL.md` | the `/mockup-to-page` Claude Code skill: that mockup translated one-to-one into React or Preact + TypeScript, and proven to match; link `~/.claude/skills/mockup-to-page` to this directory |
| `skill/mockup-to-page-react/SKILL.md` | the `/mockup-to-page-react` Claude Code skill: a mockup translated into React, TypeScript, Vite and PatternFly, with PatternFly's look and the mockup's content, data and behaviour, proven by parity tests; link `~/.claude/skills/mockup-to-page-react` to this directory |
| `skill/test-ui/SKILL.md` | the `/test-ui` Claude Code skill: a UI tested against its reference with canonical DOM and pixels, recorded walks, content checked in both directions, mutations that prove the checks fail, and the installed browser; link `~/.claude/skills/test-ui` to this directory |
| `skill/app-architect/SKILL.md` | the `/app-architect` Claude Code skill: an application reviewed in its own forked agent, from inventories and a twelve-factor scorecard to a phased roadmap with a runnable proof per step; link `~/.claude/skills/app-architect` to this directory |
| `skill/mock-app/SKILL.md` | the `/mock-app` Claude Code skill: a mock app planned from the public documents of each provider, in its own forked agent. To install it, link `~/.claude/skills/mock-app` to this directory |
| `skill/adversarial-review/SKILL.md` | the `/adversarial-review` Claude Code skill: a change attacked by two model families on a per-claim brief, every finding with its full fix and a failing-then-passing test, each decision written down; link `~/.claude/skills/adversarial-review` to this directory |
| `skill/adversarial-review/brief-template.md`, `record-template.md` | the skeletons of a review's brief and of its record |
| `skill/agent-report/SKILL.md` | the `/agent-report` Claude Code skill: how a background agent logs its research as it works, and an audit with planted claims that shows the work is real; link `~/.claude/skills/agent-report` to this directory |
| `skill/agent-report/brief-standard.md` | the text to paste into the brief of every agent, of any kind |
| `skill/agent-report/scripts/brief_check.py` | the check that refuses a brief without the current standard, with a placeholder left, without a stop point or the browser and env rules, or with planted answers that lack a verdict or sit in the job folder |
| `skill/codex-arbiter/SKILL.md` | the `/codex-arbiter` Claude Code skill: background Codex agents review pending patches in disposable clones, and Claude rules on each finding and tests it; link `~/.claude/skills/codex-arbiter` to this directory |
| `skill/fix-defect/SKILL.md` | the `/fix-defect` Claude Code skill: each defect logged at once as an issue under its parent, researched, reviewed and proven; link `~/.claude/skills/fix-defect` to this directory |
| `skill/issue/SKILL.md` | the `/issue` Claude Code skill: one GitHub issue in agile form, with a milestone and one status label, grounded in the code and the measurements; link `~/.claude/skills/issue` to this directory |
| `skill/epic/SKILL.md` | the `/epic` Claude Code skill: a body of work broken into child issues that each end in a demonstration, with risks and exit criteria; link `~/.claude/skills/epic` to this directory |
| `skill/handover/SKILL.md` | the `/handover` Claude Code skill: the working note `claude-resumes/HANDOVER-<topic>.md`, kept current by four Claude Code hooks (Stop, PreCompact, SessionStart, PostToolUse) and the self-check `scripts/handover.py`, so that /compact, auto-compact and /clear lose nothing; also the handover of a long stop; link `~/.claude/skills/handover` to this directory |
| `skill/build-tracker/SKILL.md` | the `/build-tracker` Claude Code skill: the progress of a topic in `claude-resumes/TRACKER-<topic>.md`, each unit with its SDLC phase, its status and its evidence, one unit in progress at a time; link `~/.claude/skills/build-tracker` to this directory |
| `skill/resume-work/SKILL.md` | the `/resume-work` Claude Code skill: the restart after a new session, /compact, auto-compact or /clear, from the note and the tracker, checked against git, CI, the jobs and the environment; link `~/.claude/skills/resume-work` to this directory |
| `skill/agile/SKILL.md` | the `/agile` Claude Code skill: how milestones, epics, features, stories, tasks, spikes, defects and owner actions relate, how to create each with its issue type and parent, and how each maps to the legend; link `~/.claude/skills/agile` to this directory |
| `skill/agile/LEGEND.md`, `skill/agile/templates/` | the standard legend (ID prefixes, the INV and TDT classes, severity, status, verdicts), the GitHub issue forms, the issue bodies and the milestone description |
| `skill/pull-request/SKILL.md` | the `/pull-request` Claude Code skill: a sample pull request template with the milestone, the issues, the class and a checklist for each target branch, and the rules to open and merge; link `~/.claude/skills/pull-request` to this directory |
| `skill/delivery-playbook/SKILL.md` | the `/delivery-playbook` Claude Code skill: the standard method of delivery as a page and a deck, with five figures and the legend, and how to make a client copy; link `~/.claude/skills/delivery-playbook` to this directory |
| `skill/tokensave-fork/SKILL.md` | the `/tokensave-fork` Claude Code skill: install the tokensave2 fork with its dependencies, connect Codex, Cursor and Copilot, put it on the shell PATH, remove the upstream copy, and prove it with a real query; link `~/.claude/skills/tokensave-fork` to this directory |
| `skill/tokensave-fork/cursor-allow.py` | adds the read tools of tokensave to the Cursor CLI allow list, and no tool that writes |
| `skill/tokensave-fork/cursor-job-config.py` | makes a second Cursor configuration folder, so that one job gets a shell and reads only its own folder, and the main configuration does not change |
| `skill/tokensave-fork/tool-use-audit.py` | reads the log of a Claude, Codex or Cursor agent, and shows whether the agent read through tokensave and whether it read a whole file |
| `skill/sweep-stale/SKILL.md` | the `/sweep-stale` Claude Code skill: watch for stale background agents and the processes a session leaves behind, and end them on request; link `~/.claude/skills/sweep-stale` to this directory |
| `skill/sweep-stale/sweep-stale.py` | reports stale background agents, Codex brokers, orphaned test and browser processes, zombies and leftover socket directories, as text or as a prompt hook; `--sweep` ends what it names |
| `STANDARD.md` | when to use a page and when Mermaid, the page contract, embedding, the checks, review |
| `TUTORIAL.md` | install, a first figure, render, look, embed, review |
| `RESEARCH.md` | the measurements behind every check, and the prior art |
| `examples/fan-out/` | the connector kinds of `STANDARD.md` §3 on one page (curved fan-out, labelled dashed arrows), with its PNGs |
| `examples/` | real pages and dashboards copied from the repositories they were made in, each with where it came from (`examples/README.md`): a rendered diagram page, and a Grafana dashboard with its Perses form |
| `tests/` | one test per check, offline: a stand-in browser for the exit paths, real Chromium on local pages |

## Install and render

```sh
python3 -m venv .venv
.venv/bin/pip install "diagram-kit @ git+https://github.com/ephico2real2/diagram-kit@v0.2.5"
.venv/bin/playwright install chromium
.venv/bin/diagram-template docs/diagrams/<slug>/source.html
.venv/bin/diagram-render docs/diagrams/<slug>/source.html docs/diagrams/<slug> <name-1>,<name-2>
```

The repository is not published yet. Until it is, install from a local clone in place of the second line:
`.venv/bin/pip install <path-to-clone>`.
`TUTORIAL.md` walks the whole path.

### Prerequisite for documents: pandoc 3.12.1

`doc-docx`, `delivery-page` and the decks need pandoc. `diagram-render` does not. A document's bytes depend on pandoc's version, so
install the version that `ci.yml` pins, and check it against the digest that GitHub publishes for the file.
`brew install pandoc` and `apt-get install pandoc` give another version, and the byte test then skips.

On macOS, without `sudo`, for an Intel Mac or Apple Silicon. A Homebrew pandoc can stay installed:

```sh
case "$(uname -m)" in
  arm64)  ARCH=arm64;  DIGEST=c2146cf33a583f3ac93eccddf1bb662371d5cfcce1aad1c87ad860cca1435d46 ;;
  x86_64) ARCH=x86_64; DIGEST=81ed3e2cfecf096df15d407152f89a684fd65221082b919963f738e977fad3bc ;;
esac
curl -fsSL -o pandoc.zip "https://github.com/jgm/pandoc/releases/download/3.12.1/pandoc-3.12.1-$ARCH-macOS.zip"
echo "$DIGEST  pandoc.zip" | shasum -a 256 -c -
mkdir -p ~/.local/opt ~/.local/bin
unzip -q pandoc.zip -d ~/.local/opt
ln -s "$HOME/.local/opt/pandoc-3.12.1-$ARCH/bin/pandoc" ~/.local/bin/pandoc
rm pandoc.zip
```

`~/.local/bin` must come before Homebrew on your `PATH`. In a new terminal, `which pandoc` prints
`~/.local/bin/pandoc`, and `pandoc --version` prints `pandoc 3.12.1`.

On Ubuntu or Debian, as `ci.yml` does it:

```sh
case "$(dpkg --print-architecture)" in
  amd64) ARCH=amd64; DIGEST=b4217ac7c54067c442f9d4cd38bcd0c184a43f3e7053431a12263a6f92a33ba2 ;;
  arm64) ARCH=arm64; DIGEST=38f44718c0cb15cb81fc31026bd68c33e8628ca5f7ab15ca86494a7f24f7b8e4 ;;
esac
curl -fsSL -o pandoc.deb "https://github.com/jgm/pandoc/releases/download/3.12.1/pandoc-3.12.1-1-$ARCH.deb"
echo "$DIGEST  pandoc.deb" | sha256sum -c -
sudo dpkg -i pandoc.deb
rm pandoc.deb
```

### Intel Mac requirements

The kit needs no extra package on an Intel Mac. These items differ from Apple Silicon. Measured on 2026-11-06 on an
Intel Core i9-9980HK with macOS 15.8.1, Python 3.14.7 and Playwright 1.63.0 (`RESEARCH.md`, section 5).

| Item | On an Intel Mac |
| --- | --- |
| Homebrew | The prefix is `/usr/local`, not `/opt/homebrew`. A command that names a Homebrew path takes it from `brew --prefix` |
| The kit's venv | The commands in "Install and render" do not change, and they give a `x86_64` Python |
| Chromium | `playwright install chromium` fetches the `chrome-mac-x64` build. `diagram-render` wrote its PNGs with it |
| pandoc | The `x86_64` file in "Prerequisite for documents". It gave the same document bytes as `ci.yml`'s `.deb`, and the byte test passed |
| The tokensave fork (`/tokensave-fork`) | Its Rust toolchain folder is `1.98.1-x86_64-apple-darwin`. Homebrew's `rust` 1.98.1, at commit `48a229cea`, built it with no rustup, in 19 min 51 s against 3 minutes on an M-series Mac |

Not tested on an Intel Mac: decks, because LibreOffice and `pdftoppm` were not installed; an SVG in a document, because
`rsvg-convert` was not installed; the rustup way to build the tokensave fork.

### Linux requirements

Ubuntu/Debian packages (tested on Ubuntu 24.04):

```sh
sudo apt-get install -y python3-venv          # the kit's venv
sudo .venv/bin/playwright install-deps chromium   # Chromium's system libraries
# documents built from the figures: pandoc as "Prerequisite for documents" says, then
sudo apt-get install -y libreoffice-impress   # .pptx to PDF, to look at slides before sharing
sudo apt-get install -y poppler-utils         # pdftoppm: PDF pages to PNG
sudo apt-get install -y podman                # optional: the Containerfile check
sudo apt-get install -y gh                    # pull requests to the kit (or GitHub's apt repo for the current release)
```

`gh auth login --hostname github.com --git-protocol ssh --web` once; it reuses an SSH key GitHub already knows.
Changes to the kit go in as pull requests (`CONTRIBUTING.md`): `gh pr create` from a branch.

Fonts need no package: each render loads IBM Plex from Google Fonts, so the machine needs network access.
`libreoffice-core` alone cannot open a `.pptx` (`source file could not be loaded`); install `libreoffice-impress`.

Look at a deck the way a reader will:

```sh
soffice -env:UserInstallation=file://$PWD/.lo --headless --convert-to pdf deck.pptx
pdftoppm -r 50 -png deck.pdf slide      # slide-1.png, slide-2.png, …: check nothing runs off a slide
```

Or open `deck.pdf` in a browser and page through it, with the kit's Playwright Chromium or with Claude in Chrome.
Claude in Chrome cannot open `file://` pages, so serve a folder holding only the PDF, on loopback only:

```sh
mkdir -p /tmp/deck-view && cp deck.pdf /tmp/deck-view/
python3 -m http.server 8765 --bind 127.0.0.1 --directory /tmp/deck-view   # leave running; Ctrl-C to stop
# open http://127.0.0.1:8765/deck.pdf (add ?v=2 after a rebuild so the browser does not show the cached copy)
```

`--bind 127.0.0.1` keeps it off the network; `--directory` serves that folder and nothing above it. Copy the
PDF in again after each rebuild, and stop the server when the review is done.

### In a repository's CI

`diagram-render --check <page.html>...` puts every page through the same checks and writes no PNG. A repository
calls the kit's job, and copies no steps:

```yaml
jobs:
  diagrams:
    uses: ephico2real2/diagram-kit/.github/workflows/check-diagrams.yml@v0.2.5
    with:
      kit: v0.2.5
```

It checks every tracked file named `source.html` (the input `pages` takes another git pathspec) and fails when none is
found. A page that cannot be read or loaded fails like any other, and so does one that is not done in two minutes
(a script on it that never ends); the pages after it are still checked.

Chromium on Linux and on macOS draw text at the same widths since 0.2.3. For the day a page passes on a Mac and fails
in CI all the same, the `Containerfile` builds a Linux with the kit and its Chromium:

```sh
podman build --build-arg KIT_REF=v0.2.5 -t diagram-kit-linux .
podman run --rm -v "$PWD":/repo:ro diagram-kit-linux --check docs/diagrams/<slug>/source.html
```
The tag is given twice because a called workflow cannot learn the ref it was called at.

## Dashboards

A dashboard is a figure that moves, and it goes wrong the same way: built from memory, coloured by a palette nobody
chose, never looked at. `skill/dashboard/SKILL.md` is the standard, and two commands do the parts a person should not
do by hand:

```sh
# every metric a workload emits, with the kind of data each is: the list a dashboard is chosen from
.venv/bin/metrics-inventory --prometheus <url> --match '{namespace="app",job="app"}' > docs/metrics-inventory-app.md

# the Perses form of a Grafana dashboard, the Grafana JSON staying the only file edited (needs podman or docker)
.venv/bin/perses-dashboard dashboards/app.json dashboards/app.perses.json --datasource app-thanos
```

`metrics-inventory` reads a Prometheus-compatible API (a bearer token from the environment variable
`PROMETHEUS_TOKEN`, never from the command line) or a saved `/metrics` page (`--text`). `perses-dashboard` runs
`percli migrate` from the Perses image and refuses a panel that became a placeholder or a query that differs from
the source; it writes nothing when a check fails. `RESEARCH.md` §7 has what both were measured on.

## Documents

A Word document is made from Markdown, never edited by hand, the way a PNG is made from its page.
`skill/document/SKILL.md` is the standard; `doc-docx` does the build (it needs pandoc, at the version your CI pins:
see "Prerequisite for documents"):

```sh
# the guide, then the checklist, each after a page break, links between them kept inside the document
.venv/bin/doc-docx docs/ONBOARDING.docx docs/ONBOARDING.md docs/ONBOARDING_CHECKLIST.md --date 2026-10-13
```

It refuses a link that would lead nowhere in the document, a link to a `.md` file it was not given, and an image it
cannot find. The date is stamped on the file, so the same Markdown and the same pandoc give the same bytes on every
machine; the kit's CI pins pandoc 3.12.1, and a repository that commits the `.docx` and compares it in CI pins the
same version.

## Delivery pages

A delivery page is made from a repository's tracker, handover and resume documents, at one commit, and it names that
commit. `skill/delivery-page/SKILL.md` is the standard, and `delivery-page` does the build. It needs git and pandoc.

```sh
# a starter for each document that does not exist; it never overwrites a file
.venv/bin/delivery-page --init --repo .
# the page, from what the default branch holds
git fetch origin main
.venv/bin/delivery-page delivery.html --repo . --ref refs/remotes/origin/main
```

The command refuses to write if one of the three documents is missing, empty or still starter text, and it names each
one. Raw HTML in the Markdown shows as text, and a link with an unsafe scheme keeps only its words.

## Mockups

An app mockup is the contract for the page built from it, so it is built to be translated, not interpreted. Two
skills make one standard and change together:

- **`skill/build-mockup/SKILL.md`** builds the mockup on a design canvas. It declares the target framework first
  (`react-ts` or `preact-ts`), then holds one interactive app with preview frames, every colour as a named token in one
  table, shared state declared once with its owner and persistence, sample data as typed datasets with their API
  source, and every section as one of nine fixed types. Before it is published, every tab, theme and range is
  rendered and checked at 390, 820 and 1440 px.
- **`skill/mockup-to-page/SKILL.md`** translates that mockup one-to-one: tokens to `tokens.css`, state to the URL
  or browser storage, datasets to typed API schemas, and each section type to one component. The page is then proven
  to match at the same widths in both themes, with an accessibility scan and contract tests in CI.
- **`skill/mockup-to-page-react/SKILL.md`** translates a mockup into React, TypeScript, Vite and PatternFly for a
  console-style app. PatternFly replaces the look, so the page is proven on content, states and behaviour, not by a
  pixel diff against the mockup.

Link them to install them:

```sh
ln -s "$PWD/skill/build-mockup" ~/.claude/skills/build-mockup
ln -s "$PWD/skill/mockup-to-page" ~/.claude/skills/mockup-to-page
ln -s "$PWD/skill/mockup-to-page-react" ~/.claude/skills/mockup-to-page-react
```

The render and check tools they use live in Inkcast's `scripts/mockups/` (`render.js`, `check.py`), where the
standard was decided (Inkcast ADR-0016); the skills name them and their commands.

## Application architecture

**`skill/app-architect/SKILL.md`** reviews an application, new or existing, and returns a modernization plan grounded
in measured evidence: inventories, a twelve-factor scorecard, observability against a layered OpenTelemetry standard,
an adversarial security review, KEDA scaling with the TLS and identity each scaler needs, CI/CD, a portability map to
open standards and managed services, and a phased roadmap. Every finding carries its full fix and a test that fails
before it and passes after. The skill runs in its own forked agent (`context: fork`), so the review's reading stays
out of the conversation and only its report comes back. Its figures are made with `/visual` and its dashboards with
`/dashboard`. Its worked example is Fabric Coffee, demo 57 of
[cilium-implementation-poc](https://github.com/ephico2real2/cilium-implementation-poc).

If a provider has no sandbox, **`skill/mock-app/SKILL.md`** plans a mock app for it. It runs in its own forked agent. It researches current practice online, reads the public API documentation
and contract of each provider, and compares them with the calls of the client. The plan gives the build choice, and an
OpenAPI contract and the authentication of each provider, with test values only. It also gives the contract tests
and a phased plan with a proof for each step. `/app-architect` sends each provider with no sandbox to it.

```sh
ln -s "$PWD/skill/app-architect" ~/.claude/skills/app-architect
```

## Adversarial review

**`skill/adversarial-review/SKILL.md`** is the review pass every change gets before it is called ready, and the one
`/app-architect` asks for. A brief of numbered claims goes to two reviewers or more from different model families,
never the author. Each verdict carries its artefact, and each finding carries its full fix and a test that fails
before it and passes after. The orchestrator traces every fix, writes each decision with its reason, applies and
tests, writes the record, and runs a second pass on the fixed head.

```sh
ln -s "$PWD/skill/adversarial-review" ~/.claude/skills/adversarial-review
```

A personal skill wins over a project skill of the same name, so this link hides a repository's own
`.claude/skills/adversarial-review` in that repository.

## Skills: the kit is the one copy

Each general skill lives here, and `~/.claude/skills/<name>` is a link to its directory. Change a skill here, through
a pull request, and never in a copy under `~/.claude/skills`. A copy drifts: on 2026-11-07, three local copies differed
from the kit, and the newer rules were in different places.

```sh
ln -s "$PWD/skill/<name>" ~/.claude/skills/<name>
```

- A new general skill comes here in its first pull request, with its README row and its name in
  `tests/test_skills.py`.
- This repository is public. A skill holds no firm name, no client name, no client number and no private host. An
  example from client work names the kind of work, not the client.
- A skill for one client or one project lives in that repository, under `.claude/skills/`.
- A fact about one machine, such as an installed version, goes into the memory of the agent, not into the skill.

## Why a kit

The renderer used to live in three copies with two behaviours. A fix made in one place (#342's failed-font check)
did not reach the others, and one vendored copy still lacks it
(group-sync-dashboard #436). Installing one pinned version replaces the copies.

## Tests

Install first, once per clone, and run from that virtualenv:

```sh
python3 -m venv .venv
.venv/bin/pip install ".[test]"
.venv/bin/playwright install chromium
.venv/bin/python -m pytest tests -q
```

A `pytest` from your PATH fails at collection with `ModuleNotFoundError: No module named 'diagram_kit'` or `'playwright'`.
That means the setup above has not been done, not that a test failed. `tests/test_skills.py` has no such imports, so it
passes either way and proves nothing about the rest. The tests of `doc-docx` skip without `pandoc` on the PATH, and its byte test skips on any version but 3.12.1.

No test reaches the network. The browser tests inline a font from `tests/fixtures/fonts/` (Inter, SIL Open Font
License 1.1, `tests/fixtures/fonts/OFL.txt`). The dashboard tests run no container and ask no Prometheus: they use a
saved `percli` result (`tests/fixtures/dashboard/`) and an API answered from a table.

## Prior art

[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) (MIT, Cathryn Lavery) is the same
pattern: self-contained HTML and SVG pages, colour tokens, and a Playwright export. It was there first. This kit was
written independently, and keeps its own page format. From diagram-design it borrows:

- **measuring labels against their boxes.** Its `verify-geometry.py` checks label plates against nodes, and its
  `verify-treemap.py` estimates text width per em. Ours measures the drawn text in the browser;
- **WCAG contrast as a gate.** Its `verify-heatmap.py`, `verify-dumbbell.py` and onboarding rules check contrast;
  ours checks every figure text against the box under it, and the template's tokens;
- **an exactly pinned Playwright**, chosen deliberately, because the output is pixels.

`RESEARCH.md` §1 lists each of its checks and what was taken, adapted or left, and why.

## Licence

| What | Licence | What it means |
|---|---|---|
| the renderer, the tests, the documents | [MPL-2.0](LICENSE) | use it for anything, commercial included; keep the notices; a changed copy of a kit file you distribute stays open under the MPL |
| `diagram_kit/template.html`, `examples/` | [MIT-0](LICENSES/MIT-0.txt) | a page started from the template, and its PNGs, are yours with no obligation |

Credit the kit as `diagram-kit (https://github.com/ephico2real2/diagram-kit), MPL-2.0` and keep `NOTICE` with any
copy. Please send enhancements back as a pull request (`CONTRIBUTING.md`): the licence keeps changed kit files open,
and a pull request is how they reach every project that uses the kit.
