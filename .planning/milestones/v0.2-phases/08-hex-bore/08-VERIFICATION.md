---
phase: 08-hex-bore
verified: 2026-09-27T00:00:00Z
status: passed
score: 30/30 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/ROADMAP.md", ".planning/phases/08-hex-bore/08-01-PLAN.md", ".planning/phases/08-hex-bore/08-01-SUMMARY.md", ".planning/phases/08-hex-bore/08-02-PLAN.md", ".planning/phases/08-hex-bore/08-02-SUMMARY.md", ".planning/phases/08-hex-bore/08-03-PLAN.md", ".planning/phases/08-hex-bore/08-03-SUMMARY.md", ".planning/phases/08-hex-bore/08-04-PLAN.md", ".planning/phases/08-hex-bore/08-04-SUMMARY.md", ".planning/phases/08-hex-bore/08-CONTEXT.md", ".planning/phases/08-hex-bore/08-REVIEW.md", ".planning/phases/08-hex-bore/08-SECURITY.md", "Makefile", "README.md", "bench/RESULTS.md", "bench/build_time.py", "bench/sweeps/hex_bore.json", "docs/architecture/decision_log.md", "docs/architecture/gear-maths/implementation.md", "docs/architecture/solid-model/tactics.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md", "src/spur/calc.py", "src/spur/model.py", "src/spur/params.py", "src/spur/static/app.js", "tests/regression/capture.py", "tests/regression/test_pre_v0_2.py", "tests/test_api.py", "tests/test_bench.py", "tests/test_calc.py", "tests/test_cli.py", "tests/test_model.py"]
covered_digest: "v1:sha256:93f6803c62fdb0924ec0dbfaeda3754eac42be4b85ff791f1998f76ecc4f4baf"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 30/30
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 8: Hex Bore Verification Report

**Phase Goal:** A user can request a hexagonal bore and get a correctly measured hex
profile, proving Phase 7's generalized selector against real geometry.
**Verified:** 2026-09-27T00:00:00Z
**Status:** passed
**Re-verification:** Yes — after `phase.complete` touched only ROADMAP.md's Phase 8
completion checkbox, which invalidated the prior report's `covered_digest`. No source,
test, plan, or summary file changed. `git diff --stat 27e7ddf..HEAD -- . ':!.planning'`
is empty; inside `.planning/` only `ROADMAP.md` (Phase 8 checkbox `[ ]` → `[x]`),
`STATE.md`, `PROJECT.md`, plus new `08-REVIEW.md` and `08-SECURITY.md` changed.

## Goal Achievement

This is a full re-verification, not a rubber stamp. Every truth below was re-checked
directly against the current tree (tree `bb9ddb9`), not accepted from the prior report
or from SUMMARY.md narrative.

- `make verify` run fresh: ruff clean, mypy `--strict` clean ("Success: no issues found
  in 33 source files" — surfaced within the run), import-boundary contracts 5/5 kept,
  `330 passed in 66.33s`.
- `git diff --exit-code tests/regression/pre_v0_2.json` exits 0 (byte-unchanged).
- `git diff --stat 27e7ddf..HEAD -- . ':!.planning'` is empty (no source/test file
  changed since the prior verification).

### Observable Truths — ROADMAP Success Criteria (SC1–SC5, SC2 amended per 08-01/D-01)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC1 | `bore_hex` cuts a regular hexagon with clearance across the flats, replacing the round profile; `bore_chamfer` chamfers all 12 rim edges (6/face) via an edge-count assertion; the v0.1 selector would have selected zero edges here | ✓ VERIFIED | Read `src/spur/model.py:195-218` directly: hex-first branch cuts `polygon(6, hex_across_flats(p), circumscribed=True)`. Ran `tests/test_model.py -k hex` live: 14 passed, including all 7 hex rows of `test_each_edge_selector_picks_exactly_its_own_edges` and `test_the_pre_hex_rim_bound_would_have_chamfered_nothing_on_a_hex_wider_than_the_round_bore` |
| SC2 (amended) | `bore_hex` with non-zero `bore_flat` still builds; ignored fields named with values in one `warnings` entry; never a 422; hex×keyway 422 lives in Phase 9 | ✓ VERIFIED | Ran `spur info --bore-hex 6 --bore-flat 3` live: exit 0, `warnings == ["Hex bore replaces the round profile: bore_d (9 mm) and bore_flat (3 mm) are ignored."]`. Read `src/spur/calc.py:176-201` directly: hex branch never runs the round rules. `.planning/ROADMAP.md` Phase 9 SC2 / Phase 12 SC1 read directly: both still carry the hex×keyway 422 |
| SC3 | `DerivedDimensions` gains hex corner-to-corner field, null when off; 19 existing fields unchanged; `make verify` green under `disallow_any_explicit` | ✓ VERIFIED | Read `src/spur/calc.py` field block directly: two new `float \| None` fields, no `Any`. `mypy --strict` passed in the fresh `make verify` run. `tests/regression/test_pre_v0_2.py` (44 records) passed in the fresh full-suite run |
| SC4 | Measured build time for the heaviest allowed hex configuration recorded in `bench/RESULTS.md`, inside `SPUR_BUILD_TIMEOUT=30s` | ✓ VERIFIED | Read `bench/RESULTS.md` "Hex bore build and export time (Phase 8, D-11)" section directly: 16 rows recorded, `grep -c '**NO**' bench/RESULTS.md` → 0 (ran live), heaviest row 5.08s of 30s named |
| SC5 | Phase 7's regression fixture still passes unmodified | ✓ VERIFIED | `git diff --exit-code tests/regression/pre_v0_2.json` exits 0 (ran live); the fixture's 44 records passed inside the fresh `make verify` run |

### Observable Truths — Plan-level must_haves (08-01 through 08-04)

| # | Truth (paraphrased) | Status | Evidence |
|---|---|---|---|
| 08-01.1 | REQ-hex-bore says the hexagon replaces the whole round profile; both defaults non-zero so a `bore_hex`-only link builds; old 422 sentence gone | ✓ VERIFIED | Read `.planning/REQUIREMENTS.md` REQ-hex-bore block directly (current tree): still carries the D-01/D-02 wording, `[x]` complete |
| 08-01.2 | Hex×keyway 422 not dropped — moved to REQ-keyway-bore, ROADMAP Phase 9 SC2 and Phase 12 SC1 | ✓ VERIFIED | Read REQUIREMENTS.md REQ-keyway-bore bullet (line 45, "delivered with the keyway fields") and ROADMAP Phase 9/12 sections directly: all three still carry the relocated refusal |
| 08-01.3 | ROADMAP Phase 8 SC2 cites 08-CONTEXT.md D-01/D-02; SC1/SC3/SC4/SC5 unchanged | ✓ VERIFIED | Read the current ROADMAP.md Phase 8 section directly: SC2 text matches the amended wording; the only diff since the prior verified commit (`git diff 27e7ddf..HEAD -- .planning/ROADMAP.md`) is the completion checkbox line, confirming SC1–SC5 text is unchanged |
| 08-01.4 | Every ROADMAP change went through the edit-phase workflow's observable contract | ✓ VERIFIED (see note) | `grep -cE '^- Phase (8\|9\|12) edited' .planning/STATE.md` → 3 (ran live, unchanged from prior run). Process note carried forward: 08-01's Task 1/3 mirrored edit-phase's steps via scoped Edit calls rather than literally invoking `gsd-phase --edit`; the observable contract (scope check, evolution lines, approval-gated write) holds — not a goal-blocking gap |
| 08-02.1 | `bore_hex` field: title, group, position after `bore_flat`, step 0.05, ge 0 le 200, default 0; no `app.py`/`cli.py` edit needed | ✓ VERIFIED | Read `src/spur/params.py:58-62` directly: matches exactly |
| 08-02.2 | `bore_hex > 0` cuts a regular hex prism replacing round/D-flat, even with `bore_d` 0; `bore_hex` 0 leaves round/D-flat path unchanged | ✓ VERIFIED | Read `src/spur/model.py:195-218` if/elif/else directly; ran the hex-scoped model tests live (14 passed) |
| 08-02.3 | `bore_rim_limit` hex branch returns circumradius; round/D-flat unchanged | ✓ VERIFIED | Read `src/spur/calc.py:65-81` directly: `hex_across_flats(p) / math.sqrt(3)` |
| 08-02.4 | `bore_mouth_limit` formula per shape; recess clears it by MIN_WALL for all three shapes | ✓ VERIFIED | Read `src/spur/calc.py:84-96` directly; ran `test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth[hex]` live (passed, part of the 14-test hex run) |
| 08-02.5 | `/api/info`/CLI/UI report `hex_across_flats`/`hex_across_corners`; both null off; `bore_effective` null on hex | ✓ VERIFIED | Ran `spur info --bore-hex 6` live: `hex_across_flats: 6.15, hex_across_corners: 7.101, bore_effective: null` exactly. Read `src/spur/static/app.js:25-26` directly: both DIMS rows present |
| 08-02.6 | 19 pre-v0.2 fields unchanged; fixture byte-unchanged | ✓ VERIFIED | `git diff --exit-code tests/regression/pre_v0_2.json` exits 0 (ran live) |
| 08-02.7 | 12 LINE rim edges on 7 hex matrix rows | ✓ VERIFIED | `pytest tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges --collect-only -q \| grep -c hex` → 7 (ran live); all 7 hex rows PASSED in the live run above |
| 08-02.8 | Precision within 5e-4mm; corner at `bore_rim_limit` within TOL; flat faces +X | ✓ VERIFIED | `test_a_hex_bore_measures_the_across_flats_and_corners_it_reports` PASSED (ran directly this session) |
| 08-02.9 | Idempotency: two independent builds give equal counts/volume | ✓ VERIFIED | `test_the_same_hex_link_builds_the_same_solid_twice` PASSED (ran directly this session) |
| 08-02.10 | Empty/off input: both hex fields null when `bore_hex` 0, etc. | ✓ VERIFIED | Covered by the fresh full-suite run of `tests/test_calc.py` (part of the 330-pass run) |
| 08-02.11 | Field identity: 21-name openapi set; replay compares recorded fields exactly | ✓ VERIFIED | `pytest tests/test_api.py -k "hex or openapi"` ran live: 5 passed |
| 08-02.12 | Concurrency backstop: no new process state; `DerivedDimensions` fields frozen | ✓ VERIFIED | Covered by the fresh full-suite run of `tests/test_calc.py` (part of the 330-pass run) |
| 08-03.1 | Round-profile rules skipped under hex; shape-independent chamfer-vs-face-width rule still applies | ✓ VERIFIED | Read `src/spur/calc.py:176-201` if/elif/else directly this session |
| 08-03.2 | Corner rule: 24.2 refused naming only `bore_hex`; 24.15 builds | ✓ VERIFIED | Ran live this session: `spur info --bore-hex 25` → exit 2, "Hex bore is too large for the root diameter... reduce bore_hex."; `spur info --bore-hex 24.15 --bore-chamfer 0` → builds (200 root, MIN_WALL boundary) |
| 08-03.3 | Chamfered-corner rule: 23.4 refused naming `bore_chamfer`+`bore_hex`; 23.35 builds | ✓ VERIFIED | Ran live this session: `spur info --bore-hex 23.4` (default chamfer 0.4) → exit 2, "Bore chamfer is too large for this hex bore... reduce bore_chamfer or bore_hex."; `spur info --bore-hex 23.35` → builds |
| 08-03.4 | No chamfer-vs-side rule; probe recorded as a test | ✓ VERIFIED | `tests/test_model.py -k hex` (ran live, 14 passed) includes `test_the_kernel_chamfers_a_hex_bore_far_past_its_side_length` |
| 08-03.5 | Ignored-field warning names each non-zero field with its value; none when both 0 | ✓ VERIFIED | Ran live this session: `spur info --bore-hex 6 --bore-flat 3` → exact sentence naming both fields with their values |
| 08-03.6 | API/CLI/derive() print calc's own sentences; no per-interface wording | ✓ VERIFIED | Covered by the fresh full-suite run of `tests/test_cli.py` (part of the 330-pass run) |
| 08-03.7 | README lists hex bore, `bore_hex` row w/ D-08 sentence, runnable example | ✓ VERIFIED | `grep -n "bore_hex\|hex bore" README.md` ran live this session: lines 11, 108, 135, 153 present; README example test covered by the fresh full-suite run |
| 08-03.8 | `bore_d`/`bore_clearance` help texts stay true for hex | ✓ VERIFIED | Read `src/spur/params.py:54-66` directly this session: "0 = no round bore", "hex across-flats for print shrinkage" |
| 08-04.1 | `make bench.build` runs committed script over committed sweep, prints per-set timings, names heaviest, exits non-zero over budget | ✓ VERIFIED | Read `bench/build_time.py` and `Makefile` `bench.build` target directly this session |
| 08-04.2 | Script takes params from `SWEEP=` JSON file, default `bench/sweeps/hex_bore.json`, reusable unchanged by later phases | ✓ VERIFIED | Read `bench/build_time.py` `DEFAULT_SWEEP` and `Makefile` `SWEEP ?=` directly this session |
| 08-04.3 | `hex_bore.json` holds D-11's 16-row sweep at 200 teeth | ✓ VERIFIED | `python -c "json.load(...)"` ran live this session: 16 rows, all `teeth==200` |
| 08-04.4 | `bench/RESULTS.md` records every row, host state w/ load caveat, heaviest named, all inside 30s | ✓ VERIFIED | Read `bench/RESULTS.md` section directly this session: 16 rows, 0 "**NO**" matches |
| 08-04.5 | L27 records D-01 supersession, replay refinement, D-03 bounds, D-11 heaviest row; append-only | ✓ VERIFIED | Read `docs/architecture/decision_log.md` L27 directly this session (full text present) |
| 08-04.6 | Round bore's unchecked chamfer reach filed as must debt, not fixed silently | ✓ VERIFIED | Read `docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md` directly this session: `Severity: must`, `Status: active`; INDEX.md row confirmed by grep |
| 08-04.7 | `make verify` green at end of phase | ✓ VERIFIED | Ran `make verify` fresh myself this session: ruff clean, mypy strict clean, lint-imports 5/5 kept, pytest 330 passed in 66.33s |

**Score:** 30/30 must-haves verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` `bore_hex` | field, Bore group, after `bore_flat` | ✓ VERIFIED | Present, correct position, read directly this session |
| `src/spur/calc.py` `hex_across_flats`, `bore_mouth_limit`, `bore_rim_limit` hex branch, `check()` hex branch, `derive()` warning | new functions/logic | ✓ VERIFIED | All present, wired into `recess_radii`, `check`, `derive` — read directly this session |
| `src/spur/model.py` `_cut_bore` hex branch | new cut logic | ✓ VERIFIED | `polygon(6, hex_across_flats(p), circumscribed=True)` present, read directly this session |
| `src/spur/static/app.js` DIMS rows | 2 new rows | ✓ VERIFIED | Both rows present after `bore_effective`, read directly this session |
| `tests/regression/test_pre_v0_2.py` additive-field replay | changed comparison | ✓ VERIFIED | Recorded-fields-exact + added-fields-null logic present, read directly this session; 44 records pass in the fresh full-suite run |
| `bench/build_time.py`, `bench/sweeps/hex_bore.json` | new bench tool + sweep | ✓ VERIFIED | Present, tested live, 16 rows confirmed this session |
| `bench/RESULTS.md` Phase 8 section | new section | ✓ VERIFIED | Present, 16 rows, heaviest named, read directly this session |
| `docs/architecture/decision_log.md` L27 | new entry | ✓ VERIFIED | Present, append-only, read directly this session |
| `docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md` | new debt item | ✓ VERIFIED | Present, Severity: must, INDEX row present, read directly this session |
| `README.md` hex documentation | bullet, row, example | ✓ VERIFIED | All three present, read directly this session |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `model._cut_bore` | `calc.hex_across_flats` | cut uses the same across-flats `derive()` prints | ✓ WIRED | `polygon(6, hex_across_flats(p), circumscribed=True)` in model.py, same function calc.py exports — confirmed by direct read this session |
| `model._bore_rim_edges` | `calc.bore_rim_limit` | selector band = exact bound + slack, unchanged | ✓ WIRED | `bore_rim_limit(p) + BORE_RIM_SLACK` present |
| `calc.recess_radii` | `calc.bore_mouth_limit` | hub clearance = chamfered mouth + MIN_WALL, every shape | ✓ WIRED | `hub = bore_mouth_limit(p) + MIN_WALL` present |
| `app.js` DIMS | `calc.DerivedDimensions` | UI rows match API field names | ✓ WIRED | `['hex_across_flats', ...]`/`['hex_across_corners', ...]` match `DerivedDimensions` field names exactly |
| `calc.check()` hex branch | `calc.bore_rim_limit`/`bore_mouth_limit` | refusal rules read the same extents the cut/selector/recess use | ✓ WIRED | Both `if`/`elif` conditions call the shared functions directly, confirmed this session |
| `params._feasible` | `calc.check()` | unchanged wiring: refusal tuples become 422/exit-2 | ✓ WIRED | Confirmed live this session via `spur info --bore-hex 25`/`23.4` exit-2 refusals |
| `Makefile bench.build` | `bench/build_time.py` | `python -m bench.build_time $(SWEEP)` | ✓ WIRED | Confirmed by reading the Makefile target this session |

### Data-Flow Trace (Level 4)

| Value | Source | Flows to | Status |
|-------|--------|----------|--------|
| `hex_across_flats` (API/CLI/UI) | `calc.derive()` → `r3(hex_across_flats(p))` | `/api/info`, `spur info`, `app.js` DIMS row | ✓ FLOWING — measured live this session, `6.15` for `bore_hex=6` |
| `hex_across_corners` | `calc.derive()` → `r3(2 * bore_rim_limit(p))` | same as above | ✓ FLOWING — measured live this session, `7.101` |
| Refusal/warning text | `calc.check()`/`calc.derive()` | API 422/`warnings`, CLI stderr/exit 2 | ✓ FLOWING — measured live this session at three boundary points (24.15/25, 23.35/23.4, ignored-field warning) |
| Hex geometry (12 rim edges, measured flats/corners) | `model._cut_bore`/`_bore_rim_edges` | built solid, measured directly by tests | ✓ FLOWING — confirmed by running the measurement/idempotency tests live this session |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Hex link builds and prints two numbers | `spur info --bore-hex 6` | `hex_across_flats=6.15, hex_across_corners=7.101, bore_effective=null` | ✓ PASS |
| Ignored-field warning | `spur info --bore-hex 6 --bore-flat 3` | exact warning sentence naming both fields with values | ✓ PASS |
| Corner-rule refusal | `spur info --bore-hex 25` | exit 2, "Hex bore is too large for the root diameter... reduce bore_hex." | ✓ PASS |
| Corner-rule boundary builds | `spur info --bore-hex 24.15 --bore-chamfer 0` | builds (no error) | ✓ PASS |
| Chamfered-corner refusal | `spur info --bore-hex 23.4` (default chamfer 0.4) | exit 2, "Bore chamfer is too large for this hex bore... reduce bore_chamfer or bore_hex." | ✓ PASS |
| Chamfered-corner boundary builds | `spur info --bore-hex 23.35` | builds (no error) | ✓ PASS |
| Regression fixture unchanged | `git diff --exit-code tests/regression/pre_v0_2.json` | exit 0 | ✓ PASS |
| Full test suite | `make verify` | ruff/mypy/lint-imports clean; 330 passed in 66.33s | ✓ PASS |
| Edge-selector matrix (7 hex rows) | `pytest --collect-only` + targeted run | 7 hex rows collected and PASSED, 14 hex-scoped model tests pass | ✓ PASS |
| Bench sweep file | `python -c "json.load(...)"` | 16 rows, all teeth=200 | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` files exist in this project and none are referenced by the
phase's plans or SUMMARYs (confirmed by `find` this session: no matches). `bench/build_time.py`
is this phase's measurement tool but is explicitly documented as excluded from `make verify`'s
scope — not a probe in the gated sense. Step 7c: **SKIPPED (no probe scripts declared or
found)**.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| REQ-hex-bore | 01 (wording), 02, 03, 04 | Hex A/F bore, replaces round profile, warns on ignored fields, clearance across flats; keyway 422 moved to Phase 9 | ✓ SATISFIED | REQUIREMENTS.md marked `[x]`, footer table maps it to "Phase 8, Complete" (read directly this session); behavior confirmed live via CLI/tests |
| REQ-derived-dimensions-additive | 02, 04 | 19 fields keep name/type/value; new fields null when off | ✓ SATISFIED | REQUIREMENTS.md marked `[x]`, footer table maps it to "Phase 8, Complete" (read directly this session); replay test (44 records) passed in the fresh full-suite run; fixture byte-unchanged |

No orphaned requirements: the REQUIREMENTS.md footer table maps exactly REQ-hex-bore and
REQ-derived-dimensions-additive to Phase 8 (both `Complete`), matching the union of the four
plans' declared `requirements` fields exactly (checked directly this session:
`grep -n "requirements:" .planning/phases/08-hex-bore/*-PLAN.md`).

### Anti-Patterns Found

Scanned every file modified across all four plans (`src/spur/params.py`, `src/spur/calc.py`,
`src/spur/model.py`, `src/spur/static/app.js`, `bench/build_time.py`,
`bench/sweeps/hex_bore.json`, README.md, decision_log.md, tech_debt files, tests) for
`TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` — ran live this session, **none found** (grep exit
code 1). `make verify`'s own unfinished-work scan (part of the gate) also passed clean in the
fresh run.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | none found | — | — |

### Human Verification Required

None. Every must-have across all four plans was re-verified this session against the running
codebase (direct source reads, live CLI/test execution, live `make verify`) — none accepted
from the prior VERIFICATION.md or from SUMMARY.md claims alone. No must-have asserts a
state-transition, cancellation, or ordering invariant that presence-checking alone could miss —
every such claim (idempotency, precision, concurrency/frozen-state, the pre-Phase-8-bound
regression) has a passing, directly-executed test backing it, run live this session.

### Gaps Summary

No gaps. This re-verification confirms the prior `passed` result still holds against the
current tree: `git diff --stat 27e7ddf..HEAD -- . ':!.planning'` is empty (no source, test,
plan, or summary file changed since the prior verification), the only `.planning/` change of
substance is the Phase 8 ROADMAP checkbox flip caused by `phase.complete`, and `make verify` is
green (330 passed, ruff/mypy --strict/lint-imports clean) freshly run. All ROADMAP Phase 8
Success Criteria (SC1–SC5, SC2 as amended by 08-01 per D-01/D-02) and all plan-level must-haves
across 08-01 through 08-04 were independently re-confirmed by direct reads and live command
execution in this session, not carried forward on trust. One process note (not a gap, carried
forward from the prior report): 08-01's Task 1/3 mirrored the edit-phase workflow's steps via
scoped Edit calls rather than literally invoking `gsd-phase --edit`; the workflow's observable
guarantees (milestone-scope check before/after, one Roadmap Evolution line per phase, write only
after human approval) were independently confirmed against STATE.md and hold regardless of
which tool path produced them. No regressions found relative to the prior verification.

---

*Verified: 2026-09-27T00:00:00Z*
*Verifier: Claude (gsd-verifier)*
