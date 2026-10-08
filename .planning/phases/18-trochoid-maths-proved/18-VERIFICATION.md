---
phase: 18-trochoid-maths-proved
verified: 2026-10-08T06:00:00Z
status: passed
score: 6/6 must-haves verified
covered_files:
  - ".planning/phases/18-trochoid-maths-proved/18-01-PLAN.md"
  - ".planning/phases/18-trochoid-maths-proved/18-01-SUMMARY.md"
  - ".planning/phases/18-trochoid-maths-proved/18-02-PLAN.md"
  - ".planning/phases/18-trochoid-maths-proved/18-02-SUMMARY.md"
  - ".planning/phases/18-trochoid-maths-proved/18-03-PLAN.md"
  - ".planning/phases/18-trochoid-maths-proved/18-03-SUMMARY.md"
  - ".planning/phases/18-trochoid-maths-proved/18-04-PLAN.md"
  - ".planning/phases/18-trochoid-maths-proved/18-04-SUMMARY.md"
  - ".planning/phases/18-trochoid-maths-proved/18-05-PLAN.md"
  - ".planning/phases/18-trochoid-maths-proved/18-05-SUMMARY.md"
  - ".planning/phases/18-trochoid-maths-proved/18-06-PLAN.md"
  - ".planning/phases/18-trochoid-maths-proved/18-06-SUMMARY.md"
  - "bench/RESULTS.md"
  - "bench/trochoid.py"
  - "src/spur/calc.py"
  - "tests/test_bench.py"
  - "tests/test_calc.py"
  - "tests/test_trochoid.py"
  - "tests/trochoid_oracle.py"
covered_digest: "v3:sha256:6a5d3c1e6dda4bb007c95dfaf6aa4d578ebe819ef8a5c36df1403355d786d0ab"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 5/6
  gaps_closed:
    - "Truth 6: the fourth `curve invalid` guard arm in `_root_curve` had no test that made it fire (8e96c2d)"
    - "WR-02 (anti-pattern, not a truth): `cutter()` took an unvalidated tip radius (085aee7)"
  gaps_remaining: []
  regressions: []
---

# Phase 18: Trochoid Maths, Proved - Verification Report

**Phase Goal:** The trochoid a hob cuts below the base circle can be computed, or honestly refused, for every gear the project allows, and is proven against an independent oracle, all as pure `calc.py` maths: no kernel, no `GearParams` field, nothing a user can see changes.
**Verified:** 2026-10-08
**Status:** passed
**Re-verification:** Yes, after gap plan 18-06. The previous report (`human_needed`, 5/6) had one behavior-unverified item, the fourth guard arm. I re-checked it against the code and by my own mutation run, not from the SUMMARY.

The goal is achieved. The one open item is closed: the fourth `curve invalid` arm now has a test that makes it fire and that goes red when the arm is removed. I reproduced that red result myself. The rest of the evidence below is quick regression checks of what passed last time, plus a fresh full gate.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: the rack cutter is defined once (dedendum 1.25 m, rho, backlash as thickening, shift); junction equals `Profile.half_angle`; rho above the geometric maximum is capped (floored, 3 dp) with a warning; rho = 0 legal; no curve above the tip-land limit; cap and limit pinned one step either side | VERIFIED (regression) | `cutter()` calc.py:1266 still reads `_dedendum` and `_pitch_thickness`, the helpers `profile()` reads. The gate tests for junction, cap and tip-land limit passed in my fresh `make verify`. I ran `cutter(p, 3.0)` on the 12-tooth, module 1, 20 degree gear: rho returns 0.543 (capped, not 3.0). Default `root_mode(GearParams(), ...)` returns `RootMode('radial', 'not requested', None)`. The new `ValueError` guard did not disturb `0.0`: `cutter(p, 0.0).rho == 0.0`. |
| 2 | SC2: `trochoid_root` returns an immutable `RootCurve` or `None`; sweep over the allowed space shows zero bracket failures and monotone radius; `z_min` double root has a tested rule; `derive()` cost re-measured and docstring corrected | VERIFIED (regression) | `_root_curve` calc.py:1450-1488 unchanged in structure; `RootCurve` is a frozen dataclass; `trochoid_root` returns `None` for any non-curve (calc.py:1491-1498). The sweep gate test (`test_the_trochoid_sweep_over_the_allowed_box`) and the immutability/ordering tests are part of the `1022 passed` run. The measured sweep is in bench/RESULTS.md "Trochoid maths (Phase 18)". |
| 3 | SC3: proof lives in `tests/`, shares no code with the implementation: T1 closed form, T2 swept-cutter oracle, T3 freecad.gears one-off at rho = 0 (never imported), bars with headroom, tripwire seen red | VERIFIED (regression) | `tests/trochoid_oracle.py` has one import, `import math` (grep `^import\|^from` shows only that line plus `from __future__`). `git grep` finds no `import pygears` / `import freecad`. T1-T4 and the tripwire tests are in the passing run. |
| 4 | SC4: `root_mode(p, pr)` is the single predicate; the three "undercuts" never mixed; tested one tooth step and one field step either side; root-shape step measured and recorded | VERIFIED (regression) | `root_mode` calc.py:1509; the straddle, onset-flip and first-reason tests are in the passing run; the step is recorded in bench/RESULTS.md. |
| 5 | SC5: nothing a user can see moved: fixture unchanged; only `calc.py` under `src/spur/`; no numpy/scipy; `requirements.txt` still 31 pins | VERIFIED | Run against the roadmap base `807fd2d`: `git diff --quiet 807fd2d HEAD -- tests/regression/pre_v0_2.json` clean (fixture identical); `git diff --name-only 807fd2d HEAD -- src` prints exactly `src/spur/calc.py`; `grep -rnE 'numpy\|scipy' src/spur` prints nothing (rc 1); `requirements.txt` has 31 `==` pins. |
| 6 | Each structural failure of a candidate curve (loop, above tip circle, past centreline, a point not inside the involute before a crossing junction) is refused as `curve invalid`, never clipped or healed | VERIFIED (was PRESENT_BEHAVIOR_UNVERIFIED) | The fourth arm is calc.py:1478-1480 (`join == "crossing" and any(radius >= pr.rb and half >= pr.half_angle(radius) for ... in points[:-1])`). `test_a_crossing_curve_with_an_early_point_outside_the_involute_is_refused` (tests/test_trochoid.py:973) wraps the real `_junction` (asserting it still finds the junction read beforehand), then bends exactly one early sample to `rb + 0.01` with half-angle `half_angle + 1e-3`; asserts `_root_curve == "curve invalid"`, `trochoid_root is None`, `root_mode` reads `("radial", "curve invalid")` with the captured sentence. I read the test and its premise assertion (`honest.points[-2][0] < c.pr.rb`, so the bend is necessary, not decorative). **My own mutation run:** I copied `src`, `tests`, `bench`, the fixture and `pyproject.toml` to a scratch directory, replaced the arm by `or False`, confirmed with `PYTHONPATH=<scratch>/src` that `spur.calc.__file__` was the scratch file, and ran `tests/test_trochoid.py tests/test_calc.py tests/test_bench.py`: `1 failed, 507 passed`, the single failure being the new test. A second mutant (`any` to `all`) also turns only that test red (`1 failed, 72 passed` in `test_trochoid.py`). The working tree was not touched. |

**Score:** 6/6 truths verified (0 present, behavior-unverified)

Reliance check (Step 5c): the new test's fixture does establish its own precondition (a bent sample), but that is the point of a guard-arm test and the production path (`_trochoid_point`) is the real function everywhere else. No `coincidental-reliance` flag.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/calc.py` | `Cutter`, `cutter` (with rho guard), `RootCurve`, `trochoid_root`, `RootMode`, `root_mode`, `root_warnings`, constants | VERIFIED | `math.isfinite(rho)` guard at line 1291; stdlib `math` only; no consumer in `src/` yet (by design, Phase 19). |
| `tests/test_trochoid.py` | Cap, tip-land, junction, predicate, T1-T4, fourth-arm test, rho-validation test | VERIFIED | Both gap-plan tests present and passing. |
| `tests/trochoid_oracle.py` | Independent swept-cutter oracle | VERIFIED | imports `math` only. |
| `bench/trochoid.py` + `bench/RESULTS.md` | Reproducible measurements | VERIFIED | Section "Trochoid maths (Phase 18)" present at RESULTS.md:3035. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `profile()` / `cutter()` | `_dedendum`, `_pitch_thickness` | shared helpers | WIRED | One definition of `rf`. |
| `root_mode` | `_root_curve` / `cutter` | direct call | WIRED | A NaN rho now propagates the `ValueError` through `root_mode` (I ran it). |
| `root_warnings` | `_ROOT_SENTENCES` | lookup | WIRED | The new test captures the `curve invalid` sentence from it. |
| `root_mode` / `trochoid_root` | `_outline`, `derive`, `model.py` | none | NOT WIRED (intended) | Phase 19 owns consumers; SC5 requires this phase to leave them unwired. |

### Data-Flow Trace (Level 4)

Not applicable: pure maths, no rendered dynamic data.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Bad tip radius is refused | `.venv/bin/python -I`, `cutter(p, x)` for nan, inf, -inf, -0.1 | each raises `ValueError: tip radius must be a finite, non-negative millimetre value, got ...` | PASS |
| `root_mode` never answers `trochoid` for NaN | same, `root_mode(p, profile(p), requested="trochoid", rho=nan)` | raises | PASS |
| Sharp cutter legal | `cutter(p, 0.0).rho`, `cutter(p, -0.0).rho` | `0.0`, `-0.0` (sign carried; IN-08, info) | PASS |
| Cap | `cutter(p, 3.0).rho` | 0.543 | PASS |
| Default call silent | `root_mode(GearParams(), profile(GearParams()))` | `RootMode(mode='radial', reason='not requested', cutter=None)` | PASS |
| Guard arm 4 exercised (`or False` mutant) | `PYTHONPATH=<scratch>/src pytest tests/test_trochoid.py tests/test_calc.py tests/test_bench.py -n0 --no-cov` | `1 failed, 507 passed`; failing: the new test only | PASS (the test notices removal) |
| Guard arm 4, `all` mutant | same, `test_trochoid.py` | `1 failed, 72 passed` | PASS |
| Whole gate | `make verify` | ruff `All checks passed!`; mypy `--strict` `Success: no issues found in 42 source files`; import contracts run; `1022 passed in 88.63s`; `Required test coverage of 96.0% reached. Total coverage: 97.68%`; rc 0 | PASS |

### Probe Execution

No `probe-*.sh` is declared by any plan or present under `scripts/`. Step 7c: SKIPPED (none).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-cutter-defined-once | 18-01, 18-06 | One pure function defines the rack; rho capped from the real cutter with warning; no curve above tip-land limit | SATISFIED | Truth 1; plus `cutter()` now refuses a non-finite or negative rho |
| REQ-trochoid-root-generated | 18-01, 18-03, 18-05, 18-06 | Immutable `RootCurve` or `None`; sweep; `z_min` rule; every structural failure refused | SATISFIED | Truths 2 and 6 |
| REQ-root-mode-single-predicate | 18-02, 18-05 | One predicate, three undercuts never mixed, step measured | SATISFIED | Truth 4. Consumers reading it are Phase 19's (REQUIREMENTS.md line 276). |
| REQ-trochoid-proved-independently | 18-01, 18-02, 18-04 | T1/T2/T3 (+T4) independent, bars with headroom, tripwire | SATISFIED | Truth 3 |

All four IDs declared across the six PLAN frontmatters (18-01: 3, 18-02: 2, 18-03: 1, 18-04: 1, 18-05: 2, 18-06: 2) appear in REQUIREMENTS.md (lines 96, 108, 120, 129; traceability rows 256-259), marked Complete, and are the four the phase was given. No orphaned requirement.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/spur/calc.py` | n/a | Previous WR-01 (untested arm) and WR-02 (unvalidated rho) | Closed | `8e96c2d`, `085aee7`; ledger rows read `fixed`; WR-02 reproduced as a `ValueError` above |
| `src/spur/calc.py` | ~1554 | IN-01 cap sentence says "the largest" but prints a floored value | Info | Within 0.001 mm; one float used and printed |
| `src/spur/calc.py` | 1291 | IN-07 `ValueError` documented on `cutter()` only; `root_mode()` can now raise; `+inf` went from capped to refused | Info | No reachable caller; open in the ledger |
| `tests/test_trochoid.py` | rho sharp rows | IN-08 `-0.0` row cannot tell `-0.0` from `0.0`; sign carried into `Cutter` | Info | Nothing prints a zero radius |
| `bench/trochoid.py` | various | IN-02 to IN-06 bench/evidence hygiene and the flake-debt trigger | Info | No effect on any shipped number |

I ran the debt-marker scan (`TBD|FIXME|XXX|TODO|HACK`) file by file on `bench/RESULTS.md`, `bench/trochoid.py`, `src/spur/calc.py`, `tests/test_bench.py`, `tests/test_calc.py`, `tests/test_trochoid.py`, `tests/trochoid_oracle.py`: no match. `make verify`'s unfinished-work scan also passed. 18-REVIEW.md (incremental): 0 critical, 0 warnings, 8 info; 18-REVIEW-DISPOSITION.md: WR-01/WR-02 `fixed` with shas, IN-01..IN-08 `open` (info, none blocking). 18-SECURITY.md `threats_open: 0` with T-18-17 and T-18-18 closed. 18-UAT.md test 1 `passed`, `status: complete`.

### Human Verification Required

None. The single item from the previous report (the untested guard arm) is closed with a firing test and a reproduced red mutant.

### Gaps Summary

No gaps. The cutter, the generator, the single predicate and the independent oracle exist, are wired among themselves, and pass `make verify` (`1022 passed`, coverage 97.68 %). Containment (SC5) holds against the roadmap base: fixture byte-identical, only `calc.py` changed under `src/`, no numpy/scipy, 31 pins.

Recorded caveats carried forward, none a blocker and each accepted in the phase's own records: T4's 1.39x headroom (rounded reference, D-15); the unreconciled rho 0 crossover figure (bench/RESULTS.md open note); the resource-tracker flake debt re-deferred to Phase 19 planning (IN-06, a `must` item whose trigger has rolled once). Phase 19 must validate `rho` once at its `GearParams` field; the `ValueError` in `cutter()` is the interim guard.

---

_Verified: 2026-10-08_
_Verifier: Claude (gsd-verifier)_
