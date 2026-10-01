---
phase: 08-hex-bore
plan: 04
subsystem: infra
tags: [bench, hex-bore, decision-log, tech-debt, make-verify]

# Dependency graph
requires:
  - phase: 08-hex-bore
    provides: "08-02's hex bore field and hex geometry (bore_rim_limit/bore_mouth_limit hex branches); 08-03's calc.check() hex refusals and D-02 ignored-field warning"
provides:
  - "bench/build_time.py: a reusable build/fine-STL/STEP timing sweep behind make bench.build, taking its parameter sets from a JSON file (SWEEP=), reused unchanged by Phases 9-12 (D-12)"
  - "bench/sweeps/hex_bore.json: D-11's 16-row cross product at 200 teeth (module x bore_hex x recess_sides x bore_chamfer)"
  - "bench/RESULTS.md 'Hex bore build and export time (Phase 8, D-11)': every row measured inside SPUR_BUILD_TIMEOUT=30s, heaviest named, host state with load caveat, make verify wall time"
  - "docs/architecture/decision_log.md L27: the phase's decisions, appended, never editing L01-L26"
  - "the round bore's unchecked chamfer-reach gap filed as must-severity debt (docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md)"
affects: []

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 7747
  tasks: 3
  commits: 4
  plan_head_before: 69aac226eba13b1a83d1b7f42ac60ffec98e6bc7

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "bench.build_time.py's Timing.worst_request = build + max(stl, step): SPUR_BUILD_TIMEOUT wraps one worker call, and a cold request builds once then exports once, so build plus the slower single export -- never both exports summed -- is the number that must fit"
    - "A bench script that times spur.model in-process (no service, no Docker) joins bench.latency/bench.memory's family but needs neither's setup, because it exercises the exact code a worker runs directly"

key-files:
  created:
    - bench/build_time.py
    - bench/sweeps/hex_bore.json
    - docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md
  modified:
    - Makefile
    - tests/test_bench.py
    - bench/RESULTS.md
    - docs/architecture/decision_log.md
    - docs/architecture/gear-maths/implementation.md
    - docs/architecture/solid-model/tactics.md
    - tests/regression/capture.py
    - docs/tech_debt/INDEX.md

key-decisions:
  - "L27 appended: the field (D-07/D-08), replaces-never-refuses (D-01/D-02), the derived numbers (D-04/D-05/D-06), the measured root-circle limits (D-03), and the measurement (D-11/D-12) -- one entry, decision_log.md stayed append-only throughout (0 deleted lines since 540f1a0)."
  - "The round bore's own unchecked chamfer-reach gap (check()'s round branch compares bore_radius(p), not bore_mouth_limit(p)) is filed as must-severity debt rather than fixed here: a fix would refuse round links that build today, an L05 concern out of this phase's scope."
  - "The sweep ran clean on the first attempt (heaviest row 5.08s of 30s) -- the D-11 gate never fired, so no checkpoint:decision was needed."

patterns-established:
  - "bench.build_time.py's report() shape (host-state bullets, a Markdown table, a bolded Heaviest line) is the one Phases 9-12 paste into their own bench/RESULTS.md sections unchanged."

requirements-completed: [REQ-hex-bore, REQ-derived-dimensions-additive]

coverage:
  - id: D1
    description: "make bench.build times build, fine-STL and STEP export per parameter set from a committed sweep file, prints a Markdown row with the verdict against SPUR_BUILD_TIMEOUT, names the heaviest set, and exits 1 if any set is over budget"
    requirement: "REQ-hex-bore"
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_a_set_is_inside_the_timeout_until_its_build_plus_slower_export_passes_it"
        status: pass
      - kind: integration
        ref: "make bench.build SWEEP=<one-set file> (verified manually, one-row grep match)"
        status: pass
    human_judgment: false
  - id: D2
    description: "bench/sweeps/hex_bore.json is D-11's exact 16-row cross product at 200 teeth (module x bore_hex x recess_sides x bore_chamfer), every row a buildable gear"
    requirement: "REQ-hex-bore"
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_hex_bore_sweep_is_every_combination_d_11_names"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every sweep row measured inside SPUR_BUILD_TIMEOUT=30s (heaviest 5.08s), recorded in bench/RESULTS.md with host state, load-average caveat, and the make verify wall-time delta"
    requirement: "REQ-hex-bore"
    verification:
      - kind: manual_procedural
        ref: "make bench.build (full run, exit 0); bench/RESULTS.md 'Hex bore build and export time (Phase 8, D-11)'"
        status: pass
    human_judgment: true
    rationale: "A live timing run against real hardware load -- no test asserts wall-clock numbers (they would flap), so the recorded row values and the D-11 gate's non-firing are a human-legible measurement, not a pass/fail assertion."
  - id: D4
    description: "L27 appended to decision_log.md (append-only, 0 deleted lines since 540f1a0), recording D-01/D-02 supersession, D-04/D-05 derived numbers, D-03's measured root-circle bounds, and D-11's heaviest row"
    requirement: "REQ-derived-dimensions-additive"
    verification:
      - kind: other
        ref: "git diff --numstat 540f1a0 -- docs/architecture/decision_log.md (0 deletions); grep -c '^## L27 — '"
        status: pass
    human_judgment: false
  - id: D5
    description: "The round bore's unchecked chamfer-reach gap is filed as must-severity debt with an INDEX.md row, not fixed silently"
    requirement: "REQ-hex-bore"
    verification:
      - kind: other
        ref: "docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md (Severity: must); docs/tech_debt/INDEX.md row"
        status: pass
    human_judgment: false
  - id: D6
    description: "make verify is green at the end of the phase"
    requirement: "REQ-hex-bore"
    verification:
      - kind: other
        ref: "make verify: 330 passed in 60.90s"
        status: pass
    human_judgment: false

duration: 70min
completed: 2026-09-26
status: complete
---

# Phase 8 Plan 04: Bench the Hex Bore's Heaviest Cost, Log L27, and File the Round-Bore Gap Summary

**`make bench.build` times build/fine-STL/STEP per set from a reusable sweep file; the hex bore's heaviest allowed configuration costs 5.08s of a 30s budget, and L27 plus one filed debt item close out the phase.**

## Performance

- **Duration:** ~70 min
- **Tasks:** 3
- **Files modified:** 11 (3 created, 8 modified)

## Accomplishments

- `bench/build_time.py` (new): `Timing` (`worst_request = build + max(stl, step)`, `inside(timeout)`), `load_sweep`, `time_set`, `report`, `main` — a committed, reusable timing harness behind `make bench.build`, taking its parameter sets from `SWEEP=` (default `bench/sweeps/hex_bore.json`), with no dependency on a running service or Docker.
- `bench/sweeps/hex_bore.json` (new): D-11's 16-row cross product at 200 teeth (module {1.75, 10} x `bore_hex` {200, 12.7} x `recess_sides` {both, none} x `bore_chamfer` {0.4, 3}), pinned by a new exact-match test.
- The full sweep ran clean: every row inside `SPUR_BUILD_TIMEOUT=30s`; heaviest row `teeth=200 module=1.75 bore_hex=200 recess_sides=both bore_chamfer=0.4` at **5.08s** (build 4.44s, fine STL 0.64s, STEP 0.40s) — under a sixth of the budget, and below the worst single build already on record (7.39s). The D-11 checkpoint gate never fired.
- `bench/RESULTS.md` "Hex bore build and export time (Phase 8, D-11)" section: full 16-row table, host state with the load-average caveat (this session's host sat at 3.47/3.12/2.67 by the script's own reading, 4.78/3.23/2.68 by `uptime` — both above the project's 1.5 "quiet" bar), and `make verify` wall time (330 passed in 60.90s, 61.63s total, vs. Phase 7's 52.25s/289 tests).
- `docs/architecture/decision_log.md` L27 appended (append-only; 0 deleted lines since `540f1a0`), recording the field, the replaces-never-refuses rule, the two derived hex fields, D-03's measured root-circle bounds (24.2/24.15mm corner boundary, 23.4/23.35mm chamfered-corner boundary), and D-11's heaviest row.
- Architecture docs kept true: `implementation.md` gained rows for `hex_across_flats(p)`, `bore_rim_limit(p)`, `bore_mouth_limit(p)`; `tactics.md`'s pipeline diagram now says "circle, D or hex" and names the hex's corners in Edge re-selection; `tests/regression/capture.py`'s `derived()` docstring now says a record's fields must read `null` for anything added since capture.
- Filed `docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md` (Severity: must) for the pre-existing gap where a round bore's chamfer reach is never checked against the root circle — measured on 19 and 40 teeth at chamfers of 0.4, 1 and 2mm; not fixed here per L05 (a fix would refuse links that build today). INDEX.md row added in the same commit.
- `make verify`: **330 passed in 60.90s**, 61.63s wall time — the phase's final gate, green.

## Task Commits

Each task was committed atomically:

1. **Task 1: One sweep row end to end** - `a3a651b` (feat) — `bench/build_time.py`, `bench/sweeps/hex_bore.json`, `Makefile`, `tests/test_bench.py`
2. **Task 2: Run D-11's sweep and record every row** - `6f0cd1f` (docs) — `bench/RESULTS.md`
3. **Task 3, commit A: Log L27, keep architecture docs true** - `ac28b62` (docs) — `docs/architecture/decision_log.md`, `docs/architecture/gear-maths/implementation.md`, `docs/architecture/solid-model/tactics.md`, `tests/regression/capture.py`
4. **Task 3, commit B: File the round-bore chamfer-reach debt** - `2683396` (docs) — `docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md`, `docs/tech_debt/INDEX.md`

_No plan metadata commit yet — this SUMMARY and STATE/ROADMAP updates follow below._

## Files Created/Modified

- `bench/build_time.py` (created) — the sweep runner: `DEFAULT_SWEEP`, `Timing`, `load_sweep`, `time_set`, `report`, `main`
- `bench/sweeps/hex_bore.json` (created) — the 16 Phase 8 parameter sets
- `Makefile` (modified) — `SWEEP ?=` variable, `bench.build` target and `.PHONY` entry
- `tests/test_bench.py` (modified) — two new tests for the sweep's cross product and the budget boundary
- `bench/RESULTS.md` (modified) — new "Hex bore build and export time (Phase 8, D-11)" section
- `docs/architecture/decision_log.md` (modified) — L27 appended
- `docs/architecture/gear-maths/implementation.md` (modified) — three new Layout table rows
- `docs/architecture/solid-model/tactics.md` (modified) — pipeline diagram and Edge re-selection updated
- `tests/regression/capture.py` (modified) — `derived()` docstring updated, JSON untouched
- `docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md` (created) — must-severity debt item
- `docs/tech_debt/INDEX.md` (modified) — new Active row

## Decisions Made

- L27 covers the whole phase's decision set in one append-only entry, following L26's shape (bold-led paragraphs, Rejected, Reversibility, Reason) — no separate entries for D-01 through D-12.
- The round bore's chamfer-reach gap is filed as debt, not fixed, because a fix that refuses round links that build today with less than `MIN_WALL` of wall would violate L05 without a deliberate, separately-decided `Lxx`.
- No `checkpoint:decision` was needed: the sweep's heaviest row (5.08s) landed well inside the 30s budget on the first run, so D-11's gate never triggered.

## Deviations from Plan

None - plan executed exactly as written. The plan's own Flagged Assumption A9 (a heaviest row above 15s would be noted rather than re-run) did not apply — the heaviest measured row was 5.08s, close to the planning probe's ~5s expectation.

## Issues Encountered

None. The plan-specific note about the `gsd-tools query commit` wrapper timing out against the pre-commit `make verify` hook was avoided by using plain `git commit` with explicitly staged files throughout, per D-14; every commit's pre-commit hook completed within its own run with no orphaned process.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 8 (Hex Bore) is complete: the field, the geometry, the derived numbers, the refusals, the warning, the measured cost, and the decision record are all in place and `make verify` is green.
- `bench/build_time.py` and its `make bench.build` target are ready for Phases 9-12 to reuse unchanged with their own sweep files (D-12).
- The round-bore chamfer-reach debt is on file for whichever phase (Phase 9's keyway work is named as the likely trigger) or user report revisits it.
- Landing is `/gsd-ship` followed by `make pr.land PR=N` after verification — not a task in this plan.

---
*Phase: 08-hex-bore*
*Completed: 2026-09-26*

## Self-Check: PASSED

All 11 files listed in "Files Created/Modified" confirmed present on disk (`[ -f ]`).
All four task commit hashes (`a3a651b`, `6f0cd1f`, `ac28b62`, `2683396`) confirmed in
`git log --oneline --all`. All task-level `<acceptance_criteria>` and the plan-level
`<verification>` re-run clean: `make verify` 330 passed in 60.90s; `git diff --numstat
540f1a0 -- docs/architecture/decision_log.md` and `-- bench/RESULTS.md` both report 0
deleted lines; `git diff --exit-code 540f1a0 -- tests/regression/pre_v0_2.json
tests/regression/corpus.py` exits 0.
