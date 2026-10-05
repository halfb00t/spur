---
phase: "08"
slug: "hex-bore"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-05"
reconstructed: true
---

# Phase 08 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Reconstructed on 2026-10-05 by `/gsd-validate-phase 8` (State B: the phase shipped
> without a VALIDATION.md). Every status below was re-measured on the working tree at
> that date, not copied from the SUMMARYs or from 08-VERIFICATION.md.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (pytest-xdist, pytest-cov) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`--strict-markers --strict-config`, `xfail_strict`, warnings are errors) |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_calc.py tests/test_api.py tests/test_cli.py tests/test_model.py tests/test_bench.py -k hex -q -p no:cacheprovider --no-cov && .venv/bin/python -m pytest tests/regression -q -p no:cacheprovider --no-cov && git diff --exit-code tests/regression/pre_v0_2.json` |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import-linter, no-fake-done scan, pytest) |
| **Estimated runtime** | quick: ~23 s for the 110 hex-scoped cases (`110 passed, 619 deselected in 23.12s`, 2026-10-05) plus the regression replay; full: ~67 s wall (`929 passed in 66.87s`, 8 workers, 2026-10-05) |

---

## Sampling Rate

- **After every task commit:** Run the quick run command above
- **After every plan wave:** Run `make verify`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~67 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | REQ-hex-bore | T-08-01 / T-08-02 | REQ-hex-bore carries D-01 (hex replaces the round profile, ignored fields warned, never a 422); the hex × keyway 422 moved to REQ-keyway-bore, not dropped | doc | `grep -c 'Phase 8 D-01' .planning/milestones/v0.2-REQUIREMENTS.md` → 2; `sed -n '/^### Bore profiles/,/^### Body cutouts/p' .planning/milestones/v0.2-REQUIREMENTS.md \| grep -c 'or a keyway is a 422'` → 0 | ✅ | ✅ green |
| 08-01-02 | 01 | 1 | REQ-hex-bore | T-08-02 | ROADMAP.md is written only after the human approved the diff (blocking checkpoint) | checkpoint | `git diff --quiet -- .planning/ROADMAP.md` at the checkpoint; the approval is recorded in `08-01-SUMMARY.md` key-decisions ("approved all four proposed texts verbatim") | ✅ | ✅ green (gate passed 2026-09-26) |
| 08-01-03 | 01 | 1 | REQ-hex-bore | T-08-01 / T-08-02 | Phase 8 SC2 cites D-01/D-02, the superseded criterion is gone, one Roadmap Evolution line per edited phase | doc | `sed -n '/^### Phase 8: Hex Bore/,/^### Phase 9/p' .planning/milestones/v0.2-ROADMAP.md \| grep -c '08-CONTEXT.md D-01/D-02'` → 1; same range `grep -c 'or a keyway field is a 422'` → 0; `grep -cE '^- Phase (8\|9\|12) edited' .planning/STATE.md` → 5 (≥ 3) | ✅ | ✅ green |
| 08-02-01 | 02 | 2 | REQ-hex-bore, REQ-derived-dimensions-additive | T-08-03 / T-08-04 | `derive()` and the cut compute from the same `hex_across_flats(p)`; the pre-v0.2 replay compares every recorded field exactly and requires the two new fields null | integration + regression | `.venv/bin/python -m pytest tests/test_api.py::test_a_hex_bore_link_is_served_with_its_two_numbers tests/test_calc.py::test_the_bore_rim_limit_is_a_hex_bores_circumradius tests/test_calc.py::test_a_hex_bore_reports_across_flats_and_corners_and_no_round_diameter tests/test_cli.py::test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order tests/test_cli.py::test_cli_and_api_print_the_same_hex_bore_document tests/regression -q && git diff --exit-code tests/regression/pre_v0_2.json` | ✅ | ✅ green |
| 08-02-02 | 02 | 2 | REQ-hex-bore | T-08-05 / T-08-06 | `recess_radii()` clears `bore_mouth_limit(p)` + MIN_WALL at the hex corner; exactly 12 LINE rim edges on every hex row; the same link builds the same solid twice | unit (kernel) | `.venv/bin/python -m pytest tests/test_model.py -k hex -q` — `test_each_edge_selector_picks_exactly_its_own_edges[hex-*]` (7 rows), `test_a_hex_bore_measures_the_across_flats_and_corners_it_reports`, `test_the_same_hex_link_builds_the_same_solid_twice`, `test_the_pre_hex_rim_bound_would_have_chamfered_nothing_on_a_hex_wider_than_the_round_bore`, `test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth[hex]` | ✅ | ✅ green |
| 08-03-01 | 03 | 3 | REQ-hex-bore | T-08-08 / T-08-09 / T-08-10 / T-08-11 | Both root rules refuse in `calc.check()` before any CAD, one step past refused and one step inside builds; no capping path (a conflict is a 422 naming both fields, L03); messages interpolate only floats and fixed field names; API, CLI and `derive()` print the one sentence | unit + integration | `.venv/bin/python -m pytest tests/test_calc.py tests/test_api.py tests/test_cli.py tests/test_model.py -k hex -q` — calc: `test_a_hex_bore_skips_the_round_bore_rules`, `test_a_hex_bore_is_refused_when_its_corners_reach_the_root_and_builds_one_step_inside`, `test_a_hex_bore_chamfer_that_carries_the_corners_to_the_root_is_refused_naming_both`, `test_a_hex_bore_warns_about_each_round_field_it_ignores`; api: `test_a_hex_bore_the_root_cannot_hold_is_422_naming_bore_hex`, `test_a_hex_bore_chamfer_reaching_the_root_is_422_naming_both_fields`, `test_a_hex_link_with_a_d_flat_builds_and_says_both_round_fields_are_ignored`; cli: `test_a_hex_bore_the_root_cannot_hold_exits_2_and_names_it`; model: `test_the_largest_hex_each_root_rule_allows_builds`, `test_the_kernel_chamfers_a_hex_bore_far_past_its_side_length` | ✅ | ✅ green |
| 08-03-02 | 03 | 3 | REQ-hex-bore | T-08-07 | Help text and README are static strings; the README's hex example runs and prints exactly one ignored-field warning | integration + doc | `.venv/bin/python -m pytest tests/test_cli.py::test_readme_export_examples_run -q && .venv/bin/spur export -o "$(mktemp -d)/hexgear.stl" --bore-hex 6 2>&1 \| grep -c 'warning: Hex bore replaces the round profile'` → 1 | ✅ | ✅ green |
| 08-04-01 | 04 | 4 | REQ-hex-bore, REQ-derived-dimensions-additive | T-08-13 / T-08-14 | The sweep file is D-11's full cross product and cannot be narrowed silently; an empty sweep is refused, not reported; the budget predicate is pinned from both sides; `subprocess.run` with a fixed argument list | unit + bench | `.venv/bin/python -m pytest tests/test_bench.py -q` — `test_the_hex_bore_sweep_is_every_combination_d_11_names`, `test_a_set_is_inside_the_timeout_until_its_build_plus_slower_export_passes_it`, `test_an_empty_sweep_is_refused_rather_than_reported`, `test_the_report_names_the_largest_fine_stl_and_breaks_a_tie_by_file_order`; end to end: `F=$(mktemp) && printf '[{"bore_hex": 6}]' > "$F" && make bench.build SWEEP="$F"` → one `\| bore_hex=6 \|` row | ✅ | ✅ green |
| 08-04-02 | 04 | 4 | REQ-hex-bore | T-08-12 | Every one of the 16 rows is recorded; a row over `SPUR_BUILD_TIMEOUT` halts for a human instead of being dropped | bench record (doc) | `awk '/^## Hex bore build and export time \(Phase 8, D-11\)/{f=1;next} f&&/^## /{exit} f' bench/RESULTS.md \| grep -cE '^\| teeth=200 '` → 16; same range `grep -cE '\*\*NO\*\*'` → 0 | ✅ | ✅ green |
| 08-04-03 | 04 | 4 | REQ-hex-bore | T-08-15 | L27 appended, never edited; the round-bore chamfer-reach gap filed as `must` debt with its INDEX row, not fixed silently | doc + gate | `grep -c '^## L27 — ' docs/architecture/decision_log.md` → 1 `&& make verify` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Measured 2026-10-05 on the working tree (branch `gsd/phase-16-typing-validation-debt`,
HEAD `655583f`):

- Hex-scoped subset across the five test files: `110 passed, 619 deselected in 23.12s`.
- `pytest --collect-only tests/test_model.py | grep -c '…its_own_edges[hex-'` → 7.
- Full suite: `929 passed in 66.87s`, coverage 97.24 % (floor 96 %), exit 0.
- `git diff --exit-code tests/regression/pre_v0_2.json` exits 0; the fixture's only commit
  is still `540f1a0`.
- CLI, live: `spur info --bore-hex 6` → `hex_across_flats 6.15`, `hex_across_corners 7.101`,
  `bore_effective null`, one warning naming `bore_d (9 mm)` and `bore_flat (8 mm)`;
  `spur info --bore-hex 25` → exit 2, "Hex bore is too large for the root diameter";
  `spur info --bore-hex 23.4` → "Bore chamfer is too large for this hex bore";
  `spur export … --bore-hex 6` → exactly one `warning: Hex bore replaces the round profile` line.
- One-set `make bench.build`: `| bore_hex=6 | 0.33 | 0.07 | 0.03 | 0.40 | yes | 2265184 | 45302 |`,
  `**Heaviest:** bore_hex=6 -- 0.40 s of 30 s.`, exit 0.

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

All phase behaviors have automated verification.

Task 08-01-02 is a human-approval checkpoint (a process gate, not a behavior): its
`<automated>` verify only proves the roadmap was not written before the answer. The
approval itself is recorded in `08-01-SUMMARY.md` and is not re-runnable.

---

## Reconstruction Notes

Drift between phase close (2026-09-26) and this audit (2026-10-05), none of which
weakens the phase's coverage:

- Plan 08-01's doc checks target `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md`.
  Closing v0.2 archived those files to `.planning/milestones/v0.2-REQUIREMENTS.md` and
  `v0.2-ROADMAP.md`; the current `.planning/REQUIREMENTS.md` (v0.3) cites `Phase 8 D-01`
  zero times, as expected. The commands above run against the archived files.
- Plan 08-04 Task 2's verify (`sed -n '/^## Hex bore…/,$p' bench/RESULTS.md`) now overruns
  into the Phase 9-12 sections appended below it (208 `teeth=200` rows, 20 `**NO**` rows in
  those later sections). Bounded to this phase's section the counts are the planned 16 and 0;
  the map above records the bounded form.
- 08-02's must-have "`bore_hex` declared right after `bore_flat`" is superseded: Phase 9
  inserted `keyway_width` and `keyway_depth` between them (`src/spur/params.py:65-78`), and
  `test_a_hex_bore_link_is_served_with_its_two_numbers` now asserts
  `names.index("bore_hex") == names.index("keyway_depth") + 1`. Group, unit, bound and
  default are unchanged.
- The `must` debt 08-04 filed (`2026-09-26-round-bore-chamfer-reach-is-not-checked.md`) is
  resolved in `4b6a5b9` (09-03) and lives in `docs/tech_debt/resolved/`.
- `test_each_edge_selector_picks_exactly_its_own_edges` grew to 30 rows (keyway and tip
  chamfer joined the matrix); the 7 hex rows are intact.
- Suite size went from 330 to 929 tests.

---

## Validation Audit 2026-10-05

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 67s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-10-05 (`/gsd-validate-phase 8`, State B reconstruction; every status re-measured)
