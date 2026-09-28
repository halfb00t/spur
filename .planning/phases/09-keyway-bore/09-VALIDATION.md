---
phase: "9"
slug: "keyway-bore"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-09-27"
validated: "2026-09-28"
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by plan-phase from `09-RESEARCH.md` § Validation Architecture; the per-task map was
> filled by validate-phase on 2026-09-28 against HEAD `8c09e12` (PR #10), after execution,
> code review (Claude + Codex lanes), security review, UAT 28/28 and two re-verifications.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing project pin, `pyproject.toml` `[tool.pytest.ini_options]`, `--strict-markers --strict-config`) |
| **Config file** | `pyproject.toml` (unchanged) |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_calc.py tests/test_model.py -k keyway -q` — 41 passed in 12.81 s (2026-09-28) |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import-boundary contracts, unfinished-work scan, pytest — CLAUDE.md's one gate; also the pre-commit hook) |
| **Estimated runtime** | 77.71 s and 85.04 s warm for `make verify` at 397 → 407 tests (measured 2026-09-28, two verifier runs); the seed's ~48 s was Phase 8's count. Cold first run is page cache, not the tests |

---

## Sampling Rate

- **After every task commit:** Run `.venv/bin/python -m pytest tests/test_calc.py tests/test_model.py -k keyway -q` and `git diff --exit-code tests/regression/pre_v0_2.json` (L26: the fixture never moves in a feature commit)
- **After every plan wave:** Run `make verify`
- **Before `/gsd-verify-work`:** `make verify` green and `make bench.build SWEEP=bench/sweeps/keyway_bore.json` recorded in `bench/RESULTS.md`, every row inside `SPUR_BUILD_TIMEOUT=30s`
- **Max feedback latency:** ~85 s (one warm `make verify`, which the pre-commit hook runs on every commit — every one of this branch's 38 commits carried it)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 09-01-01 | 01 | 1 | REQ-keyway-bore, REQ-keyway-wall-refused | T-09-01 / T-09-02 | Requirement text carries the as-cut-wall datum and the yielding recess; superseded phrases gone | doc-grep | `grep -cF '(bore_d + bore_clearance)/2' .planning/REQUIREMENTS.md` (≥1); superseded-phrase grep = 0 | ✅ | ✅ green |
| 09-01-02 | 01 | 1 | REQ-keyway-bore, REQ-keyway-wall-refused | T-09-02 | Nothing written to ROADMAP.md before the human approves the wording | manual (checkpoint:human-verify) | `git diff --quiet -- .planning/ROADMAP.md` at the checkpoint | ✅ | ✅ green (approved verbatim, 09-01-SUMMARY) |
| 09-01-03 | 01 | 1 | REQ-keyway-bore, REQ-keyway-wall-refused, REQ-hex-rim-chamfer | T-09-01 / T-09-02 | ROADMAP Phase 9 written only through edit-phase's write step; one Roadmap Evolution line in STATE.md; commit touches exactly three files | doc-grep | scoped `sed`/`grep -cF` on the Phase 9 section = 3 and superseded phrases = 0; `git show --name-only` = 3 files (`69948df`) | ✅ | ✅ green |
| 09-02-01 | 02 | 1 | REQ-keyway-bore, REQ-keyway-composes-with-d-flat, REQ-bore-derived-numbers | T-09-03 / T-09-04 | Slot and printed numbers read one datum (`bore_radius`, `keyway_width_effective`); every pre-v0.2 record replays byte-unchanged | integration | `tests/test_api.py::test_a_keyed_link_is_served_with_its_two_numbers`; `tests/regression/test_pre_v0_2.py` (86 passed); `spur info --keyway-width 3 --keyway-depth 1.4` → 10.55 / 3.15 / 9.15 / 13.158 / no warnings | ✅ | ✅ green |
| 09-02-02 | 02 | 1 | REQ-keyway-bore, REQ-hex-rim-chamfer, REQ-keyway-wall-refused (recess half) | T-09-03 / T-09-05 | Floor at `bore_radius + keyway_depth` on the built solid within `TOL`; rim selector takes exactly the pre-keyway edges; chamfer survives the slot, slot edges sharp; recess keeps `MIN_WALL` from the corner | integration (CAD) | `tests/test_model.py::test_a_keyway_floor_sits_keyway_depth_outside_the_as_cut_bore_wall`, `::test_the_bore_chamfer_survives_the_keyway_and_the_slot_edges_stay_sharp`, `::test_the_rim_chamfer_on_a_keyed_bore_takes_the_pre_keyway_edges`, `::test_each_edge_selector_picks_exactly_its_own_edges` (28 rows, 11 keyway), `::test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth`; `tests/test_calc.py::test_the_recess_yields_to_a_keyway_and_says_so_only_when_it_narrows_or_drops` | ✅ | ✅ green |
| 09-03-01 | 03 | 2 | REQ-keyway-bore, REQ-keyway-composes-with-d-flat, REQ-keyway-wall-refused | T-09-08 / T-09-09 / T-09-11 | Six refusals decided in `calc.check()` before any kernel work, never capped, sentences interpolate only formatted floats and literal field names; API, CLI and `spur info` agree | unit + integration | `tests/test_calc.py::test_a_keyway_needs_a_round_bore_and_both_of_its_fields`, `::test_a_keyway_on_a_hex_bore_with_only_one_field_set_names_both_sentences_hex_first`, `::test_a_keyway_as_wide_as_the_bore_is_refused_and_one_step_narrower_is_accepted`, `::test_a_keyway_that_leaves_less_than_min_wall_to_the_d_flat_is_refused_naming_both`, `::test_a_keyway_whose_floor_corner_nears_the_root_is_refused_naming_both`; `tests/test_api.py::test_a_keyway_conflict_is_422_naming_its_fields`, `::test_the_largest_keyway_each_rule_allows_is_served`; `tests/test_cli.py::test_a_keyway_the_root_cannot_hold_exits_2_and_names_it`, `::test_cli_and_api_print_the_same_keyed_document`; `tests/test_model.py::test_the_largest_keyway_each_rule_allows_builds`, `::test_the_kernel_cuts_one_valid_solid_past_each_keyway_rule` | ✅ | ✅ green |
| 09-03-02 | 03 | 2 | REQ-hex-rim-chamfer (round/D-flat chamfer reach, D-12) | T-09-10 | Refusal sits at the kernel's measured contact (`ROOT_CONTACT` 1e-9 mm), refusing no link the pinned kernel built before (L05); rules never stack; thin-wall warning inside `(0, MIN_WALL)` (WR-01) | unit + integration (CAD) | `tests/test_calc.py::test_a_round_bore_chamfer_that_touches_the_root_is_refused_naming_both`, `::test_the_round_bore_rules_never_stack`, `::test_a_bore_chamfer_under_min_wall_from_the_root_warns_with_the_measured_gap` (10 cases, `882dd76`); `tests/test_model.py::test_the_largest_round_bore_the_chamfer_rule_allows_builds`, `::test_the_kernel_fails_where_a_round_bore_chamfer_touches_the_root`, `::test_the_kernel_can_fail_inside_the_root_contact_residual_band` (WR-02); debt file moved to `docs/tech_debt/resolved/` | ✅ | ✅ green |
| 09-04-01 | 04 | 2 | REQ-keyway-bore, REQ-measured-build-time | T-09-13 | The sweep is the full 32-row cross product with the largest keyway each rule allows, so no slow row can be dropped by re-picking | unit + bench | `tests/test_bench.py::test_the_keyway_bore_sweep_is_every_combination_with_the_largest_keyway_each_rule_allows`; `make bench.build SWEEP=<one-row file>` emits its timed row | ✅ | ✅ green |
| 09-04-02 | 04 | 2 | REQ-measured-build-time | T-09-12 | All 32 rows recorded, none over `SPUR_BUILD_TIMEOUT=30s` (heaviest 4.85 s), host state and load caveat stated | bench + doc-grep | `sed -n '/^## Keyway bore build and export time (Phase 9)/,$p' bench/RESULTS.md \| grep -cE '^\| teeth=200 '` = 32; `**NO**` rows = 0 | ✅ | ✅ green |
| 09-05-01 | 05 | 3 | REQ-keyway-bore, REQ-keyway-composes-with-d-flat, REQ-bore-derived-numbers | T-09-14 | README states the datum and the two printed numbers; the keyed example runs as a test; no standard-table size given as sizing guidance | integration + doc-grep + human read | `tests/test_cli.py::test_readme_export_examples_run`; `grep -cE '^\| \`keyway_(width\|depth)\` \| 0 \|' README.md` = 2; UAT test 6 (human, passed 2026-09-28) | ✅ | ✅ green |
| 09-05-02 | 05 | 3 | all five | T-09-15 | L28 appended with 0 deleted lines; architecture docs name `keyway_corner_radius`, `ROOT_CONTACT`, `_cut_keyway`; the whole gate green | doc-grep + full gate | `grep -c '^## L28 — ' docs/architecture/decision_log.md` = 1; `git diff --numstat b522044 -- docs/architecture/decision_log.md` 0 deletions; `make verify` (407 passed in 85.04 s at `882dd76`) | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Threat refs are `09-SECURITY.md`'s register (T-09-01..T-09-15 + T-09-SC, all `closed`,
`threats_open: 0`). The requirement → test map the plans had to cover is `09-RESEARCH.md`
§ "Phase Requirements → Test Map"; every entry above was re-collected at HEAD on 2026-09-28
(`pytest --collect-only`) and re-run: 41 passed (`-k keyway`, calc + model), 14 passed (bench,
cli, api keyway subset), 86 passed (regression), `make verify` 407 passed via the pre-commit
hook on `8c09e12`.*

---

## Wave 0 Requirements

- [x] `tests/test_calc.py` — parametrized 422 cases for D-02, D-03, D-10, D-11, D-12 and D-13's two sentences: the five `test_a_keyway_*_refused*` / `*_needs_a_round_bore*` / `*_hex_first` tests and `test_a_round_bore_chamfer_that_touches_the_root_is_refused_naming_both` (REQ-keyway-bore, REQ-keyway-composes-with-d-flat, REQ-keyway-wall-refused)
- [x] `tests/test_model.py` — the built-solid datum test (D-14: `test_a_keyway_floor_sits_keyway_depth_outside_the_as_cut_bore_wall`, D-flat and round), the chamfer-survives-the-slot test (D-07: `test_the_bore_chamfer_survives_the_keyway_and_the_slot_edges_stay_sharp`), the D-flat + keyway coexistence build (D-04: the `[d-flat]` row of the datum test), the recess-yields test (D-09: `test_calc.py::test_the_recess_yields_to_a_keyway_and_says_so_only_when_it_narrows_or_drops`); new rows in `test_each_edge_selector_picks_exactly_its_own_edges` (28 collected, 11 keyway) and `test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth`
- [x] `bench/sweeps/keyway_bore.json` — the 32-row sweep file `make bench.build SWEEP=` reads, pinned by `test_bench.py` (REQ-measured-build-time)
- [x] No framework install: pytest was already installed and configured

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| ROADMAP SC1/SC3/SC4 and REQUIREMENTS.md amendments (D-20) | REQ-keyway-bore, REQ-keyway-wall-refused | One human confirmation of wording before the write, through the edit-phase tooling (08-01's pattern) | `git show 69948df -- .planning/ROADMAP.md .planning/REQUIREMENTS.md`; confirm the as-cut wall formula `(bore_d + bore_clearance)/2`, the dropped "or a recess wall" clause, and SC4's amended proof sentence. Done: approved verbatim at the 09-01 Task 2 checkpoint |
| A sweep row over `SPUR_BUILD_TIMEOUT=30s` | REQ-measured-build-time | Halts for a human decision, never a silent narrowing (08 D-11) | Read the `make bench.build` Markdown rows; any `**NO**` row stops the phase. Done: 32/32 rows inside, heaviest 4.85 s — the gate never fired |
| No DIN 6885 / ANSI B17.1 keyway size given as sizing guidance in README.md or L28 (D-16, L08) | REQ-keyway-bore | grep proves the convention names appear with no numeric example beside them; whether a sentence *reads* as a sizing recommendation needs a human read (09-05 D7, `verification: judgment`) | Read README rows 158–159, the Geometry-notes keyway bullet, and L28 (incl. "the DIN-6885-correct 3 × 1.4 mm key" in the recess paragraph). Done: UAT test 6 passed 2026-09-28 (`09-UAT.md`) |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (11/11; 09-01-02 is a human checkpoint by design and its gate is the `git diff --quiet` guard)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (every task has one)
- [x] Wave 0 covers all MISSING references (0 missing at HEAD)
- [x] No watch-mode flags
- [x] Feedback latency < 60s — **not met literally**: `make verify` is 78–85 s warm at 407 tests (the ~48 s seed figure was Phase 8's suite); the quick command is 12.81 s. Accepted as-is: the gate's cost is the CAD tests, and Phase 7's D-06 already accepted the fixture's share of it
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-09-28 by `/gsd-validate-phase 9` (Claude) against HEAD `8c09e12` — 0 gaps, 0 escalations, no tests generated (every requirement already had a green named test from execution; the one post-review gap, WR-01's untested warning, was closed by the Codex cross-review loop in `882dd76` before this audit ran).

## Validation Audit 2026-09-28

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
