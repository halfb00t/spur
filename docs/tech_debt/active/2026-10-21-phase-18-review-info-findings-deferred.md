# Phase 18's review leftovers and Phase 10's hard-coded chamfer bound

Severity: nice
Status: active
Date: 2026-10-21
Source: 18-REVIEW IN-03, IN-04, IN-05, IN-08 and 10-REVIEW IN-01, triaged in Phase 28 (D-12, D-18)
Related files:
- bench/trochoid.py:176-224 (`run_epsilon`), :568-575 (`_oracle`), :560 (`reason`), :872 and :879 (the two arguments), :820-847 (`_step_table`)
- src/spur/calc.py:66-70 (`ROOT_CURVE_POINTS`), :1415 (`cutter`'s `rho` guard)
- tests/test_trochoid.py:395-397 (the `-0.0` row)
- bench/tip_chamfer_spike.py:201, 286 (the hard-coded `3.0`)

## Context
Eight Phase 18 info findings and two Phase 10 ones were `open` at the v0.6 start. Phase 28 fixed or closed with a
reason the ones the tree had already overtaken (18 IN-01, IN-02, IN-06, IN-07). These five remain, each re-read against
the tree in Phase 28 and still true. None changes a printed number.

- **18 IN-03.** `bench/trochoid.py` `run_epsilon` prints a recommended epsilon and fails only above
  `EPSILON_CEILING = 1e-3`; it never compares the recommendation with the shipped `calc.TROCHOID_JOIN_EPS` (imported
  at line 54, used elsewhere in the file but not in that verdict). The sweep tally in `tests/test_calc.py` moves if the
  constant moves, so nothing ships wrong; the bench verdict just does not say what its docstring implies. Review fix:
  after computing `eps`, fail when `TROCHOID_JOIN_EPS < eps`.
- **18 IN-04.** Four small bench items: `_oracle` runs `sys.path.insert(0, str(_TESTS))` on every call (about 10,400
  per pooled run); `_oracle_cases` names a `RootMode` `reason` (line 560); `--stride 0` raises a bare `ValueError`
  from `islice` and a negative `--serial-slice` silently judges all but the last N cases (both arguments are
  `type=int`); `_step_table` prints `step (mm)` and `step / m` from one variable, right only because `step_row`
  hard-codes module 1.0. Review fix: guard the insert, rename the variable `rm`, give the two arguments positive-int
  validators, drop the `step / m` column or divide by the row's module.
- **18 IN-05.** The `ROOT_CURVE_POINTS` comment cites 3.58e-5 / 3.89e-5 / 3.98e-5 mm against `cq.Edge.makeSpline`
  from a scratch run in 18-RESEARCH; `bench/RESULTS.md` says nothing there is a kernel measurement, so the figure
  cannot be re-run from the repo, and the comment omits the research's own `w_c > 0` counter-measurement (3x worse).
  Review fix: add a `bench/trochoid.py spline` scenario, or reword the comment to say it is a scratch run for
  `w_c < 0` only.
- **18 IN-08.** `cutter(p, -0.0)` keeps `used = -0.0` and stores `rho_requested = -0.0` (`rho < 0` is False for it);
  the `-0.0` test row asserts `c.rho == 0.0`, true for either sign. Harmless today (`w_c`, the land and `xi` are the
  same to float); it would print `-0.0` if a later phase serialised `Cutter.rho`. Review fix: normalise at the guard
  (`rho + 0.0`) and assert `math.copysign(1.0, c.rho) == 1.0`, or accept it.
- **10 IN-01.** `bench/tip_chamfer_spike.py:201` (`hi = min(3.0, ...)`) and `:286` (`cap = min(..., 3.0)`) repeat the
  `tip_chamfer` field's `le=3` bound by hand, with no test guarding drift. Review fix: read the bound from
  `GearParams.model_fields["tip_chamfer"].metadata`.

## Why it matters
Bench and evidence hygiene. No printed number is wrong (both reviews say so). The risks are a bench verdict that stays
`ok` when the shipped epsilon is too small, an evidence figure nobody can regenerate, a `-0.0` that reaches output if
`Cutter.rho` is ever serialised, and a bench that quietly keeps a stale chamfer bound if the field's `le=3` moves.

## Next step
Two triggers, one per group, so the Phase 10 item is not held back by the trochoid maths:
(a) the four Phase 18 findings (IN-03, IN-04, IN-05, IN-08): revisit at the next phase that changes the trochoid /
hob-root maths in `calc.py` or its tests;
(b) 10 IN-01: revisit at the next edit of `bench/tip_chamfer_spike.py` or of the `tip_chamfer` field's bound.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
