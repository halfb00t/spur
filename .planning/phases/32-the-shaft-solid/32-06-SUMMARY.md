---
phase: 32-the-shaft-solid
plan: 06
subsystem: gate-and-decisions
tags: [gate-delta, close-checks, decision-log, din5480, l48, bench]

requires:
  - phase: 32-the-shaft-solid
    provides: "32-01 gate baseline (2387 passed in 251.15 s), 32-02 to 32-05 code, tests, bars, sweep and the two L47 amendments"
provides:
  - "one logged `make verify` on the final Phase 32 tree, recorded against 32-01's baseline on the same host (bench/RESULTS.md `### The gate delta (32-06)`)"
  - "eleven phase-close checks, each PASS in 32-06-close-checks.log and in `### Phase close checks (32-06)`"
  - "L48, the closing decision-log entry: how Phase 32 builds the shaft solid, what it refuses, what it hands to Phases 33 and 34"
  - "a nice debt item for the two shaft_model guard lines no passing test reaches"
affects: [33, 34]

actuals:
  tokens: 150887   # chars/4 over the added lines of 7a4e108..HEAD; 5393 lines of that is the kept verify log, the docs themselves are about 5.6k tokens
  tasks: 3
  commits: 4
plan_head_before: 7a4e1083d35846b5fe53306c6c34b15347832767
plan_head_after: f539ce3cf1beb1b1d100f0486b6411375d711ee3

tech-stack:
  added: []
  patterns:
    - "a gate reading is compared only with a logged reading of the same host, and the load of both is written beside the difference"
    - "a phase-close check is one command that appends PASS or FAIL with the decisive line to one log"

key-files:
  created:
    - .planning/phases/32-the-shaft-solid/investigation/32-06-verify.log
    - .planning/phases/32-the-shaft-solid/investigation/32-06-verify-meta.log
    - .planning/phases/32-the-shaft-solid/investigation/32-06-close-checks.log
    - docs/tech_debt/active/2026-10-27-shaft-model-two-guard-lines-no-passing-test-reaches.md
  modified:
    - bench/RESULTS.md
    - docs/architecture/decision_log.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "The reading of record is 2644 passed in 233.83 s (real 234.78 s) at load 5.24 -> 7.66: -17.32 s (-6.90 %) against 32-01's 251.15 s, inside Phase 25's ~8 % spread (about 20.09 s), so no speed claim"
  - "Two in-phase readings above L43's 300 s bar (32-04's 358.81 s, 32-05's 312.50 s) are written down in RESULTS and L48, not trimmed: the same code spans 218.58 s to 358.81 s across the phase, so wall time here is the host's load"
  - "L48 is the closing entry; it cites the two L47 amendments for the applied chamfer and the bounds instead of restating them"

requirements-completed: [REQ-shaft-solid, REQ-shaft-build-measured]  # the plan's own text: REQ-gate-cost-recorded stays open and closes at Phase 34's milestone reading, so it is NOT copied here

coverage:
  - id: D1
    description: "make verify on the final Phase 32 tree, logged and recorded against 32-01's baseline with its difference, spread and margin to 300 s"
    requirement: "REQ-gate-cost-recorded"
    verification:
      - kind: other
        ref: "grep -E '^=+ [0-9]+ passed' .planning/phases/32-the-shaft-solid/investigation/32-06-verify.log"
        status: pass
    human_judgment: false
  - id: D2
    description: "eleven phase-close checks, PASS or FAIL each in one log, none FAIL"
    verification:
      - kind: other
        ref: "grep -c '^FAIL' 32-06-close-checks.log prints 0 and grep -c '^PASS' prints 11"
        status: pass
    human_judgment: false
  - id: D3
    description: "L48 records what Phase 32 built and proved, with every number citing a SUMMARY, a bench/RESULTS.md section or a log"
    requirement: "REQ-shaft-solid"
    verification:
      - kind: other
        ref: "grep '^## L' docs/architecture/decision_log.md | tail -1 | grep -c \"the DIN 5480 shaft's solid\" prints 1"
        status: pass
    human_judgment: true
    rationale: "A decision entry is prose; no test asserts that each cited number is the one in its source, so a reviewer should spot-check the citations"

duration: 12 min
completed: 2026-10-27
status: complete
---

# Phase 32 Plan 06: The gate delta, the close checks and L48 Summary

`make verify` on the final Phase 32 tree reads `2644 passed in 233.83s` (`real 234.78`, load 5.24 -> 7.66), 17.32 s (6.90 %) under 32-01's `2387 passed in 251.15s` on the same host and inside the 8 % spread, so no speed claim; eleven close checks all pass; and L48 closes the phase in the decision log.

## Performance

- **Duration:** 12 min
- **Started:** 2026-10-27T11:00:47Z
- **Completed:** 2026-10-27T11:12Z
- **Tasks:** 3
- **Files modified:** 7 (plus three new logs)

## The gate reading

Source: `investigation/32-06-verify.log` and `32-06-verify-meta.log`; section `### The gate delta (32-06)` in `bench/RESULTS.md`.

| Field | Value |
|---|---|
| HEAD | `7a4e108` (no `src`, `tests`, `bench`, `pyproject.toml`, `Makefile` or `requirements.txt` change uncommitted) |
| UTC start -> end | `2026-10-27T11:01:04Z` -> `2026-10-27T11:05:04Z` |
| 1-minute load before -> after | `5.24` -> `7.66` |
| make's exit status | `0` |
| pytest | `======================= 2644 passed in 233.83s (0:03:53) =======================` |
| `/usr/bin/time -p` | `real 234.78`, `user 722.96`, `sys 720.61` |
| Coverage TOTAL | `TOTAL 1682 24 450 14 98.22%` (floor 96.0) |
| Gate lines | `Contracts: 10 kept, 0 broken.` and `gear.unchanged: ... (8723 bytes) are byte-equal to v0.6` |

Against the 32-01 baseline (`HEAD 7c1bc2c`, `2387 passed in 251.15s`, `real 253.13`, load 7.96 -> 15.03): pytest `-17.32 s` (`-6.90 %`), `real` `-18.35 s` (`-7.25 %`). Phase 25's spread is about 8 %, about 20.09 s of 251.15 s, so both differences are inside it and no speed claim is made. The loads differ (this plan did not control them) and the phase added 257 tests while the reading fell, which says the load moved more than the tests did. The margin to L43's 300 s bar is 66.17 s (`real`: 65.22 s). **The reading of record is not above 300 s.** The CONTEXT figure `221.86 s` is not used (it appears in no log).

Per-plan test additions, from each plan's own gate reading: 15 in 32-02, 224 in 32-03 (192 flank-angle cases and 32 kernel tests), 12 in 32-04, 6 in 32-05, none in 32-01 and 32-06: 257 in all.

**For the human: two in-phase readings exceed 300 s.** 32-04's `358.81 s` and 32-05's `312.50 s` (each under a load its SUMMARY does not record) are above L43's bar, on the same `src` and `tests` that read `233.83 s` here. The five full-gate readings of the phase span 218.58 s to 358.81 s, much wider than 8 %. They are written down in `bench/RESULTS.md` and L48 and not trimmed; they say the gate's wall time on this host is set by its load. Nothing was changed because of it. REQ-gate-cost-recorded stays open and closes at Phase 34's milestone reading.

`src/spur/shaft_model.py` reads 96.77 % (lines 179 and 187, both guards no passing test reaches); every other shaft module is 100 %. Filed as debt, below.

## The close checks

`investigation/32-06-close-checks.log`, one run on `HEAD ed5cfa1`: 11 `PASS`, 0 `FAIL`.

1. `make gear.unchanged`: byte-equal to v0.6 (8723 bytes).
2. `git diff --exit-code v0.6` over `requirements.txt`, `tests/regression/`, `ci.yml`, `calc.py`, `params.py`: exit 0.
3. `make lint-imports`: `Contracts: 10 kept, 0 broken.`
4. No `@app.<verb>("/api/shaft` route under `src`.
5. `Part = GearParams | ShaftParams` once in `parts.py`.
6. The widening debt item: in `resolved/`, `Status: resolved`, `Resolved in: 4018de8` resolves, INDEX row in the Resolved table.
7. `pool.py`, `app.py`, `cli.py`, `din5480_tables.py` byte-equal to `b4cfd71`.
8. `ShaftDimensions` has 13 keys, `end_chamfer_effective` at index 10 (32-01 choice B1).
9. The bound pin cites `The heaviest shaft (32-05)`; `-k sweep_reaches` passes (1 passed, 50 deselected).
10. AST walk of `shaft_model.py` (70 calls): no `clean`, `chamfer` or `union` call, no `glue` keyword.
11. `din5480.py` holds 5 `ASSUMPTION` markers, the same as at `b4cfd71`.

## The closing entry

**L48**, appended after the last L47 amendment (`docs/architecture/decision_log.md`, 83 lines added, 0 deleted): construction and the four forbidden routes with their logs, the applied chamfer (cites the L47 amendment of 32-02), what the solid refuses (band guard, volume bracket, one-valid-solid and kernel-failure words, each with its seen-red log), tolerances (32-03 and 32-04 bars with measured worsts), the doorway and its one ignored edge, bounds (cites the L47 amendment of 32-05), the gate delta, handoffs to Phases 33 and 34, reversibility and reason.

## Task Commits

1. **Task 1 (tracer): the gate delta** - `ed5cfa1` (docs(bench)): `bench/RESULTS.md` `### The gate delta (32-06)` and the two verify logs; its three verify commands re-run after the commit (the tracer gate) and all passed before Task 2.
2. **Task 2: the close checks** - `98891dd` (docs(bench)): `### Phase close checks (32-06)` and `32-06-close-checks.log`.
3. **Task 3: L48** - `f539ce3` (docs(decisions)).
4. Added, not in the plan: `f73df4a` (docs(debt)) for the coverage finding, committed before Task 1's docs commit because the RESULTS section names the item.

**Plan metadata:** the commit that carries this SUMMARY, STATE.md, ROADMAP.md and REQUIREMENTS.md.

## Files Created/Modified

- `bench/RESULTS.md` - `### The gate delta (32-06)` and `### Phase close checks (32-06)`, above `### Seen red once (Phase 32)`, 74 lines added and 0 deleted
- `docs/architecture/decision_log.md` - L48
- `docs/tech_debt/active/2026-10-27-shaft-model-two-guard-lines-no-passing-test-reaches.md` and `docs/tech_debt/INDEX.md` - the debt item and its row
- `.planning/phases/32-the-shaft-solid/investigation/32-06-verify.log`, `32-06-verify-meta.log`, `32-06-close-checks.log` - the evidence

## Decisions Made

- No new decision beyond L48's recording. The comparison, the spread reading and the 300 s surfacing follow the plan's rules.

## Deviations from Plan

**1. [Rule 3 - Blocking, plan inconsistency] The L48 heading's capital T**
- **Found during:** Task 3.
- **Issue:** the action gives the title `## L48 — The DIN 5480 shaft's solid: ...`, but the task's verify (`grep '^## L' ... | tail -1 | grep -c "the DIN 5480 shaft's solid"`) and the artifact's `contains:` are case-sensitive and lower-case, so the action's title prints 0.
- **Fix:** the heading reads `## L48 — How Phase 32 builds the DIN 5480 shaft's solid, what it refuses, and what it hands on (follows L46 and L47; applies L08, L24, L26)`, the same parenthesis and the same three clauses in an order that matches the check.
- **Files modified:** `docs/architecture/decision_log.md`
- **Verification:** the check prints 1.
- **Committed in:** `f539ce3`

**2. [Rule 2 - Missing critical, CLAUDE.md debt rule] A debt item filed for the coverage row**
- **Found during:** Task 1 (the coverage table copied into the RESULTS section).
- **Issue:** `src/spur/shaft_model.py` reads 96.77 %, lines 179 and 187. Not caused by this plan (code is Phase 32's, last touched at 32-03); the plan only records it.
- **Fix:** one debt item (severity nice) and its INDEX row, one commit, `f73df4a`. No source or test was touched (the plan's acceptance requires `git status --porcelain -- src tests` empty).
- **Files modified:** `docs/tech_debt/active/2026-10-27-shaft-model-two-guard-lines-no-passing-test-reaches.md`, `docs/tech_debt/INDEX.md`

**3. `requirements-completed` is not the plan's `requirements` array verbatim.** The plan declares REQ-gate-cost-recorded, REQ-shaft-solid and REQ-shaft-build-measured, and says the first stays open to Phase 34; the frontmatter lists only the other two so nothing marks it complete.

**Total deviations:** 1 plan inconsistency (Rule 3), 1 debt item filed (Rule 2), 1 frontmatter note. **Impact:** none on any recorded number.

## Issues Encountered

None that changed a result. The first draft of the RESULTS section carried a placeholder for the close checks; it was removed before any commit (the Task 1 commit holds the gate delta only, as the plan asks).

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None. T-32-13 is mitigated: one logged `/usr/bin/time -p make verify`, compared only with 32-01's logged baseline, every figure copied from a log or a SUMMARY, and the close checks logged PASS or FAIL.

## Debt and ideas filed

Filed: `docs/tech_debt/active/2026-10-27-shaft-model-two-guard-lines-no-passing-test-reaches.md` (nice, trigger `src/spur/shaft_model.py` is next touched). No idea item filed.

## Next Phase Readiness

Phase 32's plans are all summarised. Phase 33 owns the `/api/shaft/` routes, the CLI and the page, the 13 keys on the wire, the `slug()` stem, `enabled_when` for `shank_d` and the contention row; Phase 34 owns the nominal-thickness switch and the milestone gate reading that closes REQ-gate-cost-recorded. The phase-level verifier should spot-check L48's citations (D3 is a human-judgment deliverable).

## Self-Check: PASSED

- Created files exist: the three 32-06 logs, the debt item, this SUMMARY.
- Commits `f73df4a`, `ed5cfa1`, `98891dd`, `f539ce3` are ancestors of HEAD.
- Close-checks log: 0 `FAIL`, 11 `PASS`; `make gear.unchanged` green after the last commit; `git status --porcelain -- src tests bench docs pyproject.toml` empty.

---
*Phase: 32-the-shaft-solid*
*Completed: 2026-10-27*
