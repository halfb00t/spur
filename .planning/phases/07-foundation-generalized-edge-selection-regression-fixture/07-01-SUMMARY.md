---
phase: 07-foundation-generalized-edge-selection-regression-fixture
plan: 01
subsystem: testing
tags: [pytest, cadquery, regression-fixture, L05]

# Dependency graph
requires: []
provides:
  - "tests/regression/pre_v0_2.json: 44 records (39 built, 5 mate-only) pinning derive()'s
    19 fields exactly and build()'s volume/bbox/face/edge counts for every pre-v0.2
    hand-written parameter set in tests/ and README.md"
  - "make fixture.regen: the sole writer of the fixture, rebuilding every corpus set on
    the working tree's code"
  - "A measured make verify cost for the fixture (16.27s delta) and a D-06 human decision
    to accept it, recorded in bench/RESULTS.md"
  - "A proven tripwire: a silently-vanished bore chamfer turns exactly the 32 affected
    solid cases red"
  - "A must-severity debt item naming the CI-kernel-vs-fixture-pin risk"
affects: ["07-02", "08", "09", "10", "11", "12"]

# Actuals (#2632)
actuals:
  tokens: 21851
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Corpus-to-fixture capture/replay pattern: a pure corpus module (Entry/Case/cases()),
      a capture script that is the sole writer of a checked-in JSON oracle, and a replay
      test module that only reads it — one pytest case per record, id = source tag"
    - "Provenance header on a captured oracle: git HEAD, src_clean, kernel versions,
      capture date, plus a stated regeneration policy — makes a kernel-driven mass-failure
      legible as one named test instead of dozens of unexplained mismatches"

key-files:
  created:
    - tests/regression/corpus.py
    - tests/regression/capture.py
    - tests/regression/pre_v0_2.json
    - tests/regression/test_pre_v0_2.py
    - docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md
  modified:
    - Makefile
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "D-06 gate: the fixture's measured make verify delta (16.27s, two runs each way,
    same session) came in above the plan's 15.0s line. Halted for a blocking
    checkpoint:decision naming the delta, the four pytest summary lines and the ten
    slowest cases. Human chose Option A: accept the cost and keep every one of the 44
    records built, reasoning that 16.27s sits under the ~20s ceiling the plan named,
    the cost is spread evenly across all 39 builds (no single outlier), and Success
    Metric 3 ('old links unchanged') stays literal rather than trimmed to a curated
    subset."

requirements-completed: [REQ-defaults-off-regression]

coverage:
  - id: D1
    description: "The L05 regression fixture pins derive()'s 19 fields and build()'s
      volume/bbox/face/edge counts for all 44 records (39 built, 5 mate-only) covering
      every pre-v0.2 hand-written parameter set"
    requirement: REQ-defaults-off-regression
    verification:
      - kind: integration
        ref: "make fixture.regen && make test PYTEST_ARGS=\"tests/regression -q\" (85 passed)"
        status: pass
      - kind: integration
        ref: "make verify (276 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Regeneration is byte-stable (sorted keys, indent 2, trailing newline)"
    verification:
      - kind: integration
        ref: "Task 2's cmp of two consecutive make fixture.regen runs"
        status: pass
    human_judgment: false
  - id: D3
    description: "The fixture is a real tripwire: a silently vanished bore chamfer turns
      exactly the 32 chamfered-bore solid cases red and no derive case"
    verification:
      - kind: integration
        ref: ".venv/bin/python -c \"...m._bore_rim_edges = lambda *a, **k: []...\" -> 32 failed, 53 passed"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-06 gate: the fixture's make verify cost is measured (two runs each
      way, same session) and recorded in bench/RESULTS.md, with a human decision on the
      above-15.0s delta rather than a silent subset"
    verification:
      - kind: manual_procedural
        ref: "bench/RESULTS.md, '## Regression fixture cost (Phase 7, D-06)'"
        status: pass
    human_judgment: true
    rationale: "D-06's own text requires a human decision when the delta exceeds the
      line — the checkpoint:decision resolution (Option A) is a judgment call by design,
      not something a test can auto-pass."
  - id: D5
    description: "A must-severity debt item names the CI-unpinned-kernel-vs-fixture-pin
      risk, filed with its INDEX row"
    verification:
      - kind: other
        ref: "grep -c 'Severity: must' docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md"
        status: pass
    human_judgment: false

duration: 39min
completed: 2026-09-26
status: complete
---

# Phase 7 Plan 1: Regression Fixture Summary

**44-record `pre_v0_2.json` oracle pinning derive() and build() output for every pre-v0.2 parameter set, captured by `make fixture.regen`, measured at a 16.27s `make verify` cost the human accepted, and proven to catch a silently vanished bore chamfer.**

## Performance

- **Duration:** 39 min (first commit `6f06d77` 05:49:05Z to metadata commit; spans one
  checkpoint pause for the D-06 decision, so wall-clock elapsed time is longer than
  executor busy time)
- **Started:** 2026-09-26T05:49:05Z (Task 1's commit)
- **Completed:** 2026-09-26T06:29:56Z
- **Tasks:** 3
- **Files modified:** 8 (5 created, 3 edited)

## Accomplishments

- `tests/regression/corpus.py`: the closed pre-v0.2 corpus — 78 source-tagged entries
  (README + six test files) deduplicating to 44 records (39 base, 5 mate) via `cases()`
- `tests/regression/capture.py`: the sole writer of the fixture, run only as
  `make fixture.regen`; captures `derive()`'s 19 fields and `build()`'s volume/bbox/
  face/edge counts plus a provenance header (git HEAD, src_clean, kernel versions,
  capture date)
- `tests/regression/pre_v0_2.json`: 44 records captured on unmodified pre-v0.2 code
  (HEAD `b3ca789`, `src_clean: true`), byte-stable across repeated regenerations
- `tests/regression/test_pre_v0_2.py`: one pytest case per record (id = source tag) plus
  a corpus-coverage test and a kernel-version test (Pitfall 11)
- Measured the fixture's cost to `make verify`: 16.27s delta, above the plan's 15.0s
  line — resolved via a `checkpoint:decision` where the human chose to accept the cost
  and keep every record built
- Proved the fixture is a real tripwire: monkeypatching `_bore_rim_edges` to return no
  edges turns exactly the 32 chamfered-bore solid cases red (`32 failed, 53 passed`),
  with `git status --porcelain -- src tests` clean afterwards
- Filed `docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md`
  (`must`): CI resolves `cadquery`/`cadquery-ocp` from an unpinned `pyproject.toml`
  range while the fixture pins one resolved kernel's exact topology

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end fixture for one set (the defaults)** - `6f06d77` (test)
2. **Task 2: Every pre-v0.2 set — the 78-entry corpus, 44 records** - `7cb4eb6` (test)
3. **Task 3: Measure make verify cost (D-06), prove the tripwire, file the kernel debt** - `87e8548` (docs)

**Plan metadata:** (this commit, following this SUMMARY)

## Files Created/Modified

- `tests/regression/corpus.py` - `Entry`/`Case` NamedTuples, 78-entry `ENTRIES`, `cases()`
- `tests/regression/capture.py` - `FIXTURE`, `Record`/`Fixture` TypedDicts, `derived()`,
  `solid()`, `provenance()`, `main()` — the only writer of `pre_v0_2.json`
- `tests/regression/pre_v0_2.json` - provenance header + 44 records
- `tests/regression/test_pre_v0_2.py` - four test functions replaying every record
- `Makefile` - new `fixture.regen` target and `.PHONY` entry
- `bench/RESULTS.md` - new `## Regression fixture cost (Phase 7, D-06)` section: host
  state, the four pytest summary lines, the 16.27s delta, the D-06 decision (Option A),
  the ten slowest cases, the `make verify` wall time (49.51s vs the 32.47s baseline),
  and the tripwire result
- `docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` - new
  `must` debt item
- `docs/tech_debt/INDEX.md` - new Active-table row for the debt item above

## Decisions Made

- **D-06 checkpoint resolution (Option A):** the measured `make verify` delta (16.27s,
  mean of two runs each way, same session, HEAD `7cb4eb6`) exceeded the plan's 15.0s
  line, which required a blocking `checkpoint:decision` rather than a silent trim
  (prohibition 2). The human accepted the cost, keeping all 44 records built, on the
  reasoning that: (1) 16.27s is under the planner's own ~20s ceiling for accepting the
  cost as-is; (2) the cost is spread across all 39 builds — the ten slowest cases differ
  by only 0.16s, no single outlier build could be dropped for a meaningful saving; (3)
  Success Metric 3 ("old links unchanged") means every pre-v0.2 set, not a curated
  subset — narrowing the corpus to save time would contradict the requirement the
  fixture exists to prove. No record was narrowed, dropped, marked slow, or given a
  loosened tolerance.

## Deviations from Plan

None - plan executed exactly as written. The one blocking checkpoint (D-06) was an
explicit, planned decision point (prohibition 2 forbids resolving it any other way), not
a deviation from the plan's instructions.

## Issues Encountered

None. The tripwire proof (Task 3 step 4) matched the plan's expected split exactly on
first run (`32 failed, 53 passed`), and `make verify` was green with no fix pass needed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The L05 regression fixture is in place and green under `make verify`: 07-02's
  bore-rim selector generalization (and every later v0.2 phase through 12) is checked
  against this fixture rather than an ad hoc check.
- The kernel-pin debt item is filed and will surface again automatically (its own named
  test fails loudly) if a future dependency resolve drifts from the fixture's kernel.
- `make fixture.regen` exists and is documented in `make help`; regenerating it outside
  its own stated-reason commit (D-03) is now the standing rule for Phases 8-12.

## Self-Check: PASSED

All 9 key files found on disk (4 created in tests/regression/, 1 debt item, 3 edited
docs/bench files, this SUMMARY). All 3 task commit hashes (`6f06d77`, `7cb4eb6`,
`87e8548`) found in `git log --oneline --all`. `make verify` re-run clean: 276 passed.

---
*Phase: 07-foundation-generalized-edge-selection-regression-fixture*
*Completed: 2026-09-26*
