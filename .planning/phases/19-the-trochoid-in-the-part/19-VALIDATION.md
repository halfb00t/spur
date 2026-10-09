---
phase: "19"
slug: "the-trochoid-in-the-part"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-08"
validated: "2026-10-09"
---

# Phase 19 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov 7.1.0; `filterwarnings = ["error", ...]`, `--strict-markers` (read from `.venv` by 19-RESEARCH) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`; `[tool.coverage.*]` `branch = true`, `fail_under = 96`), `Makefile` |
| **Quick run command** | `make verify.fast` (commit-time slice, L36 — every test file except `test_model.py`, `test_pool.py`, `test_api.py`, `test_cli.py`); targeted: `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov"`, kernel rows `make test PYTEST_ARGS="tests/test_model.py -k trochoid -q -n0 --no-cov"` |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import contracts, unfinished-work scan, pytest `-n 8 --cov`, 96 % floor) |
| **Estimated runtime** | Measured 2026-10-09 on this host (Apple M5 Max, 18 CPUs, `PYTEST_WORKERS` 8): `make verify.fast` 11.39–11.54 s (`824 passed`, L36 kill 30 s); `make verify` 161.71–221.30 s wall (`1210 passed`; 19-09 three-run mean 192.94 s against L34's 66 s bar, which was read on an M2 Max — 19-01's same-host baseline 52.89 s, 1023 tests). The human accepted the cost (`accept-A`, 19-09; recorded in L38) rather than trim a kernel proof. |

---

## Sampling Rate

- **After every task commit:** `make verify.fast` (the L36 pre-commit hook) plus by hand `git diff --exit-code tests/regression/pre_v0_2.json` and `.venv/bin/python -m pytest tests/regression -q -n0 --no-cov`
- **After every plan wave:** `make verify`
- **Before `/gsd-verify-work`:** `make verify` green with its result line stated and its wall time recorded against the 66 s bar with host and load
- **Max feedback latency:** 30 seconds (L36 commit-time budget)

---

## Per-Task Verification Map

All 26 tasks of the 11 plans. Statuses are from the executors' SUMMARYs (every task's `<automated>` block ran green at its commit), the orchestrator's post-wave `make test` after every wave (last: `1210 passed in 196.77s`, 2026-10-09, exit 0, 0 `ReentrantCallError`), and a validate-phase re-run on 2026-10-09 of every cheap python/git check (29 of 33 green; the 4 red are the wave-1/2 "product modules untouched at the phase base" invariants, which held at their commits and were superseded by design once 19-04 shipped `root_shape` — the fixture `tests/regression/pre_v0_2.json` is still byte-identical to `df4749e`).

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 19-01-01 | 01 | 1 | REQ-trochoid-composes-and-is-priced, REQ-outline-consumes-root-curve | T-19-01 | the spike's outline assembled from the proven `RootCurve`, chamfer law re-bisected, no optimistic row | bench + pin | `make test PYTEST_ARGS="tests/test_bench.py -q -n0 --no-cov -k 'chamfer_law_verdict or chamfer_rows'"`; `.venv/bin/python -m bench.trochoid_part chamfer` → `Verdict: law holds` | ✅ | ✅ green |
| 19-01-02 | 01 | 1 | REQ-trochoid-composes-and-is-priced | T-19-02 | heaviest corner rows timed build + export against `SPUR_BUILD_TIMEOUT` 30 s, a row over stops the plan | bench + pin | `make test PYTEST_ARGS="tests/test_bench.py -q -n0 --no-cov -k 'corner_rows or chamfer_law_verdict or chamfer_rows'"`; `make verify` | ✅ | ✅ green |
| 19-02-01 | 02 | 2 | REQ-outline-consumes-root-curve, REQ-root-mode-decided | T-19-03 | kernel bar and `ROOT_ARC_MIN` computed by pure helpers pinned in tests, traceable to a measurement | unit + bench | `make test PYTEST_ARGS="tests/test_bench.py -q -n0 --no-cov -k 'proposed_bar or deviation_b'"`; `bench.trochoid_part spline`, `arc` | ✅ | ✅ green |
| 19-02-02 | 02 | 2 | REQ-derived-numbers-honest-under-trochoid | T-19-04 | guard bars read over every trochoid case of the 31,446-case product, not a sample; waist walk (D-07) | bench | `bench.trochoid_part product`, `waist`; RESULTS subsection check | ✅ | ✅ green |
| 19-02-03 | 02 | 2 | REQ-root-mode-decided, REQ-derived-numbers-honest-under-trochoid | — | the human's four answers recorded verbatim (`take the recommendations`, 2026-10-09) | decision | — (human checkpoint; the answers are in `19-02-SUMMARY.md` and `bench/RESULTS.md` "Bars adopted (19-02)", read by 19-10's L38 check) | ✅ | ✅ green |
| 19-03-01 | 03 | 2 | REQ-trochoid-composes-and-is-priced | — | the flake isolated by whole-log evidence, counts never estimated | investigation | `19-03-isolation.md` content check (`-n 8`, three configurations, counts) | ✅ | ✅ green |
| 19-03-02 | 03 | 2 | REQ-trochoid-composes-and-is-priced | T-19-05 | no blanket `filterwarnings` ignore; the human chose `debt-redefer` | decision | — (human checkpoint; recorded in `19-03-SUMMARY.md` and the debt file's dated paragraph) | ✅ | ✅ green |
| 19-03-03 | 03 | 2 | REQ-trochoid-composes-and-is-priced | T-19-05 | debt ledger consistent: file `active`, `must`, INDEX row carries the trigger | ledger check | `.venv/bin/python -c "..."` → `debt ledger consistent`; `make verify.fast` | ✅ | ✅ green |
| 19-04-01 | 04 | 3 | REQ-root-mode-decided, REQ-outline-consumes-root-curve, REQ-derived-numbers-honest-under-trochoid, REQ-cutter-tip-radius-settable | T-19-06, T-19-07, T-19-08 | `Literal["radial","trochoid"]` refuses anything else; default `radial`, radial outline body untouched, fixture byte-identical; one `root_mode` per consumer | unit + integration + regression | `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov"`; `tests/test_model.py -k hob_root`; `tests/test_cli.py tests/test_api.py`; `tests/regression`; SC1 check | ✅ | ✅ green |
| 19-04-02 | 04 | 3 | REQ-outline-consumes-root-curve | T-19-08, T-19-09 | built root read within 2e-3 × module by the independent oracle on all seven rows; tripwire fails at a 0.05 mm tip-radius error | kernel-tier | `make test PYTEST_ARGS="tests/test_model.py -q -n 8 --no-cov -k 'oracle_s_root or tip_radius_is_off or root_d_is_the_root_circle or nothing_radial'"`; `make verify` | ✅ | ✅ green |
| 19-05-01 | 05 | 4 | REQ-outline-consumes-root-curve | T-19-11 | arcs under `ROOT_ARC_MIN` share a vertex instead of calling `makeThreePointArc`; reachable from a typed backlash | kernel-tier + regression | `make test PYTEST_ARGS="tests/test_model.py -q -n0 --no-cov -k 'root_arc'"`; `ROOT_ARC_MIN` constant check; `tests/regression` | ✅ | ✅ green |
| 19-05-02 | 05 | 4 | REQ-outline-consumes-root-curve | T-19-10 | junction, spacing, annulus and area guards each a `BuildError` with the "modelling defect … root_shape" sentence, none resting on `isValid()` | kernel-tier | `make test PYTEST_ARGS="tests/test_model.py -q -n 8 --no-cov -k 'junction_is_a_build_error or spacing_bar or annulus_is_a_build_error or misses_its_polygon'"`; AST check of the four guards | ✅ | ✅ green |
| 19-05-03 | 05 | 4 | REQ-outline-consumes-root-curve | — | solid-model docs name the trochoid branch, the short-arc rule and the guards | docs check | `.venv/bin/python -c "..."` → `solid-model docs brought true`; `make verify` | ✅ | ✅ green |
| 19-06-01 | 06 | 4 | REQ-derived-numbers-honest-under-trochoid, REQ-cutter-tip-radius-settable | T-19-13 | `root_form_d` labelled the cutter-envelope junction, never ISO 21771; `root_waist` warned under the 0.4 mm floor; null on the radial default | unit + API | `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov -k 'root_form_d or root_waist or waist_warning or hob_root or pre_v0_2'"`; `tests/test_api.py -k 'openapi or ui_reads or tip_chamfer_link'`; `tests/regression` | ✅ | ✅ green |
| 19-06-02 | 06 | 4 | REQ-undercut-warning-restated | T-19-12 | undercut onset and the avoiding shift from the cutter actually used, rounded up, never above 1.0; radial fixture records byte-identical | unit + regression | `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov -k 'undercut or advised_shift or never_advised or trimmed or root_sentence or cap'"`; `tests/regression`; SC1 check | ✅ | ✅ green |
| 19-06-03 | 06 | 4 | REQ-derived-numbers-honest-under-trochoid | — | gear-maths docs name the hob-root branch of `derive()` | docs check | `.venv/bin/python -c "..."` → `gear-maths docs brought true`; `make verify` | ✅ | ✅ green |
| 19-07-01 | 07 | 5 | REQ-root-mode-decided | — | the human settled SC5's "exit 2" (`exit-documented`, 2026-10-09): parameter refusals exit 2 / 422, a root guard's `BuildError` exits 1 / 422 `build_error` (D-14) | decision | — (human checkpoint; recorded in `19-07-SUMMARY.md`, quoted in L38) | ✅ | ✅ green |
| 19-07-02 | 07 | 5 | REQ-trochoid-composes-and-is-priced, REQ-cutter-tip-radius-settable | T-19-14, T-19-15 | no case or whitespace variant normalised; the guard's 422 text names check and remedy only | integration (CLI + API) | `make test PYTEST_ARGS="tests/test_cli.py tests/test_api.py -q --no-cov -k 'trochoid or root_shape or root_guard or readme or every_gear_field'"`; `make verify` | ✅ | ✅ green |
| 19-08-01 | 08 | 5 | REQ-trochoid-composes-and-is-priced | — | 192 calc-tier rows in both root modes, every trochoid row reads its radial twin's numbers | unit matrix | `make test PYTEST_ARGS="tests/test_calc.py -q -n 8 --no-cov -k every_bore_cutout_recess_and_tip"`; `tests/test_cli.py -k refusal` | ✅ | ✅ green |
| 19-08-02 | 08 | 5 | REQ-trochoid-composes-and-is-priced | T-19-16, T-19-17 | tip-chamfer cap pinned one step either side of the hob-root junction; edge selectors never take a root arc | kernel-tier matrix | `make test PYTEST_ARGS="tests/test_model.py -q -n 8 --no-cov -k 'every_feature_proof_holds or each_edge_selector or hob_root_junction or bare_trochoid'"`; `make verify` | ✅ | ✅ green |
| 19-09-01 | 09 | 6 | REQ-trochoid-composes-and-is-priced | T-19-18 | the bench builds through `spur.model` (one outline definition); every corner row in both shapes inside 30 s (heaviest 14.64 s) | bench + pin | `make test PYTEST_ARGS="tests/test_bench.py -q -n0 --no-cov -k 'trochoid_sweep or corner_rows or chamfer_law_verdict or proposed_bar'"`; `make bench.build SWEEP=bench/sweeps/trochoid.json` | ✅ | ✅ green |
| 19-09-02 | 09 | 6 | REQ-trochoid-composes-and-is-priced | T-19-19 | before and after read on one host with loads; the 66 s and 30 s gates stopped for the human; no test trimmed | measurement + record check | `.venv/bin/python -c "..."` → `19-09 gate subsection present`, `derive docstring re-measured`; `make verify` | ✅ | ✅ green (wall time itself manual, see below) |
| 19-10-01 | 10 | 7 | REQ-root-mode-decided, REQ-trochoid-composes-and-is-priced, REQ-undercut-warning-restated | T-19-20 | L38 appended with no earlier line changed; every figure cited to a sha or a RESULTS subsection | docs check (append-only diff) | `.venv/bin/python -c "..."` → `L38 appended, nothing earlier edited`, `strategy docs point at L38`; `make verify` | ✅ | ✅ green |
| 19-11-01 | 11 | 7 | REQ-root-mode-decided, REQ-undercut-warning-restated | T-19-21 | README names `root_shape`, `root_form_d` as the cutter-envelope junction, never an ISO form diameter; README commands still run | docs check + CLI | `.venv/bin/python -c "..."` → `README and ideas brought true`; `make test PYTEST_ARGS="tests/test_cli.py -q --no-cov -k readme"` | ✅ | ✅ green |
| 19-11-02 | 11 | 7 | REQ-root-mode-decided | T-19-21 | Phase 20 skipped the way ROADMAP's skip condition prescribes, naming L38 and D-09's trigger; nothing orphaned | planning-record check | `.venv/bin/python -c "..."` → `Phase 20 skip recorded`; `make verify` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Requirement → test cross-reference (validate-phase, 2026-10-09)

| Requirement | Where it is proved | Status |
|---|---|---|
| REQ-root-mode-decided | `## L38` in `docs/architecture/decision_log.md` (19-10 append-only check); `tests/test_cli.py` / `tests/test_api.py` `test_both_root_shapes_are_accepted_and_omitting_it_reads_radial`, `test_an_unknown_root_shape_exits_2_on_the_cli_and_is_a_422_on_the_api`, `test_a_link_that_spells_the_default_root_shape_is_the_link_that_omits_it`; `tests/regression/test_pre_v0_2.py` (fixture byte-identical) | COVERED |
| REQ-outline-consumes-root-curve | `tests/test_model.py` `test_the_built_root_is_the_oracle_s_root_on_every_kernel_row`, `test_the_default_gear_asked_for_the_hob_root_builds_the_oracle_s_root`, `test_the_kernel_tier_proof_fails_when_the_printed_tip_radius_is_off_by_0_05_mm`, the four guard tests, the `root_arc` tests, `test_the_trochoid_generator_never_enters_the_model_module` | COVERED |
| REQ-derived-numbers-honest-under-trochoid | `tests/test_trochoid.py` `test_root_form_d_is_twice_the_junction_radius_and_null_when_radial`, `test_the_root_waist_is_printed_where_the_trochoid_applies_and_null_elsewhere`, `test_the_default_gear_asked_for_the_hob_root_prints_its_numbers_and_no_radial_ones`; `tests/test_api.py` `test_root_form_d_is_never_labelled_an_iso_form_diameter_where_a_user_reads_it` | COVERED |
| REQ-cutter-tip-radius-settable | `tests/test_trochoid.py` `test_the_trimmed_tip_radius_is_printed_and_warned_one_step_either_side_of_the_cap`, `test_the_cap_is_floored_and_warned_one_print_step_either_side`, `test_a_tip_radius_that_is_not_a_finite_millimetre_value_is_refused_before_any_cap`; `tests/test_cli.py` `test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order` | COVERED |
| REQ-undercut-warning-restated | `tests/test_trochoid.py` `test_the_restated_undercut_sentence_fires_at_17_teeth_and_not_18`, `test_the_advised_shift_is_rounded_up_and_flips_the_gear_out_of_undercut`, `test_a_refused_trochoid_request_keeps_the_shipped_undercut_sentence`, `test_the_undercut_onset_closed_forms_match_the_published_tables`; `tests/regression/test_pre_v0_2.py` | COVERED |
| REQ-trochoid-composes-and-is-priced | `tests/test_calc.py` 192-row matrix (`every_bore_cutout_recess_and_tip`), `tests/test_model.py` 24-row matrix (`test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore`), `test_the_largest_tip_chamfer_the_hob_root_junction_allows_builds`, `test_the_kernel_fails_one_step_past_the_hob_root_junction`; `tests/test_cli.py` `test_cli_and_api_print_the_same_trochoid_documents`; `tests/test_bench.py` sweep and corner-row pins; `bench/RESULTS.md` "Heaviest low-tooth rows", "The gate, priced (19-09)" (record presence asserted by 19-09's checks; the wall time itself is the manual reading below) | COVERED (1 manual reading) |

---

## Wave 0 Requirements

- [x] `tests/test_trochoid.py` — derive branch, sentences, waist/floor, `x_min`, `spline_start`/chamfer limit, enum/CLI parity pieces that need no kernel
- [x] `tests/test_model.py` — kernel tier (build rows, `Edge.positionAt` vs oracle, guards, short-arc branch, compose matrix, `_tip_edges` selector column)
- [x] `tests/test_cli.py` (field-walk generalisation, parity document, bad value exit 2) and `tests/test_api.py` (line 315 adjacency, the literal field set, the `DerivedDimensions` key set at line 78)
- [x] `tests/composition.py` — a root axis or a separate trochoid table; `ALWAYS` split for null `root_thickness`/`root_gap`
- [x] `bench/` spike subcommands, `bench/sweeps/trochoid.json`, `tests/test_bench.py` pin, `bench/RESULTS.md` section
- [x] Framework install: none — existing infrastructure covers the phase

All Wave 0 items were delivered by plans 19-01 to 19-09 (`tests/test_trochoid.py` 50 tests, `tests/test_model.py` 69, `tests/test_bench.py` 43, `tests/composition.py` root axis, `bench/sweeps/trochoid.json`).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `make verify` wall time against the 66 s bar (L34) | REQ-trochoid-composes-and-is-priced | A timing is read on one host with its load noted, not asserted by a test | Run `make verify` by hand; record wall time, host, CPU count and load in `bench/RESULTS.md`. Done by 19-09 (`### The gate, priced (19-09)`: three runs 208.52 / 161.71 / 208.60 s, mean 192.94 s, loads 4–9, Apple M5 Max 18 CPUs) and accepted by the human (`accept-A`, 2026-10-09; L38). |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (23 of 26 tasks carry `<automated>` blocks; the 3 without — 19-02-03, 19-03-02, 19-07-01 — are human-checkpoint decision tasks whose recorded answers are read by 19-10's automated L38 check)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (none MISSING)
- [x] No watch-mode flags
- [x] Feedback latency < 30s (`make verify.fast` 11.39–11.54 s at commit time, L36)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-10-09 (validate-phase, state A audit: 0 gaps found, 0 resolved, 0 escalated; 1 manual-only reading recorded and accepted)

## Validation Audit 2026-10-09

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
