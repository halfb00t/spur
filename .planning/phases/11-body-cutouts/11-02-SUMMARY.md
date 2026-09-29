---
phase: 11-body-cutouts
plan: 02
subsystem: bench
tags: [honeycomb, cadquery, measurement, spike, hex-cell-cap, cut-spelling]

# Dependency graph
requires: []
provides:
  - "bench/honeycomb_spike.py: whole_cells, cell_count_floor and cells_within (D-07..D-09,
    D-13's raise-to-fit), to be moved into spur.calc unchanged by 11-05"
  - "The measured HEX_CELL_CAP = 120 cells, and the cut spelling (star), for 11-03 through
    11-09 to build on"
  - "bench/RESULTS.md '## Honeycomb cell-count spike (Phase 11, D-24)' section, the
    committed measurement record cited by decision-log L30 (11-09)"
affects: [11-03, 11-04, 11-05, 11-06, 11-07, 11-08, 11-09]

# Actuals (#2632)
actuals:
  tokens: 6108
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Raise-to-fit with an area-based floor before any exact enumeration (D-13):
      cell_count_floor bounds len(whole_cells(...)) from below so cells_within never
      enumerates a size it is going to reject."

key-files:
  created:
    - bench/honeycomb_spike.py
  modified:
    - bench/RESULTS.md

key-decisions:
  - "HEX_CELL_CAP = 120 cells (the row that cut 120 of a requested 125 read 7.15 s of the
    7.5 s budget; the next row, 150 cells, read 7.95 s -- over). 11-05 writes this constant
    from bench/RESULTS.md's '**Cap:**' line."
  - "Cut spelling: star (cut(*prisms)). All three spellings (star/compound/fuse) read within
    0.03 s of each other at the cap's cell count -- inside run-to-run noise, not a real
    margin -- so D-24's >10% rule left the default in place."
  - "The verdict held on the first run: no over-budget row, over-budget confirmation or
    invalid row triggered the plan's blocking checkpoint:decision gate. 11-05/11-06 may
    proceed on this plan's measured numbers."

patterns-established:
  - "A measurement-only spike script (bare Python module, not part of make verify) that
    times every row twice, keeps the slower via slower(), and prints every row before
    computing a verdict -- extends 10-01's tip_chamfer_spike.py shape to a multi-cutter cut."

requirements-completed: []  # REQ-honeycomb-cutout is shared with 11-05/11-06/11-09; not
# marked complete here -- see "Requirements" note below.

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "bench/honeycomb_spike.py measures the honeycomb with no honeycomb field in GearParams: builds through spur.model._build_checked, enumerates whole cells on the axis-centred lattice, cuts them as hexagonal prisms in one cut call"
    requirement: "REQ-honeycomb-cutout"
    verification:
      - kind: other
        ref: ".venv/bin/python -c \"from bench.honeycomb_spike import cost_row; r = cost_row({}, 25); assert r.ok() and (r.cells, r.cell, r.d_faces) == (18, 3.0, 128)\""
        status: pass
      - kind: other
        ref: "make lint typecheck (ruff + mypy --strict, 0 errors)"
        status: pass
    human_judgment: false
  - id: D2
    description: "whole_cells/cell_count_floor/cells_within implement D-07..D-09 and D-13's raise-to-fit exactly, matching the interfaces block's hand-derived numbers"
    requirement: "REQ-honeycomb-cutout"
    verification:
      - kind: other
        ref: "cells_within(25, 3.0, 1.0, 5.975, 13.4375) == (3.0, whole_cells(3.0, 1.0, 5.975, 13.4375)) with len 18"
        status: pass
    human_judgment: false
  - id: D3
    description: "bench/RESULTS.md gains the spike section (host state, 11 cost rows, spelling, cap, module-1.75 confirmation, enumeration cost, held verdict), append-only, before any honeycomb field exists in src/"
    requirement: "REQ-honeycomb-cutout"
    verification:
      - kind: other
        ref: "plan verify block: 11 cost rows, 1 Cap line, 1 'Verdict: held' line; git diff --numstat shows 0 deletions; git diff --quiet against src tests Makefile"
        status: pass
    human_judgment: false
  - id: D4
    description: "HEX_CELL_CAP = 120 cells is the measured cap 11-05 will write, and star is the measured cut spelling every cutter (11-03 spokes, 11-06 holes, 11-08 honeycomb) will use"
    verification: []
    human_judgment: true
    rationale: "The cap and spelling are numbers read off a real (load-affected) run on shared hardware; a human should confirm the recorded numbers and their headroom (0.35 s at the cap, 0.25 s at the module-1.75 confirmation) before 11-05 through 11-09 build on them, even though the plan's own verdict gate already held."

# Metrics
duration: ~35min
completed: 2026-09-29
status: complete
---

# Phase 11 Plan 02: Honeycomb Cell-Count Spike Summary

**Measured before any honeycomb field exists: HEX_CELL_CAP = 120 cells (7.15 s of a 7.5 s budget) and cut spelling `star`, both read off `bench/honeycomb_spike.py` against the real 200-tooth module-10 gear, verdict held on the first run.**

## Performance

- **Duration:** ~35 min (script authoring + verification, then the ~2 min real sweep,
  then recording)
- **Started:** 2026-09-29T11:03:00Z (approx, this session)
- **Completed:** 2026-09-29T11:20:00Z (approx, this session)
- **Tasks:** 2 (Task 1 tracer, Task 2 auto)
- **Files modified:** 2 (`bench/honeycomb_spike.py` created, `bench/RESULTS.md` appended)

## Accomplishments

- `bench/honeycomb_spike.py` (394 lines) measures the honeycomb with no `hex_cell`/
  `hex_wall` field anywhere in `GearParams`: `whole_cells` (D-07/D-08), `cell_count_floor`
  (D-13's guaranteed area floor) and `cells_within` (D-13's raise-to-fit) enumerate and
  size the lattice; `hex_prisms`/`cut_with` build and cut the cells in exactly one
  `solid.cut(*prisms)` call (D-24); `CostRow`/`cost_row`/`slower`/`main` time build, cut
  and export per cell-count target through `spur.model._build_checked` and
  `model._write_export`, matching `bench/tip_chamfer_spike.py`'s shape.
- One configuration verified end to end before commit: the default 19-tooth gear at
  `cell_count_floor`-guided `cells_within(25, 3.0, 1.0, 5.975, 13.4375)` cuts exactly 18
  cells at 3.0 mm, `+128` faces, one valid solid -- matching the plan's `<interfaces>`
  block exactly (`inner=5.975`, `outer=13.4375`).
- The full spike ran once, real, on the pinned kernel: `bench/RESULTS.md` gained
  "## Honeycomb cell-count spike (Phase 11, D-24)" with 11 cost rows (targets 0 through
  300 at 200 teeth / module 10 / both recesses), a 3-way cut-spelling table, the measured
  cap, a module-1.75 confirmation row, the enumeration cost, and a held verdict.
- **HEX_CELL_CAP = 120 cells**: the `target=125` row raised `hex_cell` to 149.1 mm and cut
  exactly 120 whole cells, reading 7.15 s of the 7.5 s budget; the next row (`target=150`,
  150 cells) read 7.95 s -- over budget, confirming 120 is the true boundary, not a rounder
  number picked by inspection.
- **Cut spelling: `star`** (`solid.cut(*prisms)`). All three spellings read within 0.03 s
  of each other at 120 cells (6.81/6.84/6.83 s) -- inside this run's own noise, so D-24's
  ">10% faster" bar was never cleared and the default stands.
- **Module-1.75 confirmation**: 7.25 s of 7.5 s at the same 120 cells, 0.10 s heavier than
  the module-10 cap row (7.15 s) -- confirming Flagged Assumption A2 (the smaller-module
  gear is the heavier one) at a far narrower margin than the planning probe's 150-cell
  reading (8.4 s vs 7.6 s). D-11's module-10 configuration still sets the cap, with only
  0.25 s of headroom on the confirmation row.
- **Enumeration cost**: `cells_within(120, 3.0, 0.4, inner, outer)` (the heaviest input --
  `hex_wall` 0.4) reads **7.371 ms** best of 5, the number 11-05's `cells_within`
  docstring will cite once the function moves into `spur.calc`.
- **Verdict held** on the first run: no over-budget row, cap-under-50 case or
  over-budget confirmation fired the plan's blocking gate. 11-05 through 11-09 may build
  on these numbers without a human decision being required here.

## Task Commits

Each task was committed atomically:

1. **Task 1: bench/honeycomb_spike.py (tracer)** - `35f0137` (chore) -- the probe script,
   verified end to end on the default gear (18 cells, +128 faces) before commit; tracer
   feedback gate re-ran the same automated `<verify>` and passed, so Task 2 ran without a
   checkpoint (interactive, `human_verify_mode=end-of-phase`, `<verify>` carried only
   `<automated>` entries).
2. **Task 2: bench/RESULTS.md (auto)** - `fb2e34c` (docs) -- the real sweep's output,
   recorded verbatim with the required prose around each table; verdict held, so the
   plan's Task 2 gate (checkpoint on a FAILED verdict) never fired.

**Plan metadata:** this SUMMARY and `.planning/STATE.md`/`.planning/ROADMAP.md` are
committed separately per `execute-plan.md`'s `git_commit_metadata` step (`.planning/`
rides the same PR as the code, per 11-CONTEXT.md D-22).

## Files Created/Modified

- `bench/honeycomb_spike.py` - the committed spike: lattice enumeration, raise-to-fit,
  cost rows, the three cut spellings, the cap search, and a verdict; 394 lines, no
  `Any`, no `type: ignore`, `make lint typecheck` clean.
- `bench/RESULTS.md` - append-only (+100 lines, 0 deletions): the new
  "## Honeycomb cell-count spike (Phase 11, D-24)" section.

## Decisions Made

- **HEX_CELL_CAP = 120 cells**, the largest count whose row read inside 7.5 s at D-11's
  configuration (200 teeth, module 10, both recesses, `hex_wall` 1, requested `hex_cell`
  3). Not a target value (125) and not a rounder number -- exactly what the row cut.
- **Cut spelling: `star`** (`cut(*prisms)`), carried unchanged from the default because no
  alternative spelling cleared D-24's 10% bar at the cap's cell count.
- The host was loaded (8-9 on a 12-core machine, well above the project's 1.5 "quiet"
  bar) for the whole run; the numbers carry that caveat per L08 and are conservative, not
  optimistic -- a quieter host would read every row faster, which could only raise the
  measured cap, never lower it.

## Deviations from Plan

None - plan executed exactly as written. The verdict held on the first real run, so the
plan's Task 2 gate (a blocking `checkpoint:decision` on a FAILED verdict) never fired and
no human decision was required mid-plan.

## Issues Encountered

None. `make verify` (455 tests) stayed green through both commits; the pre-commit hook's
`make verify` run completed inside the hook's own window both times (no
`gsd_run query commit` wrapper was used per D-23, so the documented 30 s-timeout tech
debt did not apply here).

## User Setup Required

None - no external service configuration required.

## Requirements

`REQ-honeycomb-cutout` is declared by this plan's frontmatter and also by 11-05, 11-06
and 11-09 (the field, cutter and proof plans this spike's numbers feed). Per the phase's
shared-ID rule it is not marked complete from this plan alone -- `execute-plan.md`'s
`update_requirements` step computes the ready subset via `requirements.ready-ids` and will
mark it only once every declaring plan has its own SUMMARY.md.

## Next Phase Readiness

- 11-03 (spokes) and 11-04 can proceed independently -- this plan's numbers are the
  honeycomb's alone.
- 11-05 (honeycomb field + `calc.py` functions) writes `HEX_CELL_CAP = 120` and moves
  `whole_cells`/`cell_count_floor`/`cells_within` into `spur.calc` unchanged, per this
  plan's `key_links`.
- 11-06 through 11-09 (the honeycomb cutter, sweep and proof) use `cut(*prisms)` (`star`)
  as the cut spelling every cutter pattern adopts, per this plan's `key_links`.
- No blockers. The module-1.75 confirmation's narrow headroom (0.25 s) is worth watching
  in Phase 12's combined re-measurement, but is not a blocker here -- both readings held
  inside budget on a loaded host.

---
*Phase: 11-body-cutouts*
*Completed: 2026-09-29*

## Self-Check: PASSED

- `[ -f bench/honeycomb_spike.py ]` → FOUND
- `[ -f bench/RESULTS.md ]` → FOUND
- `[ -f .planning/phases/11-body-cutouts/11-02-SUMMARY.md ]` → FOUND
- `git log --oneline --all | grep 35f0137` → FOUND (Task 1 commit)
- `git log --oneline --all | grep fb2e34c` → FOUND (Task 2 commit)
- Plan-level `<verification>` re-run: `make lint typecheck` clean; one configuration
  (default gear) 18 cells at 3.0 mm, +128 faces, one valid solid; `bench/RESULTS.md`
  spike section has host state, 11 cost rows, spelling, cap, confirmation, enumeration
  cost and a held verdict, append-only (+100/-0 lines); `git diff --quiet b86a0e9 --
  src tests Makefile` exits 0 (unchanged since baseline)
