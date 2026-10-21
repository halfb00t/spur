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
covered_digest: "v3:sha256:2b8d7d1f873f56450eda45629cc92eef830644bf64e987dc4e53369f23a77723"
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
  - finding: "IN-09 (27-REVIEW, commit 39cf27d): `test_a_marker_in_a_compound_statements_body_does_not_allow_a_header_read` and `test_an_environ_scrub_in_a_header_that_holds_its_own_marker_is_allowed` keep names that no longer state what their tables pin (lambda and sibling-default rows were added)"
    category: other
    reason: "Test naming drift in the browser-pin hygiene test; no success criterion depends on the names. Disposition: open."
    evidence_status: "read in 27-REVIEW.md; confirmed the table rows and names in tests/test_browser_pins.py"
  - finding: "IN-10 (27-REVIEW): the environ pin's allowance is per statement with `arguments` and `lambda` as the only narrower units; sibling call arguments, conditional branches and comprehensions are not isolated, and the docstring reads stronger than the implementation"
    category: other
    reason: "Documentation gap in a tripwire test; no file in the real scan set has the shape; the REQ-launch-message-true pin on the real scan set returns no problems. Disposition: open."
    evidence_status: "read in 27-REVIEW.md with its probe table"
---

# Phase 27: Ledger Tests and Harness Verification Report

**Phase Goal:** The tests that guard the ledger cannot pass vacuously and the browser harness cannot lie: `slug()` totality is guarded in the commit slice, the failed-build name test no longer depends on cache order, `stop_group` signals the group before it inspects it, and the records and messages that describe the harness say what was observed.
**Verified:** 2026-10-21T00:00:00Z
**Status:** passed (no gaps, no open warning)
**Re-verification:** Yes. The prior report (c053794, status passed) went stale because the code-review fixes IN-01 to IN-08 changed test files. `git diff --stat c053794..HEAD -- tests src bench docs/architecture` lists exactly: `tests/test_bench.py` (IN-05), `tests/test_browser_pins.py` (IN-07, IN-08), `tests/test_process_group.py` (IN-01, IN-02), `tests/test_selector.py` (IN-03). `src/`, `bench/`, `docs/architecture/` and every other `tests/` file are unchanged since the prior pass.

## Goal Achievement

### Observable Truths (the four ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `slug()` totality guarded in the commit slice (seeded, stratified, reachable buckets non-empty, two unreachable reasons forced) | VERIFIED (regression check) | `tests/test_trochoid.py` is unchanged since the prior pass. Re-ran `pytest tests/test_trochoid.py -k slug`: 3 passed in 0.12 s. |
| 2 | Failed-build name test reads 422 regardless of cache order | VERIFIED (regression check) | `tests/test_api.py` unchanged. Re-ran `-k failed_build_records_the_name`: 2 passed. |
| 3 | `stop_group` signals before it reads; a failed `ps` fails as "survivors unknown" with the group already signalled; SIGTERM grace kept; unit test outside the `*browser*` glob | VERIFIED (re-checked against IN-01, IN-02) | `tests/process_group.py:84-108` unchanged: `_signal_group(pgid, sig)` is the first statement of the loop body, the `group_members` read sits inside `try` and a failed read sets `survivors = None; continue` so SIGKILL still goes out; `proc.wait` runs once after the loop. IN-01 (`_sleeper` skips `killpg` when `proc.returncode` is set) and IN-02 (dead `poll` recorder dropped) touch only test scaffolding in `tests/test_process_group.py`. **My mutation**, in a scratch copy of `tests/` under the scratchpad, never the repo: moved `_signal_group` after the first `group_members` read. Result: 5 failed, 1 passed (`test_the_group_is_signalled_before_ps_is_read_or_the_leader_reaped` and all four `ps`-failure params). The order test is still not vacuous after the edits. The unmutated suite passes. |
| 4 | Harness describes itself truthfully: floor comment names observed members; dated corrections under both `bench/RESULTS.md` rows, nothing rewritten; launch message names a working reinstall; pinned literal kept | VERIFIED (re-checked against IN-07, IN-08) | `tests/browser_session.py:55-67` names uvicorn, `multiprocessing.resource_tracker` and one or two spawned workers, with the macOS 4/3/4 and ubuntu-latest run 39428298442 count of 4; `MIN_GROUP_MEMBERS = 3`. `bench/RESULTS.md` lines 4781 and 4907 hold the two `**Correction (2026-10-20, 27-06)**` paragraphs; `git diff --numstat v0.5 -- bench/RESULTS.md` reads `676 0` (append-only). `tests/test_browser_pins.py` now stops the environ climb under `ast.arguments` and `ast.Lambda` (lines 119-128), which only narrows the allowance; the four new rejection rows and the two new allowed-shape asserts pass, and `test_the_browser_test_has_no_path_that_passes_without_the_browser` still reads the real scan set with no problems. The file passes (15 tests). The reviewer's red-first evidence for IN-07 and IN-08 (2 failed, 9 passed with `| ast.Lambda` reverted) is recorded in 27-REVIEW.md; I did not repeat it. |

**Score:** 4/4 truths verified (0 present, behavior-unverified).

### Changes since the prior pass, checked

| Change | File | Effect on a must-have | Result |
|--------|------|-----------------------|--------|
| IN-01, IN-02 | `tests/test_process_group.py` | scaffolding only; truth 3 | order mutation still red (above) |
| IN-07, IN-08 | `tests/test_browser_pins.py` | narrows the pin; REQ-launch-message-true | 15 passed, real scan set clean |
| IN-03 | `tests/test_selector.py` | new test `test_the_page_string_reads_a_number_as_the_page_does`, outside the must-haves | passes within the 38-test targeted run |
| IN-05 | `tests/test_bench.py` | host-state test patches `bench.trochoid_part.subprocess` instead of the shared module's `.run`; outside the must-haves | `-k host_state`: 2 passed |
| debt filing | `docs/tech_debt/` | new nice item for the unpinned `rm` hand-off; resolved items now name short shas | no effect on a truth |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-slug-totality-guarded | 27-02 | slug totality guarded in commit slice | SATISFIED | Truth 1 |
| REQ-failed-build-name-isolated | 27-02 | failed-build name test independent of cache order | SATISFIED | Truth 2 |
| REQ-stop-group-signals-first | 27-03 | `stop_group` signals before it reads | SATISFIED | Truth 3 |
| REQ-group-floor-recorded-true | 27-01, 27-06 | floor comment and bench rows say what was observed | SATISFIED | Truth 4 (comment, both corrections) |
| REQ-launch-message-true | 27-05 | launch message names a working reinstall; literal kept; pinned | SATISFIED | Truth 4; pin still clean on the real scan set |

All five IDs are declared in PLAN `requirements:` fields (27-01 and 27-06, 27-02, 27-03, 27-05), present in REQUIREMENTS.md (lines 68-87, all `[x]`) and marked Complete in its traceability table (lines 182-186). No orphaned requirement. 27-04 declares `requirements: []` on purpose.

### Boundaries and phase-close checks

| Check | Result |
|-------|--------|
| `git diff --exit-code v0.5 -- tests/regression/` | clean |
| `bench/RESULTS.md` append-only against `v0.5` | `676 0` |
| Files changed since the prior verification (tests/src/bench/architecture) | `test_bench.py`, `test_browser_pins.py`, `test_process_group.py`, `test_selector.py` |
| Regression gate (orchestrator) | `make verify` exit 0, `1348 passed in 214.18s`; not re-run by me |
| My targeted runs | pins + process_group + selector: 38 passed; `-k slug`: 3 passed; `test_api -k failed_build_records_the_name`: 2 passed; `test_bench -k host_state`: 2 passed; `test_browser_pins.py`: 15 passed |
| Repo working tree | untouched by me (mutation ran in a scratch copy); `git status --short` empty before writing this report |

### Anti-Patterns Found

None. No `TBD`/`FIXME`/`XXX` in the four changed test files; no stubs or hollow data flows (all artifacts are test code or records). 27-REVIEW lists 0 critical, 0 warning, 2 info.

### Human Verification Required

None.

### Gaps Summary

No gaps. All four success criteria hold in the code as it is now. The two open info findings (IN-09 test names, IN-10 comment strength on a tripwire) are hygiene residuals tracked in 27-REVIEW.md and contradict no success criterion.

---

_Verified: 2026-10-21T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
