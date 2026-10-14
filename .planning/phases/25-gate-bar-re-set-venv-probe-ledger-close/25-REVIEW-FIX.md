---
phase: 25-gate-bar-re-set-venv-probe-ledger-close
fixed_at: 2026-10-14T00:00:00Z
review_path: .planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 25: Code Review Fix Report

**Fixed at:** 2026-10-14
**Source review:** `.planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/25-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (WR-01, WR-02, WR-03; IN-01..IN-05 out of scope)
- Fixed: 3
- Skipped: 0

**Where it ran:** `workflow.use_worktrees` is `false` in `.planning/config.json`, so no worktree was created. Every edit, `make verify` run and commit was in the main checkout, on branch `gsd/phase-25-gate-bar-re-set-venv-probe-ledger-close`. The gate numbers below are reproducible from this tree.

**Verification (whole set):**
- `make verify`, run once on the combined working tree before the commits were split: exit 0, `1318 passed in 188.62s (0:03:08)`, `TOTAL 1358 22 386 13 97.99%`, `Required test coverage of 96.0% reached`, `real 189.22`.
- `make verify`, run again on the final committed tree (HEAD `f7ce3ab`, after the docs text was re-wrapped while splitting commits): exit 0, `1318 passed in 207.89s (0:03:27)`, coverage `Total coverage: 97.99%`. Neither run is a gate reading and neither enters L43's bar.
- `1318` is Phase 25's `1317` plus the one new test.
- Each commit also ran the pre-commit `make verify.fast` hook and `no-skip-token`: both `Passed`.
- Orchestrator follow-up `a9cf1d8`: the WR-02 and WR-03 edits had joined sentences onto existing L43 lines, leaving three at 153, 186 and 206 columns in a file that wraps near 120. Re-wrapped only; wording unchanged. Pre-commit `make verify.fast`: `Passed`.

## Fixed Issues

### WR-01: No test covers the shipped `-c requirements.txt` or the new stamp prerequisite

**Files modified:** `tests/test_hooks.py` (new test inserted at lines 162-179, before `test_the_image_suite_ignores_the_browser_test`)
**Commit:** `79958f1`
**Applied fix:** Added `test_the_dev_venv_installs_under_the_closure_and_reinstalls_when_it_moves`. The existing `_dry_run(target)` helper takes one target and bakes in `-o .venv/.browser`, so the review's snippet did not fit it. The test runs its own `make -n --no-print-directory -W requirements.txt .venv/.installed`, in the style of the neighbouring `dry_run_forcing_the_install`. `-W requirements.txt` pretends the file just changed, so the stamp recipe is printed only if the file is a prerequisite of `$(STAMP)`. It then asserts the printed `pip install -e` line carries `-c requirements.txt` exactly once. This covers both halves of the finding (the flag and the prerequisite) in one test.
**Verification:**
- `.venv/bin/python -m pytest tests/test_hooks.py -q --no-cov` on the edited file: `7 passed in 0.67s`.
- Mutation check, Makefile restored afterwards with `git checkout -- Makefile` (`git status` clean for it): with `requirements.txt` removed from the `$(STAMP)` prerequisites the new test failed, `1 failed in 0.02s` (assertion at `tests/test_hooks.py:176`); with `-c requirements.txt` removed from the install line it failed, `1 failed in 0.02s` (`:177`).
- `make verify`: exit 0, `1318 passed in 188.62s (0:03:08)` (see above).

### WR-02: L43 and RESULTS word the adoption proof and the build-constraint caveat as observed when they are inferred

**Files modified:** `docs/architecture/decision_log.md` (L43, "The venv probe" paragraph, about lines 2899-2910), `bench/RESULTS.md` ("The venv probe (25-03)", `#### Outcome`, last paragraph, about line 5932)
**Commit:** `31d0f81`
**Applied fix:** Took the reword option. Nothing was rebuilt: no `make clean`, no `make venv`, `.venv` untouched.
- L43 no longer says the probe "proves the adoption". It now says the probe set `PIP_CONSTRAINT` to an absolute path on the pre-change Makefile, the shipped recipe passes `-c` with a relative path, pip merges the two, so the shipped line is expected to behave as the probe did, and that this is an inference (no probe ran `make venv` with `-c` as shipped).
- L43 and RESULTS no longer say `hatchling` "builds / built unconstrained" as an observation. They cite pip's 2026-07-29 news, as cached in `.planning/research/PITFALLS.md` (line 389, checked), say `hatchling` is expected to build unconstrained, and say the 25-03 logs hold no `hatchling` or build-isolation line.
- The L43 decision itself (300 s bar, `-c requirements.txt`, stamp prerequisite) is unchanged.
**Verification:**
- Re-read of both edited passages after the edit: text present, surrounding paragraphs intact.
- `make verify`: exit 0, `1318 passed in 188.62s (0:03:08)` on the combined tree, and `1318 passed in 207.89s (0:03:27)` on the final tree.
- Not run: any fresh `make venv`; the review's dry-run result that the shipped line resolves is the reviewer's, and I did not repeat it.

### WR-03: The 300 s bar is stated without the same-host gate readings that exceed it

**Files modified:** `docs/architecture/decision_log.md` (L43 "The bar", about lines 2887-2900), `.pre-commit-config.yaml:9-13`
**Commit:** `f7ce3ab`
**Status note:** fixed, but **the finding's premise is partly wrong and the fix was adapted**; see below. Requires a human glance at the L43 wording.
**Applied fix:**
- I read the four figures from `bench/RESULTS.md` lines 5538-5543 and the logs under `.planning/phases/24-bore-shape-selector/investigation/` before writing them: `1 failed, 1294 passed in 296.91s` (24-01 first run, `24-01-red-1.log`), `1295 passed in 272.91s` (24-01 re-run), `1311 passed in 294.40s` (24-02), `1311 passed in 336.15s` (24-03).
- The review calls these "same M5 host" readings and the 296.91 s run a green one. Both are wrong. `24-01-SUMMARY.md:213` and `24-03-SUMMARY.md:167` record the host as an Apple M2 Max (24-04, same phase, records `12 CPUs, 32.0 GiB`); `24-02-SUMMARY.md` names no host. The 296.91 s run was red (`test_health_reports_pool_state`, the resource-tracker flake). The figures are pytest-reported seconds, not `make verify` `real`. L43 itself says no figure is carried from one host to another (L08), so writing them as M5 readings would have been a wrong number.
- Loads: only two are recorded. 296.91 s read at a host load of 15.6 (`24-01-SUMMARY.md:244`); 336.15 s at load averages `5.36 4.71 6.68` at the start (`24-03-SUMMARY.md:220`). For 272.91 s and 294.40 s no load is recorded anywhere I looked, and L43 says "load not recorded" rather than a figure.
- L43 "The bar" now says the bar is not a ceiling the gate has been read under, that this host has no loaded full-gate reading, quotes the four Phase 24 figures as read with their host, HEAD/test-count and unit caveats, states that 336.15 s is above 300 s, and says 300 s is a human-set figure whose behaviour on the M5 Max under load is unread. I did not write the review's "nearly twofold spread" (it compares readings from two different hosts).
- `.pre-commit-config.yaml`: dropped "read on 2026-10-14". It now says the 300 s is "a figure the human set, not a reading" and names the two non-decisive readings, `179.21 s and 195.23 s`, separately.
- Not changed: `README.md:310`, `docs/HOW_TO_DEVELOP.md` and `docs/architecture/packaging.md` also quote the bar with its host. The finding's Fix names only L43 and `.pre-commit-config.yaml`, so I left them; they already say "bar 300 s on an 18-CPU Apple M5 Max", which remains true.
**Verification:**
- Re-read of both edits: present, surrounding text intact.
- `make verify`: exit 0, `1318 passed in 207.89s (0:03:27)` on the final tree.
- `.pre-commit-config.yaml` is read by `tests/test_hooks.py` (`_hook_blocks`); that file passed (`7 passed`) before and inside the gate runs.

## Skipped Issues

None. IN-01 to IN-05 were out of scope (`fix_scope: critical_warning`) and were not touched.

## Filed items

No `docs/ideas/` or `docs/tech_debt/` item was filed.

---

_Fixed: 2026-10-14_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
