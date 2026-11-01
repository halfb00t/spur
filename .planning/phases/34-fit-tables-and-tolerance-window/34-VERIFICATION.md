---
phase: 34-fit-tables-and-tolerance-window
verified: 2026-11-01T10:40:00Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-01-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-01-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-02-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-02-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-03-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-03-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-04-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-04-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-05-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-05-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-06-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-06-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-07-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-07-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-08-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-08-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-09-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-09-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-10-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-10-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-11-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-11-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-12-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-12-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-13-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-13-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-14-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-14-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-15-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-15-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-16-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-16-SUMMARY.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-17-PLAN.md"
  - ".planning/phases/34-fit-tables-and-tolerance-window/34-17-SUMMARY.md"
  - "Makefile"
  - "bench/RESULTS.md"
  - "docs/architecture/decision_log.md"
  - "scripts/din5480_read1.py"
  - "scripts/din5480_tables_tool.py"
  - "src/spur/app.py"
  - "src/spur/cli.py"
  - "src/spur/din5480.py"
  - "src/spur/din5480_tables.py"
  - "src/spur/pool.py"
  - "src/spur/shaft_calc.py"
  - "src/spur/shaft_model.py"
  - "src/spur/shaft_params.py"
  - "tests/din5480_real_tables_check.py"
  - "tests/din5480_tables_fixture.py"
  - "tests/test_browser.py"
  - "tests/test_cli.py"
  - "tests/test_din5480_anchors.py"
  - "tests/test_din5480_tables.py"
  - "tests/test_pool.py"
  - "tests/test_shaft_calc.py"
  - "tests/test_shaft_model.py"
  - "tests/test_shaft_parity.py"
covered_digest: "v3:sha256:04f966b1662571d21cd8b3e9b9b1c0aced79a5cf387448546492c1383211613f"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 4/5
  gaps_closed:
    - "Truth 5: the human accepted 213.54 s (real 214.53 s) as the milestone-close reading (bench/RESULTS.md, 325fd37; 34-UAT.md test 1)"
    - "Review findings WR-01..WR-04 fixed (9215f60, d3f339b, d299fe3, e98638b) and IN-01..IN-07 filed as debt (504d5c5); 34-REVIEW-DISPOSITION.md carries every disposition"
    - "Leak review: the disclosed fixture coincidence removed (282f264); 34-UAT.md test 3"
  gaps_remaining: []
  regressions: []
---

# Phase 34: Fit Tables and Tolerance Window Verification Report

**Phase Goal:** With the human's DIN 5480 (2006 series) values transcribed into a private, gitignored file, the user sees the tooth-thickness windows and the measurement-over-pins limits at the chosen fit, and the solid carries the effective maximum-material thickness; without the file, or for a size the tables do not list, the part still builds from the formulas and every table-dependent number is `null` with a warning that says why. The milestone releases as one unit when this phase closes.
**Verified:** 2026-11-01 (HEAD a11e827)
**Status:** passed
**Re-verification:** Yes, after the code-review fixes and the human's rulings (previous: human_needed, 4/5)

No table value appears in this report. It cites counts, designations and test names only. `private/` was not opened and the real-file check was not run here; its result is cited from the 34-16 log. The full `make verify` was not re-run here; the orchestrator's run after the fixes is cited (`2940 passed in 235.27s`, rc 0, 504d5c5).

## Goal Achievement

### Observable Truths

| # | Truth (ROADMAP success criterion) | Status | Evidence |
|---|---|---|---|
| 1 | Tables are private and their absence is honest: loads from a gitignored file named by env, null plus a warning without it, part still builds, repo holds no value beyond approved anchors | VERIFIED | `din5480_tables.py`: `ENV_VAR = "SPUR_DIN5480_TABLES"`, `active()` returns `None` when unset. Run with the variable unset: all five new rows `None`, warning `NO_TABLE_FILE` present, `SOLID_AT_NOMINAL_THICKNESS` present, the shaft derives. `git ls-files -- private` returns 0 files; `git check-ignore -q private/din5480-tables.json` exits 0; `.dockerignore` carries `private`. A set but missing path refuses with exit 1 (`error: SPUR_DIN5480_TABLES=/nonexistent.json: does not exist`). `test_no_tracked_json_file_is_a_table_file` and `test_the_private_directory_is_ignored_by_git_and_by_docker` pass. Note: the warning names the variable, not a path, by design (T-34-15, D-04); the 34-VALIDATION row says the same. Leak review: resolved by the human (UAT test 3); 282f264 moved the invented default-shaft limit pair off the real file's value, and the in-process comparison printed 0 coincidences over 144 fit/class combinations. |
| 2 | Transcription is checked: two independent reads diffed to zero, provenance on every row, loader invariants (`T_G = T_act + T_eff`, unit range, no Unicode minus), seen red once | VERIFIED | `34-14-assemble.log`: pair 1 (Part 2 read 1 vs read 2) `0 differences`, pair 2 (Table 7 read A vs B) `0 differences`, assembled only then; load line `720 16 18 8 30 21`, the figure the human authorised. Provenance model (`part`, `clause`, `table`, `pages`) is on every row type and `problems()` refuses a provenance not equal to the layout's. Invariants present in `problems()`: T_G sum, `UM_LIMIT`, `_BAD_MINUS`, M1 identity, duplicates, column counts. 33 seen-red rows in `bench/RESULTS.md`, 34-02 rows with logs `34-02-red-invariants.log` and `34-02-red-guards.log`. The two weaknesses the first report named are fixed: WR-03 in d299fe3 (`problems()` now refuses a negative `T_act` or `T_eff`; two new refusal rows in `BROKEN`, run here) and WR-04 in e98638b (`assemble` refuses one path given twice for either pair; `test_assemble_refuses_one_read_given_twice` for both options, run here). |
| 3 | Windows and M_Re limits at the fit, proved against the oracle on anchor rows; fit outside tables is a warning and null; off-table size builds from formulas with every table number null and warned; numbers reach web, API and CLI through the row list and the parity test covers them | VERIFIED | `derive_shaft` computes the three-tier logic: no file, size not listed (`size_not_tabulated_warning`), fit not in Table 7 (`fit_not_in_table_7_warning`), each with null rows. `thickness_limits` is Table 6 over Table 7. `limit_measurement` runs each limit through the contact window alone. The five keys are in `ShaftParams` rows (`max_effective_thickness`, `max_actual_thickness`, `min_actual_thickness`, `measure_over_pins_max`, `measure_over_pins_min`). Ran here: `tests/test_din5480_tables.py`, `test_din5480_anchors.py`, `test_shaft_calc.py`, `test_din5480_tables_tool.py`: 291 passed. `tests/test_shaft_parity.py::test_the_api_and_the_cli_print_one_shaft_document_with_the_tables` passes. The browser step `parity with tables` passed inside the orchestrator's `make verify`. Real file: 34-16 log `22 passed` (anchors, completeness, M1 at every tabulated pin, range edges). Off-table W 19x1.25x14 (the row our copy does not print) is the human-accepted case: window rows null, warned. |
| 4 | The solid follows the tables: with them it carries s_vmax read back from the solid; without them the nominal thickness and a warning | VERIFIED | `shaft_model.build_shaft` writes the printed `max_effective_thickness` as the flank shift and falls back to the nominal one when it is `None`. Behavior-dependent, so the single named tests were run here and pass: `test_with_the_tables_the_solid_carries_the_maximum_effective_thickness`, `test_without_the_tables_the_solid_carries_the_nominal_thickness`, `test_a_fit_outside_table_7_and_an_off_table_size_build_the_nominal_solid`, `test_the_download_name_does_not_follow_the_tables`. The worker path is covered: `BuildPool(tables=...)` passes `initargs` to the initialiser and to the replacement worker (`pool.py` `_warm` calls `install(tables)`); `test_a_worker_and_its_replacement_carry_the_parents_tables` and `test_a_worker_builds_the_maximum_material_shaft_from_the_parents_tables` pass, both seen red once (34-05, 34-07). |
| 5 | Gate cost recorded and read: each phase's `make verify` time on record against its predecessor, the milestone close reading inside L43's 300 s bar or the human decides, a reading above it surfaced; Phase 30 check green | VERIFIED | Recorded in `bench/RESULTS.md` `### The gate delta (34-17)`: `2934 passed in 213.54s`, `real 214.53`, against the 34-01 baseline `230.90 s` / `232.23 s`. The reading above the bar (`308.61 s` at 287f0f3, identical code) was surfaced, and the section `### The human's ruling and the review-fix reading (Phase 34)` (325fd37) records that the human accepted `213.54 s` (`real 214.53 s`) as the milestone-close reading on 2026-11-01; the 308.61 s reading is kept, not set aside. A later reading after the fixes, `2940 passed in 235.27s`, rc 0, `real 236.30` (504d5c5, log `34-review-fixes-verify.log`, tail checked here), is under the bar. `git diff 504d5c5 HEAD -- src tests scripts` is empty; the commits after it touch only `.planning`, docs and `bench/RESULTS.md`. Phase 30 check: `make gear.unchanged` re-run here, green (`/api/schema (8723 bytes) byte-equal to v0.6`). This is the roadmap's own mechanism (a reading above the bar is surfaced and the human decides), not an override. |

**Score:** 5/5 truths verified (0 present, behavior-unverified; 0 routed to the human)

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `src/spur/din5480_tables.py` | strict schema, invariants, per-process state, lookups | VERIFIED | 427 lines added, exact-key lookups only, no nearest row. Coverage 93.48 %, the unreached refusal lines are filed as debt. |
| `src/spur/shaft_calc.py` | window, limits, tier warnings | VERIFIED | Wired in `derive_shaft`; read above. |
| `src/spur/shaft_model.py` | solid at s_vmax | VERIFIED | `xm_flank` from `max_effective_thickness`; tip and root stay the printed diameters. |
| `src/spur/pool.py`, `app.py`, `cli.py` | tables reach workers; broken file refuses | VERIFIED | `initargs`, `lifespan` reads before `BuildPool`, `cli.main` reads after `parse_args` for every subcommand. |
| `tests/din5480_real_tables_check.py` | real-file check outside the gate | VERIFIED | Run only by `make tables.test FILE=`; the gate does not collect it (close check 14). Cited result: 22 passed (34-16). |
| `scripts/din5480_tables_tool.py`, `scripts/din5480_read1.py` | check, diff, join, assemble | VERIFIED | Present, exercised by `test_din5480_tables_tool.py` (in the 291). Weak spots: WR-01, WR-04. |
| `bench/RESULTS.md` gate delta, close checks, seen-red table | cost and evidence | VERIFIED | Sections present; figures match the logs they cite. |
| `docs/architecture/decision_log.md` L50 | last entry, nothing earlier edited | VERIFIED | `## L50` present; the 34-17 close check reports 0 deleted lines against ddfb3ea. |
| `private/din5480-tables.json` | the human's file | NOT OPENED | Privacy rule. Existence and shape are evidenced by `34-14-assemble.log` and `34-16-real-file.log`. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `cli.main` | `din5480_tables.active()` | one call after parse_args | WIRED | Exit 1 with the reason; `test_a_broken_table_file_stops_every_command_with_the_reason`, `test_spur_serve_refuses_a_broken_table_file_from_the_real_process` pass (the first was run here). |
| `app.lifespan` | `BuildPool(tables=...)` | tables read before pool | WIRED | `app.py` diff. |
| `BuildPool` | worker `install()` | `initargs` on first and replacement executors | WIRED | `pool.py` diff, tests above. |
| `derive_shaft` | `Tables.size`, `Tables.fit`, `thickness_limits`, `limit_measurement` | direct calls | WIRED | `shaft_calc.py`. |
| `build_shaft` | `ShaftDimensions.max_effective_thickness` | flank shift | WIRED | One source for the printed number and the solid (L08). |
| `ShaftParams` rows | web, API, CLI | schema-carried list | WIRED | Parity test with tables passes. |
| 34-17 gate delta | 34-01 baseline | same-host logs | WIRED | Both sections present. |

### Data-Flow Trace (Level 4)

| Artifact | Data variable | Source | Produces real data | Status |
|---|---|---|---|---|
| `derive_shaft` five rows | `s_vmax`, `s_max`, `s_min`, `limit_max`, `limit_min` | `Tables.fit()` over the loaded file, then `thickness_limits`, `measure_over_pins` | Yes, with a file; `None` plus a warning without | FLOWING |
| `build_shaft` | `xm_flank` | `dims.max_effective_thickness` | Yes, read back from the solid section by tests | FLOWING |
| worker `Tables` | `_state` | parent's object by `initargs` | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| No file: five rows null, tier-1 and nominal-solid warnings | `derive_shaft(ShaftParams())` with `SPUR_DIN5480_TABLES` unset | all five `None`; `NO_TABLE_FILE` and `SOLID_AT_NOMINAL_THICKNESS` in warnings | PASS |
| Missing named file refuses | `SPUR_DIN5480_TABLES=/nonexistent.json python -m spur shaft info` | `error: ... does not exist`, rc 1 | PASS |
| Re-run at HEAD: loader, anchors, calc, tool, read1, solid, pool, parity, CLI | `.venv/bin/python -m pytest --no-cov -n0 -q` on tests/test_din5480_tables.py, test_din5480_anchors.py, test_shaft_calc.py, test_din5480_tables_tool.py, test_din5480_read1.py, test_shaft_model.py, test_pool.py, test_shaft_parity.py, test_cli.py | 494 passed in 110.54s | PASS |
| No file at HEAD: five rows null | `derive_shaft(ShaftParams())` with the variable unset | five `None`, 8 warnings | PASS |
| Tracked table files | `git ls-files -- private`; `git check-ignore -q private/din5480-tables.json` | 0 files; ignored | PASS |
| Gear unchanged | `make gear.unchanged` | byte-equal to v0.6 | PASS |
| Import contracts | `make lint-imports` | `Contracts: 10 kept, 0 broken.` | PASS |
| Whole gate | orchestrator: `make verify` at 504d5c5 (after the fixes) | `2940 passed in 235.27s`, rc 0, real 236.30 | PASS (cited, not re-run) |

### Probe Execution

Step 7c: SKIPPED. No probe scripts are declared by the plans (`scripts/*/tests/probe-*.sh` absent).

### Requirements Coverage

All seven IDs appear in the plans' `requirements` fields and in REQUIREMENTS.md (all marked complete); no ID mapped to Phase 34 is orphaned.

| Requirement | Source plans | Description | Status | Evidence |
|---|---|---|---|---|
| REQ-tables-private-file | 02, 05, 14, 17 and others (9 plan mentions) | private gitignored file, env-named, null plus warning without it | SATISFIED | Truth 1. The warning names the variable, not a path. |
| REQ-tables-transcribed-twice | 02, 03, 08..14 (10 plan mentions) | two reads diffed to zero, provenance, invariants seen red | SATISFIED | Truth 2. |
| REQ-fit-tolerance-window | 04, 06, 15, 16 (7 mentions) | effective and actual windows; fit outside tables is null plus warning | SATISFIED | Truth 3; real-file check 22 passed (cited). |
| REQ-mre-limits | 04, 06, 15 (6 mentions) | M_Re max and min with D_Re from the copy, oracle-proved on anchors | SATISFIED | Truth 3; limits computed by the same formula as the nominal M_Re, tested against the oracle at the written thickness. |
| REQ-solid-max-material | 07 and others (4 mentions) | solid carries s_vmax, nominal plus warning without | SATISFIED | Truth 4. |
| REQ-off-table-builds | 04, 05, 17 (4 mentions) | off-table size builds, rows null and warned | SATISFIED | Truth 3 and the tier tests. |
| REQ-gate-cost-recorded | 01, 17 | gate time recorded against predecessor, inside 300 s or human decides | SATISFIED | Truth 5: the human decided and the ruling is recorded. |

### Human-Authorized Deviations (not gaps)

Table 7 has 30 tolerance rows; Part 2 has 720 sizes (the m 1.25 d_B 19 z 14 nominal row is not printed in our copy, filed as debt `2026-10-31-table-12-m1-25-db19-z14-row-missing-from-our-copy.md`); the load line is `720 16 18 8 30 21`; D-13 keep; range edge read as edge-upper, confirmed on page 24; 34-15 F1 and F2, the d_Ff1 bound, and the derived limit thicknesses accepted. All were checked against the evidence and are consistent with the code and logs.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `src/spur/` (phase files), `scripts/din5480_*.py` | n/a | `TBD` / `FIXME` / `XXX` | none found | Debt-marker gate clear. |
| `src/spur/din5480_tables.py` | 38 | comment said "721 of 721 rows" | none now | Fixed in e0708a7 (grep shows 720). |
| `src/spur/shaft_calc.py` | ~405 | `odd_confirmed` branch unreachable from production (review IN-01) | Info | Deferred as debt `2026-11-01-limit-measurement-odd-confirmed-branch-is-dead.md`. |
| `src/spur/din5480_tables.py` | 278-281 | no sign check on tolerance rows (WR-03) | none now | Fixed in d299fe3. The remaining oversized-`A_s` bound is filed as debt `2026-11-01-an-oversized-a-s-cell-loads-and-shifts-every-limit.md` (Info, deferred by the human). |
| `scripts/din5480_tables_tool.py` | 246-250 | `assemble` accepted one read passed twice (WR-04) | none now | Fixed in e98638b. |
| `scripts/din5480_read1.py` | 165-182 | `ensure_ignored` failed open on git exit 128 (WR-01) | none now | Fixed in 9215f60: 128 passes only with no `.git` above the path; directories are made after the check. Two new tests, run here. |
| `README.md`, `docs/architecture/packaging.md` | 86, 89 | mode 0600 vs uid 10001 (WR-02) | none now | Fixed in d3f339b: both documents now say owner uid 10001, mode 0400 for the container. |

No 🛑 blocker anti-pattern was found. The debt-marker grep over the three phase files (`din5480_tables.py`, `din5480_read1.py`, `din5480_tables_tool.py`) at HEAD is empty. The eight debt files dated 2026-11-01 are in `docs/tech_debt/active/`.

### Human Verification Required

None. The three items of the first report are resolved in `34-UAT.md` (status complete, 3 passed, 0 issues): the gate-cost reading accepted by the human, the review findings dispositioned in `34-REVIEW-DISPOSITION.md`, the leak review closed with the fixture changed.

### Gaps Summary

No gaps. All five criteria verify at HEAD. Nothing the first report verified regressed: `src`, `tests` and `scripts` are identical between 504d5c5 (the orchestrator's full gate, 2940 passed) and HEAD, and the 494 targeted tests, `make lint-imports` (`Contracts: 10 kept, 0 broken.`) and `make gear.unchanged` (byte-equal to v0.6) pass here. The fixture change in 282f264 moved the default-shaft row's expected values in `tests/test_shaft_calc.py` and `tests/test_din5480_tables.py` by invented amounts only; the oracle-agreement tests still pass against the new thickness. Limits of this re-verification: the full gate was cited, not re-run; `private/` was not opened, so the leak review and the 22 real-file checks rest on the human's ruling and the logs; the orchestrator regenerated `covered_digest` over the same covered files at HEAD.

---

_Verified: 2026-11-01_
_Verifier: Claude (gsd-verifier)_
