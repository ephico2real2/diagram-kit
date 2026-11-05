ADVERSARIAL REVIEW: pull request <n> "<title>", repository <name>, head <sha>, exported read-only to <dir>/head.
Diff: `git diff <base>...<sha>`. Source of the change: <issue, specification or design record>.

For EACH claim, return one line `C<n>: CONFIRMED | REFUTED | PLAUSIBLE` and the artefact: a command and its output,
`file:line`, or a quoted line from the installed source. A bare CONFIRMED with no artefact counts as nothing.

For EVERY finding (a REFUTED verdict, a PLAUSIBLE verdict that names a risk, and anything you volunteer), give the
FULL code of the fix: the whole function, block or file section as it must read, with its path and where it goes.
Give a test that fails before the fix and passes after, in full. A finding without its full snippet and its test
is not a finding and will be discarded. Measure. Do not reason from memory.

Constraints: do not modify tracked files and do not commit. Run the change only in a copy outside the repository.
Create nothing inside the repository tree. Delete every temporary file you create. Write your whole answer to
<dir>/findings.md.

C1. <file>, <symbol> (lines a to b). CLAIM: <one sentence>. Refute it with <the concrete way to break it>. Show it
    by <the measurement>.
C2. <the semantics the change relies on: an expression, an option's default, a version>. CLAIM: <...>. Cite the
    documentation or the measured behaviour.
C3. <the off state and every switch interaction>. CLAIM: <...>.
C4. <fidelity to the source of the change, and that nothing else changed>. CLAIM: <...>. Diff each block.
C5. <what depends on the change: callers, workflows, other charts>. CLAIM: <...>.
C6. <the next real use of the change>. Run it in a copy and read the result. Refute anything an owner would fix by
    hand.
C7. <what can turn red with no code change>. CLAIM: <...>. Name every source and the worst one.

End with the single most important finding, and anything you saw that was not asked, each with its full snippet
and its test, as for a claim.
