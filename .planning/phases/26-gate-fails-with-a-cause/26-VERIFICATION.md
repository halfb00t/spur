---
phase: 26-gate-fails-with-a-cause
verified: 2026-10-21T08:30:00Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - ".planning/phases/26-gate-fails-with-a-cause/26-01-PLAN.md"
  - ".planning/phases/26-gate-fails-with-a-cause/26-01-SUMMARY.md"
  - ".planning/phases/26-gate-fails-with-a-cause/26-02-PLAN.md"
  - ".planning/phases/26-gate-fails-with-a-cause/26-02-SUMMARY.md"
  - ".planning/phases/26-gate-fails-with-a-cause/26-03-PLAN.md"
  - ".planning/phases/26-gate-fails-with-a-cause/26-03-SUMMARY.md"
  - ".planning/phases/26-gate-fails-with-a-cause/26-04-PLAN.md"
  - ".planning/phases/26-gate-fails-with-a-cause/26-04-SUMMARY.md"
  - ".planning/phases/26-gate-fails-with-a-cause/26-05-PLAN.md"
  - ".planning/phases/26-gate-fails-with-a-cause/26-05-SUMMARY.md"
  - ".planning/phases/26-gate-fails-with-a-cause/26-06-PLAN.md"
  - ".planning/phases/26-gate-fails-with-a-cause/26-06-SUMMARY.md"
  - ".planning/phases/26-gate-fails-with-a-cause/26-07-PLAN.md"
  - ".planning/phases/26-gate-fails-with-a-cause/26-07-SUMMARY.md"
  - "Makefile"
  - "bench/RESULTS.md"
  - "pyproject.toml"
  - "tests/test_browser.py"
  - "tests/test_hooks.py"
  - "tests/test_pool.py"
covered_digest: "v3:sha256:51441535f6fc88641759aed4b96e55894fd5fe5ab902506b2bd162401dec8cec"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 4/5 must-haves verified
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 26: Gate Fails With a Cause Verification Report

**Phase Goal:** `make verify` and `main` CI stop failing for reasons that are not the product, and the failures and stalls that remain leave their cause in the log: false reds fixed from reproductions (or honestly re-deferred), a hang leaves its test id and a stack dump, the image recipe tests what it claims, the Ubuntu 26 runner is read before the migration reaches the repo.
**Verified:** 2026-10-21
**Status:** passed
**Re-verification:** Yes. The earlier report went stale when Phase 27 (1434a47, PR #44) changed `bench/RESULTS.md` and `tests/test_browser.py`. I re-checked every claim against HEAD and did not copy the old report.

## What changed since the previous report

1. The one open human item is closed. The previous report held the twin-selectors truth open because no `main` push run of the fix existed. Three `main` push runs now exist, and all are green at the browser test (see Truth 2).
2. The `bench/RESULTS.md` change is additive only. Phase 27 appended a `#### The D-05 post-merge read (2026-10-20)` section, two dated `Correction` paragraphs, and a `## Ledger tests and harness (Phase 27)` section. It rewrote nothing Phase 26 recorded. The two corrections rename the members of the browser test's server process group. That is Phase 25/27 content and no Phase 26 claim cites it.
3. The `tests/test_browser.py` change touches only the oracle test and a new `fixture_hash` test, plus one import. The twin-selectors step is byte-identical to what the old report cited.
4. The twin carrying item `2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md` has moved from `active/` to `resolved/` (`Status: resolved`).
5. The gate size grew from 1321 to 1348 tests. The orchestrator's `make verify` on this HEAD read `1348 passed in 196.80s`, exit 0. I cite it and did not re-run it.

## Goal Achievement

### Observable Truths (ROADMAP success criteria are the contract)

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | SC1: Recipes tell the truth. The hook pin passes with a caller's `PYTEST_ARGS`; `make test-image` red set recorded, then passes with every skip named; both debt items retired | VERIFIED | `git diff a4d55a6 HEAD --stat -- Makefile pyproject.toml tests/test_hooks.py tests/test_pool.py` is empty, so these files are unchanged since the old verification. `tests/test_hooks.py:27` has `_MAKE_VARIABLES = ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "PYTEST_ARGS")`, and the two caller-form tests are at lines 157-173. I ran `PYTEST_ARGS=--ignore=tests/test_browser.py .venv/bin/python -m pytest tests/test_hooks.py --no-cov -n0 -q`: `9 passed in 0.54s`. The kept logs `26-01-tests-red.log` and `26-06-first*.log` are in the phase directory. Both items are under `docs/tech_debt/resolved/`: `2026-10-10-hook-pin-reads-the-callers-pytest-args.md` and `2026-10-10-test-image-collects-tests-that-read-host-files.md`. I did not re-run the 15-minute `make test-image`. I relied on the kept `26-06-after.log` (`1201 passed`, no skips), as the old report did. |
| 2 | SC2: The "twin selectors" red on `main` is gone and its mechanism proved; baseline after the link's own STL request plus the debounce; CX-05 and IN-04a folded in; debt retired | VERIFIED | Code at HEAD (`tests/test_browser.py`): `DEBOUNCE_SETTLE_MS = 1_000` (line 75). The twin step waits for `/api/model.stl` with `expect_request(..., timeout=BUILD_WAIT_MS)` and then settles (lines 1559-1620). A second settle precedes the zero-request assertion (line 1658, the CX-05 fix). `_follow_link` is at line 211 and its wait carries `timeout=BUILD_WAIT_MS` (line 221, the IN-04a fix). The step's comment records the departure from the SC wording: the `/api/info` response is the lever, not the STL route. The mechanism proof (three-run arms and the CX-05 control) is in `bench/RESULTS.md`, `### Twin selectors (26-03)`, and that section is unchanged since the last report. **The post-merge `main` read now exists.** I read the saved logs `26-postmerge-run-38858407163-test.log` (head `1981d93`, `1321 passed in 469.99s`) and `26-postmerge-run-39409577060-test.log` (head `a4d55a6`, `1322 passed in 580.19s`). Each holds the line `PASSED tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser` once, and neither prints `twin selectors` (a failure would). `gh run list --branch main --workflow ci` shows both runs, and the next push to `main`, run 39563588816 (head `1434a47`), as `success`. I fetched that third job log: the same PASSED line once, `1348 passed in 714.58s`. The earlier reds were runs 38347283201 and 38680454993, both `main` push runs. Strength: the evidence is consistent with the fix and is not statistically conclusive. bench/RESULTS.md says so itself: two greens at the old 2-in-8 red rate happen by luck about 56 % of the time, and three greens about 42 %. The goal clause is "no longer reds on `main`". Three consecutive `main` push runs of the fix are green on the place and event that failed, and the mechanism is proved on the real app. A later red at the step re-opens the twin item, and the resolved item says so. I count this as verified, and the residual luck-risk is disclosed. The carrying item is in `resolved/`. |
| 3 | SC3: The `resource_tracker` flake is located and fixed from a reproduction, in `tests/test_pool.py` only | VERIFIED | `git diff v0.5 --stat -- src/spur/pool.py` is empty. `tests/test_pool.py` is unchanged since the old report. I ran `pytest tests/test_pool.py -k forced_gc --no-cov -n0 -q`: `1 passed, 20 deselected`. The old report's red-without-fix result on a scratch copy (`check_alive calls: 94`) is a recorded reading. I did not repeat it, and nothing it depends on has changed. The "consistent, not conclusive" wording (natural rate did not reproduce) stands. The item is in `resolved/`. |
| 4 | SC4: A stalled test names itself (`-v` test id plus dump-only `faulthandler_timeout`), set from a recorded `--durations` reading, cost measured against 300 s, hang item stays active with a runbook | VERIFIED | `Makefile:185` is `... --cov --cov-report=term -v --durations=25 $(PYTEST_ARGS)`. `pyproject.toml:133` is `faulthandler_timeout = 170`, with the sizing comment citing 83.55 s from CI's first `--durations` reading (2 x 83.55 = 167.1, rounded up to 170). Both files are unchanged since the old report. The orchestrator's gate read `196.80s` on this HEAD, under the 300 s bar. The hang item `2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md` is `Status: active`. The stall proof is in kept log `26-05-stall.log`. |
| 5 | SC5: Ubuntu 26 pre-classified from a throwaway `runs-on`-only PR, whole logs read, nothing merged but the record, debt item stays active | VERIFIED | `gh pr view 40` reads `state: CLOSED`, `mergedAt: null`. `git diff v0.5 --stat -- .github` is empty. The Ubuntu item `2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md` is `Status: active`. Phase 27's note that its own `ubuntu-latest` run was still on 24.04 on 2026-10-20 does not contradict the Phase 26 reading. It adds to it, and `REQ-ubuntu26-classified-on-migration` stays Pending in Phase 29. |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `tests/test_hooks.py` | strips `PYTEST_ARGS`; two caller-form tests | VERIFIED | Unchanged since the last report. 9 passed under an env `PYTEST_ARGS`. |
| `tests/test_browser.py` | twin baseline after the STL request, settle, `BUILD_WAIT_MS` | VERIFIED | Twin step intact at HEAD. The oracle and `fixture_hash` tests added by Phase 27 pass: `pytest -k "oracle or fixture_link"` gives `2 passed`. |
| `tests/test_pool.py` | autouse GC fixture, `del manager` x3, forced-GC gate test | VERIFIED | Unchanged. The forced-GC test passes. |
| `Makefile` | `-v --durations=25`; `test-image` recipe with named ignores | VERIFIED | Unchanged. |
| `pyproject.toml` | `faulthandler_timeout = 170` | VERIFIED | Unchanged. |
| `bench/RESULTS.md` | Phase 26 records for 26-01 to 26-07 | VERIFIED | The Phase 26 sections are intact. Phase 27 appended after them and the post-merge section closes the twin read. |
| `docs/tech_debt/` | hook, test-image, tracker and twin items resolved; hang and Ubuntu items active | VERIFIED | All four are in `resolved/` and both stay in `active/`. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `tests/test_hooks.py` pins | `Makefile` recipes | dry-run text comparison | WIRED | 9 passed under a caller's `PYTEST_ARGS`. |
| forced-GC test | `tests/test_pool.py` producer tests | child `pytest.main` | WIRED | Passes at HEAD. |
| `faulthandler_timeout` | `-v` ids and `--durations` | ini plus recipe | WIRED | Both strings present in the files. |
| twin step baseline | the page's own STL request | `expect_request` on `/api/model.stl`, then `DEBOUNCE_SETTLE_MS` | WIRED | Lines 1605-1620 of `tests/test_browser.py`. |

### Data-Flow Trace (Level 4)

Not applicable. The phase changes gate recipes, tests and records and renders no dynamic data.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Hook pin under env `PYTEST_ARGS` | `PYTEST_ARGS=--ignore=tests/test_browser.py .venv/bin/python -m pytest tests/test_hooks.py --no-cov -n0 -q` | 9 passed | PASS |
| Forced-GC test | `pytest tests/test_pool.py -k forced_gc --no-cov -n0 -q` | 1 passed | PASS |
| `test_browser.py` still collects and the new oracle tests pass | `pytest tests/test_browser.py -k "oracle or fixture_link" --no-cov -n0 -q` | 2 passed | PASS |
| `main` CI reads the browser test green | `gh run view 39563588816 --log --job {test}` | PASSED line x1, `1348 passed in 714.58s` | PASS |
| Full gate | orchestrator-run `make verify` | exit 0, `1348 passed in 196.80s` | Relied on, not re-run |

### Probe Execution

Not applicable. The plans declare no `probe-*.sh`.

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
| ----------- | ---------- | ------ | -------- |
| REQ-hook-pin-ignores-caller-args | 26-01 | SATISFIED | Truth 1. |
| REQ-twin-selectors-race-fixed | 26-03, 26-07 | SATISFIED | Truth 2. The post-merge read the old report waited on is done, on three `main` runs. |
| REQ-tracker-flake-fixed-from-repro | 26-04 | SATISFIED | Truth 3. |
| REQ-hang-leaves-evidence | 26-05, 26-07 | SATISFIED | Truth 4. |
| REQ-test-image-runs-what-it-claims | 26-06 | SATISFIED | Truth 1. |
| REQ-ubuntu26-preclassified | 26-02, 26-07 | SATISFIED | Truth 5. |

All six IDs appear in `.planning/REQUIREMENTS.md` (lines 39-124, `[x]`) and in its traceability table (lines 176-181, Phase 26, Complete). There are no orphans. `REQ-ubuntu26-classified-on-migration` is Pending under Phase 29, which is correct. The `[x]` on the twin requirement, which the old report called ahead of the evidence, now matches it.

### Anti-Patterns Found

None new. Files unchanged since the last scan show the same results. In `tests/test_browser.py` I grepped the Phase 27 hunks and found no `TBD`, `FIXME`, `XXX`, `TODO` or `HACK`. The two review warnings in `26-REVIEW-DISPOSITION.md` (WR-01, WR-02) are documentation-only. WR-02's target, the twin carrying item, has since been retired.

### Human Verification Required

None. The single item in the old report (post-merge `main` read) was performed and recorded in `bench/RESULTS.md` under `#### The D-05 post-merge read (2026-10-20)`. I confirmed it against the saved logs and `gh`.

### Gaps Summary

There are no gaps. All five roadmap success criteria and all six requirement IDs hold on HEAD `1434a47`. The twin-selectors truth moved from UNCERTAIN (human) to VERIFIED, and the evidence is three green `main` push runs. That evidence is not conclusive by chance alone, and the record says so. If the step reds on a later `main` run, the resolved twin item says to re-open it.

Unverified by me: the 15-minute `make test-image` (I relied on the kept log) and the scratch-copy red run of the forced-GC test (I relied on the recorded reading, since the files are unchanged). No debt item was filed by this re-verification.

---

_Verified: 2026-10-21_
_Verifier: Claude (gsd-verifier)_
