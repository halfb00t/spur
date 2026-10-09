---
phase: 18-trochoid-maths-proved
plan: 04
subsystem: gear-maths
tags: [trochoid, swept-cutter-oracle, roll-window, freecad-gears, kisssoft, tripwire, bars-and-headroom, bench, stdlib-math]

requires:
  - phase: 18-trochoid-maths-proved
    provides: "plans 01-03: the cutter, the generator, root_mode and its six refusals, the sweep product and SWEEP_BAR, the oracle of 18-01"
provides:
  - "T2: twelve gate rows, three negative controls and a 1e-6 mm tip-radius tripwire in tests/test_trochoid.py; the same oracle over all 10,326 curves and 73 severed teeth of the sweep product in bench/trochoid.py oracle"
  - "tests/trochoid_oracle.py with a roll window of +-3 spans (was +-1), which restores the severed-tooth separation 18-RESEARCH described"
  - "T3: FREECAD_T3_POINTS, 60 literals printed once by freecad.gears 4cc4b1a (GPL-3.0, never imported), matched point for point at 1.8e-15 mm and 1.9e-16 rad"
  - "T4: ZHANG_T4, KISSsoft 4.1530 in reproduced at 3.6e-5 in against a half-digit bar of 5e-5, headroom 1.39 as accepted at D-15"
  - "bench/RESULTS.md Oracle bars (18-04) with host state, the failed first run and its cause, the controls, tripwires, bars and headroom"
affects: [18-05, 19]

actuals:
  tokens: 12535   # chars/4 over the added lines of src, tests and bench (50,139 chars, RESULTS.md included)
  tasks: 3        # Task 3 (the L33 D-06 checkpoint) was not reached; it is counted as resolved by its own clause
  commits: 4      # MEASURED: git rev-list --count ff74291..08a1d8d
plan_head_before: ff74291b5a448773ca103172b853806acc29eadd
plan_head_after: 08a1d8d8f1c83a78ab10fbb6d200e8e323270c85
commits: 4

tech-stack:
  added: []
  patterns:
    - "an oracle's search window is a measured quantity too: written beside the largest roll it must contain, and the whole product is run before a bar is trusted"
    - "a reference's printed numbers enter the repository as literals with source file, commit, licence and date; the code that printed them never does"
    - "a bar that cannot reach 10x by construction (a rounded reference) is recorded as such with the acceptance beside it, and its tripwire carries the weight"

key-files:
  created: []
  modified:
    - tests/test_trochoid.py
    - tests/trochoid_oracle.py
    - tests/test_bench.py
    - bench/trochoid.py
    - bench/RESULTS.md

key-decisions:
  - "Oracle roll window widened from +-1 to +-3 spans of 2 pi / z (grid unchanged at 2001): the contact roll of a trochoid point reaches 2.13 spans over the sweep product and about 2.3 over the box; at +-1, 3,244 of 10,326 curves read up to 0.61 mm uncut"
  - "ORACLE_BAR_MM stays 1e-9 mm: 335x over the product's worst reading (a join-band case, geometry), 6.3e3x outside the band, 1.0e5x on the gate rows; the tripwire reads 220x the bar"
  - "T3_BAR_MM and T3_BAR_RAD are the 1e-12 libm floor (10x the larger gap is 1.8e-14): headroom 563 and 5.1e3, tripwire 7.4e5x and 1.8e5x"
  - "T4_BAR_IN = 5e-5 in, half the last printed digit; headroom 1.39 accepted at D-15 and not escalated; tripwire 15.6x"
  - "T3's psi is the library's own sample parameter, not acos((df/2)/R): the inverse turns 1e-16 in R into 1.5e-8 rad at the first point"
  - "The severed-tooth agreement is the one flank with the neighbouring cutter teeth on (a gouge on 73 of 73), as the plan said, not the mirror flank 18-02 had to use"
  - "L33 D-06 checkpoint not reached: every bar at or above 10x"

requirements-completed: [REQ-trochoid-proved-independently]

coverage:
  - id: D1
    description: "The swept-cutter oracle with neighbouring teeth reads every point of twelve gate rows (crossing and tangent; rho 0, w_c 0, w_c > 0, tip land nearly gone; module 0.2 to 10; backlash 0 to 1.0) within 1e-9 mm, in either point order, and a rho moved by 1e-6 mm reads 220 times the bar"
    requirement: REQ-trochoid-proved-independently
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_t2_the_oracle_reads_every_gate_row_as_the_cut_boundary"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_t2_moving_rho_by_1e_6_mm_breaks_the_oracle_bar"
        status: pass
    human_judgment: false
  - id: D2
    description: "The oracle can see a gouge: the involute below the crossing, the trochoid past it, and a severed tooth (one flank, neighbours on) all read below -1e-4 mm; the severed tooth reads nothing with the neighbours off"
    requirement: REQ-trochoid-proved-independently
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_t2_the_oracle_sees_a_gouge_where_one_exists"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_a_severed_tooth_is_refused_and_the_oracle_with_neighbours_agrees"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every curve of the whole sweep product (10,326) reads within 1e-9 mm in bench, every one of the 73 severed teeth reads a gouge, and the reading does not depend on the worker count"
    requirement: REQ-trochoid-proved-independently
    verification:
      - kind: other
        ref: ".venv/bin/python -m bench.trochoid oracle (exit 0, worst 2.985e-12 mm, 73 of 73)"
        status: pass
      - kind: other
        ref: ".venv/bin/python -m bench.trochoid oracle --serial-slice 200 (worst equal to the pooled run's on the same 200 cases)"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_the_oracle_worker_reads_a_curve_clean_and_a_severed_tooth_as_a_gouge"
        status: pass
    human_judgment: false
  - id: D4
    description: "The sharp cutter matches 60 points printed once by freecad.gears (commit 4cc4b1a, GPL-3.0, never imported) at 1.8e-15 mm and 1.9e-16 rad; a tip radius of 1e-6 mm reads above both bars; no GPL code is in the tree"
    requirement: REQ-trochoid-proved-independently
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_t3_the_sharp_cutter_matches_freecad_gears_point_for_point"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_t3_a_1e_6_mm_tip_radius_breaks_the_freecad_bar"
        status: pass
    human_judgment: false
  - id: D5
    description: "The tangent junction reproduces KISSsoft's 4.1530 in (Zhang, AGMA 18FTM02, Table 7 example 7) within half the last printed digit, with the inferred pitch recorded; labelled the cutter-envelope junction, not ISO 21771 parity"
    requirement: REQ-trochoid-proved-independently
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_t4_the_tangent_junction_matches_kisssoft_s_form_diameter"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_t4_a_1e_3_in_tip_radius_moves_the_form_diameter_past_the_bar"
        status: pass
    human_judgment: false
  - id: D6
    description: "Every bar of the phase has at least 10x headroom over the gap it was set from, apart from T4's accepted 1.4x"
    requirement: REQ-trochoid-proved-independently
    verification: []
    human_judgment: true
    rationale: "A bar placed to pass cannot be told from a measured one by a test; the table below and bench/RESULTS.md carry the two numbers beside each bar for a reader to judge (L33 D-06)"

duration: 28min
completed: 2026-10-08
status: complete
---

# Phase 18 Plan 04: The Independent Proof Summary

**The trochoid is now read as the cut boundary by something that shares no code with it, at 1e-9 mm over a dozen gate rows and all 10,326 curves of the sweep product, against freecad.gears at 1.8e-15 mm on a sharp cutter and against KISSsoft's 4.1530 in; the first whole-product run failed because the oracle's roll window was too narrow, and fixing that also restored the severed-tooth separation 18-02 could not reproduce.**

## Performance

- **Duration:** 28 min (start 2026-10-08T02:14:24Z recorded after the initial reads; the pooled oracle runs took 4.3 minutes each)
- **Completed:** 2026-10-08T02:43Z
- **Tasks:** 2 executed; Task 3 is a conditional checkpoint and was not reached
- **Files modified:** 5 (`tests/test_trochoid.py`, `tests/trochoid_oracle.py`, `tests/test_bench.py`, `bench/trochoid.py`, `bench/RESULTS.md`)

## Accomplishments

- **T2 at the gate.** Twelve rows (10-tooth tracer, the default gear, 17 and 18 teeth at the undercut edge, thin positive waist, two cap requests, w_c 0 and above, module 0.2 and 10, backlash up to 1.0) read within 1e-9 mm, worst 9.83e-15 mm. Each asserts its curve has 16 points before reading and reads the same, reversed, with the points reversed.
- **Three negative controls**, all below -1e-4 mm: the involute between rb and the crossing (-5.3e-3, -3.7e-3, -1.9e-3), the trochoid past the crossing (-9.6e-3, -2.2e-2, -5.19e-2, the research's 5.19e-2 at the foot), and a severed tooth (-0.138979 mm one flank, neighbours on; -2.1e-15 mm off).
- **Tripwire:** the tracer generated at tip radius + 1e-6 mm reads 2.205e-07 mm, 220 times the bar.
- **T2 over the whole product** (`bench.trochoid oracle`, 12 spawn workers, 257 s): 10,326 curves, none beyond the bar, worst 2.985e-12 mm at a join-band case (geometry), every other curve 1.6e-13 mm or less; 73 of 73 severed teeth read a gouge. Serial 200-case slice: worst 2.63897000341122582e-15 mm, equal to the pooled run's on the same cases to every printed digit.
- **T3:** 60 literals (12 gears, five points each) from freecad.gears `4cc4b1a233c232e15c3fdfb8a35909aa0d828796`, matched point for point at 1.776e-15 mm and 1.943e-16 rad; bars 1e-12; tripwire 7.4e5 and 1.8e5 times the bars.
- **T4:** KISSsoft 4.1530 in against 4.153036 in (gap 3.59e-5 in, bar 5e-5, headroom 1.39 as D-15 accepted); a 1e-3 in tip radius reads 15.6 times the bar; the pitches 7.999 and 8.001 miss it by 11.0 and 9.6 times.

## Bars, their two numbers and their headroom (the Task 3 collection)

| Bar | Value | Measured gap it was set from | Headroom |
|---|---|---|---|
| `JUNCTION_BAR_RAD` (18-01) | 1e-12 rad | 4.16e-17 rad | 2.4e4 |
| `JUNCTION_BAR_MM` (18-01) | 1e-12 mm | 1.78e-15 mm | 562 |
| `DIRECTION_BAR_RAD` (18-01) | 1e-5 rad | 1.38e-7 rad; the crossing row reads 4.13e-3 rad, 413 times the bar | 72 |
| `SWEEP_BAR` (18-03) | 1e-12 | 6.9e-16 rad (crossing), 1.7e-16 rad and 4.0e-16 relative (tangent) | 1.4e3, 6.0e3, 2.5e3 |
| `ORACLE_BAR_MM` | 1e-9 mm | 2.985e-12 mm (product's worst, a join-band case), 1.594e-13 mm (worst outside the band), 9.83e-15 mm (gate rows) | 335, 6.3e3, 1.0e5 |
| `T3_BAR_MM` | 1e-12 mm | 1.776e-15 mm | 563 |
| `T3_BAR_RAD` | 1e-12 rad | 1.943e-16 rad | 5.1e3 |
| `T4_BAR_IN` | 5e-5 in | 3.593e-5 in | 1.39, accepted at D-15 |

**L33 D-06 checkpoint not reached -- every bar at or above 10x (smallest: `DIRECTION_BAR_RAD` 72, `JUNCTION_BAR_MM` 562, `T3_BAR_MM` 563, `ORACLE_BAR_MM` 335 over the product's worst; the crossing row's separation over its direction bar 413). T4's 1.4x is the one sub-10x bar and was accepted at D-15, not escalated again.**

## Task Commits

1. **Task 1: T2 at the gate and over the whole product** - `16d82a4` (test: gate rows, controls, tripwire, `bench.trochoid oracle`, the oracle's window, 18-02's severed test updated), `63837c5` (docs, bench/RESULTS.md)
2. **Task 2: T3 and T4** - `0ef6a5e` (test), `08a1d8d` (docs)
3. **Task 3: the L33 D-06 checkpoint** - not reached (above)

All four through the pre-commit hook (`make verify.fast`, 15.0 s for the heaviest commit); no `--no-verify`, no `SKIP=`. The two docs commits touch no Python, so the hook skipped the slice.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The oracle's roll window was too narrow, and it hid the severed-tooth separation**
- **Found during:** Task 1, the first pooled run of `bench.trochoid oracle`
- **Issue:** 3,244 of the 10,326 curves read beyond the 1e-9 mm bar, worst +0.6075 mm (14 teeth, module 10, 14.5 degrees, x -0.6, sharp cutter). The gate rows had all read clean. The roll at which the cutter touches a trochoid point is `(a + w_c tan(beta)) / r`; for that gear's first failing point it is -0.473 rad against the oracle's window of +-0.449 (+-1 span of 2 pi / z). Over the product the largest roll is 2.13 spans, and 3,729 cases need more than one span; the closed form bounds the box at about 2.3. A diagnostic window of +-2 spans read the same 16 points at 1e-15 mm. The generator was right; the oracle could not reach the contact. The same window explains 18-02's deviation: its measurement that the neighbouring teeth make no difference on a severed tooth was an artefact of the narrow window.
- **Fix:** `span = 3 * 2 * pi / z` in `tests/trochoid_oracle.py` (1.3 times the box's bound), grid unchanged: 2001 / 3001 / 4001 / 6001 rolls read worst 1.0e-13 / 1.1e-13 / 8.9e-14 / 9.2e-14 mm on a 259-case sample. With it, the 6-tooth, 14.5 degree, x -0.6 sharp-cutter gear reads -0.138979 mm on its one flank with the neighbours on and -2.1e-15 mm off (x -0.5: -0.020103 against -8e-16; the 7-tooth gear nothing either way), which is 18-RESEARCH's account (0.141 and 0.0201). 18-02's `test_a_severed_tooth_is_refused_and_the_oracle_with_neighbours_agrees` now pins that separation, and the bench's severed agreement is the plan's own (one flank, neighbours on) instead of the mirror flank 18-02 had to use. The oracle's docstring, the bar's comment and RESULTS.md state the window and the failed run.
- **Files modified:** `tests/trochoid_oracle.py` and `tests/test_trochoid.py` (18-02's test and docstring), neither of them changing the generator or any `src/spur` file
- **Verification:** the pooled run (exit 0, 0 beyond the bar, 73 of 73 severed), the 259-case grid check, `make verify`
- **Committed in:** `16d82a4`

**2. [Rule 1 - Bug] The plan's recovery of psi from the radius is ill-conditioned at the first point**
- **Found during:** Task 2, the one-off script
- **Issue:** `psi = acos((df/2)/R)` returns 1.49e-8 for a first point whose radius rounds to `rf(1 + 1e-16)`, which would have moved the matched point by about 1e-8 rad and put the T3 comparison nowhere near float level.
- **Fix:** the script records the library's own sample parameter (`numpy.linspace(0, undercut_end, 200)`), asserting `|R - (df/2)/cos(psi)| < 1e-12` at every sample; recorded in `FREECAD_T3_POINTS`' provenance block.
- **Files modified:** none in the repository (the scratch script only)
- **Verification:** the comparison reads 1.776e-15 mm and 1.943e-16 rad
- **Committed in:** `0ef6a5e` (the literals)

---

**Total deviations:** 2 auto-fixed (2 Rule 1)
**Impact on plan:** The first was necessary for the proof to mean anything and strengthened it; the plan's expectation about the neighbours turned out right once the oracle could reach the contact. No change to the generator, to `src/spur` or to a bar.

### Judgement calls inside the plan (not rule deviations)

- **Files beyond the plan's list.** `tests/trochoid_oracle.py` (deviation 1) and `tests/test_bench.py` (one test of the bench worker, so a worker that read 0 on everything fails somewhere in the gate) were touched; the plan's `files_modified` names three.
- **One bar, two copies.** The bench cannot import the test module (the test imports the bench), so `ORACLE_BAR_MM = 1e-9` is written in both and `test_t2_the_bench_oracle_uses_the_gate_s_bar` pins them equal.
- **`_flank_points` in bench/trochoid.py** replaces the eight sampling lines `_severed_waist` had (18-03's noted duplication) because the oracle's severed branch needs the samples too. `tests/test_trochoid.py::_flank_samples` is the same logic once more; left as it was.
- **Scratch directories** are under the session's scratchpad (`spur-18-04-freecad/pygears/`, `spur-18-04-t3/run.py`) rather than `${TMPDIR:-/tmp}`, as the session instruction asked; both are outside the repository.
- **Extra output in the bench run:** the five largest readings, the headroom of the bar over the worst, and the count above 1e-13, so the join-band case is not mistaken for noise.
- **TDD ordering.** Both tasks are `tdd="true"` in a `type: execute` plan and the hook forbids committing a failing test, so tests and code landed together. The failing-first evidence is the first pooled run (3,244 failures), which is the finding in deviation 1; the three tripwires are the red-seen proofs.
- **Co-Authored-By line.** The dispatch prompt asked for `Claude Fable 5.1`; the session's attribution instruction names `Claude Sonnet 5.5`, which is what the four commits carry, as in 18-01 to 18-03.
- **SC5 check** ran as the plan's exact logic from a scratch script after each task and printed `SC5 holds` each time.
- **Pre-existing working-tree changes** (`.planning/state.json` modified, `.DS_Store` and `.planning/milestone.lock` untracked) were there before the plan started and are in no commit.

## Issues Encountered

- The first pooled run took 275 s and failed; see deviation 1. The second and third (with the window fixed) took 258 s each at a 1-minute load of 30 to 40, caused by this session and other users.
- `mypy --strict bench` on its own cannot resolve `trochoid_oracle`; `make typecheck` (src tests docker bench scripts) resolves it from the tests root, as the plan's probe said.

## Verification

- `make verify` after the last code commit: **`1016 passed in 74.77s (0:01:14)`**, `Required test coverage of 96.0% reached. Total coverage: 97.68%`; ruff, mypy `--strict`, 5 import contracts and the unfinished-work scan green.
- `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov --durations=0 -k t2_"`: 15 passed in 6.05 s (twelve rows 0.42 to 0.45 s each, controls 0.61 s, tripwire 0.21 s); `-k 't3_ or t4_'`: 4 passed in 0.13 s.
- `.venv/bin/python -m bench.trochoid oracle`: exit 0, `worst |reading|: 2.985e-12 mm`, 10,326 curves, 73 of 73 severed teeth read a gouge. `--serial-slice 200`: exit 0, same first-200 worst as the pooled run.
- `oracle bars recorded`; `T3/T4 provenance recorded; no GPL code in the tree`; `SC5 holds: fixture byte-identical, only calc.py under src/spur, stdlib maths, 31 pins`.

## Known Stubs

None.

## Threat Flags

None. Tests and a bench subcommand only: no endpoint, auth path, file access beyond the committed tsv or a schema. T-18-11 (each bar from two recorded numbers with headroom beside it, a tripwire per bar seen red, none under 10x apart from D-15's), T-18-12 (the freecad.gears run in scratch directories outside the repository with `-I`, only literals entering with source, commit and licence; no tracked path names pygears or freecad and no tracked file imports it), T-18-13 (the oracle imports nothing from spur; three controls; 73 of 73 severed agreement) are mitigated as planned.

## Tech debt and ideas filed

None filed. Two items to carry: `tests/test_trochoid.py::_flank_samples` and `bench/trochoid.py::_flank_points` are the same sampling twice (a nice-to-merge when either next changes); and 18-02's SUMMARY still records the neighbours as making no difference, which this summary supersedes (deviation 1).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for 18-05 (the per-call costs and the root-shape step). The oracle's window is now measured against the box; if 18-05 or Phase 19 widens the allowed box (module, pressure angle, shift limits), the bound `d cot(alpha) / (r * span)` of 2.3 spans must be re-read against the 3-span window.
- Phase 19's waist-floor decision (D-17) now has an independent reading for it: every one of the 73 severed teeth reads a gouge from -1.653e-03 mm to -1.899 mm, so a floor placed above zero is a choice about how thin a tooth to allow, not about whether the oracle agrees.
- The oracle's reading in the join band is 1e-12 mm (geometry, 2 (tan(phi) - phi)), not noise; a bar tightened below about 3e-12 mm would fail on the two band cases of the product.

## Self-Check: PASSED

- FOUND: `tests/test_trochoid.py`, `tests/trochoid_oracle.py`, `tests/test_bench.py`, `bench/trochoid.py`, `bench/RESULTS.md`
- FOUND commits: `16d82a4`, `63837c5`, `0ef6a5e`, `08a1d8d`
- Acceptance greps found: `def test_t2_the_oracle_reads_every_gate_row_as_the_cut_boundary(`, `def test_t2_the_oracle_sees_a_gouge_where_one_exists(`, `def test_t2_moving_rho_by_1e_6_mm_breaks_the_oracle_bar(`, `FREECAD_T3_POINTS`, `T3_BAR_MM`, `T3_BAR_RAD`, `ZHANG_T4`, `T4_BAR_IN`, `def _oracle(`, `### Oracle bars (18-04)`, `#### T3 and T4`
- `make verify` green, SC5 holds

---
*Phase: 18-trochoid-maths-proved*
*Completed: 2026-10-08*
