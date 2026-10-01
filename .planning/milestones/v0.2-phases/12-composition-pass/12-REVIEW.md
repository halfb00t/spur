---
phase: 12-composition-pass
reviewed: 2026-10-01T02:42:01Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - bench/RESULTS.md
  - bench/export_cost.py
  - docs/architecture/cli.md
  - docs/architecture/decision_log.md
  - src/spur/params.py
  - tests/test_bench.py
findings:
  critical: 0
  warning: 0
  info: 5
  total: 5
status: issues_found
---

# Phase 12: Code Review Report (incremental re-review)

**Reviewed:** 2026-10-01T02:42:01Z
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found

## Summary

This is an incremental re-review of the four fix commits (`55e2979`, `65a4554`, `6dce386`,
`9dcf1a4`) applied against `12-REVIEW.md`'s nine open Warnings (WR-01..WR-09), scoped to
`git diff b9dc04e..HEAD` on the six files the fix touched. All nine are confirmed resolved
by re-reading the current source at the cited lines and, where the finding was an
arithmetic claim, re-deriving the numbers by hand rather than trusting the fix report's
own account. No regression and no incomplete fix was found, so no new Warning (WR-10+) is
opened this pass.

The one fix that needed real verification work, not just a text diff, was WR-06
(`tests/test_bench.py`'s `test_level_9_is_compared_against_the_level_currently_adopted`):
the fixer changed `level9_beats_1_not_6`'s `concurrent_ms` from `300.0` to `100.0` rather
than applying the review's literal three-row proposal. Re-running `_decisions()`'s actual
arithmetic by hand on both the real implementation and a hypothetical "always compare
against level 1" regression confirms the row now does separate the two: the real
implementation holds the final level at 6 (shrink 500,000 < 900,000 bar fails against the
level-6 base), while the hypothetical regression would compute a shrink of 1,500,000 >=
1,000,000 against level 1 and a wall of 100 <= 150 — both bars clear, so the regression
adopts level 9 and the assertion flips to 9 and fails. The fix is correct, and more
economical than the review's own suggested fix (one changed value instead of a new third
fixture row).

`bench/export_cost.py`'s error-path fix (WR-03/WR-04) was re-checked for the specific
things the task asked about: the child's stderr now reaches the user
(`sys.stderr.write(child.stderr)` before the `SystemExit`, unconditional on which of the
two failure conditions — non-zero exit or empty stdout — tripped); every exit on that path
now carries a reason (the `SystemExit` message names the mode, the run number and the
exit code, and the final `all_triangles` mismatch path now prints the disagreeing counts
and names L24's invariant before `return 1`); and the new code introduces no explicit
`Any` and nothing `mypy --strict` would reject by construction — `subprocess.run(...,
capture_output=True, text=True)` with `text=True` as a literal selects typeshed's
`str`-typed overload for `stdout`/`stderr`, so `sys.stderr.write(child.stderr)` is
`str` into a method that accepts `str`, no cast needed.

The three doc/decision-log wording fixes (WR-01, WR-05, WR-07, WR-08, WR-09 — `cli.md`,
`decision_log.md`'s L31, and `bench/RESULTS.md`) were checked sentence-by-sentence against
the diff: each corrected sentence now states only what the cited test or measurement
actually shows, with no remaining universal claim contradicted by data in the same
paragraph (WR-08's honeycomb exception), no remaining mislabelled measurement method
(WR-07's end-of-run-vs-at-start loads), and no remaining test misattribution (WR-01's exit
status count and field-prefix claims, WR-05's test name). `src/spur/params.py`'s
`hole_count` comment (WR-02) now matches the already-corrected `spoke_count` comment's
wording verbatim in shape.

The five Info findings from the prior review (IN-01..IN-05) are carried forward below,
unresolved: none of the four fix commits touched the lines they cite. `tests/test_model.py`
(IN-05) and `tests/test_api.py` (IN-04) are both outside this diff's six changed files
(confirmed via `git diff b9dc04e..HEAD --stat`, which lists exactly the six files in
scope), so both were re-read from current source rather than assumed unchanged.

## Resolved since the last review

- **WR-01** (`cli.md` "Errors"/"Shape" claims about exit statuses and the field-prefix
  shape) — fixed in `55e2979`: "Three cases, three exit statuses" corrected to "...two
  exit statuses"; the parameter-error bullet now names all three real stderr shapes
  (argparse's own error, a field-level `ValidationError`, and a `check()` refusal with no
  field prefix); the "Shape" paragraph now states the same split. Confirmed by re-reading
  `docs/architecture/cli.md`'s current "Shape" (lines 24-26) and "Errors" (lines 34-48)
  sections verbatim against the fix text.
- **WR-02** (`params.py`'s `hole_count` comment attributing a re-measurement to the wrong
  phase) — fixed in `9dcf1a4`: the comment now reads "Phase 10's 14.87 s tip-chamfer row
  (an arithmetic total only -- Phase 12's composed sweep measured the real stack)",
  matching `spoke_count`'s already-corrected comment four fields above. Confirmed by
  re-reading `src/spur/params.py:142-144`.
- **WR-03** (`bench/export_cost.py` exits 1 with no reason on a triangle-count mismatch)
  — fixed in `65a4554`: the mismatch branch now prints the disagreeing triangle counts and
  names L24's invariant to stderr before `return 1`. Confirmed by re-reading
  `bench/export_cost.py`'s current end of `main()`.
- **WR-04** (a failing `--child` subprocess's stderr and traceback were captured and
  discarded) — fixed in `65a4554`: both `--child` subprocess calls now run with
  `check=False`; a non-zero exit or empty stdout writes the child's captured stderr
  through and raises `SystemExit` naming the mode, run number and exit code, which also
  closes the bare-`IndexError`-on-empty-stdout-success case WR-04 named. Confirmed by
  re-reading `bench/export_cost.py:268-277` and re-checking the `subprocess.run(...,
  text=True)` overload gives `child.stderr: str` (no `Any`, nothing for mypy `--strict`
  to reject).
- **WR-05** (`decision_log.md` L31 credits the wrong test for the schema/CLI field-order
  proof) — fixed in `55e2979`: the sentence now credits
  `tests/test_cli.py::test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`
  with the schema/CLI order walk and
  `tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code`
  with the separate `app.js` round-trip proof. Confirmed by re-reading
  `docs/architecture/decision_log.md:1357-1363`.
- **WR-06** (the level-9-vs-adopted-level regression test couldn't actually distinguish
  the bug it named) — fixed in `6dce386`: `level9_beats_1_not_6`'s `concurrent_ms` lowered
  from 300.0 to 100.0, which holds the wall clause inside both bases' bars and leaves only
  the shrink clause able to decide the row. Hand-rederived both the real implementation's
  arithmetic (shrink 500,000 < 900,000 against the level-6 base -> not adopted -> stays 6)
  and a hypothetical "pinned to level 1" regression's arithmetic (shrink 1,500,000 >=
  1,000,000 and wall 100 <= 150 against level 1 -> adopted -> flips to 9): the assertion
  `== 6` now passes under the real code and fails under the named regression, which it did
  not do before this fix. Confirmed by re-reading `tests/test_bench.py:505-553`.
- **WR-07** (decision-log and RESULTS.md prose calling two end-of-run load readings
  "at-start loads") — fixed in `55e2979`: both records now split the four load figures
  into "loads 12.66 and 7.04 (both read at the end of the run, the tool-bug reading; see
  above) and 2.74 and 1.54 (read at a genuine start, after the fix)". Confirmed by
  re-reading `docs/architecture/decision_log.md:1301-1304` and `bench/RESULTS.md:1559-1562`.
- **WR-08** (L31 claiming every composed pattern measured below its arithmetic total when
  the honeycomb row in the same sentence measured above it) — fixed in `55e2979`: reworded
  to "Two of the three patterns' worst composed rows read below... The third, honeycomb,
  measured above its total...". Confirmed by re-reading
  `docs/architecture/decision_log.md:1317-1321`.
- **WR-09** ("L24's invariant held" / "identical mesh content" overstating what the
  triangle-count-only comparison checks) — fixed in `55e2979`: `bench/RESULTS.md` now
  reads "every run's triangle count agrees -- copy and in-place produced the same
  triangle *count*; this does not by itself prove identical mesh content down to vertex
  positions or winding, which this script does not check". Confirmed by re-reading
  `bench/RESULTS.md:1773-1775` against the actual check at
  `bench/export_cost.py`'s `all_triangles` set-equality test (still a count-only check,
  unchanged by this fix, so the corrected wording remains accurate).

## Narrative Findings (AI reviewer)

## Info

### IN-01: `_decisions` docstring says integer arithmetic decides `adopted`; the wall clause is float

**File:** `bench/export_cost.py:122-134`
**Issue:** Still open — unchanged by any of the four fix commits (none touch lines before
268). The docstring: "Integer arithmetic decides `adopted`; `shrink_pct`/`wall_ratio` are
floats for the printed verdict line only". Only `shrunk` is integer; `wall_ok =
candidate.concurrent_ms <= 1.5 * current.concurrent_ms` is a float comparison and is
equally part of `adopted`.
**Fix:** "Integer arithmetic decides the shrink clause (a `1 - a / b` form reads
0.0999... at exactly 10%, D-18); the wall clause compares the measured floats directly,
`candidate <= 1.5 * current`."

### IN-02: `test_bench.py` docstring claims no `conftest.py` exists anywhere in the repo; `tests/conftest.py` does

**File:** `tests/test_bench.py:27-29`
**Issue:** Still open — unchanged by `6dce386` (which only touched lines ~541-547). The
docstring claims no `conftest.py` exists anywhere in the repo; `tests/conftest.py` exists
(the autouse root-logger reset). The substantive point (it puts `tests/` on `sys.path`,
not the repo root, so it does not help `bench` import) is stated correctly.
**Fix:** "... and `tests/conftest.py` (which exists for the logger reset) puts `tests/`
on `sys.path`, not the repo root, so it does not help either."

### IN-03: `cli.md` "Tests" still says "4 tests" beside a new section that names three others

**File:** `docs/architecture/cli.md:73`
**Issue:** Still open — the `55e2979` fix reworded the "Shape" and "Errors" sections only;
the "Tests" section (now at line 73, after the Errors-section line growth) is unchanged
and still reads "`tests/test_cli.py`, 4 tests — added because the CLI had none...".
Already noted as a tangent in the resolved debt record this phase closed.
**Fix:** "`tests/test_cli.py` -- added because the CLI had none and the README's own
example did not run (F3/F8). ..."

### IN-04: The shareable-link proof pins eight verbatim `app.js` source lines, so a whitespace-only edit fails a test named as a round-trip proof

**File:** `tests/test_api.py:158-169`
**Issue:** Still open — `tests/test_api.py` is outside this diff's scope (not one of the
six files the fix commits touched; confirmed via `git diff b9dc04e..HEAD --stat`) and the
file is unchanged. `assert snippet in source` on exact strings; a reformat of `app.js`
fails the test with a message naming a snippet, not a behaviour.
**Fix:** Either note the brittleness in the docstring, or match on whitespace-normalised
source with the same snippets normalised.

### IN-05: `cast(dict[str, float], HOLES)` asserts a type the value does not have

**File:** `tests/test_model.py:1430-1432`
**Issue:** Still open — `tests/test_model.py` is outside this diff's scope and unchanged
(confirmed by re-reading the current lines and by its absence from `git diff
b9dc04e..HEAD --stat`). `HOLES`/`CELLS` are inferred `dict[str, int]`; the `cast` exists
only to make them assignable beside `SPOKES` (`dict[str, float]`).
**Fix:**
```python
HOLES: dict[str, float] = {"hole_count": 6, "hole_d": 4, "hole_circle_d": 20}
CELLS: dict[str, float] = {"hex_cell": 3, "hex_wall": 1}
```
and drop the two `cast(...)` calls and the `typing.cast` import if nothing else uses it.

---

_Reviewed: 2026-10-01T02:42:01Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
