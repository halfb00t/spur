---
phase: 17-debt-first-commit-gate-and-pool-race
fixed_at: 2026-10-06T00:00:00Z
review_path: .planning/phases/17-debt-first-commit-gate-and-pool-race/17-REVIEW.md
iteration: 2
findings_in_scope: 16
fixed: 16
skipped: 0
status: all_fixed
---

# Phase 17: Code Review Fix Report

**Fixed at:** 2026-10-06
**Source review:** .planning/phases/17-debt-first-commit-gate-and-pool-race/17-REVIEW.md
**Iteration:** 2

**Summary:**
- Findings in scope: 16 (12 from the earlier review, fixed in iteration 1; 4 from the incremental re-review, fixed in iteration 2; scope `all`, no critical findings)
- Fixed: 16
- Skipped: 0

**Id reuse:** the incremental re-review reuses the ids WR-01, IN-01, IN-02 and IN-03 for four different findings. The twelve earlier entries below carry an "(earlier review, `c604370`)" marker in their headings; the four new entries come first under "Iteration 2".

**Where it ran:** `workflow.use_worktrees` is `false` in `.planning/config.json`, so every edit, commit and gate run happened in the main checkout on `gsd/phase-17-debt-first-commit-gate-and-pool-race`. No worktree, temp branch or recovery sentinel was created. `.planning/state.json` was modified before the run and was never staged.

**Verification:** `make verify` after the last fix commit of iteration 2 (`90307d4`): `944 passed in 77.75s (0:01:17)`, coverage `97.25%` (floor 96.0% reached). ruff, mypy, import contracts and the unfinished-work scan are part of that command and passed. No resource-tracker flake hit this run. Iteration 1's gate, after `366d6d4`: `944 passed in 79.14s (0:01:19)`, coverage `97.25%`; its first (WR) pass read `944 passed in 65.48s`, `97.25%`. All three ran in the main checkout.

## Fixed Issues

### Iteration 2 (incremental re-review)

### WR-01: The IN-07 comment says a wedged worker is "left to process exit to reap"; measured, process exit waits for it

**Files modified:** `src/spur/pool.py`
**Commit:** 98f2350
**Applied fix:** Comment only, no behaviour change. I reproduced the measurement before writing the figure, with a scratchpad script (not in the repo) on the project's Python 3.12.13: spawn-context `ProcessPoolExecutor(max_workers=1)`, an 8 s task, `shutdown(wait=False)` at 1.5 s. `main done` printed at 1.51 s and the interpreter exited at 8.10 s (`time -p` real). The reviewer measured 8.13 s; the comment carries my figure, 8.10 s. It now says the guard skips the terminate, `shutdown(wait=False)` never kills a running task, and the interpreter's exit joins the executor's manager thread and waits for the task, so a wedged worker is not reaped. The uvicorn-reachability sentence is unchanged (still unmeasured, PITFALLS 9, A4). The reviewer's optional follow-up (file a debt item that a hung shutdown can block process exit, trigger "`BuildPool.shutdown` is next touched") was not asked for as a fix and I filed nothing; the human may want it.

### IN-01: The IN-04 tripwire also misses an async comprehension

**Files modified:** `tests/test_pool.py`
**Commit:** 95a2679
**Applied fix:** `_suspensions_in_timeout_handler` now also reports `ast.ListComp`, `SetComp`, `DictComp` and `GeneratorExp` nodes with an async generator (`any(each.is_async for each in node.generators)`). These nodes carry the line number; `ast.comprehension` itself does not, so I walked the enclosing node rather than the `ast.comprehension` the review named. A fourth seed, `_ = [x async for x in aiter(())]`, is placed before the handler's `raise` by the existing AST-derived position. The docstrings say four forms. Checked both ways: `make test PYTEST_ARGS="tests/test_pool.py -k never_awaits -q --no-cov -n0"` gave 2 passed on the shipped code; with the comprehension clause removed the new seed failed (`assert [] != []`, seed `_ = [x async for x in aiter(())]`) and the other test passed. The red-check removal was reverted with `git checkout` before it was committed, which also dropped the uncommitted real edit, so I re-applied it and re-ran the check; the committed diff is the intended one. Status: fixed. The `yield` caveat from iteration 1 still stands.

### IN-02: `HOW_TO_DEVELOP.md` still says `make venv` installs all three hooks

**Files modified:** `docs/HOW_TO_DEVELOP.md`
**Commit:** a591a88
**Applied fix:** The sentence now reads "Run `make venv` once in the main checkout and it installs all three hooks, unless `core.hooksPath` is set: then the gate prints a message and installs nothing." `docs/architecture/decision_log.md` L36 is not edited (append-only, per the instruction); the Makefile message's `(L36)` pointer is also unchanged. L36's text still does not record the `core.hooksPath` branch, which was the review's other half; I left it as the decision log's rules require.

### IN-03: `STATE.md` and `PROJECT.md` still record WR-01..WR-05 as open and unfixed

**Files modified:** `.planning/STATE.md`, `.planning/PROJECT.md`
**Commit:** 90307d4
**Applied fix:** One commit, surgical edits to the existing sentences. STATE.md: the Phase 17 review bullet (Blockers/Concerns) now says the twelve findings are fixed (`17-REVIEW-FIX.md`, `9927f3c`...`366d6d4`), that WR-01's "bigger host" clause was corrected in `9927f3c`, and that the incremental re-review raised four further items being fixed now; the first Operator Next Steps bullet's "Before ship" clause says the same. PROJECT.md: the Phase 17 Validated entry's "review 0 critical / 5 warning / 7 info open" clause and the L37 Outcome cell's "fix before ship" tail now record the fix and the four re-review items. Not touched: the neighbouring STATE.md resource-tracker bullet still says the debt file "still reads 'One occurrence so far'" (review WR-05), which `daa954a` made stale. It is outside the listed sites, so I left it for whoever closes the review loop.

### Earlier review (`c604370`, iteration 1)

### WR-01: User-facing guidance says to raise `SPUR_BUILD_TIMEOUT` "on a bigger host", which is backwards (earlier review, `c604370`)

**Files modified:** `README.md`, `docs/architecture/decision_log.md`, `docs/tech_debt/resolved/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`
**Commit:** 9927f3c
**Applied fix:** All three places now say a slower or busier host raises the variable. The `decision_log.md` edit is to L37's own paragraph, which this phase added and has not shipped. It is a wording correction, not a re-litigation of the decision; L36's text is untouched.

### WR-02: `test_hooks.py` does not pin the exact `--ignore` set, so the commit slice can shrink silently (earlier review, `c604370`)

**Files modified:** `tests/test_hooks.py`
**Commit:** b863105
**Applied fix:** The per-name membership loop is replaced by a set-equality assertion over every `--ignore=` word in the `test.fast` pytest line. `make test PYTEST_ARGS="tests/test_hooks.py -q --no-cov -n0"` passed (3 passed) against the current recipe before the commit. Status: fixed. The assertion is a test change, not a logic change in shipped code.

### WR-03: A failing `pre-commit install` fails every gate run, including `make verify` and `make worktree.land` (earlier review, `c604370`)

**Files modified:** `Makefile`, `tests/test_hooks.py`
**Commit:** bc1318f
**Applied fix:** The reviewer's first option, narrowed. When `git config --get core.hooksPath` is non-empty the `$(HOOKS)` recipe prints an actionable message and installs nothing. The main-checkout install and the linked-worktree skip are unchanged, so L36's "installs from the main checkout only" still holds, and I judged this a hardening, not a change to L36's contract. One deliberate detail: `touch $@` moved inside the install and worktree branches. In the `core.hooksPath` branch the stamp is not written, so the message repeats on every gate run until the key is unset, and the hooks get installed then. A failing `pre-commit install` in the main checkout still fails the gate (`install && touch`). New test `test_the_hook_stamp_skips_loudly_when_core_hooks_path_is_set` pins it: no install call, message present, no stamp. I confirmed it fails against the previous Makefile (1 failed, 3 passed) and passes against the new one (4 passed). Status: fixed, requires human verification (conditional logic in a recipe; the tests cover the three branches but only against a shim, not real `pre-commit` under a real `core.hooksPath`).

### WR-04: `HOW_TO_DEVELOP.md` says the push cannot be red; L36 says what pre-push does not guarantee (earlier review, `c604370`)

**Files modified:** `docs/HOW_TO_DEVELOP.md`
**Commit:** 15a3f51
**Applied fix:** The sentence now reads "while `main` cannot: the push runs the whole gate, but `--no-verify`, `SKIP=` or pushing a ref other than the checked-out one skips it, so CI and the ruleset are the wall (`L36`)."

### WR-05: The resource-tracker debt record contradicts itself, its revisit trigger has fired, and the phase's own new test is where it struck (earlier review, `c604370`)

**Files modified:** `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md`, `docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md`, `docs/tech_debt/INDEX.md`
**Commit:** daa954a
**Applied fix:**
- Resource tracker: "Why it matters" now says two occurrences (second: `b8ef84a`, run 2 of 17-04's stability runs, worker `gw2`, load 17.54, `test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal`; `make verify` 2 of 3 green). "Revisit when" records that the "fails a second time" trigger fired on 2026-10-06 and sets a new named trigger: a third failure, or `[tool.coverage.run] concurrency` next touched, or the `-n 0` / no-`--cov` isolation runs done. Severity stays `nice`.
- Worker coverage: stale `pool.py` line numbers replaced by `build_export` and `BuildPool.export`; the Phase 17 firing of its trigger is recorded with the outcome (`pool.py` 100.00 % in 43 of 43 runs, not observed, cause still unestablished). The next-touch trigger is reworded to "after Phase 17".
- INDEX rows for both items match the new triggers.

**Open question for the human:** whether the resource-tracker debt should escalate to `must`. A gate that failed 1 of 3 full proof runs is arguable. Under CLAUDE.md a `must` that is a blocker-shaped gate defect would mean fix now or stop and ask. I did not make that call; the file says so too.

### IN-01: `app.py` cites SC3's 30004 ms to "Phase 17" in `bench/RESULTS.md` (earlier review, `c604370`)

**Files modified:** `src/spur/app.py`
**Commit:** 0568d0d
**Applied fix:** Comment only. Both figures checked against `bench/RESULTS.md` first: 30004 is in "Composed worst row under ten concurrent builds (Phase 13)", 30003 is in "Same-slot timeout race (Phase 17)" (the `identical` scenario). The comment now names each section.

### IN-02: `_report_markdown` prints "pass bar is <= 2.00x" under the `composed` and `identical` headings (earlier review, `c604370`)

**Files modified:** `bench/latency.py`, `tests/test_bench.py`
**Commit:** fee06da
**Applied fix:** The ratio line is built from the same `name` test as `baseline_line`; `composed` and `identical` print the ratio with no bar, `single` and `concurrent` are unchanged. `test_the_composed_report_omits_the_single_concurrent_baseline_line` now also asserts both sides. `make test PYTEST_ARGS="tests/test_bench.py -q --no-cov -n0"`: 26 passed.

### IN-03: `run_composed` generalised its `rows` but hard-codes `attempted=10` (earlier review, `c604370`)

**Files modified:** `bench/latency.py`
**Commit:** edfb0dc
**Applied fix:** `ThreadPoolExecutor(max_workers=len(rows))` and `ScenarioResult(..., len(rows), refused)`. Both existing callers pass ten rows, so the report is unchanged. No new test: nothing in the suite drives `run_composed` against a server, and no caller passes another length. `tests/test_bench.py`: 26 passed.

### IN-04: The `await`-tripwire test is anchored to exact source indentation and misses non-`await` yields (earlier review, `c604370`)

**Files modified:** `tests/test_pool.py`
**Commit:** 0922c85
**Applied fix:** The helper is split into `_timeout_handler` and `_suspensions_in_timeout_handler`, which walks `(ast.Await, ast.AsyncWith, ast.AsyncFor)`. The tripwire half seeds each of the three forms before the handler's `raise`, placed from that node's `lineno` and `col_offset`, with no source-string anchor. Checked both ways: green on the shipped code (`-k never_awaits`: 2 passed), and red when a real `await asyncio.sleep(0)` was seeded into `pool.py` (`assert [232] == []`; reverted with `git checkout`). The first commit attempt was refused by the pre-commit hook for an E501 line in the edited docstring; the docstring was reflowed and the commit made once, after the hook passed. The review's `yield` remark is not covered: its Fix line names only the three async nodes. Status: fixed.

### IN-05: `ci.yml` states "no hook fires in CI" as fact; L36 records it as an open assumption (earlier review, `c604370`)

**Files modified:** `.github/workflows/ci.yml`
**Commit:** 968eb21
**Applied fix:** Comment only: "none is expected to fire in CI (L36 A1, open until the phase's first CI run is read)". The YAML still parses.

### IN-06: The Makefile's "the four, by share" sentence misstates the ranking, and its "620 passed" figure is already stale (earlier review, `c604370`)

**Files modified:** `Makefile`
**Commit:** a236a22
**Applied fix:** Comment only, no recipe change. Ranking checked against `bench/RESULTS.md` "Per-file share": `tests/regression/test_pre_v0_2.py` 7.8 %, `tests/test_cli.py` 4.3 %. The comment now says `test_cli.py` is the fourth by D-02, not by share, and that the fixture replay stays in the slice on purpose (L36). The "620 passed" line is marked a snapshot, with a new count that I re-measured: `pytest --collect-only` with the four `--ignore` flags collected 623 tests on 2026-10-06. (The review's 622 predates the test WR-03 added.) `tests/test_hooks.py`: 4 passed.

### IN-07: After `shutdown()`, a timed-out request raises `BuildTimeout` but never terminates its wedged worker (earlier review, `c604370`)

**Files modified:** `src/spur/pool.py`
**Commit:** 366d6d4
**Applied fix:** Comment only: the closed-pool path answers the request but leaves worker reaping to process exit, and its reachability under uvicorn's graceful shutdown stays unmeasured (PITFALLS 9, A4). The "leaves worker reaping to process exit" half was wrong and is corrected by iteration 2's WR-01 (`98f2350`).

## Skipped Issues

None.

---

_Fixed: 2026-10-06_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 2_
