---
phase: 25-gate-bar-re-set-venv-probe-ledger-close
plan: 01
subsystem: testing
tags: [bench, gate, pre-registration, rehearsal, timeout, loadavg]

requires:
  - phase: 24
    provides: "bench/RESULTS.md as the measurement record; the gate recipe (make verify) the rule governs"
provides:
  - "bench/RESULTS.md `## The gate re-set (Phase 25)` / `### The rule (25-01)`: the idle threshold, the wait, N = 5 per arm, the caps, the A/B design, the candidate rule, and the two fenced recipe blocks `# the wait (25-01)` and `# one run (25-01)`"
  - "investigation/25-01-rehearsal*.log: proof both recipe blocks run on this host (untracked; 25-03 commits them)"
affects: [25-02, 25-03, 25-04]

actuals:
  tokens: 2658       # chars/4 over `git diff dc41527..HEAD` (10631 chars): the rule section only
  tasks: 3
  commits: 1
plan_head_before: dc41527b2e8ab6036514e131d9a008ac7cedc2e3
plan_head_after: 1d5ce8ad6f973b8b10d30e074a44d6c173b3caec
commits: 1

tech-stack:
  added: []
  patterns:
    - "Pre-register a measurement rule in a commit of its own; git log -S orders it before any reading"
    - "Recipe blocks committed in the rule are extracted byte for byte and run by the readings"

key-files:
  created: []
  modified: [bench/RESULTS.md]

key-decisions:
  - "Rule committed as drafted on the human's answer `commit` (2026-10-14T10:42:40Z); no amend"
  - "Rehearsal logs stay untracked in investigation/ until 25-03 commits them"

requirements-completed: [REQ-gate-rule-pre-registered]

coverage:
  - id: D1
    description: "The gate re-set rule is in bench/RESULTS.md with its two recipe blocks, committed alone, before any reading"
    requirement: "REQ-gate-rule-pre-registered"
    verification:
      - kind: other
        ref: "git log --format=%H -S'### The rule (25-01)' -- bench/RESULTS.md prints 1d5ce8a; git show --name-status lists only bench/RESULTS.md (Task 3 automated verify, rule commit 1d5ce8a line)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Whether the rule's numbers and gap-fill clauses are the ones the human wants binding for ten readings"
    requirement: "REQ-gate-rule-pre-registered"
    verification: []
    human_judgment: true
    rationale: "The thresholds, caps and gap-fills are the human's decisions; the human confirmed them at the Task 2 blocking-human gate (answer `commit`), and no test can judge them"

duration: 11min
completed: 2026-10-14
status: complete
---

# Phase 25 Plan 01: Pre-register the gate re-set rule Summary

**The idle-host gate rule (load strictly under 1.5, three 30 s samples, N = 5 per arm interleaved A/B, 900 s wait and run caps, `math.ceil` candidate) is committed alone as 1d5ce8a with its wait and run recipes rehearsed on zero-cost stand-ins, before any reading exists.**

## Performance

- **Duration:** about 11 min across two executors (Task 1 draft and rehearsal, then the human gate, then Task 3)
- **Started:** 2026-10-14T10:3xZ (rehearsal transcript header `2026-10-14T10:36:41Z`)
- **Completed:** 2026-10-14T10:44:23Z
- **Tasks:** 3 (1 tracer, 1 blocking-human decision, 1 commit)
- **Files modified:** 1 tracked (`bench/RESULTS.md`, +129 lines), 6 untracked rehearsal logs

## Accomplishments

- `## The gate re-set (Phase 25)` / `### The rule (25-01)` appended to `bench/RESULTS.md` (5543 -> 5672 lines). The first paragraph says this is a new method, not L34's (Phase 15 D-04 read the gate at 1-minute loads of 5 to 30 and took the largest of three).
- Ten numbered clauses fix D-01..D-09 and D-21 before any reading, plus the planner's gap-fill clauses the human saw at Task 2.
- Two fenced `sh` blocks, `# the wait (25-01)` and `# one run (25-01)`, rehearsed on this host before the commit.
- The rule is one commit touching only `bench/RESULTS.md`, and `git log -S'### The rule (25-01)'` names it (SC1).

## Host facts and collect counts (read in Task 1, read-only)

- `bench.machine_facts()`: `18 CPUs, arm64, 64.0 GiB RAM`; chip `Apple M5 Max`; model `Mac17,6`
- `HEAD` at drafting: `dc41527` on `gsd/phase-25-gate-bar-re-set-venv-probe-ledger-close`; `git merge-base HEAD main`: `1864bcdca18922fd5c649c58f04632b9ea0c1706`
- `pytest --collect-only -q`: `1317 tests collected`; with `--ignore=tests/test_browser.py`: `1315 tests collected` (as the plan expected)
- `timeout` is GNU coreutils 9.12 at `/opt/homebrew/bin/timeout`
- `make -n verify | grep -E 'pip install|playwright install|pre-commit install'` printed nothing (stamps fresh at drafting)
- 1-minute load read during the rehearsal: 1.91 (wait sample), 2.07 (run before/after), above 1.5 as expected with agent sessions open. This is not a reading; no gate ran.

## Rehearsal outcomes (`investigation/25-01-rehearsal.log`, untracked)

| Block | Substitution | Result |
|---|---|---|
| wait | `CAP=900` -> `CAP=0` | one sample row `1.91 0 0`, then `GAVE_UP`, `wait exit 3` |
| run | `timeout -k 30 900 make verify` -> `timeout -k 30 900 sleep 1`, ARM=B | `real 1.00`, `make verify exit 0`, `run-record` line |
| run | -> `timeout -k 1 2 sleep 10`, ARM=B | `real 2.00`, `make verify exit 124`, `run-record` line |
| run | -> `timeout -k 30 900 printenv PYTEST_ADDOPTS`, ARM=A | log shows `--ignore=tests/test_browser.py` |
| run | same, ARM=B | log shows no value (`printenv` exit 1) |

No `make verify`, `make test` or pytest run other than `--collect-only` ran before the commit. The only host load after Task 1 was the pre-commit hook's `make verify.fast`, which the plan allows before any reading.

## Task Commits

1. **Task 1: Tracer, draft the rule and rehearse both blocks** - no commit, by plan (draft held in the working tree)
2. **Task 2: One-way gate** - checkpoint, no commit
3. **Task 3: Commit the rule alone** - `1d5ce8a` (docs)

**Plan metadata:** recorded by the `docs(25-01)` commit that adds this file.

## Task 2: the human's answer

Verbatim: `commit`
UTC time: `2026-10-14T10:42:40Z`
Answered by the project human through the orchestrator; the gate was `blocking-human`, so no auto-approval applied.

The gap-fill clauses the planner wrote and the human saw before they bound: a red attempt is retried at its own slot; a green run whose wait gave up fills its slot and never enters the statistics; the 3 h clock starts at the A1 wait that releases; at the cap no new wait starts and a started run finishes; an arm past its budget is short and the other arm runs on; statistics use decisive greens only and an arm with none prints no figure; the median of an even count is the mean of the two middle values; no warm-up run; one `caffeinate -i -t 10800`; GNU `timeout` as the per-run kill.

## Task 3: the rule commit

- **sha:** `1d5ce8ad6f973b8b10d30e074a44d6c173b3caec` (`1d5ce8a`)
- **`git log -1 --format=%ct`:** `1791974637`
- **`git log -1 --format=%cI`:** `2026-10-14T16:43:57+06:00` (= `2026-10-14T10:43:57Z`)
- **Subject:** `docs(25): pre-register the gate re-set rule -- idle below 1.5, five runs per arm, interleaved A/B`
- **Files:** `bench/RESULTS.md` only (+129 lines)
- **Hook result line:** `make verify.fast (static checks + every test file but the five heavy ones, under 30 s)......Passed`; `reject GitHub Actions skip tokens in the commit message......Passed`
- **Both Task 3 automated verifies passed:** `rule commit 1d5ce8a touches only bench/RESULTS.md and is the -S anchor`; and no `25-02-A-1.log` / `25-02-A-1.wait.tsv` exists, regression fixtures clean, no tracked file modified outside the GSD state files.
- **Order:** the human's answer (10:42:40Z) precedes the commit (10:43:57Z). **No reading has started**: no `25-02-*` file exists, and the 25-02 first wait must start after epoch `1791974637`.
- The rehearsal logs under `investigation/` are untracked; 25-03 commits them. Nothing else that loads the host ran after the commit.

## Files Created/Modified

- `bench/RESULTS.md` - the gate re-set rule section appended (tracked, committed in 1d5ce8a)
- `.planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/25-01-rehearsal.log`, `25-01-rehearsal-wait.wait.tsv`, `25-01-rehearsal-{ok,cap,armA,armB}.log` - rehearsal transcript (untracked)

## Decisions Made

- Committed the rule as drafted (`commit`); no clause changed after the human saw it.
- The rehearsal logs are kept untracked here so the rule commit touches one file; 25-03 commits them with the readings.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. The pre-commit hook stashed and restored the unstaged GSD state files around its run, as it does for any commit; `STATE.md` and `state.json` came back intact.

## Known Stubs

None.

## Threat Flags

None. The commit adds a record and two shell recipes that the later plans run; it adds no network endpoint, auth path or schema.

## Debt or ideas filed

None.

## Next Phase Readiness

- 25-02 can extract the two blocks from 1d5ce8a and run the D-09 quiet-host checkpoint. Its first wait must start after epoch `1791974637`.
- Between this commit and the last reading only `.planning/` may change (D-07). The current 1-minute load on this host is above 1.5, so the human must quiet it at the D-09 checkpoint before run 1.

## Self-Check: PASSED

- `bench/RESULTS.md` holds `### The rule (25-01)`: FOUND
- Commit `1d5ce8a` is an ancestor of HEAD: FOUND
- `git rev-list --count dc41527..HEAD` printed 1, matching `commits: 1`
- Rehearsal logs exist and are untracked: FOUND

---
*Phase: 25-gate-bar-re-set-venv-probe-ledger-close*
*Completed: 2026-10-14*
