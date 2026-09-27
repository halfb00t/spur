---
phase: 09-keyway-bore
plan: 05
subsystem: docs
tags: [keyway, bore, documentation, decision-log, readme]

# Dependency graph
requires:
  - phase: 09-keyway-bore
    provides: "09-02's built keyway (fields, cut, derived numbers), 09-03's six refusals and D-12's fix, 09-04's measured 32-row sweep -- this plan writes down what they built and measured"
provides:
  - "README.md: feature bullet, keyway_width/keyway_depth rows in params.py order, extended bore_clearance row, a keyed CLI export example that runs as a test, refusal prose, and a Geometry notes bullet naming the datum, the sharp slot edges, the unmodelled floor radius and the two printed numbers"
  - "docs/architecture/decision_log.md L28: the keyway's fields, placement, datum formula, build order, recess yield, every refusal, D-12's fix, the two derived numbers and the sweep's heaviest row, all cited to their SUMMARY sha or measurement"
  - "docs/architecture/gear-maths/implementation.md and solid-model/tactics.md kept true: the keyway helpers, ROOT_CONTACT and _cut_keyway named in the pipeline"
affects: []

# Actuals (#2632)
actuals:
  tokens: 4913
  tasks: 2
  commits: 3
  plan_head_before: 8fda4d3c7564efbcf1bf458ca41ad92f478f0cef

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A no-code documentation plan still runs make verify as its own gate and quotes the pytest summary line rather than predicting it"

key-files:
  created: []
  modified:
    - README.md
    - tests/test_cli.py
    - docs/architecture/decision_log.md
    - docs/architecture/gear-maths/implementation.md
    - docs/architecture/solid-model/tactics.md

key-decisions:
  - "No standard keyway size (DIN 6885 or ANSI B17.1) is cited anywhere in README.md or L28 -- the CLI's 3 x 1.4 mm example is an invocation, not a recommendation (D-16, L08)"
  - "L28 appended after L27 with zero deleted lines against the b522044 baseline -- decision_log.md stayed append-only"
  - "The heaviest sweep row (4.85 s of 30 s) is quoted verbatim from bench/RESULTS.md, not re-derived, matching the project's 'measured, not estimated' standard"

patterns-established: []

requirements-completed: [REQ-keyway-bore, REQ-keyway-composes-with-d-flat, REQ-bore-derived-numbers]

coverage:
  - id: D1
    description: "README.md documents the keyway: feature bullet, keyway_width/keyway_depth rows between bore_flat and bore_hex (params.py order), the bore_clearance row extended, a keyed CLI export example, refusal prose, and a Geometry notes bullet on the datum and the two printed numbers"
    requirement: REQ-keyway-bore
    verification:
      - kind: unit
        ref: "tests/test_cli.py::test_readme_export_examples_run"
        status: pass
      - kind: other
        ref: "grep -cE '^\\| \\`keyway_(width|depth)\\` \\| 0 \\|' README.md == 2"
        status: pass
    human_judgment: false
  - id: D2
    description: "The README's keyed CLI example (spur export -o keyedgear.step --keyway-width 3 --keyway-depth 1.4) builds the default D-flat bore plus keyway link end to end with no warning, proving the composition the example is meant to show"
    requirement: REQ-keyway-composes-with-d-flat
    verification:
      - kind: integration
        ref: "tests/test_cli.py::test_readme_export_examples_run (keyed example)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The Geometry notes bullet names both derived fields -- keyway_floor_to_wall and keyway_width_effective -- and what a pin/calipers check reads from each, matching DerivedDimensions (09-02)"
    requirement: REQ-bore-derived-numbers
    verification:
      - kind: other
        ref: "grep -c 'keyway_floor_to_wall' README.md >= 1"
        status: pass
    human_judgment: false
  - id: D4
    description: "L28 is appended after L27 with the datum formula, every phase decision and its SUMMARY citation, and the sweep's heaviest row; decision_log.md stays append-only"
    verification:
      - kind: other
        ref: "git diff --numstat b522044 -- docs/architecture/decision_log.md (0 deletions); grep -c '^## L28 — ' == 1"
        status: pass
    human_judgment: false
  - id: D5
    description: "docs/architecture/gear-maths/implementation.md and solid-model/tactics.md name the keyway helpers, ROOT_CONTACT and _cut_keyway so the architecture docs describe the shipped code"
    verification:
      - kind: other
        ref: "grep -c 'keyway_corner_radius(p)' docs/architecture/gear-maths/implementation.md == 1; grep -c '_cut_keyway' docs/architecture/solid-model/tactics.md >= 1"
        status: pass
    human_judgment: false
  - id: D6
    description: "make verify is green at the end of the phase"
    verification:
      - kind: other
        ref: "make verify"
        status: pass
    human_judgment: false
  - id: D7
    description: "No DIN 6885 or ANSI B17.1 keyway size is given anywhere as sizing guidance, in README.md or L28's user-facing wording (D-16, L08's prohibition)"
    human_judgment: true
    rationale: "The plan's own must_haves mark this prohibition 'verification: judgment' -- grep can prove the convention names (DIN 6885, ISO R773 t2, ANSI B17.1) appear with no numeric example beside them, but confirming no added sentence reads as a sizing recommendation needs a human read of the new prose, not a pattern match."

# Metrics
duration: ~21min
completed: 2026-09-27
status: complete
---

# Phase 9 Plan 5: Document the keyway and log the phase's decisions Summary

**README.md tells a user what the keyway is, how its depth is measured and what gets refused, with no standard size cited; L28 records the whole phase's decisions after L27, append-only; `make verify` closes the phase at 396 passed.**

## Performance

- **Duration:** ~21 min (reconstructed from STATE.md's last session timestamp,
  2026-09-27T14:54:58Z, to this plan's completion, 2026-09-27T15:15:49Z; not measured
  with a dedicated stopwatch)
- **Started:** ~2026-09-27T14:54:58Z
- **Completed:** 2026-09-27T15:15:49Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- README.md: the feature bullet now names the keyway; `keyway_width`/`keyway_depth` rows
  sit between `bore_flat` and `bore_hex` (params.py's order), carrying the help text
  verbatim (D-16, D-17); `bore_clearance`'s row now names the keyway width too; a keyed
  CLI export example (`--keyway-width 3 --keyway-depth 1.4`) runs as part of
  `test_readme_export_examples_run` and stays out of `tests/regression/corpus.py`;
  the 422/warnings prose states the recess-yields and keyway-refusal rules; a new
  Geometry notes bullet states the as-cut-wall datum with its formula, the DIN 6885 /
  ISO R773 `t2` convention against ANSI B17.1's different "T", the sharp slot edges, the
  unmodelled floor-corner radius, and both derived fields (`keyway_floor_to_wall`,
  `keyway_width_effective`).
- `docs/architecture/decision_log.md` L28 appended after L27 (0 deleted lines against
  the `b522044` baseline): the fields, placement and composition, the datum with its
  formula and 09-01's amendment sha, the chamfer-then-cut build order and its measured
  failure/success cases, the recess yield with its measured clearance, every refusal
  (D-02/D-03/D-10/D-11/D-13) with 09-03's re-confirmed kernel behaviour, D-12's
  re-measured `ROOT_CONTACT` fix and its resolved debt file, the two derived numbers,
  and the 32-row sweep's heaviest row quoted verbatim from `bench/RESULTS.md`.
- `docs/architecture/gear-maths/implementation.md`'s Layout table gains `ROOT_CONTACT`
  in the constants row and three keyway-helper rows
  (`keyway_width_effective`/`keyway_corner_radius`/`keyway_flat_wall`); `bore_mouth_limit`'s
  row now names the keyway corner.
- `docs/architecture/solid-model/tactics.md`'s pipeline diagram gains `_cut_keyway` after
  `_cut_bore`, and Edge re-selection notes the keyway is cut after `_bore_rim_edges` runs.
- `make verify`: **396 passed in 77.99s (0:01:17)** — the phase's final gate, green.

## Task Commits

Each task was committed atomically:

1. **Task 1: Document the keyway where users read it** - `1e1c841` (docs)
2. **Task 2: Log L28, keep the architecture docs true, and run the phase's final gate** - `f384fd7` (docs)

**Plan metadata:** committed separately after this SUMMARY (docs).

## Files Created/Modified
- `README.md` - feature bullet, keyway rows, extended `bore_clearance` row, keyed CLI
  example, refusal prose, Geometry notes bullet
- `tests/test_cli.py` - `test_readme_export_examples_run` runs the keyed example
- `docs/architecture/decision_log.md` - L28 appended
- `docs/architecture/gear-maths/implementation.md` - `ROOT_CONTACT`, three keyway helper
  rows, extended `bore_mouth_limit` row
- `docs/architecture/solid-model/tactics.md` - `_cut_keyway` in the pipeline diagram,
  a sentence in Edge re-selection

## Decisions Made
- No standard keyway size (DIN 6885 or ANSI B17.1) is given anywhere in README.md or
  L28 as sizing guidance — the CLI example's 3 × 1.4 mm is an invocation, not a
  recommendation (D-16, L08).
- L28's heaviest-row quote is copied verbatim from `bench/RESULTS.md`, never
  re-estimated, per the project's "measured, not estimated" standard.
- Task 2's D-12 paragraph describes the actual test method used in 09-03
  (`GearParams().model_copy(update=kw)`), not the plan's original
  `model_construct(**kw)` phrasing, since 09-03's own deviation record shows the latter
  fails mypy strict — L28 records what shipped, not what the plan first proposed.

## Deviations from Plan

None - plan executed exactly as written. The only wording adjustment (citing
`model_copy` instead of `model_construct` in L28's D-11/D-12 paragraph) reflects a
deviation 09-03 already made and documented in its own SUMMARY, not a new deviation
introduced by this plan.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
Phase 9 (Keyway Bore) is complete: all five plans have produced summaries, `make verify`
is green (396 tests), `docs/architecture/decision_log.md` carries L28, and
`tests/regression/pre_v0_2.json` and `tests/regression/corpus.py` are unchanged since
`b522044`. No blockers. Landing is `/gsd-ship` and then `make pr.land PR=N` after
verification (D-18, L22/L25) — not a task in this plan.

---
*Phase: 09-keyway-bore*
*Completed: 2026-09-27*

## Self-Check: PASSED
