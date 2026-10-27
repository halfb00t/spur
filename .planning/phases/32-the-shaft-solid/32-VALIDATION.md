---
phase: "32"
slug: "the-shaft-solid"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
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

Task IDs are filled by the planner; rows are keyed by requirement / success criterion until then.

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-----------|-------------------|-------------|--------|
| REQ-shaft-solid / SC1 | Default shaft: one valid solid, volume = closed form (tolerance recorded beside test) | kernel | `pytest tests/test_shaft_model.py -k default -q -n0 --no-cov` | ❌ W0 | ⬜ pending |
| SC1 | STL preview + fine closed shell, mesh volume within measured bias; STEP has `ISO-10303-21;` + `MANIFOLD_SOLID_BREP` | kernel | `-k export` | ❌ W0 | ⬜ pending |
| SC1 | Splined section + shank + chamfer present: bbox z `Ls + Lk`, radial `max(ra, shank_d/2)`, root/tip read back | kernel | `-k section` | ❌ W0 | ⬜ pending |
| SC2 | Shank rows (= tip_d, = root_d, between, ±tiny offsets, below root, length 0): valid + closed form | kernel | `-k shank` | ❌ W0 | ⬜ pending |
| SC2 | `.clean()` guard seen red once (`fuse().clean()` at shank = tip → invalid) | kernel | `-k clean` | ❌ W0 | ⬜ pending |
| SC2 | Chamfer read back from solid = `end_chamfer_effective` | kernel | `-k chamfer_readback` | ❌ W0 | ⬜ pending |
| SC2 | Chamfer past tooth height / splined length: capped, warned naming `end_chamfer`, closed form at effective value | calc + kernel | `-k cap` | ❌ W0 | ⬜ pending |
| SC2 | Cap rounds down (`Ls = 2.0006` case builds one solid) | kernel | `-k round_down` | ❌ W0 | ⬜ pending |
| SC2 | Sub-resolution chamfer: `end_chamfer_effective` is `None` + warning | calc | `pytest tests/test_shaft_calc.py -k chamfer -q -n0 --no-cov` | ❌ W0 | ⬜ pending |
| SC2 | Defect guards (pre-build near-root offset, post-build bracket) raise `BuildError`; each seen red once | kernel | `-k guard` | ❌ W0 | ⬜ pending |
| SC2 | Small-z and z 82 rows build and match | kernel | `-k small_z or z82` | ❌ W0 | ⬜ pending |
| REQ-shaft-solid | `Part` widening: mypy strict clean; `model.build(ShaftParams())` and `pool.build_export` return bytes; shared cache | typecheck + pool | `make typecheck`; `pytest tests/test_pool.py -k shaft -q -n0 --no-cov` | partial | ⬜ pending |
| Seam | `ignore_imports` in same commit as static import; contracts kept; `shaft_model` imports no `spur.model` | lint | `make lint-imports`; `pytest tests/test_seam.py -q -n0 --no-cov` | ✅ | ⬜ pending |
| Keys | `ShaftDimensions` new key pinned; warnings tuple pins updated | unit | `pytest tests/test_shaft_calc.py -q -n0 --no-cov` | ✅ (edit) | ⬜ pending |
| REQ-shaft-build-measured / SC3 | Sweep rows in `bench/RESULTS.md` (host, command, load, margin vs 30 s and L17); bounds pinned | bench + pin | `make bench.build SWEEP=bench/sweeps/shaft.json`; `pytest tests/test_shaft_params.py -k bound -q -n0 --no-cov` | partial | ⬜ pending |
| SC4 | Gate delta recorded in `bench/RESULTS.md`; `make gear.unchanged` green; v0.6 diff empty | gate | `/usr/bin/time -p make verify`; `make gear.unchanged` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_shaft_model.py` — all kernel rows above; each guard seen red once with a log under `investigation/` and a row in `bench/RESULTS.md`
- [ ] `tests/shaft_oracle.py` — closed-form section/chamfer volume helpers (imports nothing from `spur`)
- [ ] `bench/sweeps/shaft.json` + part switch and RSS column in `bench/build_time.py`; `tests/test_bench.py` row for the loader
- [ ] Decide whether `tests/test_shaft_model.py` joins `HEAVY_TEST_FILES` (`tests/test_hooks.py`)
- [ ] Framework install: none

---

## Manual-Only Verifications

All phase behaviors have automated verification. Timing rows in `bench/RESULTS.md` are measured by command and recorded, not asserted by a test.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
