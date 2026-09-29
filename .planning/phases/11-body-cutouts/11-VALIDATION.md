---
phase: "11"
slug: "body-cutouts"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-09-29"
validated: "2026-09-29"
audited_at_head: "3424078"
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Audited after execution (State A, 2026-09-29): every requirement has green automated
> coverage at HEAD `3424078`; no gaps were sent to the Nyquist auditor.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (Python 3.12, `.venv`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `make test PYTEST_ARGS="tests/test_calc.py -q"` (any file subset via `PYTEST_ARGS`) |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import contracts, unfinished-work scan, pytest) |
| **Estimated runtime** | ~178 s wall for `make verify` at phase end (621 tests; was 98 s / 453 tests after Phase 10 — `bench/RESULTS.md` "make verify wall time") |

---

## Sampling Rate

- **After every task commit:** Run `make test PYTEST_ARGS="<the task's test files> -q"` (each task's `<automated>` block names them)
- **After every plan wave:** Run `make verify` (the pre-commit hook runs it on every commit; the orchestrator re-ran `make test` after every wave: 455 → 482 → 515 → 539 → 542 → 596 → 621 passed, all green)
- **Before `/gsd-verify-work`:** Full suite must be green — 621 passed in 178.44 s at `3424078`
- **Max feedback latency:** ~180 s (full suite, loaded desktop host); ~20 s for a single-file quick run

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | REQ-spoke-cutout | — | N/A (planning text) | docs | `sed -n '/REQ-spoke-cutout/,/REQ-hole-cutout/p' .planning/REQUIREMENTS.md \| grep -cF 'spoke_fillet'` | ✅ | ✅ green |
| 11-01-02 | 01 | 1 | REQ-spoke-cutout | T-11-02 | Human's wording + arm-rule answer recorded verbatim | checkpoint | `git diff --quiet -- .planning/ROADMAP.md` (nothing written before approval) | ✅ | ✅ green |
| 11-01-03 | 01 | 1 | REQ-spoke-cutout | T-11-01 | ROADMAP written only through edit-phase's write step; milestone scope unchanged | docs | `git show --name-only --format= HEAD` = exactly REQUIREMENTS/ROADMAP/STATE | ✅ | ✅ green |
| 11-02-01 | 02 | 2 | REQ-honeycomb-cutout | T-11-03 | Every row timed twice, kept in the record | bench (tracer) | `make lint typecheck && .venv/bin/python -c "from bench.honeycomb_spike import cost_row; ..."` | ✅ | ✅ green |
| 11-02-02 | 02 | 2 | REQ-honeycomb-cutout | T-11-04 | Cap measured against 7.5 s before any field exists | bench | `sed -n '/^## Honeycomb cell-count spike/,$p' bench/RESULTS.md \| grep -cE '^\*\*Cap:\*\* HEX_CELL_CAP'` | ✅ | ✅ green |
| 11-03-01 | 03 | 3 | REQ-hole-cutout, REQ-cutout-composes, REQ-cutout-derived-numbers | T-11-06, T-11-07 | Printed walls read from the same datums the cut uses | integration (api/cli/model), unit (calc) | `make test PYTEST_ARGS="tests/test_api.py tests/test_model.py tests/test_calc.py tests/test_cli.py tests/regression -q"` | ✅ | ✅ green |
| 11-03-02 | 03 | 3 | REQ-cutout-conflicts-refused-early | T-11-05 | A wall breach is a 422 / exit 2 before any CAD work | unit (calc), integration (cli/api) | `make test PYTEST_ARGS="tests/test_calc.py tests/test_cli.py tests/test_api.py tests/test_model.py tests/regression -q"` | ✅ | ✅ green |
| 11-04-01 | 04 | 4 | REQ-spoke-cutout, REQ-cutout-derived-numbers | T-11-08, T-11-09 | Sector wire cannot self-intersect; printed fillet == cut fillet | integration (api/cli/model), unit (calc) | `make test PYTEST_ARGS="tests/test_api.py tests/test_model.py tests/test_calc.py tests/test_cli.py tests/regression -q"` | ✅ | ✅ green |
| 11-04-02 | 04 | 4 | REQ-one-cutout-pattern, REQ-cutout-conflicts-refused-early | T-11-10 | Two patterns / any spoke wall breach refused before CAD | unit (calc), integration (cli/api) | `make test PYTEST_ARGS="tests/test_calc.py tests/test_cli.py tests/test_api.py tests/test_model.py tests/regression -q"` | ✅ | ✅ green |
| 11-05-01 | 05 | 5 | REQ-honeycomb-cutout, REQ-cutout-derived-numbers | T-11-11, T-11-13 | Enumeration bounded (7.4 ms); one `hex_cells()` result feeds check, derive and the cut | integration (api/cli/model), unit (calc) | `make test PYTEST_ARGS="tests/test_api.py tests/test_model.py tests/test_calc.py tests/test_cli.py tests/test_bench.py tests/regression -q"` | ✅ | ✅ green |
| 11-05-02 | 05 | 5 | REQ-one-cutout-pattern, REQ-cutout-conflicts-refused-early | T-11-12 | Honeycombs that cannot exist refused; cap from the measured record | unit (calc), integration (cli/api) | `make test PYTEST_ARGS="tests/test_calc.py tests/test_cli.py tests/test_api.py tests/test_model.py tests/regression -q"` | ✅ | ✅ green |
| 11-06-01 | 06 | 6 | REQ-hole-cutout, REQ-spoke-cutout, REQ-honeycomb-cutout | T-11-15 | Every sweep row recorded; none dropped or re-run until green | bench | `make test PYTEST_ARGS="tests/test_bench.py -q"` | ✅ | ✅ green |
| 11-06-02 | 06 | 6 | (D-18 gate) | — | Over-budget rows halt for a human; no source touched before the decision | checkpoint | `git diff --quiet -- src/spur/params.py src/spur/calc.py` | ✅ | ✅ green |
| 11-06-03 | 06 | 6 | REQ-hole-cutout, REQ-spoke-cutout | T-11-14 | Every allowed configuration builds inside 30 s (`le` 60 / 40) | unit (calc/api), bench | `make test PYTEST_ARGS="tests/test_calc.py tests/test_api.py tests/test_bench.py tests/regression -q"` | ✅ | ✅ green |
| 11-07-01 | 07 | 7 | REQ-cutout-composes | T-11-16 | Each selector takes exactly its own edges with every cutout | integration (kernel) | `make test PYTEST_ARGS="tests/test_model.py -q -k 'selector_takes_only_its_own_edges_with_a_body_cutout or tip_'"` | ✅ | ✅ green |
| 11-07-02 | 07 | 7 | REQ-cutout-conflicts-refused-early | T-11-17 | Rules sit where the part needs them, one step either side, proven on the kernel | integration (kernel) | `make test PYTEST_ARGS="tests/test_model.py tests/regression -q" && git diff --exit-code tests/regression/pre_v0_2.json` | ✅ | ✅ green |
| 11-08-01 | 08 | 8 | REQ-cutout-derived-numbers, REQ-hole-cutout, REQ-spoke-cutout, REQ-honeycomb-cutout | T-11-18 | A skipped or misplaced cut fails the proof while derive() still prints | integration (kernel) | `make test PYTEST_ARGS="tests/test_model.py -q -k 'exactly_what_derive_prints or cutout_proof_fails or same_cutout_link'"` | ✅ | ✅ green |
| 11-08-02 | 08 | 8 | REQ-cutout-composes | T-11-19 | Recess floor fillet survives on every floor edge, counted | integration (kernel) | `make test PYTEST_ARGS="tests/test_model.py tests/regression -q" && git diff --exit-code tests/regression/pre_v0_2.json` | ✅ | ✅ green |
| 11-09-01 | 09 | 9 | REQ-hole-cutout, REQ-spoke-cutout, REQ-honeycomb-cutout | T-11-20 | README examples run as tests | integration (cli) | `make test PYTEST_ARGS="tests/test_cli.py tests/regression -q"` | ✅ | ✅ green |
| 11-09-02 | 09 | 9 | REQ-cutout-derived-numbers | T-11-21 | Decision log appended, never edited (0 deleted lines) | docs | `git diff --numstat b86a0e9 -- docs/architecture/decision_log.md` (deletions == 0) | ✅ | ✅ green |
| 11-09-03 | 09 | 9 | (phase close-out) | — | Gate cost measured, not assumed | full gate | `make verify` | ✅ | ✅ green (621 passed, 177.62 s) |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Requirement → test evidence (all green at `3424078`; names read like the requirement):

| Requirement | Evidence (test names, `tests/`) | Status |
|-------------|--------------------------------|--------|
| REQ-hole-cutout | `test_the_hole_link_cuts_six_holes_through_the_recessed_floor`, `test_a_hole_link_is_served_with_its_walls`, `test_cli_and_api_print_the_same_hole_document`, `test_the_hole_count_is_an_integer_from_0_to_60`, `test_the_hole_cutout_sweep_is_every_combination_the_plan_names` | COVERED |
| REQ-spoke-cutout | `test_a_spoke_link_is_served_with_the_fillet_it_cut`, `test_a_spoke_fillet_is_capped_to_whichever_limit_binds_first`, `test_a_spoke_fillet_at_its_cap_builds_on_extreme_sectors`, `test_cli_and_api_print_the_same_spoke_document` | COVERED |
| REQ-honeycomb-cutout | `test_a_honeycomb_cuts_whole_cells_only_on_an_axis_centred_lattice`, `test_the_honeycomb_link_cuts_eighteen_whole_cells`, `test_a_honeycomb_over_the_cap_is_raised_in_field_steps_to_the_first_size_that_fits`, `test_the_honeycomb_walls_are_measured_on_the_cut_cells`, `test_the_honeycomb_sweep_runs_at_the_cap` | COVERED |
| REQ-one-cutout-pattern | `test_two_cutout_patterns_are_422_naming_both`, `test_two_cutout_patterns_on_one_part_are_refused_naming_both`, `test_three_cutout_patterns_are_refused_naming_all_three` | COVERED |
| REQ-cutout-conflicts-refused-early | `test_a_hole_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly`, `test_a_spoke_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly`, `test_a_honeycomb_rule_refuses_one_step_past_it_and_names_its_fields`, `test_a_hole_conflict_is_422_naming_its_fields`, `test_the_kernel_cuts_one_valid_solid_past_each_cutout_rule` | COVERED |
| REQ-cutout-composes | `test_the_recess_floor_fillet_survives_every_cutout_on_every_bore`, `test_every_selector_takes_only_its_own_edges_with_a_body_cutout`, `test_the_hole_link_cuts_six_holes_through_the_recessed_floor` | COVERED |
| REQ-cutout-derived-numbers | `test_a_cutout_reports_its_thinnest_walls_and_null_without_one`, `test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid`, `test_the_cutout_proof_fails_when_the_cutout_step_is_skipped`, `test_the_cutout_numbers_follow_the_recess_numbers_in_order` | COVERED |

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No Wave 0 stubs were needed: every
plan shipped its tests in the same commits as its behavior (11-03 to 11-06 under TDD).

---

## Manual-Only Verifications

These are human judgments recorded during execution, not phase behaviors lacking a test.
They are listed so `/gsd-verify-work` presents them once rather than treating them as untested.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The spoke-arm `MIN_WALL` rule is what the human wanted (11-01 D4) | REQ-spoke-cutout | A policy decision transcribed from the human's own words at the 11-01 checkpoint — the code implements it (`test_a_spoke_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly`); only the choice itself is a judgment | Read `11-01-SUMMARY.md` "Decisions Made"; confirm "kept" matches intent |
| `HEX_CELL_CAP = 120` and spelling `star` are acceptable as measured under host load 8–9 (11-02 D4) | REQ-honeycomb-cutout | Numbers read off one load-affected run on shared hardware; the identity `calc.HEX_CELL_CAP == RESULTS.md cap` is tested, the acceptability of the margin is not | Read `bench/RESULTS.md` "Honeycomb cell-count spike"; accept or ask for a quiet-host re-run |
| The 33.39 s arithmetic total (spoke `le` 40 row + Phase 10 chamfer row) is deferred to Phase 12's composed measurement (11-06 D5) | REQ-spoke-cutout | Whether one loaded-host reading (load 32) warrants revisiting the `le` now is a judgment; recorded as `must` debt `docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md` | Read the debt item; confirm the Phase 12 trigger is acceptable |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (22/22; the two checkpoint tasks carry a `git diff --quiet` guard)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (none)
- [x] No watch-mode flags
- [x] Feedback latency < 200 s (full gate 178 s on a loaded desktop host)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-09-29 (post-execution audit; every requirement COVERED, 0 gaps, 3 human-judgment items listed above)

---

## Validation Audit 2026-09-29

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
| Manual-only (human judgments, not test gaps) | 3 |

Audited at HEAD `3424078`: `make test` 621 passed in 178.44 s; requirement-to-test map built from the nine SUMMARYs' `coverage:` blocks (`gsd-tools uat classify-coverage`: 11-03/04/05/07/08/09 all auto-covered; 11-01/02/06 each carry one human-judgment deliverable, tabled above). No test files were generated; no auditor was spawned.
