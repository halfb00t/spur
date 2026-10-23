---
phase: 26-gate-fails-with-a-cause
plan: 05
subsystem: testing
tags: [pytest, faulthandler, xdist, hang-evidence, makefile, tech-debt, gate-cost]

requires:
  - phase: 26-gate-fails-with-a-cause
    provides: plans 26-01 to 26-04, the shared-recipe pin in tests/test_hooks.py, the Phase 26 section of bench/RESULTS.md and the investigation/ directory
provides:
  - "Makefile: the test recipe runs -v --durations=25, with the reason and the measured cost in its comment; test.fast untouched"
  - "pyproject.toml: faulthandler_timeout = 120 (dump-only), sized from a recorded local --durations reading"
  - "tests/test_hooks.py: the shared-recipe pin asserts -v and --durations= in test and neither in test.fast (seen red first)"
  - "docs/tech_debt/active/2026-10-10-make-verify-hung-...: a Runbook (Phase 26); item still active, no cause claimed"
  - "bench/RESULTS.md: Hang evidence (26-05) - the 120 s rule, the stall proof, the 3 + 3 cost table"
affects: [26-07]

actuals:
  tokens: 2600    # chars/4 over the lines authored in Makefile, pyproject.toml, tests/test_hooks.py, bench/RESULTS.md and docs/ (10414 added chars); logs excluded
  tasks: 3
  commits: 2
plan_head_before: 70609110609a64347c9fa501e4780c3a1aee6ab1
plan_head_after: 75b43cbc46c3af785386d771e4574cfcdcdcb83c
commits: 2

tech-stack:
  added: []
  patterns:
    - "A dump-only faulthandler_timeout in the ini plus -v on the gate: a stalled test names itself and the run carries on"
    - "A throwaway stall probe run once, quoted in the record, deleted before any commit (the commit hook would collect it)"

key-files:
  created:
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-05-durations-local.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-05-pin-red.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-05-stall.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-05-Makefile.A.mk
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-05-cost-A1.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-05-cost-B1.log
  modified:
    - Makefile
    - pyproject.toml
    - tests/test_hooks.py
    - bench/RESULTS.md
    - docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "faulthandler_timeout stays 120: the slowest phase S read 32.33 s locally, 2 x S = 64.66 s is below 120, so the rule keeps 120 (CI confirm is 26-07)"
  - "The 3 + 3 cost delta read -0.51 %, below the 5 % stop rule, so no checkpoint was needed and the flags stay as planned"
  - "The cost runs went out as one background driver (A B A B A B back to back) rather than six separate 900 s commands; same order, same no-idle-wait, the six wall clocks are the plan's run-records"
  - "The commit trailer follows the session's attribution (Claude Sonnet 5.5), not the plan text, as in 26-01 to 26-04"

requirements-completed: [REQ-hang-leaves-evidence]

coverage:
  - id: D1
    description: "The test recipe runs -v --durations=25 and test.fast does not; the pin asserts both and was red (3 failed, 6 passed) on the -v assertion before the recipe edit, green (9 passed) after"
    requirement: REQ-hang-leaves-evidence
    verification:
      - kind: unit
        ref: "tests/test_hooks.py::test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe; investigation/26-05-pin-red.log"
        status: pass
    human_judgment: false
  - id: D2
    description: "faulthandler_timeout = 120 in the ini, accepted under --strict-config, set from the recorded local reading (S = 32.33 s); no other pyproject line changed"
    requirement: REQ-hang-leaves-evidence
    verification:
      - kind: integration
        ref: "git diff --numstat v0.5 -- pyproject.toml reads 7 added, 0 deleted, all the key and its # comment; investigation/26-05-durations-local.log"
        status: pass
    human_judgment: false
  - id: D3
    description: "A throwaway stalled test at -n 8 --cov through make test left its id (-v start line) and a stack dump with a frame in test_stalls in the log; the probe never reached a commit"
    requirement: REQ-hang-leaves-evidence
    verification:
      - kind: integration
        ref: "investigation/26-05-stall.log (Timeout (0:00:05)!, line 5 in test_stalls, 1 passed in 30.58s); test ! -e tests/test_zz_stall_probe.py"
        status: pass
    human_judgment: false
  - id: D4
    description: "The gate's cost of the flags, 3 + 3 interleaved, against L43's 300 s bar: mean 206.87 s before, 205.81 s after, -0.51 %; all six green, no Timeout line in arm B"
    requirement: REQ-hang-leaves-evidence
    verification:
      - kind: integration
        ref: "investigation/26-05-cost-{A,B}{1,2,3}.log run-records, checked in order by the Task 2 verify script"
        status: pass
    human_judgment: false
  - id: D5
    description: "The hang item stays active with a runbook that covers what prints, how to read it, what the per-item timer cannot see and the operator step (kill -ABRT marked UNVERIFIED), and claims no cause"
    requirement: REQ-hang-leaves-evidence
    verification:
      - kind: integration
        ref: "Task 3 verify: Status: active, '## Runbook (Phase 26)', Makefile:185 reference current, 2026-10-10 log line verbatim"
        status: pass
    human_judgment: true
    rationale: "Wording and honesty of the runbook (no cause claimed, the blind spot stated plainly) are read, not asserted by a test. The verifier reads the item and the RESULTS subsection."

duration: ~32min
completed: 2026-10-15
status: complete
---

# Phase 26 Plan 05: A stalled test names itself Summary

**`-v --durations=25` on the `test` recipe and a dump-only `faulthandler_timeout = 120` in the ini, proved by a throwaway 30 s stall at `-n 8 --cov` that left its test id and a stack naming `test_stalls` in the log; the gate cost -0.51 % over 3 + 3 interleaved runs (206.87 s vs 205.81 s, against L43's 300 s bar).**

## Performance

- **Duration:** ~32 min wall (start about 12:02Z, last commit 12:33Z); the local reading 197 s, the stall run 31 s, the six cost runs 20 min, `make verify` 185.44 s
- **Completed:** 2026-10-15
- **Tasks:** 3 (Task 1 a tracer, Tasks 2 and 3 auto)
- **Files modified:** 6 source, record or debt files; 6 new log files plus `26-05-Makefile.A.mk` and the six cost logs under `investigation/`

## Accomplishments

- **The timeout, from a reading (D-07).** `make test PYTEST_ARGS="--durations=25"` before any edit: `1321 passed in 196.96s`, exit 0, load 11.27 at the end. The slowest single phase S is **32.33 s** (`tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser`); 2 x S = 64.66 s is below 120, so `faulthandler_timeout = 120`. Dump-only: `faulthandler_exit_on_timeout` is not set.
- **Pin red, then green (D-06).** The shared-recipe pin gained four assertions (`-v` and a `--durations=` word in `test`, neither in `test.fast`). Before the recipe edit: `3 failed, 6 passed` (the pin and the two tests that call it), on the `-v` assertion. After: `9 passed`. The comparison of the two recipes still goes only through `-n N`.
- **The stall proof (D-08, SC4).** `tests/test_zz_stall_probe.py` (one test, 30 s sleep) through `make test PYTEST_ARGS="tests/test_zz_stall_probe.py -o faulthandler_timeout=5 --cov-fail-under=0"`, i.e. `-n 8 --cov -v --durations=25`: the start line `tests/test_zz_stall_probe.py::test_stalls`, then `Timeout (0:00:05)!`, then `File ".../tests/test_zz_stall_probe.py", line 5 in test_stalls`, and `1 passed in 30.58s` (dump-only). The probe was deleted before the change commit; `git status -- tests/` was clean.
- **The cost of the flags, 3 + 3 interleaved (D-09).** Arm A is the old recipe (`git show 7060911:Makefile`) with `-o faulthandler_timeout=0`; arm B is `make test`. Order A1 B1 A2 B2 A3 B3, back to back, no idle wait.

| Run | Arm | Wall | pytest s | Load before -> after | Exit |
|-----|-----|------|----------|----------------------|------|
| A1 | before | 207.21 s | 207.00 | 4.67 -> 7.93 | 0 |
| B1 | after | 218.94 s | 218.66 | 7.93 -> 7.59 | 0 |
| A2 | before | 211.07 s | 210.79 | 7.59 -> 7.68 | 0 |
| B2 | after | 208.50 s | 208.28 | 7.68 -> 9.62 | 0 |
| A3 | before | 202.32 s | 201.83 | 9.62 -> 10.12 | 0 |
| B3 | after | 189.99 s | 189.28 | 10.12 -> 10.45 | 0 |

  Mean A **206.87 s**, mean B **205.81 s**, delta **-0.51 %**. The 5 % stop rule did not trip, so no checkpoint was raised. The per-pair deltas are +5.7 %, -1.2 %, -6.1 % and the load rose from 4.7 to 10.5 over the run: the spread is larger than the effect. The reading is "no measurable cost", not "free". Every run is under L43's 300 s bar (highest 218.94 s). Empty edge: no arm-B log contains `Timeout (`, every arm-B exit is 0.
- **The runbook (D-10).** The hang item stays `Status: active`, no cause claimed. Four parts: what a stalled gate prints (start lines without a worker id, `[gwN] [ NN%] PASSED <id>` out of order, the `Timeout (0:02:00)!` dump on stderr that can start mid-line and names the function not the parametrize id); how to read it (in flight = started minus finished); what it cannot see (a stall after a worker's last test, in xdist shutdown or pytest-cov's combine, leaves no dump); the operator step for that window (`ps`, keep the whole log, `kill -ABRT <pid>` marked UNVERIFIED). A dated line under Next step records that the evidence is on. The INDEX trigger cell was updated in place.
- **The gate:** `make verify`, exit 0, `1321 passed in 185.44s (0:03:05)`, `TOTAL 1358 22 386 13 97.99%`, `Required test coverage of 96.0% reached`; 1321 `PASSED` lines, 0 `Timeout (` lines.

## Task Commits

1. **Task 1: the flags, the ini key, the pin, the stall proof** - `04fd620` (test)
2. **Task 2: the 3 + 3 cost runs** - no commit of its own, by the plan's design (logs and `26-05-Makefile.A.mk` committed with Task 3)
3. **Task 3: the runbook, the record, the cost in the recipe comment** - `75b43cb` (docs)

`commits: 2` is measured from the ledger base `7060911` to the Task 3 commit, before this SUMMARY's commit.

## Files Created/Modified

- `Makefile` - `test` recipe `-v --durations=25`; comment with the reason and the measured cost (recipe command now on line 185)
- `pyproject.toml` - `faulthandler_timeout = 120` with its comment (7 added lines, 0 deleted against `v0.5`)
- `tests/test_hooks.py` - four assertions in the shared-recipe pin
- `bench/RESULTS.md` - `### Hang evidence (26-05)` (77 added lines, 0 deleted against `v0.5`)
- `docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md` - the runbook, the dated line, the refreshed `Makefile:185` reference
- `docs/tech_debt/INDEX.md` - the hang item's trigger cell
- `.planning/phases/26-gate-fails-with-a-cause/investigation/26-05-*` - durations reading, pin red, stall log, arm-A Makefile, six cost logs

## Decisions Made

See `key-decisions`. None needed a new `Lxx`: the plan's D-06 to D-10 and L43 govern, and nothing here contradicts a locked decision.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The hang item's Related-files link to the flake item pointed at `active/`**
- **Found during:** Task 3
- **Issue:** the third bullet cited `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md`; 26-04 moved that item to `resolved/`, so the link was dead.
- **Fix:** the path now reads `docs/tech_debt/resolved/...`. One word in a file Task 3 already edits; no other line of that bullet changed.
- **Files modified:** the hang item
- **Commit:** `75b43cb`

**2. [Process, not a rule] The six cost runs were one background driver, not six 900 s commands**
- **Found during:** Task 2
- **Issue:** the plan asks for each run as its own background command capped at 900 s. Six sequential runs of about 3.5 minutes exceed one 900 s command, and separate launches would put model turns between runs (idle gaps D-09 forbids).
- **Fix:** one driver script ran A B A B A B back to back, writing the same per-run logs and run-record lines. The Task 2 verify script (six green run-records, in order, no `Timeout (` in B) passed unchanged. No run was red, so no retry was needed.
- **Commit:** `75b43cb` (logs)

**Total deviations:** 1 auto-fixed (Rule 1), 1 process note. **Impact:** none on the measured numbers or the committed result.

## Issues Encountered

- The host was shared and loaded (1-minute load 4.7 to 11.3 across the plan). It is logged per run and stated as the reason the cost reading is "no measurable cost".
- `make venv` re-installed the closure once after the ini edit (the stamp depends on `pyproject.toml`), untimed, before any timed run, as planned.

## Known Stubs

None. No placeholder, hardcoded empty value or unwired data in the files this plan touched.

## Threat Flags

None. The stack dumps in a log show repo-relative and venv paths and function names only (T-26-11, accepted); the probe was deleted before any commit (T-26-12, mitigated and checked by `ls tests/`); the gate cost was measured against the bar (T-26-13).

## Debt and ideas

Filed none. Resolved none: the hang item stays active by the plan's design (it gained a runbook, not a resolution). Open for 26-07: confirm `faulthandler_timeout = 120` against the first CI `--durations` (change only if CI's slowest x 2 exceeds 120 s).

## Next Phase Readiness

Ready for 26-06. 26-07 owns the CI confirm of the 120 s value and reads CI's `--durations`.

## Self-Check: PASSED

- Files exist: Makefile, pyproject.toml, tests/test_hooks.py, bench/RESULTS.md, the hang item, INDEX.md, and the 26-05 logs under `investigation/`.
- Commits exist on the branch: `04fd620`, `75b43cb`.
- `tests/test_zz_stall_probe.py` is absent and in no commit; `git diff --exit-code v0.5 -- tests/regression/ requirements.txt src/` exits 0; `faulthandler_exit_on_timeout` appears nowhere in the pyproject diff.
- `.venv/bin/python -m pytest tests/test_hooks.py -n0 --no-cov -q -p no:cacheprovider`: `9 passed`.
- `make verify`: exit 0, `1321 passed in 185.44s (0:03:05)`.
