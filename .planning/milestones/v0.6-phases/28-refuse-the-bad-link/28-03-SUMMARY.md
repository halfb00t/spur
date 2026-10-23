---
phase: 28-refuse-the-bad-link
plan: 03
subsystem: docs
tags: [comments, docstrings, info-findings, tech-debt]

requires:
  - phase: 28-refuse-the-bad-link
    provides: 28-02's commits on the shared working tree
provides:
  - the environ-allowance comment in tests/test_browser_pins.py naming the real unit (27 IN-11)
  - the Makefile image-ignore comment and the hang debt item citing bench/RESULTS.md first (26 IN-04)
  - root_mode's docstring naming the ValueError from cutter (18 IN-07)
affects: [28-04]

actuals:
  tokens: 1500
  tasks: 3
  commits: 3
plan_head_before: a39cf3d65698551649b055430904902742386a8d
plan_head_after: 90928023b74af80ba9524d33459ae4edf52d857e

key-files:
  created: []
  modified:
    - tests/test_browser_pins.py
    - Makefile
    - docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md
    - src/spur/calc.py

key-decisions:
  - "D-15: the 27 IN-11 fix is the comment only; the test name test_an_environ_read_is_allowed_by_its_statement_not_its_line keeps the word statement"
  - "D-17: durable record (bench/RESULTS.md) first, a .planning/ path only as a secondary pointer"

requirements-completed: [REQ-info-findings-triaged, REQ-old-info-findings-triaged]

coverage:
  - id: D1
    description: "27 IN-11 comment says the allowance is per top-level expression of a statement; the module AST equals 0efc87c"
    requirement: "REQ-info-findings-triaged"
    verification:
      - kind: unit
        ref: "AST equality against 0efc87c plus tests/test_browser_pins.py: 15 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "26 IN-04 Makefile and hang item cite bench/RESULTS.md first; the Phase 21 log path points at the archived copy; Makefile diff is comment lines only"
    requirement: "REQ-old-info-findings-triaged"
    verification:
      - kind: unit
        ref: "tests/test_hooks.py tests/test_no_fake_done.py: 14 passed; the Makefile diff has no non-comment changed line"
        status: pass
    human_judgment: false
  - id: D3
    description: "18 IN-07 root_mode docstring states the ValueError, proved by a four-case probe; calc.py equals v0.5 once docstrings are stripped"
    requirement: "REQ-old-info-findings-triaged"
    verification:
      - kind: unit
        ref: "docstring-stripped AST equality against v0.5 plus tests/test_trochoid.py: 101 passed"
        status: pass
    human_judgment: false

duration: ~10min
completed: 2026-10-21
status: complete
---

# Phase 28 Plan 03: Three comment and docstring fixes Summary

**27 IN-11, 26 IN-04 and 18 IN-07 are fixed in three comment- or docstring-only commits; no behaviour moved and the gate is green.**

## Commits (28-04 cites these)

| Finding | Commit | Subject |
|---|---|---|
| 27 IN-11 | `87d98ab` | docs(28): say the environ allowance is per top-level expression, not per statement (27 IN-11) |
| 26 IN-04 | `54f3b53` | docs(28): cite the bench record, not a phase planning path, for the image ignores and the hang runbook (26 IN-04) |
| 18 IN-07 | `9092802` | docs(28): say root_mode raises for a bad tip radius once the trochoid is requested (18 IN-07) |

## Accomplishments

- `tests/test_browser_pins.py`: the three-line "per statement" sentence is replaced by the review's text (with `(27-REVIEW IN-11)` after the first sentence). `ast.dump` of the module equals the one at `0efc87c`.
- `Makefile`: the image-ignore comment cites `bench/RESULTS.md "make test-image (26-06)"` and says the run's notes were in the Phase 26 investigation folder. Every changed line is a `#` comment.
- Hang item: `Source:` names the archived Phase 21 log (`.planning/milestones/v0.5-phases/21-.../investigation/...log`, confirmed with `test -f`) and the 26-05 evidence in `bench/RESULTS.md "Hang evidence (26-05)"`; the Runbook proof cites that section first and keeps the `26-05-stall.log` path as a secondary pointer. The hang item's `Makefile:185` citation stays right: the Makefile edit adds a line at 226, below it.
- `src/spur/calc.py`: one paragraph in `root_mode`'s docstring. With docstrings stripped, `calc.py` has the same AST as `v0.5`.

## The four probe outcomes (default `GearParams`, its `profile`)

| Call | Outcome |
|---|---|
| `requested="trochoid", rho=nan` | `ValueError: tip radius must be a finite, non-negative millimetre value, got nan` |
| `requested="trochoid", rho=-1.0` | `ValueError: ... got -1.0` |
| `requested="trochoid", rho=inf` | `ValueError: ... got inf` |
| default `requested`, `rho=-1.0` | returns `RootMode` with reason `not requested`, no raise |

All four match the sentence written.

## Gate

Command: `make verify`. Result line: `1348 passed in 236.48s (0:03:56)`, `exit 0`; import-linter `Contracts: 5 kept, 0 broken.`, `TOTAL ... 97.99%`. Each commit also passed the pre-commit hook. `git diff --exit-code v0.5 -- tests/regression/` is empty.

## Deviations from Plan

None - plan executed exactly as written. One wrap detail: the docstring paragraph was wrapped so the phrase "raises `ValueError` from `cutter` before any reason is decided" sits on one line, because the plan's automated check greps for it as one string.

## Tangent (not done, per D-15)

`test_an_environ_read_is_allowed_by_its_statement_not_its_line` in `tests/test_browser_pins.py` still says "statement", and the review suggested using the new term in names and docstrings. Renaming is a code change, left out of a comment-only commit.

## Debt ledger

No debt item was filed.

## Known Stubs

None.

## Threat Flags

None. The three commits touch comments and one docstring (T-28-10 and T-28-11 mitigations ran as AST and probe checks).

## Self-Check: PASSED

- Modified files exist; commits `87d98ab`, `54f3b53`, `9092802` are ancestors of HEAD; `commits: 3` measured from `a39cf3d..HEAD`.
- Cited headings exist once each in `bench/RESULTS.md`; the archived Phase 21 log exists; the dangling `.planning/phases/21-browser-test-of-the-viewer` path is gone from the hang item.
