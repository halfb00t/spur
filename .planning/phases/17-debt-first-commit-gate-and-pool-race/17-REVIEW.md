---
phase: 17-debt-first-commit-gate-and-pool-race
reviewed: 2026-10-06T00:00:00Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - .github/workflows/ci.yml
  - Makefile
  - README.md
  - bench/latency.py
  - docs/HOW_TO_DEVELOP.md
  - docs/architecture/decision_log.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md
  - docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md
  - docs/tech_debt/resolved/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md
  - src/spur/app.py
  - src/spur/pool.py
  - tests/test_bench.py
  - tests/test_hooks.py
  - tests/test_pool.py
findings:
  critical: 0
  warning: 1
  info: 3
  total: 4
status: issues_found
---

# Phase 17: Code Review Report (incremental re-review after the 12 fixes)

**Reviewed:** 2026-10-06
**Depth:** standard
**Files Reviewed:** 15
**Status:** issues_found

## Summary

Scope was `git diff c604370 HEAD` over the 15 files (143 insertions, 48 deletions, 12 fix commits).
Each of the twelve earlier findings was re-read against the current source. All twelve are
fixed correctly. The fixes introduced one factual defect, in the IN-07 comment about what
happens to a wedged worker at process exit, plus three small leftovers.

Checks run: `ruff check .` clean; `mypy` strict on 39 files clean; `pytest tests/test_hooks.py
tests/test_bench.py --no-cov -n0` 30 passed; `pytest tests/test_pool.py -k "never_awaits or
closed_pool"` 3 passed; `pytest --collect-only` with the four `--ignore` flags collects 623
tests, which matches the Makefile's new snapshot figure. `make -n verify.fast` shows the
unchanged static prefix and the four-`--ignore` pytest line. The live bench and the full gate
were not run.

Fix verification, one line each:

- WR-01: "slower or busier host" now appears in `README.md`, L37 and the resolved race debt. No
  "bigger host" remains in `src/`, `docs/` or `README.md`. The remaining hits are in
  `.planning/` (see IN-03).
- WR-02: the set-equality assertion over every `--ignore=` word is correct. It compares against
  `HEAVY_TEST_FILES`, so adding or dropping an ignore fails the test.
- WR-03: the guard matches pre-commit 4.6.2's own check (`git config core.hooksPath`, read from
  `.venv/.../git.py:180` and `install_uninstall.py:123`). `install && touch $@` keeps a failed
  install red, and the `if` compound's exit status is the last branch's. The stamp is left
  untouched on the skip branch, so the message repeats, as the comment says. The new test runs
  under `_clean_git_env()`, so a host-global `core.hooksPath` cannot leak into the other two
  stamp tests.
- WR-04, WR-05, IN-01, IN-05, IN-06: wording and records match their sources. The 30004 figure
  is in the SC3 table as `30.004 s`. The 7.8 % and 4.3 % shares match "Per-file share". `b8ef84a`
  resolves, and the 43-run tally matches `17-04-SUMMARY.md`.
- IN-02, IN-03: `has_bar` gates the baseline line and the bar together. The implicit string
  concatenation still binds before the ternary, so the baseline line is unchanged. Both
  `max_workers` and `attempted` now follow `len(rows)`. Every `run_composed` caller passes ten
  rows, so the report is unchanged.
- IN-04: the helper walks `Await`, `AsyncWith` and `AsyncFor`, and the seed is placed from the
  `raise` node's `lineno` and `col_offset`, so it no longer depends on source indentation.
- IN-07: the comment was added, but it states the wrong mechanism (WR-01 below).

## Warnings

### WR-01: The IN-07 comment says a wedged worker is "left to process exit to reap"; measured, process exit waits for it

**File:** `src/spur/pool.py:227-231`
**Issue:** The new comment says that after `shutdown()` the timeout path only answers the
request, and that "a wedged worker is left to process exit to reap (`shutdown(wait=False)` never
kills a running task)". The second half is true. The first half describes a mechanism that
measurement contradicts. CODING_VALUES makes this the project's standard: a comment carries the
measurement, and an unmeasured claim is not stated as fact.

Probe, run with the project's Python 3.12.13: a spawn-context `ProcessPoolExecutor(max_workers=1)`
running an 8 s task, `shutdown(wait=False)` called 1.5 s in, then the main thread returns.
`main done` printed immediately and the interpreter exited 8.13 s after start. So `shutdown(wait=False)`
does not let the process exit while the worker is busy. `concurrent.futures`' atexit hook joins
the executor's manager thread, which waits for the running task. Exit does not reap the worker. It
blocks on it. A truly wedged OCCT build would hold the process until it ends, or until the
supervisor's SIGKILL (the Docker stop grace period).

This is not a regression. `BuildPool.shutdown()` has always done this. The comment, however,
tells the next reader that process exit handles it, which would stop them from seeing a
shutdown that can hang. The "unmeasured" hedge in the last sentence covers only whether uvicorn
reaches the path, not the exit behaviour, and that part is measurable.

**Fix:** Replace the claim with the measurement:

```python
            # ... After `shutdown()` that answer is all this path gives: the guard skips
            # the terminate, and `shutdown(wait=False)` never kills a running task, so a
            # wedged worker is not reaped: the interpreter's exit joins the executor's
            # manager thread and waits for the task (8 s task, `shutdown(wait=False)` at
            # 1.5 s, interpreter exit at 8.13 s, Python 3.12.13, 2026-10-06). Whether
            # uvicorn's graceful shutdown can reach this path is unmeasured (PITFALLS 9, A4).
```

If a hung shutdown is not acceptable, file it in `docs/tech_debt/active/` with the trigger
"`BuildPool.shutdown` is next touched". Terminating `executor._processes` inside `shutdown()`
is the likely fix, but it is a behaviour change, so it is not asked for here.

## Info

### IN-01: The IN-04 tripwire also misses an async comprehension

**File:** `tests/test_pool.py:683-690`
**Issue:** The known caveat is an `await`-free `yield`. A separate gap: `[x async for x in aiter()]`
suspends the loop through `ast.comprehension(is_async=1)` and produces no `Await`, `AsyncWith` or
`AsyncFor` node, so `_suspensions_in_timeout_handler` reports nothing for it. It is the same
class of miss as `yield`, not covered by the three seeds.
**Fix:** Add an `ast.comprehension` check to the helper and a fourth seed:

```python
if isinstance(node, (ast.Await, ast.AsyncWith, ast.AsyncFor))
or (isinstance(node, ast.comprehension) and node.is_async)
# seed: "_ = [x async for x in aiter(())]\n"
```

### IN-02: `HOW_TO_DEVELOP.md` still says `make venv` installs all three hooks

**File:** `docs/HOW_TO_DEVELOP.md:30-31`
**Issue:** WR-03 added a branch where `make venv` installs nothing (`core.hooksPath` set). The
sentence "Run `make venv` once in the main checkout and it installs all three hooks" is now
unconditional and false for that host. L36's text does not record the branch either. The Makefile
message cites L36 as if it did.
**Fix:** Append "(unless `core.hooksPath` is set: pre-commit refuses, the stamp prints a
message and installs nothing)" to the HOW_TO_DEVELOP sentence. Add one clause to L36, or drop the
`(L36)` pointer from the Makefile echo.

### IN-03: `STATE.md` and `PROJECT.md` still record WR-01..WR-05 as open and unfixed

**File:** `.planning/STATE.md:348-352` and `:517-518`; `.planning/PROJECT.md:575`
**Issue:** STATE.md says "`17-REVIEW-DISPOSITION.md`, 12 open ... fix all three in one commit
before ship" and "Before ship: fix review WR-01's backwards 'bigger host' clause". The
disposition file now records 12 fixed and 0 open. PROJECT.md's L37 row ends "review WR-01 ...
fix before ship". A later session reading STATE first would redo or distrust finished work. These
are planning files outside the reviewed source list, so this is a note for whoever closes the
review loop.
**Fix:** Update the STATE.md lines to "12 fixed, 0 open (17-REVIEW-DISPOSITION.md)" and strike
the "fix before ship" tail from the PROJECT.md L37 row.

---

_Reviewed: 2026-10-06_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
