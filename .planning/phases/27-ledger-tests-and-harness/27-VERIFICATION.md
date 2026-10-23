---
phase: 27-ledger-tests-and-harness
verified: 2026-10-23T01:37:17Z
status: passed
score: 4/4 must-haves verified
covered_files:
  - ".planning/phases/27-ledger-tests-and-harness/27-01-PLAN.md"
  - ".planning/phases/27-ledger-tests-and-harness/27-01-SUMMARY.md"
  - ".planning/phases/27-ledger-tests-and-harness/27-02-PLAN.md"
  - ".planning/phases/27-ledger-tests-and-harness/27-02-SUMMARY.md"
  - ".planning/phases/27-ledger-tests-and-harness/27-03-PLAN.md"
  - ".planning/phases/27-ledger-tests-and-harness/27-03-SUMMARY.md"
  - ".planning/phases/27-ledger-tests-and-harness/27-04-PLAN.md"
  - ".planning/phases/27-ledger-tests-and-harness/27-04-SUMMARY.md"
  - ".planning/phases/27-ledger-tests-and-harness/27-05-PLAN.md"
  - ".planning/phases/27-ledger-tests-and-harness/27-05-SUMMARY.md"
  - ".planning/phases/27-ledger-tests-and-harness/27-06-PLAN.md"
  - ".planning/phases/27-ledger-tests-and-harness/27-06-SUMMARY.md"
  - "bench/RESULTS.md"
  - "docs/architecture/decision_log.md"
  - "src/spur/model.py"
  - "tests/browser_session.py"
  - "tests/process_group.py"
  - "tests/test_api.py"
  - "tests/test_bench.py"
  - "tests/test_browser_pins.py"
  - "tests/test_process_group.py"
  - "tests/test_selector.py"
  - "tests/test_trochoid.py"
covered_digest: "v3:sha256:1b82a3fbc566f3c73f248632f2aa1b6a3c070892736a3b479bdfae4ab3a11ab8"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 4/4
  gaps_closed: []
  gaps_remaining: []
  regressions: []
gaps: []
---

# Phase 27: Ledger Tests and Harness Verification Report

**Phase Goal:** The tests that guard the ledger cannot pass vacuously and the browser harness cannot lie: `slug()` totality is guarded in the commit slice, the failed-build name test no longer depends on cache order, `stop_group` signals the group before it inspects it, and the records and messages that describe the harness say what was observed.
**Verified:** 2026-10-23T01:37:17Z, at HEAD `43fbf721ecb9b30049d3bc3a6953592257c0fa7f` (branch `gsd/v0.6-close-gaps`). `43fbf72` sits on `a620399` and changes only `.planning/phases/28-refuse-the-bad-link/28-UAT.md`; the code is `a620399`'s.
**Status:** passed (no gaps, no open warning, no open advisory)
**Re-verification:** Yes. The previous report (commit `1434a47`, PR #44, status passed 4/4) went stale when Phase 28 (`fc7338a`, PR #46) and Phase 29 (`a620399`, PR #47) changed `bench/RESULTS.md`, `docs/architecture/decision_log.md`, `tests/test_api.py` and `tests/test_browser_pins.py`. I re-checked every truth against HEAD and did not copy the old verdicts.

## What changed since the previous report

`git diff --stat 1434a47..HEAD` over the covered files: `bench/RESULTS.md` +202/-0, `docs/architecture/decision_log.md` +114/-0, `tests/test_api.py` 27 lines, `tests/test_browser_pins.py` 10 lines. `src/spur/model.py`, `tests/browser_session.py`, `tests/process_group.py`, `tests/test_bench.py`, `tests/test_process_group.py`, `tests/test_selector.py`, `tests/test_trochoid.py` and every 27 PLAN/SUMMARY are unchanged.

| Stale file | Commit | What changed | Touches a Phase 27 claim? |
| ---------- | ------ | ------------ | ------------------------- |
| `bench/RESULTS.md` | `fc7338a`, `a620399` | Append only: `## Refuse the bad link (Phase 28)` and `## Ubuntu 26 final reading (Phase 29)`. `git diff --numstat v0.5` reads `878 0`. | No. The two `**Correction (2026-10-20, 27-06)**` paragraphs (lines 4781, 4907) and the Phase 27 section are intact; the file stays append-only, which Truth 4 requires. |
| `docs/architecture/decision_log.md` | `fc7338a` | Append only: `## L44` (a link value its control cannot hold is refused by 422) and `## L45` (tip_chamfer_effective gated on the applied value). `git diff --numstat v0.5` reads `116 0`. | No. L40's `22-REVIEW IN-03` amendment (3.56, 2.63, the `test_slug_is_total...` sentence) is present; L44/L45 amend L39, L42 and L29, none of which a Phase 27 claim cites. |
| `tests/test_api.py` | `fc7338a` | Only `test_the_shareable_link_round_trips_every_field_through_generic_code`: ten new `app.js` token pins for L44's `rejected` map, two tokens lengthened, plus their comment. | No. The failed-build name tests and the 24 IN-03 `_has_key` walker are untouched; both pass (below). |
| `tests/test_browser_pins.py` | `fc7338a` (87d98ab, 27 IN-11) | The 3-line comment in `_problems` became a 7-line comment: the environ allowance is "per top-level expression of a statement", naming the target/with-item/decorator/annotation cases. No executable line. | No. `clause = ast.stmt \| ast.ExceptHandler \| ast.match_case \| ast.arguments \| ast.Lambda` and the `while` climb are byte-identical. This closes the old report's advisory IN-11; IN-12 was triaged `skipped` (safe-side limit) in `27-REVIEW-DISPOSITION.md`. |

## Goal Achievement

### Observable Truths (the four ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `slug()` totality guarded in the commit slice (seeded, stratified, reachable buckets non-empty, two unreachable reasons forced) | VERIFIED | `tests/test_trochoid.py` unchanged since `1434a47`. Ran `.venv/bin/python -m pytest tests/test_trochoid.py -k slug --no-cov -n0 -q -p no:cacheprovider`: `3 passed, 98 deselected in 0.12s`. Phase 28 changed `src/spur/calc.py` (L45 tip-chamfer gate); `slug()` still passes its totality test and the full gate. |
| 2 | Failed-build name test reads 422 regardless of cache order | VERIFIED | The Phase 28 edit to `tests/test_api.py` is confined to the shareable-link token test. Ran `pytest tests/test_api.py -k "failed_build_records_the_name or openapi_documents or shareable_link_round_trips" --no-cov -n0 -q -p no:cacheprovider`: `4 passed, 58 deselected in 1.72s` (the two failed-build name cases, the `_has_key` OpenAPI walk, and the changed token test). |
| 3 | `stop_group` signals before it reads; a failed `ps` fails as "survivors unknown" with the group already signalled; SIGTERM grace kept; unit test outside the `*browser*` glob | VERIFIED | `tests/process_group.py` and `tests/test_process_group.py` unchanged. Read `process_group.py:82-108` again: `_signal_group(pgid, sig)` is the loop body's first statement; `group_members` sits inside `try`; a failed read sets `survivors = None; continue` so SIGKILL still goes out; `proc.wait` after the loop; "survivors unknown" `pytest.fail` follows. `test_browser_pins.py` + `test_process_group.py`: `21 passed in 0.12s`. |
| 4 | Harness describes itself truthfully: floor comment names observed members; dated corrections under both `bench/RESULTS.md` rows, nothing rewritten; launch message names a working reinstall; pinned literal kept | VERIFIED | `tests/browser_session.py:55-67` unchanged: names uvicorn, `multiprocessing.resource_tracker` and one or two spawned workers, macOS 4/3/4 and ubuntu-latest run 39428298442 reading 4; `MIN_GROUP_MEMBERS = 3`. `bench/RESULTS.md:4781,4907` hold both dated corrections; file append-only vs `v0.5` (`878 0`). Launch message names `playwright install --only-shell chromium` (`browser_session.py:176`), matched by `INSTALL_COMMAND` (`test_browser_pins.py:44`). Pin passes on its tables and the real scan set (21 passed above; and inside the gate). |

**Score:** 4/4 truths verified (0 present, behavior-unverified).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-slug-totality-guarded | 27-02 | slug totality guarded in commit slice | SATISFIED | Truth 1 |
| REQ-failed-build-name-isolated | 27-02 | failed-build name test independent of cache order | SATISFIED | Truth 2 |
| REQ-stop-group-signals-first | 27-03 | `stop_group` signals before it reads | SATISFIED | Truth 3 |
| REQ-group-floor-recorded-true | 27-01, 27-06 | floor comment and bench rows say what was observed | SATISFIED | Truth 4 |
| REQ-launch-message-true | 27-05 | launch message names a working reinstall; literal kept; pinned | SATISFIED | Truth 4 |

All five IDs are `[x]` in `.planning/REQUIREMENTS.md` (lines 68-87) and Complete in its traceability table (lines 187-191). No orphans. 27-04 declares `requirements: []` on purpose.

### Boundaries and phase-close checks

| Check | Result |
|-------|--------|
| `git diff --exit-code v0.5 -- tests/regression/` | clean |
| `bench/RESULTS.md` append-only against `v0.5` | `878 0` |
| `docs/architecture/decision_log.md` append-only against `v0.5` | `116 0`; L40 amendment present |
| Full gate | `make verify` run by me, 01:32:56-01:36:52Z, no other gate running: exit 0; ruff `All checks passed!`, mypy `Success: no issues found in 51 source files`, `Contracts: 5 kept, 0 broken.`, `======================= 1348 passed in 236.23s (0:03:56) =======================` |
| `main` CI at `a620399` | run 39883204624 `success`, test job `1348 passed in 768.55s` |
| Repo working tree | `git status --short` empty before writing; only the two VERIFICATION.md files written |

### Anti-Patterns Found

None. The Phase 28 hunks in `tests/test_api.py` and `tests/test_browser_pins.py` carry no `TBD`, `FIXME` or `XXX`; the gate's unfinished-work scan passed inside `make verify`.

### Human Verification Required

None.

### Gaps Summary

No gaps. All four success criteria and five requirement IDs hold at HEAD `43fbf72` (code identical to `a620399`). None of the four stale files touched a Phase 27 claim: two records grew by append only, `tests/test_api.py` changed a different test, and `tests/test_browser_pins.py` changed a comment, which also closed the previous report's IN-11 advisory. IN-12 is triaged `skipped` in `27-REVIEW-DISPOSITION.md`, so the advisory list is now empty. No debt item filed.

---

_Verified: 2026-10-23T01:37:17Z_
_Verifier: Claude (gsd-verifier)_
