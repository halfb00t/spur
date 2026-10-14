---
phase: 25-gate-bar-re-set-venv-probe-ledger-close
plan: 03
subsystem: testing
tags: [bench, gate, readings, venv, pip-constraint, probe, worktree]

requires:
  - phase: 25
    provides: "25-02's two non-decisive readings (A1, B1), the aborted A2 and the kept logs; 25-01's rule commit 1d5ce8a"
provides:
  - "bench/RESULTS.md: the host record, the readings record (Runs, Per arm, Red runs, Waits that gave up) and the venv probe record with Outcome: GREEN"
  - "investigation/: every 25-01 and 25-02 log committed (1f7ce01); ten 25-03 probe files committed (dbc50d9)"
  - "Candidate bar (D-05): none -- the human writes the bar at 25-04"
  - "Probe outcome GREEN: make venv under PIP_CONSTRAINT=requirements.txt works in a linked worktree"
affects: [25-04]

actuals:
  tokens: 26400      # chars/4 over `git diff 861e2cc HEAD` (105651 chars; bench/RESULTS.md alone is 14672 chars, the rest are the committed logs)
  tasks: 2           # Task 1 and Task 2 complete; Task 3 (the branch decision) awaits the human
  commits: 2         # measured: git rev-list --count 861e2cc..HEAD at SUMMARY write (the metadata commit comes after)
plan_head_before: 861e2cca502419ad088d51d3c2f39332c95655f6
plan_head_after: dbc50d991a145ae7001bc5f70b518abc376af698

tech-stack:
  added: []
  patterns:
    - "A probe that must not touch shared git state runs in a linked worktree with the shim hashes compared before and after"

key-files:
  created:
    - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/25-03-probe.log"
    - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/25-03-venv.log"
    - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/25-03-verify.log"
    - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/25-03-pins.log"
    - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/25-03-freeze.diff"
  modified:
    - "bench/RESULTS.md"

key-decisions:
  - "The two non-decisive readings are recorded in full and enter no statistic: both arms print `no decisive run`, `Candidate bar (D-05): none`, and the human writes the bar at 25-04"
  - "The probe is GREEN by D-12's four criteria; the 13 other freeze-diff lines are recorded as read, not explained"

patterns-established:
  - "Wait-end cell `WAIVED` for a run whose wait the human waived, a value the rule did not foresee"

requirements-completed: []   # REQ-gate-bar-reset needs the human's bar at 25-04; REQ-venv-constraint-probe is probed here but its adoption (green branch) is 25-04's

duration: 13min
completed: 2026-10-14
status: complete
---

# Phase 25 Plan 03: Record the readings, probe make venv under PIP_CONSTRAINT Summary

**Two non-decisive readings (A1 195.23 s, B1 179.21 s) recorded with no candidate bar, plus a GREEN `make venv` probe under `PIP_CONSTRAINT=requirements.txt` in a linked worktree, both committed with every kept log; only the branch decision (Task 3) awaits the human.**

## Performance

- **Duration:** about 13 min (start not recorded; the previous commit is at 13:28:02Z)
- **Started:** 2026-10-14T13:28Z (approximate)
- **Completed:** 2026-10-14T13:41Z (SUMMARY write)
- **Tasks:** 2 of 3 complete; Task 3 is the human's checkpoint
- **Files modified:** `bench/RESULTS.md` plus 29 new log files (30 paths in `git diff --stat 861e2cc HEAD`, 1880 insertions)

## Accomplishments

- `bench/RESULTS.md` records `### The host, before run 1 (25-02)` and `### The gate, idle, A/B interleaved (25-02)`. `#### Runs` holds three rows (A1, B1 non-decisive; A2 "aborted by the human's decision, not a reading"). `#### Per arm` prints `no decisive run` in both arms, `mean(B) - mean(A): none` and `Candidate bar (D-05): none`. `#### Red runs`: none. `#### Waits that gave up`: A1's seven give-ups and the aborted eighth, with each wait's load range, and the `WAIVED` wait-end value explained.
- The `### The rule (25-01)` section is byte-identical to the rule commit's; the new text is appended after it (the old file is a prefix of the new).
- The venv probe: `make venv` exit 0 (linked-worktree line printed, no hook installed), `make verify` exit 0 (`1317 passed in 248.73s`, `TOTAL 97.99%`, `real 270.35`, not a gate reading), `pip check` clean, `pins: 31 installed, 31 match, 0 absent`, the freeze diff shows `fastapi` 0.141.1, `starlette` 1.6.0, `uvicorn` 0.53.0, `fonttools` 4.65.0, and the three hook shims hash the same before and after (line 6 still names the main `.venv/bin/python`). UTC window 13:33:03Z to 13:38:32Z, after the last reading's end (13:26:04Z).
- The worktree was removed with a plain `git worktree remove`; git did not refuse.

## Task Commits

1. **Task 1: Record the readings** - `1f7ce01` (docs) -- `bench/RESULTS.md` plus 19 files (every `25-01-*` and `25-02-*`), 20 paths
2. **Task 2: Probe make venv under PIP_CONSTRAINT** - `dbc50d9` (docs) -- `bench/RESULTS.md` plus the ten `25-03-*` files
3. **Task 3: The branch decision** - not yet run; see "Task 3" below

**Plan metadata:** the docs(25-03) commit that carries this file, `STATE.md` and `ROADMAP.md`.

## Per-arm figures and the candidate

| | A | B |
|---|---|---|
| decisive runs (n) | 0 | 0 |
| min / median / max / mean | no decisive run | no decisive run |

`mean(B) - mean(A)`: none. `Candidate bar (D-05): none`. The two `real` values (A1 195.23 s, B1 179.21 s) are quoted in `#### Runs` only and feed nothing (L08).

## The probe in numbers

- `PIP_CONSTRAINT=/Users/half/git/halfb00t/spur/.claude/worktrees/venv-probe/requirements.txt`, set for the one `make venv` call. Warm pip cache: `make venv` took 25 s.
- Freeze diff (main `.venv` vs probe): the four predicted moves plus 13 other lines, recorded as read in `bench/RESULTS.md` and not explained: `aiohttp` 3.14.4 -> 3.14.5, `ast_serialize` 0.12.1 -> 0.13.0, `filelock` 4.0.12 -> 4.1.1, `multidict` 6.9.1 -> 7.1.0, `opentelemetry-api` 1.45.1 -> absent, `platformdirs` 4.12.4 -> 4.13.0, `pre_commit` 4.6.2 -> 4.7.0, `python-discovery` 1.6.1 -> 1.6.2, `ruff` 0.16.10 -> 0.17.0, `trame-common` 1.2.8 -> 1.2.9, `trame-server` 4.0.0 -> 4.1.0, `virtualenv` 21.14.5 -> 21.14.7, `wslink` 2.5.7 -> 2.6.0. None of these names is among the 31 pins.
- Shim sha256 (unchanged): pre-commit `fa3b3ab7...5e4`, commit-msg `6dca5c45...66`, pre-push `22fcbf73...e2e` (full values in `25-03-shims-before.log`).
- `Outcome: GREEN`. A green macOS arm64 run does not show the `linux/arm64` image, a Pi 5, a cold pip cache or build requirements under pip 26.2.

## Task 3: the branch decision (awaiting the human)

`git worktree list` lists only the main checkout. `agent/venv-probe` exists at `1f7ce01`, the phase branch tip from before the probe commit, so `git branch -d agent/venv-probe` accepts it. Options: `delete` (`git branch -d`), `force-remove-and-delete` (not needed: the plain remove succeeded), `keep`. The human's answer, verbatim and with its UTC time, is recorded here by the continuation: **pending**.

## Deviations from Plan

### Human-ordered deviations (not auto-fix rules)

1. **The plan assumed ten decisive readings; there are two non-decisive ones.** The human waived the waits and cut the session (25-02 answers 5 to 8). The record says so; the rule section was not edited. The wait-end cell is `WAIVED` for A1, B1 and A2 (a value the plan did not foresee); A1's exception override is recorded as the human's, not the rule's.
2. **Task 1's first automated verify fails, as written, and was not edited or skipped.** Reason: the human waived the waits (so B1's and A2's wait files hold a `WAIVED` row and no `IDLE` or `GAVE_UP` row, and A1's ends `ABORTED` then `WAIVED`), and the plan's glob `25-02-[AB]-[1-5]*.log` also matches the two give-up snapshot logs, which have no `run-record`. Output, verbatim:

```
Traceback (most recent call last):
  File "<stdin>", line 24, in <module>
IndexError: list index out of range
exit 1
```

   Line 24 is the `idle = [...][-1]` read of a wait file's last `IDLE`/`GAVE_UP` row. A separate supplementary check (not a replacement, not committed) confirmed what the plan's script would otherwise assert: the three `#### Runs` rows equal their logs' `real`, load, UTC window and `HEAD`, no windows overlap, and the rule section is unchanged. Task 1's second automated block passed (`readings commit: 20 paths, every 25-01 and 25-02 log in it and nothing else`), and so did Task 2's two blocks (`probe: worktree only, shims unchanged, after the last reading; outcome GREEN matches the logs; commit dbc50d9`).
3. **The attribution line** on both commits reads `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, the one the harness's session reminder gives, not the `Claude Fable 5.1` line the dispatch prompt named; I am Sonnet 5.5.

**Total deviations:** 0 auto-fixed; 3 recorded above. **Impact on plan:** 25-04 gets no candidate; the human writes the bar and the reason (25-04's verify accepts that path). The probe outcome is complete and recorded.

## Issues Encountered

None beyond the above. `git worktree remove` did not refuse; no `--force` was used.

## Known Stubs

None.

## Threat Flags

None. The probe installed only `pyproject.toml`'s existing `[dev]` extras under the existing 31 pins (no new package), and wrote nothing into the main checkout's `.git/hooks`.

## Debt and ideas filed

None filed. No red run of a new shape occurred.

## Next Phase Readiness

- 25-04: no candidate exists, so the human writes the bar and the reason or answers `no-bar`; the two readings are load-polluted (4.18 to 7.33). The probe is GREEN, so 25-04's green branch applies: `-c requirements.txt` and the stamp prerequisite on `$(STAMP)`, and L43 widens L34's CI sentence.
- The branch decision (Task 3) is still open and is the human's.

## Self-Check: PASSED

Verified on disk: `bench/RESULTS.md` holds both new sections; all ten `25-03-*` files and every `25-01-*`/`25-02-*` file exist; commits `1f7ce01` and `dbc50d9` are ancestors of HEAD; the worktree directory is gone and `agent/venv-probe` exists.

---
*Phase: 25-gate-bar-re-set-venv-probe-ledger-close*
*Completed: 2026-10-14 (Tasks 1 and 2; Task 3 awaits the human)*
