---
phase: 17-debt-first-commit-gate-and-pool-race
fixed_at: 2026-10-06T00:00:00Z
review_path: .planning/phases/17-debt-first-commit-gate-and-pool-race/17-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 17: Code Review Fix Report

**Fixed at:** 2026-10-06
**Source review:** .planning/phases/17-debt-first-commit-gate-and-pool-race/17-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 5 (WR-01 to WR-05; scope `critical_warning`, no critical findings)
- Fixed: 5
- Skipped: 0

**Where it ran:** `workflow.use_worktrees` is `false` in `.planning/config.json`, so every edit, commit and gate run happened in the main checkout on `gsd/phase-17-debt-first-commit-gate-and-pool-race`. No worktree, temp branch or recovery sentinel was created. `.planning/state.json` was modified before the run and was never staged.

**Verification:** `make verify` after the last fix commit: `944 passed in 65.48s`, coverage `97.25%` (floor 96.0% reached). ruff, mypy, import contracts and the unfinished-work scan are part of that command and passed. No resource-tracker flake hit this run.

## Fixed Issues

### WR-01: "raise `SPUR_BUILD_TIMEOUT` on a bigger host" is backwards

**Files modified:** `README.md`, `docs/architecture/decision_log.md`, `docs/tech_debt/resolved/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`
**Commit:** 9927f3c
**Applied fix:** All three places now say a slower or busier host raises the variable. The `decision_log.md` edit is to L37's own paragraph, which this phase added and has not shipped. It is a wording correction, not a re-litigation of the decision; L36's text is untouched.

### WR-02: `test_hooks.py` does not pin the exact `--ignore` set

**Files modified:** `tests/test_hooks.py`
**Commit:** b863105
**Applied fix:** The per-name membership loop is replaced by a set-equality assertion over every `--ignore=` word in the `test.fast` pytest line. `make test PYTEST_ARGS="tests/test_hooks.py -q --no-cov -n0"` passed (3 passed) against the current recipe before the commit. Status: fixed. The assertion is a test change, not a logic change in shipped code.

### WR-03: A failing `pre-commit install` fails every gate run

**Files modified:** `Makefile`, `tests/test_hooks.py`
**Commit:** bc1318f
**Applied fix:** The reviewer's first option, narrowed. When `git config --get core.hooksPath` is non-empty the `$(HOOKS)` recipe prints an actionable message and installs nothing. The main-checkout install and the linked-worktree skip are unchanged, so L36's "installs from the main checkout only" still holds, and I judged this a hardening, not a change to L36's contract. One deliberate detail: `touch $@` moved inside the install and worktree branches. In the `core.hooksPath` branch the stamp is not written, so the message repeats on every gate run until the key is unset, and the hooks get installed then. A failing `pre-commit install` in the main checkout still fails the gate (`install && touch`). New test `test_the_hook_stamp_skips_loudly_when_core_hooks_path_is_set` pins it: no install call, message present, no stamp. I confirmed it fails against the previous Makefile (1 failed, 3 passed) and passes against the new one (4 passed). Status: fixed, requires human verification (conditional logic in a recipe; the tests cover the three branches but only against a shim, not real `pre-commit` under a real `core.hooksPath`).

### WR-04: `HOW_TO_DEVELOP.md` says the push cannot be red

**Files modified:** `docs/HOW_TO_DEVELOP.md`
**Commit:** 15a3f51
**Applied fix:** The sentence now reads "while `main` cannot: the push runs the whole gate, but `--no-verify`, `SKIP=` or pushing a ref other than the checked-out one skips it, so CI and the ruleset are the wall (`L36`)."

### WR-05: Resource-tracker debt contradicts itself, trigger fired

**Files modified:** `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md`, `docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md`, `docs/tech_debt/INDEX.md`
**Commit:** daa954a
**Applied fix:**
- Resource tracker: "Why it matters" now says two occurrences (second: `b8ef84a`, run 2 of 17-04's stability runs, worker `gw2`, load 17.54, `test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal`; `make verify` 2 of 3 green). "Revisit when" records that the "fails a second time" trigger fired on 2026-10-06 and sets a new named trigger: a third failure, or `[tool.coverage.run] concurrency` next touched, or the `-n 0` / no-`--cov` isolation runs done. Severity stays `nice`.
- Worker coverage: stale `pool.py` line numbers replaced by `build_export` and `BuildPool.export`; the Phase 17 firing of its trigger is recorded with the outcome (`pool.py` 100.00 % in 43 of 43 runs, not observed, cause still unestablished). The next-touch trigger is reworded to "after Phase 17".
- INDEX rows for both items match the new triggers.

**Open question for the human:** whether the resource-tracker debt should escalate to `must`. A gate that failed 1 of 3 full proof runs is arguable. Under CLAUDE.md a `must` that is a blocker-shaped gate defect would mean fix now or stop and ask. I did not make that call; the file says so too.

## Skipped Issues

None. Info findings IN-01 to IN-07 were out of scope (`fix_scope: critical_warning`) and remain open.

---

_Fixed: 2026-10-06_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
