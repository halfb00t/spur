---
phase: 12-composition-pass
reviewed: 2026-09-30T17:07:24Z
depth: standard
files_reviewed: 26
files_reviewed_list:
  - bench/build_time.py
  - bench/export_cost.py
  - bench/RESULTS.md
  - bench/sweeps/composed.json
  - bench/sweeps/spoke_cutout.json
  - docs/architecture/cli.md
  - docs/architecture/decision_log.md
  - docs/ideas/2026-09-21-browser-test-for-the-viewer.md
  - docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md
  - docs/ideas/2026-09-29-conditional-form-fields.md
  - docs/ideas/INDEX.md
  - docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md
  - docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md
  - docs/tech_debt/resolved/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md
  - Makefile
  - README.md
  - src/spur/app.py
  - src/spur/params.py
  - tests/composition.py
  - tests/test_api.py
  - tests/test_bench.py
  - tests/test_calc.py
  - tests/test_cli.py
  - tests/test_model.py
findings:
  critical: 0
  warning: 9
  info: 5
  total: 14
status: issues_found
---

# Phase 12: Code Review Report

**Reviewed:** 2026-09-30T00:00:00Z
**Depth:** standard
**Files Reviewed:** 26
**Status:** issues_found

## Summary

This is the cross-CLI second pass over the same `c9a169d..HEAD` diff an internal (Claude)
review already covered at `6b7d67d` (`12-REVIEW.md`, findings WR-01..05/IN-01..05, all
still `open`). None of the reviewed files changed between `6b7d67d` and `HEAD` (confirmed
by `git diff 6b7d67d..HEAD -- <files>` — empty), so all ten prior findings still hold
verbatim at the current HEAD; they are carried forward under their original ids per the
task's instruction to keep ids stable across passes. An external reviewer lane (codex)
independently reviewed the same scope and surfaced five claims; I re-opened and re-read
every cited line myself before accepting any of them. Four are new, confirmed defects
(added below as WR-06..09); one (the wrong-test citation for the schema/CLI order proof)
duplicates the already-open WR-05 and is folded into it rather than re-numbered.

The pattern across both passes is consistent with this project's own standing rule (L08,
"a number the tool prints is a number someone will cut metal to"): every new defect this
pass found is a doc or decision-log claim that overstates what was actually measured —
end-of-run load readings relabelled "at start", "arithmetic total" framed as a universal
"below" when one of three rows measured above it, "mesh content" claimed where only a
triangle *count* was compared, and a regression test whose fixture values can't actually
distinguish the bug it claims to catch. None of these touch code that computes a
dimension a user would cut metal to (`calc.py`/`model.py` are unchanged in this diff) —
they are all in the bench/decision-log/test layer — so no Critical findings result, but
per this project's explicit framing (a plausible-but-unmeasured claim in a record is a
real defect, not a doc nit) all nine are Warnings, matching the severity the prior pass
already assigned to the same class of issue.

## Structural Findings (fallow)

None provided for this run.

## Narrative Findings (AI reviewer)

## Warnings

### WR-01: `cli.md` "Errors" claims every parameter error prints `error: <field>: <message>` -- two of the three shapes it groups do not

**File:** `docs/architecture/cli.md:36-38` (and the same claim in "Shape", `docs/architecture/cli.md:24-26`)
**Issue:** Confirmed unchanged from the prior pass (`6b7d67d..HEAD` diff on this file is
empty). `check()` refusals print `error: <message>` with no field prefix (`loc` is empty
for the `infeasible` error type); argparse's own flag-parsing errors print argparse's own
`spur <cmd>: error: argument --x: ...` shape; only pydantic field-level errors match the
documented `error: <field>: <message>` shape. `tests/test_cli.py:435-437`
(`test_every_refusal_reads_the_same_on_the_api_and_the_cli`) itself asserts the no-prefix
shape for `check()` refusals, directly contradicting this doc section.

Independently re-verified one more inaccuracy in the same section the external lane
flagged (codex claim 4): the section's own opening line, "Three cases, three exit
statuses" (`cli.md:32`), is also wrong — the three cases produce only **two** distinct
exit status values (2 for a parameter error, 1 for both the bad-extension and
`BuildError` cases), not three. This is additional evidence the section was not checked
against the code it describes, same root cause as the field-prefix claim.
**Fix:**
```markdown
Three cases, two exit statuses -- the CLI's real contract, not a guess from the API's:

- A parameter error raises `SystemExit(2)` -- exit 2 -- with one of three stderr shapes:
  argparse's own `spur <cmd>: error: argument --x: ...` for a flag it cannot parse;
  `error: <field>: <message>` for a field-level `GearParams` bound; and
  `error: <message>` (no field prefix -- the `infeasible` error's `loc` is empty) for a
  `check()` refusal, the sentence the API's 422 carries in `detail[].msg`. The fields the
  API names in `detail[].ctx.fields` are not printed by the CLI.
```
And align the "Shape" paragraph (`cli.md:24-26`) with it.

### WR-02: `hole_count`'s comment still attributes the 14.87 s row to "Phase 12 ... (re-measured in the same section)" after this phase corrected the identical sentence on `spoke_count`

**File:** `src/spur/params.py:142-143`
**Issue:** Confirmed unchanged from the prior pass. `spoke_count`'s comment was corrected
this phase from "Phase 12's 14.87 s tip-chamfer row (re-measured in the same section)" to
"Phase 10's 14.87 s tip-chamfer row (an arithmetic total only, not yet a real composed
build)" (`params.py:109-110`); `hole_count`'s comment four fields below still carries the
original, uncorrected wording, naming the wrong phase for a re-measurement that did not
happen.
**Fix:**
```python
    # near-linear; 60 holes leave margin beside Phase 10's 14.87 s tip-chamfer row (an
    # arithmetic total only -- Phase 12's composed sweep measured the real stack).
```

### WR-03: `bench.export_cost` exits 1 on its only failure path without saying why

**File:** `bench/export_cost.py:296-299`
**Issue:** Confirmed unchanged. When the copy and in-place children disagree on triangle
count, `main()` returns 1 with nothing on stderr, forcing the reader to diff six table
rows by eye to find what failed.
**Fix:**
```python
    if len(all_triangles) != 1:
        print(f"error: copy and in-place exports disagree on triangle count "
              f"({sorted(all_triangles)}) -- L24's invariant (a copy meshes identically) "
              "did not hold on this set", file=sys.stderr)
        return 1
    return 0
```

### WR-04: A failing child process reports only "returned non-zero exit status 1" -- its `BuildError` text and traceback are captured and discarded

**File:** `bench/export_cost.py:268-273`
**Issue:** Confirmed unchanged. `subprocess.run(..., capture_output=True, check=True)`
raises `CalledProcessError`; the child's stderr (where a `BuildError`, an OCCT
`Standard_Failure`, or `_find_set`'s own error line would land) is captured and never
printed. `json.loads(child.stdout.strip().splitlines()[-1])` on the next line would also
raise a bare `IndexError` on an empty-stdout success.
**Fix:**
```python
            child = subprocess.run(
                [sys.executable, "-m", "bench.export_cost", str(args.sweep),
                 "--set", args.label, "--child", mode],
                capture_output=True, text=True, check=False,
            )
            if child.returncode != 0 or not child.stdout.strip():
                sys.stderr.write(child.stderr)
                raise SystemExit(
                    f"error: --child {mode} run {run} exited {child.returncode} "
                    "without a payload (its stderr is above)")
            child_payload: _ChildPayload = json.loads(child.stdout.strip().splitlines()[-1])
```

### WR-05: L31 attributes the "schema, form source and CLI parser in one order" proof to the wrong test

**File:** `docs/architecture/decision_log.md:1355-1357`
**Issue:** Confirmed unchanged, and independently re-confirmed by the external reviewer
lane (its claim 6 cites the same two tests). L31 credits
`tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code`
with proving the schema/form/CLI order; that test (`tests/test_api.py:142-191`) never
touches the CLI or group order. The walk across `/api/schema` group order and `--help`
flag order is `tests/test_cli.py::test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`
(`tests/test_cli.py:187-236`).
**Fix:**
```markdown
One generic field walk
(`tests/test_cli.py::test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`)
proves every v0.2 field reaches the schema and the CLI parser in that one order, without a
per-field test; a second
(`tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code`)
proves `app.js` carries the hash -> form -> query path generically, naming no field.
```

### WR-06: the "level 9 compared against the currently-adopted level" regression test can't actually distinguish that from the bug it names

_New in this pass — raised by the external `codex` reviewer lane, re-verified against the cited source before acceptance._

**File:** `tests/test_bench.py:543` (function `test_level_9_is_compared_against_the_level_currently_adopted`, second assertion block, lines ~538-547)
**Issue:** Independently re-derived the arithmetic rather than trusting the external
claim. The test's docstring says the second scenario "would wrongly adopt level 9 if the
comparison stayed pinned to level 1" -- i.e. it exists to prove `_decisions()`
(`bench/export_cost.py:122-141`) compares a later candidate against the level *actually
adopted so far* (here, level 6, `current.concurrent_ms=150.0`), not always against level
1 (`concurrent_ms=100.0`). But `level9_beats_1_not_6`'s `concurrent_ms=300.0` fails the
1.5x wall bar against **both** bases: `300 > 1.5*150=225` (correct comparison) and
`300 > 1.5*100=150` (the buggy comparison the test claims to catch). Since `adopted =
shrunk and wall_ok`, `wall_ok` is `False` either way, so `adopted` is `False` and the
level stays at 6 under a hypothetical regression that re-pinned the comparison to level
1, identically to the correct implementation. The assertion `== 6` therefore passes
whether or not the bug it's named for exists; only the `out_bytes`/shrink-bar half of the
scenario is actually exercised by this row. The corresponding unit in
`bench/build_time.py`'s own docstring standard ("a short-circuiting generator would
silently skip the rest") is the kind of regression-catching the bench package holds
itself to elsewhere; this row falls short of it for the wall clause specifically.
**Fix:** Lower `level9_beats_1_not_6`'s `concurrent_ms` so it separates the two bases,
e.g. 200.0 (fails against level1's 150 wall bar, passes against level6's 225 wall bar) --
combined with the already-failing shrink bar this still holds level at 6, but now do the
same for a *third* row where shrink also passes only against level 1 (not level 6) and
`concurrent_ms` passes against level 6's bar only, so a re-pinned-to-level-1 regression
would flip that row's `adopted` to `False` when it should be `True` (or vice-versa),
making the assertion fail under the bug it claims to catch.

### WR-07: decision-log and RESULTS.md prose calls two end-of-run load readings "at-start loads"

_New in this pass — raised by the external `codex` reviewer lane, re-verified against the cited source before acceptance._

**File:** `docs/architecture/decision_log.md:1301-1302`, and the identical claim in `bench/RESULTS.md:1559-1560`
**Issue:** Both records already correctly document, a few sentences earlier in the same
paragraph, that Runs 1 and 2's load figures (12.66 and 7.04) were mismeasured: "the
runner itself was found to be reading load at the end of a 6-7 minute sweep, not its
start" (`decision_log.md:1297-1298`; the identical disclosure sits at
`bench/RESULTS.md:1255-1261`, which states Run 1 and Run 2's genuine at-start readings
were 1.13 and 1.33). Despite that disclosure, the very next sentence in both files
labels all four numbers uniformly: "the human reviewed all four runs -- **at-start
loads** 12.66, 7.04, 2.74 and 1.54, an eightfold spread" (`decision_log.md:1301-1302`;
`bench/RESULTS.md:1559-1560` reads the same). 12.66 and 7.04 are not at-start readings by
the file's own preceding sentence -- they are end-of-run readings under a tool bug that
was fixed for Runs 3 and 4 only. This is the project's own standing rule (L08) applied to
its own decision record: a record that states a measurement was taken one way in one
sentence and calls it something else two sentences later is a plausible-but-wrong number
in exactly the kind of document CLAUDE.md calls "the single source of locked decisions."
The underlying D-02 supersession conclusion (four runs agree the four spoke rows are over
budget regardless of load) is not in question -- only the mislabelling of what was
measured.
**Fix:**
```markdown
the human reviewed all four runs -- loads 12.66 and 7.04 (both read at the end of the
run, the tool-bug reading; see above) and 2.74 and 1.54 (read at a genuine start, after
the fix) -- an eightfold spread across the two measurement methods -- and found the same
four `spoke_count=40` composed rows over `SPUR_BUILD_TIMEOUT` (30 s) in every one...
```
Apply the equivalent correction at `bench/RESULTS.md:1559-1560`.

### WR-08: L31 says every composed pattern measured below its arithmetic total; the honeycomb row it cites in the same sentence measured above it

_New in this pass — raised by the external `codex` reviewer lane, re-verified against the cited source before acceptance._

**File:** `docs/architecture/decision_log.md:1315-1318`
**Issue:** "Each pattern's worst composed row read below the Phase 10/11 arithmetic
total it replaced by measurement, not assumption: spokes 32.03 s against a 33.39 s total
(-1.36 s), holes 25.05 s against 26.66 s (-1.61 s), honeycomb 27.49 s against 23.52 s
(**+3.97 s**, the one pattern where stacking cost more than the naive sum)." The opening
clause ("read below ... the total") is contradicted by the honeycomb figure in the same
sentence, which the sentence itself correctly flags as the exception ("stacking cost
more"). `bench/RESULTS.md:1486-1504` records the same three numbers without making the
false universal claim, so the error is specific to this decision-log summary sentence,
not the underlying measurement. This is the same class of defect as WR-07: a locked
decision record's summary line says something its own supporting data, one clause later,
contradicts.
**Fix:**
```markdown
Two of the three patterns' worst composed rows read below the Phase 10/11 arithmetic
total they replaced by measurement, not assumption: spokes 32.03 s against a 33.39 s
total (-1.36 s), holes 25.05 s against 26.66 s (-1.61 s). The third, honeycomb, measured
above its total: 27.49 s against 23.52 s (+3.97 s) -- the one pattern where stacking cost
more than the naive sum.
```

### WR-09: "L24's invariant held" / "identical mesh content" overstates what the triangle-count comparison actually checks

_New in this pass — raised by the external `codex` reviewer lane, re-verified against the cited source before acceptance._

**File:** `bench/RESULTS.md:1773-1774`; underlying check at `bench/export_cost.py:296-298`
**Issue:** `bench/RESULTS.md` states "Exit code: 0 (every run's triangle count agrees --
copy and in-place produced the same mesh content, L24's invariant held)." The only check
performed, both in `main()` (`export_cost.py:296-298`) and in the printed evidence table
(six rows, all reading the same integer `346120`), is that the *set* of triangle counts
across all six runs has exactly one element -- i.e. every run produced the same *number*
of triangles. Two meshes can share a triangle count while differing in vertex positions,
winding order, or topology (a `.copy()` that silently perturbed geometry while
preserving facet count would pass this check). "Produced the same mesh content" is a
claim about geometry the script never measures; only "agree on triangle count" is
measured. This is the same plausible-but-unmeasured pattern the project's own standing
rule (L08) warns against, applied here to a decision record rather than to a part
dimension.
**Fix:**
```markdown
Exit code: 0 (every run's triangle count agrees -- copy and in-place produced the same
triangle *count*; this does not by itself prove identical mesh content down to vertex
positions or winding, which this script does not check).
```
If the stronger "identical mesh content" claim is wanted, add a content-level check
(e.g. hash the exported STL's vertex/facet bytes, ignoring header timestamp bytes if
any) and cite that instead of the triangle count.

## Info

### IN-01: `_decisions` docstring says integer arithmetic decides `adopted`; the wall clause is float

**File:** `bench/export_cost.py:122-134`
**Issue:** Confirmed unchanged. The docstring: "Integer arithmetic decides `adopted`;
`shrink_pct`/`wall_ratio` are floats for the printed verdict line only". Only `shrunk` is
integer; `wall_ok = candidate.concurrent_ms <= 1.5 * current.concurrent_ms` is a float
comparison and is equally part of `adopted`.
**Fix:** "Integer arithmetic decides the shrink clause (a `1 - a / b` form reads
0.0999... at exactly 10%, D-18); the wall clause compares the measured floats directly,
`candidate <= 1.5 * current`."

### IN-02: `test_bench.py` docstring claims no `conftest.py` exists anywhere in the repo; `tests/conftest.py` does

**File:** `tests/test_bench.py:27-29`
**Issue:** Confirmed unchanged. `tests/conftest.py` exists (the autouse root-logger
reset); the substantive point (it puts `tests/` on `sys.path`, not the repo root, so it
does not help `bench` import) is stronger stated correctly.
**Fix:** "... and `tests/conftest.py` (which exists for the logger reset) puts `tests/`
on `sys.path`, not the repo root, so it does not help either."

### IN-03: `cli.md` "Tests" still says "4 tests" beside a new section that names three others

**File:** `docs/architecture/cli.md:69`
**Issue:** Confirmed unchanged. Already noted as a tangent in the resolved debt record
this phase closed.
**Fix:** "`tests/test_cli.py` -- added because the CLI had none and the README's own
example did not run (F3/F8). ..."

### IN-04: The shareable-link proof pins eight verbatim `app.js` source lines, so a whitespace-only edit fails a test named as a round-trip proof

**File:** `tests/test_api.py:158-169`
**Issue:** Confirmed unchanged. `assert snippet in source` on exact strings; a reformat
of `app.js` fails the test with a message naming a snippet, not a behaviour.
**Fix:** Either note the brittleness in the docstring, or match on whitespace-normalised
source with the same snippets normalised.

### IN-05: `cast(dict[str, float], HOLES)` asserts a type the value does not have

**File:** `tests/test_model.py:1430-1432`
**Issue:** Confirmed unchanged. `HOLES`/`CELLS` are inferred `dict[str, int]`; the
`cast` exists only to make them assignable beside `SPOKES` (`dict[str, float]`).
**Fix:**
```python
HOLES: dict[str, float] = {"hole_count": 6, "hole_d": 4, "hole_circle_d": 20}
CELLS: dict[str, float] = {"hex_cell": 3, "hex_wall": 1}
```
and drop the two `cast(...)` calls and the `typing.cast` import if nothing else uses it.

## External claims checked and rejected

One external-lane claim (codex claim 4's field-prefix part) duplicates WR-01 and is
folded into it above rather than listed separately. No external claim was found
unverifiable or false on inspection; all five were independently confirmed against the
cited source (four as new findings WR-06..09, one as additional evidence for the
already-open WR-01/WR-05).

---

_Reviewed: 2026-09-30T17:07:24Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
