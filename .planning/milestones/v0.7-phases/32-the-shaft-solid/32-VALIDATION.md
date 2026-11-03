---
phase: "32"
slug: "the-shaft-solid"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: true) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-27"
---

# Phase 32 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `32-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 + pytest-xdist 3.8.0 + pytest-cov 7.1.0 (`--strict-markers --strict-config`, `filterwarnings = error`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]`; coverage `fail_under = 96` |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_shaft_model.py tests/test_shaft_calc.py tests/test_shaft_params.py tests/test_seam.py -q -n0 --no-cov` |
| **Full suite command** | `make verify` |
| **Estimated runtime** | quick: kernel rows 0.3-2.4 s each; full: ~240 s (last recorded 2355 passed / 243.23 s; take a fresh baseline at phase start) |

---

## Sampling Rate

- **After every task commit:** Run the quick command; the commit slice must stay under L36's 30 s (measure with `make verify.fast`).
- **After every plan wave:** Run `make verify` (or the full shaft files `-n 8` plus `make lint-imports typecheck`).
- **Before `/gsd-verify-work`:** `make verify` green with result line recorded, `make gear.unchanged` green, `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` empty.
- **Max feedback latency:** 30 seconds (commit slice).

---

## Per-Task Verification Map

Rows keyed by requirement / success criterion, mapped to the tests the plans shipped (the planned `-k` names
`clean`, `chamfer_readback`, `round_down`, `guard`, `small_z or z82` select nothing; the real names are below).
All green in `make verify` (`2644 passed in 233.72s`, 2026-10-27, HEAD after 32-06).

| Requirement | Behavior | Plan | Test Type | Automated Command | Status |
|-------------|----------|------|-----------|-------------------|--------|
| REQ-shaft-solid / SC1 | Default shaft: one valid solid, volume = closed form | 32-03 | kernel | `pytest tests/test_shaft_model.py -q -n0 --no-cov -k default` (7) | ✅ green |
| SC1 | STL preview + fine closed shell within measured bias; STEP solid | 32-04 | kernel | `pytest tests/test_shaft_model.py -q -n0 --no-cov -k export` (3); `test_the_shaft_stl_carries_its_chamfer_at_the_end_face` | ✅ green |
| SC1 | Splined section + shank + chamfer; root/tip read back | 32-03 | kernel | `pytest tests/test_shaft_model.py -q -n0 --no-cov -k section` (`test_the_default_shaft_reads_back_its_root_and_tip_from_a_section`) | ✅ green |
| SC2 | Shank rows (= tip, = root, between, ±tiny, below root, length 0) | 32-03 | kernel | `pytest tests/test_shaft_model.py -q -n0 --no-cov -k shank` (13) | ✅ green |
| SC2 | No-`.clean()` guard seen red once | 32-03 | kernel + log | `test_every_shank_regime_builds_with_the_closed_form_volume`; red: `investigation/32-03-red-clean.log` | ✅ green |
| SC2 | Chamfer read back = `end_chamfer_effective` | 32-03 | kernel | `test_the_default_shaft_reads_back_its_applied_chamfer` | ✅ green |
| SC2 | Chamfer caps: capped, warned, closed form at effective value | 32-02, 32-03 | calc + kernel | `pytest tests/test_shaft_model.py -q -n0 --no-cov -k cap` (6); `pytest tests/test_shaft_calc.py -k chamfer` (6) | ✅ green |
| SC2 | Cap rounds down (`Ls = 2.0006` builds one solid) | 32-03 | kernel | `test_every_chamfer_cap_builds_at_the_applied_size` (rows with `splined_length=2.0006`) | ✅ green |
| SC2 | Sub-resolution chamfer → `None` + warning | 32-02 | calc | `pytest tests/test_shaft_calc.py -k chamfer -q -n0 --no-cov` | ✅ green |
| SC2 | Defect guards raise `BuildError`, each seen red once | 32-03 | kernel | `test_a_cone_start_inside_the_root_band_is_refused_before_the_kernel_runs`, `test_a_cone_past_the_tooth_height_is_refused_by_the_volume_bracket`, `test_no_lattice_chamfer_reaches_the_root_band` | ✅ green |
| SC2 | Small-z and z 82 rows build and match | 32-03 | kernel | `test_a_shaft_whose_base_circle_lies_above_the_root_builds` (W14x2x6, W9x1x8), `test_an_82_tooth_shaft_builds_with_the_closed_form_volume` | ✅ green |
| REQ-shaft-solid | `Part` widening; model/pool build a shaft; shared cache | 32-04 | typecheck + pool | `make typecheck`; `pytest tests/test_pool.py -k shaft` (1); `pytest tests/test_shaft_model.py -q -n0 --no-cov -k doorway or cache` | ✅ green |
| Seam | `ignore_imports` with the static import; contracts kept; no cycle | 32-04 | lint | `make lint-imports` (10 kept); `pytest tests/test_seam.py` (7) | ✅ green |
| Keys | `ShaftDimensions` 13th key pinned; warnings tuple pins | 32-02 | unit | `pytest tests/test_shaft_calc.py -q -n0 --no-cov` | ✅ green |
| REQ-shaft-build-measured / SC3 | Sweep rows recorded; bounds pinned | 32-05 | bench + pin | `make bench.build SWEEP=bench/sweeps/shaft.json`; `pytest tests/test_shaft_params.py -k bound` (7) | ✅ green |
| SC4 | Gate delta recorded; `make gear.unchanged` green; v0.6 diff empty | 32-06 | gate | `/usr/bin/time -p make verify`; `make gear.unchanged` | ✅ green |

*Status: ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/test_shaft_model.py` — all kernel rows above; each guard seen red once with a log under `investigation/` and a row in `bench/RESULTS.md`
- [x] `tests/shaft_oracle.py` — closed-form section/chamfer volume helpers (imports nothing from `spur`)
- [x] `bench/sweeps/shaft.json` + part switch and RSS column in `bench/build_time.py`; `tests/test_bench.py` row for the loader
- [x] Decided (32-03, measured 20.97 s at load 23-30): `tests/test_shaft_model.py` joins `HEAVY_TEST_FILES`. Decide whether `tests/test_shaft_model.py` joins `HEAVY_TEST_FILES` (`tests/test_hooks.py`)
- [x] Framework install: none

---

## Manual-Only Verifications

All phase behaviors have automated verification. Timing rows in `bench/RESULTS.md` are measured by command and recorded, not asserted by a test.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-10-27 (validate-phase, state A; no gaps)

## Validation Audit 2026-10-27

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
| Selector drift fixed | 5 |
