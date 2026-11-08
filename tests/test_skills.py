# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Every skill is one a person can install: a SKILL.md whose name is its directory, a description that says when to
use it, and a README row that says where to link it. The two mockup skills are one standard and name each other."""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

import playwright
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = sorted(p.parent for p in ROOT.glob("skill/*/SKILL.md"))


def frontmatter(path: pathlib.Path) -> dict[str, str]:
    match = re.match(r"---\n(.*?)\n---\n", path.read_text(), re.S)
    assert match, f"{path.relative_to(ROOT)} starts without a --- frontmatter block"
    return dict(line.split(": ", 1) for line in match.group(1).splitlines())


def test_the_kit_ships_every_skill():
    assert [p.name for p in SKILLS] == ["adversarial-review", "app-architect", "build-mockup", "dashboard", "document", "mockup-to-page",
                                      "mockup-to-page-react", "test-ui", "visual"]


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_a_skill_is_named_for_its_directory_and_says_when_to_use_it(skill):
    meta = frontmatter(skill / "SKILL.md")
    assert meta["name"] == skill.name
    assert "Use when" in meta["description"]


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_the_readme_says_where_to_link_each_skill(skill):
    assert f"link `~/.claude/skills/{skill.name}` to this directory" in (ROOT / "README.md").read_text()


def test_the_mockup_skills_are_one_standard():
    build = (ROOT / "skill" / "build-mockup" / "SKILL.md").read_text()
    page = (ROOT / "skill" / "mockup-to-page" / "SKILL.md").read_text()
    assert "`/mockup-to-page` are one standard: change them together" in build
    assert "`/build-mockup` are one standard: change them together" in page


def test_the_patternfly_page_skill_is_part_of_the_mockup_standard():
    build = (ROOT / "skill" / "build-mockup" / "SKILL.md").read_text()
    page = (ROOT / "skill" / "mockup-to-page-react" / "SKILL.md").read_text()
    assert "`/mockup-to-page-react` are one standard" in build
    assert "`react-pf-ts`" in build
    assert "`/build-mockup` are one standard: change them together" in page


def test_the_architect_skill_runs_in_its_own_agent_and_receives_its_subject():
    skill = ROOT / "skill" / "app-architect" / "SKILL.md"
    meta = frontmatter(skill)
    assert (meta["context"], meta["agent"]) == ("fork", "general-purpose")
    assert "$ARGUMENTS" in skill.read_text()


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_a_frontmatter_value_that_yaml_reads_as_a_list_or_a_map_is_quoted(skill):
    # `argument-hint: [path] [scope]` is a YAML list followed by stray text, and a strict parser refuses the block
    for key, value in frontmatter(skill / "SKILL.md").items():
        assert not value.startswith(("[", "{")), f"{skill.name}: quote the value of {key}"


def test_the_review_skill_names_the_templates_it_ships():
    skill = ROOT / "skill" / "adversarial-review"
    text = (skill / "SKILL.md").read_text()
    for template in ("brief-template.md", "record-template.md"):
        assert (skill / template).is_file()
        assert f"${{CLAUDE_SKILL_DIR}}/{template}" in text


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_a_wrapped_line_does_not_start_a_numbered_list(skill):
    # In CommonMark, a line that starts with "1." or "1)" interrupts the paragraph above it and opens a list.
    # Another number ("403.") does not. So a wrap before a "1." is a defect, unless the line above is a list item too.
    lines, fenced, bad = (skill / "SKILL.md").read_text().splitlines(), False, []
    for n, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and n and re.match(r"\s*1[.)] ", line):
            above = lines[n - 1]
            if above.strip() and not re.match(r"\s*(\d+[.)]|[-*+]) |\s*\|", above):
                bad.append(f"{n + 1}: {line.strip()[:40]}")
    assert not bad, bad


UI_STATES = ("loading", "empty", "error", "forbidden", "conflict", "success")


@pytest.mark.parametrize("name", ["build-mockup", "mockup-to-page", "mockup-to-page-react"])
def test_the_mockup_standard_names_every_ui_state(name):
    # The mockup shows each state, and each page skill says what each one becomes, so none is left to a guess
    text = (ROOT / "skill" / name / "SKILL.md").read_text()
    for state in UI_STATES:
        assert f"`{state}`" in text, f"{name} does not name the {state} state"


@pytest.mark.parametrize("name", ["build-mockup", "mockup-to-page", "mockup-to-page-react"])
def test_the_mockup_standard_points_to_its_example(name):
    text = (ROOT / "skill" / name / "SKILL.md").read_text()
    assert "build-mockup/example/workspaces.html" in text
    assert (ROOT / "skill" / "build-mockup" / "example" / "workspaces.html").is_file()


@pytest.mark.parametrize("name", ["mockup-to-page", "mockup-to-page-react"])
def test_each_page_skill_shows_its_mapping_in_code(name):
    text = (ROOT / "skill" / name / "SKILL.md").read_text()
    assert "```tsx" in text, f"{name} has no React example"


def test_the_build_skill_keeps_every_target():
    text = (ROOT / "skill" / "build-mockup" / "SKILL.md").read_text()
    for target in ("`react-ts`", "`preact-ts`", "`react-pf-ts`"):
        assert target in text


def test_the_readme_names_every_target_and_the_number_of_section_types():
    text = (ROOT / "README.md").read_text()
    for target in ("`react-ts`", "`preact-ts`", "`react-pf-ts`"):
        assert target in text
    build = (ROOT / "skill" / "build-mockup" / "SKILL.md").read_text()
    table = build.split("Sections: a fixed vocabulary", 1)[1].split("\n## ", 1)[0]
    count = len(re.findall(r"^\| `[a-z-]+` \|", table, re.M))
    words = {9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}
    assert f"{words[count]} fixed types" in text


def test_the_page_skill_sends_a_patternfly_target_to_its_own_skill():
    assert "`react-pf-ts`" in (ROOT / "skill" / "mockup-to-page" / "SKILL.md").read_text()


@pytest.mark.parametrize("name", ["build-mockup", "mockup-to-page", "mockup-to-page-react"])
def test_the_mockup_standard_keeps_secrets_out_and_permissions_on_the_server(name):
    # Each skill says it on its own, because an owner who reads only one skill must not miss it
    text = " ".join((ROOT / "skill" / name / "SKILL.md").read_text().split())
    assert "token" in text and ("is never in a fixture" in text or "also applies to sample data" in text), name
    assert "The server enforces each permission." in text, name


def test_the_page_skill_says_what_each_other_http_answer_becomes():
    text = (ROOT / "skill" / "mockup-to-page" / "SKILL.md").read_text()
    for status in ("401", "404", "422", "429"):
        assert re.search(rf"^  - {status}\b", text, re.M), f"no rule for {status}"


def test_the_example_fetch_obeys_the_http_rules_of_its_skill():
    # The rules and the code that people copy must agree: a 401 goes to the shell, not to a "Try again"
    text = (ROOT / "skill" / "mockup-to-page" / "SKILL.md").read_text()
    fetch = text.split("export async function getWorkspaces", 1)[1].split("\n}\n", 1)[0]
    generic = fetch.index("if (!response.ok)")
    for status in ("401", "403", "429"):
        assert f"response.status === {status}" in fetch[:generic], f"{status} falls to the generic error"
    unauthorized = re.search(r"status === 401\)(.*)", fetch).group(1)
    assert "signIn()" in unauthorized and "'error'" not in unauthorized
    assert "Retry-After" in fetch
    # Run the exact type and fetch declarations, without JSX. Playwright already ships the Node runtime.
    snippet = "export type Workspace =" + text.split("export type Workspace =", 1)[1].split("// components/RowList.tsx:", 1)[0]
    node = pathlib.Path(playwright.__file__).parent / "driver" / ("node.exe" if sys.platform == "win32" else "node")
    program = """import assert from 'node:assert/strict';
let signIns = 0;
function signIn() { signIns += 1; }
""" + snippet + """
const cases = [
  [200, {}, { state: 'ready', data: { items: [] } }, 0],
  [401, {}, { state: 'loading' }, 1],
  [403, {}, { state: 'forbidden' }, 0],
  [404, {}, { state: 'error', cause: 'The server sent HTTP 404.' }, 0],
  [503, {}, { state: 'error', cause: 'The server sent HTTP 503.' }, 0],
  [429, { 'Retry-After': '30' }, { state: 'error', cause: 'The server is busy. Try again in 30 seconds.' }, 0],
  [429, { 'Retry-After': 'Wed, 21 Oct 2015 07:28:00 GMT' }, { state: 'error', cause: 'The server is busy.' }, 0],
  [429, {}, { state: 'error', cause: 'The server is busy.' }, 0],
  [429, { 'Retry-After': '-1' }, { state: 'error', cause: 'The server is busy.' }, 0],
  [429, { 'Retry-After': 'invalid' }, { state: 'error', cause: 'The server is busy.' }, 0],
];
for (const [status, headers, expected, expectedSignIns] of cases) {
  const signal = new AbortController().signal;
  let requests = 0;
  signIns = 0;
  globalThis.fetch = async (url, options) => {
    requests += 1;
    assert.equal(url, '/api/workspaces?team=example');
    assert.equal(options.signal, signal);
    return new Response(JSON.stringify({ items: [] }), { status, headers });
  };
  assert.deepEqual(await getWorkspaces(new URLSearchParams('team=example'), signal), expected, `HTTP ${status}`);
  assert.equal(signIns, expectedSignIns, `HTTP ${status} sign-in count`);
  assert.equal(requests, 1);
}
globalThis.fetch = async () => { throw new Error('network failed'); };
await assert.rejects(getWorkspaces(new URLSearchParams(), new AbortController().signal), /network failed/);
console.log('10 HTTP cases and network rejection passed');
"""
    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "fetch.mts"
        script.write_text(program)
        result = subprocess.run([str(node), str(script)], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "10 HTTP cases and network rejection passed"


@pytest.mark.parametrize(("old", "new"), [
    ("return { state: 'forbidden' };", "return { state: 'loading' };"),
    ("signIn(); return", "/* signIn() */ return"),
    ("Number.isInteger(wait) && wait > 0", "false"),
])
def test_the_http_rule_test_rejects_wrong_behavior(monkeypatch, tmp_path, old, new):
    text = (ROOT / "skill" / "mockup-to-page" / "SKILL.md").read_text()
    assert text.count(old) == 1
    skill = tmp_path / "skill" / "mockup-to-page" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(text.replace(old, new))
    monkeypatch.setitem(globals(), "ROOT", tmp_path)
    with pytest.raises(AssertionError):
        test_the_example_fetch_obeys_the_http_rules_of_its_skill()


def test_the_patternfly_example_does_not_hide_a_fault_behind_retries():
    # Query's default retries keep the section in `loading` for about 7 s before `error`
    text = (ROOT / "skill" / "mockup-to-page-react" / "SKILL.md").read_text()
    hook = text.split("export function useWorkspaces", 1)[1].split("\n}\n", 1)[0]
    assert "retry: false" in hook


def test_the_patternfly_skill_maps_a_new_token_to_a_one_time_copy():
    text = (ROOT / "skill" / "mockup-to-page-react" / "SKILL.md").read_text()
    assert re.search(r"^\| A new token, shown one time \|.*`ClipboardCopy", text, re.M)


def test_the_review_record_identifies_the_second_pass_sources():
    record = (ROOT / "docs" / "reviews" / "pr-17.md").read_text()
    heading = "## Second pass: F1 and F2"
    assert heading in record
    second_pass = record.split(heading, 1)[1]
    assert "`d1d40cb`" in second_pass
    for finding, source in (("F1", "tests/test_mockup_example.py"),
                            ("F2", "skill/mockup-to-page/SKILL.md")):
        assert f"### {finding}:" in second_pass and source in second_pass
