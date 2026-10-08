---
phase: 18-trochoid-maths-proved
verified: 2026-10-08T05:00:00Z
status: human_needed
score: 5/6 must-haves verified
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
  - "bench/RESULTS.md"
  - "bench/trochoid.py"
  - "src/spur/calc.py"
  - "tests/test_bench.py"
  - "tests/test_calc.py"
  - "tests/test_trochoid.py"
  - "tests/trochoid_oracle.py"
covered_digest: "v3:sha256:7c15cf0d22f790d1214c4260f0e19cda72fe5545c9fc7e33f1d3beb8bb93e3e2"
behavior_unverified: 1
overrides_applied: 0
behavior_unverified_items:
  - truth: "Every structural failure of a candidate curve (falling radius, above the tip circle, past the space centreline, a point not inside the involute before a crossing junction) is refused as `curve invalid`, never clipped or healed"
    test: "Patch `spur.calc._trochoid_point` on the tracer gear (10 teeth, module 1, 20 degrees, rho 0.38) so one early point past rb has half-angle = pr.half_angle(radius) + 1e-3, then call `_root_curve(c)`"
    expected: "Returns `\"curve invalid\"`. Today the fourth arm of the guard (`join == \"crossing\" and any(radius >= pr.rb and half >= pr.half_angle(radius) ...)`, calc.py ~1465-1468) can be replaced by `False` and all 473 tests in test_trochoid.py + test_calc.py + test_bench.py still pass"
    why_human: "The arm is present and wired, and the whole-box sweep never produces such a curve, but no test makes the generator refuse one. `test_every_structural_failure_is_refused_as_curve_invalid` is named for four arms and covers three. A human decides: add the one test (cheap, recommended) or accept the arm as untested defensive code. Mutation reproduced by this verifier, not taken from the review (18-REVIEW WR-01)."
---

# Phase 18: Trochoid Maths, Proved - Verification Report

**Phase Goal:** The trochoid a hob cuts below the base circle can be computed, or honestly refused, for every gear the project allows, and is proven against an independent oracle, all as pure `calc.py` maths: no kernel, no `GearParams` field, nothing a user can see changes.
**Verified:** 2026-10-08
**Status:** human_needed
**Re-verification:** No, initial verification

The goal is achieved in the code. Every roadmap success criterion is backed by code I read and commands I ran, not by SUMMARY claims. One sub-truth (a guard arm of the generator) is present and wired but no test makes it fire, so it routes to the human rather than counting as verified.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: the rack cutter is defined once (dedendum 1.25 m, rho, backlash as thickening, shift); its junction equals `Profile.half_angle` at backlash 0 and 0.10; rho above the geometric maximum is capped (floored to 3 dp) with a warning; rho = 0 legal; no curve above the tip-land limit; cap and limit pinned one step either side | VERIFIED | `cutter()` calc.py:1266 reads `_dedendum` and `_pitch_thickness`, the same helpers `profile()` now reads (so `rf` has one definition). I ran it: 19 teeth, m 1.75, 25 deg, rho 0.5, junction gap to `Profile.half_angle` is 1.39e-17 rad at backlash 0 and at 0.10 (bar 1e-12 in `test_trochoid.py`, headroom 2.4e4). 12 teeth, m 1, 20 deg, rho 3.0 returns rho 0.471 and the sentence "Cutter tip radius reduced to 0.471 mm". Tip-land limit: 32.0 deg trochoid / 32.5 deg `tip land gone`; 33.0 / 33.5 at m 1.75, backlash 0.10, x -0.4. Cap is read from the real cutter (`rho_max = a0 / (1/cos a - tan a)`, backlash in `a0`), not a constant. 0.318 m vs 0.363 m reconciled as one formula at two backlashes by the phase's first test and recorded in bench/RESULTS.md. |
| 2 | SC2: `trochoid_root` returns an immutable `RootCurve` or `None`; sweep over the allowed space (floor 7,296) shows zero bracket failures and monotone radius; `z_min` double root has a tested rule; `derive()` cost re-measured with load and the stale docstring corrected | VERIFIED | `RootCurve` is `frozen=True` with tuple-of-tuples points (I confirmed `FrozenInstanceError`; 16 points, first radius equals `pr.rf` exactly, radius strictly rising). Sweep recorded in bench/RESULTS.md: 31,446 cases, 18,554 gears, 10,326 curves, 0 `bracket degenerate`, 0 `curve invalid`; the same tally is a gate test (`test_the_trochoid_sweep_over_the_allowed_box`) and passed in my `make verify`. The double root is a tangent join by explicit rule (`TROCHOID_JOIN_EPS` 1e-4 of rb, measured by 400-gear scan) with one-step-either-side tests. `derive()` docstring now reads 14.7 usec at load 14.4, dated, and says it moves with the host. |
| 3 | SC3: proof lives in `tests/`, shares no code with the implementation: T1 closed-form onset, T2 swept-cutter oracle, T3 freecad.gears one-off at rho = 0 (source, commit, licence recorded, never imported), bars from two recorded numbers with headroom, tripwire seen red | VERIFIED | `tests/trochoid_oracle.py` imports only `math` (read in full): it rebuilds the rack from textbook definitions with neighbouring teeth over +-3 roll spans. T1 `test_t1_the_closed_form_onset_pins_when_the_root_is_a_crossing` types its own xi and onset over 4,200 combinations. T2 gate rows worst 9.8e-15 mm against `ORACLE_BAR_MM` 1e-9; whole 10,399-case product 0 beyond bar, worst 2.99e-12. Tripwire (rho + 1e-6 mm) reads 2.2e-7 mm, 220x the bar, and is a test. T3: 60 literals with commit `4cc4b1a2...`, GPL-3.0, date; no tracked file names `pygears`/`freecad`. T4 (KISSsoft/Zhang) added: headroom 1.39 by construction (reference rounded to 4 decimals), human-accepted at D-15, tripwire 15.6x. No other bar is under 10x (smallest 72). |
| 4 | SC4: `root_mode(p, pr)` is the single predicate; the three "undercuts" never mixed; tested one tooth step and one field step either side; root-shape step at the threshold measured and recorded; contradicting figure would reopen the choice | VERIFIED | `root_mode` calc.py ~1560 owns all six reasons in a fixed order (`not requested`, `nothing radial to replace` on `rb <= rf`, `tip land gone`, `bracket degenerate`, `curve invalid`, `tooth severed`), sentences from `root_warnings`. Default call returns `RootMode('radial','not requested',None)` (I ran it). Tests: `test_the_fixture_straddles_the_three_undercuts_without_mixing_them`, `test_the_undercut_onset_flips_one_field_step_either_side_of_a_tuned_shift`, `test_a_gear_failing_two_tests_reports_the_first`. Step measured on the project's own generator: 0.1463 / 0.1449 mm at 17 / 18 teeth, rho 0.38 (premise line 0.105-0.175 mm committed first in `8badc55`), recorded in bench/RESULTS.md "Root-shape step", human reading `d05-hold`. The one unreconciled figure (rho 0 crossover, +0.1403 vs the prototype's -0.1885) is recorded as an open ASSUMPTION note and does not touch the premise rule. |
| 5 | SC5: nothing a user can see moved: fixture unchanged; only `calc.py` under `src/spur/`; no numpy/scipy; `requirements.txt` still 31 pins | VERIFIED | `git diff --exit-code 807fd2d..HEAD -- tests/regression/pre_v0_2.json` clean. `git diff --stat 807fd2d..HEAD -- src/` names only `src/spur/calc.py`. `grep -rnE 'numpy\|scipy' src/spur` prints nothing (rc 1). `requirements.txt`: 31 pins, no diff. The only change to existing code is the `_dedendum` / `_pitch_thickness` extraction in `profile()`; the 44-record fixture replays unchanged inside my `make verify`. |
| 6 | Each structural failure of a candidate curve (loop, above tip circle, past centreline, a point not inside the involute before a crossing junction) is refused as `curve invalid`, never clipped or healed | PRESENT_BEHAVIOR_UNVERIFIED | Three of four arms are exercised by tests. The fourth (calc.py ~1465-1468) is wired but untested: I copied `src/` to the scratchpad, replaced it with `or False` and ran `tests/test_trochoid.py tests/test_calc.py tests/test_bench.py` against the mutant (confirmed the mutant file was the one imported): 473 passed. See `behavior_unverified_items`. |

**Score:** 5/6 truths verified (1 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/calc.py` | `Cutter`, `cutter`, `undercut_teeth`, `undercut_shift`, `RootCurve`, `trochoid_root`, `RootMode`, `root_mode`, `root_warnings`, constants | VERIFIED | +391 lines, all present, substantive, imported by tests; stdlib `math` only. Nothing under `src/` consumes them yet (by design, Phase 19). |
| `tests/trochoid_oracle.py` | Independent swept-cutter oracle | VERIFIED | 111 lines, imports `math` only, not collected, used by `test_trochoid.py` and `bench/trochoid.py`. |
| `tests/test_trochoid.py` | Cap, tip-land, junction, predicate, T1-T4 proofs | VERIFIED | 1,392 lines, all pass in `make verify`. |
| `bench/trochoid.py` + `bench/RESULTS.md` "Trochoid maths (Phase 18)" | Reproducible measurements | VERIFIED | Sections for cap, epsilon, sweep, oracle bars, T3/T4, root-shape step, per-call cost, each with host load. |
| `docs/architecture/gear-maths/implementation.md` | Layout rows for the new pieces | VERIFIED | Rows for `Cutter`, `root_mode`, `RootCurve`, constants, `_ROOT_SENTENCES` present. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `profile()` | `_dedendum` / `_pitch_thickness` | shared helpers | WIRED | `rf` and the half tooth-thickness angle have one definition read by `cutter()` too. |
| `root_mode` | `_root_curve` / `cutter` | direct call after closed-form `rb <= rf` | WIRED | |
| `root_warnings` | `_ROOT_SENTENCES` | lookup | WIRED | Tests capture sentences from it (L33 pattern). |
| `trochoid_oracle.clearance` | `tests/test_trochoid.py`, `bench/trochoid.py` | import | WIRED | Oracle imports nothing from `spur`. |
| `root_mode` / `trochoid_root` | `_outline`, `derive`, `model.py` | none | NOT WIRED (intended) | Phase 19 owns the consumers; ROADMAP "Boundary with Phase 19" and SC5 require this phase to leave them unwired. |

### Data-Flow Trace (Level 4)

Not applicable: pure maths, no rendered dynamic data. Radius and half-angle flow from `cutter()` through `_trochoid_point` into `RootCurve`, and the first point equals `pr.rf` bit for bit (checked).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Junction equals `half_angle` at backlash 0 / 0.10 | scratch script via `.venv/bin/python -I` | 1.39e-17 rad both | PASS |
| Cap floored and warned | same, `rho=3.0` on 12-tooth gear | rho 0.471, sentence names 0.471 | PASS |
| Tip-land limit one step either side | same | 32.0 trochoid / 32.5 refused; 33.0 / 33.5 | PASS |
| Default call is silent radial | `root_mode(GearParams(), profile(p))` | `radial / not requested` | PASS |
| Curve immutable, radius rising, first point `rf` | same | frozen, True, True, 16 points | PASS |
| Whole gate | `make verify` | ruff clean, mypy --strict clean, import contracts kept, `1017 passed in 62.90s`, coverage 97.68 % (floor 96) | PASS |
| Guard arm 4 is exercised | mutant `or False`, 473 tests | all pass | FAIL (see truth 6) |

### Probe Execution

No `probe-*.sh` is declared by any plan or present under `scripts/`. Step 7c: SKIPPED (none).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-cutter-defined-once | 18-01 | One pure function defines the rack; rho capped from the real cutter with warning; no curve above the tip-land limit | SATISFIED | Truth 1 |
| REQ-trochoid-root-generated | 18-01, 18-03, 18-05 | Immutable `RootCurve` or `None`; bracket after sign test; `z_min` rule; sweep; `derive()` cost corrected | SATISFIED | Truth 2; the one untested guard arm is truth 6, a proof-strength gap rather than a missing capability |
| REQ-root-mode-single-predicate | 18-02, 18-05 | One predicate, three undercuts never mixed, step measured and shown | SATISFIED | Truth 4. The consumers (`_outline`, `root_fillet`, ...) reading it is Phase 19's, per REQUIREMENTS.md line 276. |
| REQ-trochoid-proved-independently | 18-01, 18-02, 18-04 | T1/T2/T3 (+T4) independent of the implementation, bars with headroom, tripwire | SATISFIED | Truth 3 |

All four IDs declared across the five PLAN frontmatters appear in REQUIREMENTS.md, are marked Complete, and are the four the ROADMAP lists for Phase 18. No orphaned requirement: REQ-undercut-warning-restated is mapped to Phase 19 (Pending); Phase 18 only supplies `undercut_teeth` / `undercut_shift`, as the roadmap's boundary note says.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/spur/calc.py` | ~1465 | Guard arm with no test that makes it fire (WR-01) | Warning | Truth 6; the L08 "healed curve" case is the one it guards |
| `src/spur/calc.py` | 1266-1296 | `cutter()` takes an unvalidated tip radius (WR-02) | Warning | Reproduced: `rho=nan` returns `mode=trochoid`, `reason=None`, `root_warnings == ()`, rho trimmed to 0.471 with no sentence; `rho=-0.5` is refused as `curve invalid` with a sentence blaming the geometry. Not reachable today (no field, form bounded 0-3, nothing in `src/` calls it); becomes a silent part change under the project's second standing rule the first time Phase 19 feeds `rho` from anything else. Fix is a two-line check in `cutter()`. |
| `src/spur/calc.py` | 1554 | Cap sentence says "the largest" but prints a floored value (IN-01) | Info | Within 0.001 mm; printed and used number are one float. |
| `bench/trochoid.py` | various | IN-03, IN-04 bench hygiene; IN-05 `ROOT_CURVE_POINTS` evidence not reproducible in repo; IN-02 `trochoid_root` and `root_mode` can disagree on `rb <= rf` | Info | No effect on any shipped number. |

No `TBD`, `FIXME`, `XXX`, `TODO` or `HACK` in any file the phase modified. All 8 review findings sit at `open` in 18-REVIEW-DISPOSITION.md (0 critical, 2 warnings, 6 info); I re-derived WR-01 and WR-02 myself and both reproduce as described.

### Human Verification Required

#### 1. The untested `curve invalid` guard arm

**Test:** Decide whether to add the one test described in `behavior_unverified_items` (patch `_trochoid_point` so an early point on the tracer gear lies outside the involute, assert `_root_curve(c) == "curve invalid"`) before Phase 19 consumes the predicate.
**Expected:** `_root_curve` returns `"curve invalid"`; the arm then dies under the `or False` mutation.
**Why human:** Whether defensive code the allowed box never reaches needs its own proof is a quality-bar call. Recommendation: add it, since this arm is the only thing stopping a later-root bisection result from shipping as a healed curve.

### Gaps Summary

No gaps block the phase goal. The cutter, the generator, the single predicate and the independent oracle all exist, are wired among themselves, and pass `make verify` (`1017 passed`, coverage 97.68 %). The SC5 containment holds: fixture byte-identical, only `calc.py` touched, no numpy/scipy, 31 pins.

Open items for the human, none a blocker:

1. Truth 6 (WR-01): one guard arm has no firing test. Needs a decision, which is why the status is `human_needed` and not `passed`.
2. WR-02: `cutter()` does not validate `rho`; NaN is trimmed with no sentence. Latent until Phase 19 wires a tip radius field; cheapest to fix before then.
3. Recorded caveats, accepted by the human in the phase's own records: T4's 1.39x headroom (rounded reference, D-15); the unreconciled rho 0 crossover figure (bench/RESULTS.md open note); the resource-tracker flake debt re-deferred to Phase 19 planning (IN-06, a `must` item whose trigger has now rolled once).

---

_Verified: 2026-10-08_
_Verifier: Claude (gsd-verifier)_
