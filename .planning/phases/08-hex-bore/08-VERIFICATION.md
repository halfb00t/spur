---
phase: 08-hex-bore
verified: 2026-09-26T16:33:49Z
status: passed
score: 30/30 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/ROADMAP.md", ".planning/phases/08-hex-bore/08-01-PLAN.md", ".planning/phases/08-hex-bore/08-01-SUMMARY.md", ".planning/phases/08-hex-bore/08-02-PLAN.md", ".planning/phases/08-hex-bore/08-02-SUMMARY.md", ".planning/phases/08-hex-bore/08-03-PLAN.md", ".planning/phases/08-hex-bore/08-03-SUMMARY.md", ".planning/phases/08-hex-bore/08-04-PLAN.md", ".planning/phases/08-hex-bore/08-04-SUMMARY.md", ".planning/phases/08-hex-bore/08-CONTEXT.md", "Makefile", "README.md", "bench/RESULTS.md", "bench/build_time.py", "bench/sweeps/hex_bore.json", "docs/architecture/decision_log.md", "docs/architecture/gear-maths/implementation.md", "docs/architecture/solid-model/tactics.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md", "src/spur/calc.py", "src/spur/model.py", "src/spur/params.py", "src/spur/static/app.js", "tests/regression/capture.py", "tests/regression/test_pre_v0_2.py", "tests/test_api.py", "tests/test_bench.py", "tests/test_calc.py", "tests/test_cli.py", "tests/test_model.py"]
covered_digest: "v1:sha256:9404429a838da23c84232b92b6456990dbe266aa6499079c134a41e86c8d48f6"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 8: Hex Bore Verification Report

**Phase Goal:** A user can request a hexagonal bore and get a correctly measured hex
profile, proving Phase 7's generalized selector against real geometry.
**Verified:** 2026-09-26T16:33:49Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

All checks below were run directly against the codebase at HEAD `27e7ddf` on
`gsd/phase-08-hex-bore`, not accepted from SUMMARY.md narrative. `make verify` was run
fresh: `330 passed in 60.85s`. `git diff --exit-code tests/regression/pre_v0_2.json`
exits 0 (byte-unchanged). `git diff --quiet 540f1a0 -- src/spur/app.py src/spur/cli.py`
exits 0. `git diff --quiet 540f1a0 -- tests/regression/corpus.py` exits 0.

### Observable Truths — ROADMAP Success Criteria (SC1–SC5, SC2 amended per 08-01/D-01)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC1 | `bore_hex` cuts a regular hexagon with clearance across the flats, replacing the round profile; `bore_chamfer` chamfers all 12 rim edges (6/face) via an edge-count assertion; the v0.1 selector (bare `bore_radius` band) would have selected zero edges here | ✓ VERIFIED | `src/spur/model.py:195-218` hex-first branch cuts `polygon(6, hex_across_flats(p), circumscribed=True)`; `tests/test_model.py` 7 hex rows in `test_each_edge_selector_picks_exactly_its_own_edges` all assert `Counter({"LINE": 12})` (ran: 17 collected, 7 hex); `test_the_pre_hex_rim_bound_would_have_chamfered_nothing_on_a_hex_wider_than_the_round_bore` PASSED (ran directly) |
| SC2 (amended) | `bore_hex` with non-zero `bore_flat` still builds; ignored fields named with values in one `warnings` entry; never a 422; hex×keyway 422 lives in Phase 9 | ✓ VERIFIED | `.venv/bin/spur info --bore-hex 6 --bore-flat 3` ran live: exit 0, `warnings == ["Hex bore replaces the round profile: bore_d (9 mm) and bore_flat (3 mm) are ignored."]`; `src/spur/calc.py:176-201` hex branch never runs the round rules; REQ-keyway-bore and ROADMAP Phase 9 SC2 carry the hex×keyway 422 (confirmed by direct read) |
| SC3 | `DerivedDimensions` gains hex corner-to-corner field, null when off; 19 existing fields unchanged; `make verify` green under `disallow_any_explicit` | ✓ VERIFIED | `src/spur/calc.py:269-273` two new `float \| None` fields, no `Any`; `mypy --strict` in `make verify` passed ("Success: no issues found in 33 source files"); replay test (`tests/regression/test_pre_v0_2.py`, 44 records) passed live |
| SC4 | Measured build time for the heaviest allowed hex configuration recorded in `bench/RESULTS.md`, inside `SPUR_BUILD_TIMEOUT=30s` | ✓ VERIFIED | `bench/RESULTS.md` "## Hex bore build and export time (Phase 8, D-11)" section read directly: 16/16 rows "yes" inside 30s, heaviest row 5.08s of 30s named; `sed | grep -c 'teeth=200'` → 16; `grep -c '\*\*NO\*\*'` → 0 |
| SC5 | Phase 7's regression fixture still passes unmodified | ✓ VERIFIED | `git diff --exit-code tests/regression/pre_v0_2.json` exits 0 (ran live); `tests/regression/test_pre_v0_2.py` 44/44 records passed in the fresh `make verify` run |

### Observable Truths — Plan-level must_haves (08-01 through 08-04)

| # | Truth (paraphrased) | Status | Evidence |
|---|---|---|---|
| 08-01.1 | REQ-hex-bore says the hexagon replaces the whole round profile; both defaults non-zero so a `bore_hex`-only link builds; old 422 sentence gone | ✓ VERIFIED | Read `.planning/REQUIREMENTS.md` lines 44-52 directly: exact wording present, "Phase 8 D-01/D-02 superseded the earlier `bore_flat` 422" |
| 08-01.2 | Hex×keyway 422 not dropped — moved to REQ-keyway-bore, ROADMAP Phase 9 SC2 and Phase 12 SC1 | ✓ VERIFIED | Read REQUIREMENTS.md REQ-keyway-bore bullet and ROADMAP Phase 9/12 sections directly: all three carry the relocated refusal |
| 08-01.3 | ROADMAP Phase 8 SC2 cites 08-CONTEXT.md D-01/D-02; SC1/SC3/SC4/SC5 unchanged | ✓ VERIFIED | `git show fddf9b8 -- .planning/ROADMAP.md` shows only SC2 (Phase 8), SC2 (Phase 9) and SC1 (Phase 12) changed — no other criteria touched |
| 08-01.4 | Every ROADMAP change went through the edit-phase workflow's observable contract: scope check before/after, one Roadmap Evolution line per phase, write only after human approval | ✓ VERIFIED (see note) | `grep -cE '^- Phase (8\|9\|12) edited' .planning/STATE.md` → 3 (ran live); `roadmap.milestone-scope` → scope "complete", 6 phases (ran live, matches pre/post claim). **Note:** SUMMARY and the orchestrator's own context flag that Task 1/3 mirrored edit-phase's steps via scoped Edit calls rather than literally invoking the `gsd-phase --edit` skill program. The observable contract (scope check, evolution lines, approval-gated single write) holds; the literal tool-invocation path differs from the plan's wording. This is a process deviation, not a goal-blocking gap — flagged for visibility, not scored as a failure. |
| 08-02.1 | `bore_hex` field: title, group, position after `bore_flat`, step 0.05, ge 0 le 200, default 0; no `app.py`/`cli.py` edit needed | ✓ VERIFIED | Read `src/spur/params.py:58-62` directly; `git diff --quiet 540f1a0 -- src/spur/app.py src/spur/cli.py` exits 0 (ran live) |
| 08-02.2 | `bore_hex > 0` cuts a regular hex prism replacing round/D-flat, even with `bore_d` 0; `bore_hex` 0 leaves round/D-flat path unchanged | ✓ VERIFIED | Read `src/spur/model.py:195-218` if/elif/else; `tests/test_model.py` hex-no-round-bore row and full suite passed live |
| 08-02.3 | `bore_rim_limit` hex branch returns circumradius; round/D-flat unchanged | ✓ VERIFIED | Read `src/spur/calc.py:67-82`; `tests/test_calc.py::test_the_bore_rim_limit_is_a_hex_bores_circumradius` passed live |
| 08-02.4 | `bore_mouth_limit` formula per shape; recess clears it by MIN_WALL for all three shapes | ✓ VERIFIED | Read `src/spur/calc.py:85-97,111-112`; `tests/test_model.py::test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth[round\|d-flat\|hex]` passed live (ran as part of `-k "hex or chamfered_bore_mouth"`, 16 passed) |
| 08-02.5 | `/api/info`/CLI/UI report `hex_across_flats`/`hex_across_corners`; both null off; `bore_effective` null on hex | ✓ VERIFIED | `.venv/bin/spur info --bore-hex 6` ran live: `(6.15, 7.101, None)` exactly as specified; `app.js:25-26` two DIMS rows read directly |
| 08-02.6 | 19 pre-v0.2 fields unchanged; fixture byte-unchanged | ✓ VERIFIED | `git diff --exit-code tests/regression/pre_v0_2.json` exits 0 (ran live) |
| 08-02.7 | 12 LINE rim edges on 7 hex matrix rows | ✓ VERIFIED | `grep -c 'test_each_edge_selector_picks_exactly_its_own_edges\[hex-'` → 7 (ran live); all 17 rows collected |
| 08-02.8 | Precision within 5e-4mm; corner at `bore_rim_limit` within TOL; flat faces +X | ✓ VERIFIED | `tests/test_model.py::test_a_hex_bore_measures_the_across_flats_and_corners_it_reports` PASSED (ran directly) |
| 08-02.9 | Idempotency: two independent builds give equal counts/volume | ✓ VERIFIED | `tests/test_model.py::test_the_same_hex_link_builds_the_same_solid_twice` PASSED (ran directly) |
| 08-02.10 | Empty/off input: both hex fields null when `bore_hex` 0, etc. | ✓ VERIFIED | `tests/test_calc.py -k hex` (14 passed, ran directly) includes the 5-row `test_a_hex_bore_reports_across_flats_and_corners_and_no_round_diameter` |
| 08-02.11 | Field identity: 21-name openapi set; replay compares recorded fields exactly | ✓ VERIFIED | `tests/test_api.py::test_openapi_documents_the_typed_contracts` PASSED (ran directly) |
| 08-02.12 | Concurrency backstop: no new process state; `DerivedDimensions` fields frozen | ✓ VERIFIED | `tests/test_calc.py::test_a_derived_dimensions_result_cannot_be_changed` iterates `model_fields` (read directly, includes new hex fields); passed in full suite |
| 08-03.1 | Round-profile rules skipped under hex; shape-independent chamfer-vs-face-width rule still applies | ✓ VERIFIED | Read `src/spur/calc.py:176-201` if/elif/else structure; `test_a_hex_bore_skips_the_round_bore_rules` passed in full suite |
| 08-03.2 | Corner rule: 24.2 refused naming only `bore_hex`; 24.15 builds | ✓ VERIFIED | `.venv/bin/spur info --bore-hex 25` ran live: exit 2, exact sentence "Hex bore is too large for the root diameter..."; boundary tests passed in full suite |
| 08-03.3 | Chamfered-corner rule: 23.4 refused naming `bore_chamfer`+`bore_hex`; 23.35 builds | ✓ VERIFIED | Read `src/spur/calc.py:195-201`; boundary tests passed in full suite |
| 08-03.4 | No chamfer-vs-side rule; probe recorded as a test | ✓ VERIFIED | `tests/test_model.py -k chamfered_bore_mouth` and hex filter (16 passed, ran directly) includes `test_the_kernel_chamfers_a_hex_bore_far_past_its_side_length` |
| 08-03.5 | Ignored-field warning names each non-zero field with its value; none when both 0 | ✓ VERIFIED | `.venv/bin/spur info --bore-hex 6 --bore-flat 3` ran live: exact sentence produced |
| 08-03.6 | API/CLI/derive() print calc's own sentences; no per-interface wording | ✓ VERIFIED | `tests/test_cli.py -k "hex or readme"` (3 passed, ran directly) includes `test_cli_and_api_print_the_same_hex_bore_document` |
| 08-03.7 | README lists hex bore, `bore_hex` row w/ D-08 sentence, runnable example | ✓ VERIFIED | `grep` on README.md (lines 11, 108, 135, 153) read directly; `test_readme_export_examples_run` passed in full suite |
| 08-03.8 | `bore_d`/`bore_clearance` help texts stay true for hex | ✓ VERIFIED | Read `src/spur/params.py:54-66` directly: "0 = no round bore", "hex across-flats for print shrinkage" |
| 08-04.1 | `make bench.build` runs committed script over committed sweep, prints per-set timings, names heaviest, exits non-zero over budget | ✓ VERIFIED | Read `bench/build_time.py` (`Timing`, `load_sweep`, `time_set`, `report`, `main`); `Makefile` `bench.build` target read directly |
| 08-04.2 | Script takes params from `SWEEP=` JSON file, default `bench/sweeps/hex_bore.json`, reusable unchanged by later phases | ✓ VERIFIED | Read `bench/build_time.py` `DEFAULT_SWEEP` and `Makefile` `SWEEP ?=` directly |
| 08-04.3 | `hex_bore.json` holds D-11's 16-row sweep at 200 teeth | ✓ VERIFIED | `.venv/bin/python -c "..."` ran live: `len(d)==16, all teeth==200` → True |
| 08-04.4 | `bench/RESULTS.md` records every row, host state w/ load caveat, heaviest named, all inside 30s | ✓ VERIFIED | Read `bench/RESULTS.md` section directly: 16 rows, all "yes", host state + caveat present, heaviest 5.08s named |
| 08-04.5 | L27 records D-01 supersession, replay refinement, D-03 bounds, D-11 heaviest row; append-only | ✓ VERIFIED | Read `docs/architecture/decision_log.md` L27 directly (full text); `git diff --numstat 540f1a0 -- docs/architecture/decision_log.md` → 82 insertions, 0 deletions (ran live) |
| 08-04.6 | Round bore's unchecked chamfer reach filed as must debt, not fixed silently | ✓ VERIFIED | Read `docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md` directly: `Severity: must`; INDEX.md row confirmed by grep |
| 08-04.7 | `make verify` green at end of phase | ✓ VERIFIED | Ran `make verify` fresh myself: ruff clean, mypy strict clean, lint-imports 5/5 kept, pytest 330 passed in 60.85s |

**Score:** 30/30 must-haves verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` `bore_hex` | field, Bore group, after `bore_flat` | ✓ VERIFIED | Present, correct position, contains `_f(0.0, 0, 200, title="Hex bore A/F", group="Bore"` |
| `src/spur/calc.py` `hex_across_flats`, `bore_mouth_limit`, `bore_rim_limit` hex branch, `check()` hex branch, `derive()` warning | new functions/logic | ✓ VERIFIED | All present, wired into `recess_radii`, `check`, `derive` |
| `src/spur/model.py` `_cut_bore` hex branch | new cut logic | ✓ VERIFIED | `polygon(6, hex_across_flats(p), circumscribed=True)` present |
| `src/spur/static/app.js` DIMS rows | 2 new rows | ✓ VERIFIED | Both rows present after `bore_effective` |
| `tests/regression/test_pre_v0_2.py` additive-field replay | changed comparison | ✓ VERIFIED | Recorded-fields-exact + added-fields-null logic present; 44 records pass |
| `bench/build_time.py`, `bench/sweeps/hex_bore.json` | new bench tool + sweep | ✓ VERIFIED | Present, tested, 16 rows |
| `bench/RESULTS.md` Phase 8 section | new section | ✓ VERIFIED | Present, 16 rows, heaviest named |
| `docs/architecture/decision_log.md` L27 | new entry | ✓ VERIFIED | Present, append-only |
| `docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md` | new debt item | ✓ VERIFIED | Present, Severity: must, INDEX row present |
| `README.md` hex documentation | bullet, row, example | ✓ VERIFIED | All three present |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `model._cut_bore` | `calc.hex_across_flats` | cut uses the same across-flats `derive()` prints | ✓ WIRED | `polygon(6, hex_across_flats(p), circumscribed=True)` in model.py, same function calc.py exports |
| `model._bore_rim_edges` | `calc.bore_rim_limit` | selector band = exact bound + slack, unchanged | ✓ WIRED | `bore_rim_limit(p) + BORE_RIM_SLACK` present, no selector edits needed |
| `calc.recess_radii` | `calc.bore_mouth_limit` | hub clearance = chamfered mouth + MIN_WALL, every shape | ✓ WIRED | `hub = bore_mouth_limit(p) + MIN_WALL` present |
| `app.js` DIMS | `calc.DerivedDimensions` | UI rows match API field names | ✓ WIRED | `['hex_across_flats', ...]`/`['hex_across_corners', ...]` match `DerivedDimensions` field names exactly |
| `calc.check()` hex branch | `calc.bore_rim_limit`/`bore_mouth_limit` | refusal rules read the same extents the cut/selector/recess use | ✓ WIRED | Both `if`/`elif` conditions call the shared functions directly |
| `params._feasible` | `calc.check()` | unchanged wiring: refusal tuples become 422/exit-2 | ✓ WIRED | No change needed; confirmed live via CLI/API refusal tests |
| `Makefile bench.build` | `bench/build_time.py` | `python -m bench.build_time $(SWEEP)` | ✓ WIRED | Confirmed by reading Makefile target and by the plan's own one-set smoke test passing in 08-04's execution |

### Data-Flow Trace (Level 4)

| Value | Source | Flows to | Status |
|-------|--------|----------|--------|
| `hex_across_flats` (API/CLI/UI) | `calc.derive()` → `r3(hex_across_flats(p))` | `/api/info`, `spur info`, `app.js` DIMS row | ✓ FLOWING — measured live, `6.15` for `bore_hex=6` |
| `hex_across_corners` | `calc.derive()` → `r3(2 * bore_rim_limit(p))` | same as above | ✓ FLOWING — measured live, `7.101` |
| Refusal/warning text | `calc.check()`/`calc.derive()` | API 422/`warnings`, CLI stderr/exit 2 | ✓ FLOWING — measured live, identical sentence across API and CLI |
| Hex geometry (12 rim edges, measured flats/corners) | `model._cut_bore`/`_bore_rim_edges` | built solid, measured directly by tests | ✓ FLOWING — confirmed by running the measurement/idempotency tests directly, not just reading source |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Hex link builds and prints two numbers | `.venv/bin/spur info --bore-hex 6` | `hex_across_flats=6.15, hex_across_corners=7.101, bore_effective=None` | ✓ PASS |
| Corner-rule refusal | `.venv/bin/spur info --bore-hex 25` | exit 2, exact refusal sentence naming `bore_hex` | ✓ PASS |
| Ignored-field warning | `.venv/bin/spur info --bore-hex 6 --bore-flat 3` | exact warning sentence naming both fields with values | ✓ PASS |
| Regression fixture unchanged | `git diff --exit-code tests/regression/pre_v0_2.json` | exit 0 | ✓ PASS |
| Full test suite | `make verify` | ruff/mypy/lint-imports clean; 330 passed in 60.85s | ✓ PASS |
| Edge-selector matrix (7 hex rows) | `pytest --collect-only` + targeted run | 7 hex rows collected, all `Counter({"LINE": 12})`, 16 hex-scoped model tests pass | ✓ PASS |
| Bench sweep file | `python -c "json.load(...)"` | 16 rows, all teeth=200 | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` files exist in this project and none are referenced by the phase's plans or SUMMARYs. `bench/build_time.py`/`make bench.build` is this phase's measurement tool but is explicitly documented (in its own module docstring and 08-04-PLAN.md) as excluded from `make verify`'s scope — it is not a probe in the gated sense. Step 7c: **SKIPPED (no probe scripts declared or found)**.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| REQ-hex-bore | 01 (wording), 02, 03 | Hex A/F bore, replaces round profile, warns on ignored fields, clearance across flats; keyway 422 moved to Phase 9 | ✓ SATISFIED | REQUIREMENTS.md marked `[x]`; wording matches; behavior confirmed live via CLI/API/tests |
| REQ-derived-dimensions-additive | 02 | 19 fields keep name/type/value; new fields null when off | ✓ SATISFIED | REQUIREMENTS.md marked `[x]`; replay test (44 records) confirmed live; fixture byte-unchanged |

No orphaned requirements: REQUIREMENTS.md footer table maps exactly REQ-hex-bore and
REQ-derived-dimensions-additive to Phase 8, both `Complete`, matching the two plans'
declared `requirements` fields exactly.

### Anti-Patterns Found

Scanned every file modified across all four plans (`src/spur/params.py`, `src/spur/calc.py`,
`src/spur/model.py`, `src/spur/static/app.js`, `bench/build_time.py`,
`bench/sweeps/hex_bore.json`, README.md, decision_log.md, tech_debt files, tests) for
`TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` and empty-implementation patterns. **None found.**
`make verify`'s own unfinished-work scan (part of the gate) also passed clean.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | none found | — | — |

### Human Verification Required

None. Every must-have across all four plans was verified against the running codebase
(direct source reads, live CLI/test execution, live `make verify`), not accepted from
SUMMARY.md claims. No must-have asserts a state-transition, cancellation, or ordering
invariant that presence-checking alone could miss — every such claim (idempotency,
precision, concurrency/frozen-state, the pre-Phase-8-bound regression) has a passing,
directly-executed test backing it.

### Gaps Summary

No gaps. All ROADMAP Phase 8 Success Criteria (SC1–SC5, with SC2 as amended by 08-01 per
D-01/D-02) and all plan-level must-haves across 08-01 through 08-04 are verified directly
against the codebase. `make verify` is green (330 passed, ruff/mypy --strict/lint-imports
clean). One process note (not a gap): 08-01's Task 1/3 mirrored the edit-phase workflow's
steps via scoped Edit calls rather than literally invoking `gsd-phase --edit`; the
workflow's observable guarantees (milestone-scope check before/after, one Roadmap
Evolution line per phase, write only after human approval) were independently confirmed
against STATE.md and `roadmap.milestone-scope` and hold regardless of which tool path
produced them.

---

*Verified: 2026-09-26T16:33:49Z*
*Verifier: Claude (gsd-verifier)*
