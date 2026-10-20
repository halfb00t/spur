---
phase: 27-ledger-tests-and-harness
verified: 2026-10-20T17:00:00Z
status: passed
score: 4/4 must-haves verified
covered_files:
  - .planning/phases/27-ledger-tests-and-harness/27-01-PLAN.md
  - .planning/phases/27-ledger-tests-and-harness/27-01-SUMMARY.md
  - .planning/phases/27-ledger-tests-and-harness/27-02-PLAN.md
  - .planning/phases/27-ledger-tests-and-harness/27-02-SUMMARY.md
  - .planning/phases/27-ledger-tests-and-harness/27-03-PLAN.md
  - .planning/phases/27-ledger-tests-and-harness/27-03-SUMMARY.md
  - .planning/phases/27-ledger-tests-and-harness/27-04-PLAN.md
  - .planning/phases/27-ledger-tests-and-harness/27-04-SUMMARY.md
  - .planning/phases/27-ledger-tests-and-harness/27-05-PLAN.md
  - .planning/phases/27-ledger-tests-and-harness/27-05-SUMMARY.md
  - .planning/phases/27-ledger-tests-and-harness/27-06-PLAN.md
  - .planning/phases/27-ledger-tests-and-harness/27-06-SUMMARY.md
  - bench/RESULTS.md
  - docs/architecture/decision_log.md
  - src/spur/model.py
  - tests/browser_session.py
  - tests/process_group.py
  - tests/test_api.py
  - tests/test_browser_pins.py
  - tests/test_process_group.py
  - tests/test_trochoid.py
covered_digest: "v3:sha256:57f3d5dbe6fbeabde44b577823d3fff7217099b799bbb5ea5fd3a6d7708d2abc"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 4/4
  gaps_closed: []
  gaps_remaining: []
  regressions: []
gaps: []
advisory:
  - finding: "WR-04: _problems raises KeyError on a module-level `from os import environ` (also `from os import environ` followed by `environ[...]` at module level). The WR-01 climb reads parents[expression] for an ast.ImportFrom, which is already an ast.stmt whose parent is the Module, and Module has no parent."
    category: other
    reason: "Reproduced by me with PYTHONPATH=tests: `_problems('x.py', 'from os import environ\\n')` raises `KeyError <ast.Module ...>`; the same import inside a def reports one problem; `os.environ['A']` reports one problem. The real scan set (`_scan_problems()`) returns [] and holds no module-level environ import (only `os.environ.items()` at browser_session.py:128 and `os.environ.get('PLAYWRIGHT_BROWSERS_PATH', ...)` at :171). If such an import were added the pin would go red as an error, not green, but the scan would abort on the first such file and hide every other problem, and the message would be a bare KeyError instead of the D-02 report. Fix per 27-REVIEW: stop when the node is already an ast.stmt, plus a self-test row for `from os import environ`."
    evidence_status: "reproduced"
  - finding: "IN-07 and IN-01 to IN-06 (27-REVIEW): info-level residuals (the climb stops at `arguments`, `_sleeper` killpg after reap, dead `poll` recorder, a second unpinned copy of `_js_number`, no pin that `_build` passes `rm`, process-wide `subprocess.run` patch, `Resolved in:` holding subjects)"
    category: other
    reason: "Test hygiene and record wording; none contradicts a success criterion. Disposition: open."
    evidence_status: "read in 27-REVIEW.md and 27-REVIEW-DISPOSITION.md"
---

# Phase 27: Ledger Tests and Harness Verification Report

**Phase Goal:** The tests that guard the ledger cannot pass vacuously and the browser harness cannot lie: `slug()` totality is guarded in the commit slice, the failed-build name test no longer depends on cache order, `stop_group` signals the group before it inspects it, and the records and messages that describe the harness say what was observed.
**Verified:** 2026-10-20T17:00:00Z
**Status:** passed (one open advisory warning, WR-04, no gaps)
**Re-verification:** Yes. The prior report (status passed) went stale after review-fix commits 5bf2a0f (WR-01), 2e724cf (WR-02) and 41212d5 (WR-03) changed `tests/process_group.py`, `tests/test_browser_pins.py` and `tests/test_process_group.py`. `git diff --stat f4aa341..HEAD -- tests src bench docs/architecture` lists exactly those three files, so truths 1, 2 and the record parts of 4 were regression-checked (existence and a re-run), and truths 3 and 4 were fully re-checked against the changed code.

## Goal Achievement

### Observable Truths (the four ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `slug()` totality guarded in the commit slice (seeded, stratified, reachable buckets non-empty, two unreachable reasons forced, red against raising `_junction` and `_root_curve`, `verify.fast` under 30 s) | VERIFIED (regression check) | `tests/test_trochoid.py` and the `investigation/27-02-red-slug-*.log` reds are untouched since the prior pass (not in the post-f4aa341 diff). Re-run this pass: `pytest tests/test_trochoid.py -k slug` is part of the 23-passed selection below. The orchestrator's `make verify` (exit 0, `1341 passed in 230.02s`) includes it. |
| 2 | Failed-build name test reads 422 regardless of cache order (fresh `_BlobCache` per test via `fresh_exports`) | VERIFIED (regression check) | `tests/test_api.py` unchanged since the prior pass. Re-run: `pytest tests/test_api.py -k failed_build_records_the_name` gives `2 passed`. Pre-seeded red is kept in `investigation/27-02-red-name-preseeded.log`. |
| 3 | `stop_group` signals before it reads; a failed `ps` fails as "survivors unknown" with the group already signalled; SIGTERM grace kept; sub-second unit test outside the `*browser*` glob | VERIFIED (re-checked against WR-03) | `tests/process_group.py:stop_group`: per signal, `_signal_group(pgid, sig)` is the first statement of the loop body, then the read sits inside `try`; the `except` now covers `CalledProcessError`, `TimeoutExpired`, `OSError`, `ValueError` and does `survivors = None; continue`, so a failed read goes on to SIGKILL; `proc.wait` (the reap) runs after the loop, once; "survivors unknown" is raised only when the last read failed; `group_members` runs `ps` with `timeout=PS_BOUND_S` (5 s). `TERM_BOUND_S = 10.0` kept. `tests/test_process_group.py` (no `browser` in the name) has four failing-reader rows (`ps-exits-non-zero`, `ps-is-absent`, `ps-hangs`, `ps-row-is-not-numbers`), each asserting signals `[SIGTERM, SIGKILL]`, a reaped leader and `survivors unknown`, plus `test_ps_is_run_with_a_timeout`. **My own mutation:** I moved `group_members(pgid)` ahead of `_signal_group` in a working copy, ran the file, and got `5 failed, 1 passed in 20.09s` (the order test and all four failing-reader rows red); restored from backup, `git status` clean, `6 passed in 0.05s`. WR-03's advisory from the prior report is closed by 41212d5. |
| 4 | Harness describes itself truthfully: floor comment names observed members; dated corrections under both `bench/RESULTS.md` rows, nothing rewritten; launch message names a working reinstall; pinned literal kept | VERIFIED (re-checked against WR-01/WR-02) | `tests/browser_session.py:55-67` comment names uvicorn, `multiprocessing.resource_tracker` and one or two spawned workers with the macOS 4/3/4 and ubuntu-latest run 39428298442 count of 4; `MIN_GROUP_MEMBERS = 3`. `bench/RESULTS.md` lines 4781 and 4907 hold the two `**Correction (2026-10-20, 27-06)**` paragraphs; `git diff --numstat v0.5` reads `676 0`. `launch()` (`browser_session.py:161-180`) says "`rm -f .venv/.browser && make test` installs it again: the stamp alone skips the install while it is present" and keeps `playwright install --only-shell chromium`. The pin `test_the_browser_test_has_no_path_that_passes_without_the_browser` asserts `process_group.py` is in `_scan_set()` (WR-02), asserts `launch()` calls `pytest.fail` and holds both literals, and runs `_scan_problems()`; I ran it: passes with an empty problem list. The WR-01 environ rule was exercised by me: `os.environ['A']` in a plain statement reports one problem; the three body-marker rows and the header-scrub row are in the 23 passing. WR-04 (below) is a defect in that rule's edge, not in what the message or pin currently assert. |

**Score:** 4/4 truths verified (0 present, behavior-unverified).

### WR-04 judged on evidence

`27-REVIEW.md` WR-04: `_problems` raises `KeyError` for a module-level `from os import environ`. Disposition: open.

**Reproduced.** With `PYTHONPATH=tests` and the repo venv:

| Source | Result |
|--------|--------|
| `from os import environ\n` | `KeyError <ast.Module ...>` |
| `from os import environ\nx=environ['A']\n` | `KeyError <ast.Module ...>` (the ImportFrom node is walked first) |
| `def f():\n    from os import environ\n` | one problem reported |
| `import os\nx = os.environ['A']\n` | one problem reported |
| `_scan_problems()` on the real scan set | `[]` |

Cause confirmed in `tests/test_browser_pins.py:119-122`: `while not isinstance(parents[expression], clause)` starts at the node itself; an `ast.ImportFrom` at module level has the `Module` as parent, which is not a clause, so the loop climbs to `Module` and `parents[Module]` is a `KeyError`.

**Does it defeat REQ-launch-message-true or any must-have? No.**

1. No scanned module has the shape today (`grep environ` over the four scan-set modules finds only `os.environ.items()` at `browser_session.py:128` and `os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ...)` at `:171`), so the pin passes and the launch-message asserts after the scan (`pytest.fail` present, `INSTALL_COMMAND` and `REINSTALL_COMMAND` constants inside `launch()`) run and hold.
2. The failure direction is red, not green. A future module-level `from os import environ` makes the pin test error out. It does not pass silently, which is what D-02 forbids.
3. The cost is diagnostic: the scan aborts at the first such file, hiding other problems, and the message is a bare `KeyError` rather than the D-02 report. It is a regression against a4091f9 (which reported it) that the WR-01 fix introduced. It narrows no success criterion.

Judgment: WARNING, advisory, not a gap. REQ-launch-message-true stays SATISFIED. The one-line fix in 27-REVIEW (stop the climb when the node is already an `ast.stmt`) plus a self-test row should land before Phase 28 relies on the pin to catch new environ reads.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-slug-totality-guarded | 27-02 | slug totality guarded in commit slice | SATISFIED | Truth 1 |
| REQ-failed-build-name-isolated | 27-02 | failed-build name test independent of cache order | SATISFIED | Truth 2 |
| REQ-stop-group-signals-first | 27-03 | `stop_group` signals before it reads | SATISFIED | Truth 3, incl. my order mutation |
| REQ-group-floor-recorded-true | 27-01, 27-06 | floor comment and bench rows say what was observed | SATISFIED | Truth 4 (comment, both corrections, Linux listing log) |
| REQ-launch-message-true | 27-05 | launch message names a working reinstall; literal kept; pinned | SATISFIED | Truth 4; WR-04 does not defeat it (above) |

All five IDs from the phase brief are declared in PLAN `requirements:` fields (27-01 and 27-06, 27-02, 27-03, 27-05) and present in REQUIREMENTS.md. No orphaned requirement. 27-04 declares `requirements: []` on purpose and contributes to REQ-info-findings-triaged, which Phase 28 closes.

### Boundaries and phase-close checks

| Check | Result |
|-------|--------|
| `git diff --exit-code v0.5 -- tests/regression/` | clean (printed `regression-clean`) |
| `src/` diff since `v0.5` | only `src/spur/model.py`, 7 insertions, 3 deletions (the 19 IN-01/02 line) |
| `bench/RESULTS.md` append-only | `676 0` |
| `docs/architecture/decision_log.md` amended not rewritten | `2 0` |
| `make verify` (orchestrator, after the last fix) | exit 0, `1341 passed in 230.02s`; not re-run by me |
| My targeted run | `pytest tests/test_browser_pins.py tests/test_process_group.py tests/test_trochoid.py -k "pins or process_group or slug or browser_pins or teardown or ps_ or group"`: 23 passed in 0.42 s; `test_api -k failed_build_records_the_name`: 2 passed |
| Working tree after my mutation | restored; `git status --short` empty |

### Anti-Patterns Found

No `TBD`/`FIXME`/`XXX` introduced (the gate in `make verify` includes the unfinished-work scan and passed). No stubs or hollow data flows; every phase artifact is test code or a record, and the single production line (`model.py`) is covered by existing model and bench tests.

### Human Verification Required

None.

### Gaps Summary

No gaps. All four success criteria hold in the code as it is now, after the three review fixes. The three prior advisories (WR-01, WR-02, WR-03) are closed by commits 5bf2a0f, 2e724cf and 41212d5, and I confirmed the WR-03 and WR-02 behavior directly (order mutation red, `process_group.py` in the scan set). One new advisory, WR-04, is open: a latent `KeyError` in the pin's allowance code, reproduced, not reachable from the code that exists, and failing red rather than green when it is.

---

_Verified: 2026-10-20T17:00:00Z_
_Verifier: Claude (gsd-verifier)_
