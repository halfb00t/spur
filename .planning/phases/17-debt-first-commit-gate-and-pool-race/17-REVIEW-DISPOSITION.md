---
phase: 17
review: 17-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "The IN-07 comment says a wedged worker is \"left to process exit to reap\"; measured, process exit waits for it"
  - id: IN-01
    severity: info
    disposition: open
    title: "The IN-04 tripwire also misses an async comprehension"
  - id: IN-02
    severity: info
    disposition: open
    title: "`HOW_TO_DEVELOP.md` still says `make venv` installs all three hooks"
  - id: IN-03
    severity: info
    disposition: open
    title: "`STATE.md` and `PROJECT.md` still record WR-01..WR-05 as open and unfixed"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`test_hooks.py` does not pin the exact `--ignore` set, so the commit slice can shrink silently"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "A failing `pre-commit install` fails every gate run, including `make verify` and `make worktree.land`"
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "`HOW_TO_DEVELOP.md` says the push cannot be red; L36 says what pre-push does not guarantee"
  - id: WR-05
    severity: warning
    disposition: fixed
    title: "The resource-tracker debt record contradicts itself, its revisit trigger has fired, and the phase's own new test is where it struck"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "The `await`-tripwire test is anchored to exact source indentation and misses non-`await` yields"
  - id: IN-05
    severity: info
    disposition: fixed
    title: "`ci.yml` states \"no hook fires in CI\" as fact; L36 records it as an open assumption"
  - id: IN-06
    severity: info
    disposition: fixed
    title: "The Makefile's \"the four, by share\" sentence misstates the ranking, and its \"620 passed\" figure is already stale"
  - id: IN-07
    severity: info
    disposition: fixed
    title: "After `shutdown()`, a timed-out request raises `BuildTimeout` but never terminates its wedged worker"
open: 4
total: 12
recorded: 2026-10-06T11:47:32.834Z
---

# Phase 17: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| WR-02 | warning | fixed | 17-REVIEW-FIX.md (not in the current review) |
| WR-03 | warning | fixed | 17-REVIEW-FIX.md (not in the current review) |
| WR-04 | warning | fixed | 17-REVIEW-FIX.md (not in the current review) |
| WR-05 | warning | fixed | 17-REVIEW-FIX.md (not in the current review) |
| IN-04 | info | fixed | 17-REVIEW-FIX.md (not in the current review) |
| IN-05 | info | fixed | 17-REVIEW-FIX.md (not in the current review) |
| IN-06 | info | fixed | 17-REVIEW-FIX.md (not in the current review) |
| IN-07 | info | fixed | 17-REVIEW-FIX.md (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
