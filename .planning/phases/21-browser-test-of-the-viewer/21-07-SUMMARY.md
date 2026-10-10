---
phase: 21-browser-test-of-the-viewer
plan: 07
subsystem: testing
tags: [playwright, make-verify, gate-cost, ab-interleaved, bench, d-01, d-12]

requires:
  - phase: 21-06
    provides: the admitted tests/test_browser.py inside make verify, test depends on $(BROWSER)
provides:
  - "bench/RESULTS.md ### The browser test, priced (21-07): isolated cost, six-run interleaved A/B, red-run list, D-01 outcome, the human's answer"
  - seven kept logs under investigation/ (21-07-A-1, A-1-retry1, A-2, A-3, B-1, B-2, B-3)
  - the human's answer "accept" on the price (O1 kept), the figure L39 in 21-08 cites
  - a filed nice debt item: the shared-recipe hook pin reads the caller's PYTEST_ARGS
affects: [21-08, 25]

actuals:
  tokens: 3800
  tasks: 2
  commits: 3

plan_head_before: 45195ce56c539b60c70b7d51e6922e8bb419492e
plan_head_after: 3e8e8f9eabef722e47d87805b3dce3d48314efb4

tech-stack:
  added: []
  patterns:
    - "A/B arm spelled PYTEST_ADDOPTS, not PYTEST_ARGS, when the hook pin's make -n dry run would read the caller's variable"

key-files:
  created:
    - docs/tech_debt/active/2026-10-10-hook-pin-reads-the-callers-pytest-args.md
    - .planning/phases/21-browser-test-of-the-viewer/investigation/21-07-A-1.log
    - .planning/phases/21-browser-test-of-the-viewer/investigation/21-07-A-1-retry1.log
    - .planning/phases/21-browser-test-of-the-viewer/investigation/21-07-A-2.log
    - .planning/phases/21-browser-test-of-the-viewer/investigation/21-07-A-3.log
    - .planning/phases/21-browser-test-of-the-viewer/investigation/21-07-B-1.log
    - .planning/phases/21-browser-test-of-the-viewer/investigation/21-07-B-2.log
    - .planning/phases/21-browser-test-of-the-viewer/investigation/21-07-B-3.log
  modified:
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "The human accepted the browser test's price: it stays inside make verify and CI (D-01, O1); D-01 did not reopen"
  - "Arm A is spelled PYTEST_ADDOPTS=--ignore=tests/test_browser.py make verify, because the plan's PYTEST_ARGS spelling makes a hook pin fail deterministically"

requirements-completed: [REQ-browser-in-the-gate]

duration: 2 sessions (measurement 13:47-14:08Z, answer recorded same day)
completed: 2026-10-10
status: complete
---

# Phase 21 Plan 07: Pricing the browser test Summary

**The browser test costs 4.23 s serial and 4.57 s at `-n 2` in isolation, shows no cost above noise in a six-run interleaved A/B of the full gate (B - A = -2.47 s), D-01 does not reopen, and the human answered `accept`.**

## Performance

- **Measured:** 2026-10-10, 13:47 to 14:08 UTC, Apple M5 Max, host not idle (load 5.8 to 13.2), HEAD `45195ce`
- **Tasks:** 2 (Task 1 auto, Task 2 blocking-human decision)
- **Files modified:** `bench/RESULTS.md`, `docs/tech_debt/INDEX.md`, one debt item, seven logs

## Accomplishments

- Isolated cost at the final path: serial `-n0` pytest mean 4.23 s (3.55 to 4.65), `-n 2` mean 4.57 s (3.98 to 5.04), against the research figures 3.21 s and 3.80 s. The first build is 2.02 to 2.56 s of the serial run.
- Six interleaved full-gate runs A1, B1, A2, B2, A3, B3: A mean 166.44 s (145.50 to 192.59), B mean 163.96 s (158.44 to 168.30), **B - A = -2.47 s**; pair deltas +19.65, -2.78, -24.29 s. Coverage 97.92 % in all six; B runs 1226 tests, A 1225. The delta is smaller than A's own spread (47.09 s) and changes sign, so it does not separate the file's cost from host load; the isolated figure is the only direct reading.
- D-01's order-of-magnitude rule applied: serial 4.23 s < 32.1 s, `-n 2` 4.57 s < 38.0 s, A/B delta -2.47 s < 38.0 s. None reached, D-01 does not reopen.
- Set beside the bars, quoted not rescaled: B's 163.96 s is 2.48 times L34's 66 s (an Apple M2 Max reading) and 28.98 s below 19-09's 192.94 s on this host. The reading sets no bar (D-12); Phase 25 does.

## Human's answer (Task 2)

Verbatim: `accept`. Option id `accept` (keep the browser test inside `make verify` and CI, O1), recorded 2026-10-10 UTC in `bench/RESULTS.md` under `#### Outcome`. No further words were given; the human did not ask for arm A to be re-measured with the plan's literal `PYTEST_ARGS` spelling. 21-08 may start.

## Red runs

One red run, kept whole at `investigation/21-07-A-1.log`, listed apart from the six: `1 failed, 1224 passed in 164.55s`, the failure `tests/test_hooks.py::test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe` at `assert "--ignore=" not in whole_pytest`.

Classification: not the resource-tracker flake (no `resource_tracker`, `ReentrantCall` or `ExceptionGroup` in any of the seven logs). Deterministic: the pin's `make -n verify` dry run reads the caller's `PYTEST_ARGS` and prints `--ignore=tests/test_browser.py` into the recipe it checks. Arm A was re-run at the same position with `PYTEST_ADDOPTS="--ignore=tests/test_browser.py" make verify`, which leaves the Makefile's recipe unchanged; A2 and A3 use the same spelling. Budget: arm A 4 of 6 attempts, arm B 3 of 6. No `filterwarnings` entry added.

## Task Commits

1. **Debt: hook pin reads the caller's `PYTEST_ARGS` (nice)** - `36a9f45` (docs)
2. **Task 1: isolated cost, six-run A/B, red runs, rule applied** - `9229f26` (docs)
3. **Task 2: record the human's answer** - `3e8e8f9` (docs)

**Plan metadata:** the commit that carries this SUMMARY, STATE.md, ROADMAP.md and REQUIREMENTS.md follows; `commits: 3` above counts the plan's own commits and was measured with `git rev-list --count 45195ce..HEAD` before it.

## Files Created/Modified

- `bench/RESULTS.md` - `### The browser test, priced (21-07)` with `#### Host state`, `#### Isolated cost`, `#### Full gate, A/B interleaved`, `#### Red runs`, `#### Outcome` and the answer
- `docs/tech_debt/active/2026-10-10-hook-pin-reads-the-callers-pytest-args.md`, `docs/tech_debt/INDEX.md` - the filed `nice` item
- `.planning/phases/21-browser-test-of-the-viewer/investigation/21-07-*.log` - every run's log, none deleted

## Decisions Made

- Spelling arm A with `PYTEST_ADDOPTS` is a deviation from the plan's literal `PYTEST_ARGS` text, forced by the pin (see below). Both arms run the same recipe, `-n 8 --cov`; A differs from B only in the ignored file.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Arm A re-spelled with `PYTEST_ADDOPTS`**
- **Found during:** Task 1 (A1, first attempt)
- **Issue:** `make verify PYTEST_ARGS="--ignore=tests/test_browser.py"` fails `test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe` every time; repeating it would show nothing new.
- **Fix:** `PYTEST_ADDOPTS="--ignore=tests/test_browser.py" make verify` for the A1 retry, A2 and A3. `make -n verify | grep -c -- "--ignore="` prints 0 with it and 1 with the plan's spelling; `tests/test_hooks.py` alone read `6 passed` with it set.
- **Files modified:** none in the product; debt filed
- **Committed in:** `36a9f45` (debt item), `9229f26` (record)

**Total deviations:** 1 (Rule 3). **Impact on plan:** measured quantity unchanged; the human saw the substitution under `#### Red runs` and answered `accept`.

## Issues Encountered

The host was not idle (a `fleet-client-cli` at 99 % CPU, an MTPLX runtime, an unrelated `Python` at 108 %), so every wall figure is an upper bound and A's spread is 47 s. Recorded in `#### Host state`; no figure is presented as a bar.

## Known Stubs

None. This plan wrote measurements and a debt item only.

## Threat Flags

None. No product, network, auth or schema surface changed; `git diff --exit-code 592506f` over the fixture, `tests/test_api.py` and the product modules exits 0, and `git diff 592506f -- pyproject.toml | grep -c filterwarnings` prints 0.

## Debt filed

Yes: `docs/tech_debt/active/2026-10-10-hook-pin-reads-the-callers-pytest-args.md` (nice), INDEX row in the same commit `36a9f45`. No idea filed.

## Verification run

- Task 2 verify: `answer recorded` (bench/RESULTS.md, placeholder gone, option id present).
- Task 1 verify (run by the previous agent at `9229f26`) and the product-module diff check re-run here: `diff-clean`, `filterwarnings` count 0.
- The pre-commit hook ran `make verify.fast` on the answer commit and passed; no full `make verify` was run in this continuation (the measurement runs are the A/B above, each ending `1225 passed` or `1226 passed`).

## Next Phase Readiness

21-08 may start: L39 cites the A/B delta (-2.47 s, not separable from noise), the isolated means and the answer `accept` in `### The browser test, priced (21-07)`.

## Self-Check: PASSED

- `bench/RESULTS.md`, the seven logs and the debt file exist; commits `36a9f45`, `9229f26`, `3e8e8f9` are ancestors of HEAD.

---
*Phase: 21-browser-test-of-the-viewer*
*Completed: 2026-10-10*
