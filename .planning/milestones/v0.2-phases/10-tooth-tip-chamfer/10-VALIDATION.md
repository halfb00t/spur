---
phase: "10"
slug: "tooth-tip-chamfer"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-09-28"
validated: "2026-09-28"
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (existing project pin, `pyproject.toml` `[tool.pytest.ini_options]`, `--strict-markers --strict-config`, `filterwarnings = error`) |
| **Config file** | `pyproject.toml` (unchanged by the phase) |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_calc.py tests/test_model.py -k "tip or spline" -q` — 37 passed in 10.24 s (2026-09-28) |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import-boundary contracts, unfinished-work scan, pytest — CLAUDE.md's one gate; also the pre-commit hook) |
| **Estimated runtime** | 98–104 s warm for `make verify` at 455 tests (98.11 s fixer run, 101.44 s post-wave-5, 104.50 s post-WR-01 — all 2026-09-28); 81.6 s at 407 tests when the phase started. The 10-03 built-solid proofs and the two 200-tooth matrix rows are the increase (R-10-03). Cold first run is page cache, not the tests |

---

## Sampling Rate

- **After every task commit:** Run `.venv/bin/python -m pytest tests/test_calc.py tests/test_model.py -k "tip or spline" -q` and `git diff --exit-code tests/regression/pre_v0_2.json` (L26: the fixture never moves in a feature commit — it did not, across all 17 phase commits)
- **After every plan wave:** Run `make verify`
- **Before `/gsd-verify-work`:** `make verify` green and `make bench.build SWEEP=bench/sweeps/tip_chamfer.json` recorded in `bench/RESULTS.md`, every row inside `SPUR_BUILD_TIMEOUT=30s`
- **Max feedback latency:** ~100 s (one warm `make verify`, which the pre-commit hook runs on every commit — every commit of this branch carried it)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 10-01-01 | 01 | 1 | REQ-tip-chamfer-capped | T-10-01 / T-10-02 | The tracer row's topology deltas (38 arcs, 19/19, +38 CONE faces, +114 edges) and its timing are printed, never assumed; nothing under `src`, `tests` or `Makefile` changes (D-05) | bench-tracer | `.venv/bin/python -c "from bench.tip_chamfer_spike import cost_row; r = cost_row({}, 0.4); ... assert r.ok() and (r.arcs, r.per_face, r.d_faces, r.d_cone, r.d_edges) == (38, (19, 19), 38, 38, 114)"` + `make lint typecheck` | ✅ | ✅ green (re-run 2026-09-28: row `ok`, 0.79 s) |
| 10-01-02 | 01 | 1 | REQ-tip-chamfer-capped | T-10-01 / T-10-02 / T-10-03 | Every cost row and one verdict recorded verbatim in `bench/RESULTS.md`; a FAILED verdict halts for D-07 | doc-grep | `sed -n '/^## Tooth-tip chamfer spike (Phase 10, D-05)/,$p' bench/RESULTS.md \| ... \| grep -c '^\| teeth='` → 18; `grep -c '^**Verdict:** held'` → 1 | ✅ | ✅ green |
| 10-02-01 | 02 | 2 | REQ-tip-chamfer, REQ-tip-chamfer-capped | T-10-04 / T-10-05 / T-10-08 | One value is cut and printed (`model.py:261` reads `calc.tip_chamfer_effective`); every pre-v0.2 set replays byte-unchanged; CLI, API and form schema agree | integration + regression | `make test PYTEST_ARGS="tests/test_api.py tests/test_calc.py tests/test_model.py tests/test_cli.py tests/regression -q" && git diff --exit-code tests/regression/pre_v0_2.json`; `.venv/bin/spur info --tip-chamfer 3` → `(1.75, 36.75, ['Tip chamfer reduced to 1.75 mm to keep it above the pitch circle.'])`; `spur export --tip-chamfer 0.4` writes an `ISO-10303-21;` STEP | ✅ | ✅ green (`make verify` 455 passed on `8409322`; `info`/`export` re-run 2026-09-28) |
| 10-02-02 | 02 | 2 | REQ-tip-chamfer-capped | T-10-04 / T-10-05 / T-10-06 / T-10-07 | The cap is pinned at each limit and one step either side with its full warning string; the rounding contract; no other derived number moves; the probe shares `calc.spline_start` | unit (tdd) | `test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first` (`test_calc.py:616`, 16 collected cases incl. `print-precision-inside`), `:655`, `:670`, `:699`; `.venv/bin/python -c "import bench.tip_chamfer_spike as s, spur.calc as c; assert s.spline_start is c.spline_start"` | ✅ | ✅ green (post-review: `test_a_sub_print_precision_tip_chamfer_request_still_warns` `:632`, added by `54fe020` / `60d02f7`) |
| 10-03-01 | 03 | 3 | REQ-tip-chamfer | T-10-09 | The tip selector's exact count on 30 matrix rows and in the real chamfered pipeline; an empty selection is a `BuildError` (`model.py:353`), a 422 naming the defect, and a CLI export that stops and writes nothing | integration | `.venv/bin/python -m pytest tests/test_model.py --collect-only -q \| grep -c 'test_each_edge_selector_picks_exactly_its_own_edges\['` → 30; `test_model.py:243`, `:264`; `test_api.py:785`; `test_cli.py:188` | ✅ | ✅ green |
| 10-03-02 | 03 | 3 | REQ-tip-chamfer, REQ-tip-chamfer-capped | T-10-09 / T-10-10 / T-10-11 | Only the tip arcs change on the built solid (D-12); the proof goes red when the step is skipped (D-14); the flank boundary holds one step either side (D-04: 2.937 mm builds, 2.9875 mm fails) | kernel proof | `.venv/bin/python -m pytest tests/test_model.py -q -k "breaks_only_the_tip_arcs or proof_fails_when_the_tip_step or largest_tip_chamfer or kernel_fails_one_step_past"` — 6 passed in 8.83 s (2026-09-28) | ✅ | ✅ green |
| 10-04-01 | 04 | 4 | REQ-tip-chamfer-capped | T-10-12 / T-10-13 | The sweep file is the full cross product with each largest chamfer exactly on its limit; one chamfered set runs through the unchanged Phase 8 runner | unit + bench-tracer | `make test PYTEST_ARGS="tests/test_bench.py -q"` (`test_the_tip_chamfer_sweep_is_every_combination_d_06_names`, `test_bench.py:133`); `make bench.build SWEEP=<one-row file>` → 1 timed row | ✅ | ✅ green (`bench.build` re-run 2026-09-28) |
| 10-04-02 | 04 | 4 | REQ-tip-chamfer-capped | T-10-12 | Every 200-tooth row recorded, none marked `**NO**`; the heaviest row (14.87 s of 30 s) and the narrowed margin published and filed as must-debt | doc-grep | `sed -n '/^## Tooth-tip chamfer build and export time (Phase 10)/,$p' bench/RESULTS.md \| grep -cE '^\| teeth=200 '` → 9; `... \| grep -cE '\*\*NO\*\*'` → 0 | ✅ | ✅ green |
| 10-05-01 | 05 | 5 | REQ-tip-chamfer | T-10-15 / T-10-16 | README documents the field wherever parameters are described, names no size; its tip-chamfer example runs as a test | doc-grep + CLI | `make test PYTEST_ARGS="tests/test_cli.py tests/regression -q"` (`test_readme_export_examples_run`, `test_cli.py:81`); README-row digit check (one row, no digit beyond `0 = none`); `! git grep -nE '0\.1 ?[–-] ?0\.2' -- README.md src docs` | ✅ | ✅ green (all three re-run 2026-09-28) |
| 10-05-02 | 05 | 5 | REQ-tip-chamfer, REQ-tip-chamfer-capped | T-10-14 / T-10-15 | L29 appended, never edited; names `spline_start`, `TIP_CHAMFER_MARGIN`, D-04 and the spike; no sizing figure anywhere under `docs` | doc-grep | `git diff --numstat 277a98f -- docs/architecture/decision_log.md` → 0 deletions; L29 term grep → 9; `! git grep -nE '0\.1 ?[–-] ?0\.2' -- docs` | ✅ | ✅ green |
| 10-05-03 | 05 | 5 | REQ-tip-chamfer-capped | — | Debt record current (typing item says five; lead-in item filed with its INDEX row); the phase's final gate is green | doc-grep + full gate | `grep -c 'five' docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md` → 1; INDEX greps → 1/1; `make verify` → 453 passed / 99.28 s (10-05), 455 passed / 98–104 s after the review fixes | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No stubs, fixtures or framework installs were needed: every test the phase added lives in `tests/test_calc.py`, `tests/test_model.py`, `tests/test_api.py`, `tests/test_cli.py` and `tests/test_bench.py`, next to the Phase 7–9 tests it extends, and the 44-record regression replay (`tests/regression/test_pre_v0_2.py`) ran unmodified.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| A spike or sweep row over `SPUR_BUILD_TIMEOUT=30s` | REQ-tip-chamfer-capped | Halts for a human decision (D-07), never a silent lowering of the cap | Read the spike's verdict (`bench/RESULTS.md` § "Tooth-tip chamfer spike") and the sweep's Markdown rows (§ "Tooth-tip chamfer build and export time"); any `FAILED` verdict or `**NO**` row stops the phase. Done: verdict held, 18/18 and 9/9 rows inside, heaviest 15.90 s / 14.87 s — the gate never fired |
| No chamfer size presented as sourced guidance in help text, README or L29 (ROADMAP SC2, D-16) | REQ-tip-chamfer | The negative grep for the research-era figure is automated in the plans (0 hits at audit) but is not a committed test — a future edit that reintroduces a figure would not fail `make verify`; whether a sentence *reads* as a recommendation needs a human read | Read `README.md:158` (the row), `:202-212` (Geometry notes) and L29 (`decision_log.md:1045`); confirm the figure is described only as unsourced and no number is given as a convention. Done: verifier confirmed SC2 on 2026-09-28 (`10-VERIFICATION.md`); repo-wide grep 0 hits at audit |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (11/11)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (every task has one)
- [x] Wave 0 covers all MISSING references (0 missing at HEAD)
- [x] No watch-mode flags
- [x] Feedback latency < 60s — **not met literally**: `make verify` is 98–104 s warm at 455 tests; the quick command is 10.24 s. Accepted as-is, as Phase 9 did: the gate's cost is the CAD tests, and 10-04 records the wall time beside Phase 9's so the trend stays visible
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-09-28 by `/gsd-validate-phase 10` (Claude) against HEAD `8409322` — 0 gaps, 0 escalations, no tests generated (every requirement had a green named test from execution; the two post-review gaps — WR-01's untested warning and CR-01's untested warning *text* — were closed with full-string tests by the review loop in `54fe020` and `60d02f7` before this audit ran).

## Validation Audit 2026-09-28

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
