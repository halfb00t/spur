---
phase: 12-composition-pass
plan: 02
subsystem: infra
tags: [bench, build-time, stl, composition, measurement]

# Dependency graph
requires:
  - phase: 12-composition-pass
    provides: "12-01-SUMMARY.md: the amended SC3 this plan measures against, and 12-CONTEXT.md D-01/D-02/D-04/D-16"
provides:
  - "stl_size() and Timing.stl_bytes/stl_triangles in bench/build_time.py, so every sweep report from here on names the largest fine STL by a number (D-16)"
  - "bench/sweeps/composed.json: the 18-row composed sweep every cutout pattern's heaviest row, tip-chamfered and doubly-recessed, on its heaviest bore, at both modules, plus six same-host baselines"
  - "Two recorded, non-decisive runs of that sweep in bench/RESULTS.md, naming the heaviest row, the largest fine STL, and the four rows over SPUR_BUILD_TIMEOUT in both runs"
affects: [12-03-timeout-gate, 12-04-export-cost, 12-09-milestone-record]

# Actuals (#2632)
actuals:
  tokens: 9347
  tasks: 3
  commits: 3
  plan_head_before: ed8910b9ff4fa81d60545f31c466cfd3e032f9ab
  plan_head_after: 278d982c5d5672cffb29c546fe505150d89ec638

# Tech tracking
tech-stack:
  added: []
  patterns: ["A sweep-runner report() call reads os.getloadavg() only after every row has built, so its own 'Load averages at start' figure is a load reading taken at report time (near the run's end for a multi-minute sweep), not literally at process start -- documented here so a future decisive-run judgement is not misled by the label"]

key-files:
  created:
    - bench/sweeps/composed.json
  modified:
    - bench/build_time.py
    - tests/test_bench.py
    - bench/RESULTS.md

key-decisions:
  - "Neither of the two runs taken is decisive by D-02's <1.5 bar on the script's own printed load figure, even though the host was independently confirmed quiet (<1.5) immediately before each run was launched -- both are recorded exactly as measured, per the plan's own instruction to stop after one repeat and leave the le/timeout decision to 12-03"
  - "The largest fine STL across both runs is the module-10 hex-bore hole row (bore_hex=200, hole_count=60, hole_d=5.85, hole_circle_d=400, tip_chamfer=3): 17,306,084 bytes, 346,120 triangles, identical in both runs -- 12-04's input for D-16's re-measurement"

patterns-established:
  - "stl_size(data) -> (byte_count, triangle_count): O(1) header read (int.from_bytes(data[80:84], 'little')), raising ValueError on any length mismatch rather than returning a plausible-but-wrong count (L08) -- reused wherever a fine-STL size needs recording"

requirements-completed: [REQ-measured-build-time]

coverage:
  - id: D1
    description: "bench/build_time.py records every sweep row's fine-STL byte count and triangle count (stl_size(), Timing.stl_bytes/stl_triangles, report()'s two new columns) and names the row with the largest fine STL on a **Largest fine STL:** line, refusing (never guessing) on a length/header mismatch"
    requirement: "REQ-measured-build-time"
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_a_binary_stl_is_sized_by_its_length_and_the_triangle_count_its_header_names"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_an_stl_whose_length_disagrees_with_its_header_is_refused"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_the_report_names_the_largest_fine_stl_and_breaks_a_tie_by_file_order"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_an_empty_sweep_is_refused_rather_than_reported"
        status: pass
      - kind: integration
        ref: "one-row tracer: .venv/bin/python -m bench.build_time <one-row sweep> prints '**Largest fine STL:** teeth=19 -- 2313984 bytes, 46278 triangles.'"
        status: pass
    human_judgment: false
  - id: D2
    description: "bench/sweeps/composed.json holds the 18-row composed sweep (D-01): each cutout pattern's heaviest row stacked with the tip chamfer at its cap and both recesses, on its heaviest bore_hex or a keyed round bore, at module 1.75 and 10, plus six same-host baselines"
    requirement: "REQ-measured-build-time"
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_composed_sweep_stacks_each_cutout_on_its_heaviest_bore_beside_six_baselines"
        status: pass
    human_judgment: false
  - id: D3
    description: "bench/RESULTS.md gains '## Composed build and export time (Phase 12)' with two runs recorded exactly as measured (host load readings, tables, Heaviest and Largest fine STL lines), naming the four rows over SPUR_BUILD_TIMEOUT in both runs and stating explicitly that neither run is decisive so no le/timeout decision rests on them (D-02)"
    requirement: "REQ-measured-build-time"
    verification:
      - kind: other
        ref: "plan <verification>: sed -n '/^## Composed .../,$p' bench/RESULTS.md greps for 18+ rows per module, two '### Run N (... decisive)' headers, two Largest fine STL lines, and a zero-deletion git diff against c9a169d"
        status: pass
    human_judgment: true
    rationale: "Whether the recorded non-decisive readings are a sufficient basis to proceed to 12-03's checkpoint, versus attempting further quiet re-runs first, is a judgement about measurement sufficiency this SUMMARY documents but does not itself decide (that decision belongs to 12-03's human checkpoint)."

# Metrics
duration: ~52min (across two host-quiet waits totalling ~16 min and two ~6-7 min sweep runs; continuation session, orchestrator-resumed mid-Task-3)
completed: 2026-09-30
status: complete
---

# Phase 12 Plan 02: Composed Build-Time Sweep Summary

**The 18-row composed sweep (every cutout pattern's heaviest row, tip-chamfered and doubly-recessed, on its heaviest bore, both moduli) measured twice on a host that read quiet before launch but not by the runner's own end-of-run figure — four spoke rows read 31.2-32.0 s of the 30 s timeout in both runs, and the module-10 hex-bore hole row is the largest fine STL (17,306,084 bytes) 12-04 re-measures on.**

## Performance

- **Duration:** ~52 min of wall-clock work this session (continuation: Task 1/2 code+tests, two D-02 quiet-host waits, two ~6-7 min sweep runs, RESULTS.md write-up)
- **Started:** 2026-09-30T08:35Z (approx, this session's first tool call)
- **Completed:** 2026-09-30T09:35Z (approx)
- **Tasks:** 3 (1 tracer/tdd, 2 auto)
- **Files modified:** 4 (1 created, 3 modified)

## Accomplishments

- `bench/build_time.py` records every sweep row's fine-STL byte count and triangle count via a new `stl_size()` header read (O(1), never walking facets), and `report()` names the row with the largest fine STL by a number (D-16) — proven end-to-end through the real runner on a one-row tracer sweep before any other code changed
- `bench/sweeps/composed.json`: 18 rows per D-01 — each of the three cutout patterns' recorded heaviest row, stacked with the tip chamfer at that gear's own cap (1.75 mm at module 1.75, 3 mm at module 10) and both recesses, on the largest `bore_hex` its hub rule allows (43.35 / 156.3 / 200 mm) and separately a keyed round bore, at both moduli — plus the six single-feature heaviest rows re-run unchanged as same-host baselines
- Two runs of the full sweep recorded in `bench/RESULTS.md`, both taken immediately after independently confirming the host quiet (`uptime`/`sysctl -n vm.loadavg` < 1.5), but neither decisive by the script's own printed "Load averages at start" figure (12.66 and 7.04) — a load reading `report()` takes only after every row has already built, so it reflects load near the end of a 6-7 minute run, not its true start
- Four spoke rows (both bore shapes, both moduli, each stacked with the tip chamfer and both recesses) read over `SPUR_BUILD_TIMEOUT=30s` in both runs (31.16-31.98 s), within 0.7 s of each other run to run; every other row is inside budget in both runs
- The largest fine STL in both runs is the module-10 hex-bore hole row: 17,306,084 bytes, 346,120 triangles, byte-identical between runs — the row 12-04 re-measures L19 and L24 on

## Task Commits

1. **Task 1: Tracer — one sweep row's fine-STL bytes and triangles end to end through the real runner** - `c79d178` (feat)
2. **Task 2: Commit the 18-row composed sweep and pin it** - `682dca6` (test)
3. **Task 3: Run the composed sweep one gear at a time on a quiet host and record every run** - `278d982` (docs)

_Task 1 carried `tdd="true"`; RED (tests written first, confirmed failing on `ImportError: cannot import name 'stl_size'`) and GREEN (implementation, 14/14 passing) landed in the one `feat` commit above, not separate `test(...)`/`feat(...)` commits — `workflow.tdd_mode` is not enabled in `.planning/config.json`, so the mechanical RED/GREEN/REFACTOR commit-pattern gate does not apply (Phase 8/11 precedent, `08-03-SUMMARY.md`, `11-03-SUMMARY.md`); RED was still run and confirmed failing before GREEN was written, and the plan's own `<action>` explicitly directs one combined commit here._

**Plan metadata:** committed separately (see below)

## Files Created/Modified

- `bench/build_time.py` — `stl_size(data)` (header-only, O(1) byte/triangle read, refuses on length mismatch); `Timing` gains `stl_bytes`/`stl_triangles` (no defaults); `time_set()` returns the fine-STL size alongside the three existing timings; `report()` prints two new columns and a `**Largest fine STL:**` line, and now refuses (`ValueError`) rather than reports an empty sweep
- `tests/test_bench.py` — updates the three existing `Timing(...)` constructions with two integers; adds four Phase-12 unit tests (`stl_size`'s length check, the header-mismatch refusal, the report's new columns/tie-breaking, the empty-sweep refusal) and the composed-sweep pin test (18 rows exact, each hex row's one-step-past refusal naming the cutout's own hub fields, each module's tip-chamfer cap, each baseline's label traced to its own source file)
- `bench/sweeps/composed.json` — new file, 18 rows (D-01)
- `bench/RESULTS.md` — new `## Composed build and export time (Phase 12)` section: intro (SC3 citation, D-01's row design, the largest-hex arithmetic, the module-1.75 recess-position note, D-04's single-gear caveat), two `### Run N (load L at start; not decisive)` subsections (host bullets, 18-row table, Heaviest/Largest fine STL lines, copied verbatim from the runner's own stdout), `### Against the single-feature baselines`, `### SPUR_BUILD_TIMEOUT margin` and `### Gate` — each stating plainly that no run was decisive so no number-backed decision is drawn, per D-02

## Decisions Made

- Recorded two runs, neither decisive, and stopped there per the plan's own instruction ("repeat steps 1-2 once more... if neither is decisive, record them and leave the rest to 12-03's checkpoint") rather than attempting a third run — the plan's protocol caps the retry at one repeat
- Documented, as a measured fact rather than a design change, that `bench/build_time.py`'s `report()` reads `os.getloadavg()` after the whole sweep has run, so its "Load averages at start" figure is really an end-of-run reading — this is pre-existing behaviour (unchanged by D-16's own edits to `report()`) that this session's two independently-quiet-at-launch runs both exposed; recorded in the SUMMARY and in `bench/RESULTS.md`'s intro, not fixed (out of this plan's `files_modified` scope, and changing the runner's own measurement semantics is a Rule 4 architectural question, not raised for this plan)
- Did not touch `docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` or `docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md` (D-05) — the plan's `files_modified` list and its objective statement ("Whether any row is over 30 s, and what happens then, is 12-03's checkpoint") both scope that resolution to 12-03, which is `depends_on: [12-02]` and lists both files in its own `files_modified`

## Deviations from Plan

None - plan executed exactly as written. Two runs were taken exactly per the plan's own step 3 ("if it is not decisive, repeat steps 1-2 once more and record both runs"); neither the RED/GREEN commit consolidation (explicitly directed by Task 1's own `<action>`) nor the two-run stopping point (explicitly directed by Task 3's own `<action>`) is a deviation from the plan — both are the plan's own written instructions.

## Issues Encountered

- The orchestrator's mid-session check reported "no monitor will notify you" and asked me to run the sweep in the foreground; in fact the background quiet-wait task I had already started did complete and notify normally a short time later. No functional impact: I ran the quiet-host wait and both sweep runs as directed (each as its own bounded, monitored background task with a notification on completion), and no other CPU-heavy work ran concurrently with either sweep, satisfying D-02/D-04 either way.
- The host's load average never sustained a from-the-runner's-own-vantage-point reading below 1.5 across two full sweep attempts, despite reading quiet immediately before each launch — documented above as a runner-measurement-timing fact (`report()` reads load after all rows build), not treated as a host problem to fix.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 12-03 (`depends_on: [12-02]`, `autonomous: false`) reads this plan's non-decisive-run record directly: its own first must-have ("if 12-02 recorded no decisive run, the checkpoint's first option is a quiet re-run, not a decision") anticipates exactly this outcome
- 12-04 has its input: the module-10 hex-bore hole row (`bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both`), 17,306,084 bytes / 346,120 triangles, named by `**Largest fine STL:**` in both runs
- `REQ-measured-build-time` stays open in `REQUIREMENTS.md` (shared with 12-03, 12-04, 12-09 per the shared-ID gate, #2388) — marks complete only once the last declaring plan finishes
- `make verify`: **626 passed in 177.44s (0:02:57 wall)**, host load 4.85/4.26/4.52 at start — green, no regressions; `make lint typecheck` and the plan's own `<verification>` block all pass
- No blockers

---
*Phase: 12-composition-pass*
*Completed: 2026-09-30*

## Self-Check: PASSED

- FOUND: `bench/sweeps/composed.json` (created, 18 rows)
- FOUND: `bench/build_time.py` (modified, `stl_size`/`Timing` fields/`report` columns)
- FOUND: `tests/test_bench.py` (modified, 5 new tests)
- FOUND: `bench/RESULTS.md` (modified, new Phase 12 section)
- FOUND: commit `c79d178` in `git log --oneline --all`
- FOUND: commit `682dca6` in `git log --oneline --all`
- FOUND: commit `278d982` in `git log --oneline --all`
- Re-ran all three tasks' acceptance criteria and the plan-level `<verification>` block: all PASS (see task-by-task grep output above in this session's tool transcript)
- `git rev-list --count ed8910b9ff4fa81d60545f31c466cfd3e032f9ab..HEAD` = 3, matching `commits: 3` above
