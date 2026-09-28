---
phase: 10-tooth-tip-chamfer
verified: 2026-09-28T00:00:00Z
status: passed
score: 5/5 must-haves verified
covered_files: [".planning/phases/10-tooth-tip-chamfer/10-01-PLAN.md", ".planning/phases/10-tooth-tip-chamfer/10-01-SUMMARY.md", ".planning/phases/10-tooth-tip-chamfer/10-02-PLAN.md", ".planning/phases/10-tooth-tip-chamfer/10-02-SUMMARY.md", ".planning/phases/10-tooth-tip-chamfer/10-03-PLAN.md", ".planning/phases/10-tooth-tip-chamfer/10-03-SUMMARY.md", ".planning/phases/10-tooth-tip-chamfer/10-04-PLAN.md", ".planning/phases/10-tooth-tip-chamfer/10-04-SUMMARY.md", ".planning/phases/10-tooth-tip-chamfer/10-05-PLAN.md", ".planning/phases/10-tooth-tip-chamfer/10-05-SUMMARY.md", "README.md", "bench/RESULTS.md", "bench/sweeps/tip_chamfer.json", "bench/tip_chamfer_spike.py", "docs/architecture/decision_log.md", "docs/architecture/gear-maths/implementation.md", "docs/architecture/solid-model/tactics.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md", "docs/tech_debt/active/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md", "docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md", "src/spur/calc.py", "src/spur/model.py", "src/spur/params.py", "src/spur/static/app.js", "tests/test_api.py", "tests/test_bench.py", "tests/test_calc.py", "tests/test_cli.py", "tests/test_model.py"]
covered_digest: "v2:sha256:5ae64ffc28864accc0af8359c8a4bcd0aa4b4d48ecedd531f49bba274f60703a"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 10: Tooth-Tip Chamfer Verification Report

**Phase Goal:** A user can break the tooth-tip edges for a safer, more printable part,
with flanks, root fillets, bore and outside diameter untouched.
**Verified:** 2026-09-28
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Setting `tip_chamfer` breaks tooth-tip arc edges at both end faces; flanks, root fillets, bore, cutouts untouched; OD unchanged | VERIFIED | `src/spur/model.py:_tip_edges`/`_chamfer_tips`; `tests/test_model.py::test_the_tip_chamfer_breaks_only_the_tip_arcs_on_the_built_solid` re-run live (3 rows: d-flat, keyway-round, hex) — all pass, asserting +38 CONE faces, +114 edges, smaller volume, bounding box and `tip_d` unchanged within TOL, rim/floor selector counts unchanged |
| 2 | Chamfer is the end-face edge break (3D edge op), recorded as new `Lxx` with measured cost; no sizing guidance cited as sourced standard | VERIFIED | `docs/architecture/decision_log.md` `## L29` present (append-only: `git diff --numstat 277a98f` shows 0 deletions), cites `solid.chamfer(c, None, edges)` and 10-01/10-04's measured costs; repo-wide `git grep -nE '0\.1 ?[–-] ?0\.2' -- README.md src docs` returns no match |
| 3 | A chamfer larger than the tip land allows is capped and reported in `warnings` (L03) | VERIFIED | `src/spur/calc.py:tip_chamfer_limit`/`tip_chamfer_effective`, `derive()` warning; `tests/test_calc.py` cap tests re-run live (25 tests pass, includes `test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first`) |
| 4 | Operator's cost at heaviest allowed config measured against `SPUR_BUILD_TIMEOUT=30s` and recorded in `bench/RESULTS.md` | VERIFIED | `bench/RESULTS.md` `## Tooth-tip chamfer build and export time (Phase 10)` section present; heaviest row 14.87s of 30s recorded; `tests/test_bench.py` sweep test re-run live (1 pass) |
| 5 | Phase 7's regression fixture still passes — `tip_chamfer` defaults to off, every pre-v0.2 parameter set unchanged | VERIFIED | `git diff --exit-code tests/regression/pre_v0_2.json` — 0 diff; `tests/regression` suite re-run live — 86 passed |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` | `tip_chamfer` field, Teeth group, after `root_fillet` | VERIFIED | Line 49: `tip_chamfer: float = _f(0.0, 0, 3, title="Tip chamfer", group="Teeth", unit="mm", ...)` |
| `src/spur/calc.py` | `TIP_CHAMFER_MARGIN`, `spline_start`, `tip_chamfer_limit`, `tip_chamfer_effective`, `DerivedDimensions.tip_chamfer_effective`, warning | VERIFIED | All present (lines 39, 219, 247, 273, 462, 543-549) |
| `src/spur/model.py` | `_tip_edges`, `_chamfer_tips` last in `_build`, `_outline` reading `calc.spline_start` | VERIFIED | `_chamfer_tips` at line 250, `_tip_edges` at line 332, `_build` calls `_chamfer_tips` last (line 368) after `_cut_keyway` (line 367) |
| `src/spur/static/app.js` | one DIMS row | VERIFIED | Line 24: `['tip_chamfer_effective', 'Tip chamfer used']` |
| `tests/test_api.py` | the tip-chamfer link over HTTP; the 24-field contract | VERIFIED | `test_a_tip_chamfer_link_is_served_with_the_chamfer_it_cut` present, re-run passing |
| `tests/test_calc.py` | cap at each limit, warning, no-other-number, rounded cap inside kernel boundary | VERIFIED | `test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first` present, re-run passing (25 tests total) |
| `tests/test_cli.py` | CLI/API parity, README example run, empty-selection guard | VERIFIED | `test_cli_and_api_print_the_same_tip_chamfer_document`, `test_readme_export_examples_run` (with `--tip-chamfer 0.4`), guard test — all re-run passing |
| `bench/tip_chamfer_spike.py` | committed spike, `cost_row(` | VERIFIED | Present, imports `spline_start` from `spur.calc` |
| `bench/RESULTS.md` | two Phase 10 sections | VERIFIED | `## Tooth-tip chamfer spike (Phase 10, D-05)` (line 670) and `## Tooth-tip chamfer build and export time (Phase 10)` (line 790) both present |
| `bench/sweeps/tip_chamfer.json` | 9 Phase 10 parameter sets | VERIFIED | Present, 9-row cross product confirmed by `test_the_tip_chamfer_sweep_is_every_combination_d_06_names` |
| `docs/architecture/decision_log.md` | L29 | VERIFIED | `## L29 —` present, append-only |
| `docs/architecture/gear-maths/implementation.md` / `solid-model/tactics.md` | four calc rows, `_chamfer_tips` in pipeline | VERIFIED | Confirmed present via SUMMARY-cited greps and spot read |
| `docs/tech_debt/active/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md` | Severity: must | VERIFIED | File exists, indexed in `docs/tech_debt/INDEX.md` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `model.py (_build)` | `model.py (_chamfer_tips)` | last step, after `_cut_keyway` | WIRED | `solid = _chamfer_tips(solid, p, pr)` is the final line of `_build`'s pipeline (line 368) |
| `model.py (_chamfer_tips)` | `calc.py (tip_chamfer_effective)` | applies exactly the printed cap | WIRED | `c = tip_chamfer_effective(p)` (line 261) |
| `model.py (_outline)` | `calc.py (spline_start)` | shared involute-start radius | WIRED | `r0 = spline_start(pr, fillet)` (line 128) |
| `static/app.js (DIMS)` | `calc.py (DerivedDimensions)` | UI reads a real derived field | WIRED | `tip_chamfer_effective` is a real `DerivedDimensions` field (calc.py:462), not a static value |
| `README.md (CLI example)` | `tests/test_cli.py (test_readme_export_examples_run)` | example executed as a test | WIRED | `--tip-chamfer 0.4` appears in both README (line 112) and the test (line 104) |

### Behavioral Spot-Checks (tests re-run live by verifier, not trusted from SUMMARY)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Built-solid proof (only tip arcs changed) | `pytest tests/test_model.py -k "tip_chamfer or tip_arc"` | 9 passed | PASS |
| Cap/warning/rounding contract | `pytest tests/test_calc.py -k "tip_chamfer or spline_start"` | 25 passed | PASS |
| API link + 422 guard | `pytest tests/test_api.py -k tip_chamfer` | 2 passed | PASS |
| CLI parity + README example + export guard | `pytest tests/test_cli.py -k "tip_chamfer or readme"` | 3 passed | PASS |
| Selector matrix (30 rows incl. teeth-200, module-0.2) | `pytest tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges` | 30 passed | PASS |
| Cost sweep pinned | `pytest tests/test_bench.py -k tip_chamfer` | 1 passed | PASS |
| Pre-v0.2 regression | `pytest tests/regression` + `git diff --exit-code tests/regression/pre_v0_2.json` | 86 passed, 0 diff | PASS |
| Static analysis on touched src | `ruff check src/spur/{params,calc,model}.py bench/tip_chamfer_spike.py tests/test_bench.py` | All checks passed | PASS |
| Strict typing on touched src | `mypy --strict src/spur/{params,calc,model}.py` | Success, no issues | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-tip-chamfer | 10-02, 10-03, 10-05 | Tip-arc chamfer, positional selector, untouched flanks/fillets/bore/OD | SATISFIED | Built-solid proof + real-pipeline spy tests pass; REQUIREMENTS.md marks Complete |
| REQ-tip-chamfer-capped | 10-01, 10-02, 10-04, 10-05 | Capped and reported in warnings; cost measured against `SPUR_BUILD_TIMEOUT` | SATISFIED | Cap tests pass; `bench/RESULTS.md` sweep records heaviest row at 14.87s/30s; REQUIREMENTS.md marks Complete |

No orphaned requirements — `.planning/REQUIREMENTS.md`'s "Phase 10" rows list exactly REQ-tip-chamfer and REQ-tip-chamfer-capped, matching both plans' frontmatter declarations.

### Anti-Patterns Found

None. `grep -n -E "TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER"` (case-insensitive, plus placeholder/stub phrasing) over all touched `src/` and `bench/` files returned no matches. Both tech-debt items filed this phase are `Severity: must` (deferred with a named trigger, per CLAUDE.md's debt taxonomy), not `blocker` — correctly not requiring immediate action.

### Human Verification Required

None. All must-haves are code-verifiable and were verified by re-running the actual tests (not by trusting SUMMARY claims), reading the implementation, and confirming append-only invariants on `decision_log.md` and `bench/RESULTS.md` via `git diff --numstat` against the Phase 9 baseline commit.

### Gaps Summary

No gaps. All five ROADMAP success criteria are independently verified against the codebase:
the chamfer implementation exists, is wired into `_build`'s pipeline as the last step, is
proven not to touch any other feature by a built-solid proof with its own tripwire (shown to
fail when the step is skipped), is capped via a three-limit `min()` and reported in warnings,
its cost is measured and recorded in `bench/RESULTS.md` against the 30s timeout (heaviest row
14.87s, well inside budget), and the Phase 7 regression fixture is byte-unchanged with all 86
regression cases still passing. `docs/architecture/decision_log.md` L29 documents the phase
append-only, and no unsourced chamfer-sizing figure appears anywhere in README, src/, or docs/.

---

_Verified: 2026-09-28_
_Verifier: Claude (gsd-verifier)_
