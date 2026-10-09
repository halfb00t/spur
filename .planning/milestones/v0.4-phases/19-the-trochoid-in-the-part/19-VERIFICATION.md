---
phase: 19-the-trochoid-in-the-part
verified: 2026-10-09T10:00:00Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - ".planning/phases/19-the-trochoid-in-the-part/19-01-PLAN.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-01-SUMMARY.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-02-PLAN.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-02-SUMMARY.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-03-PLAN.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-03-SUMMARY.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-04-PLAN.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-04-SUMMARY.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-05-PLAN.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-05-SUMMARY.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-06-PLAN.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-06-SUMMARY.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-07-PLAN.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-07-SUMMARY.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-08-PLAN.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-08-SUMMARY.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-09-PLAN.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-09-SUMMARY.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-10-PLAN.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-10-SUMMARY.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-11-PLAN.md"
  - ".planning/phases/19-the-trochoid-in-the-part/19-11-SUMMARY.md"
  - "bench/RESULTS.md"
  - "docs/architecture/decision_log.md"
  - "src/spur/calc.py"
  - "src/spur/model.py"
  - "src/spur/params.py"
  - "src/spur/static/app.js"
  - "tests/regression/pre_v0_2.json"
  - "tests/test_model.py"
  - "tests/test_trochoid.py"
covered_digest: "v3:sha256:f821e0042d2b1b5fc0ada97448c6778e11d4c70200e80703427dc9949d7f576a"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: none
  note: "Initial verification. Phases 17 and 18 (both status: passed) were regression-checked: their gates still hold on this tree (no src/spur file outside calc.py, model.py, params.py, app.js moved since df4749e; no numpy/scipy; requirements.txt still 31 pins)."
---

# Phase 19: The Trochoid in the Part Verification Report

**Phase Goal:** The trochoid root reaches the built solid, the printed numbers and all three interfaces without changing any part a shared link produces today -- the outline consumes the proven curve, every number printed beside it is proved or warned, it composes with every shipped feature inside `SPUR_BUILD_TIMEOUT`, and the pre-v0.2 fixture is byte-identical to the milestone's start.
**Verified:** 2026-10-09
**Status:** passed
**Re-verification:** No -- initial verification (phase base `df4749e`, HEAD `b1b111b`)

Judged against the code as it stands after the review fixes (`e733cc2` CR-01, `b51931c` WR-01). SUMMARY figures for `root_waist` are superseded by the code and were not used as evidence.

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | No part a shared link produces today changed: fixture clean, 85 replay cases pass unmodified, omitted-field link gives the same `derive()` document and solid, new fields null on replay | VERIFIED | `git diff --quiet df4749e -- tests/regression/pre_v0_2.json` exits 0 (printed `FIXTURE_IDENTICAL`); `git diff df4749e HEAD --stat -- tests/regression` is empty (no replay test or corpus file touched). `make test PYTEST_ARGS="tests/regression tests/test_trochoid.py -q --no-cov"` gave `178 passed in 7.29s`. `params.py` default `root_shape="radial"`; a default `GearParams()` derives `root_form_d None`, `root_waist None`, `root_thickness 3.166`, `root_gap 1.609`, no hob warning. Radial branch of `_outline` is guarded by `if curve is not None` and otherwise untouched. The undercut sentence in radial mode is guarded by `rm.mode == "radial"` and keeps its old text (the five records at `pre_v0_2.json:582,632,948,996,1588` replay green). |
| 2 | The root in the solid is the oracle's root: `root_d == 2 rf` in both modes; kernel-tier proof against the Phase 18 oracle at a measured bar; guards that do not rest on `isValid()`; generator never in `model.py` | VERIFIED | Derived `root_d` 28.875 = `2*rf` in both modes (run live, default gear). `tests/test_model.py::test_root_d_is_the_root_circle_in_both_root_modes` (4 cases), `test_the_built_root_is_the_oracle_s_root_on_every_kernel_row` (7 rows), `test_the_default_gear_asked_for_the_hob_root_builds_the_oracle_s_root` and the tripwire `..._off_by_0_05_mm` all pass (21 passed in 22.34s). The oracle (`tests/trochoid_oracle.py`) imports nothing from `spur` (takes plain floats), so it is independent of `calc`; the tripwire reads 5.5x over the bar so the proof can go red. `model.py` implements `_guard_junction` (1e-11 rad), `_guard_spacing` (ratio 1000), `_guard_annulus` (TOL), `_guard_area` (5e-2 vs polygon of its own points) plus `ROOT_ARC_MIN`; none calls `isValid()`; each raises `BuildError` naming `root_shape=radial`. `model.py` imports `RootCurve`/`root_mode`/`spline_start` from `calc` and defines no root solver (generator `_root_curve`/`_trochoid_point`/`_waist` live in `calc.py`). Built live: 4 hob-root gears, all `isValid()`, 0.07 to 0.81 s. |
| 3 | Every number printed beside the trochoid has a proof or a warning: tip radius used at 3 dp with cap warning; `root_thickness`/`root_gap` null with a warning; waist with a floor; undercut sentence restated from the cutter with `x_min`; no lead-in warning without a chord; radial fixture sentences byte-identical | VERIFIED | Live `derive()` on hob-root gears: `root_thickness None`, `root_gap None` plus the one "not printed with the hob-cut root" sentence; `root_fillet 0.634` printed with "reduced to 0.634 mm ... largest that keeps the cutter a tip land" when 1.0 and 3.0 were asked; `root_form_d` 30.62 (junction diameter); `root_waist` printed and, on 8 teeth, 14.5 deg, shift -0.5132, reads 0.395 with the "only 0.395 mm thick at its narrowest ... under the 0.4 mm" warning firing (CR-01 case, the old reading 0.401 was silent). 16-point minimum of `2Rh` agrees (0.395; 3.15 vs printed 3.149) and `_waist` minimises `R*h` with a fixed 60-step golden section. Undercut sentence for a crossing join reads "Below 12.0 teeth this cutter undercuts the gear ... a profile shift of 0.174 or more avoids the undercut", with no "radial root" wording; the lead-in warning is inside the `else` branch that only runs without a curve. The cap/lead-in/undercut sentences all come from `root_warnings`/`_undercut_advice`, with `x_min` printed. Radial-mode record replay passes. |
| 4 | The trochoid composes and is priced: tip chamfer re-bisected across the junction; recesses and each cutout pattern build; heaviest low-tooth row in `bench/RESULTS.md` against `SPUR_BUILD_TIMEOUT`; `make verify` cost recorded against 66 s bar | VERIFIED | `test_the_kernel_fails_one_step_past_the_hob_root_junction`, `test_the_largest_tip_chamfer_the_hob_root_junction_allows_builds` and the 192-row `tests/test_calc.py` composition product (root x bore x cutout x recess x tip) pass (composition rows in the 114/30/178 targeted runs and the fixer's full gate). `bench/RESULTS.md` "Chamfer across the junction (19-01)" and "Chamfer law on the real build (19-09)": law holds, no optimistic row. "Composed build time on the real build (19-09)": 34 requests, heaviest 14.64 s of 30 s (trochoid), every row inside the timeout. "The gate, priced (19-09)": `make verify` mean 192.94 s against the 66 s bar (2.92x), with the kernel-tier rows priced (21 of the 25 slowest calls). The criterion asks that the cost be recorded, and it is; the overrun was put to the human, who answered `accept-A` and L38 records it (see Notes). |
| 5 | All three interfaces agree from one model and the record is true: field walk covers `root_shape` once across schema/form/CLI as a `Literal`; `spur info` and `/api/info` byte-identical; refusals route to 422 and exit 2; new `Lxx` appended; docs brought true | VERIFIED | `root_shape` is `Literal["radial","trochoid"]` (never a bool); `tests/test_cli.py:227-231` walks `enum == get_args(annotation)` for every choice field and pins `["radial","trochoid"]`; `tests/test_api.py:385` asserts the schema enum; `app.js` DIMS gained `root_form_d`/`root_waist` rows, `<select>` renders from `enum`. `test_cli.py` parity tests (`test_cli_and_api_print_the_same_tip_chamfer_document`, `test_a_root_guard_build_error_reads_the_same_on_the_api_and_the_cli`, `test_a_kernel_refusal_in_the_hob_root_outline_is_a_422_that_names_the_outline`) pass: `make test PYTEST_ARGS="tests/test_cli.py tests/test_api.py -q --no-cov"` gave `114 passed in 10.39s`. L38 appended (supersedes L10, amends L09 and L33) at `decision_log.md:2091`, names the flip trigger (a real fit report or a mating-pair request below `z_min`). `git diff --stat df4749e HEAD` shows README, gear-maths (4 files), solid-model (5 files), `docs/ideas/2026-09-21-trochoidal-root-fillets.md`, `bench/RESULTS.md` all changed in the phase. |

**Score:** 5/5 truths verified (0 present, behavior-unverified; 0 overrides)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` | `root_shape` default-off `Literal` after `tip_chamfer`; `root_fillet` help names both meanings | VERIFIED | Present, wired to `root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)` in `calc.py` (3 call sites) and `model._build` (line 773) |
| `src/spur/calc.py` | `root_mode`, `RootCurve`, `_waist`, `root_form_d`/`root_waist` fields, `ROOT_WAIST_FLOOR`, restated undercut | VERIFIED | Substantive (1777 lines), single predicate read by `derive`, `_build`, `spline_start`, `tip_chamfer_limit` |
| `src/spur/model.py` | trochoid outline, junction from one `Vector`, four guards, `ROOT_ARC_MIN`, kernel-failure wrapper | VERIFIED | `_trochoid_outline`, `_trochoid_teeth`, `_guard_*`, `_hob_root_kernel_failure` all present and used by `_gear_blank` |
| `src/spur/static/app.js` | form rows for the two new numbers | VERIFIED | DIMS gained `root_form_d`, `root_waist` |
| `tests/regression/pre_v0_2.json` | byte-identical to `df4749e` | VERIFIED | `git diff --quiet` exit 0 |
| `bench/RESULTS.md`, `docs/architecture/decision_log.md` L38 | measurements and the decision | VERIFIED | Sections listed above; L38 present |

### Key Link Verification

| From | To | Via | Status |
|------|----|-----|--------|
| `GearParams.root_shape` | outline in the built solid | `root_mode(...).curve` -> `_outline(pr, fillet, curve)` -> `_trochoid_outline` | WIRED (built live) |
| `RootCurve.points[-1]` | involute spline start | the same `cq.Vector` object (`flank_l = [root_l[-1]] + ...`) and `spline_start(..., curve)` | WIRED |
| `derive()` | built solid | single `root_mode` call, same predicate as `model._build` | WIRED |
| `tip_chamfer_limit` | hob-root junction | reads `RootMode.curve`, bound `ra - R_join - TIP_CHAMFER_MARGIN` | WIRED (pinned by kernel tests) |
| `root_shape` | web form / CLI / `/api/info` | schema `enum`, `choices=`, `<select>` | WIRED (field-walk tests) |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Real Data | Status |
|----------|---------------|--------|-----------|--------|
| `DerivedDimensions.root_waist` | `rm.curve.waist` | `_waist` minimising `R h` over the solved curve | Yes (matches a sampled minimum, 3 gears) | FLOWING |
| `DerivedDimensions.root_form_d` | `rm.curve.points[-1][0]` | junction radius from the solved curve | Yes | FLOWING |
| `DerivedDimensions.root_fillet` | `rm.cutter.rho` | `cutter()` capped value | Yes (0.634 on a 1.0/3.0 request) | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Fixture byte-identical | `git diff --quiet df4749e -- tests/regression/pre_v0_2.json` | exit 0 | PASS |
| Regression + trochoid tier | `make test PYTEST_ARGS="tests/regression tests/test_trochoid.py -q --no-cov"` | 178 passed in 7.29s | PASS |
| CLI + API parity | `make test PYTEST_ARGS="tests/test_cli.py tests/test_api.py -q --no-cov"` | 114 passed in 10.39s | PASS |
| Hob-root model/guard/chamfer tests | `make test PYTEST_ARGS="tests/test_model.py -k 'hob or trochoid or root_d or kernel_exception' -q --no-cov"` | 30 passed in 33.93s | PASS |
| Kernel tier + tripwire | `-k 'oracle_s_root or root_d_is or off_by_0_05 or no_guard_fires'` | 21 passed in 22.34s | PASS |
| Lint / types | `ruff check src tests bench`; `mypy --strict src` | All checks passed; no issues in 10 source files | PASS |
| Live build of four hob-root gears | `model.build(GearParams(root_shape="trochoid", ...))` | all `isValid()`, 0.07 to 0.81 s | PASS |
| Full gate | `make verify` (fixer, final tree `b51931c`) | `1220 passed in 196.18s`, coverage 97.92 %, exit 0; `git diff --stat b51931c HEAD -- src tests bench Makefile pyproject.toml` is empty, so the tree the gate ran on is the tree verified. Not re-run here. | PASS (inherited, tree identical) |

### Probe Execution

Step 7c: SKIPPED (the plans declare no `probe-*.sh`; the proof tier is pytest).

### Requirements Coverage

All six IDs appear in plan frontmatter and in REQUIREMENTS.md (all `[x]`, traceability table "Phase 19 / Complete"); no orphans.

| Requirement | Source Plans | Status | Evidence |
|-------------|--------------|--------|----------|
| REQ-root-mode-decided | 19-02, 19-04, 19-07, 19-10, 19-11 | SATISFIED | L38 (O4: opt-in, flip deferred, supersedes L10, amends L09/L33); `Literal` field; fixture identical; Phase 20 recorded skipped |
| REQ-outline-consumes-root-curve | 19-02, 19-04, 19-05, 19-06 | SATISFIED | `_trochoid_outline`, junction from one `Vector`, four guards, kernel-tier proof, generator absent from `model.py` |
| REQ-derived-numbers-honest-under-trochoid | 19-02, 19-04, 19-07, 19-09 | SATISFIED | thickness/gap null + warning, `root_form_d`, `root_waist` + floor warning (CR-01 fixed and re-pinned), no lead-in without chord |
| REQ-cutter-tip-radius-settable | 19-04, 19-07, 19-09 | SATISFIED | `root_fillet` reinterpreted (D-01), capped value printed at 3 dp with cap sentence, exposed from the model |
| REQ-undercut-warning-restated | 19-06, 19-10, 19-11 | SATISFIED | restated from the cutter with `x_min`, no "radial root" wording; radial sentence byte-identical |
| REQ-trochoid-composes-and-is-priced | 19-01, 19-05, 19-07, 19-08, 19-09, 19-10, 19-11 | SATISFIED | chamfer re-bisection, 192-row composition product, 34-row timing sweep inside 30 s, gate cost recorded, docs brought true |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (src diff vs `df4749e`) | - | `TBD/FIXME/XXX/TODO/HACK` in added lines | none | None found; the repo's unfinished-work scan passes in `make verify` |

The four info findings the review skipped (IN-01 to IN-04: a half-true "one answer" comment, a stale `bench/trochoid_part.py` docstring, stale gate-cost comments, label nits) are deferred as one named debt item (`docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md`). None affects a printed number or a built part.

### Human Verification Required

None. Every truth is exercised by a passing test or a live run; no truth is a state-transition or cleanup invariant left to presence checks. The one visual item (the hob-root number rows and the `<select>` in the web form) is covered at the schema and field-walk level by tests; a browser glance is optional polish, not a gate.

### Notes (not gaps)

- **The gate costs 2.92x L34's 66 s bar** (192.94 s mean, same host as the 52.89 s before-figure). The success criterion requires the cost to be recorded against the bar, not held inside it; the human saw the priced options and chose `accept-A` (19-09), and L38 records it. L34's 66 s stays on paper while the gate reads about 193 s locally. Re-setting the bar or revisiting the oracle's 401-position count is a separate, open decision the phase did not make.
- **Phase 20** is recorded `Skipped (O4, flip deferred)` by 19-11 per D-08. The ROADMAP.md top-level list still shows the Phase 19 line as `[ ]`; that checkbox is the orchestrator's to flip on completion.
- Earlier SUMMARY `root_waist` figures (for example 1.473) are superseded by CR-01's fix (1.442); the code, `bench/RESULTS.md` and the tests agree on the new values.

## Gaps Summary

No gaps. All five roadmap success criteria hold in the code, all six requirement IDs are accounted for and satisfied, the fixture is byte-identical to the milestone start, and the hob-root numbers printed beside the trochoid are each proved (junction bars, kernel-tier oracle, dense-sample waist check) or warned.

---

_Verified: 2026-10-09_
_Verifier: Claude (gsd-verifier)_
