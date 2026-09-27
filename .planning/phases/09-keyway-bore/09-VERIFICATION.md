---
phase: 09-keyway-bore
verified: 2026-09-27T00:00:00Z
status: passed
score: 12/12 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/ROADMAP.md", ".planning/phases/09-keyway-bore/09-01-PLAN.md", ".planning/phases/09-keyway-bore/09-01-SUMMARY.md", ".planning/phases/09-keyway-bore/09-02-PLAN.md", ".planning/phases/09-keyway-bore/09-02-SUMMARY.md", ".planning/phases/09-keyway-bore/09-03-PLAN.md", ".planning/phases/09-keyway-bore/09-03-SUMMARY.md", ".planning/phases/09-keyway-bore/09-04-PLAN.md", ".planning/phases/09-keyway-bore/09-04-SUMMARY.md", ".planning/phases/09-keyway-bore/09-05-PLAN.md", ".planning/phases/09-keyway-bore/09-05-SUMMARY.md", "README.md", "bench/RESULTS.md", "bench/sweeps/keyway_bore.json", "docs/architecture/decision_log.md", "docs/architecture/gear-maths/implementation.md", "docs/architecture/solid-model/tactics.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/resolved/2026-09-26-round-bore-chamfer-reach-is-not-checked.md", "src/spur/calc.py", "src/spur/model.py", "src/spur/params.py", "src/spur/static/app.js", "tests/test_api.py", "tests/test_bench.py", "tests/test_calc.py", "tests/test_cli.py", "tests/test_model.py"]
covered_digest: "v1:sha256:ca8e219318790bf9ff905ae992cdb3cd70d72823af87181f9cc9d45dbc2ff765"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 9: Keyway Bore Verification Report

**Phase Goal:** A user can cut a keyway into a round or D-flat bore with an explicit,
DIN-6885-convention depth a human can verify with calipers on the printed part.
**Verified:** 2026-09-27
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | ROADMAP SC1/REQ-keyway-bore and REQ-keyway-wall-refused amended (D-20) before code, so the phase is checked against D-07/D-09/D-10/D-14, not the superseded text | ✓ VERIFIED | `.planning/ROADMAP.md` Phase 9 SC1/SC3/SC4 and `.planning/REQUIREMENTS.md` REQ-keyway-bore/REQ-keyway-wall-refused carry the amended text verbatim; commit `69948df` |
| 2 | `keyway_width`/`keyway_depth` fields exist between `bore_flat` and `bore_hex`, 0=off, help states DIN 6885/ISO R773 `t2` and the ANSI B17.1 warning, no size cited | ✓ VERIFIED | `src/spur/params.py` lines 59-69; field-order check `f.index('keyway_width') == f.index('bore_flat') + 1` passes; help text grepped, no DIN/ANSI size present |
| 3 | A keyway is cut as a rectangular slot after the chamfered bore, floor at `bore_radius(p) + keyway_depth` (the as-cut wall), width `keyway_width + bore_clearance`, centred +Y, sharp edges | ✓ VERIFIED | `src/spur/model.py::_cut_keyway` (after `_cut_bore` in `_build`); `test_a_keyway_floor_sits_keyway_depth_outside_the_as_cut_bore_wall` and `test_the_bore_chamfer_survives_the_keyway_and_the_slot_edges_stay_sharp` pass (25 keyway-marked tests green in `tests/test_model.py`) |
| 4 | `/api/info`, `spur info` and the web UI print `keyway_floor_to_wall` and `keyway_width_effective`, null with no keyway | ✓ VERIFIED | `src/spur/calc.py::derive()`; `app.js` DIMS rows; live check: `spur info --keyway-width 3 --keyway-depth 1.4` → `10.55 3.15 9.15 13.158 25.158 []` |
| 5 | A keyway and a D-flat coexist (default link is D-flat + keyway); a keyway into the flat is refused naming both fields | ✓ VERIFIED | `bore_effective == 9.15` on the default keyed link (flat retained); live check: `--keyway-width 6.5` → "Keyway runs too close to the D-flat ... reduce keyway_width or increase bore_flat." |
| 6 | A keyway on a hex bore or with `bore_d=0` is refused naming the fields; a half-set keyway is refused naming both | ✓ VERIFIED | Live checks reproduce all three exact sentences from `calc.check()` |
| 7 | A keyway whose floor corner nears the root, or one at least as wide as the bore, is refused (never capped) naming the fields, one step either side | ✓ VERIFIED | Live checks: `--keyway-width 9` (bore 9mm) and `--keyway-depth 9.4` reproduce D-11/D-10's exact sentences; `test_the_largest_keyway_each_rule_allows_builds` / `test_the_kernel_cuts_one_valid_solid_past_each_keyway_rule` pass |
| 8 | The face recess yields to the keyway corner (never a 422); D-12's round/D-flat chamfer-reach debt is resolved at the measured contact point, not `rf-MIN_WALL` | ✓ VERIFIED | Default keyed link recess moves to 13.158/25.158 with no warning; live check `--bore-d 24.75 --bore-chamfer 2` reproduces the exact D-12 sentence; debt file moved to `docs/tech_debt/resolved/`, `Status: resolved`, sha `4b6a5b9` |
| 9 | The rim selector takes only pre-keyway edges; the chamfer survives the slot on every bore shape, with and without a keyway (SC4 as amended) | ✓ VERIFIED | 28 matrix rows collected (11 keyway) in `test_each_edge_selector_picks_exactly_its_own_edges`, all pass; spy test `test_the_rim_chamfer_on_a_keyed_bore_takes_the_pre_keyway_edges` passes |
| 10 | Every pre-v0.2 record replays unchanged; the two new fields read null on every old record; the fixture is byte-identical | ✓ VERIFIED | `git diff --stat d03533b..HEAD -- tests/regression/pre_v0_2.json tests/regression/corpus.py` empty; `tests/regression/test_pre_v0_2.py` passes in the full `make verify` run |
| 11 | Measured build time at the heaviest keyway configuration is recorded in `bench/RESULTS.md`, every row inside `SPUR_BUILD_TIMEOUT=30s` | ✓ VERIFIED | `bench/RESULTS.md` "## Keyway bore build and export time (Phase 9)": 32/32 rows recorded, heaviest 4.85s of 30s, all marked "yes" |
| 12 | L28 states the keyway datum with its formula; README documents the feature, the datum, the sharp edges, the two numbers, with no standard-table size as guidance | ✓ VERIFIED | `docs/architecture/decision_log.md` L28 present, states `bore_radius(p) + keyway_depth`; README bullet/rows/example/Geometry-notes bullet present; no DIN/ANSI size cited as guidance anywhere |

**Score:** 12/12 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` | `keyway_width`/`keyway_depth` fields, Bore group, between `bore_flat`/`bore_hex` | ✓ VERIFIED | Present, correct bounds (0-200, step 0.05), help text matches D-16 |
| `src/spur/calc.py` | `keyway_width_effective`, `keyway_corner_radius`, `keyway_flat_wall`, `ROOT_CONTACT`, `bore_mouth_limit`'s keyway branch, six refusal rules, two `DerivedDimensions` fields | ✓ VERIFIED | All present and wired into `check()`/`derive()`; live-checked outputs match |
| `src/spur/model.py` | `_cut_keyway` after `_cut_bore` in `_build` | ✓ VERIFIED | Present at the documented line, `makeBox` typed, no new `type: ignore` |
| `src/spur/static/app.js` | Two `DIMS` rows | ✓ VERIFIED | `keyway_floor_to_wall` / `keyway_width_effective` rows present, covered by `test_every_key_the_ui_reads_is_a_derived_dimensions_field` |
| `tests/test_api.py`, `tests/test_calc.py`, `tests/test_model.py`, `tests/test_cli.py`, `tests/test_bench.py` | Keyed link E2E, refusals, matrix rows, sweep pinning | ✓ VERIFIED | All named tests exist and pass; 41/41 keyway-marked tests in `test_calc.py`+`test_model.py` green |
| `bench/sweeps/keyway_bore.json` | 32-row sweep, largest keyway per (module, flat) pair | ✓ VERIFIED | 32 rows confirmed via `json.load`; pinned by `test_the_keyway_bore_sweep_is_every_combination_with_the_largest_keyway_each_rule_allows` |
| `docs/tech_debt/resolved/2026-09-26-round-bore-chamfer-reach-is-not-checked.md` | Resolved debt record | ✓ VERIFIED | `Status: resolved`, `Resolved in: 4b6a5b9`, moved out of `active/`, INDEX row moved to Resolved |
| `docs/architecture/decision_log.md` | L28 | ✓ VERIFIED | Present, append-only (`git diff --numstat d03533b..HEAD` shows 0 deletions before L28), cites the datum formula and the sweep's heaviest row |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `model._cut_keyway` | `calc.keyway_width_effective`, `calc.bore_radius` | slot geometry sourced from calc | ✓ WIRED | Confirmed by reading `_cut_keyway`'s body |
| `model._build` | `model._cut_bore` then `model._cut_keyway` | ordering | ✓ WIRED | `solid = _cut_keyway(solid, p)` sits directly after `solid = _cut_bore(solid, p)` |
| `calc.recess_radii` | `calc.bore_mouth_limit` → `keyway_corner_radius` | recess yields to the corner | ✓ WIRED | `bore_mouth_limit` returns `max(rim+chamfer, keyway_corner_radius(p))`; live-checked recess values match |
| `app.js` DIMS | `calc.DerivedDimensions` | UI rows read real fields | ✓ WIRED | Confirmed by `test_every_key_the_ui_reads_is_a_derived_dimensions_field` |
| `params._feasible` | `calc.check` | every refusal becomes a 422/exit 2 | ✓ WIRED | Live CLI checks reproduce every documented refusal sentence exactly |
| `docs/tech_debt/INDEX.md` | `docs/tech_debt/resolved/...` | debt moved in the fix commit | ✓ WIRED | Confirmed row present under `## Resolved`, absent under `## Active` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|---------------------|--------|
| `keyway_floor_to_wall` (API/CLI/UI) | `derive()` computed value | `2 * bore_radius(p) + p.keyway_depth`, real calc from validated params | Yes | ✓ FLOWING |
| `keyway_width_effective` (API/CLI/UI) | `derive()` computed value | `keyway_width_effective(p)` | Yes | ✓ FLOWING |
| Keyway slot geometry (STL/STEP) | kernel-cut solid | `_cut_keyway` → `cq.Solid.makeBox` on validated params | Yes | ✓ FLOWING |
| `recess_id`/`recess_od` with a keyway | `recess_radii(p, rf)` | reads `bore_mouth_limit(p)` which includes the keyway corner | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Default keyed link prints correct numbers | `spur info --keyway-width 3 --keyway-depth 1.4` | `10.55 3.15 9.15 13.158 25.158 []` | ✓ PASS |
| Hex+keyway refused | `spur info --keyway-width 3 --keyway-depth 1.4 --bore-hex 6` | exact D-13 sentence | ✓ PASS |
| No-bore+keyway refused | `spur info --keyway-width 3 --keyway-depth 1.4 --bore-d 0` | exact D-13 sentence | ✓ PASS |
| Half-set keyway refused | `spur info --keyway-width 3` | exact D-03 sentence | ✓ PASS |
| Keyway as wide as bore refused | `spur info --bore-flat 0 --keyway-width 9 --keyway-depth 1.4` | exact D-11 sentence | ✓ PASS |
| Keyway too close to D-flat refused | `spur info --keyway-width 6.5 --keyway-depth 1.4` | exact D-02 sentence, "0.381 mm" | ✓ PASS |
| Keyway too deep refused | `spur info --keyway-width 3 --keyway-depth 9.4` | exact D-10 sentence | ✓ PASS |
| Round bore chamfer reaches root refused | `spur info --bore-d 24.75 --bore-chamfer 2 --bore-flat 0` | exact D-12 sentence | ✓ PASS |
| Full test suite passes | `make verify` | ruff/mypy/import-linter/396 tests passed in 76.86s | ✓ PASS |
| Regression fixture byte-identical | `git diff --stat d03533b..HEAD -- tests/regression/pre_v0_2.json tests/regression/corpus.py` | empty | ✓ PASS |
| 28 matrix rows (11 keyway) collected | `pytest tests/test_model.py --collect-only -q` | 28 / 11 | ✓ PASS |
| 32-row sweep recorded, all inside timeout | `bench/RESULTS.md` Phase 9 section | 32/32 rows "yes", heaviest 4.85s | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-keyway-bore | 09-01, 02, 03, 04, 05 | Keyway fields, as-cut-wall datum, clearance on width, `bore_d=0`/hex 422s, no standard sizing | ✓ SATISFIED | `params.py`, `calc.py`, live refusal checks, README, L28 |
| REQ-keyway-composes-with-d-flat | 09-02, 03 | Keyway + D-flat coexist; into-the-flat 422 | ✓ SATISFIED | `bore_effective` retained on default keyed link; D-02 refusal live-checked |
| REQ-keyway-wall-refused | 09-01, 02, 03 | Corner-vs-root 422, never capped; recess yields | ✓ SATISFIED | D-10 refusal live-checked; recess-yield tests pass |
| REQ-hex-rim-chamfer | 09-01, 02 | Hex rim chamfer (Phase 8, re-confirmed); keyway bore's round rim chamfered pre-slot | ✓ SATISFIED | Hex-marked tests still pass (`-k hex`); 28-row matrix includes keyway rows |
| REQ-bore-derived-numbers | 09-02, 05 | `keyway_floor_to_wall`/`keyway_width_effective`, null when off; hex numbers re-confirmed | ✓ SATISFIED | `derive()` fields present and correct; README rows |

No orphaned requirements: REQUIREMENTS.md's Phase-9-mapped IDs (`REQ-keyway-bore`, `REQ-keyway-composes-with-d-flat`, `REQ-keyway-wall-refused`, `REQ-hex-rim-chamfer`, `REQ-bore-derived-numbers`) exactly match the union of `requirements:` frontmatter across 09-01..09-05.

### Anti-Patterns Found

None. Scanned all files changed since `d03533b` (phase start) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` and stub-return patterns — no matches.

### Deviations Verified Behavior-Neutral

- 09-02 Task 2: ruff `ARG005` forced an unused lambda parameter rename (`p` → `_p`) in a test monkeypatch — cosmetic, confirmed no behavior change (11 keyway matrix rows still pass).
- 09-03 Task 1/2: mypy strict rejected `GearParams.model_construct(**kw)` typed against a `dict[str, object]`; replaced with `GearParams().model_copy(update=kw)`, which pydantic v2 documents as an equally validation-bypassing operation on a frozen model — confirmed the same "kernel builds/fails past the rule" tests pass with the substitution (`model_copy(update=` found at both call sites in `tests/test_model.py`).

### Human Verification Required

None. All must-haves resolved programmatically with direct code reads, live CLI/API checks and a green `make verify` run reproduced independently by the verifier (396 passed, 76.86s, matching the orchestrator's claimed 396 passed at HEAD `e7a03fc`).

### Gaps Summary

No gaps. Every roadmap Success Criterion (SC1-SC5, as amended by 09-01 through the edit-phase write step) and every phase requirement ID is independently confirmed against the live codebase: fields exist with correct bounds and help text; the keyway cuts after the chamfer with the datum measured on the built solid; every refusal fires with its exact sentence and fields, one step either side; the round-bore chamfer-reach debt is resolved at the measured contact; the recess yields; the two derived numbers are correct and null when off; the pre-v0.2 fixture and corpus are byte-identical; the 32-row sweep is recorded inside the 30s budget; L28 and the README document the datum with no standard-table size as guidance; and `make verify` is green (396 passed) at the stated HEAD.

---

*Verified: 2026-09-27*
*Verifier: Claude (gsd-verifier)*
