---
phase: "18"
slug: "trochoid-maths-proved"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-07"
validated: "2026-10-08"
---

# Phase 18 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (pytest-xdist, pytest-cov), `filterwarnings = ["error", ...]`, `xfail_strict = true` |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`), `Makefile` |
| **Quick run command** | `make verify.fast` (static steps + every test file but the four heavy ones; L36 budget 30 s) |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import contracts, unfinished-work scan, pytest `-n 8 --cov`, 96 % floor) |
| **Estimated runtime** | `make verify.fast` 14.4–14.8 s (18-03 measurement); `make verify` 63–86 s wall (18-01..18-05 runs) |

---

## Sampling Rate

- **After every task commit:** `make verify.fast` runs as the pre-commit hook (L36); every Phase 18 commit went through it, none with `--no-verify` or `SKIP=`.
- **After every plan wave:** `make verify` — run by the executor at each plan's close and again by the orchestrator after each wave (963, 981, 996, 1016, 1017 passed; coverage 97.29 % → 97.68 %).
- **Before `/gsd-verify-work`:** Full suite green — `make verify` at wave 5 close: `1017 passed in 72.28s`; after gap plan 18-06: `1022 passed in 90.62s`, `Total coverage: 97.68%`.
- **Max feedback latency:** ~15 s (`make verify.fast`), under the 18 s target set at planning.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 18-01-01 | 01 | 1 | REQ-cutter-defined-once, REQ-trochoid-root-generated, REQ-trochoid-proved-independently | — | N/A (pure maths; no input crosses a trust boundary) | unit + oracle | `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov"` (tracer, oracle-with-neighbours, `calc`-independence AST check) | ✅ `tests/test_trochoid.py`, `tests/trochoid_oracle.py` | ✅ green |
| 18-01-02 | 01 | 1 | REQ-cutter-defined-once | — | N/A | unit | `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov"` (cap reconciliation, floored cap, tip-land limit, junction equality at backlash 0 / 0.10) | ✅ `tests/test_trochoid.py` | ✅ green |
| 18-02-01 | 02 | 2 | REQ-root-mode-single-predicate | — | N/A | unit + fixture | `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov"` (six refusals in order, `nothing radial to replace`, `tooth severed`, fixture straddles the three undercuts) | ✅ `tests/test_trochoid.py` | ✅ green |
| 18-02-02 | 02 | 2 | REQ-root-mode-single-predicate, REQ-trochoid-proved-independently | — | N/A | unit (T1 closed form) | `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov"` (undercut onset vs published tables, T1 over the grid) | ✅ `tests/test_trochoid.py` | ✅ green |
| 18-03-01 | 03 | 3 | REQ-trochoid-root-generated | — | N/A | unit | `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov"` (z_min double root one step either side, join epsilon separates found from degenerate, every structural failure refused) | ✅ `tests/test_trochoid.py` | ✅ green |
| 18-03-02 | 03 | 3 | REQ-trochoid-root-generated | — | N/A | gate sweep | `make test PYTEST_ARGS="tests/test_calc.py tests/test_bench.py -q -n 8 --no-cov -k 'trochoid or check_curve'"` (31,446-case box sweep, 0 numerical failures, 1.7 s at `-n 8`) | ✅ `tests/test_calc.py::test_the_trochoid_sweep_over_the_allowed_box`, `tests/test_bench.py` | ✅ green |
| 18-03-03 | 03 | 3 | — (checkpoint:decision, D-11) | — | N/A | decision | not reached — sweep reported no unnamed refusal and no numerical failure | n/a | ✅ recorded in 18-03-SUMMARY.md |
| 18-04-01 | 04 | 4 | REQ-trochoid-proved-independently | — | N/A | oracle (T2) | `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov --durations=5 -k t2_"` (twelve gate rows, three negative controls, 1e-6 mm tip-radius tripwire; bench oracle over the whole product) | ✅ `tests/test_trochoid.py`, `bench/trochoid.py` | ✅ green |
| 18-04-02 | 04 | 4 | REQ-trochoid-proved-independently | — | N/A | cross-check (T3, T4) | `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov -k 't3_ or t4_'"` (freecad.gears literals with provenance; KISSsoft form diameter) | ✅ `tests/test_trochoid.py` | ✅ green |
| 18-04-03 | 04 | 4 | — (checkpoint:decision, L33 D-06) | — | N/A | decision | not reached — every bar other than T4's at or above 10× (smallest 72×) | n/a | ✅ recorded in 18-04-SUMMARY.md |
| 18-05-01 | 05 | 5 | REQ-root-mode-single-predicate, REQ-trochoid-root-generated | — | N/A | bench + pin | `make test PYTEST_ARGS="tests/test_bench.py -q -n0 --no-cov -k d05_premise"` (D-05 line committed before the measurement; step tables; per-call costs) | ✅ `tests/test_bench.py`, `bench/trochoid.py` | ✅ green |
| 18-05-02 | 05 | 5 | — (checkpoint:decision, D-05 + debt) | — | N/A | decision | human decided `d05-hold`, `debt-redefer` (2026-10-08) | n/a | ✅ recorded in 18-05-SUMMARY.md |
| 18-05-03 | 05 | 5 | REQ-root-mode-single-predicate, REQ-trochoid-root-generated | — | N/A | gate | `make verify` (full) + SC5 check (fixture byte-identical, only `calc.py` under `src/spur`, stdlib maths, 31 pins) | ✅ | ✅ green — `1017 passed in 85.12s`, coverage 97.68 % |
| 18-06-01 | 06 (gap) | 6 | REQ-trochoid-root-generated | T-18-18 | the fourth `curve invalid` arm refuses a crossing curve with an early point outside the involute, never heals it | unit + mutation | `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov -k 'curve_invalid or outside_the_involute'"`; `False` mutant on a scratch copy: `1 failed, 503 passed` (control `504 passed`) | ✅ `tests/test_trochoid.py::test_a_crossing_curve_with_an_early_point_outside_the_involute_is_refused` | ✅ green |
| 18-06-02 | 06 (gap) | 6 | REQ-cutter-defined-once | T-18-17 | `cutter()` raises `ValueError` on a non-finite or negative tip radius; a NaN can never be trimmed silently to the cap (L05/L08) | unit | `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov -k finite_millimetre"`; `make verify` → `1022 passed`, SC5 holds | ✅ `src/spur/calc.py:1291`, `tests/test_trochoid.py::test_a_tip_radius_that_is_not_a_finite_millimetre_value_is_refused_before_any_cap` | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Requirement coverage (cross-referenced against `tests/` on 2026-10-08, all green under `make verify`):

| Requirement | Tests | Status |
|-------------|-------|--------|
| REQ-cutter-defined-once | `test_the_cutter_reads_the_root_circle_from_the_same_expression_as_profile`, `test_the_cap_formula_reconciles_…`, `test_the_cap_is_floored_and_warned_…`, `test_the_tip_land_limit_moves_…`, `test_a_sharp_cutter_and_a_corner_centre_…`, `test_a_tip_radius_that_is_not_a_finite_millimetre_value_is_refused_before_any_cap` (18-06) | COVERED |
| REQ-trochoid-root-generated | `test_the_tracer_gear_is_cut_by_its_cutter_and_nothing_else`, `test_the_double_root_at_z_min_…`, `test_the_join_epsilon_separates_…`, `test_every_structural_failure_is_refused_as_curve_invalid`, `test_a_crossing_curve_with_an_early_point_outside_the_involute_is_refused` (18-06, seen red under mutation), `test_a_root_curve_is_immutable_…`, `test_calc.py::test_the_trochoid_sweep_over_the_allowed_box` | COVERED |
| REQ-root-mode-single-predicate | `test_root_mode_hands_back_…`, `test_root_mode_refuses_where_the_cutter_has_no_tip_land`, `test_a_gear_failing_two_tests_reports_the_first`, `test_a_severed_tooth_is_refused_…`, `test_the_fixture_straddles_the_three_undercuts_…`, `test_nothing_requested_leaves_the_root_radial_and_silent`, 18-05's no-consumer check | COVERED |
| REQ-trochoid-proved-independently | `tests/trochoid_oracle.py` (no `spur.calc` import, AST-checked), `test_t2_*` (4), `test_t3_*` (2), `test_t4_*` (2), `test_bench.py::test_the_oracle_worker_reads_a_curve_clean_and_a_severed_tooth_as_a_gouge` | COVERED |

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No Wave 0 was needed: pytest, xdist and coverage were in place before the phase; `tests/test_trochoid.py` and `tests/trochoid_oracle.py` were created by 18-01 Task 1.

---

## Manual-Only Verifications

All phase behaviors have automated verification. The three `checkpoint:decision` tasks are human decisions, not behaviours; their outcomes are recorded in the plan SUMMARYs and, for 18-05, beside the step tables in `bench/RESULTS.md`.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (none)
- [x] No watch-mode flags
- [x] Feedback latency < 18s (`make verify.fast` 14.4–14.8 s)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-10-08 (validate-phase audit, state A: draft template filled from the five executed plans and the test tree)

## Validation Audit 2026-10-08

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

## Validation Audit 2026-10-08

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
| Gap plan 18-06 rows added | 2 |
