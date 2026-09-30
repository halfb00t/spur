---
phase: 12-composition-pass
reviewed: 2026-09-30T14:23:41Z
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
  warning: 5
  info: 5
  total: 10
status: issues_found
---

# Phase 12: Code Review Report

**Reviewed:** 2026-09-30T14:23:41Z
**Depth:** standard
**Files Reviewed:** 26
**Status:** issues_found

## Summary

Reviewed the full `c9a169d..HEAD` diff for Phase 12: two shipped-code edits (`params.py`'s `spoke_count` `le` 40 -> 32, a dated comment table in `app.py`), the `bench/build_time.py` fix and D-16 columns, the new `bench/export_cost.py`, two sweep files, the composition tables and four test modules, and the decision-log / tech-debt / idea records. `make verify` at HEAD is reported as 907 passed; I additionally ran the three CLI error shapes by hand to check `cli.md`'s new "Errors" contract and verified every commit SHA the decision log and debt records cite resolves in this repository.

The shipped-code changes are sound: the `le` lowering is backed by the measured gate, its schema/bound tests moved with it, the sweep files no longer carry 40, and the `app.py` table arithmetic (7.46% / 7.44% / 13.43x / 29.9% / 27.7%) reproduces from the recorded bytes. The `bench/build_time.py` load-read fix is correct and pinned by a test that can actually catch a regression. `tests/composition.py` is hand-written, never derived from `calc`, as claimed.

No blockers. Five warnings: `cli.md`'s new "real contract" text mis-describes what two of its three parameter-error shapes print (verified by running them); a `params.py` comment left contradicting the sibling comment this phase corrected; `bench/export_cost.py` exits 1 without a message on its one failure path and swallows a failing child's stderr; and L31 attributes the schema/CLI order proof to the wrong test. The remaining items are stale docstrings and a type cast.

## Narrative Findings (AI reviewer)

## Warnings

### WR-01: `cli.md` "Errors" claims every parameter error prints `error: <field>: <message>` -- two of the three shapes it groups do not

**File:** `docs/architecture/cli.md:36-38` (and the same claim in "Shape", `docs/architecture/cli.md:24-26`)
**Issue:** The new section calls itself "the CLI's real contract, not a guess" and states that a parameter error -- "argparse's own flag parsing, or `GearParams`/`check()` validation" -- "prints `error: <field>: <message>` per error". Verified against `src/spur/cli.py:63-68` and by running the CLI:

- `check()` refusal (`spur info --keyway-width 3`): `error: A keyway needs both keyway_width and keyway_depth: ...` -- no field prefix, because the `infeasible` error's `loc` is empty and `_params` only prefixes when `where` is non-empty. `tests/test_cli.py:435-437` (`test_every_refusal_reads_the_same_on_the_api_and_the_cli`) asserts exactly `err == f"error: {sentence}"` for all 23 refusals, so this phase's own test contradicts this phase's own doc.
- argparse error (`spur info --teeth abc`): `spur info: error: argument --teeth: invalid int value: 'abc'` plus a usage block -- argparse's format, not `error: <field>: <message>`.
- Only pydantic field-level errors (`spur info --spoke-count 33` -> `error: spoke_count: Input should be less than or equal to 32`) match the sentence.

The follow-on clause "the same fields the API names in `detail[].ctx.fields`" is also false for the `check()` case: the API puts `fields` in `ctx`, the CLI prints none of them. The debt this section resolved (`2026-09-28-cli-md-claims-exit-2-...`) was precisely "a doc claim never executed"; the replacement text repeats the pattern one bullet over.
**Fix:** State the three stderr shapes the code actually produces:
```markdown
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
**Issue:** This phase edited the `spoke_count` comment from "Phase 12's 14.87 s tip-chamfer row (re-measured in the same section)" to "Phase 10's 14.87 s tip-chamfer row (an arithmetic total only, not yet a real composed build)" (`params.py:109-110`). The `hole_count` comment four fields below carries the original, uncorrected wording. It is wrong on both counts: 14.87 s is Phase 10's single-feature tip-chamfer row (`bench/RESULTS.md:826`), and the Phase 11 section (`RESULTS.md:959-1214`) contains no re-measurement of that row -- `RESULTS.md:1097` says "beside Phase 10's 14.87 s tip-chamfer row (Phase 12's own combined re-measurement, not ...)". Under this project's comment standard (`CODING_VALUES.md:20-25`, "carry the measurement ... that forced the choice") a comment that names the wrong phase and a re-measurement that did not happen is the failure mode the standard exists to prevent, and the file now says two different things about the same number.
**Fix:**
```python
    # near-linear; 60 holes leave margin beside Phase 10's 14.87 s tip-chamfer row (an
    # arithmetic total only -- Phase 12's composed sweep measured the real stack).
```

### WR-03: `bench.export_cost` exits 1 on its only failure path without saying why

**File:** `bench/export_cost.py:296-299`
**Issue:** When the copy and in-place children disagree on triangle count -- the one condition that would mean L24's invariant broke -- `main()` returns 1 with nothing on stderr. The table above it shows the counts, but a `make bench.export` failing with a bare exit status forces the reader to diff six rows by eye to discover what failed. `CODING_VALUES.md:130` ("fail loud, once, with an actionable message") and `bench/build_time.py:196-200`, which prints a `warning:` line per over-budget row before returning 1, both set the expectation this script misses.
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
**Issue:** `subprocess.run(..., capture_output=True, check=True)` raises `CalledProcessError` whose message is the command and status; the child's stderr (where a `BuildError` from `model._build_checked`, an OCCT `Standard_Failure`, or `_find_set`'s own `error: no set labeled ...` line lands) sits only in the exception's `.stderr` attribute and is never printed. The parent's `main()` has already built the same set once, so a child failure here is most likely a kernel non-determinism or memory event on a 1.8 GiB process -- exactly the case where the child's message is the only diagnostic. `json.loads(child.stdout.strip().splitlines()[-1])` on the next line would also raise a bare `IndexError` if a child exited 0 with empty stdout.
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
**Issue:** L31 says "One generic field walk (`tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code`) proves every v0.2 field reaches the schema, the form's source and the CLI parser in that one order". That test (`tests/test_api.py:142-191`) never touches the CLI or group order -- it asserts eight `app.js` snippets and that no `GearParams` name appears as a per-field special case. The walk across `/api/schema` group order and the `--help` flag order is `tests/test_cli.py::test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order` (`tests/test_cli.py:187-236`). The decision log is "the single source of locked decisions" (CLAUDE.md); a reader following this citation to check the seven-group claim lands on a test that does not assert it.
**Fix:**
```markdown
One generic field walk
(`tests/test_cli.py::test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`)
proves every v0.2 field reaches the schema and the CLI parser in that one order, without a
per-field test; a second
(`tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code`)
proves `app.js` carries the hash -> form -> query path generically, naming no field.
```

## Info

### IN-01: `_decisions` docstring says integer arithmetic decides `adopted`; the wall clause is float

**File:** `bench/export_cost.py:122-134`
**Issue:** The docstring: "Integer arithmetic decides `adopted`; `shrink_pct`/`wall_ratio` are floats for the printed verdict line only". Only `shrunk` is integer (`10 * (a - b) >= a`); `wall_ok = candidate.concurrent_ms <= 1.5 * current.concurrent_ms` is a float comparison on millisecond floats. The test at `tests/test_bench.py:521-523` pins the 1.5x edge at 150.0 vs 150.001, which holds, but the docstring's stated reason for the integer form does not cover half the decision.
**Fix:** "Integer arithmetic decides the shrink clause (a `1 - a / b` form reads 0.0999... at exactly 10%, D-18); the wall clause compares the measured floats directly, `candidate <= 1.5 * current`."

### IN-02: `test_bench.py` docstring claims no `conftest.py` exists anywhere in the repo; `tests/conftest.py` does

**File:** `tests/test_bench.py:27-29`
**Issue:** "there is no `tests/__init__.py` or `conftest.py` anywhere in this repo to do it another way" -- `tests/conftest.py` exists (the autouse root-logger reset). The line predates this phase (`d334049a`, 2026-09-24) but the docstring was extended this phase, and the substantive point (a bare `pytest` still cannot import `bench` because a `tests/conftest.py` only puts `tests/` on `sys.path`, not the repo root) is stronger stated correctly.
**Fix:** "... and `tests/conftest.py` (which exists for the logger reset) puts `tests/` on `sys.path`, not the repo root, so it does not help either."

### IN-03: `cli.md` "Tests" still says "4 tests" beside a new section that names three others

**File:** `docs/architecture/cli.md:69`
**Issue:** The resolved debt record (`docs/tech_debt/resolved/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md:60-62`) already notes this as a tangent. The file now has an "Errors" section citing tests by name and a "Tests" section counting four; `tests/test_cli.py` has 40-odd. Since the file was edited this phase, dropping the count is a one-word fix rather than a new debt item.
**Fix:** "`tests/test_cli.py` -- added because the CLI had none and the README's own example did not run (F3/F8). ..."

### IN-04: The shareable-link proof pins eight verbatim `app.js` source lines, so a whitespace-only edit fails a test named as a round-trip proof

**File:** `tests/test_api.py:158-169`
**Issue:** `assert snippet in source` on exact strings such as `"for (const [name, { input }] of fields) input.value = h.get(name) ?? defaults[name];"`. Reflowing that line, renaming `h`, or splitting the ternary fails `test_the_shareable_link_round_trips_every_field_through_generic_code` with a message naming a snippet, not a behaviour; the name then tells the next reader the round trip broke when only formatting did. Acceptable as a deliberate static proof (D-11) but worth knowing the brittleness is by construction.
**Fix:** Either note the brittleness in the docstring ("these are exact source lines; a reformat of app.js must update them"), or match on whitespace-normalised source (`re.sub(r"\s+", " ", source)`) with the same snippets normalised.

### IN-05: `cast(dict[str, float], HOLES)` asserts a type the value does not have

**File:** `tests/test_model.py:1430-1432`
**Issue:** `HOLES` and `CELLS` (`tests/test_model.py:253-255`) are inferred `dict[str, int]`; the `cast` exists only to make them assignable beside `SPOKES` (`dict[str, float]`). It is harmless at runtime but is the `as any`-shaped move the review checklist flags, and the honest fix is one annotation at the definition site.
**Fix:**
```python
HOLES: dict[str, float] = {"hole_count": 6, "hole_d": 4, "hole_circle_d": 20}
CELLS: dict[str, float] = {"hex_cell": 3, "hex_wall": 1}
```
and drop the two `cast(...)` calls and the `typing.cast` import if nothing else uses it.

---

_Reviewed: 2026-09-30T14:23:41Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
