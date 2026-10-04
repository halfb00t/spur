---
phase: 15-the-gate-measured-and-pinned
plan: 04
subsystem: testing
tags: [make-verify, pytest-xdist, pytest-cov, bench, before-after, bar]

requires:
  - phase: 15-the-gate-measured-and-pinned
    provides: "15-03's decision: N = 8, bar 66 s, no cut, Before = serial --cov C0; 15-02's D-05 verdict (6 of 6 green at N = 8) and coverage floor"
provides:
  - "Makefile: PYTEST_WORKERS (8, clamped to the online CPUs) and -n $(PYTEST_WORKERS) in the test recipe, --cov --cov-report=term intact"
  - "bench/RESULTS.md ### Before and after: A1 B1 A2 B2, mean(A) 228.99 s, mean(B) 63.555 s, bar 66 s met"
affects: [15-05, 15-06]

actuals:
  tokens: 1983
  tasks: 2
  commits: 3
plan_head_before: 741096df8eeafc0a74272c6926646432f6871b8d
plan_head_after: ba53d1786da5264daeac92f4633c24cad6eafd8c

tech-stack:
  added: []
  patterns:
    - "the worker count is one Makefile literal read through a clamp (w=8 inside the shell), overridable as PYTEST_WORKERS=n on the make command line"
    - "serial runs of the xdist-enabled gate are PYTEST_ARGS=\"-n0\": the later flag wins and --cov stays on"

key-files:
  created: []
  modified:
    - Makefile
    - bench/RESULTS.md
    - docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md

key-decisions:
  - "N = 8 goes into the Makefile as PYTEST_WORKERS ?= $(shell w=8; n=$$(getconf _NPROCESSORS_ONLN); echo $$(( n < w ? n : w ))): 8 on the dev host, 4 on a 4-vCPU runner, one literal"
  - "A in the before/after is serial with coverage (PYTEST_ARGS=-n0), the Before the human chose, not the plan's no-coverage A"
  - "The .pre-commit-config.yaml '~11 s' comment is left for 15-06: this plan's action text and files_modified do not name it"

patterns-established:
  - "A bar the human sets at a checkpoint is read by the same recipe on the same host: alternating A/B, load recorded, verdict computed from the recorded two-decimal walls against the bar as written"

requirements-completed: [REQ-verify-at-the-bar, REQ-verify-profiled]

coverage:
  - id: D1
    description: "The gate runs on pytest-xdist workers: make test passes -n $(PYTEST_WORKERS), 8 clamped to the host's CPUs, with --cov --cov-report=term unseparated; no -n auto, addopts untouched, no rerun plugin"
    requirement: REQ-verify-at-the-bar
    verification:
      - kind: other
        ref: "Task 1 automated check -> 'make test runs -n 8'; make -n test prints '.venv/bin/python -m pytest -n 8 --cov --cov-report=term'"
        status: pass
      - kind: other
        ref: "git diff --quiet 20cd484 -- src tests/regression/pre_v0_2.json requirements.txt -> 'D-20 ok'; git diff --quiet 20cd484 -- tests exits 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "The 66 s bar is read by alternating A1 B1 A2 B2 runs: mean(B) 63.555 s against 66 s is met, 927 passed in every row, test count unchanged"
    requirement: REQ-verify-at-the-bar
    verification:
      - kind: other
        ref: "Task 2 automated check -> 'verdict met 63.55 bar 66.0'; 'reading committed'; 'nothing changed after the reading'"
        status: pass
    human_judgment: false
  - id: D3
    description: "Whether the A row is a fair Before (serial with coverage, -n0 overriding -n 8 in the recipe) and whether load differences (A at 14.15 and 19.17, B at 5.91 and 5.31) flatter or hurt the reading"
    requirement: REQ-verify-profiled
    verification: []
    human_judgment: true
    rationale: "The Before was chosen by the human; the plan's A was serial without coverage. Whether -n0 on the xdist recipe is the same serial gate as C0's plain pytest --cov is a reading of how the plugin behaves that no assertion covers (the A walls, 228.23 and 229.75 s, sit 15-16 s under C0's 244.59 s)"

duration: 23min
completed: 2026-10-04
status: complete
---

# Phase 15 Plan 04: The Gate on Eight Workers, Read Against the Bar Summary

**`make test` now runs `pytest -n 8 --cov` (8 clamped to the host's CPUs); four alternating full runs read the gate at mean(B) 63.555 s against the human's 66 s bar, a 165.4 s cut from the serial `--cov` gate's 228.99 s, with 927 tests passing in every run.**

## Performance

- **Duration:** 23 min (the first clock reading was 05:41:53Z; the plan was loaded about five minutes before that)
- **Started:** 2026-10-04T05:37:00Z (approximate)
- **Completed:** 2026-10-04T06:00:00Z
- **Tasks:** 2 executed, Task 3 not reached (bar met)
- **Files modified:** 3 (Makefile, bench/RESULTS.md, one debt note); `tests/`, `src/` and `requirements.txt` untouched

## Accomplishments

- Makefile, above `test:` under a comment that cites bench/RESULTS.md's xdist sweep and Gate decision and names `-n0` and `--no-cov`: `PYTEST_WORKERS ?= $(shell w=8; n=$$(getconf _NPROCESSORS_ONLN); echo $$(( n < w ? n : w )))`. `make -n test` prints `.venv/bin/python -m pytest -n 8 --cov --cov-report=term` on this 12-CPU host; `make -n test PYTEST_WORKERS=3` prints `-n 3`. The clamp keeps one literal; on CI's 4-vCPU runner it yields 4, which 15-05 proves from xdist's "created" line.
- `### Before and after` (bench/RESULTS.md): the order line written before A1; the four rows; the means; the verdict `Bar: 66 s (15-CONTEXT.md D-01 addendum) -> met, mean(B) = 63.555 s`.
- No cut applied; `tests/` is byte-identical to `20cd484`.

## The reading

HEAD `5797199` for every row; A is `make verify PYTEST_ARGS="-n0"` (serial, `--cov` on), B is `make verify`.

| Run | Args | Load | pytest | Wall (s) | Peak RSS (MiB, procs) | Exit | Coverage |
|---|---|---|---|---|---|---|---|
| A1 | `-n0` | 14.15 | 927 passed in 227.22s | 228.23 | 1415 (5) | 0 | 96.99% |
| B1 | none (`-n 8`) | 5.91 | 927 passed in 63.63s | 64.19 | 6638 (17) | 0 | 97.21% |
| A2 | `-n0` | 19.17 | 927 passed in 228.73s | 229.75 | 1418 (5) | 0 | 96.99% |
| B2 | none (`-n 8`) | 5.31 | 927 passed in 62.35s | 62.92 | 6634 (15) | 0 | 97.21% |

mean(A) = 228.99 s, mean(B) = 63.555 s, delta = -165.435 s. Bar 66 s: **met**, 2.445 s to spare. Task 3 (`checkpoint:decision`) is not presented: miss checkpoint not reached -- mean(B) 63.555 s at or under the bar 66 s.

Hook wall time observed after `-n 8` landed: Task 1's commit (the hook runs `make verify`, plus the commit-msg hook) took 64 s by `date`; the Task 2 commit 63 s; the debt-note commit is the same hook again. These are context, not bar readings.

## Task Commits

1. **Task 1: put the human's N in the Makefile** - `5797199` (build)
2. **Task 2: before and after, alternating runs** - `b8b4dd1` (docs)
3. **Debt note: tally of which full runs lost the worker coverage flush** - `ba53d17` (docs)

**Plan metadata:** the closing `.planning/` commit (`docs(15-04): summarise the gate read against the bar`)

## Files Created/Modified

- `Makefile` - `PYTEST_WORKERS`, `-n $(PYTEST_WORKERS)` in the `test` recipe, the merged partial-run example (`tests/regression -q -n0 --no-cov`)
- `bench/RESULTS.md` - `### Before and after`
- `docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md` - an eight-run tally (see below)

## Decisions Made

- N = 8 enters the Makefile as one literal inside the clamp (`w=8`); the plan's example repeated N twice, this form keeps it once. `PYTEST_WORKERS` sits between 15-02's comment and `test:`, as the plan's action text says, not beside `PYTEST_ARGS ?=`.
- D-05's tolerance runs at N were not re-run: N equals the apparent knee K = 8 and 15-02's six runs at `-n 8` (6 of 6 green) stand, as the human's answer and 15-03's addendum state. No `### Tolerance at N`.
- The `.pre-commit-config.yaml` "~11 s" hook comment (line 6) was **not** edited. 15-03's return assigned it to this plan, but this plan's `files_modified` and Task 1 action do not name it and 15-06's plan does (SC2's hook comment); following my own plan's text, it stays for 15-06. After this plan the measured gate on this host is mean(B) 63.555 s for 15-06 to copy into the "~11 s" sites and L34.

## Deviations from Plan

**1. [Human decision, via orchestrator] A is serial with coverage, not the plan's serial no-coverage**
- **Found during:** Task 2
- **Issue:** the plan's A is `PYTEST_ARGS="-n0 --no-cov"` (what `20cd484` ran). At 15-03's checkpoint the human chose the serial `--cov` configuration as Before so that `-n` is the only variable between A and B.
- **Fix:** A = `make verify PYTEST_ARGS="-n0"`: `PYTEST_ARGS` comes last, so `-n0` overrides `-n 8`, `--cov --cov-report=term` stays. The record says so in `### Before and after`. mean(A) is therefore 228.99 s, not a no-coverage serial figure (224.28 s at P1/P2).
- **Files modified:** bench/RESULTS.md
- **Committed in:** `b8b4dd1`

**2. [Rule 1 - wrong plan assumption] None of the plan's regexes needed a fix, but my first Makefile comment contained the literal `-n auto`**
- **Found during:** Task 1
- **Issue:** Task 1's verify asserts `'-n auto' not in Makefile`; the first draft of the comment named the option it was rejecting and failed the check.
- **Fix:** reworded to "not the host's CPU count". No behaviour change.
- **Files modified:** Makefile
- **Committed in:** `5797199`

**3. [Rule 2 - evidence for an existing debt] Tally in the lost-flush debt note**
- **Found during:** Task 2
- **Issue:** the four rows made the pattern in 15-02's debt note sharper than "sometimes".
- **Fix:** a short tally paragraph in the note: C0, A1, A2 (serial) all lost lines 63-67 and 222 of `pool.py`; none of the five `-n 8 --cov` runs that printed `pool.py` did. Eight runs, no cause; 15-RESEARCH's one loss at `-n 4` keeps it from being read as serial-only. Severity and Status are unchanged.
- **Files modified:** docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md
- **Committed in:** `ba53d17`

---

**Total deviations:** 3 (1 human decision relayed, 1 own-draft wording, 1 evidence note)
**Impact on plan:** none on the outcome. The reading is as measured; no run was repeated, dropped or replaced.

## Issues Encountered

- A stray read-only helper command of mine (`.venv/bin/python -` fed by a heredoc, run between the B2 reading and the write-up) hung waiting on stdin for about two minutes. It ran after all four measured runs were complete and before any further run, so no reading was affected; it was killed.
- Run labels `X_A1`..`X_B2` were used for the raw files, so the scratchpad's 15-02 `A1`..`B3` files were not overwritten. Raw outputs stay in the session scratchpad, not the repo.

## Known Stubs

None (config and records only).

## Threat Flags

None. No network endpoint, auth path or file access pattern was added; `make test` gained a `getconf` call and two flags.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

For 15-05 and 15-06:

- **15-05 (CI):** CI runs `make verify PYTHON=python`, so it inherits `-n $(PYTEST_WORKERS)`; on a 4-vCPU runner `getconf _NPROCESSORS_ONLN` is 4 and the clamp gives `-n 4`. The proof is xdist's "created: 4/4 workers" line in the CI log, which `### CI run` should quote. CI time is context on a different host, never the bar (D-02).
- **15-06 (prose and L34):** the measured number is mean(B) 63.555 s (B1 64.19, B2 62.92; loads 5.91, 5.31) on the dev host with `-n 8 --cov`, against a serial `--cov` mean(A) of 228.99 s and the human's bar of 66 s. The "~11 s" sites are `.pre-commit-config.yaml:6` (named by 15-06's plan, not edited here), `README.md:282`, `docs/HOW_TO_DEVELOP.md:21`, `docs/architecture/packaging.md:41` and lines 8 and 15 of `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`. Note the hook wall time (64 s) is the whole commit, not only pytest.
- `make test-image` stays serial and unchanged (D-07). A partial run is `make test PYTEST_ARGS="tests/regression -q -n0 --no-cov"`.
- Peak RSS at `-n 8` is 6.6 GiB as an upper bound (17 processes, B1); the serial gate is 1.4 GiB. Relevant to any memory-limited runner.

## Self-Check: PASSED

- Files FOUND: `Makefile` (with `PYTEST_WORKERS ?=` line 85 and `-n $(PYTEST_WORKERS)` line 88), `bench/RESULTS.md` (with `### Before and after`), this SUMMARY
- Commits FOUND: `5797199`, `b8b4dd1`, `ba53d17`; `git rev-list --count 741096d..HEAD` was 3 before this SUMMARY
- Re-run: Task 1 checks -> `make test runs -n 8`, `D-20 ok`; Task 2 checks -> `verdict met 63.55 bar 66.0`, `reading committed`; Task 3's check -> `nothing changed after the reading`; `git diff --quiet 20cd484 -- src tests requirements.txt` exits 0

---
*Phase: 15-the-gate-measured-and-pinned*
*Completed: 2026-10-04*
