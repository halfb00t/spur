---
phase: 32-the-shaft-solid
plan: 02
subsystem: shaft-maths
tags: [din5480, end-chamfer, floor-rule, warnings, slug, l08, l47]

requires:
  - phase: 32-the-shaft-solid
    provides: "32-01 Decision result A1 B1 C1 D1 and the floor-grid evidence"
provides:
  - "floor_mm, ChamferReading, end_chamfer_reading and the two chamfer sentences in shaft_calc"
  - "ShaftDimensions.end_chamfer_effective, the 13th key, after measure_over_pins"
  - "ROOT_FORM_CONSTRUCTION on every shaft, SHANK_STEP_NO_RELIEF when shank_length > 0"
  - "the end_chamfer and splined_length help (D-04, D-08) and ShaftParams.slug()"
  - "the L47 amendment for the applied end chamfer"
  - "seven guards seen red once (bench/RESULTS.md, Seen red once (Phase 32))"
affects: [32-03, 32-04, 32-05, 33]

tech-stack:
  added: []
  patterns:
    - "a cut size is computed once in derive_shaft from the printed diameters; the solid reads it and never re-derives it"

key-files:
  created:
    - .planning/phases/32-the-shaft-solid/investigation/32-02-overshoot.py
    - .planning/phases/32-the-shaft-solid/investigation/32-02-overshoot.log
    - .planning/phases/32-the-shaft-solid/investigation/32-02-red-round.log
    - .planning/phases/32-the-shaft-solid/investigation/32-02-red-no-epsilon.log
    - .planning/phases/32-the-shaft-solid/investigation/32-02-red-no-tooth-cap.log
    - .planning/phases/32-the-shaft-solid/investigation/32-02-red-no-cap-warning.log
    - .planning/phases/32-the-shaft-solid/investigation/32-02-red-zero-printed.log
    - .planning/phases/32-the-shaft-solid/investigation/32-02-red-key-order.log
    - .planning/phases/32-the-shaft-solid/investigation/32-02-red-shank-sentence.log
  modified:
    - src/spur/shaft_calc.py
    - src/spur/shaft_params.py
    - tests/test_shaft_calc.py
    - tests/test_shaft_params.py
    - docs/architecture/decision_log.md
    - bench/RESULTS.md

key-decisions:
  - "A1 used: floor_mm(v) = floor(v*1000 + 1e-9)/1000 on the request, the tooth height from the printed diameters and splined_length; applied is the minimum of the three"
  - "B1 used: end_chamfer_effective sits after measure_over_pins and before designation, index 10 of 13"
  - "C1 used: ShaftParams().slug() is spur_shaft_w25x1.25x18, numbers only, no fit"
  - "The cap warning fires only where a limit binds at the 0.001 mm resolution (the gear's 10-REVIEW CR-01 rule)"

requirements-completed: []  # REQ-shaft-solid needs the solid (32-03); this plan delivers its number side only

duration: 12 min
completed: 2026-10-27
status: complete
actuals:
  tokens: 49792   # chars/4 over the added lines of f2141af..HEAD; 4840 of that is src, tests, docs and bench, the rest is the seven red logs, the overshoot script and its log
  tasks: 3
  commits: 4
plan_head_before: f2141af1f8cf0945e9aab136f271018cead0d8ab
plan_head_after: 95b1b9a7b74cc4a1c87493e128bfb402fd974114
---

# Phase 32 Plan 02: The applied end chamfer, two sentences, field help and slug Summary

`derive_shaft` now prints `end_chamfer_effective` (the 13th key), the size the solid will cut: the smallest of the request, the tooth height and `splined_length`, each floored to 0.001 mm, capped and warned, never refused; every shaft carries a no-number root-construction sentence and a shank with a step carries the no-relief sentence.

## Values used from 32-01

| Letter | Value used |
|---|---|
| A (A1) | `floor_mm(v) = math.floor(v * 1000 + 1e-9) / 1000` |
| B (B1) | `end_chamfer_effective` after `measure_over_pins`, before `designation` (`13 10`) |
| C (C1) | `ShaftParams().slug()` is `spur_shaft_w25x1.25x18` |

## What shipped

Task commits:

1. Task 1 (tracer): `1923016` feat(32-02): the applied end chamfer, floored and capped, as the 13th dims key (L47 amendment)
2. Task 2: `f826d8c` feat(32-02): the root-construction and shank-step sentences, the solid fields' help, and the shaft slug
3. Task 2 follow-up: `ab415fe` test(32-02): the millimetre floor test names the first decimal that moved
4. Task 3: `95b1b9a` docs(bench): the applied chamfer's guards seen red once (32-02)

Printed values (acceptance run): the default shaft `1.0`; W 10x0.5x18 `0.5`; W 70x3x22 with `splined_length` 2.0006 and `end_chamfer` 5 `2.0`; `end_chamfer` 0.0004 `None`.

### The sentences as shipped

`ROOT_FORM_CONSTRUCTION` (no digit, no `hobbed`):

> The solid's tooth root is a construction, not the cut of a hob or broach: each flank follows the involute down to the root circle, radially below the base circle where that lies above the root, and the teeth are joined by an arc on root_d. Do not take a root fillet's shape or size from the solid.

`SHANK_STEP_NO_RELIEF` (no notch factor):

> The spline steps straight into the shank: the solid has no relief groove (DIN 509) and no hob run-out, and splined_length is a full-form prism.

`chamfer_capped_warning`, with limits `tooth height (tip_d - root_d)/2` and `splined_length` (both, tooth height first, on a tie):

> end_chamfer {requested} mm is capped at {applied} mm, the {limits}: the 45 degree cone cannot cut below the root circle or past the splined section.

`chamfer_below_resolution_warning`:

> end_chamfer {requested} mm is below the 0.001 mm resolution it is cut at and was not cut.

Help texts: `end_chamfer` "A 45 degree cone at the free end, sized at the tip diameter: it starts on the end face at tip_d - 2*end_chamfer and reaches tip_d at end_chamfer from the end. Capped at the tooth height and at the splined length, with a warning. 0 = none."; `splined_length` "Length of the toothed part of the shaft, a full-form prism: the teeth keep their full form up to the shank, with no relief groove or hob run-out."

The default shaft's warnings are now six sentences, in the order of the plan's objective; no Phase 31 sentence moved.

## The two CONTEXT wording corrections

Both are recorded in the L47 amendment (`docs/architecture/decision_log.md`, "Amendment (2026-10-27, Phase 32: the applied end chamfer)").

1. D-05's "a link that sets only `module` still builds" cannot validate: `ShaftParams(module=0.5)` with the default reference diameter 25 and 18 teeth needs a shift of +15.45 and is refused. The 0.5 mm cap is exercised on W 10x0.5x18 (shift +0.45).
2. The printed tooth height equals the module only on typed decimal inputs (13,552 rows, `32-01-floor-grid.log`). For an arbitrary float each diameter is rounded to 0.001 on its own, so the tooth height is within 0.0005 of the module and a multiple of 0.0005.

## Verification

- `make verify`: `======================= 2402 passed in 218.58s (0:03:38) =======================` (2387 at the 32-01 baseline in 251.15 s; 15 new test items). Static steps green, `Contracts: 10 kept, 0 broken.`, `make gear.unchanged` green.
- `git diff --exit-code v0.6 -- src/spur/calc.py src/spur/params.py tests/regression/ .github/workflows/ci.yml` exits 0.
- Every task's acceptance criteria were run and held, including `13 10`, the single `end_chamfer_reading(p, tip_d, root_d)` call, `6 True False True` and `None False`.
- Tracer gate: the Task 1 verify was re-run after its commit (1021 passed) before Task 2 began.

## Seen red once

Seven breaks, each run on `tests/test_shaft_calc.py` with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared before and after, then reverted with `git checkout`; `git status --porcelain -- src tests` was empty after each and after the commit. Rows are in `bench/RESULTS.md` under `### Seen red once (Phase 32)`, logs are `investigation/32-02-red-*.log`.

| Break | Result |
|---|---|
| round | 3 failed, first `assert 2.001 == 2.0` |
| no-epsilon | 1 failed, first `assert ['1.001', '1.003', '1.005'] == []` |
| no-tooth-cap | 1 failed, first `assert 1.0 == 0.5` |
| no-cap-warning | 4 failed, first `assert [] == ['end_chamfer...ned section.']` |
| zero-printed | 1 failed, first `assert 0.0 is None` |
| key-order | 1 failed, first `At index 10 diff: 'designation' != 'end_chamfer_effective'` |
| shank-sentence | 1 failed, the shank-sentence test |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The 32-01 claim "exceeds splined_length only by under 1e-12 mm" is false by 2 percent**
- **Found during:** Task 1, measuring the carried-forward unverified claim before writing it into a comment.
- **Issue:** `floor_mm` can land above its input when the input is within 1e-9 / 1000 mm below a lattice point. Eight fixed offsets below each of 71,286 lattice points (302,586 rows above their input) and a walk of 40 single ulps below each of 38,385 lattice points, all in 1..500 mm, found a maximum excess of 1.0231815394945443e-12 mm at 256.051999999999, not under 1e-12.
- **Fix:** `floor_mm`'s comment, the floor test's docstring and the L47 amendment say "at most 1.03e-12 mm up to 500 mm", cited to the new `32-02-overshoot.log`. The tests assert only what holds: `<= p.splined_length` at the rows 2.0006 and 1.0009, and the typed-decimal grids. No claim of "under 1e-12" is made anywhere.
- **Files modified:** `src/spur/shaft_calc.py`, `tests/test_shaft_calc.py`, `docs/architecture/decision_log.md`; created `32-02-overshoot.py` and `.log` (not in the plan's file list).
- **Verification:** `32-02-overshoot.py` run under `-I`, ruff clean.
- **Commit:** 1923016

**2. [Rule 1 - Bug] The floor test did not name the decimal that moved**
- **Found during:** Task 3, planning R2 (the plan wants the R2 log to name the first decimal that floored below itself).
- **Issue:** The test as first written used `all(...)`, whose failure shows `assert False` and no decimal.
- **Fix:** It collects the offenders and asserts `moved[:3] == []`, so the R2 log reads `['1.001', '1.003', '1.005']`. The same for the four-place check. Committed on its own before the reds, so the Task 3 commit holds no `src` or `tests` change as the plan's verify requires.
- **Files modified:** `tests/test_shaft_calc.py`
- **Commit:** ab415fe

**3. [Rule 3 - Blocking] A literal grep in the acceptance criteria did not match a wrapped string**
- **Found during:** Task 2 acceptance (`grep -c 'full-form prism' src/spur/shaft_params.py` printed 0: the phrase broke across two source lines).
- **Fix:** Rewrapped the help string so the phrase sits on one line; amended the unpushed Task 2 commit (`f826d8c` is the final hash). The test reads the field description, so behavior is unchanged.

**4. [Rule 3 - Blocking] The ruff pre-commit hook lints `.planning/**/investigation/*.py`**
- **Found during:** Task 1 commit. The first overshoot script had `if r > v: worst2 = ...` on one line (E701), so the commit failed.
- **Fix:** Rewrote the script cleanly; the first commit attempt committed nothing and the second succeeded.

**5. TDD commit shape.** Task 2 is `tdd="true"`, but the pre-commit hook runs `make verify.fast`, so a failing RED commit cannot land without `--no-verify`, which is forbidden. RED was run and seen (calc tests: ImportError on collection; params tests: 3 failed, 70 passed) and then GREEN, in one `feat` commit as the plan's action specifies. The plan is `type: execute`, so no `## TDD Gate Compliance` violation applies.

**Total deviations:** 4 auto-fixed (2 bug, 2 blocking) and 1 note. **Impact:** none on the printed numbers; one claim in a 32-01 note corrected before it entered any file.

## Auth gates

None.

## Debt and ideas filed

None filed. Two things worth knowing for later plans, neither a debt item yet:
- Anything under `.planning/**/investigation/*.py` is linted by the commit hook; evidence scripts must be ruff-clean.
- The 1.03e-12 mm overshoot means `end_chamfer_effective` may exceed `splined_length` by that much; 32-03's solid must not assume strict `<=` at the float level (the kernel read a cone 1e-7 mm past the length as clean, `32-windows-axial.log`).

## Known Stubs

None.

## Threat Flags

None. T-32-02 and T-32-03 are mitigated: the floor, the 2.0006 and 1.0009 rows, the typed-decimal grids and the cap and resolution sentences are tested and each seen red.

## Self-Check: PASSED

Commits 1923016, f826d8c, ab415fe and 95b1b9a are ancestors of HEAD; `shaft_calc.py`, `shaft_params.py`, the seven red logs and the overshoot files exist; `git status --porcelain -- src tests` is empty.
