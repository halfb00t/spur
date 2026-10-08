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
  warning: 2
  info: 6
  total: 8
status: issues_found
---

# Phase 18: Code Review Report

**Reviewed:** 2026-10-08
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Reviewed the trochoid cutter / generator / predicate in `src/spur/calc.py` (about lines 60-140
and 1230-1576), the oracle and the proofs in `tests/`, the bench driver and its recorded results,
and the doc and debt-ledger edits.

Checks I ran, so the verdict rests on commands and not on reading:

- `make verify` on the current tree: ruff, mypy `--strict`, import contracts and pytest all pass,
  `1017 passed in 92.62s`, coverage 97.68 % (floor 96 %).
- A 40,000-case fuzz of `bench.trochoid.check_case` over random allowed gears off the committed
  grids (odd modules such as 3.47, pressure angles to 0.1 degree, shifts to 0.01, backlash to
  0.01, tip radius 0 to 3 mm): zero exceptions, zero checker problems. Outcomes: 29,158 nothing
  radial, 7,180 not a gear, 3,607 curves, 52 tip land gone, 3 severed.
- Mutation probes on a scratch copy of `calc.py` (the working tree was not touched). Killed:
  dropping the centreline arm, the tip-circle arm, the waist refinement, the `max(0, ...)` land
  floor, floor-to-round on the cap, the cap warning, 60 to 20 bisections, 60 to 5 golden steps.
  Surviving: `<=` to `<` on `waist[1]`, `>=` to `>` on the tangent test and `<=` to `<` on
  `rb <= rf`. All three are equality boundaries that cannot be built from field values, so
  they are not findings. One non-equivalent mutation survived: WR-01.
- `derive()` timed on the pre-phase and current `calc.py`, alternating, three pairs: 19/15/14.4 usec
  old against 15/14.7/17.8 usec new. No regression separable from load, so the docstring's
  "moves with the host" claim holds.
- The recorded tallies in `bench/RESULTS.md` cross-add (31,446 = 12,892 + 18,554;
  10,326 + 8,228 = 18,554; 10,399 = 10,326 + 73; the by-module rows sum to the grid sizes).
  F9's "undercut implies rb > rf" also follows by hand: xi < 0 gives d > (zm/2)sin^2(alpha), and
  sin^2 = (1 - cos)(1 + cos) >= (1 - cos), which is rb > rf.

No critical issues. The maths is correct on every case I could construct. Both warnings are about
proof strength and an unguarded public input, not about a wrong number reaching a user today
(nothing in `model.py`, `app.py` or `cli.py` reads any of this yet; `profile()` is bit-identical
after the `_dedendum` / `_pitch_thickness` extraction).

## Warnings

### WR-01: One of the four `curve invalid` guard arms is untested, and the test claims all of them

**File:** `src/spur/calc.py:1462-1469`, `tests/test_trochoid.py:907`
**Issue:** `_root_curve` documents "one guard for four structural failures". The fourth arm
(`join == "crossing" and any(radius >= pr.rb and half >= pr.half_angle(radius) ...)`, a point
before the junction that is not inside the involute) is never exercised. I replaced the whole
arm with `or False` in a scratch copy and `tests/test_trochoid.py`, `tests/test_calc.py` and
`tests/test_bench.py` stayed green (503 passed). Line coverage cannot see it because the four
arms are a single boolean expression. `test_every_structural_failure_is_refused_as_curve_invalid`
(name and docstring) covers the tip-circle arm, the falling-radius arm and, in
`test_a_curve_that_cannot_be_trusted_is_refused_with_a_reason_and_no_points`, the centreline arm,
but not this one. The `thick` fixture in the latter ends in `bracket degenerate` and never
reaches it. The only other cover is `bench.trochoid.check_curve`'s own `outside` check, which
runs in the sweep test and can only report, not prove the generator refuses. The arm guards
the case the bisection finds a later root, which is exactly the "healed curve" L08 forbids, so it
should be pinned like the others.
**Fix:** Add a fourth row built the way the monkeypatch row is: a crossing cutter (the tracer
gear, 10 teeth, tip radius 0.38) with `_trochoid_point` patched so one early point has
`half = pr.half_angle(radius) + 1e-3` at `radius > pr.rb`, then assert `_root_curve(c) ==
"curve invalid"`. Rename the test to what it covers, or keep the name once all four arms are in.

```python
def test_a_crossing_curve_with_an_early_point_outside_the_involute_is_refused(monkeypatch):
    c = cutter(tracer_gear, 0.38)
    real = calc._trochoid_point
    def bent(cc, beta):
        r, h = real(cc, beta)
        return (r, cc.pr.half_angle(r) + 1e-3) if cc.pr.rb < r and beta < 0.5 * math.pi / 2 else (r, h)
    monkeypatch.setattr("spur.calc._trochoid_point", bent)
    assert _root_curve(c) == "curve invalid"
```

### WR-02: `cutter()` and `root_mode()` take an unvalidated tip radius; NaN is silently capped, negative gets the wrong reason

**File:** `src/spur/calc.py:1266-1296`, `src/spur/calc.py:1560-1576`
**Issue:** `rho` is not a `GearParams` field in this phase (D-07), so the "validate once at the
boundary" rule has nothing to rely on, and `cutter` does not check it. Measured on the 12-tooth,
module 1, 20 degree gear:

- `rho = nan`: `rho <= rho_max` is False, so the cap is used; `c.rho < c.rho_requested` is
  `0.471 < nan`, False. Result: `mode == "trochoid"`, `reason is None`, `root_warnings == ()`. A
  request that cannot be honoured is trimmed to a different part with no sentence, the exact
  "silent change" L03 and the project's second standing rule forbid.
- `rho = -0.5`: used as is (`w_c` shifts, the curve is built for a cutter of negative radius), then
  refused as `curve invalid` with the sentence "loops, leaves the tooth space or runs past its
  junction". The cause is the input, and the sentence blames the geometry.

Neither is reachable from the form today (the field is 0 to 3 and pydantic rejects NaN against
bounds), so this is a robustness gap in a public function, not a live wrong number. It becomes
live the first time Phase 19 or a test feeds `rho` from anything other than that field.
**Fix:** Reject at `cutter()`, the one place the tip radius enters:

```python
if not (rho >= 0 and math.isfinite(rho)):
    raise ValueError(f"tip radius must be a finite number of mm >= 0, got {rho!r}")
```

`inf` is currently handled (it caps with a sentence), so `math.isfinite` can be dropped if that is
wanted. Add one test row each for NaN and -0.5.

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

---

_Reviewed: 2026-10-08_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
