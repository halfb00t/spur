---
phase: 26-gate-fails-with-a-cause
verified: 2026-10-23T01:37:17Z
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
covered_digest: "v3:sha256:760b87a650355ebe683c9170d1cab5856ad6d2d44a62be873042b7f65b46a603"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 5/5 must-haves verified
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 26: Gate Fails With a Cause Verification Report

**Phase Goal:** `make verify` and `main` CI stop failing for reasons that are not the product, and the failures and stalls that remain leave their cause in the log: false reds fixed from reproductions (or honestly re-deferred), a hang leaves its test id and a stack dump, the image recipe tests what it claims, the Ubuntu 26 runner is read before the migration reaches the repo.
**Verified:** 2026-10-23T01:37:17Z, at HEAD `43fbf721ecb9b30049d3bc3a6953592257c0fa7f` (branch `gsd/v0.6-close-gaps`). `43fbf72` sits on `a620399` and changes only `.planning/phases/28-refuse-the-bad-link/28-UAT.md`; the code is `a620399`'s.
**Status:** passed
**Re-verification:** Yes. The previous report (commit `7cd616c`, PR #45, status passed 5/5) went stale when Phase 28 (`fc7338a`, PR #46) and Phase 29 (`a620399`, PR #47) changed `Makefile`, `bench/RESULTS.md` and `tests/test_browser.py`. I re-checked every truth against HEAD and did not copy the old verdicts.

## What changed since the previous report

`git diff --stat 7cd616c..HEAD` over the covered files: `Makefile` 3 lines, `bench/RESULTS.md` +202/-0, `tests/test_browser.py` 401 lines. `pyproject.toml`, `tests/test_hooks.py`, `tests/test_pool.py` and every 26 PLAN/SUMMARY are unchanged.

| Stale file | Commit | What changed | Touches a Phase 26 claim? |
| ---------- | ------ | ------------ | ------------------------- |
| `Makefile` | `fc7338a` (Phase 28, 54f3b53, 26 IN-04) | The comment over the `test-image` ignores now cites `bench/RESULTS.md` "make test-image (26-06)" in place of the phase-scoped `investigation/26-06-redset.md` path. Comment only. | No. The `test` recipe (`-v --durations=25`) and the six named `--ignore`s in `test-image` are unchanged. |
| `bench/RESULTS.md` | `fc7338a`, `a620399` | Append only: `## Refuse the bad link (Phase 28)` and `## Ubuntu 26 final reading (Phase 29)` added after line 6606. No line removed (`git diff --numstat v0.5` reads `878 0`). | No. The Phase 26 sections (26-01 to 26-07, the D-05 post-merge read) are untouched. |
| `tests/test_browser.py` | `fc7338a` (Phase 28) | New steps for refused links (`form build error`, bad-link steps), a `_stl_requests` helper, `_follow_link` callers now use the page's sent query. In the twin-selectors step, only two comments changed: `app.js:262-272` became `app.js update()` and `app.js:643-644` became a description of the bootstrap (26 IN-03). | Twin step: comments only, no executable line. `DEBOUNCE_SETTLE_MS = 1_000` (line 77), the STL-request baseline wait (lines 1640-1647), the second settle before the zero-request count (line 1689) and `_follow_link`'s `timeout=BUILD_WAIT_MS` (lines 241-243) are intact. |

Also changed, not covered: `26-REVIEW-DISPOSITION.md` moved IN-01..IN-05 from `open` to fixed/skipped (Phase 28 triage); the hang item gained a pointer to `bench/RESULTS.md` "Hang evidence (26-05)"; the Ubuntu item gained the Phase 29 close paragraph and stays `active`.

New evidence for Truth 2: two more `main` push runs are green at the browser test, `39812587970` (head `7cd616c`, `1348 passed in 447.26s`) and `39883204624` (head `a620399`, `1348 passed in 768.55s`). That makes five consecutive green `main` push runs of the fix. `gh run list` shows no separate `main` push run for `fc7338a`.

## Goal Achievement

### Observable Truths (ROADMAP success criteria are the contract)

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | SC1: Recipes tell the truth. The hook pin passes with a caller's `PYTEST_ARGS`; `make test-image` red set recorded, then passes with every skip named; both debt items retired | VERIFIED | `tests/test_hooks.py:27` `_MAKE_VARIABLES = ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "PYTEST_ARGS")`, file unchanged since `7cd616c`. Ran `PYTEST_ARGS=--ignore=tests/test_browser.py .venv/bin/python -m pytest tests/test_hooks.py --no-cov -n0 -q -p no:cacheprovider`: `9 passed in 0.73s`. `Makefile:251-261` `test-image` keeps six named whole-file `--ignore`s; only the comment above it changed. Both items in `docs/tech_debt/resolved/` (`2026-10-10-hook-pin-reads-the-callers-pytest-args.md`, `2026-10-10-test-image-collects-tests-that-read-host-files.md`, `Status: resolved`). Not re-run: the 15-minute `make test-image`; relied on the kept `26-06-after.log`, as both earlier reports did. |
| 2 | SC2: The "twin selectors" red on `main` is gone and its mechanism proved; baseline after the link's own STL request plus the debounce; CX-05 and IN-04a folded in; debt retired | VERIFIED | Code at HEAD: the twin step (`tests/test_browser.py:1589` onwards) waits on `expect_request("/api/model.stl", timeout=BUILD_WAIT_MS)` around `goto`, then `wait_for_timeout(DEBOUNCE_SETTLE_MS)` (line 1647); the second settle precedes the zero-request assertion (line 1689, CX-05); `_follow_link` waits with `timeout=BUILD_WAIT_MS` (line 242, IN-04a). Phase 28 changed only comments in this step. Mechanism record `### Twin selectors (26-03)` in `bench/RESULTS.md` unchanged. `main` reads: runs 38858407163, 39409577060, 39563588816 (from the last report) plus 39812587970 and 39883204624, all `success`; I read the last two job logs: `PASSED tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser` once each, no `twin selectors` failure text. Local gate: the browser test PASSED (log line 1998). Strength as before: consistent with the fix, not statistically conclusive by itself; at the old 2-in-8 red rate five greens happen by luck about 24 % of the time. The mechanism is proved on the real app. Item `2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md` in `resolved/`. |
| 3 | SC3: The `resource_tracker` flake is located and fixed from a reproduction, in `tests/test_pool.py` only | VERIFIED | `tests/test_pool.py` unchanged since `7cd616c`; `src/spur/pool.py` unchanged since `v0.5` (Phase 28 touched only `calc.py` and `static/app.js` under `src/`). Ran `pytest tests/test_pool.py -k forced_gc --no-cov -n0 -q -p no:cacheprovider`: `1 passed, 20 deselected in 10.90s`. Recorded red-without-fix reading not repeated (nothing it depends on changed). Item `2026-10-06-resource-tracker-flake-fails-the-gate.md` in `resolved/`. |
| 4 | SC4: A stalled test names itself (`-v` test id plus dump-only `faulthandler_timeout`), set from a recorded `--durations` reading, cost measured against 300 s, hang item stays active with a runbook | VERIFIED | `Makefile:185` `$(PY) -m pytest -n $(PYTEST_WORKERS) --cov --cov-report=term -v --durations=25 $(PYTEST_ARGS)`; `pyproject.toml:133` `faulthandler_timeout = 170`; both executable lines unchanged. My gate run: `1348 passed in 236.23s`, under the 300 s bar (L43). Hang item `docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md` is `Status: active`; Phase 28 only re-pointed its evidence paths (archived v0.5 path, `bench/RESULTS.md` "Hang evidence (26-05)"), the runbook stands. Kept `26-05-stall.log` still in the phase directory. |
| 5 | SC5: Ubuntu 26 pre-classified from a throwaway `runs-on`-only PR, whole logs read, nothing merged but the record, debt item stays active | VERIFIED | PR #40 closed unmerged (prior report's `gh pr view 40`, unchanged fact). `### Ubuntu 26.04, pre-classified (26-02)` in `bench/RESULTS.md` unchanged. Ubuntu item `docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md` stays `Status: active`; Phase 29 appended its close paragraph (30 of 30 jobs still on `Image: ubuntu-24.04`, trigger restated), which builds on the 26-02 reading and does not contradict it. `REQ-ubuntu26-classified-on-migration` moved to Future Requirements at Phase 29 close (`.planning/REQUIREMENTS.md:176,204`), which is not this phase's requirement. The `a620399` main run still read `Image: ubuntu-24.04`. |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `tests/test_hooks.py` | strips `PYTEST_ARGS`; two caller-form tests | VERIFIED | Unchanged. 9 passed under an env `PYTEST_ARGS`. |
| `tests/test_browser.py` | twin baseline after the STL request, settle, `BUILD_WAIT_MS` | VERIFIED | Twin step executable lines unchanged by Phase 28; browser test passes in the gate. |
| `tests/test_pool.py` | autouse GC fixture, `del manager` x3, forced-GC gate test | VERIFIED | Unchanged. Forced-GC test passes. |
| `Makefile` | `-v --durations=25`; `test-image` recipe with named ignores | VERIFIED | Recipes unchanged; one comment re-pointed to `bench/RESULTS.md`. |
| `pyproject.toml` | `faulthandler_timeout = 170` | VERIFIED | Unchanged. |
| `bench/RESULTS.md` | Phase 26 records for 26-01 to 26-07 | VERIFIED | Append-only since `v0.5` (`878 0`); Phase 26 sections intact. |
| `docs/tech_debt/` | hook, test-image, tracker and twin items resolved; hang and Ubuntu items active | VERIFIED | Four in `resolved/`, two in `active/`. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `tests/test_hooks.py` pins | `Makefile` recipes | dry-run text comparison | WIRED | 9 passed; recipes unchanged, only a comment moved. |
| forced-GC test | `tests/test_pool.py` producer tests | child `pytest.main` | WIRED | Passes at HEAD. |
| `faulthandler_timeout` | `-v` ids and `--durations` | ini plus recipe | WIRED | Both present; the gate log prints per-test `-v` lines. |
| twin step baseline | the page's own STL request | `expect_request` on `/api/model.stl`, then `DEBOUNCE_SETTLE_MS` | WIRED | `tests/test_browser.py:1640-1647`. |

### Data-Flow Trace (Level 4)

Not applicable. The phase changes gate recipes, tests and records and renders no dynamic data.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Hook pin under env `PYTEST_ARGS` | `PYTEST_ARGS=--ignore=tests/test_browser.py .venv/bin/python -m pytest tests/test_hooks.py --no-cov -n0 -q -p no:cacheprovider` | `9 passed in 0.73s` | PASS |
| Forced-GC test | `.venv/bin/python -m pytest tests/test_pool.py -k forced_gc --no-cov -n0 -q -p no:cacheprovider` | `1 passed, 20 deselected in 10.90s` | PASS |
| `main` CI reads the browser test green | `gh run view --job 119942521894 --log`, `gh run view --job 120185199233 --log` | PASSED line x1 each; `1348 passed in 447.26s`, `1348 passed in 768.55s` | PASS |
| Full gate | `make verify` (run by me, 01:32:56-01:36:52Z, no other gate running) | exit 0; ruff `All checks passed!`, mypy `Success: no issues found in 51 source files`, `Contracts: 5 kept, 0 broken.`, `======================= 1348 passed in 236.23s (0:03:56) =======================` | PASS |

### Probe Execution

Not applicable. The plans declare no `probe-*.sh`.

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
| ----------- | ---------- | ------ | -------- |
| REQ-hook-pin-ignores-caller-args | 26-01 | SATISFIED | Truth 1. |
| REQ-twin-selectors-race-fixed | 26-03, 26-07 | SATISFIED | Truth 2. Five green `main` push runs. |
| REQ-tracker-flake-fixed-from-repro | 26-04 | SATISFIED | Truth 3. |
| REQ-hang-leaves-evidence | 26-05, 26-07 | SATISFIED | Truth 4. |
| REQ-test-image-runs-what-it-claims | 26-06 | SATISFIED | Truth 1. |
| REQ-ubuntu26-preclassified | 26-02, 26-07 | SATISFIED | Truth 5. |

All six IDs are `[x]` in `.planning/REQUIREMENTS.md` (lines 39-124) and Complete in its traceability table (lines 181-186). No orphans.

### Anti-Patterns Found

None. The Phase 28 hunks in `tests/test_browser.py` and `Makefile` carry no `TBD`, `FIXME` or `XXX`; the gate's unfinished-work scan (`tests/test_no_fake_done.py`) passed inside `make verify`.

### Human Verification Required

None.

### Gaps Summary

No gaps. All five success criteria and six requirement IDs hold at HEAD `43fbf72` (code identical to `a620399`). The three stale files were changed by Phase 28 and 29 without touching a Phase 26 claim: a re-pointed comment in `Makefile`, appended sections in `bench/RESULTS.md`, and new browser steps plus two comment edits inside the twin step in `tests/test_browser.py`. The twin-selectors evidence grew from three to five green `main` push runs; still not conclusive by chance alone, as the record says.

Not re-run by me: the 15-minute `make test-image` (kept log relied on) and the scratch-copy red run of the forced-GC test (recorded reading relied on; its files are unchanged). No debt item filed.

---

_Verified: 2026-10-23T01:37:17Z_
_Verifier: Claude (gsd-verifier)_
