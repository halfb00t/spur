---
phase: 27-ledger-tests-and-harness
verified: 2026-10-21T00:00:00Z
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
  - tests/test_bench.py
  - tests/test_browser_pins.py
  - tests/test_process_group.py
  - tests/test_selector.py
  - tests/test_trochoid.py
covered_digest: "v3:sha256:333a6e4f0e53384856ee1e2128c7d03867c29cfe925c14563576e60aa01d3275"
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
  - finding: "IN-11 (27-REVIEW): the new comment in `tests/test_browser_pins.py:126-128` says the environ allowance is 'per statement', but the climb stops at the expression directly under a statement or clause node, so it is narrower than a statement in more places than the comment names (assignment target vs value, another with-item, another decorator, a return annotation, match subject vs case)"
    category: other
    reason: "Comment wording only. The error is on the safe side (false positives, never a missed read). No success criterion depends on the wording. Disposition: open."
    evidence_status: "read in 27-REVIEW.md with its probe list; the climb condition at test_browser_pins.py:128-129 read directly"
  - finding: "IN-12 (27-REVIEW): the over-allowance the comment documents (another call argument, the other branch of a conditional, a comprehension's iterable) has no test pin"
    category: other
    reason: "A known, documented limit of a tripwire test. The REQ-launch-message-true pin on the real scan set returns no problems. Disposition: open."
    evidence_status: "read in 27-REVIEW.md; confirmed no test row for those shapes in tests/test_browser_pins.py"
---

# Phase 27: Ledger Tests and Harness Verification Report

**Phase Goal:** The tests that guard the ledger cannot pass vacuously and the browser harness cannot lie: `slug()` totality is guarded in the commit slice, the failed-build name test no longer depends on cache order, `stop_group` signals the group before it inspects it, and the records and messages that describe the harness say what was observed.
**Verified:** 2026-10-21T00:00:00Z
**Status:** passed (no gaps, no open warning)
**Re-verification:** Yes. The prior report (299d527, status passed) went stale because commits 75b93f6 and 8e65fbc changed `tests/test_browser_pins.py`. `git diff --stat 299d527..HEAD -- . ':!.planning'` lists exactly that one file, 7 insertions and 3 deletions. `src/`, `bench/`, `docs/architecture/` and every other `tests/` file are unchanged since the prior pass.

## Goal Achievement

### Observable Truths (the four ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `slug()` totality guarded in the commit slice (seeded, stratified, reachable buckets non-empty, two unreachable reasons forced) | VERIFIED (regression check) | `tests/test_trochoid.py` unchanged since the prior pass. Re-ran `pytest tests/test_trochoid.py -k slug`: 3 passed. |
| 2 | Failed-build name test reads 422 regardless of cache order | VERIFIED (regression check) | `tests/test_api.py` unchanged. Re-ran `-k failed_build_records_the_name`: 2 passed. |
| 3 | `stop_group` signals before it reads; a failed `ps` fails as "survivors unknown" with the group already signalled; SIGTERM grace kept; unit test outside the `*browser*` glob | VERIFIED (regression check) | `tests/process_group.py` and `tests/test_process_group.py` unchanged. Read lines 84-108 again: `_signal_group(pgid, sig)` is the first statement of the loop body, the `group_members` read sits inside `try`, a failed read sets `survivors = None; continue` so SIGKILL still goes out, `proc.wait` runs once after the loop, and the "survivors unknown" failure follows. `test_process_group.py` passes (inside the 21 passed below). The order mutation from the prior pass is not repeated: the file it mutates has not changed. |
| 4 | Harness describes itself truthfully: floor comment names observed members; dated corrections under both `bench/RESULTS.md` rows, nothing rewritten; launch message names a working reinstall; pinned literal kept | VERIFIED (re-checked against IN-09, IN-10) | `tests/browser_session.py:55-67` names uvicorn, `multiprocessing.resource_tracker` and one or two spawned workers, with the macOS 4/3/4 and ubuntu-latest run 39428298442 count of 4; `MIN_GROUP_MEMBERS = 3` (line 67). `bench/RESULTS.md` lines 4781 and 4907 hold the two `**Correction (2026-10-20, 27-06)**` paragraphs; `git diff --numstat v0.5 -- bench/RESULTS.md` reads `676 0` (append-only). The launch message names `playwright install --only-shell chromium` (`browser_session.py:176`), matched by `INSTALL_COMMAND` in the pin (`test_browser_pins.py:44`). The pin file's full diff since the prior pass, read line by line, is: one 3-line comment inside `_problems`, and two test renames plus one docstring edit. The climb logic (`clause = ast.stmt \| ast.ExceptHandler \| ast.match_case \| ast.arguments \| ast.Lambda`, the `while` loop, the `ALLOWED_ENVIRON_MARKERS` check) is byte-identical. The pin passes on its tables and on the real scan set. |

**Score:** 4/4 truths verified (0 present, behavior-unverified).

### Changes since the prior pass, checked

| Change | File | Effect on a must-have | Result |
|--------|------|-----------------------|--------|
| IN-09 (75b93f6) | `tests/test_browser_pins.py` | renames only. `test_a_marker_in_a_compound_statements_body_does_not_allow_a_header_read` is now `test_a_marker_outside_the_reads_own_expression_does_not_allow_it` (7 parametrized rows, unchanged). `test_an_environ_scrub_in_a_header_that_holds_its_own_marker_is_allowed` is now `test_an_environ_read_that_holds_its_own_marker_is_allowed` (3 asserts, unchanged) with a docstring that names header, default and lambda body | 15 passed in the file. A grep for the two old names finds them only in `27-REVIEW-FIX.md` (the rename record) and in this phase's earlier report, which this rewrite replaces. No code or test refers to them. |
| IN-10 (8e65fbc) | `tests/test_browser_pins.py` | a 3-line comment inside `_problems`; no executable line touched | file still parses and passes; the comment's own accuracy is IN-11 below |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-slug-totality-guarded | 27-02 | slug totality guarded in commit slice | SATISFIED | Truth 1 |
| REQ-failed-build-name-isolated | 27-02 | failed-build name test independent of cache order | SATISFIED | Truth 2 |
| REQ-stop-group-signals-first | 27-03 | `stop_group` signals before it reads | SATISFIED | Truth 3 |
| REQ-group-floor-recorded-true | 27-01, 27-06 | floor comment and bench rows say what was observed | SATISFIED | Truth 4 (comment, both corrections) |
| REQ-launch-message-true | 27-05 | launch message names a working reinstall; literal kept; pinned | SATISFIED | Truth 4; the pin is clean on the real scan set |

All five IDs are declared in PLAN `requirements:` fields (27-01 and 27-06, 27-02, 27-03, 27-05), present in REQUIREMENTS.md (lines 68-87, all `[x]`) and marked Complete in its traceability table (lines 182-186). No orphaned requirement. 27-04 declares `requirements: []` on purpose.

### Boundaries and phase-close checks

| Check | Result |
|-------|--------|
| `git diff --exit-code v0.5 -- tests/regression/` | clean |
| `bench/RESULTS.md` append-only against `v0.5` | `676 0` |
| Files changed since the prior verification (non-`.planning`) | `tests/test_browser_pins.py` only |
| Regression gate (orchestrator) | `make verify` exit 0, `1348 passed in 238.11s`; not re-run by me |
| My targeted runs | `test_browser_pins.py` + `test_process_group.py`: 21 passed in 0.24s; `test_trochoid.py -k slug`: 3 passed; `test_api.py -k failed_build_records_the_name`: 2 passed |
| Repo working tree | `git status --short` empty before writing this report; no source or test file touched by me |

### Anti-Patterns Found

None. No `TBD`/`FIXME`/`XXX` in `tests/test_browser_pins.py`; no stubs or hollow data flows (all artifacts are test code or records). 27-REVIEW lists 0 critical, 0 warning, 2 info.

### Human Verification Required

None.

### Gaps Summary

No gaps. All four success criteria hold in the code as it is now. The change since the prior pass is two renames, a docstring edit and a comment, with no logic touched. The two open info findings are hygiene residuals tracked in 27-REVIEW.md and contradict no success criterion. IN-11 says the new "per statement" comment overstates the unit, and the error is on the safe side. IN-12 says the documented over-allowance has no pinning test.

---

_Verified: 2026-10-21T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
