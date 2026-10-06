---
phase: 17-debt-first-commit-gate-and-pool-race
reviewed: 2026-10-06T00:00:00Z
depth: standard
files_reviewed: 21
files_reviewed_list:
  - .github/workflows/ci.yml
  - .pre-commit-config.yaml
  - Makefile
  - README.md
  - bench/RESULTS.md
  - bench/latency.py
  - docs/HOW_TO_DEVELOP.md
  - docs/architecture/decision_log.md
  - docs/architecture/packaging.md
  - docs/ideas/2026-09-28-reverify-after-post-verification-fixes.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md
  - docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md
  - docs/tech_debt/resolved/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md
  - scripts/pr_land.py
  - src/spur/app.py
  - src/spur/pool.py
  - tests/test_bench.py
  - tests/test_hooks.py
  - tests/test_no_fake_done.py
  - tests/test_pool.py
findings:
  critical: 0
  warning: 5
  info: 7
  total: 12
status: issues_found
---

# Phase 17: Code Review Report

**Reviewed:** 2026-10-06
**Depth:** standard
**Files Reviewed:** 21
**Status:** issues_found

## Summary

The race fix in `src/spur/pool.py` is sound. I traced the two-fact guard
(`executor_for(p) is executor and executor._processes is not None`), the `_closed` guard in
`recreate_for`, and the three branches that reach `recreate_for` (own timeout, sibling
timeout against a replaced slot, `BrokenProcessPool`). Each ends in a documented 503 and
replaces the worker once. The "nothing awaits in this branch" atomicity claim holds: the
only calls in the block are `proc.terminate()`, `recreate_for` and `worker_replaced`, all
synchronous. `tests/test_pool.py`'s stale-executor test is deterministic and does fail on
the old code. I found no correctness defect in `pool.py`, `app.py`, `bench/latency.py` or
the Makefile recipes that blocks shipping.

The defects are in the gate's robustness, in tests that claim more than they pin, and in
documents that contradict each other or the code.

- The `$(HOOKS)` stamp makes a hook-install failure fail every gate run.
- `tests/test_hooks.py` does not pin the thing it says it pins.
- One user-facing sentence about the timeout is backwards.
- `HOW_TO_DEVELOP.md` overclaims what the push stage guarantees, against L36's own caveats.
- The resource-tracker debt record contradicts itself, and its own revisit trigger has
  fired.

Verified by running: `pytest --collect-only` gives 74 tests for `tests/test_pool.py` plus
`tests/test_api.py`, matching L37's "74 passed". `make -n verify.fast` gives the expected
prefix, with one pytest line carrying the four `--ignore` flags. `pre-commit` 4.6.2 in
`.venv` does contain the "Cowardly refusing to install hooks with `core.hooksPath` set"
path (WR-03).

## Warnings

### WR-01: User-facing guidance says to raise `SPUR_BUILD_TIMEOUT` "on a bigger host", which is backwards

**File:** `README.md:97` (repeated in `docs/architecture/decision_log.md:2042` and
`docs/tech_debt/resolved/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md:123`)
**Issue:** The README tells operators that a build can return `503 timeout` under
concurrent load and to "raise the variable on a bigger host". A bigger host builds faster,
so it is the host that needs the timeout least. The failure L37 records (29.42 s alone, over
30 s at host load 5.5 to 18.9) is a slower or busier host. `app.py`'s own comment frames the
timeout as "margin for hardware slower than the measurement machine". As written, the README
points an operator who hits `503 timeout` at the opposite remedy. This is the only place
this phase tells a user what to do about the limit it documents.
**Fix:** Say what the evidence says:
```
... can exceed `SPUR_BUILD_TIMEOUT` under concurrent load and return `503` `timeout`;
on a slower or busier host, raise the variable (L37).
```
Make the same edit in L37's "The decision" paragraph and in the resolved debt's Resolution
section, which copied the phrase.

### WR-02: `test_hooks.py` does not pin the exact `--ignore` set, so the commit slice can shrink silently

**File:** `tests/test_hooks.py:115-116`
**Issue:** The module docstring says drift between the commit stage and the gate "is what
turns the drift into a red test". The test only asserts that each of the four named files
is present in `fast_pytest`:
```python
for name in HEAVY_TEST_FILES:
    assert f"--ignore=tests/{name}.py" in fast_pytest, name
```
It never asserts that nothing else is excluded. A fifth `--ignore=tests/test_hooks.py`, or
`--ignore=tests/regression`, added to `test.fast` passes every assertion. The commit stage
would then quietly stop running that file, which is the "second list of checks that drifts"
PITFALLS 14 warns about. L36 also sells the exclusion form because "a new test file runs at
commit until someone names it heavy", and a silent fifth exclusion defeats that.
**Fix:** Compare the whole set:
```python
ignored = {w.removeprefix("--ignore=") for w in fast_pytest.split() if w.startswith("--ignore=")}
assert ignored == {f"tests/{n}.py" for n in HEAVY_TEST_FILES}
```

### WR-03: A failing `pre-commit install` fails every gate run, including `make verify` and `make worktree.land`

**File:** `Makefile:59-66` (and `verify.static` at `Makefile:79`)
**Issue:** `$(HOOKS)` is a prerequisite of `verify.static`, so `make verify`,
`make verify.fast` and `make worktree.land` now all depend on `pre-commit install`
succeeding. The comment says "No `|| true`" on purpose. But `pre-commit` 4.6.2
(`.venv/.../install_uninstall.py:125`) exits 1 with "Cowardly refusing to install hooks with
`core.hooksPath` set" whenever that key is set in any config scope (a husky or global-hooks
setup, a corporate `~/.gitconfig`). On such a host the one command CLAUDE.md calls the gate
goes red with no code change, and the error is about hook installation, not the code under
test. The same applies to a checkout whose `.git/hooks` is read-only. The stamp is only
written after a successful install, so the failure repeats on every run. The Makefile's own
linked-worktree branch already shows the author considered hook install optional where it is
unsafe.
**Fix:** Keep failing loudly but make it actionable and avoid blocking the gate on an
environment the repo does not control. Either skip with a message when `core.hooksPath` is
set:
```make
@if [ -n "$$(git config --get core.hooksPath)" ]; then \
  echo "make: core.hooksPath is set; pre-commit cannot install. Hooks not installed (L36)."; \
elif [ "$$(git rev-parse --absolute-git-dir)" = "$$(git rev-parse --path-format=absolute --git-common-dir)" ]; then \
  $(VENV)/bin/pre-commit install; \
else ...
```
or move the install out of `verify.static` into `venv` only and have the gate warn when the
hooks are absent.

### WR-04: `HOW_TO_DEVELOP.md` says the push cannot be red; L36 says what pre-push does not guarantee

**File:** `docs/HOW_TO_DEVELOP.md:28`
**Issue:** "so a local commit can be red on those four while the push and `main` cannot."
L36 records the opposite for the push. The hook does not run for `--no-verify`, `SKIP=`,
tag-only pushes or delete-only pushes (scenarios 5 to 8). It runs against whatever is checked
out, so it does not verify an arbitrary sha pushed from another checkout (PITFALLS 13).
Unstaged changes are stashed, so it reads committed content. Only `main` is walled (CI, the
ruleset, `make pr.land`). A reader of HOW_TO_DEVELOP will conclude a pushed branch has
passed the gate, which L36 explicitly does not claim.
**Fix:** "...while `main` cannot: the push runs the whole gate, but `--no-verify`, `SKIP=` or
pushing a ref other than the checked-out one skips it, so CI and the ruleset are the wall
(L36)."

### WR-05: The resource-tracker debt record contradicts itself, its revisit trigger has fired, and the phase's own new test is where it struck

**File:** `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md:28`
(also `docs/tech_debt/INDEX.md`, and
`docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md:10,18`)
**Issue:** This phase appended a second occurrence to the file, but "Why it matters" still
says "One occurrence so far", and "Revisit when" still lists "fails `make verify` a second
time", which is now true. The severity stays `nice`, and the INDEX row carries the already
fired trigger unchanged. The second occurrence hit
`test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal`, which this phase
added. 17-04-stability.md shows `make verify` at 2/3 green. A gate that failed 1 of 3 full
proof runs, in a new test of a file PITFALLS 10 already flagged as flaky, was accepted by the
human but never re-triaged in the ledger. CLAUDE.md's debt rules want a fired trigger to
change the record. The worker-coverage debt has the same problem. Its trigger
("`BuildPool.shutdown`/`_run_with_timeout` is next touched") fired, and the SUMMARY says "No
change to that debt file". Its `Related files` also still cite `pool.py` "222 `export`",
which is now line 247.
**Fix:** Edit the resource-tracker record to say two occurrences. Record the outcome of the
trigger on the INDEX row, or raise the severity to `must` with a dated reason. Update the
stale line numbers in the coverage debt, or cite symbols (`BuildPool.export`) as the
resolved debt files in this phase already do.

## Info

### IN-01: `app.py` cites SC3's 30004 ms to "Phase 17" in `bench/RESULTS.md`

**File:** `src/spur/app.py:146-149`
**Issue:** The comment says "SC3 `duration_ms` 30004, bench/RESULTS.md, Phase 17". The 30004
figure is in RESULTS.md's Phase 13 section ("### Composed worst row under ten concurrent
builds (Phase 13)", line 538). Phase 17's section records 30003 from a different scenario
(`identical`). A reader following the citation lands in the wrong section.
**Fix:** "(SC3 `duration_ms` 30004, bench/RESULTS.md Phase 13; `identical` 30003, Phase 17)".

### IN-02: `_report_markdown` prints "pass bar is <= 2.00x" under the `composed` and `identical` headings

**File:** `bench/latency.py:397`
**Issue:** This phase suppressed the single/concurrent baseline line for `identical` but
left the ratio line. RESULTS.md says the `identical` p95 section "is not read against the
bar". Printing "pass bar is <= 2.00x" beside a ratio for a scenario with no bar invites that
reading. This is the L08 shape: a plausible number next to a criterion that does not apply.
**Fix:** Build the ratio line from `name`, as `baseline_line` already is: omit "pass bar"
for `composed` and `identical`.

### IN-03: `run_composed` generalised its `rows` but hard-codes `attempted=10`

**File:** `bench/latency.py:277` (`ThreadPoolExecutor(max_workers=10)` at line 246)
**Issue:** `run_composed` now takes `rows` so `identical` can reuse it, but
`ScenarioResult(label, ..., 10, refused)` and `max_workers=10` are literals. A caller passing
a different number of rows would get a wrong "N attempted" count in the report. No caller
does today.
**Fix:** `len(rows)`, and size the pool from it.

### IN-04: The `await`-tripwire test is anchored to exact source indentation and misses non-`await` yields

**File:** `tests/test_pool.py:668-716`
**Issue:** `_awaits_in_timeout_handler` looks only for `ast.Await`. An `async with` or
`async for` (or `await`-free `yield`) inside the handler reopens the same window and is not
detected. The seeded-await half also depends on the literal 12-space
`"            raise BuildTimeout("` string, so a reformat of that line fails the test with an
opaque `src.count(anchor) == 1`, not with a message about what moved.
**Fix:** Walk for `(ast.Await, ast.AsyncWith, ast.AsyncFor)`. Derive the seeded insertion
from the AST (for example, the `raise` node's `lineno`) instead of a string anchor.

### IN-05: `ci.yml` states "no hook fires in CI" as fact; L36 records it as an open assumption

**File:** `.github/workflows/ci.yml:28`
**Issue:** L36 says assumptions A1 and A3 (CI installs the hooks and fires none) "stay open
until the phase's first CI run is read at ship". The workflow comment asserts it
unconditionally. Harmless today (CI never commits), but it is a claim the repo has not
verified on its own runner.
**Fix:** Soften to "(none is expected to fire; L36 A1)" until the first CI run is read.

### IN-06: The Makefile's "the four, by share" sentence misstates the ranking, and its "620 passed" figure is already stale

**File:** `Makefile:147-155`
**Issue:** The comment lists the four heavy files "by share of pytest's seconds"
(74.1 %, 8.5 %, 4.8 %) and calls `tests/test_cli.py` "the fourth". By RESULTS.md's
"Per-file share" table the fourth by share is `tests/regression/test_pre_v0_2.py` (7.8 %).
`test_cli.py` (4.3 %) is fifth. The fixture replay is kept at commit on purpose (L36: "keeps
the fixture replay ... at the commit boundary"), but the Makefile comment never says so.
The pricing line "620 passed in 10.75 s" is also a snapshot: the slice collects 622 tests
at HEAD (measured). No check watches the slice's 30 s budget as it grows.
**Fix:** Add "(`tests/regression/test_pre_v0_2.py` at 7.8 % is kept on purpose: L36)" and
date-stamp the count, or drop the count.

### IN-07: After `shutdown()`, a timed-out request raises `BuildTimeout` but never terminates its wedged worker

**File:** `src/spur/pool.py:228-235`
**Issue:** Before this phase that path crashed with `AttributeError`. Now the guard skips
the terminate block because `_processes` is `None`, so the documented 503 is raised while
the wedged worker process survives (`shutdown(wait=False)` never kills a running task). The
comment and PITFALLS 9 note that reachability through uvicorn's graceful shutdown is
unmeasured (A4). This is not a regression, and a process-group exit probably reaps the
worker in the container. It is worth one sentence in the comment so the next reader does not
assume the `_closed` path also cleans up.
**Fix:** Note in the comment that the closed-pool path answers the request but leaves worker
reaping to process exit.

---

_Reviewed: 2026-10-06_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
