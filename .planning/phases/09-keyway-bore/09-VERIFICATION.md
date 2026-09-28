---
phase: 09-keyway-bore
verified: 2026-09-28T03:15:00Z
status: passed
score: 12/12 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/ROADMAP.md", ".planning/phases/09-keyway-bore/09-01-PLAN.md", ".planning/phases/09-keyway-bore/09-01-SUMMARY.md", ".planning/phases/09-keyway-bore/09-02-PLAN.md", ".planning/phases/09-keyway-bore/09-02-SUMMARY.md", ".planning/phases/09-keyway-bore/09-03-PLAN.md", ".planning/phases/09-keyway-bore/09-03-SUMMARY.md", ".planning/phases/09-keyway-bore/09-04-PLAN.md", ".planning/phases/09-keyway-bore/09-04-SUMMARY.md", ".planning/phases/09-keyway-bore/09-05-PLAN.md", ".planning/phases/09-keyway-bore/09-05-SUMMARY.md", ".planning/phases/09-keyway-bore/09-REVIEW-FIX.md", ".planning/phases/09-keyway-bore/09-REVIEW.md", ".planning/phases/09-keyway-bore/09-SECURITY.md", ".planning/phases/09-keyway-bore/09-UAT.md", ".planning/phases/09-keyway-bore/09-VALIDATION.md", "README.md", "bench/RESULTS.md", "bench/sweeps/keyway_bore.json", "docs/architecture/decision_log.md", "docs/architecture/gear-maths/implementation.md", "docs/architecture/solid-model/tactics.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/resolved/2026-09-26-round-bore-chamfer-reach-is-not-checked.md", "src/spur/calc.py", "src/spur/model.py", "src/spur/params.py", "src/spur/static/app.js", "tests/test_api.py", "tests/test_bench.py", "tests/test_calc.py", "tests/test_cli.py", "tests/test_model.py"]
covered_digest: "v1:sha256:86383a17b91918cb2511ed957f01253622b63e610c3ca24c0e7bdf87d6b4df32"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 12/12
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 9: Keyway Bore Verification Report

**Phase Goal:** A user can cut a keyway into a round or D-flat bore with an explicit,
DIN-6885-convention depth a human can verify with calipers on the printed part.
**Verified:** 2026-09-28
**Status:** passed
**Re-verification:** Yes — the prior report (verified 2026-09-27 at commit `3af023d`) went
stale after `f4818a0` (WR-01) and `7a88d7a` (WR-02) touched `src/spur/calc.py`. Every truth
below was re-checked against HEAD `5cef005`, not copied from the prior report.

## What changed since the prior verification

Two review-driven fixes landed in `src/spur/calc.py` after the prior VERIFICATION.md was
written, both additive and confirmed to leave the phase's locked boundaries untouched:

- **WR-01** (`f4818a0`): `derive()` gained an `else` branch — parallel to the existing
  `if p.bore_hex > 0:` branch — that appends a warning when a round/D-flat bore's chamfered
  mouth leaves `0 <= wall_gap < MIN_WALL` (0.4 mm) of wall to the root circle. `ROOT_CONTACT`
  (the `check()` refusal boundary, D-12) is untouched; this is L03's cap-and-warn pattern
  applied to a gap the refusal itself always let through, not a new refusal and not a new
  cap on a value the user set (L05).
- **WR-02** (`7a88d7a`): the `ROOT_CONTACT` comment was corrected from "cannot be produced
  by any value a user or the API can set" to "unreachable through the UI's stepped widgets,
  not proven unreachable for an ordinary high-precision API/CLI float" — and a new test,
  `test_the_kernel_can_fail_inside_the_root_contact_residual_band`, pins that
  `GearParams(bore_d=24.724999998, bore_chamfer=2, bore_flat=0)` passes `check()` (gap
  `1.000000082740371e-09 > ROOT_CONTACT`) yet still raises `BuildError` from the kernel.
  No constant moved; no link that built before this fix stops building.

Both are reviewed and re-verified directly below rather than assumed from SUMMARY.md.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | ROADMAP SC1/REQ-keyway-bore and REQ-keyway-wall-refused carry the D-20 amendment (as-cut-wall datum, recess-yields clause, pre-keyway-count proof) | ✓ VERIFIED | `.planning/ROADMAP.md` Phase 9 SC1/SC3/SC4 (`gsd query roadmap.get-phase 9`) and `.planning/REQUIREMENTS.md` REQ-keyway-bore/REQ-keyway-wall-refused read the amended text verbatim; unchanged since the prior verification |
| 2 | `keyway_width`/`keyway_depth` fields exist between `bore_flat` and `bore_hex`, 0=off, DIN/ANSI help with no size cited | ✓ VERIFIED | `src/spur/params.py:57-72`: `bore_flat` → `keyway_width` → `keyway_depth` → `bore_hex`, confirmed by direct read; no DIN/ANSI number in help text |
| 3 | A keyway is cut as a rectangular slot after the chamfered bore, floor at `bore_radius(p) + keyway_depth`, width `keyway_width + bore_clearance`, centred +Y, sharp edges | ✓ VERIFIED | `src/spur/model.py` (unchanged since prior verification — `git diff d03533b..HEAD -- src/spur/model.py` shows no diff after `d6300e8`); `.venv/bin/pytest -q tests/test_model.py::test_the_kernel_can_fail_inside_the_root_contact_residual_band` passed (new); the full model-file suite passed inside `make verify`'s 397 |
| 4 | `/api/info`, `spur info` and the web UI print `keyway_floor_to_wall` and `keyway_width_effective`, null with no keyway | ✓ VERIFIED | `src/spur/calc.py::derive()`; `app.js:27-28` DIMS rows read directly; live re-check: `.venv/bin/spur info --keyway-width 3 --keyway-depth 1.4` → `keyway_floor_to_wall: 10.55, keyway_width_effective: 3.15` |
| 5 | A keyway and a D-flat coexist (default link is D-flat + keyway); a keyway into the flat is refused naming both | ✓ VERIFIED | Live re-check: default keyed link → `bore_effective: 9.15` (flat retained), `recess_id/od: 13.158/25.158`; `.venv/bin/spur info --keyway-width 6.5 --keyway-depth 1.4` → exact D-02 refusal sentence naming `bore_flat`/`keyway_width` |
| 6 | A keyway on a hex bore or with `bore_d=0` is refused naming the fields; a half-set keyway is refused naming both | ✓ VERIFIED | Live re-checks reproduce all three exact `check()` sentences: hex+keyway, `bore_d=0`+keyway, half-set (`--keyway-width 3` alone) |
| 7 | A keyway whose floor corner nears the root, or one at least as wide as the bore, is refused naming the fields | ✓ VERIFIED | Live re-checks: `--keyway-width 9` (9 mm bore) → D-11 sentence; `--keyway-depth 9.4` → D-10 sentence, both exact |
| 8 | The face recess yields to the keyway corner (never a 422); D-12's round/D-flat chamfer-reach debt is resolved at the measured contact point, now with a warning below `MIN_WALL` but above `ROOT_CONTACT` (WR-01) | ✓ VERIFIED | Live re-check: `--bore-d 24.75 --bore-chamfer 2` → exact D-12 refusal; `--bore-d 27.905 --bore-flat 0` (0.01 mm wall) → WR-01's new warning `"Bore chamfer leaves only 0.01 mm of wall..."`, reproduced directly via `spur.calc.derive()`; default and default-keyed links still warn `()` (unaffected — gap 9.46 mm); debt file `docs/tech_debt/resolved/...` still `Status: resolved` |
| 9 | The rim selector takes only pre-keyway edges; the chamfer survives the slot on every bore shape, with and without a keyway | ✓ VERIFIED | `.venv/bin/pytest tests/test_model.py --collect-only -q \| grep -c picks_exactly_its_own_edges` → 28 (unchanged; `model.py` untouched since prior verification) |
| 10 | Every pre-v0.2 record replays unchanged; the two new fields read null on every old record; the fixture is byte-identical | ✓ VERIFIED | `git diff --stat d03533b..HEAD -- tests/regression/pre_v0_2.json tests/regression/corpus.py` → empty (re-run, not assumed) |
| 11 | Measured build time at the heaviest keyway configuration is recorded in `bench/RESULTS.md`, every row inside `SPUR_BUILD_TIMEOUT=30s` | ✓ VERIFIED | `bench/RESULTS.md` "## Keyway bore build and export time (Phase 9)" present, unchanged since prior verification (no bench file touched by WR-01/WR-02) |
| 12 | L28 states the keyway datum with its formula; README documents the feature with no standard-table size cited | ✓ VERIFIED | `grep "## L28" docs/architecture/decision_log.md` → present at line 908, formula `bore_radius(p) + keyway_depth`; README bullets/rows/example unchanged since prior verification (no README diff in this cycle) |

**Score:** 12/12 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` | `keyway_width`/`keyway_depth` fields between `bore_flat`/`bore_hex` | ✓ VERIFIED | Confirmed by direct read; unchanged since prior verification (`git diff d03533b..HEAD` shows no post-phase-start diff on this file beyond phase commits) |
| `src/spur/calc.py` | Keyway helpers, `ROOT_CONTACT`, six refusal rules, two `DerivedDimensions` fields, **plus WR-01's warning and WR-02's corrected comment** | ✓ VERIFIED | All present and wired into `check()`/`derive()`; WR-01's `else` branch at line 488-499 confirmed by direct read and live output; WR-02's comment at lines 15-37 confirmed to name the live repro and the new test |
| `src/spur/model.py` | `_cut_keyway` after `_cut_bore` in `_build` | ✓ VERIFIED | Present, unchanged since prior verification |
| `src/spur/static/app.js` | Two `DIMS` rows | ✓ VERIFIED | `keyway_floor_to_wall`/`keyway_width_effective` rows present at lines 27-28 |
| `tests/test_model.py` | **New:** `test_the_kernel_can_fail_inside_the_root_contact_residual_band` pinning WR-02's disclosed residual band | ✓ VERIFIED | Present at line 475; run in isolation: `1 passed in 2.22s`; also green inside the full 397-test `make verify` run |
| `docs/tech_debt/resolved/2026-09-26-round-bore-chamfer-reach-is-not-checked.md` | Resolved debt record | ✓ VERIFIED | `Status: resolved`, `Resolved in: 4b6a5b9`, present under `resolved/` |
| `docs/architecture/decision_log.md` | L28 | ✓ VERIFIED | Present at line 908, append-only (no deletions in this cycle) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `derive()`'s new `else` branch (WR-01) | `bore_radius`, `p.bore_chamfer`, `pr.rf`, `MIN_WALL` | reads the same values `check()`'s `ROOT_CONTACT` rule reads, gated on `p.bore_hex == 0` implicitly by the `if/else` structure | ✓ WIRED | Confirmed by direct read: the `else` sits opposite `if p.bore_hex > 0:`, so the warning never fires for a hex bore |
| `calc.recess_radii` → `calc.bore_mouth_limit` → `keyway_corner_radius` | recess yields to the keyway corner | unchanged since prior verification | ✓ WIRED | Live re-check reproduces the same recess numbers (13.158/25.158) as the prior report |
| `params._feasible` → `calc.check` | every refusal becomes a 422/exit 2 | unchanged since prior verification | ✓ WIRED | Live CLI re-checks reproduce every refusal sentence exactly |
| `docs/tech_debt/INDEX.md` → `docs/tech_debt/resolved/...` | debt moved in the fix commit | unchanged since prior verification | ✓ WIRED | Confirmed row present under `## Resolved` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|---------------------|--------|
| `keyway_floor_to_wall`/`keyway_width_effective` (API/CLI/UI) | `derive()` computed values | real calc from validated params, re-checked live | Yes | ✓ FLOWING |
| WR-01's new warning string | `derive()`'s `wall_gap` computation | `pr.rf - (bore_radius(p) + p.bore_chamfer)`, a real measured value, not a static string | Yes | ✓ FLOWING |
| Keyway slot geometry (STL/STEP) | kernel-cut solid | `_cut_keyway` (unchanged) | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Default keyed link prints correct numbers | `spur info --keyway-width 3 --keyway-depth 1.4` | `keyway_floor_to_wall 10.55, keyway_width_effective 3.15, recess_id 13.158, recess_od 25.158` | ✓ PASS |
| Hex+keyway refused | `spur info --keyway-width 3 --keyway-depth 1.4 --bore-hex 6` | exact D-13 sentence | ✓ PASS |
| No-bore+keyway refused | `spur info --keyway-width 3 --keyway-depth 1.4 --bore-d 0` | exact D-13 sentence | ✓ PASS |
| Half-set keyway refused | `spur info --keyway-width 3` | exact D-03 sentence | ✓ PASS |
| Keyway as wide as bore refused | `spur info --bore-flat 0 --keyway-width 9 --keyway-depth 1.4` | exact D-11 sentence | ✓ PASS |
| Keyway too close to D-flat refused | `spur info --keyway-width 6.5 --keyway-depth 1.4` | exact D-02 sentence | ✓ PASS |
| Keyway too deep refused | `spur info --keyway-width 3 --keyway-depth 9.4` | exact D-10 sentence | ✓ PASS |
| Round bore chamfer reaches root refused (D-12) | `spur info --bore-d 24.75 --bore-chamfer 2 --bore-flat 0` | exact D-12 sentence | ✓ PASS |
| **New: WR-01's thin-wall warning fires** | `python -c "derive(GearParams(bore_d=27.905, bore_flat=0)).warnings"` | `('Bore chamfer leaves only 0.01 mm of wall to the root circle...', 'No room for a face recess...')` | ✓ PASS |
| **New: WR-01 does not false-fire** | same, on `GearParams()` and `GearParams(keyway_width=3, keyway_depth=1.4)` | `()` both times | ✓ PASS |
| **New: WR-02's pinning test passes in isolation** | `.venv/bin/pytest -q tests/test_model.py::test_the_kernel_can_fail_inside_the_root_contact_residual_band` | `1 passed in 2.22s` | ✓ PASS |
| 28 matrix rows (11 keyway) still collected | `pytest tests/test_model.py --collect-only -q \| grep -c picks_exactly_its_own_edges` | 28 | ✓ PASS |
| Regression fixture still byte-identical | `git diff --stat d03533b..HEAD -- tests/regression/pre_v0_2.json tests/regression/corpus.py` | empty | ✓ PASS |
| Full test suite passes at HEAD | `make verify` | ruff/mypy --strict/import-linter/unfinished-work scan/**397 tests** passed in 77.71s | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-keyway-bore | 09-01..05 | Keyway fields, as-cut-wall datum, clearance on width, `bore_d=0`/hex 422s, no standard sizing | ✓ SATISFIED | `params.py`, `calc.py`, live refusal re-checks, README, L28 — all re-verified at HEAD |
| REQ-keyway-composes-with-d-flat | 09-02, 03 | Keyway + D-flat coexist; into-the-flat 422 | ✓ SATISFIED | `bore_effective` retained on default keyed link (re-checked); D-02 refusal live-re-checked |
| REQ-keyway-wall-refused | 09-01, 02, 03 | Corner-vs-root 422, never capped; recess yields | ✓ SATISFIED | D-10 refusal live-re-checked; recess-yield numbers re-checked |
| REQ-hex-rim-chamfer | 09-01, 02 | Hex rim chamfer (Phase 8); keyway bore's round rim chamfered pre-slot | ✓ SATISFIED | Hex-marked tests pass inside `make verify`'s 397; 28-row matrix (11 keyway) re-collected |
| REQ-bore-derived-numbers | 09-02, 05 | `keyway_floor_to_wall`/`keyway_width_effective`, null when off; hex numbers re-confirmed | ✓ SATISFIED | `derive()` fields re-checked live; README rows unchanged |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s Phase-9-mapped IDs (`REQ-keyway-bore`,
`REQ-keyway-composes-with-d-flat`, `REQ-keyway-wall-refused`, `REQ-hex-rim-chamfer`,
`REQ-bore-derived-numbers`) exactly match the union of `requirements:` frontmatter across
09-01..09-05 and the phase's ROADMAP `Requirements:` line; all five show `Complete` in
REQUIREMENTS.md's traceability table.

### Anti-Patterns Found

None. Scanned `src/spur/calc.py`, `src/spur/model.py`, `src/spur/params.py`,
`src/spur/static/app.js` for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` and stub-return
patterns — no matches. `git diff --stat 3af023d..HEAD` (prior-verification commit to HEAD)
confirms only `src/spur/calc.py` (+20/-1) and `tests/test_model.py` (+15) changed in the
covered-file set since the stale prior report — exactly WR-01 and WR-02, nothing broader.

### L03/L05/L08 Check on WR-01/WR-02 (why this rerun called it out)

- **L08 ("no plausible number"):** WR-01's warning prints a real measured `wall_gap`
  (`pr.rf - (bore_radius(p) + p.bore_chamfer)`), not a placeholder or estimate — confirmed
  the printed `0.01 mm` matches the live-computed value exactly (`0.010000000000005116`
  rounded to 2 dp, same rounding convention the file already uses for warnings).
- **L05 ("a parameter the user did not set must never silently change the part"):** WR-01
  adds a warning, not a cap — no dimension moves. Confirmed the default `GearParams()` and
  default-keyed link's `wall_gap` (9.46 mm) stay far above `MIN_WALL`, so neither link's
  warnings changed; the fixture (whose smallest gap is 1.775 mm) is unaffected and its
  `git diff --exit-code` stayed clean.
- **L03 (cap vs. refuse):** correctly classified as a "wish" (warn, per the existing
  `root_fillet`/`recess_radii` pattern for a physical-limit encounter), not a "conflict"
  (which would need a 422) — the refusal boundary (`ROOT_CONTACT`, D-12) is untouched, so
  no round/D-flat link that built before this fix became a 422. Verified by exercising the
  same D-12 boundary case (`bore_d=24.75, bore_chamfer=2`) and confirming it still refuses,
  and `bore_d=24.7` still builds.

### Human Verification Required

None. All must-haves resolved programmatically: direct code reads of the two changed regions,
live CLI/API checks reproduced independently (not copied from SUMMARY.md or the prior
VERIFICATION.md), a green `make verify` run at HEAD (397 passed, 77.71s — up from 396 at the
prior report's commit, the delta being exactly WR-02's new pinning test), and a byte-identical
regression fixture confirmed by re-running the diff, not by assumption.

### Gaps Summary

No gaps. The two files that changed since the stale prior verification (`src/spur/calc.py`,
`tests/test_model.py`) were re-read in full and their behavior re-derived by hand and by live
execution: WR-01 adds a correctly-scoped, correctly-gated warning (never a refusal, never a
false-fire on the default or default-keyed links) that closes the "no warning at all" gap the
code review found; WR-02 softens an overstated comment and adds a pinning regression test for
a disclosed, already-accepted residual band, without moving the locked `ROOT_CONTACT`
boundary. All twelve of the original phase's observable truths were independently
re-confirmed against HEAD `5cef005` — not copied from the prior report's evidence — and none
regressed. Every roadmap Success Criterion (SC1-SC5), every phase requirement ID, the
byte-identical pre-v0.2 fixture, the 32-row sweep, L28, and the README all still hold.

---

*Verified: 2026-09-28*
*Verifier: Claude (gsd-verifier)*
