---
phase: 09-keyway-bore
plan: 04
subsystem: infra
tags: [bench, keyway, build-time, measurement]

# Dependency graph
requires:
  - phase: 09-keyway-bore
    provides: "09-03's six check() refusals (D-02/D-10/D-11/D-12/D-13) that gate every row in this sweep, pinning the exact largest keyway each rule allows at bore_d 200"
provides:
  - "bench/sweeps/keyway_bore.json: the 32-row Phase 9 cross product (module x bore_flat x keyway x recess_sides x bore_chamfer), each row pinned one step from a refusal"
  - "the measured keyway heaviest-configuration build time in bench/RESULTS.md, satisfying ROADMAP Phase 9 SC5 and REQ-measured-build-time's per-feature entry"
affects: [09-05-PLAN.md]

# Actuals (#2632)
actuals:
  tokens: 4945
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A sweep row's 'largest keyway the rules allow' is pinned by a live +0.05 mm probe against the running validator (GearParams.model_validate), not by re-typing the planning-time number -- if a rule's boundary ever drifts, this test fails instead of silently sweeping a value that is no longer the largest allowed"
    - "A sweep that must cover 'the heaviest configuration' when the obvious candidate (the largest keyway) is not obviously the heaviest measures both candidates rather than asserting one -- planning's own probe showed the largest keyway drops the recess and is lighter, which this sweep confirmed live"

key-files:
  created:
    - bench/sweeps/keyway_bore.json
  modified:
    - tests/test_bench.py
    - bench/RESULTS.md

key-decisions:
  - "The sweep's 32 rows are exactly the loop order the plan specified (module, bore_flat, keyway, recess_sides, bore_chamfer); no row was narrowed, dropped, re-picked or re-ordered, and the gate never fired -- every row measured inside SPUR_BUILD_TIMEOUT=30s on the first run"
  - "The heaviest row is a 3 x 1.4 mm keyway that keeps its face recess (4.85 s), not the largest keyway the rules allow (2.46-2.55 s at module 1.75, since the largest keyway pushes the recess out entirely) -- confirms the planning probe's prediction that the sweep must measure both keyway sizes to find the heaviest, not assume the largest keyway is heaviest"
  - "The +0.05 mm edge-of-refusal assertion re-validates every large keyway's boundary live against GearParams.model_validate rather than trusting the planning-time numbers verbatim -- all 8 boundary probes (4 (module, bore_flat) pairs x 2 fields) confirmed refused"

requirements-completed: []  # REQ-keyway-bore is also declared by sibling plan 09-05, which has not yet produced a SUMMARY (shared-ID gate, requirements.ready-ids reported 0/1 ready)

coverage:
  - id: D1
    description: "bench/sweeps/keyway_bore.json holds the full 32-row cross product (module x bore_flat x keyway x recess_sides x bore_chamfer), every row a buildable gear under 09-03's rules, each large keyway sitting exactly one step (0.05 mm) from a refusal"
    requirement: REQ-keyway-bore
    verification:
      - kind: unit
        ref: "tests/test_bench.py::test_the_keyway_bore_sweep_is_every_combination_with_the_largest_keyway_each_rule_allows"
        status: pass
      - kind: other
        ref: ".venv/bin/python -c \"import json; d=json.load(open('bench/sweeps/keyway_bore.json')); assert len(d) == 32\""
        status: pass
    human_judgment: false
  - id: D2
    description: "One keyed set (keyway_width=3, keyway_depth=1.4) runs end to end through make bench.build and produces its timed Markdown row"
    verification:
      - kind: other
        ref: "make bench.build SWEEP=<one-row tmpfile> | grep -cE '^\\| keyway_width=3 keyway_depth=1.4 \\| [0-9]+\\.[0-9]{2} \\|' == 1"
        status: pass
    human_judgment: false
  - id: D3
    description: "bench/RESULTS.md records all 32 measured rows, none over 30 s, the named heaviest row, the host state with its load caveat, and the make verify wall time delta -- REQ-measured-build-time's per-feature entry for the keyway, ROADMAP Phase 9 SC5"
    requirement: REQ-measured-build-time
    verification:
      - kind: other
        ref: "sed -n '/^## Keyway bore build and export time (Phase 9)/,$p' bench/RESULTS.md | grep -cE '^\\| teeth=200 ' == 32; grep -cE '\\*\\*NO\\*\\*' == 0"
        status: pass
    human_judgment: false

# Metrics
duration: ~23min
completed: 2026-09-27
status: complete
---

# Phase 9 Plan 4: Measure the keyway's heaviest build and export time Summary

**All 32 rows of the keyway sweep build inside `SPUR_BUILD_TIMEOUT=30s` on the first run, with the heaviest at 4.85 s of 30 s -- a small 3 x 1.4 mm keyway that keeps its face recess, not the largest keyway the rules allow, which pushes the recess out and builds in about half the time.**

## Performance

- **Duration:** ~23 min (from STATE.md's last session timestamp, 14:28:27Z, to this
  plan's completion, 14:50:52Z; not measured with a dedicated stopwatch)
- **Started:** ~2026-09-27T14:28:27Z
- **Completed:** 2026-09-27T14:50:52Z
- **Tasks:** 2
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments
- `bench/sweeps/keyway_bore.json`: 32 rows, the full cross product of module {1.75, 10} x
  bore_flat {0, 150} x keyway {the largest each rule allows, 3 x 1.4} x recess_sides
  {both, none} x bore_chamfer {0.4, 3} at 200 teeth on the largest bore the rules allow
  (`bore_d` 200).
- `tests/test_bench.py::test_the_keyway_bore_sweep_is_every_combination_with_the_largest_keyway_each_rule_allows`
  pins the exact cross product and re-proves live, via `GearParams.model_validate`, that
  every large keyway sits one step (0.05 mm) from a refusal on both `keyway_width` and
  `keyway_depth` -- 4 (module, bore_flat) pairs x 2 fields, all refused as expected.
  `make test PYTEST_ARGS="tests/test_bench.py -q"`: 6 passed (5 existing + 1 new).
  `make lint typecheck`: both clean.
  `bench/build_time.py` and the `Makefile` are byte-unchanged since `b522044` (08 D-12).
- One keyed set (`keyway_width=3 keyway_depth=1.4`) ran end to end through
  `make bench.build`, producing exactly one timed Markdown row.
- `make bench.build SWEEP=bench/sweeps/keyway_bore.json`: all 32 rows measured inside
  30 s on the first run, exit code 0 -- the 08 D-11 gate never fired, so no
  `checkpoint:decision` was needed. Full sweep wall time (re-timed separately, output
  discarded): 2:01.03.
- `bench/RESULTS.md` "## Keyway bore build and export time (Phase 9)" records all 32
  rows, the host state (load averages 6.10/5.08/4.98 at script start, `uptime`
  4.87/4.33/4.74 -- both above the project's 1.5 quiet bar, caveat recorded per L08), the
  named heaviest row, and the `make verify` wall-time delta this phase added.
- `tests/regression/pre_v0_2.json` stayed byte-unchanged (`git diff --exit-code` after
  both tasks).

## Task Commits

Each task was committed atomically:

1. **Task 1: Commit the keyway sweep, prove every large keyway is the largest the rules allow, and run one keyed set end to end through make bench.build** - `575b3a9` (test)
2. **Task 2: Run the keyway sweep and record every row, the host state and the heaviest row in bench/RESULTS.md** - `aca8487` (docs)

**Plan metadata:** committed separately after this SUMMARY (docs).

## Files Created/Modified
- `bench/sweeps/keyway_bore.json` - the 32-row Phase 9 sweep (new)
- `tests/test_bench.py` - module docstring extended; new cross-product + edge-of-refusal test
- `bench/RESULTS.md` - "## Keyway bore build and export time (Phase 9)" section appended

## Measured Numbers (`make bench.build SWEEP=bench/sweeps/keyway_bore.json`, 2026-09-27, HEAD `575b3a9`)

- **Heaviest row:** `teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=3
  keyway_depth=1.4 recess_sides=both bore_chamfer=0.4` -- **build 4.20 s, fine STL 0.66 s,
  STEP 0.41 s, build + slower export 4.85 s of 30 s.**
- The other 3 x 1.4 mm keyway rows with a kept recess (module 1.75, either `bore_flat`)
  cluster at 4.11-4.20 s build / 4.78-4.85 s worst-request -- all noticeably heavier than
  the corresponding largest-keyway rows (1.86-1.97 s build / 2.46-2.55 s worst-request),
  confirming the planning probe: the largest keyway at module 1.75 pushes the recess out
  entirely, and the lighter recess-free build costs less than the small keyway that keeps
  its recess.
- Module 10 rows run 2.63-2.67 s build / 3.78-3.83 s worst-request when the recess is
  kept (both keyway sizes cost about the same there -- module 10's export time, not the
  keyway size, dominates), and 1.87-2.00 s build / 2.59-2.97 s worst-request with no
  recess.
- No row is within an order of magnitude of the 30 s budget; the 08 D-11 gate ("a set
  over `SPUR_BUILD_TIMEOUT` halts for a human decision") did not fire.
- `time make verify`: **396 passed in 77.20s** -- **78.21s** wall time, against Phase 8's
  recorded **61.74s** / 330 tests -- **+16.47s** for the phase's 66 new tests
  (09-01 through 09-04 combined), measured rather than assumed.

## Decisions Made
- No deviations from the plan's row shape or loop order: every planning-time number in
  09-04-PLAN.md's `<interfaces>` block (the four largest-keyway (width, depth) pairs, the
  chamfer-vs-root-circle margin at module 1.75) reproduced exactly against the running
  validator this session.
- The sweep's heaviest row confirms rather than merely restates the planning hypothesis:
  it was measured live in this session's own `make bench.build` run, not carried over
  from the planning-time single-configuration probe.

## Deviations from Plan

None - plan executed exactly as written. The 08 D-11 gate did not fire (every row
measured inside the 30 s budget on the first run), so no `checkpoint:decision` was
needed, matching the plan's own expectation ("planning expects the heaviest near 5 s, so
this gate is not expected to fire").

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
Ready for 09-05-PLAN.md. The keyway's heaviest configuration is measured and recorded
inside `SPUR_BUILD_TIMEOUT=30s` (ROADMAP Phase 9 SC5 satisfied); `bench/build_time.py`
and the `Makefile` remain unchanged since Phase 8 (08 D-12); `tests/regression/pre_v0_2.json`
stayed byte-unchanged. No blockers. No new tech debt or ideas filed this plan.

---
*Phase: 09-keyway-bore*
*Completed: 2026-09-27*

## Self-Check: PASSED
