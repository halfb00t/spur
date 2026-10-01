---
phase: 12-composition-pass
fixed_at: 2026-10-01T08:13:34Z
review_path: .planning/phases/12-composition-pass/12-REVIEW.md
iteration: 1
findings_in_scope: 9
fixed: 9
skipped: 0
status: all_fixed
---

# Phase 12: Code Review Fix Report

**Fixed at:** 2026-10-01
**Source review:** `.planning/phases/12-composition-pass/12-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 9 (WR-01 through WR-09 at `critical_warning`; the five Info findings
  are out of scope for this run)
- Fixed: 9
- Skipped: 0

All edits were made and committed directly in the main checkout on
`gsd/phase-12-composition-pass` (`workflow.use_worktrees` is `false` in
`.planning/config.json` — no worktree, branch, or sentinel was created). Every commit ran
this project's real pre-commit gate (`make verify`: ruff, mypy `--strict`, import-boundary
contracts, unfinished-work scan, full pytest, ~3.5 min) and passed before being recorded.

## Fixed Issues

### WR-01: `cli.md` "Errors" claims every parameter error prints `error: <field>: <message>` -- two of the three shapes it groups do not

**Files modified:** `docs/architecture/cli.md`
**Commit:** `55e2979`
**Applied fix:** Reworded the "Shape" paragraph (`_params(ns)`) to state only
`ValidationError` produces `error: <field>: <message>`, and that a `check()` refusal
prints `error: <message>` with no field prefix. Reworded the "Errors" section's opening
line from "Three cases, three exit statuses" to "Three cases, two exit statuses" (the
three cases produce only two distinct exit values, 2 and 1) and expanded the parameter-error
bullet to name all three real stderr shapes (argparse's own flag error, a field-level
`GearParams` bound, and a `check()` refusal), matching `tests/test_cli.py:435-437`'s
own assertion of the no-prefix refusal shape. Verified by re-reading the edited sections
and cross-checking against the cited test.

### WR-02: `hole_count`'s comment still attributes the 14.87 s row to "Phase 12 ... (re-measured in the same section)" after this phase corrected the identical sentence on `spoke_count`

**Files modified:** `src/spur/params.py`
**Commit:** `9dcf1a4`
**Applied fix:** Applied the fix text verbatim — the comment now says "Phase 10's
14.87 s tip-chamfer row (an arithmetic total only — Phase 12's composed sweep measured
the real stack)", matching the already-corrected `spoke_count` comment four fields above.
Comment-only change; `hole_count`'s bound (60) and every other field untouched. Verified
by re-reading the diff; `ruff check` and `mypy --strict` clean.

### WR-03: `bench.export_cost` exits 1 on its only failure path without saying why

**Files modified:** `bench/export_cost.py`
**Commit:** `65a4554`
**Applied fix:** The triangle-count mismatch branch now prints which triangle counts
disagreed and cites the violated invariant (L24: a copy meshes identically) to stderr
before returning 1, per the fix text. Verified with `ast.parse`, `ruff check`, and
`mypy --strict` (all clean), plus the commit-time `make verify` gate (full suite green).

### WR-04: A failing child process reports only "returned non-zero exit status 1" -- its `BuildError` text and traceback are captured and discarded

**Files modified:** `bench/export_cost.py`
**Commit:** `65a4554`
**Applied fix:** Both `--child` subprocess calls now run with `check=False`; a non-zero
exit code or empty stdout writes the captured child stderr through to this process's
stderr and raises `SystemExit` naming the mode, run number, and exit code, so a real
`BuildError`/OCCT failure/`_find_set` error reaches the user instead of
`subprocess`'s own paraphrase, and an empty-stdout success no longer raises a bare
`IndexError`. No new test added — both paths require a child process to actually fail
or disagree on triangle count, which is not a cheap, deterministic unit to construct
without mocking subprocess internals this module does not otherwise mock; documented in
the commit body. Verified with `ast.parse`, `ruff check`, `mypy --strict` (all clean),
and the commit-time `make verify` gate.

### WR-05: L31 attributes the "schema, form source and CLI parser in one order" proof to the wrong test

**Files modified:** `docs/architecture/decision_log.md`
**Commit:** `55e2979`
**Applied fix:** Applied the fix text verbatim: the sentence now credits
`tests/test_cli.py::test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`
(confirmed present at `tests/test_cli.py:187`) with the schema/CLI field-order walk, and
`tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code`
with the `app.js` hash → form → query round trip, naming no field. Verified both test
names exist in their respective files before committing. `git diff --numstat c9a169d --
docs/architecture/decision_log.md` reads 140 insertions / 0 deletions — the append-only
invariant holds (L31 was added this branch, so in-place rewording of its own sentences is
the established precedent from 11-REVIEW-FIX WR-02's L30 reword).

### WR-06: the "level 9 compared against the currently-adopted level" regression test can't actually distinguish that from the bug it names

**Files modified:** `tests/test_bench.py`
**Commit:** `6dce386`
**Applied fix:** Adapted rather than applied the review's literal fix text (which proposed
changing one value and adding a third fixture row). A simpler single-value change achieves
the same regression-catching property: lowering `level9_beats_1_not_6`'s `concurrent_ms`
from 300.0 to 100.0 holds the wall clause inside both bases' bars (100 <= 150 against
level 1, 100 <= 225 against level 6), so it can no longer mask the result; only the shrink
clause differs between bases (15.0% against level 1, past the 10% bar; 5.6% against level
6, under it). Verified by hand against the real `_decisions()` and a hand-rolled
pinned-to-level-1 implementation (shown in the commit body): the real implementation holds
`adopted=False` for level 9 (final level stays 6, matching the assertion), while the
pinned-to-1 regression computes `adopted=True` (final level becomes 9) — the assertion
would now fail under the exact bug it is named for. Also verified by running
`make test PYTEST_ARGS="tests/test_bench.py -q"`: 20 passed. Comment rewritten to show the
arithmetic inline. This finding touches test logic that decides a pass/fail boundary
(not a dimension a user cuts metal to), and both the real and the hypothetical-regression
arithmetic were independently computed and cross-checked with a live Python REPL before
committing — commit status recorded as `fixed`, not flagged for additional human
verification, since the catching behavior was directly demonstrated rather than inferred.

### WR-07: decision-log and RESULTS.md prose calls two end-of-run load readings "at-start loads"

**Files modified:** `docs/architecture/decision_log.md`, `bench/RESULTS.md`
**Commit:** `55e2979`
**Applied fix:** Both records now split the four load figures into the two methods that
actually produced them: "loads 12.66 and 7.04 (both read at the end of the run, the
tool-bug reading; see above) and 2.74 and 1.54 (read at a genuine start, after the fix)".
Did not reuse the fix text's literal "see above" + named-subsection form for
`bench/RESULTS.md`, since no "Host state" heading sits immediately above that sentence —
checked the file structure first and used a plain "see above", which is accurate: the
disclosure of the tool's end-of-sweep reading bug sits a few paragraphs earlier in the
same `## Composed build and export time (Phase 12)` section (`bench/RESULTS.md:1255-1259`).
No measured number, table cell, or run heading changed — prose only. Verified by re-reading
both edited passages for sentence flow.

### WR-08: L31 says every composed pattern measured below its arithmetic total; the honeycomb row it cites in the same sentence measured above it

**Files modified:** `docs/architecture/decision_log.md`
**Commit:** `55e2979`
**Applied fix:** Applied the fix text verbatim: "Each pattern's worst composed row read
below ..." became "Two of the three patterns' worst composed rows read below ... The
third, honeycomb, measured above its total: 27.49 s against 23.52 s (+3.97 s) — the one
pattern where stacking cost more than the naive sum." `bench/RESULTS.md:1486-1504` already
recorded the same three numbers without the false universal claim (per the review's own
note), so no change was needed there. Verified by re-reading the edited sentence against
the three cited figures.

### WR-09: "L24's invariant held" / "identical mesh content" overstates what the triangle-count comparison actually checks

**Files modified:** `bench/RESULTS.md`
**Commit:** `55e2979`
**Applied fix:** Applied the fix text verbatim: "Exit code: 0 (every run's triangle count
agrees — copy and in-place produced the same triangle *count*; this does not by itself
prove identical mesh content down to vertex positions or winding, which this script does
not check)." Did not add the stronger content-level check (hashing exported STL bytes)
the fix text offered as an alternative — out of scope for a doc-claim correction and not
requested by the orchestrator's task grouping. Verified by re-reading the edited sentence
against `bench/export_cost.py:296-301`'s actual check (a set of triangle counts).

## Skipped Issues

None — all nine in-scope findings were fixed.

---

_Fixed: 2026-10-01_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
