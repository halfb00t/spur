---
phase: 27
status: draft
closes_in: 28
recorded: 2026-10-20
---

# Phase 27: draft triage of the review info findings

Phase 27 fixed most of the open info findings of Phases 19 and 21-24; this draft starts the table so Phase 28's close is a reading,
not a first pass. The authoritative record stays each `*-REVIEW-DISPOSITION.md`, which Phase 28 writes. Vocabulary: `fixed` + sha,
`deferred` + debt or idea path, `skipped` + a one-line reason, `open`. Shas are read from `git log` on `gsd/phase-27-ledger-tests-and-harness`;
a Phase 25 or 26 branch commit was squash-merged, so the row names the squash commit that is an ancestor of HEAD and the branch commit
beside it. `19-REVIEW-DISPOSITION.md` reads `skipped` for IN-01 to IN-04 today with no reason (the review-fix stage's word); the
proposed dispositions below replace that.

| Finding | Review | Proposed disposition | Fix / path | Phase |
|---|---|---|---|---|
| 19 IN-01 | `19-REVIEW.md` | fixed | `f7d0366` (`_chamfer_tips` takes `_build`'s one `RootMode`; the only `src/` change of the milestone, fixture byte-identical) | 27 |
| 19 IN-02 (bench half) | `19-REVIEW.md` | fixed | `9c62fac` (`trochoid_curve` reads `rm.curve`; the stale paragraph replaced) | 27 |
| 19 IN-02 (near-copy replacement) | `19-REVIEW.md` | skipped | the bench's near-copies (`root_edges`, `tooth0_root_edges`, `oracle_reading`) stay: they differ from the test helpers in error type (the test helper asserts against `ValueError`), in sample count (a fixed 400 against a `samples` parameter) and in signature (D-07) | 27 |
| 19 IN-03 | `19-REVIEW.md` | fixed (already resolved) | `34270c8` (Phase 25 branch commit, landed as `cbbe730`, PR #38); the debt file says so | - |
| 19 IN-04 (`_host_state`) | `19-REVIEW.md` | fixed | `9c62fac` (reads `unknown` where git cannot name HEAD; seen red first) | 27 |
| 19 IN-04 (`root_fillet` label) | `19-REVIEW.md` | open | REQ-root-fillet-label-follows-root; `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` | 28 |
| 21 WR-01 | `21-REVIEW.md` | fixed | `a7c5f78` (`stop_group` signals before it reads `ps`; the group teardown was first moved to a playwright-free module in `675cf68`); `docs/tech_debt/resolved/2026-10-10-stop-group-reads-ps-before-it-signals.md` | 27 |
| 21 WR-02 | `21-REVIEW.md` | fixed | `99e2b7d` (the `MIN_GROUP_MEMBERS` comment from 27-01's two listings, two dated corrections); `docs/tech_debt/resolved/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md` | 27 |
| 21 WR-03 | `21-REVIEW.md` | fixed | `a393e50` (the launch failure names the reinstall that works); `docs/tech_debt/resolved/2026-10-10-launch-failure-message-names-a-stamp-that-skips-the-install.md` | 27 |
| 21 IN-01 | `21-REVIEW.md` | fixed | `a7c5f78` (the dead assignment and the misleading bound are gone with the reorder) | 27 |
| 21 IN-02 | `21-REVIEW.md` | fixed | `4d43b64` (`fixture_hash` refuses a non-scalar param; seen red first) | 27 |
| 21 IN-03 | `21-REVIEW.md` | fixed | `0ed2057` (the environ allowance is read from the statement, not the line; seen red first) | 27 |
| 21 IN-04 (04a, the waits) | `21-REVIEW.md` | fixed | `1981d93` (PR #41; branch commit `6ff1269` bounds `_follow_link`'s `/api/info` wait by `BUILD_WAIT_MS`) | 26 |
| 21 IN-04 (04b, the hot loop) | `21-REVIEW.md` | deferred | `docs/tech_debt/active/2026-10-15-wait-until-parked-spins-without-a-pause.md` | 28 (record) |
| 22 WR-01 | `22-REVIEW.md` | fixed | `345ee08` (a seeded, stratified `slug()` totality test in the commit slice; seen red twice); `docs/tech_debt/resolved/2026-10-15-slug-totality-is-not-guarded-in-the-gate.md` (the file reads `deferred` today) | 27 |
| 22 WR-02 | `22-REVIEW.md` | fixed | `c47bfc4` (the failed-build name test gets its own export cache; seen red with a pre-seed); `docs/tech_debt/resolved/2026-10-15-failed-build-name-test-depends-on-cache-order.md` (the file reads `deferred` today) | 27 |
| 22 IN-01 | `22-REVIEW.md` | fixed | `c30ebd0` (one `BORE_OFF` in `tests/composition.py` for the finding's two files). Inline copies outside them are left: `tests/test_cli.py:524` `_BORE_OFF`, and bore-off field blocks in `tests/test_calc.py`, `tests/test_bench.py` and `tests/test_model.py` | 27 |
| 22 IN-02 | `22-REVIEW.md` | fixed | `4d43b64` (`serve_stl_from`'s docstring re-wrapped) | 27 |
| 22 IN-03 | `22-REVIEW.md` | fixed | `d7f069d` (L40's dated amendment: 1.13 to 3.56 s, mean 2.63 s, `BUILD_WAIT_MS` unchanged) | 27 |
| 23 IN-08 | `23-REVIEW.md` | fixed | `c30ebd0` (`honeycomb (4)` joins `CUTOUT_STATES`; the meta-test probes the gate twice; seen red first) | 27 |
| 23 IN-11 | `23-REVIEW.md` | fixed | `4d43b64` (`_js_number` asserts the range JavaScript writes positionally and writes `-0` as `0`; seen red first) | 27 |
| 24 IN-01 | `24-REVIEW.md` | open | the `app.js` stash comment | 28 |
| 24 IN-02 / CX-03 | `24-REVIEW.md`, `24-CROSS-REVIEW.md` | open | "Could not build the form" for a selector naming a group no field has | 28 |
| 24 IN-03 | `24-REVIEW.md` | fixed | `c30ebd0` (`_has_key` walks the parsed `/openapi.json` for the key `selectors`; seen red first) | 27 |
| 24 IN-04 | `24-REVIEW.md` | deferred | `docs/ideas/2026-10-14-hex-warning-names-fields-by-form-title.md` | 28 (record) |
| 24 CX-05 | `24-CROSS-REVIEW.md` | fixed | `1981d93` (PR #41; branch commit `6ff1269` settles past the 350 ms debounce before the zero-request assertion) | 26 |
| Phase 18 IN-01..IN-08, Phase 10 IN-01/IN-02 | `18-REVIEW.md`, `10-REVIEW.md` | open | REQ-old-info-findings-triaged: overtaken ones closed with a reason (18 IN-02, IN-06), the 18 IN-07 docstring fixed, the rest filed as one `nice` item with a named trigger, 10 IN-02 filed as a decision for the human | 28 |
| Phase 26 IN-01..IN-05 | `26-REVIEW.md` | open | five `\| info \| open \|` rows in `26-REVIEW-DISPOSITION.md` that neither REQUIREMENTS nor the roadmap lists: raise at Phase 28, not triaged here | 28 |

Totals by proposed disposition, in rows (28 rows; the Phase 18 and 10 row groups ten findings and the Phase 26 row five): fixed 20,
skipped 1, deferred 2, open 5 (19 IN-04's label, 24 IN-01, 24 IN-02 / CX-03, the Phase 18 and 10 group, the Phase 26 group).
