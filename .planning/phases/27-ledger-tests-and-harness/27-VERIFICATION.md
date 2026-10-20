---
phase: 27-ledger-tests-and-harness
verified: 2026-10-20T00:00:00Z
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
covered_digest: "v3:sha256:7532a749958fe92820dd0db6469cffa2faa5ac001647ec0e5c1107e18ca86180"
behavior_unverified: 0
overrides_applied: 0
re_verification: false
gaps: []
advisory:
  - finding: "WR-03: stop_group's except clause covers CalledProcessError and OSError only; a ValueError from group_members' int() parse (or a hung ps, which has no timeout) skips SIGKILL and the reap after SIGTERM was sent"
    category: other
    reason: "SC3 as written is met (SIGTERM precedes every read; a failed ps fails as survivors unknown). The code's docstring claim 'a reader that fails must not stop the signals' is wider than the code. Reproduced by patching group_members to raise ValueError: it escapes stop_group after SIGTERM only."
    evidence_status: "reproduced (scratchpad run), not reachable from real ps output on macOS or Linux"
  - finding: "WR-02: tests/process_group.py is outside test_browser_pins._scan_set() (glob tests/*browser*.py plus capture_requests.py)"
    category: other
    reason: "Phase 27 moved stop_group/group_members out of browser_session.py, which the scan covers, so the scan surface shrank. The module holds no skip spelling and no environ read today (grep clean); a future edit could add one unseen."
    evidence_status: "confirmed: _scan_set() prints browser_session.py, capture_requests.py, test_browser.py"
  - finding: "WR-01: _problems' environ allowance climbs to the nearest statement and walks its whole body, so a marker constant in the body of an if/while/with/def allows a header read"
    category: other
    reason: "Reproduced: _problems('c.py', 'import os\\nif os.environ.get(\"CI_NO_BROWSER\"):\\n    x = \"SPUR_\"\\n') returns []. The rule is still tighter than the line-based one it replaced, and no such code exists in the scanned modules."
    evidence_status: "reproduced"
---

# Phase 27: Ledger Tests and Harness Verification Report

**Phase Goal:** The tests that guard the ledger cannot pass vacuously and the browser harness cannot lie: `slug()` totality is guarded in the commit slice, the failed-build name test no longer depends on cache order, `stop_group` signals the group before it inspects it, and the records and messages that describe the harness say what was observed.
**Verified:** 2026-10-20
**Status:** passed (with three advisory warnings, no gaps)
**Re-verification:** No, initial verification

## Goal Achievement

### Observable Truths (the four ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `slug()` totality guarded in the commit slice: seeded, stratified, every reachable reason bucket non-empty, two unreachable reasons forced and labelled, red against raising `_junction` and `_root_curve`, `verify.fast` under 30 s | VERIFIED | `tests/test_trochoid.py:269` `test_slug_is_total_and_ends_trochoid_exactly_when_root_mode_does`: `random.Random(20261020)`, five `_SlugBox` strata, asserts `name.endswith("_trochoid") == (rm.mode == "trochoid")` per draw, asserts `RootReason` members equal reachable plus forced, asserts every reachable bucket plus "trochoid" non-empty, asserts no validated draw reaches a forced reason. `:326` parametrized `forced-bracket-degenerate` / `forced-curve-invalid` patch `spur.calc._junction` / `_root_curve`. File name has no `browser`, not in the Makefile `--ignore` list (`Makefile:211-213`), so it runs in `verify.fast`. Reds on disk: `investigation/27-02-red-slug-junction.log` (`RuntimeError`, 1 failed) and `27-02-red-slug-root-curve.log` (`RuntimeError: mutated _root_curve`, `1 failed, 100 deselected in 0.08s`). I ran `-k slug`: 3 passed in 0.17 s. I ran `make verify.fast`: `932 passed in 12.28s`, 13.06 s wall, under L36's 30 s. |
| 2 | Failed-build name test reads 422 regardless of order; `_EXPORTS` replaced per test with a fresh `_BlobCache`; red when pre-seeded under the old code | VERIFIED | `tests/test_api.py:1304-1311` fixture `fresh_exports` does `monkeypatch.setattr(spur.app, "_EXPORTS", spur.app._BlobCache(1 << 20))`, applied by `@pytest.mark.usefixtures("fresh_exports")` to `test_a_failed_build_records_the_name_of_the_part_it_would_have_been` (asserts `r.status_code == 422` and non-empty caplog). Red: `investigation/27-02-red-name-preseeded.log` shows `assert 200 == 422` for both `applies` and `refused` rows with the old code and a pre-seeded cache (`2 failed, 1 passed`); `27-02-green-name-preseeded.log` is the matching green. I ran the test: 2 passed. |
| 3 | `stop_group` signals before it reads; a failed `ps` fails as "survivors unknown" with the group already signalled; SIGTERM grace and leader-only-break red kept; sub-second unit test outside the `*browser*` glob proves both paths and cleans up | VERIFIED (advisory WR-03) | `tests/process_group.py:stop_group`: per signal, `_signal_group(pgid, sig)` is the first statement, then `group_members` inside `try`; `proc.wait` runs only after the loop; there is no `proc.poll()`. `CalledProcessError`/`OSError` set `survivors = None` and `continue` to SIGKILL; `survivors is None` fails with "survivors unknown ... after SIGTERM and SIGKILL were sent". `TERM_BOUND_S = 10.0` grace kept. `tests/test_process_group.py` (no `browser` in name) records event order from wrapped functions: test 1 asserts `events[0] == "signal SIGTERM"` and exactly one signal when the group reads empty; test 2 (ids `ps-exits-non-zero`, `ps-is-absent`) asserts signals `["signal SIGTERM", "signal SIGKILL"]` and `survivors unknown`. A real `sleep 60` in its own session is killed and reaped in the fixture. I ran both files: 7 passed in 0.26 s together with the pins; `-k` red on the old order is in `27-03-red-old-order.log` (`3 failed in 0.05s`, `assert 'read' == 'signal SIGTERM'`). Leader-only red: see "Known deviation" below. |
| 4 | Harness describes itself truthfully: `MIN_GROUP_MEMBERS` comment names observed members; dated corrections under both `bench/RESULTS.md` rows with no reading rewritten; launch message names a working reinstall; text-only; pinned literal kept | VERIFIED | `tests/browser_session.py:55-67` names uvicorn, `multiprocessing.resource_tracker` and one or two spawned workers with macOS counts 4, 3, 4 and the ubuntu-latest run 39428298442 count 4, and says the floor stays `>= 3`. The Linux listing is real: `investigation/27-01-run-39428298442-test.log` holds `spur-group-listing:` rows for uvicorn, `resource_tracker`, and two `multiprocessing.spawn` workers, then `server group members before the kill: 4`. `bench/RESULTS.md`: two `**Correction (2026-10-20, 27-06)...**` paragraphs (lines 4781 and 4907) under the two rows; `git diff --numstat v0.5 -- bench/RESULTS.md` reads `676 0` (0 deleted); a `### Seen red once (Phase 27)` section exists at 6591. `launch()` (`browser_session.py:161-180`) now says "`rm -f .venv/.browser && make test` installs it again: the stamp alone skips the install while it is present" and keeps the literal `playwright install --only-shell chromium`; `VENV/.browser` is the Makefile stamp (`Makefile:22`). `test_browser_pins.py` pins both strings (`INSTALL_COMMAND`, `REINSTALL_COMMAND`, asserted inside `launch()`), reds in `27-05-red-launch-pin.log`. Pins file: passes. |

**Score:** 4/4 truths verified (0 present, behavior-unverified).

### Known deviation (27-03): leader-only SIGTERM mutation stayed green

The plan's literal break (`os.kill(pgid, sig)` to the leader only) left `tests/test_browser.py` green because uvicorn shuts its pool workers down on SIGTERM, so the group reads empty (`27-03-red-leader-only.log` run 1, `2 passed in 23.66s`). The executor ran the break that ROADMAP SC3 and `bench/RESULTS.md` row 21-01 actually name, `os.kill(pgid, signal.SIGKILL)` to the leader only (RESULTS.md line 4819: "`stop_group` sends SIGKILL to the leader only"). Run 2 goes red: `server process group 46075 still has live pids [46103, 46206, 49708] after SIGTERM (10 s) and SIGKILL (5 s)`, `2 passed, 1 error`. SC3 says "the leader-only-break red (row 21-01) are kept", and that red is the SIGKILL one, so the must-have is met; the plan's own mutation was weaker than the roadmap's. The module was restored (`cmp` clean per the SUMMARY; I confirmed `os.killpg(pgid, sig)` is what is in HEAD). Not a gap.

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|-------------|-------------|--------|----------|
| REQ-slug-totality-guarded | 27-02 | SATISFIED | Truth 1 |
| REQ-failed-build-name-isolated | 27-02 | SATISFIED | Truth 2 |
| REQ-stop-group-signals-first | 27-03 | SATISFIED | Truth 3 |
| REQ-group-floor-recorded-true | 27-01, 27-06 | SATISFIED | Truth 4 (comment, both corrections, Linux listing) |
| REQ-launch-message-true | 27-05 | SATISFIED | Truth 4 (launch message and pin) |

All five IDs in the phase brief appear in a PLAN `requirements:` field and in REQUIREMENTS.md (checked `[x]`, traceability table "Phase 27 / Complete"). No orphaned requirement. 27-04 declares `requirements: []` on purpose and `contributes_to: [REQ-info-findings-triaged]`, which Phase 28 closes; REQUIREMENTS.md does not mark it complete here.

### Boundaries and phase-close checks

| Check | Result |
|-------|--------|
| `git diff --exit-code v0.5 -- tests/regression/` | empty, exit 0 |
| `src/spur/` touched only by the optional 19 IN-01/02 line | `git diff --stat v0.5..HEAD -- src/` shows `src/spur/model.py | 10 +++---` and nothing else |
| `bench/RESULTS.md` append-only | 676 added, 0 deleted |
| L40 takes a dated amendment, not a rewrite | `git diff --numstat v0.5 -- docs/architecture/decision_log.md` reads `2 0`; no deleted line since phase start |
| `make verify` at f4aa341 | orchestrator-reported: exit 0, `1333 passed in 215.98s`, coverage 97.99% (not re-run by me); I re-ran `make verify.fast`: 932 passed, 13 s |
| Debt items retired | five items under `docs/tech_debt/resolved/`, each `Status: resolved` (the `Resolved in:` field holds subjects, see IN-06) |
| Untracked files | only `.planning/milestone.lock`, pre-existing |
| 27-01 spike commit | 9c42559 lives on `spike/27-group-listing` only, by design; the HEAD tree carries neither the print nor a workflow edit (`git diff 9943a7b..HEAD --stat -- .github` empty) |

### Anti-Patterns Found

No `TBD`/`FIXME`/`XXX` markers found by the gate (`make verify` includes the unfinished-work scan and passed). No stubs or hollow data flows: the new modules are all test code, and the one production change (`model.py`, `_chamfer_tips` takes `_build`'s `rm`) is checked by the existing model and bench tests.

### Review findings judged against the success criteria

| Finding | Defeats a success criterion? | Judgment |
|---------|------------------------------|----------|
| WR-03 (`stop_group` and a non-`CalledProcessError`/`OSError` reader failure; `ps` has no timeout) | No | SC3 asks that the group be signalled before any `ps` read and that a failed `ps` fail the teardown as "survivors unknown". Both hold: SIGTERM is the first statement of the loop body, and the two failure shapes a `ps` has (non-zero exit, absent binary) are tested. I reproduced the gap by patching `group_members` to raise `ValueError`: the error escapes after SIGTERM only, so SIGKILL and the reap are skipped. That output cannot come from `ps -A -o pgid=,stat=,pid=` on either host measured (every row is two ints and a state), so this is robustness, and the failure would be loud (an unrelated `ValueError` in teardown), not a silent pass. The `stop_group` docstring ("a reader that fails must not stop the signals") claims more than the code. Cheap to close: add `ValueError` and `subprocess.TimeoutExpired` to the `except` and a `timeout=5` to the `ps` call. Recommended before ship, not a blocker. |
| WR-02 (`tests/process_group.py` outside the pin scan) | No | The "harness cannot lie" clause is carried by SC4's truthful records and messages, which hold. But the phase moved code out of a scanned file, so the pin's coverage narrowed; I confirmed the scan set. The moved module is clean today (grep for skip, xfail, environ, importorskip finds nothing). A future skip spelling there would pass unseen. One line closes it (`found.add(REPO_ROOT / "tests" / "process_group.py")`). Recommended, not a blocker. |
| WR-01 (environ allowance bypassable in a compound statement) | No | I reproduced it. The 27-05 rule is statement-scoped, which is tighter than the line-scoped rule it replaced, and no scanned module has the shape. It is a pin-quality weakness, not a regression and not part of any SC. |
| IN-01 to IN-06 | No | Test-hygiene and record-wording points. IN-04 (nothing pins that `_build` passes `rm` to `_chamfer_tips`) is the only one about guard strength, and it concerns the `Rides with` 19 IN-01 line, not a success criterion. |

### Human Verification Required

None. Every success criterion was checked against code and a recorded or re-run test.

### Gaps Summary

No gaps. All four success criteria hold in the codebase, all five requirement IDs are accounted for, and the guard tests have recorded reds. Three review warnings are open (`27-REVIEW-DISPOSITION.md`, all `open`); none contradicts a success criterion, and WR-02 and WR-03 are cheap enough that Phase 28 or a short follow-up should close them before the harness is trusted for the red-first runs Phase 28 depends on.

---

_Verified: 2026-10-20_
_Verifier: Claude (gsd-verifier)_
