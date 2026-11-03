---
phase: 30-scope-seam-and-gear-safety-guard
plan: 05
subsystem: testing
tags: [phase-close, gate-cost, gear-unchanged, order-check, make-verify]

requires:
  - phase: 30-scope-seam-and-gear-safety-guard
    provides: "30-01: make gear.unchanged; 30-02: L46 (5d61f8e); 30-03: the five placeholders, ten contracts, tests/test_seam.py; 30-04: Part and _serve_model"
provides:
  - "bench/RESULTS.md ### The gate delta (30-05): Phase 30's make verify reading against v0.6's close, with load, host, HEAD and the five placeholders' coverage rows"
  - "bench/RESULTS.md ### Phase close checks (30-05): seven checks, all PASS"
  - "investigation/30-05-close-checks.log, 30-05-verify.log, 30-05-verify-meta.log: the real command output behind both sections"
affects: [31, 32, 33, 34]

plan_head_before: fc00d77cb758906d97aa414b29ffd3bb1bd4433f
plan_head_after: 41fad7dabd7d9fd1bb466f77aa6f90a1122b758c

actuals:
  tokens: 82200   # chars/4 over `git diff fc00d77 HEAD` (328839 chars; 2843 lines of it are the kept make verify log), before this SUMMARY
  tasks: 2
  commits: 1      # MEASURED: git rev-list --count fc00d77cb758906d97aa414b29ffd3bb1bd4433f..HEAD, before this SUMMARY's own commit

tech-stack:
  added: []
  patterns:
    - "an order check that cannot pass on an empty list: it fails when no L46 commit or no placeholder-adding commit is found, then needs the L46 commit to be a strict ancestor of each"
    - "a gate reading is recorded with its load before and after, HEAD, host and source log, and compared like for like (pytest 'passed in' against 'passed in')"

key-files:
  created:
    - .planning/phases/30-scope-seam-and-gear-safety-guard/investigation/30-05-close-checks.log
    - .planning/phases/30-scope-seam-and-gear-safety-guard/investigation/30-05-verify.log
    - .planning/phases/30-scope-seam-and-gear-safety-guard/investigation/30-05-verify-meta.log
  modified:
    - bench/RESULTS.md

key-decisions:
  - "The delta is read against the recorded 236.23 s (1348 passed, v0.6 close) with the same-host 239.51 s beside it, as 30-RESEARCH recommended; the like-for-like column is pytest's 'passed in' against 'passed in'"
  - "No precise delta is claimed: one reading at a 1-minute load of 16.75 -> 16.06 on a non-idle host supports 'no measurable gate cost', and the faster sign sits inside the noise of the two baselines, which differ from each other by 3.28 s"

patterns-established:
  - "The cross-check's `real` (4:00.37 = 240.37 s) is compared with this reading's `real`; the baseline of record has only the pytest figure, so a real-against-passed-in difference is labelled not like for like"

requirements-completed: [REQ-gate-cost-recorded, REQ-scope-decision-logged, REQ-gear-unchanged-proof]

coverage:
  - id: D1
    description: "Seven phase-close checks pass on the final Phase 30 tree and are logged: gear.unchanged, byte-identical paths, the D-20 order on a non-empty list, no shaft behaviour, five docstring-only placeholders, model.py unchanged in shape, ten contracts kept and the seam tests green"
    requirement: REQ-gear-unchanged-proof
    verification:
      - kind: other
        ref: "investigation/30-05-close-checks.log (seven PASS verdicts, no FAIL; 'D-20 order: L46 5d61f8e3d82c2751164dfa22cf5e3381b35415b1 precedes 1 placeholder commit(s)'; 'docstring-only: 5 of 5 []'; 'Contracts: 10 kept, 0 broken.')"
        status: pass
    human_judgment: false
  - id: D2
    description: "Phase 30's make verify time recorded against v0.6's close on the same host: 1369 passed in 233.18s, real 234.48 s, load 16.75 -> 16.06, under L43's 300 s bar, coverage 98.00 %, the five placeholders at 0 statements and 100.00 %"
    requirement: REQ-gate-cost-recorded
    verification:
      - kind: other
        ref: "make verify (investigation/30-05-verify.log), exit status 0 in 30-05-verify-meta.log"
        status: pass
    human_judgment: false
  - id: D3
    description: "REQ-gate-cost-recorded is a cross-cutting requirement: Phase 30's delta is on record, the requirement itself closes at Phase 34's milestone reading"
    requirement: REQ-gate-cost-recorded
    verification: []
    human_judgment: true
    rationale: "The requirement spans every phase; whether the milestone-wide record is complete is Phase 34's judgment, and this plan must not mark it complete (plan prohibition)"

duration: 8min
completed: 2026-10-23
status: complete
---

# Phase 30 Plan 05: Gate delta and phase-close checks Summary

**Phase 30 closed on evidence: `make verify` reads `1369 passed in 233.18s` (real 234.48 s, 98.00 % coverage) against v0.6's 236.23 s, and all seven phase-close checks read PASS with the D-20 order proved on a non-empty list**

## Performance

- **Duration:** 8 min
- **Started:** 2026-10-23T16:39:10Z
- **Completed:** 2026-10-23T16:47Z
- **Tasks:** 2
- **Files modified:** 4 (one doc, three logs)

## The reading

`make verify` on `HEAD fc00d77`, host `18 CPUs, arm64, 64.0 GiB RAM` (Apple M5 Max), 2026-10-23T16:40:02Z to 16:43:56Z, exit status 0.

| Field | Value |
|---|---|
| pytest result line | `1369 passed in 233.18s (0:03:53)` |
| `/usr/bin/time -p` | `real 234.48`, `user 671.57`, `sys 537.41` |
| Coverage TOTAL | `1363 22 386 13 98.00%`, floor 96.0 % reached |
| 1-minute load before -> after | `16.75` -> `16.06` (not an idle host) |
| Five placeholders | each `0 0 0 0 100.00%` |

Baseline used: the recorded 236.23 s (`1348 passed`, v0.6 close, `.planning/PROJECT.md`), with the same-host 239.51 s (`HEAD 760ac4e`, real 240.37 s, load 11 to 37) beside it.

| This reading minus | pytest `passed in` | `real` |
|---|---|---|
| baseline of record, 236.23 s | -3.05 s (-1.29 %) | -1.75 s (-0.74 %), not like for like |
| cross-check, 239.51 s / 240.37 s | -6.33 s (-2.64 %) | -5.89 s (-2.45 %) |

Every difference is a fraction of Phase 25's ~8 % run-to-run spread (about 18.9 s), so it sits inside the spread. The reading is 65.52 s under L43's 300 s bar, so nothing is surfaced for a decision. The phase added 21 tests (14 from 30-01, 6 in `tests/test_seam.py`, 1 in `tests/test_api.py`), the 0.46 s check and five more contracts. A precise delta is not claimed from one non-idle reading.

## Close-check verdicts

All seven PASS (`30-05-close-checks.log`): `make gear.unchanged` green; `requirements.txt`, `tests/regression/`, `.github/workflows/ci.yml`, `README.md`, `src/spur/calc.py` and `src/spur/params.py` byte-identical to `v0.6`; the L46 commit `5d61f8e` is a strict ancestor of the one commit that adds the five placeholders; no `class Shaft...` and no `/api/shaft` route under `src`; five docstring-only placeholders; `model.py`'s diff since v0.6 adds 0 lines naming isinstance or shaft; `Contracts: 10 kept, 0 broken.` and 19 passed in `tests/test_seam.py` plus `tests/test_gear_unchanged.py`.

## Accomplishments

- The Phase 30 gate delta is on record with its load, host, HEAD, UTC window and source logs, read against two baselines and labelled as one non-idle reading.
- Every phase-close condition from the roadmap and CONTEXT is checked green on the final tree, and the D-20 order check cannot pass on an empty list.
- Coverage shows the five placeholders at 0 statements and 100.00 %, the total at 98.00 % against the 96 % floor.

## Task Commits

1. **Task 1: Every phase-close check on the final tree, logged** - no commit by plan design; the log rides in Task 2's commit
2. **Task 2: The gate delta, read on this host and recorded with its load** - `41fad7d` (docs)

**Plan metadata:** the commit that carries this SUMMARY, then one commit for STATE.md, ROADMAP.md and REQUIREMENTS.md.

## Files Created/Modified

- `bench/RESULTS.md` - `### The gate delta (30-05)` and `### Phase close checks (30-05)`, inserted above `### Seen red once (Phase 30)`, 57 lines added, 0 deleted
- `.planning/phases/30-scope-seam-and-gear-safety-guard/investigation/30-05-close-checks.log` - the seven checks with command, output, exit status and verdict
- `.planning/phases/30-scope-seam-and-gear-safety-guard/investigation/30-05-verify.log` - the whole `/usr/bin/time -p make verify` output
- `.planning/phases/30-scope-seam-and-gear-safety-guard/investigation/30-05-verify-meta.log` - UTC start and end, both loadavg readings, HEAD, host line, make's exit status

## Decisions Made

- Baseline of record 236.23 s with 239.51 s as the cross-check, per 30-RESEARCH; the comparison is like for like on pytest's `passed in`.
- No precise delta or "faster" claim: the sign is inside the noise of one non-idle reading.
- REQ-gate-cost-recorded is not marked complete; it closes at Phase 34. The stale `v0.6` tag concern in STATE.md Blockers/Concerns was cleared on the orchestrator's instruction (`git cat-file -t v0.6` prints `tag`).

## Deviations from Plan

None - plan executed exactly as written. One wording point: the plan asks for "the `real` seconds" against each baseline, but the baseline of record exists only as pytest's `passed in` figure, so the section gives both measures and labels real-against-passed-in as not like for like.

## Issues Encountered

None. The host was not idle (1-minute load 16 to 19, other Python processes active before the run); the plan accepts a non-idle reading provided its load is recorded, which it is.

## Open items and handoffs

- **Assumption A1 stays open:** that CI's first run fetches the `v0.6` tag with `git fetch --depth=1 origin tag v0.6` under `actions/checkout@v4`'s persisted credentials. It cannot be tested from this host; the first CI run of the phase is the proof, and `ci.yml` cannot be edited, so a failure goes to the human.
- **Phase 32 handoff (from 30-03):** when `model.py` first imports `shaft_model` statically, that same commit adds `ignore_imports = ["spur.model -> spur.shaft_model"]` to C3; added earlier it errors with `No matches for ignored import`.
- Phase 31 widens `Part` in one line of `parts.py`; Phase 33's shaft routes call `_serve_model` as its second caller (30-04 handoff).
- No debt or idea item was filed.

## Known Stubs

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 30 has five of five plans summarised; ready for phase verification and the first CI run (A1).

## Self-Check: PASSED

The three logs and `bench/RESULTS.md` exist; commit `41fad7d` is an ancestor of HEAD; `grep -c FAIL` on the close-checks log prints 0; the verify log holds the result line, `real 234.48`, `Required test coverage of 96.0% reached` and the five placeholder rows; RESULTS.md diff is 57 added, 0 deleted; the heading `### The gate delta (30-05)` appears once.

---
*Phase: 30-scope-seam-and-gear-safety-guard*
*Completed: 2026-10-23*
