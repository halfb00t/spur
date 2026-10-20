---
phase: 27-ledger-tests-and-harness
verified: 2026-10-20T18:00:00Z
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
covered_digest: "v3:sha256:81ff5b526ac24b66355fd9d4e01b32aafba4c5a144e0e5228b12a568a26d1c0f"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 4/4
  gaps_closed:
    - "WR-04 (advisory in the prior report): _problems raised KeyError on a module-level `from os import environ`"
  gaps_remaining: []
  regressions: []
gaps: []
advisory:
  - finding: "IN-01 to IN-07 (27-REVIEW, commit 130aa9e): info-level residuals (`_sleeper` killpg after reap, dead `poll` recorder, a second unpinned copy of `_js_number` in test_selector.py, no pin that `_build` passes `rm`, process-wide `subprocess.run` patch, `Resolved in:` holding subjects, the climb stopping at `arguments`)"
    category: other
    reason: "Test hygiene and record wording; none contradicts a success criterion. The re-review reports 0 critical, 0 warning, 7 info. Disposition: open."
    evidence_status: "read in 27-REVIEW.md and 27-REVIEW-DISPOSITION.md"
---

# Phase 27: Ledger Tests and Harness Verification Report

**Phase Goal:** The tests that guard the ledger cannot pass vacuously and the browser harness cannot lie: `slug()` totality is guarded in the commit slice, the failed-build name test no longer depends on cache order, `stop_group` signals the group before it inspects it, and the records and messages that describe the harness say what was observed.
**Verified:** 2026-10-20T18:00:00Z
**Status:** passed (no gaps, no open warning)
**Re-verification:** Yes. The prior report (d54ea56, status passed with advisory WR-04) went stale because `tests/test_browser_pins.py` changed in fix commit 27628ef. `git diff --stat d54ea56..HEAD -- tests src bench docs/architecture` lists exactly that one file (19 insertions, 2 deletions). Truths 1, 2, 3 and the record parts of 4 are therefore regression-checked by a re-run; the launch-message pin in truth 4 was fully re-checked against the changed code.

## Goal Achievement

### Observable Truths (the four ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `slug()` totality guarded in the commit slice (seeded, stratified, reachable buckets non-empty, two unreachable reasons forced) | VERIFIED (regression check) | `tests/test_trochoid.py` holds `test_slug_is_total_and_ends_trochoid_exactly_when_root_mode_does` (line 269) and `test_slug_stays_total_on_the_two_reasons_only_a_patch_reaches` (line 326); file unchanged since d54ea56. Re-ran `pytest tests/test_trochoid.py -k slug`: 3 passed in 0.12 s. |
| 2 | Failed-build name test reads 422 regardless of cache order | VERIFIED (regression check) | `tests/test_api.py` unchanged since d54ea56. Re-ran `pytest tests/test_api.py -k failed_build_records_the_name`: 2 passed. |
| 3 | `stop_group` signals before it reads; a failed `ps` fails as "survivors unknown" with the group already signalled; SIGTERM grace kept; unit test outside the `*browser*` glob | VERIFIED (regression check, code re-read) | `tests/process_group.py:84-108`: `_signal_group(pgid, sig)` is the first statement of the loop body; the `group_members` read sits inside `try`; the `except` covers `CalledProcessError`, `TimeoutExpired`, `OSError`, `ValueError` and sets `survivors = None; continue`, so a failed read still reaches SIGKILL; `proc.wait` runs once after the loop; "survivors unknown" is raised only when the last read failed. `tests/test_process_group.py` has no `browser` in its name. Re-ran it with `test_browser_pins.py`: 17 passed in 0.11 s. The order mutation from the prior pass was not repeated (file untouched since). |
| 4 | Harness describes itself truthfully: floor comment names observed members; dated corrections under both `bench/RESULTS.md` rows, nothing rewritten; launch message names a working reinstall; pinned literal kept | VERIFIED (re-checked against WR-04) | `tests/browser_session.py:55-67` names uvicorn, `multiprocessing.resource_tracker` and one or two spawned workers, with the macOS 4/3/4 and ubuntu-latest run 39428298442 count of 4; `MIN_GROUP_MEMBERS = 3`. `bench/RESULTS.md` lines 4781 and 4907 hold the two `**Correction (2026-10-20, 27-06)**` paragraphs; `git diff --numstat v0.5 -- bench/RESULTS.md` reads `676 0` (append-only). `launch()` (`browser_session.py:161-180`) says "`rm -f .venv/.browser && make test` installs it again: the stamp alone skips the install while it is present" and keeps `playwright install --only-shell chromium`. The pin module passes (11 tests) and `_scan_problems()` on the real scan set returns `[]`. |

**Score:** 4/4 truths verified (0 present, behavior-unverified).

### WR-04 closure judged on evidence

The prior report held WR-04 open as an advisory. Closed by 27628ef.

| Check | Result |
|-------|--------|
| `tests/test_browser_pins.py:119-124` | the climb is now `while not (isinstance(expression, ast.stmt) or isinstance(parents[expression], clause))`, with a comment naming the Module-has-no-parent cause |
| `_problems('x.py', 'from os import environ\n')` (run by me, `python -I`, `tests/` on the path) | `['x.py:1: \`environ\` in \`from os import environ\`']`, a report and not a `KeyError` |
| `_problems('x.py', 'import os\nx=os.environ["A"]\n')` | one problem (WR-01 behavior kept) |
| **My mutation:** reverted the climb to `while not isinstance(parents[expression], clause)` in the working file | `test_an_import_of_environ_is_reported_not_a_crash[module-level]` fails with `KeyError` at `test_browser_pins.py:124` (1 failed, 10 passed). The new test is not vacuous. |
| Restore | file copied back from backup; `git status --short` empty; 11 passed |
| Tech-debt move | resolved in 27628ef, sha named in b9755ad, per CLAUDE.md (re-review 130aa9e confirms) |

The WR-01 cases (if-header, default-argument, except-header marker-in-body rows) still pass, so the fix did not reopen them.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-slug-totality-guarded | 27-02 | slug totality guarded in commit slice | SATISFIED | Truth 1 |
| REQ-failed-build-name-isolated | 27-02 | failed-build name test independent of cache order | SATISFIED | Truth 2 |
| REQ-stop-group-signals-first | 27-03 | `stop_group` signals before it reads | SATISFIED | Truth 3 |
| REQ-group-floor-recorded-true | 27-01, 27-06 | floor comment and bench rows say what was observed | SATISFIED | Truth 4 (comment, both corrections) |
| REQ-launch-message-true | 27-05 | launch message names a working reinstall; literal kept; pinned | SATISFIED | Truth 4; pin now also reports a module-level `environ` import |

All five IDs are declared in PLAN `requirements:` fields (27-01 and 27-06, 27-02, 27-03, 27-05), present in REQUIREMENTS.md (lines 68-87, all `[x]`) and marked Complete in its traceability table (lines 182-186). No orphaned requirement. 27-04 declares `requirements: []` on purpose.

### Boundaries and phase-close checks

| Check | Result |
|-------|--------|
| `git diff --exit-code v0.5 -- tests/regression/` | clean |
| `bench/RESULTS.md` append-only against `v0.5` | `676 0` |
| Files changed since the prior verification (`d54ea56..HEAD`, tests/src/bench/architecture) | `tests/test_browser_pins.py` only |
| Regression gate (orchestrator) | `make test`: 1343 passed in 228.14 s; not re-run by me |
| My targeted runs | `test_browser_pins.py` + `test_process_group.py`: 17 passed; `-k slug`: 3 passed; `test_api -k failed_build_records_the_name`: 2 passed |
| Working tree after my mutation | restored, `git status --short` empty |

### Anti-Patterns Found

None. No `TBD`/`FIXME`/`XXX` in the changed file; no stubs or hollow data flows (all artifacts are test code or records). The 27-REVIEW re-review lists 0 critical, 0 warning, 7 info.

### Human Verification Required

None.

### Gaps Summary

No gaps. All four success criteria hold in the code as it is now, and the only advisory warning from the prior pass (WR-04) is closed and proven by a mutation. The seven info findings (IN-01 to IN-07) are hygiene residuals, tracked in 27-REVIEW-DISPOSITION.md, and contradict no success criterion.

---

_Verified: 2026-10-20T18:00:00Z_
_Verifier: Claude (gsd-verifier)_
