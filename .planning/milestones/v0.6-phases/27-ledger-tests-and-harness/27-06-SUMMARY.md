---
phase: 27-ledger-tests-and-harness
plan: 06
subsystem: testing
tags: [browser-harness, process-group, bench-records, decision-log, triage, tech-debt]

requires:
  - phase: 27-ledger-tests-and-harness
    provides: 27-01's macOS and ubuntu-latest `ps` listings of the server group; the red logs of 27-02 to 27-05
provides:
  - the MIN_GROUP_MEMBERS comment, serve() docstring and floor message naming the members ps lists (uvicorn, resource tracker, one or two workers), floor unchanged at 3
  - a dated correction under each of the two bench/RESULTS.md rows that read "3 (uvicorn and two pool workers)"
  - L40's dated amendment giving the download step's range
  - "### Seen red once (Phase 27)" with 12 rows, each naming its kept log
  - 27-TRIAGE.md, the draft info-finding table Phase 28 closes
  - the group-floor debt item retired
affects: [Phase 28 info-finding triage, Phase 29 ubuntu-latest rollout reading]

actuals:
  tokens: 4560   # chars/4 over the +/- lines of the three commits, investigation logs excluded
  tasks: 3
  commits: 3     # MEASURED: git rev-list --count d855b37..HEAD at write time (before the SUMMARY commit)

plan_head_before: d855b37eff69a1d923a01a78860a7c3c8d465283
plan_head_after: 8561dcc11757d86d121aee939394fe7883d6b821

tech-stack:
  added: []
  patterns:
    - "A floor comment carries the observed members per host (run id, image, version, date), and the count that clears it is stated as a range (3 or 4), not as the roster"
    - "A correction to a recorded reading is a bold-led dated paragraph directly after its table; the reading itself stays"

key-files:
  created:
    - .planning/phases/27-ledger-tests-and-harness/27-TRIAGE.md
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-06-verify.log
  modified:
    - tests/browser_session.py
    - bench/RESULTS.md
    - docs/architecture/decision_log.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md

key-decisions:
  - "MIN_GROUP_MEMBERS stays 3 and names no member: 3 is every build on one executor slot, 4 is both, and a run reading either clears it (D-01)"
  - "The ubuntu correction says the 21-02 reading counted rows with a ps that prints no command, so which three members it counted was never observed; the member set comes from 27-01's later listing"

requirements-completed: [REQ-group-floor-recorded-true]

coverage:
  - id: D1
    description: "MIN_GROUP_MEMBERS comment, serve() docstring and floor message name the members ps listed on macOS and ubuntu-latest and cite 27-01; the floor is still 3"
    requirement: REQ-group-floor-recorded-true
    verification:
      - kind: unit
        ref: "make test PYTEST_ARGS=\"tests/test_browser.py tests/test_browser_pins.py -n0 --no-cov -q\" (7 passed in 24.12s) and the Task 1 comment check (needles uvicorn, resource_tracker, macOS, ubuntu, 27-01)"
        status: pass
    human_judgment: true
    rationale: "Whether the comment claims no more than the two listings show (L08) is a reading, not a test"
  - id: D2
    description: "Two dated corrections sit directly after their tables in bench/RESULTS.md, naming their rows; no reading and no L40 sentence is rewritten"
    requirement: REQ-group-floor-recorded-true
    verification:
      - kind: other
        ref: "Task 1 check: 2 correction paragraphs each directly after its own table; git diff --numstat v0.5 -- bench/RESULTS.md docs/architecture/decision_log.md: 0 deleted lines (676 and 2 added)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The group-floor debt item is resolved, git mv-ed, and its INDEX row moved in the commit that writes the comment"
    requirement: REQ-group-floor-recorded-true
    verification:
      - kind: other
        ref: "Task 1 item check (Status resolved, Resolved in set, INDEX points at resolved/, nothing at active/)"
        status: pass
    human_judgment: false
  - id: D4
    description: "L40's amendment and the 12-row Seen red once (Phase 27) table, each row naming its kept log"
    verification:
      - kind: other
        ref: "Task 2 check (amendment text, 12 rows, every row names a .log) and grep -cF of four first-failure strings in their logs (1, 1, 2, 1)"
        status: pass
    human_judgment: false
  - id: D5
    description: "27-TRIAGE.md proposes a disposition for every finding this milestone owns and the phase closes green"
    verification:
      - kind: other
        ref: "Task 3 triage check; make verify exit 0 (1333 passed in 240.09s, coverage 97.99%); git diff --exit-code v0.5 -- tests/regression/ empty; src/ diff is src/spur/model.py only; make verify.fast real 11.32 s"
        status: pass
    human_judgment: true
    rationale: "Whether each proposed disposition is the right one is Phase 28's decision with the human; the table is a draft"

duration: 14min
completed: 2026-10-20
status: complete
---

# Phase 27 Plan 06: The harness records and the phase close Summary

**The group-floor comment, docstring and message now name the members `ps` listed on macOS and ubuntu-latest (uvicorn, resource tracker, one or two workers) with the floor unchanged at 3, two dated corrections sit under the RESULTS rows that said "two pool workers", L40 carries the download step's 1.13 to 3.56 s range, the phase's 12 red runs are in one table, and a 28-row draft triage waits for Phase 28.**

## Performance

- **Duration:** 14 min
- **Started:** 2026-10-20T13:58Z (approximate; the first guard run read 14:00:44Z)
- **Completed:** 2026-10-20T14:11Z
- **Tasks:** 3
- **Files modified:** 7 on the phase branch across the three commits (2,858 lines added, 10 deleted, 2,755 of the added are the kept `make verify` log)

## Accomplishments

- **Task 1 (`99e2b7d`)**: the comment above `MIN_GROUP_MEMBERS = 3` now reads, in full:

  > The kill's non-vacuity check: the group is counted before the kill so that the zero counted after it is a real zero and not a reader that matches nothing. After the browser test's builds `ps -ww` lists uvicorn, `multiprocessing.resource_tracker` and one or two spawned workers (27-01), not "uvicorn plus the pool's 2 workers": the pool is two single-worker executors routed by `hash(p) % workers` (src/spur/pool.py, D-07 affinity), each starting its worker at its first build, and `hash(GearParams())` is salted per process. So 3 is every build on one executor slot and 4 is both slots; a run reading exactly 3 and one reading 4 both clear `>=`, and neither shows both workers ran. macOS (Apple M5 Max, macOS 27.0.1, 1-minute load 4.7-7.7, 2026-10-20, 27-01) read 4, 3 and 4 over three runs; ubuntu-latest (run 39428298442, `Image: ubuntu-24.04` version 20261012.334.1, 2026-10-20, 27-01) read 4 in its one run, the same three commands. A forced second build would show both workers and was rejected (D-01); members are not matched by command either, the floor is a count (D-01).

  `serve()`'s docstring says the pre-build group is uvicorn and the resource tracker (2 members, macOS 2026-10-10) and a worker starts at its executor's first build. The floor message reads "expected uvicorn, the resource tracker and at least one pool worker (>= 3)". Browser test and pins: `7 passed in 24.12s`.
- Corrections, first lines: `**Correction (2026-10-20, 27-06), row "Group members seen before the kill".** The row reads "3 (uvicorn and two pool workers)".` and `**Correction (2026-10-20, 27-06), row "Server process group members before the kill".** The row reads "3 (uvicorn and two pool workers)".` The item `2026-10-10-group-floor-of-3-is-not-two-pool-workers.md` is `Status: resolved`, moved, and its INDEX row is the first Resolved row.
- **Task 2 (`d7f069d`)**: L40's `**Amendment (2026-10-20, 22-REVIEW IN-03).**` gives `step download name` as 3.56, 3.20 and 1.13 s, mean 2.63 s, `BUILD_WAIT_MS` unchanged, and points at the seeded totality test (seed 20261020, 1,300 draws, 0.07 s). `### Seen red once (Phase 27)` has **12 rows**: 27-02 (junction, root curve, name test, OpenAPI walk, honeycomb), 27-03 (old order, leader-only), 27-04 (host state), 27-05 (launch pin, environ rule, `-0`, non-scalar fixture param).
- **Task 3 (`8561dcc`)**: `27-TRIAGE.md` has **28 rows**: fixed 20, skipped 1 (19 IN-02's near-copy replacement, D-07's reason), deferred 2 (21 IN-04b, 24 IN-04), open 5 (19 IN-04's `root_fillet` label, 24 IN-01, 24 IN-02 / CX-03, the Phase 18 and 10 group, Phase 26's five IN rows flagged "raise at Phase 28").

## Phase-close results

| Check | Result |
|---|---|
| `make verify` | exit 0; `======================= 1333 passed in 240.09s (0:04:00) =======================`; `Required test coverage of 96.0% reached. Total coverage: 97.99%` (kept as `investigation/27-06-verify.log`) |
| `git diff --exit-code v0.5 -- tests/regression/` | exit 0, empty |
| `git diff --name-only v0.5 -- src/` | `src/spur/model.py` |
| `git diff --numstat v0.5 -- bench/RESULTS.md docs/architecture/decision_log.md` | `676 0` and `2 0`: no deleted line |
| `make verify.fast` | `932 passed in 10.81s`, `real 11.32` s (under 30 s) |

## Task Commits

1. **Task 1: the MIN_GROUP_MEMBERS comment, docstring and message from both listings, two dated corrections, item retired** - `99e2b7d` (docs)
2. **Task 2: L40's dated amendment and the phase's red runs** - `d7f069d` (docs)
3. **Task 3: the draft triage table for Phase 28, then the phase-close gate** - `8561dcc` (docs)

**Plan metadata:** the commit that adds this SUMMARY, STATE.md, ROADMAP.md and REQUIREMENTS.md (docs: complete plan)

## Files Created/Modified

- `tests/browser_session.py` - the comment, docstring and floor message
- `bench/RESULTS.md` - two corrections and the 12-row red table (inserted lines only)
- `docs/architecture/decision_log.md` - L40's amendment
- `docs/tech_debt/resolved/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md`, `docs/tech_debt/INDEX.md` - the item retired
- `.planning/phases/27-ledger-tests-and-harness/27-TRIAGE.md` - the draft triage (new)
- `.planning/phases/27-ledger-tests-and-harness/investigation/27-06-verify.log` - the phase-close gate log

## Decisions Made

- The ubuntu correction does not repeat 27-01's member set as if 21-02 had seen it: 21-02 counted with a `ps` that prints no command, so its three members were never named. The correction says that and gives 27-01's later listing as the evidence (L08).
- The comment is dated with a load range (4.7 to 7.7) taken from 27-01's recorded before and after loads, not a single figure.
- The triage names the squash-merge commit (an ancestor of HEAD) beside the branch commit for the two rows fixed on a squashed branch (19 IN-03 as `cbbe730` for `34270c8`; 21 IN-04a and 24 CX-05 as `1981d93` for `6ff1269`).

## Deviations from Plan

### Auto-fixed Issues

**1. [Process] First Task 1 commit attempt failed on a pathspec**
- **Found during:** Task 1 commit
- **Issue:** `git add` was given the old `active/` path of an item already staged as a rename by `git mv`, so it refused the whole command and nothing was committed.
- **Fix:** re-ran `git add` without that path; the rename was already staged. No file change.
- **Committed in:** `99e2b7d`

**2. [Plan variation] 12 red rows, not 11; one extra kept file**
- **Found during:** Tasks 2 and 3
- **Issue:** the 27-05 harness-info log holds two failing tests (`_js_number`'s `-0` and the non-scalar fixture param), so one row each reads more truthfully than one row naming two tests. Task 3 also keeps the phase-close `make verify` log, which the plan lists only as a result to record.
- **Fix:** 12 rows (the verify needs at least 11); the log is committed beside the others, as 27-02 did for `verify-fast`.
- **Files modified:** `bench/RESULTS.md`, `investigation/27-06-verify.log`
- **Committed in:** `d7f069d`, `8561dcc`

---

**Total deviations:** 2 (one process slip with no effect, one plan-compatible variation)
**Impact on plan:** none on scope.

## Issues Encountered

- `.planning/milestone.lock` is untracked and predates this plan; left alone.
- `34270c8` and `6ff1269` are branch commits that exist locally but are not ancestors of HEAD (the phases were squash-merged). The triage names the ancestor squash commit beside each. This is the existing active item `docs/tech_debt/active/2026-10-05-resolved-in-shas-point-at-squashed-branch-commits.md`, not a new one.
- `19-REVIEW-DISPOSITION.md` reads `skipped` for IN-01 to IN-04 with no reason today, which is not the vocabulary REQ-info-findings-triaged asks for; the triage's intro says so, for Phase 28.
- Left alone, as earlier plans recorded: the inline bore-off copies in `tests/test_cli.py:524` (`_BORE_OFF`), `tests/test_calc.py`, `tests/test_bench.py`, `tests/test_model.py` (noted on the 22 IN-01 row); 27-03's literal leader-only break stayed green (recorded in that red row, run 2 is the red one); 27-04's bench near-copies (recorded `skipped`).

## Debt filed

None filed: no new item or idea. One item retired: `docs/tech_debt/resolved/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md`.

## Known Stubs

None.

## Threat Flags

None. No new endpoint, auth path, file access or schema change; T-27-19 (no deleted line in RESULTS or the decision log), T-27-20 (the comment cites 27-01's Linux run id, image and date) and T-27-21 (every triage sha is a commit; the two non-ancestors are named beside their ancestor) are mitigated as planned.

## Authentication Gates

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 27's six plans are done and the gate is green with the fixture byte-identical and one `src/` file changed. The phase is ready for verification and Phase 28.
- Phase 28 reads `27-TRIAGE.md`, writes each `*-REVIEW-DISPOSITION.md`, and raises Phase 26's five open IN rows with the human. The human still owns deleting `spike/27-group-listing` (local and `origin`).

---
*Phase: 27-ledger-tests-and-harness*
*Completed: 2026-10-20*

## Self-Check: PASSED

Verified: `27-TRIAGE.md`, `investigation/27-06-verify.log`, `tests/browser_session.py`, `bench/RESULTS.md` and the resolved debt item exist; `99e2b7d`, `d7f069d` and `8561dcc` are ancestors of HEAD; `git log -1` subjects of the three commits match the plan's wording.
