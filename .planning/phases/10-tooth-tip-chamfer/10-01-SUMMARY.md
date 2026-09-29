---
phase: 10-tooth-tip-chamfer
plan: 01
subsystem: bench
tags: [cadquery, chamfer, benchmarking, measurement-spike]

requires: []
provides:
  - "bench/tip_chamfer_spike.py: a committed, rerunnable probe measuring Mixin3D.chamfer()
    on the 2 x teeth end-face tip-arc edges through spur.model._build_checked, before
    any tip_chamfer field exists"
  - "bench/RESULTS.md '## Tooth-tip chamfer spike (Phase 10, D-05)' section: 18 cost
    rows, the kernel-boundary bisection, the 405-set grid, a held verdict"
  - "the measured boundary radius pred = ra - spline_start(pr, root_fillet(p)), teeth-
    independent where compared, one flagged configuration conservative by 0.04mm --
    10-02's third cap term"
  - "the measured fact that chamfer cost is dominated by edge count, not c or module --
    10-02..10-05 do not need a teeth-dependent or c-dependent cap for cost reasons"
affects: [10-02, 10-03, 10-04, 10-05]

actuals:
  tokens: 6536
  tasks: 2
  commits: 2
  plan_head_before: 0317b636a3a673c24df3428d1122ab16d6140487
  plan_head_after: 54a21923cda98259b99454f00288bf466d9b1dfb

tech-stack:
  added: []
  patterns:
    - "measurement-only spike before design: a probe script under bench/, committed
      (not a throwaway), reusing model._build_checked/_write_export unchanged, run
      once and recorded verbatim in bench/RESULTS.md before the field/cap/selector/
      proof plans are written (D-05)"

key-files:
  created:
    - bench/tip_chamfer_spike.py
  modified:
    - bench/RESULTS.md

key-decisions:
  - "The tip-arc selector needs no z-height filter beyond the two end-face positions
    to distinguish the original tip arcs from the moved ones after a chamfer: testing
    both endpoints' z against {0, face_width} (not just one) is what makes 'at both
    end faces, on the unchamfered solid' true -- confirmed working at 200 teeth and
    module 0.2/10, not just the 19-tooth case this session's research probe checked."
  - "pred = ra - spline_start is the correct third cap term (D-04): five of six
    boundary sets bisect to within ~2 microns of pred, teeth-independent (19 and 40
    teeth agree exactly); the sixth (module 1, profile_shift 1.0) builds 0.04mm past
    pred, confirming the rule is conservative there, never optimistic, exactly as
    10-02's own <interfaces> flagged."
  - "A smaller tip_chamfer would not have been cheaper: chamfer cost is set by edge
    count (38/80/400 edges -> 0.3-0.5s/0.8-1.1s/11.9-12.8s), not by c or module (at
    200 teeth, changing c from the small value to the analytic cap moves chamfer
    time by only 2-4%, within this session's run-to-run noise). D-07's over-budget
    checkpoint never fires (heaviest 200-tooth request 15.90s of 30s), so this is
    recorded for 10-02..10-05's benefit, not acted on here."
  - "17 of 163 grid sets where pred sits inside the analytic cap also built when
    chamfered all the way to the analytic cap -- the pred-based rule trims some
    chamfers the kernel would have accepted. Conservative by construction, capped
    and warned (never a 422), matching L03."

requirements-completed: [REQ-tip-chamfer-capped]

coverage:
  - id: D1
    description: "bench/tip_chamfer_spike.py measures the chamfer operator's cost,
      the kernel's boundary against the analytic caps, and the flank rule over a
      405-set grid, with no tip_chamfer field in GearParams"
    requirement: REQ-tip-chamfer-capped
    verification:
      - kind: other
        ref: ".venv/bin/python -m bench.tip_chamfer_spike (exit 0, verdict held)"
        status: pass
      - kind: unit
        ref: "bench/tip_chamfer_spike.py cost_row({}, 0.4) tracer assertion (38 arcs,
          19/19 per face, +38 CONE faces, +114 edges)"
        status: pass
    human_judgment: false
  - id: D2
    description: "bench/RESULTS.md records the full spike run: host state, 18 cost
      rows, the boundary table, the grid line and a held verdict, append-only"
    requirement: REQ-tip-chamfer-capped
    verification:
      - kind: other
        ref: "grep -c '^| teeth=' over the Cost table == 18; grep -c '^\\*\\*Verdict:\\*\\*
          held' == 1; git diff --numstat 25b2216 -- bench/RESULTS.md == 0 deletions"
        status: pass
    human_judgment: false

duration: 52min
completed: 2026-09-28
status: complete
---

# Phase 10 Plan 01: Tooth-Tip Chamfer Spike Summary

**Measured `Mixin3D.chamfer()` on up to 400 tooth-tip-arc edges at once: 18 cost rows, a
teeth-independent kernel boundary at `ra - spline_start`, and a 405-set grid, all before
the `tip_chamfer` field exists -- verdict held, no checkpoint fired.**

## Performance

- **Duration:** 52 min (includes an ~8 min full spike run against the pinned kernel)
- **Started:** 2026-09-28T11:21:48Z (previous commit on this branch)
- **Completed:** 2026-09-28T12:14:03Z
- **Tasks:** 2
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments

- `bench/tip_chamfer_spike.py`: a committed, typed (mypy `--strict`, no `Any`), ruff-clean
  probe script that builds each set through `spur.model._build_checked`, selects the
  `2 x teeth` end-face tip-arc `CIRCLE` edges by radius `ra` and both-endpoint z-position,
  and times `Mixin3D.chamfer()` plus fine-STL and STEP export -- `bore_chamfer`'s exact
  call, reused verbatim.
- 18 cost rows (19/40/200 teeth x module 1.75/10/0.2, `c` at 0.4/0.05 and each config's
  analytic cap): every row `ok()` -- exactly `2 x teeth` tip arcs split evenly per face,
  `+2 x teeth` CONE faces, `+6 x teeth` edges, volume strictly smaller, bounding box
  unchanged within `TOL` (D-12's expected deltas, pinned by measurement, not derived).
- Heaviest 200-tooth request: **15.90s of the 30s `SPUR_BUILD_TIMEOUT`** (module 0.2,
  backlash 0.07, `c`=0.05) -- about half the budget. D-07's over-budget checkpoint does
  not fire.
- Kernel-boundary bisection (20 steps, 09-03's method) on six configurations: `pred = ra
  - spline_start` holds to within ~2 microns on five of six, teeth-independent where
  compared; the sixth (module 1, x 1.0) is conservative by 0.04mm, exactly as flagged.
  The 200-tooth pair confirms it: builds 0.001mm inside `pred`, fails 0.05mm past it,
  while D-01/D-02's analytic caps alone would both have passed that same `c`.
- 405-set grid (19 teeth, no bore, no recess): 163 sets where `pred` sits inside the
  analytic cap, 0 failures at `pred` or 0.05mm inside it, 17 of those 163 also build at
  the (larger) analytic cap -- confirming the rule is conservative, never a 422.

## Task Commits

Each task was committed atomically:

1. **Task 1: One tip-chamfer measurement end to end** - `56daf85` (chore)
2. **Task 2: Run the whole spike and record every cost row, the kernel boundary, the
   grid and the verdict** - `54a2192` (docs)

_Plan metadata (this SUMMARY, STATE.md, ROADMAP.md) is committed separately below._

## Files Created/Modified

- `bench/tip_chamfer_spike.py` - the committed spike: `spline_start()`, `tip_arcs()`,
  `chamfered()`, `CostRow`, `cost_row()`, `boundary()`, `edge_of_200()`, `grid_check()`,
  `main()`; `COST_SETS` (18 rows), `BOUNDARY_SETS` (6 sets), `GRID` (405 sets)
- `bench/RESULTS.md` - new `## Tooth-tip chamfer spike (Phase 10, D-05)` section
  (append-only, 120 lines added, 0 deleted)

## Decisions Made

See `key-decisions` in the frontmatter above -- the selector's z-both-endpoints test,
`pred`'s teeth-independence (with its one flagged 0.04mm-conservative exception), the
edge-count-not-`c`-or-module cost finding, and the grid's 17-conservative-sets reading.

## Deviations from Plan

None - plan executed exactly as written. Two lint-only fix cycles during Task 1 (ruff
flagged unused `noqa: SLF001`/`BLE001` directives -- neither rule is enabled in this
project's ruff config; removed rather than suppressed) and one mypy fix (an unnecessary
`# type: ignore[attr-defined]` on `cq.Solid.chamfer()` -- `cq.Solid`, unlike `cq.Shape`,
already types `chamfer` directly, so the ignore model.py needs on a `cq.Shape`-typed
variable was unneeded here). All three are Rule 3 (blocking, auto-fixed): the file would
not have passed `make lint typecheck` otherwise. No behavior change; committed as part of
Task 1's single commit, not separately.

## Issues Encountered

None. Host load was well above this project's usual "quiet" bar (7.18-7.72 of the 1.5
convention on this 12-core host) for the full spike run; the RESULTS.md section carries
that caveat per L08, and the one place it could plausibly matter (whether chamfer cost
moves with `c`) is called out explicitly as noise-level rather than presented as clean.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `bench/RESULTS.md`'s spike section reads `**Verdict:** held`, so 10-02 through 10-05
  are cleared to run on this plan's `<interfaces>` numbers -- the plan's own gate
  precondition (`bench/RESULTS.md` "the applied `c` ... a superseding decision" / key_links
  `^\*\*Verdict:\*\* held`) is satisfied. No `checkpoint:decision` was needed.
- 10-02's cap function needs the third term folded in as `pred` (this plan's
  `spline_start()` mirrored from `model._outline` lines 123-125, to be moved into
  `spur.calc` per the module's own docstring note) less a small margin -- the exact
  margin is 10-02's own decision, informed by the ~2-micron-to-0.04mm range measured here.
- No blockers. `src/`, `tests/` and the `Makefile` are byte-unchanged since `25b2216`,
  confirmed by `git diff --quiet` in both tasks' acceptance criteria.

---
*Phase: 10-tooth-tip-chamfer*
*Completed: 2026-09-28*

## Self-Check: PASSED

- FOUND: bench/tip_chamfer_spike.py
- FOUND: bench/RESULTS.md
- FOUND: .planning/phases/10-tooth-tip-chamfer/10-01-SUMMARY.md
- FOUND commit: 56daf85
- FOUND commit: 54a2192
