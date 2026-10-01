---
phase: 12-composition-pass
plan: 03
subsystem: infra
tags: [bench, build-time, spoke-count, tech-debt, timeout-gate]

# Dependency graph
requires:
  - phase: 12-composition-pass
    provides: "12-02-SUMMARY.md: the 18-row composed sweep and two non-decisive runs; 12-CONTEXT.md D-02, D-03, D-04, D-05"
provides:
  - "D-03's gate run to a decision: spoke_count's `le` lowered 40 -> 32, the largest count the composed sweep measures inside SPUR_BUILD_TIMEOUT=30s on the heaviest composed row"
  - "bench/RESULTS.md's Composed section closed out: Run 3 and Run 4 (the two further quiet re-runs D-02 asked for), the D-02 supersession recorded as a decision, the Gate probe, the Gate decision, and the post-gate re-run -- every composed row now inside 30 s (heaviest 29.42 s)"
  - "Both build-timeout debts this sweep triggered resolved with the measured number and the decision (D-05); the tip-chamfer debt's concurrent-load question re-homed into the waived-latency debt (D-04)"
affects: [12-04-export-cost, 12-09-milestone-record]

# Actuals (#2632)
actuals:
  tokens: 14507
  tasks: 3
  commits: 8
  plan_head_before: 2207912
  plan_head_after: 359f8db

# Tech tracking
tech-stack:
  added: []
  patterns: ["bench/build_time.py's report() reads os.getloadavg() before the first row builds, not after the last -- fixed pre-Task-1 as a deviation so 'Load averages at start' means what it says for every run from Run 3 onward"]

key-files:
  created: []
  modified:
    - bench/RESULTS.md
    - src/spur/params.py
    - bench/sweeps/composed.json
    - bench/sweeps/spoke_cutout.json
    - bench/build_time.py
    - tests/test_calc.py
    - tests/test_api.py
    - tests/test_bench.py
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md
    - docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md
    - docs/tech_debt/resolved/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md

key-decisions:
  - "Human answer 1 (orchestrator checkpoint before Task 1, doc-vs-code conflict on D-02's \"Load averages at start\"): \"Fix runner, then 12-03 (Recommended)\" -- bench/build_time.py's report() now reads os.getloadavg() before the first row builds (9b9af43)."
  - "Human answer 2 (Task 2, first ask, after Task 1 found no decisive run): \"quiet-rerun\" -- Run 3 taken (2.74 at start, not decisive)."
  - "Human answer 3 (Task 2, second ask, after Run 3 non-decisive): \"quiet-rerun, I'll step away (Recommended)\" -- Run 4 taken (1.54 at start, not decisive by D-02's letter)."
  - "Human answer 4 (Task 2, third ask, after Run 4 also non-decisive): \"Supersede D-02: treat Run 4 as decisive (Recommended)\" -- D-02's <1.5 bar superseded for this gate on the measured load-independence of four runs (at-start loads 1.54-12.66, the same four rows over budget in every one, quietest runs not the fastest); Run 4 is the reference run."
  - "Human answer 5 (Task 2, fourth ask, after D-03's probe on Run 4's heaviest row): \"lower-le: spoke_count 32 (Recommended)\" -- the probe's own offer (32 measured inside budget at 29.41 s, 33 over at 30.11 s)."
  - "spoke_count's `le` lowered 40 -> 32 in src/spur/params.py (547214e); the two sweep files' spoke_count=40 rows moved to 32 (40 is no longer valid); the whole composed sweep re-run confirms every row inside 30 s at the new le (heaviest 29.42 s, the same module=10 keyed-bore spokes+tip_chamfer=3 row that was over budget at 40)."
  - "RED and GREEN for the spoke_count le change landed in one feat commit (547214e), not separate test(...)/feat(...) commits -- workflow.tdd_mode is not enabled in .planning/config.json, so the mechanical RED/GREEN/REFACTOR commit-pattern gate does not apply (08-03/11-03/12-02's precedent). RED was confirmed failing (4 tests, genuine assertion failures against the still-le-40 params.py and sweep files) before GREEN was written; the project's own pre-commit make verify hook blocks a commit with any failing test, which is why the RED-only commit attempt itself failed and the combined commit is the only legal shape here."
  - "Both build-timeout debts resolved (D-05): docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md and docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md, each with a Resolution section citing the composed row's measured number, the arithmetic total it replaced, and the decision; moved to docs/tech_debt/resolved/ in 89304e2, sha recorded in 359f8db per 09-03's precedent (a file cannot carry its own commit's sha)."
  - "D-04: the tip-chamfer debt's unanswered concurrent-load question re-homed as one added trigger sentence in docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md and its INDEX row (89304e2), citing 12-CONTEXT.md D-04."
  - "decision_log.md and 12-CONTEXT.md were not edited (out of this plan's files_modified list) -- 12-09 owns the phase's L31 entry and will cite this plan's record and SUMMARY for the D-02 supersession and the spoke_count le change."

patterns-established: []

requirements-completed: [REQ-measured-build-time]

coverage:
  - id: D1
    description: "D-03's gate probe measures the first offer's number: on the still-no-decisive-run record (Task 1's first pass) the section states plainly no probe was needed; once Run 4 was accepted as decisive (D-02 superseded), a second Task 1 pass probes the module=10 keyed-bore spokes+tip_chamfer=3 row and finds spoke_count 32 the largest count inside 30 s (29.41 s), 33 over again (30.11 s)"
    requirement: "REQ-measured-build-time"
    verification:
      - kind: other
        ref: "bench/RESULTS.md 'Composed build and export time (Phase 12)' section: '### Gate probe' verbatim probe table (five rows, spoke_count 30-35, each with sysctl and runner load readings) and its Offer line"
        status: pass
    human_judgment: false
  - id: D2
    description: "The human decided the gate's outcome across four checkpoint rounds: fix the runner first, two further quiet re-runs, superseding D-02 for this gate on Run 4's load-independence, and finally the probe's own offer (\"lower-le: spoke_count 32\")"
    requirement: "REQ-measured-build-time"
    verification: []
    human_judgment: true
    rationale: "The human's own words are the artifact being verified -- no automated check proves a transcription is verbatim; all five answers are recorded above and in this SUMMARY's Deviations/Decisions sections for a reader to compare against the checkpoint transcript."
  - id: D3
    description: "The chosen limit (spoke_count le 40 -> 32) is applied with its tests (RED confirmed failing, GREEN passing), every affected sweep row updated, and the whole composed sweep re-run on a quiet-per-the-superseded-gate host confirms every row now inside SPUR_BUILD_TIMEOUT=30s (heaviest 29.42 s)"
    requirement: "REQ-measured-build-time"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_the_spoke_count_is_an_integer_from_0_to_32"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_spoke_link_is_served_with_the_fillet_it_cut (schema maximum == 32)"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_the_composed_sweep_stacks_each_cutout_on_its_heaviest_bore_beside_six_baselines"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_the_spoke_cutout_sweep_is_every_combination_the_plan_names"
        status: pass
      - kind: other
        ref: "bench/RESULTS.md '### Re-run after the gate (lower-le: spoke_count 32)': full 18-row table, all 'yes' in Inside 30 s, Heaviest 29.42 s of 30 s"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both build-timeout debts this sweep triggered are resolved with the composed row's measured number and the decision, moved to docs/tech_debt/resolved/ with sha-recorded Resolved in: fields; the tip-chamfer debt's concurrent-load question is re-homed into the waived-latency debt's trigger, not dropped"
    requirement: "REQ-measured-build-time"
    verification:
      - kind: other
        ref: "for f in 2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md 2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md: ls docs/tech_debt/active/$f docs/tech_debt/resolved/$f; grep -c \"$f\" docs/tech_debt/INDEX.md -- each file exists in resolved/ only, INDEX count 1"
        status: pass
      - kind: other
        ref: "grep -cE '^Resolved in: [0-9a-f]{7,}' on both resolved files -- 1 each, sha 89304e2"
        status: pass
      - kind: other
        ref: "grep -c '12-CONTEXT.md D-04' docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md -- 1"
        status: pass
    human_judgment: false

# Metrics
duration: ~40min (this continuation session, Task 3 only; Task 1's two passes and Task 2's four checkpoint rounds ran across earlier sessions)
completed: 2026-09-30
status: complete
---

# Phase 12 Plan 03: Composed Sweep Timeout Gate Summary

**`spoke_count`'s schema maximum lowered from 40 to 32 -- the largest count the real composed build (spokes + tip chamfer + both recesses) measures inside `SPUR_BUILD_TIMEOUT`=30s on Run 4, the run D-02 was superseded to treat as decisive -- closing both build-timeout debts Phase 12's composed sweep exists to answer.**

## Performance

- **Duration:** ~40 min (this continuation session, Task 3 only, from the "human decided the gate" checkpoint to plan completion)
- **Started:** 2026-09-30T09:26Z (approx, this session's first tool call)
- **Completed:** 2026-09-30T10:10Z (approx)
- **Tasks:** 3 (1 auto/probe, 1 checkpoint:decision, 1 auto/tdd) -- Task 1 ran twice (no-decisive-run pass, then the decisive-run probe pass) and Task 2 ran four times (one runner-fix checkpoint before Task 1, three gate checkpoints) across this plan's full, multi-session history
- **Files modified this session:** 12 (0 created, 12 modified/moved)

## Accomplishments

- D-02's own bar (<1.5 at the runner's genuine start) never resolved cleanly across four full composed-sweep runs (loads 12.66, 7.04, 2.74, 1.54 at start) -- the human superseded it for this one gate on the measured fact that the same four `spoke_count=40` rows read over budget in every run, within a roughly 2 s band that did not track the load figure, and named Run 4 (the closest to quiet) the reference run
- D-03's probe measured the first offer directly on Run 4's heaviest composed row (module=10, keyed bore, `tip_chamfer=3`, both recesses): `spoke_count` 32 is the largest count that still builds inside 30 s (29.41 s), 33 reads over again (30.11 s)
- The human chose the probe's own offer; `spoke_count`'s `le` moved from 40 to 32 in `src/spur/params.py`, with tests (RED confirmed failing, then GREEN) and both affected sweep files (`bench/sweeps/composed.json`, `bench/sweeps/spoke_cutout.json`) updated
- The whole composed sweep was re-run at the new `le` on a host that never settled under 1.5 within the human's own 5-minute cap for this gate (1.68 at the runner's genuine start) -- every one of the 18 rows now reads inside 30 s, heaviest 29.42 s (0.58 s of margin), the same pattern that was over budget at `spoke_count=40`
- Both build-timeout debts this sweep exists to close (`2026-09-28-tip-chamfer-...`, `2026-09-29-spoke-le-...`) are resolved with the composed row's measured number and the decision, moved to `docs/tech_debt/resolved/`; the tip-chamfer debt's own unanswered concurrent-load question is re-homed, not dropped, into `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`'s trigger

## Task Commits

Every task was committed atomically; this plan spans eight commits across its full history (Task 1's two passes, Task 2's checkpoints producing no code commits of their own, and Task 3's three commits this session):

1. **Pre-Task-1 deviation: fix `report()`'s load-averages timing (Human answer 1)** - `9b9af43` (fix)
2. **Task 1 (first pass): no decisive run on record -- no probe** - `238b6cc` (docs)
3. **Task 2 checkpoint, first re-ask: quiet re-run (Human answer 2)** - `ea31799` (docs, Run 3)
4. **Task 2 checkpoint, second re-ask: quiet re-run, human steps away (Human answer 3)** - `083b312` (docs, Run 4)
5. **Task 1 (second pass): probe D-03's first offer against Run 4 (post-supersession, Human answer 4)** - `98743ab` (docs)
6. **Task 3: apply the chosen le (Human answer 5), RED+GREEN together** - `547214e` (feat)
7. **Task 3: re-run the composed sweep, record the gate decision, resolve both debts** - `89304e2` (docs)
8. **Task 3: record the gate commit's sha in the resolved debt records** - `359f8db` (docs)

**Plan metadata:** committed separately (see below)

_Task 3 carried `tdd="true"`; RED (tests written first, confirmed failing on the still-le-40 params.py and sweep files -- four genuine assertion failures, see this session's transcript) and GREEN landed in one `feat` commit (547214e), not separate `test(...)`/`feat(...)` commits -- `workflow.tdd_mode` is not enabled in `.planning/config.json`, so the mechanical RED/GREEN/REFACTOR commit-pattern gate does not apply (08-03/11-03/12-02's precedent). This project's own pre-commit `make verify` hook blocks any commit with a failing test, so a RED-only commit is not achievable here regardless; RED was run and confirmed failing (both directly via `make test` and by the hook's own rejection of the attempted RED-only commit) before GREEN was written._

## Files Created/Modified

- `src/spur/params.py` -- `spoke_count`'s `le` lowered 40 -> 32; comment extended with D-03's measurement (Run 4's composed row at 32.03 s of 30 s at 40 arms, the probe's 32/33 boundary)
- `bench/sweeps/composed.json`, `bench/sweeps/spoke_cutout.json` -- every `spoke_count=40` row moved to 32 (40 is no longer a valid value)
- `tests/test_calc.py`, `tests/test_api.py`, `tests/test_bench.py` -- the bound test renamed/rewritten, the schema maximum, and both sweeps' pinned `want` values updated to 32
- `bench/build_time.py` -- `report()` reads `os.getloadavg()` before the first row builds, not after the last (pre-Task-1 deviation, Human answer 1)
- `bench/RESULTS.md` -- Run 3 and Run 4 (further quiet re-runs), `### Against the single-feature baselines` and `### SPUR_BUILD_TIMEOUT margin` filled in against Run 4, `### Gate` (the four over-budget rows plus the D-02 supersession paragraph), `### Gate probe` (both the no-probe-needed pass and the decisive-run probe table), `### Re-run after the gate (lower-le: spoke_count 32)` (the whole 18-row re-run), `### Gate decision` (the human's verbatim answer, what was applied, the numbers it rests on) -- all append-only, zero deletions against `c9a169d`
- `docs/tech_debt/INDEX.md` -- the two build-timeout Active rows moved to Resolved (sha `89304e2`); the concurrent-latency debt's trigger cell gained the D-04 sentence
- `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` -- "Revisit when:" gained one added trigger sentence re-homing the tip-chamfer debt's concurrent-load question (D-04)
- `docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md`, `docs/tech_debt/resolved/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md` -- `git mv`d from `active/`, `Status: resolved`, `Resolved in: 89304e2`, each with a `## Resolution (2026-09-30)` section citing the composed row's measured number, the arithmetic total it replaced, and the decision

## Decisions Made

See `key-decisions` in the frontmatter for all five human answers verbatim, plus the RED/GREEN commit-combination and debt-resolution decisions.

## Deviations from Plan

None - plan executed exactly as written for the `lower-le` branch of Task 3's `<action>`. The RED-then-GREEN-in-one-commit shape is not a deviation: it is this project's established precedent (08-03, 11-03, 12-02) for when `workflow.tdd_mode` is disabled, and it is additionally the only shape this project's own pre-commit `make verify` hook permits, since the hook runs the full test suite and blocks any commit -- including an intentional RED commit -- that leaves a test failing.

## Issues Encountered

- The first attempt to commit the RED tests alone (before implementing the `le` change) failed: the pre-commit hook's `make verify` ran the full suite, found the four intentionally-failing RED tests, and blocked the commit (`make: *** [Makefile:70: test] Error 1`). This is expected behaviour given the hook's design, not a bug -- resolved by implementing GREEN immediately after confirming RED via a direct `make test` run (not via a commit attempt) and committing RED+GREEN together, per this project's own established precedent.
- The host's 1-minute load average never settled under 1.5 during either wait this session (composed-sweep re-run wait: 4.41 falling to 1.53 across a 5-minute cap; the runner's own genuine at-start reading came in at 1.68). Per the human's D-02 supersession for this gate, the wait was capped at 5 minutes (not 30) and the re-run launched once the cap expired -- both readings recorded honestly (L08), not treated as a fresh gate trigger.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `REQ-measured-build-time` stays open in `REQUIREMENTS.md` (shared with 12-04, 12-09 per the shared-ID gate, #2388) -- marks complete only once the last declaring plan finishes
- 12-04 (export cost) and 12-09 (milestone record) can cite this plan's D-02 supersession and the `spoke_count` le change directly from `bench/RESULTS.md`'s `### Gate` and `### Gate decision` sections and this SUMMARY; 12-09 owns writing the phase's `Lxx` decision-log entry for both
- `make verify`: 627 passed (full suite, run before the Task 3 gate-decision commit) -- green, no regressions; `make lint typecheck` and the plan's own `<verification>` block all pass
- No blockers

---
*Phase: 12-composition-pass*
*Completed: 2026-09-30*

## Self-Check: PASSED

- FOUND: `src/spur/params.py` (modified, `spoke_count` le lowered to 32)
- FOUND: `bench/RESULTS.md` (modified, Gate/Gate probe/Re-run/Gate decision sections)
- FOUND: `docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md`
- FOUND: `docs/tech_debt/resolved/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`
- CONFIRMED GONE from `active/`: both debt files (moved, not duplicated)
- FOUND: commit `9b9af43` in `git log --oneline --all`
- FOUND: commit `238b6cc` in `git log --oneline --all`
- FOUND: commit `ea31799` in `git log --oneline --all`
- FOUND: commit `083b312` in `git log --oneline --all`
- FOUND: commit `98743ab` in `git log --oneline --all`
- FOUND: commit `547214e` in `git log --oneline --all`
- FOUND: commit `89304e2` in `git log --oneline --all`
- FOUND: commit `359f8db` in `git log --oneline --all`
- Re-ran the plan's own `<verification>` block: `make test PYTEST_ARGS="tests/test_calc.py tests/test_api.py tests/test_bench.py tests/regression -q"` -- 310 passed; `git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json` -- clean (exit 0); `make lint typecheck` -- both clean
- `git rev-list --count 2207912..HEAD` = 8, matching `commits: 8` above
