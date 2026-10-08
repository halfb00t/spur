---
phase: 18-trochoid-maths-proved
reviewed: 2026-10-08T00:00:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - bench/RESULTS.md
  - bench/trochoid.py
  - docs/architecture/gear-maths/implementation.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md
  - src/spur/calc.py
  - tests/test_bench.py
  - tests/test_calc.py
  - tests/test_trochoid.py
  - tests/trochoid_oracle.py
findings:
  critical: 0
  warning: 0
  info: 8
  total: 8
status: issues_found
---

# Phase 18: Code Review Report

**Reviewed:** 2026-10-08
**Depth:** standard (incremental re-review of gap plan 18-06, diff base `2f6e1e7`)
**Files Reviewed:** 10 (the phase scope; this pass re-read only `src/spur/calc.py` and
`tests/test_trochoid.py` for the `2f6e1e7..HEAD` hunks)
**Status:** issues_found

## Summary

This pass judged the two gap-closure commits: `8e96c2d` (a test that makes the fourth `curve
invalid` guard arm in `_root_curve` fire, plus a docstring correction) and `085aee7` (a
`ValueError` guard in `cutter()` for a non-finite or negative tip radius, with its test). Both
hunks are correct. No critical issue and no warning; the verdict on the two earlier warnings is
below. The six info findings from the first review are carried forward unchanged, and two new
info items on the gap hunks are added.

Checks I ran, so the verdict rests on commands and not on reading:

- `ruff check` and `mypy --strict` on `src/spur/calc.py` and `tests/test_trochoid.py`: clean.
  `pytest tests/test_trochoid.py tests/test_calc.py`: `478 passed`. (The full `make verify` was
  not re-run; this pass covers the two files.)
- Pre-guard behaviour, measured on a scratch `git archive` of `2f6e1e7` (12 teeth, module 1,
  20 degrees, backlash 0, bore off): `nan` gave `trochoid`, no reason, no sentence, radius
  0.471; `-0.1` gave `trochoid`, no sentence; `-0.5` gave `radial` / `curve invalid`; `-inf` gave
  `radial` / `bracket degenerate`; `inf` gave `trochoid` with the cap sentence. Every claim in
  the new test's docstring matches. On HEAD, `nan`, `+-inf`, `-0.1` and `-0.5` all raise
  `ValueError` ("... got nan" etc., through `root_mode` too), and `0.0` / `-0.0` answer
  `trochoid` with no warning.
- Mutation probes on scratch copies of HEAD (working tree untouched). The new arm test is killed
  by replacing the whole fourth arm with `False` and by `any` -> `all`. It survives a tolerance
  of 5e-4 on the half-angle compare, which is correct: the bend is 1e-3. The rho test is killed
  by `rho < 0` -> `rho <= 0` (the `0.0` rows) and by dropping the NaN clause.
- Patch isolation: the wrapper `junction_then_arm` calls the real `_junction` (bound in the test
  module at import) while `calc._trochoid_point` is already patched, but `state["calls"]` is -1
  during that call, so the bent function returns the real point. Arming happens only after the
  junction solve returns. The bent sample is the fifteenth call after arming, i.e. `points[-2]`
  (`tuple(...)` in `_root_curve` samples in order and nothing else calls the point function
  before it). Measured: `points[-2]` is radius 4.6401, half-angle 0.1686; `rb` 4.6985;
  junction radius 4.7256. The bent point is radius `rb + 0.01` = 4.7085, strictly between its
  neighbours, so the rising-radius arm stays quiet; its half-angle is about 0.17 against
  `pi/10` = 0.314 and `ra`, so the tip-circle and centreline arms stay quiet. Only the fourth
  arm can fire, and `state["bent"]` proves the sample was reached.
- The guard sits before `profile(p)` and every other arithmetic line in `cutter()`; its message
  names the offending value with `{rho!r}`, so "nan" and "-0.1" are what the user reads, and it
  claims nothing beyond "finite, non-negative millimetre value".

## Resolved since last review

- **WR-01** (fourth `curve invalid` arm untested): resolved by `8e96c2d`. The new test
  `test_a_crossing_curve_with_an_early_point_outside_the_involute_is_refused` reaches the arm
  and fails when the arm is removed; the older test's docstring now says it covers two of four
  arms and names where the others are covered.
- **WR-02** (`cutter()` / `root_mode()` take an unvalidated tip radius): resolved by `085aee7`.
  `cutter()` raises `ValueError` for NaN, +-inf and negative values before any arithmetic;
  parametrised rows cover `nan`, `inf`, `-inf` and `-0.1`, and `0.0` / `-0.0` are accepted.
  Code comments cite "18-REVIEW WR-01 / WR-02"; those ids now live only in this section.

## Info

### IN-01: The cap sentence says "the largest", but prints a value floored to 3 dp, and prints `0.000` for a cap under 1 micrometre

**File:** `src/spur/calc.py:1554-1556`, `src/spur/calc.py:1287`
**Issue:** "Cutter tip radius reduced to {rho:.3f} mm, the largest that leaves the cutter a tip
land" is true to within 0.001 mm, not exactly: the cap is floored, so up to 1 micrometre of
legal radius is thrown away. At 12 teeth, module 1, 32.14 degrees, backlash 0 the cap is
1.05e-4 mm, the used radius is exactly 0.0, and the sentence reads "reduced to 0.000 mm, the
largest that leaves a tip land" while a land of 5.8e-5 mm exists at that cap. The printed and
used number are the same float, so L08 is met; the word "largest" is the overclaim. The flooring
rationale (round-to-nearest produced a -3.6e-4 mm land) is sound and documented.
**Fix:** Say "to {rho:.3f} mm, within 0.001 mm of the largest that leaves ..." or drop "the
largest". No code change needed in `cutter`.

### IN-02: Two public entry points give different answers for the same gear, and `root_mode` discards the curve it computed

**File:** `src/spur/calc.py:1479-1487`, `src/spur/calc.py:1497-1535`
**Issue:** `root_mode` refuses `rb <= rf` in closed form; `trochoid_root` has no such test and
returns a curve for the same gear. `bench/RESULTS.md` ("the 42- and 43-tooth rows print the
generator's curve anyway") and the T4 test (`_zhang_form_diameter_in`) rely on this, so it is
deliberate, but the module's headline claim is "the single answer" (REQ-root-mode-single-predicate)
and `trochoid_root`'s docstring says "or None when no honest curve exists". For a 42-tooth gear it
returns a curve that no consumer is allowed to use. Separately, `root_mode` builds the full curve,
keeps only `isinstance(curve, RootCurve)`, and drops it, so a caller needing both the mode and the
points computes the solve twice (33.7 usec against 30.7 usec for the tangent default gear in
`bench/RESULTS.md`, 88.9 usec for a crossing) and can only get the curve through the second,
independent call. Performance is out of scope; the design point is that mode and curve are not
carried together, so Phase 19 can read one and the other from calls that differ.
**Fix:** Add a sentence to `trochoid_root`'s docstring: "It does not test `rb <= rf`; ask
`root_mode` whether the curve applies." Consider a `curve: RootCurve | None` field on `RootMode`
filled when `mode == "trochoid"`.

### IN-03: The epsilon bench cannot fail on the shipped constant

**File:** `bench/trochoid.py:176-224`
**Issue:** `run_epsilon` prints a recommended epsilon and fails only if it exceeds
`EPSILON_CEILING = 1e-3`. It never compares the recommendation with `calc.TROCHOID_JOIN_EPS`
(imported at line 54 but unused there). If a future re-run recommends 1e-3, it prints `verdict: ok`
while the shipped 1e-4 sits under the 10x margin that the constant's own comment promises. In
practice the sweep tally in `tests/test_calc.py` moves if the constant moves (I confirmed
1e-5 and 2e-5 both fail it), so nothing ships wrong today; the bench's verdict just does not say
what its docstring implies.
**Fix:** After computing `eps`, add `if TROCHOID_JOIN_EPS < eps: print(...FAIL...); return 1`.

### IN-04: Small bench hygiene items

**File:** `bench/trochoid.py:571`, `:556`, `:475`, `:604`, `:815-822`
**Issue:**
- `_oracle` runs `sys.path.insert(0, str(_TESTS))` on every call; the pooled run makes about
  10,400 calls, so each worker's `sys.path` grows by thousands of identical entries. Harmless
  because the module is cached after the first import, but it is also a `bench` to `tests`
  dependency the import contracts do not describe.
- `_oracle_cases` names a `RootMode` `reason` (`reason.mode`, `reason.reason`).
- `--stride 0` raises a bare `ValueError` from `islice`, and a negative `--serial-slice` silently
  judges all but the last N cases; argparse accepts both.
- `_step_table` prints `step (mm)` and `step / m` from the same variable, correct only because
  `step_row` hard-codes module 1.0.
**Fix:** Guard the insert (`if str(_TESTS) not in sys.path`), rename the variable `rm`, give the
two arguments `type=` validators for positive ints, and either drop the `step / m` column or
divide by the row's module.

### IN-05: The `ROOT_CURVE_POINTS` evidence is not reproducible in the repo and omits the research's own counter-measurement

**File:** `src/spur/calc.py:66-70`, `docs/architecture/gear-maths/implementation.md` (the constants row)
**Issue:** The comment cites 3.58e-5 / 3.89e-5 / 3.98e-5 mm against `cq.Edge.makeSpline`. That came
from a scratch run in `18-RESEARCH.md` (line 357), and `bench/RESULTS.md` states "Nothing here is
a kernel measurement", so the number cannot be re-run from the repository, which is the standard
the coding values set for a comment that carries a measurement. The same research paragraph
records that sampling uniform in tan(beta) is worse than uniform in beta where `w_c > 0`
(6.0e-5 against 1.8e-5 mm at 12 teeth, 14.5 degrees, x 0.9, rho 0.5). The comment mentions only
the `w_c < 0` rows. The research defers the bar to Phase 19, so this is not a wrong value, but the
comment reads as a settled choice for all gears.
**Fix:** Either add a `bench/trochoid.py spline` scenario (kernel imported inside the function, as
`step` does) so the figure is regenerable, or change the comment to "from 18-RESEARCH (scratch run,
w_c < 0 only; the w_c > 0 case is 3x worse and is Phase 19's bar)".

### IN-06: The flake debt's trigger was rolled forward on evidence that cannot discriminate

**File:** `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md:68-82`,
`docs/tech_debt/INDEX.md`
**Issue:** The item is `must`, escalated by the human because a required check fails by itself.
Its trigger ("Phase 18 planning") fired and was re-deferred to "Phase 19 planning" on the grounds
of four green full gates. At the recorded rate of about 1 in 43, four clean runs happen with
probability about 0.91 whether or not the flake is fixed, so they carry almost no information
(the entry itself says "most likely see nothing"). The decision was the human's and is recorded,
so this is a process note only: a `must` item whose trigger is a planning event that has now
passed twice without action behaves like `nice`. The grep claim (no `multiprocessing`,
`ProcessPool` or `subprocess` in `tests/test_trochoid.py` and `tests/trochoid_oracle.py`) checks
out; `bench.trochoid` imports `multiprocessing` but only `run_oracle` uses it, and no gate test
calls that.
**Fix:** Pin the trigger to something that cannot roll: a date, or "the next CI run that fails
with `ReentrantCallError`", and note in the entry that the green-run count is not evidence.

### IN-07: The new `ValueError` is documented on `cutter()` only; `root_mode()` can now raise and does not say so, and `+inf` went from an honest cap to a refusal

**File:** `src/spur/calc.py:1509-1530` (`root_mode` docstring), `src/spur/calc.py:1277-1285`
**Issue:** `root_mode(..., requested="trochoid")` calls `cutter(p, rho)` first, so it now raises
`ValueError` for a bad `rho`, yet its docstring lists six ordered refusals and ends with "decides
them in one fixed order" without saying that a non-finite or negative `rho` is a raise, not a
`RootReason`. Phase 19's caller reads `root_mode`, not `cutter`. The test pins the behaviour
(`root_mode` raises the same message) but the contract text does not. Separately, `rho = +inf`
used to be capped to 0.471 mm with the "reduced to" sentence (measured on `2f6e1e7`), an honest
and warned outcome; it is now refused, which the cutter docstring covers ("not a finite ...
value") but neither the test docstring ("All four now raise", where one of the four was already
handled honestly) nor the 18-06 notes call out as a deliberate narrowing of the earlier fix
suggestion, which said `isfinite` could be dropped. Not a wrong number: a request for an infinite
tip radius is not a legal input and refusing it is defensible.
**Fix:** Add one line to `root_mode`'s docstring: "A `rho` that is not a finite, non-negative
millimetre value raises `ValueError` from `cutter` before any reason is decided; with nothing
requested it is not read." Optionally reword the test docstring to say that `+inf` was capped
before and is refused now on purpose.

### IN-08: The `-0.0` row cannot tell `-0.0` from `0.0`, and the sign is carried into `Cutter`

**File:** `tests/test_trochoid.py:260-262`, `src/spur/calc.py:1292`
**Issue:** The guard `rho < 0` is False for `-0.0`, so `cutter(p, -0.0)` keeps `used = -0.0` and
stores `rho_requested = -0.0`. The test asserts `c.rho == 0.0`, which is True for either sign, so
it proves acceptance but not that a negative-signed zero is harmless downstream. Today it is:
`w_c = used - d`, the land arithmetic and `xi` are the same to float, and the only printed `rho`
is on the cap path, which uses `max(0.0, ...)`. If a later phase serialises `Cutter.rho` or
`rho_requested` (a number someone reads, L08) the output would read `-0.0`.
**Fix:** Either accept it as is, or normalise at the guard (`rho = abs(rho)` after the check, or
`rho + 0.0`, which maps `-0.0` to `0.0`), and assert `math.copysign(1.0, c.rho) == 1.0` in the
test.

---

_Reviewed: 2026-10-08_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
