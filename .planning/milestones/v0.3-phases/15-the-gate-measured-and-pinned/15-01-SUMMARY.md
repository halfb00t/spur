---
phase: 15-the-gate-measured-and-pinned
plan: 01
subsystem: testing
tags: [make-verify, pytest, pytest-xdist, pytest-cov, bench, profiling]

requires:
  - phase: 12-composition-pass
    provides: the D-10 measurement method (alternating full runs, load recorded) this plan applies without a quiet bar
provides:
  - "bench/RESULTS.md section '## The gate, measured and pinned (Phase 15)': host state, run recipe R1-R5, per-stage, per-file, slowest 25, xdist sweep"
  - "pytest-xdist>=3.8 and pytest-cov>=7.1 as [dev] extras only"
  - "apparent knee K = 8 for the xdist sweep (15-02 runs at K; the human picks N at 15-03)"
  - "planning record corrected: the bar is set at the profile checkpoint, not at discuss-phase (D-01)"
affects: [15-02, 15-03, 15-04, 15-05, 15-06]

actuals:
  tokens: 4100
  tasks: 3
  commits: 2
plan_head_before: 862a8075a543b6a813025e46262396c82056aefb
plan_head_after: 65ef9db1cd5f132119d28565d656f24ff8d1b7c2

tech-stack:
  added: [pytest-xdist 3.8.0, pytest-cov 7.1.0 (with coverage 7.16.2, execnet 2.1.2)]
  patterns:
    - "one run recipe (R1-R5) quoted verbatim in ### Method and reused for every Phase 15 row"
    - "knee rule written before the sweep numbers; the plan's verify recomputes it from the table"

key-files:
  created: []
  modified:
    - bench/RESULTS.md
    - pyproject.toml
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "Apparent knee is N = 8 (68.93 s): S12 (75.47 s) is within 1.10x but is the larger N, and is slower than S8"
  - "No bench/ script: the per-file awk and the RSS sampler live as committed prose in ### Method (RESEARCH Open Question 3)"
  - "REQUIREMENTS.md's introduction sentence 'set from the profile at discuss-phase' left as written: it records the kickoff choice, not what the phase does"

requirements-completed: [REQ-verify-profiled, REQ-verify-at-the-bar, REQ-coverage-floor]

coverage:
  - id: D1
    description: "Serial gate profiled per stage, per file and slowest 25 (two runs, P1 and P2, 927 passed each) into bench/RESULTS.md with host state and the reproducible run recipe"
    requirement: REQ-verify-profiled
    verification:
      - kind: other
        ref: "Task 1 automated check (python structure assert over the Phase 15 section) -> 'profile ok'"
        status: pass
    human_judgment: false
  - id: D2
    description: "pytest-xdist>=3.8 and pytest-cov>=7.1 installed as [dev] extras only; requirements.txt byte-identical to 20cd484; addopts unchanged"
    requirement: REQ-verify-at-the-bar
    verification:
      - kind: other
        ref: "Task 3 automated check (tomllib assert, git diff --quiet 20cd484 -- requirements.txt, pip show count 2) -> 'extras ok' / 2"
        status: pass
    human_judgment: false
  - id: D3
    description: "xdist sweep S2/S4/S8/S12 recorded with load, pytest line, wall, peak tree RSS and exit; knee rule stated before the table; Apparent knee N = 8"
    requirement: REQ-verify-profiled
    verification:
      - kind: other
        ref: "Task 3 automated check (recomputes the knee from the table) -> 'sweep ok, knee 8'"
        status: pass
    human_judgment: false
  - id: D4
    description: "REQ-verify-profiled acceptance and ROADMAP Phase 15 Depends-on / SC2 / Research flag say the bar is set at the profile checkpoint; milestone scope identical before and after"
    requirement: REQ-verify-profiled
    verification:
      - kind: other
        ref: "Task 3 automated checks -> 'D-01 sentences ok'; roadmap milestone-scope complete 13/14/15/16 before and after (cmp identical)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Package legitimacy of pytest-xdist and pytest-cov confirmed by the human before install"
    verification: []
    human_judgment: true
    rationale: "A trust decision about a PyPI package; automation cannot establish it, which is why the checkpoint is blocking-human. The answer is recorded below."

duration: 10h 41m wall (includes the wait at the Task 2 human checkpoint; active time not separately measured)
completed: 2026-10-04
status: complete
---

# Phase 15 Plan 01: The Gate, Profiled and Swept Summary

**The serial `make verify` costs 224 s (3.7 min), 99.8 % of it pytest and 74 % of that one file; `pytest-xdist -n 8` cuts it to 68.93 s at 5.6 GiB peak tree RSS, with an apparent knee at N = 8.**

## Performance

- **Duration:** 10h 41m wall (elapsed from 2026-10-03T16:53:46Z to 2026-10-04T03:35:28Z; mostly the pause at Task 2's blocking-human checkpoint)
- **Started:** 2026-10-03T16:53:46Z
- **Completed:** 2026-10-04T03:35:28Z
- **Tasks:** 3 (Task 2 is the human checkpoint)
- **Files modified:** 5 (`bench/RESULTS.md`, `pyproject.toml`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`)

## Accomplishments

- Two serial profile runs on an Apple M2 Max (12 CPUs, 32.0 GiB), HEAD `862a807`, code identical to `20cd484`:

  | Run | Load | pytest | Wall (s) | Peak tree RSS (MiB, procs) |
  |---|---|---|---|---|
  | P1 | 6.53 | 927 passed in 229.15s | 230.20 | 1396 (6) |
  | P2 | 9.09 | 927 passed in 217.59s | 218.36 | 1390 (5) |

  Mean wall 224.28 s. user+sys over real was 4.2 cores (P1) and 4.5 (P2), so the serial gate is already multi-core.
- Per-stage table (P1 / P2, seconds): ruff 0.07 / 0.03, mypy 0.37 / 0.20, import-linter 0.11 / 0.09, unfinished-work scan 0.02 / 0.01, pytest 229.63 / 218.03 (its own reading 229.15 / 217.59), whole gate 230.20 / 218.36. Pytest is 99.75 % / 99.85 % of the gate; nothing outside the test suite is worth cutting.
- Top three files by share of pytest time (P1 / P2 per-file sums): `tests/test_model.py` 74.1 % / 73.3 % (167.76 s, 201 items), `tests/test_pool.py` 8.5 % / 8.3 % (19.29 s, 16 items), `tests/regression/test_pre_v0_2.py` 7.8 % / 7.9 % (17.58 s, 85 items). 18 of the slowest 25 phases are in `test_model.py` (twelve tip-chamfer-with-each-cutout-on-each-bore rows alone take 28.9 s), 5 in `test_pool.py`, 2 in `test_cli.py`.
- xdist sweep, all four rows green (rule fixed before the numbers: smallest N within 1.10x of the fastest green wall):

  | Run | N | Load | pytest | Wall (s) | Peak RSS (MiB, procs) | Exit |
  |---|---|---|---|---|---|---|
  | S2 | 2 | 2.29 | 927 passed in 128.45s | 130.72 | 2226 (8) | 0 |
  | S4 | 4 | 9.33 | 927 passed in 84.02s | 84.76 | 3969 (11) | 0 |
  | S8 | 8 | 17.07 | 927 passed in 67.95s | 68.93 | 5649 (17) | 0 |
  | S12 | 12 | 28.01 | 927 passed in 74.21s | 75.47 | 7880 (22) | 0 |

  **Apparent knee: N = 8** (68.93 s against the fastest 68.93 s at N = 8). Speed-ups against the serial mean: 1.72x, 2.65x, 3.25x, 2.97x (sublinear, Pitfall 9). S12 is slower than S8 by 6.54 s; oversubscription (12 workers plus the controller on 12 CPUs) is a likely cause but was not tested here. User time stays near 340 s at every N while sys time falls from 507.65 s (N = 2) to 106.30 s (N = 12), against 616.20 / 629.40 s serial.
- No red row: no shared-state site (`tests/test_pool.py`, `tests/test_api.py`, `tests/test_records.py`) failed at any N, so 15-02's `xdist_group` response has no failing node id to inherit from this sweep. 15-02 still owns settling that tolerance with coverage on.
- `pytest-xdist>=3.8` and `pytest-cov>=7.1` added to `[dev]` only (installed: pytest-xdist 3.8.0, pytest-cov 7.1.0, with coverage 7.16.2 and execnet 2.1.2); `requirements.txt` byte-identical to `20cd484`, `addopts` unchanged.
- D-01: the planning record now says the bar is set at the phase's profile checkpoint (diffs below).

## Task Commits

1. **Task 1: tracer, the serial gate profiled end to end** - `39eb062` (docs)
2. **Task 2: human confirms pytest-xdist and pytest-cov are the pytest-dev packages** - no commit (checkpoint). **Human's answer, verbatim: `approved`**
3. **Task 3: dev extras, sweep, knee, D-01 sentences** - `65ef9db` (build); the D-01 planning-record edits ride the closing commit below, per the plan

**Plan metadata:** the closing `docs(15-01): say the bar is set at the profile checkpoint, not at discuss-phase` commit (this SUMMARY, REQUIREMENTS.md, ROADMAP.md, STATE.md). The frontmatter `commits: 2` is measured from the plan ledger (`862a807..65ef9db`) and counts the two task commits, not the closing commit.

Both task commits ran the pre-commit hook's full `make verify` (serial: `addopts` is unchanged) and passed.

## Files Created/Modified

- `bench/RESULTS.md` - new section `## The gate, measured and pinned (Phase 15)`: Host state, Method (R1-R5, sampler awk, per-file awk), Per-stage wall time, Per-file share, Slowest 25, xdist sweep
- `pyproject.toml` - two `[dev]` extras after `"pre-commit>=4",`
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` - D-01 sentence corrections
- `.planning/STATE.md` - position, metric, decision, session, Roadmap Evolution line

## D-01 planning-record diffs

REQUIREMENTS.md, REQ-verify-profiled acceptance:

```diff
-  the table and the proposal list exist in `bench/RESULTS.md`; the human sets the bar from
-  them at discuss-phase and it is recorded in that phase's CONTEXT. This requirement is
+  the table and the proposal list exist in `bench/RESULTS.md`; the human sets the bar from
+  them at the phase's profile checkpoint (15-CONTEXT.md D-01; the profile is the phase's
+  own first deliverable) and it is recorded in that phase's CONTEXT. This requirement is
```

ROADMAP.md, Phase 15 section (scoped Edits; `roadmap milestone-scope` before and after identical: scope complete, phases 13, 14, 15, 16; one Roadmap Evolution line added):

```diff
-before `REQ-verify-at-the-bar` (the bar is set from it at this phase's discuss-phase) and
+before `REQ-verify-at-the-bar` (the bar is set from it at this phase's profile checkpoint,
+15-CONTEXT.md D-01) and
-  2. The bar the human sets at this phase's discuss-phase from the profile (recorded in
-     that phase's CONTEXT) is read at or under, measured the same way; the before/after rows
+  2. The bar the human sets at this phase's profile checkpoint from the profile (recorded in
+     this phase's CONTEXT as a dated addendum under D-01) is read at or under, measured the
+     same way; the before/after rows
-from the profile at this phase's discuss-phase, not before.
+from the profile at this phase's profile checkpoint (15-CONTEXT.md D-01), not before.
```

SC4's "at this phase's discuss-phase" is true (D-13 was picked there) and is 15-05's to amend. REQUIREMENTS.md's introduction sentence is left as written (see the plan's Flagged Assumptions).

## Decisions Made

- The apparent knee is N = 8; this is a recommendation of the pre-registered rule, not a choice. The human picks N at 15-03.
- The per-file and RSS readings stand on committed commands in `### Method` plus the `make verify` target; no `bench/` script (RESEARCH Open Question 3).

## Deviations from Plan

None - plan executed exactly as written.

The plan's `estimate.tokens` was 70000; the realized diff measures about 4100 on the same chars/4 scale (16.3 kB of added text). The estimate counted reading and reasoning, not the diff, so it overstates by an order of magnitude when read as diff size.

## Issues Encountered

- Load figures for S4, S8 and S12 (9.33, 17.07, 28.01) are mostly the previous sweep row's own tail, because the rows ran back to back and the 1-minute average lags. They are recorded as read, per D-04; the order and loads are in the table so a reader can weigh them. S2 started at a quiet 2.29.
- Between Task 1 and Task 3 the working tree carried GSD tooling state (`.planning/state.json`, `.planning/milestone.lock`) from the orchestrator's phase-start write. The pre-commit hook stashed and restored it around both task commits without incident. The closing commit stages them only if still dirty (see the final commit).
- Time spent: the wall duration above is dominated by the human-checkpoint wait, not by work.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 15-02 can run its coverage baseline at the sweep's knee K = 8 (or at the N the sweep rows show it should use); it owns the `BuildPool` worker-coverage settlement and any `xdist_group` response, and has no red node id from this sweep.
- 15-03's checkpoint has the profile table, the per-file shares and the sweep rows to set the bar and pick N from.
- Concern for 15-02: coverage with `concurrency = ["multiprocessing", "thread"]` is untested; the sweep ran without `--cov`.

## Known Stubs

None.

## Threat Flags

None. The two new packages are `[dev]` only (T-15-02, T-15-SC mitigated: human confirmation `approved` before install; `requirements.txt` and `[project] dependencies` untouched).

## TDD Gate Compliance

Not applicable (plan type `execute`, not `tdd`).

## Self-Check: PASSED

- `bench/RESULTS.md`, `pyproject.toml`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`: FOUND
- Commits `39eb062` and `65ef9db`: FOUND
- Task 3 automated checks: extras ok (pip show count 2), sweep ok / knee 8, D-01 sentences ok, milestone scope complete 13/14/15/16, D-20 ok

---
*Phase: 15-the-gate-measured-and-pinned*
*Completed: 2026-10-04*
