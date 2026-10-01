---
phase: 12-composition-pass
plan: 04
subsystem: infra
tags: [bench, gzip, mesh-copy, export-cost, l19, l24]

# Dependency graph
requires:
  - phase: 12-composition-pass
    provides: "12-01-SUMMARY.md: the human's binding answer (\"comment + L31\") for where the re-measured gzip row lands; 12-03-SUMMARY.md: the composed sweep's decisive row and its largest-fine-STL line, unaffected by the spoke_count le change"
provides:
  - "bench/export_cost.py, committed behind `make bench.export SWEEP=<json> SET=\"<label>\"` (D-17): re-measures L19's gzip-level table and L24's mesh-copy cost for one parameter set, on demand"
  - "L19's table and L24's copy cost re-measured on the heaviest v0.2 topology (D-16): teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both, 17,306,084 bytes -- D-18's rule re-applied, level 1 confirmed, _GZIP_LEVEL unchanged"
  - "The re-measured gzip table landed as a dated comment addition above _GZIP_LEVEL in src/spur/app.py per 12-01's binding answer; docs/architecture/decision_log.md left untouched by this plan (L31 is 12-09's)"
affects: [12-09-milestone-record]

# Actuals (#2632)
actuals:
  tokens: 7095
  tasks: 2
  commits: 2
  plan_head_before: f7a5483cb8448bfbcca494b4c6d9c8f58ce108a4
  plan_head_after: 4782322dfd65d81fa7909c46a48bf51dbc55c54c

# Tech tracking
tech-stack:
  added: []
  patterns: ["a --child {copy,in-place} subprocess re-invocation for reading a fresh process's own RUSAGE_SELF peak RSS, one process per run, never RUSAGE_CHILDREN's cumulative maximum over every reaped child"]

key-files:
  created:
    - bench/export_cost.py
  modified:
    - Makefile
    - tests/test_bench.py
    - bench/RESULTS.md
    - src/spur/app.py

key-decisions:
  - "D-16's row confirmed by the number, not inspection: the composed sweep's `**Largest fine STL:**` line names the same row in every one of five recorded runs (Runs 1-4 plus the post-gate re-run, 12-02/12-03) -- teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both, 17,306,084 bytes, 346,120 triangles"
  - "D-18's rule re-applied exactly as written on the re-measured table: level 6 misses the 10% shrink bar by the same margin as L19's own reading (7.46% here vs 8.7% there), level 9 likewise (7.44% vs 8.66%) -- level 1 stays, _GZIP_LEVEL unchanged, no test_api.py gzip-body test needed re-running for a level change"
  - "12-01's binding answer (\"comment + L31\") applied: the re-measured table is a dated addition above the existing comment in src/spur/app.py; docs/architecture/decision_log.md carries zero diff against c9a169d from this plan (L31 is 12-09's to write)"
  - "L24's copy cost recorded only, per D-18: +52.9 ms mean export, -56.0 MiB mean peak RSS over in place on this run -- both outside L24's own v0.1 range (+1.4 to +17.6 ms, +3.2 to +7.7 MiB), recorded exactly as measured (L08) rather than adjusted toward it; the copy in model._write_export is unchanged -- a correctness decision (a cached solid never carries a mesh), not a cost trade"
  - "The D-02 quiet-host wait (load1 4.40 falling to 1.30 over 6 minutes) and the script's own genuine at-start reading (1.38, read before any building starts, `bench/build_time.py`'s 12-03 discipline) together make this run decisive -- no loaded-run exception needed"

patterns-established: []

requirements-completed: [REQ-measured-build-time]

coverage:
  - id: D1
    description: "bench/export_cost.py measures, for one parameter set: gzip.compress at levels 1/6/9 (single-threaded median of 5, output bytes, ten-concurrent wall median of 3, L19's table shape) and the fine-STL export on shape.copy() against in place (3 runs per mode alternating, export wall time and peak RSS via resource.getrusage in a fresh child process each run, L24's numbers), with host state printed"
    requirement: "REQ-measured-build-time"
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_l19s_rule_applied_to_its_own_table_keeps_level_1"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_a_higher_gzip_level_is_adopted_exactly_on_both_of_l19s_bars"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_level_9_is_compared_against_the_level_currently_adopted"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_peak_rss_reads_bytes_on_macos_and_kibibytes_on_linux"
        status: pass
      - kind: other
        ref: "make bench.export SWEEP=<tmp one-set sweep> SET=\"teeth=19\" > out.md; grep -cE both verdict-line patterns in out.md == 2 (tracer's own end-to-end run)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The set measured is the composed-sweep row with the largest recorded fine STL (D-16), chosen by the number bench/RESULTS.md's Largest fine STL line records, not by inspection"
    requirement: "REQ-measured-build-time"
    verification:
      - kind: other
        ref: "bench/RESULTS.md \"Export cost on the heaviest v0.2 topology (Phase 12)\" intro paragraph names the row and cites every one of five recorded composed-sweep runs agreeing on it"
        status: pass
    human_judgment: false
  - id: D3
    description: "L19's rule is applied as written on the re-measured table (rows 5-9 of the composed sweep's own quiet-host wait and the script's own at-start load, both recorded); it selects level 1 and _GZIP_LEVEL is unchanged, landed per 12-01's binding answer"
    requirement: "REQ-measured-build-time"
    verification:
      - kind: other
        ref: "sed -n '/^## Export cost on the heaviest v0.2 topology (Phase 12)/,$p' bench/RESULTS.md | grep -cE both verdict-line patterns == 2"
        status: pass
      - kind: other
        ref: "grep -cE '^_GZIP_LEVEL = (1|6|9)$' src/spur/app.py == 1, value 1, matching the section's **L19 selects:** level 1 line"
        status: pass
      - kind: integration
        ref: "make test PYTEST_ARGS=\"tests/test_api.py tests/test_bench.py -q\" -- 73 passed"
        status: pass
    human_judgment: false
  - id: D4
    description: "L24's copy cost is recorded only; the copy in model._write_export is untouched (git diff --quiet c9a169d -- src/spur/model.py exits 0)"
    requirement: "REQ-measured-build-time"
    verification:
      - kind: other
        ref: "git diff --quiet c9a169d -- src/spur/model.py (exit 0, confirmed twice, after each task)"
        status: pass
    human_judgment: false

# Metrics
duration: ~30min
completed: 2026-09-30
status: complete
---

# Phase 12 Plan 04: Export Cost Re-measurement (L19/L24) Summary

**A committed `bench/export_cost.py` behind `make bench.export` re-measures L19's gzip-level table and L24's mesh-copy cost on the composed sweep's heaviest fine-STL row (17,306,084 bytes) -- the rule reads the same verdict as L19's own hand-run table, so `_GZIP_LEVEL` stays 1 and the re-measured table lands as a dated comment addition.**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-09-30T10:15:00Z (approx)
- **Completed:** 2026-09-30T10:45:00Z (approx)
- **Tasks:** 2 (1 tracer/tdd, 1 auto)
- **Files modified:** 5 (1 created, 4 modified)

## Accomplishments

- `bench/export_cost.py` re-measures, for one named parameter set, L19's gzip-level table (levels 1/6/9, single-threaded median of 5, output bytes, ten-concurrent wall median of 3 via `ThreadPoolExecutor`) and L24's mesh-copy cost (`shape.copy()` versus in place, 3 runs per mode alternating, each run its own fresh child process reading `resource.getrusage(RUSAGE_SELF)` so peak RSS is that run's own reading, never `RUSAGE_CHILDREN`'s cumulative maximum)
- `D-18`'s selection rule (integer arithmetic on the 10% shrink bar, each candidate compared against the level currently adopted, not always level 1) is implemented once in `select_gzip_level`/`_decisions` and pinned by four tests against L19's own recorded table, both of its bars exactly, and the level-9-vs-current-adopted distinction
- `make bench.export SWEEP=<json> SET="<label>"` runs end to end: verified on a tiny default gear (tracer) and then on the real heaviest-topology row (Task 2)
- The composed sweep's largest-fine-STL row (`teeth=200 module=10 bore_hex=200 hole_count=60 hole_d=5.85 hole_circle_d=400 tip_chamfer=3 recess_sides=both`, 17,306,084 bytes, 346,120 triangles -- the same row every one of five recorded composed-sweep runs names) was measured on a quiet host (load1 1.38 at the script's own genuine at-start reading, after a 6-minute D-02 wait from 4.40 down to 1.30): the rule again selects level 1 (7.46%/7.44% shrink, both short of the 10% bar, matching L19's own 8.7%/8.66% miss), so `_GZIP_LEVEL` is unchanged; L24's copy cost is recorded as measured (+52.9 ms mean export, -56.0 MiB mean peak RSS -- outside L24's v0.1 range on both axes, at this much larger mesh and process size, recorded honestly rather than adjusted)
- The re-measured table landed exactly where 12-01's binding answer ("comment + L31") put it: a dated addition above the existing comment in `src/spur/app.py`; `docs/architecture/decision_log.md` carries zero diff from this plan

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer -- the export-cost script end to end on the default gear through `make bench.export`** - `64528fb` (feat)
2. **Task 2: Re-measure on the largest composed fine STL, record it, and apply L19's rule** - `4782322` (docs)

**Plan metadata:** committed separately (see below)

_Task 1 carried `tdd="true"`; RED was written first (four tests importing the not-yet-existing `bench.export_cost`, confirmed failing on `ModuleNotFoundError` via a direct `pytest` collection run) and GREEN (the module itself) landed in the same commit as RED and the Makefile wiring -- `workflow.tdd_mode` is not enabled in `.planning/config.json` (confirmed at session start), so the mechanical RED/GREEN/REFACTOR commit-pattern gate does not apply, matching 08-03/11-03/12-02/12-03's established precedent. This project's own pre-commit `make verify` hook blocks any commit that leaves a test failing, so a RED-only commit is not achievable here regardless; RED was confirmed failing by direct `pytest` invocation (not by a rejected commit attempt this time) before GREEN was written._

## Files Created/Modified

- `bench/export_cost.py` -- new module: `GzipRow`, `select_gzip_level`/`_decisions` (D-18's rule), `gzip_rows`, `maxrss_bytes` (Darwin bytes / Linux kibibytes), `_ChildPayload` (typed JSON wire shape for `--child`), `_run_child`, `main()`
- `Makefile` -- `SET ?=` beside `SWEEP ?=`; `bench.export` target and `.PHONY` entry
- `tests/test_bench.py` -- four new tests pinning the D-18 rule and the RSS unit split; module docstring extended
- `bench/RESULTS.md` -- new `## Export cost on the heaviest v0.2 topology (Phase 12)` section: intro, the D-02 quiet-wait readings, the script's output verbatim, and a closing comparison against L19's and L24's v0.1 numbers
- `src/spur/app.py` -- the re-measured gzip table added as a dated comment addition above `_GZIP_LEVEL` (12-01's "comment + L31" answer); `_GZIP_LEVEL` value itself unchanged (still `1`)

## Decisions Made

See `key-decisions` in the frontmatter for the row-selection confirmation, the rule's re-applied outcome, the "comment + L31" landing choice, and the recorded-only copy cost. No new human checkpoint was needed this plan -- both governing decisions (D-16's row, D-18's rule, and 12-01's landing-location answer) were already binding from prior plans.

## Deviations from Plan

None - plan executed exactly as written. One presentation choice within the plan's own latitude: `**Copy cost:**` prints a signed float (`{delta:+.1f}`) rather than a hardcoded `+` prefix, so a run where copy happens to read cheaper than in place (as this run's peak-RSS delta did, -56.0 MiB) prints its honest sign rather than a misleading "+-56.0" double-sign artifact -- consistent with L08 (never a plausible-looking number) and within the plan's own literal template, which was illustrating the typical case, not mandating a hardcoded character.

## Issues Encountered

None. The D-02 quiet-host wait reached below the 1.5 bar within 6 minutes (well inside the 30-minute budget), so no loaded-run re-run or human escalation (D-02's own exception path) was needed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `REQ-measured-build-time` stays open in `REQUIREMENTS.md` (shared with 12-01, 12-02, 12-03, 12-09 per the shared-ID gate, #2388) -- `gsd_run query requirements.ready-ids` confirms it is not yet markable (12-09 has no SUMMARY.md); it will flip once 12-09 finishes
- 12-09 (milestone record) can now cite this plan's `bench/RESULTS.md` section and `src/spur/app.py`'s dated comment directly when it writes the phase's one `L31` entry (D-19) -- L19's own text was never edited (decision-log append-only invariant, D-19's own rule, held)
- `make verify`: 627 passed at session start (before any change, D-21's "run once at session start"); after both tasks, `make test PYTEST_ARGS="tests/test_api.py tests/test_bench.py -q"` (73 passed), `make lint typecheck lint-imports no-fake-done` (all clean), and `git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json` (clean) all re-confirmed green
- No blockers

---
*Phase: 12-composition-pass*
*Completed: 2026-09-30*

## Self-Check: PASSED

- FOUND: `bench/export_cost.py` (created)
- FOUND: `.planning/phases/12-composition-pass/12-04-SUMMARY.md` (this file)
- FOUND: commit `64528fb` in `git log --oneline --all`
- FOUND: commit `4782322` in `git log --oneline --all`
- Re-ran the plan's own `<verification>` block: `make test PYTEST_ARGS="tests/test_api.py tests/test_bench.py -q"` -- 73 passed; `make lint typecheck lint-imports no-fake-done` -- all clean; `git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json` -- clean (exit 0)
- Re-ran the tracer's own end-to-end check and Task 2's `<verify>` grep: both verdict lines present in `bench/RESULTS.md`'s new section (count 2)
- `git rev-list --count f7a5483..HEAD` = 2, matching `commits: 2` above
