---
phase: "12"
slug: "composition-pass"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: true) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-09-29"
validated: "2026-09-30"
audited_at_head: "fed8baf"
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Audited after execution (State A, 2026-09-30): both requirements have green automated
> coverage at HEAD `fed8baf` (907 passed); no gaps were sent to the Nyquist auditor. The
> live-browser half of REQ-three-interfaces-extended was checked by hand and recorded in
> `12-UAT.md` (4/4 pass).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (Python 3.12.13, `.venv`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`--strict-markers --strict-config`, `xfail_strict`, warnings are errors) |
| **Quick run command** | `make test PYTEST_ARGS="tests/test_calc.py -q"` (any file subset via `PYTEST_ARGS`) |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import contracts, unfinished-work scan, pytest) |
| **Estimated runtime** | ~218 s wall for `make verify` at phase end (907 tests; was 178 s / 621 tests after Phase 11 — `bench/RESULTS.md` "Composition pass test cost (Phase 12, D-10)", run B2) |

---

## Sampling Rate

- **After every task commit:** Run `make test PYTEST_ARGS="<the task's test files> -q"` (each task's `<automated>` block names them)
- **After every plan wave:** Run `make verify` (the pre-commit hook runs it on every commit; 12-09's A/B runs measured 621 → 907 passed at phase end)
- **Before `/gsd-verify-work`:** Full suite must be green — 907 passed in 212.42 s at the verifier's run, and again in the pre-commit hook at `fed8baf`
- **Max feedback latency:** ~220 s (full gate, loaded desktop host — load 9.07 at B2's start); ~20 s for a single-file quick run; the phase's own 286 added items cost a measured 28.28 s (D-10, inside the 30.0 s line)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | REQ-measured-build-time | T-12-01 | ROADMAP edit built as a diff; nothing written before approval | docs | `git diff --quiet -- .planning/ROADMAP.md` | ✅ | ✅ green |
| 12-01-02 | 01 | 1 | REQ-measured-build-time | T-12-02 | Human's SC3/SC5 wording and both evidence-conflict answers recorded verbatim | checkpoint | `git diff --quiet -- .planning/ROADMAP.md` (nothing written before approval) | ✅ | ✅ green |
| 12-01-03 | 01 | 1 | REQ-measured-build-time | T-12-01 | Written only through edit-phase's write step; commit holds exactly ROADMAP + STATE | docs | `sed -n '/^### Phase 12: Composition Pass/,/^## Process Notes/p' .planning/ROADMAP.md \| grep -cF -e '12-CONTEXT.md D-01/D-03/D-06' -e '12-CONTEXT.md D-15'` (== 2) | ✅ | ✅ green |
| 12-02-01 | 02 | 2 | REQ-measured-build-time | T-12-05 | A truncated or ASCII STL is refused, never sized | unit + tracer (bench) | `make test PYTEST_ARGS="tests/test_bench.py -q"` + one-row `bench.build_time` run | ✅ | ✅ green |
| 12-02-02 | 02 | 2 | REQ-measured-build-time | T-12-03 | The 18-row composed sweep is pinned to D-01's design | unit (bench) | `make test PYTEST_ARGS="tests/test_bench.py -q"` + 18-row JSON count | ✅ | ✅ green |
| 12-02-03 | 02 | 2 | REQ-measured-build-time | T-12-04 | Every run appended with its load; no row dropped or re-picked | bench | `sed -n '/^## Composed build and export time (Phase 12)/,$p' bench/RESULTS.md \| grep -cE '^### Run [0-9]+ \(load'` | ✅ | ✅ green |
| 12-03-01 | 03 | 3 | REQ-measured-build-time | T-12-06 | The probe is measured before any source changes | bench | `git diff --quiet c9a169d -- src/spur/params.py src/spur/calc.py src/spur/app.py` + `grep -c '^### Gate probe'` | ✅ | ✅ green |
| 12-03-02 | 03 | 3 | (D-03 gate) | T-12-06 | No source touched before the human decides | checkpoint | `git diff --quiet HEAD -- src/spur/params.py src/spur/calc.py src/spur/app.py bench/build_time.py` | ✅ | ✅ green |
| 12-03-03 | 03 | 3 | REQ-measured-build-time | T-12-06, T-12-07 | `spoke_count le=32` re-run inside 30 s; both debts resolved citing the number | unit (calc/api/bench), regression | `make test PYTEST_ARGS="tests/test_calc.py tests/test_api.py tests/test_bench.py tests/regression -q" && git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json` | ✅ | ✅ green |
| 12-04-01 | 04 | 4 | REQ-measured-build-time | T-12-09 | `--set` must match a sweep label exactly; L19's rule tested at both bars | unit + tracer (bench) | `make test PYTEST_ARGS="tests/test_bench.py -q"` + `make bench.export SWEEP=<one-set> SET="teeth=19"` | ✅ | ✅ green |
| 12-04-02 | 04 | 4 | REQ-measured-build-time | T-12-08 | A gzip level is adopted only on both of L19's bars | unit (api/bench) | `grep -cE '^_GZIP_LEVEL = (1\|6\|9)$' src/spur/app.py` + `make test PYTEST_ARGS="tests/test_api.py tests/test_bench.py -q"` | ✅ | ✅ green |
| 12-05-01 | 05 | 5 | REQ-three-interfaces-extended | T-12-11 | 96 rows pin the exact non-null field set and warnings per combination | unit (calc) | `make test PYTEST_ARGS="tests/test_calc.py -q"` | ✅ | ✅ green |
| 12-05-02 | 05 | 5 | REQ-three-interfaces-extended | T-12-10 | 138 rows pin every refusal's sentence and fields with each other family on | unit (calc), regression | `make test PYTEST_ARGS="tests/test_calc.py tests/regression -q" && git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json` | ✅ | ✅ green |
| 12-06-01 | 06 | 6 | REQ-three-interfaces-extended | T-12-12 | Both feature proofs pass unchanged on the composed solid | integration (kernel) | `make test PYTEST_ARGS="tests/test_model.py -q -k tip_chamfered_gear"` | ✅ | ✅ green |
| 12-06-02 | 06 | 6 | REQ-three-interfaces-extended | T-12-12 | All 15 rows' face/edge/volume/TORUS deltas measured and pinned as literals | integration (kernel) | `make test PYTEST_ARGS="tests/test_model.py -q -k 'tip_chamfered_gear or single_sided_recess'" && git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json` | ✅ | ✅ green |
| 12-07-01 | 07 | 7 | REQ-three-interfaces-extended | T-12-13 | README's composed example runs; `spur info` prints every family's number, no warning | integration (cli) | `make test PYTEST_ARGS="tests/test_cli.py -q"` + the composed `spur info` assert | ✅ | ✅ green |
| 12-07-02 | 07 | 7 | REQ-three-interfaces-extended | T-12-13, T-12-14 | Every field reaches schema, form and CLI in one order; URL round trip is generic | integration (cli/api) | `make test PYTEST_ARGS="tests/test_cli.py tests/test_api.py -q"` | ✅ | ✅ green |
| 12-07-03 | 07 | 7 | REQ-three-interfaces-extended | T-12-13 | 23 refusals read the same on the API's 422 and the CLI's exit 2 | integration (cli/api), regression | `make test PYTEST_ARGS="tests/test_cli.py tests/regression -q" && git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json` | ✅ | ✅ green |
| 12-08-01 | 08 | 8 | REQ-three-interfaces-extended | T-12-15 | The real process's exit status asserted; `cli.md` states 2 / 1 / 1 | integration (cli) | `make test PYTEST_ARGS="tests/test_cli.py -q"` + `spur export -o gear.obj; test $? -eq 1` | ✅ | ✅ green |
| 12-08-02 | 08 | 8 | REQ-three-interfaces-extended | — | `app.js` untouched; the UI verdict recorded in the three ideas | docs | `git diff --quiet c9a169d -- src/spur/static/app.js` + `grep -l '^## Judged at Phase 12' ... \| wc -l` (== 2) | ✅ | ✅ green |
| 12-09-01 | 09 | 9 | REQ-measured-build-time | T-12-16, T-12-18 | Same-host alternating A/B runs; the import path proven before timing | full gate (bench), regression | `sed -n '/^## Composition pass test cost (Phase 12, D-10)/,$p' bench/RESULTS.md \| grep -cE '^\| [AB][12] \|'` (== 4) + `make test PYTEST_ARGS="tests/regression -q"` | ✅ | ✅ green |
| 12-09-02 | 09 | 9 | (D-10 gate) | T-12-16 | Nothing trimmed before the human decides | checkpoint | `git diff --quiet HEAD -- tests/test_model.py` | ✅ | ✅ green |
| 12-09-03 | 09 | 9 | REQ-measured-build-time, REQ-three-interfaces-extended | T-12-17 | L31 appended, never edited (0 deleted lines); every number cites a RESULTS section | docs + regression | `grep -c '^## L31 — ' docs/architecture/decision_log.md` (== 1) + numstat deletions == 0 + `make test PYTEST_ARGS="tests/test_model.py tests/regression -q"` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Requirement → test evidence (all green at `fed8baf`; names read like the requirement):

| Requirement | Evidence (test names, `tests/`) | Status |
|-------------|--------------------------------|--------|
| REQ-measured-build-time | `test_a_binary_stl_is_sized_by_its_length_and_the_triangle_count_its_header_names`, `test_an_stl_whose_length_disagrees_with_its_header_is_refused`, `test_the_report_names_the_largest_fine_stl_and_breaks_a_tie_by_file_order`, `test_the_composed_sweep_stacks_each_cutout_on_its_heaviest_bore_beside_six_baselines`, `test_the_spoke_count_is_an_integer_from_0_to_32`, `test_l19s_rule_applied_to_its_own_table_keeps_level_1`, `test_a_higher_gzip_level_is_adopted_exactly_on_both_of_l19s_bars`, `test_level_9_is_compared_against_the_level_currently_adopted`, `test_peak_rss_reads_bytes_on_macos_and_kibibytes_on_linux`; the measurements themselves are records in `bench/RESULTS.md` ("Composed build and export time", "Export cost on the heaviest v0.2 topology", "Composition pass test cost"), each pinned by a plan `<automated>` grep | COVERED |
| REQ-three-interfaces-extended | `test_every_bore_cutout_recess_and_tip_combination_derives_its_own_numbers` (96 rows), `test_every_refusal_reads_the_same_with_each_other_family_switched_on` (138), `test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore` (12), `test_the_recess_fillet_and_cutout_proofs_hold_with_a_single_sided_recess` (3), `test_readme_export_examples_run`, `test_cli_and_api_print_the_same_composed_document`, `test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order`, `test_the_shareable_link_round_trips_every_field_through_generic_code`, `test_every_refusal_reads_the_same_on_the_api_and_the_cli` (23), `test_an_unknown_output_extension_exits_1_from_the_real_process`; the rendered-browser half is `12-UAT.md` tests 1–4 (pass, 2026-09-30) | COVERED |

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No Wave 0 stubs were needed: every
plan shipped its tests in the same commits as its behavior (12-02, 12-03 and 12-04 under
TDD; 12-05 to 12-08 as tracer-then-matrix).

---

## Manual-Only Verifications

These are human judgments recorded during execution, not phase behaviors lacking a test.
They are listed so `/gsd-verify-work` presents them once rather than treating them as untested.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SC3/SC5 wording and the two evidence-conflict answers (12-01 Task 2) | REQ-measured-build-time | The success-criteria text is the human's own wording, transcribed at the checkpoint; the greps prove it landed, not that it is what was meant | Read `12-01-SUMMARY.md` "Decisions Made"; confirm the ROADMAP Phase 12 SC3/SC5 text matches intent |
| Two non-decisive loaded runs were a sufficient basis to proceed to 12-03's checkpoint (12-02 D3) | REQ-measured-build-time | Measurement sufficiency is a judgment the record documents but does not decide | Read `bench/RESULTS.md` "Composed build and export time (Phase 12)" Runs 1–2; confirm the D-02 handling |
| The gate's outcome — runner fix, two quiet re-runs, Run 4 accepted as decisive, then `lower-le: spoke_count 32` (12-03 Task 2) | REQ-measured-build-time | A limit change is a policy choice; `test_the_spoke_count_is_an_integer_from_0_to_32` and the 18-row re-run prove the code, not the choice | Read the "### Gate probe" and "### Gate decision" subsections; confirm `le=32` (29.42 s heaviest) is the accepted margin |
| The rendered form, composed link, copy-link round trip and live 422 (12-07 D6) | REQ-three-interfaces-extended | Runtime DOM/WebGL behavior the static `app.js` read and the API/CLI parity tests cannot observe | Done: `12-UAT.md` tests 1–4, all pass on 2026-09-30 against a fresh `make serve` |
| D-10's gate on the measured 28.28 s delta: "accept" (12-09 Task 2) | REQ-measured-build-time | A gate decision is the human's own call; the verbatim record is the audit trail | Read `bench/RESULTS.md` "Composition pass test cost (Phase 12, D-10)" "### Gate decision"; confirm the 1.72 s margin is acceptable |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (23/23; the three checkpoint tasks carry a `git diff --quiet` guard)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (none)
- [x] No watch-mode flags
- [x] Feedback latency < 220 s (full gate 217.83 s on a loaded desktop host; the phase's own delta 28.28 s against D-10's 30.0 s line)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-09-30 (post-execution audit; both requirements COVERED, 0 gaps, 5 human-judgment items listed above)

---

## Validation Audit 2026-09-30

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
