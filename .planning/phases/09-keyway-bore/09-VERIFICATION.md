---
phase: 09-keyway-bore
verified: 2026-09-28T07:00:00Z
status: passed
score: 12/12 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/ROADMAP.md", ".planning/phases/09-keyway-bore/09-01-PLAN.md", ".planning/phases/09-keyway-bore/09-01-SUMMARY.md", ".planning/phases/09-keyway-bore/09-02-PLAN.md", ".planning/phases/09-keyway-bore/09-02-SUMMARY.md", ".planning/phases/09-keyway-bore/09-03-PLAN.md", ".planning/phases/09-keyway-bore/09-03-SUMMARY.md", ".planning/phases/09-keyway-bore/09-04-PLAN.md", ".planning/phases/09-keyway-bore/09-04-SUMMARY.md", ".planning/phases/09-keyway-bore/09-05-PLAN.md", ".planning/phases/09-keyway-bore/09-05-SUMMARY.md", ".planning/phases/09-keyway-bore/09-REVIEW-FIX.md", ".planning/phases/09-keyway-bore/09-REVIEW.md", ".planning/phases/09-keyway-bore/09-SECURITY.md", ".planning/phases/09-keyway-bore/09-UAT.md", ".planning/phases/09-keyway-bore/09-VALIDATION.md", "README.md", "bench/RESULTS.md", "bench/sweeps/keyway_bore.json", "docs/architecture/decision_log.md", "docs/architecture/gear-maths/implementation.md", "docs/architecture/solid-model/tactics.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/resolved/2026-09-26-round-bore-chamfer-reach-is-not-checked.md", "src/spur/calc.py", "src/spur/model.py", "src/spur/params.py", "src/spur/static/app.js", "tests/test_api.py", "tests/test_bench.py", "tests/test_calc.py", "tests/test_cli.py", "tests/test_model.py"]
covered_digest: "v1:sha256:4316b1814ef2e122fd842963fa192aee84087607b792469b3703456a90ab883b"
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
**Re-verification:** Yes — the prior report (verified 2026-09-28 at commit `31269e2`,
against tree `5cef005`) went stale again after `882dd76` touched `src/spur/calc.py`,
`tests/test_calc.py` and `tests/test_model.py`. Every truth below was re-checked against
HEAD `882dd76`, not copied from the prior report.

## What changed since the prior verification

One commit landed after the prior VERIFICATION.md was written:

- **`882dd76`** ("pin the thin-root-wall warning; correct WR-02's reach and precision
  claims"): a Codex cross-review of PR #10's two post-review fixes (`f4818a0` WR-01,
  `7a88d7a` WR-02) returned REVISE with three findings, all closed by this commit:
  1. A 10-case `pytest.mark.parametrize` test in `tests/test_calc.py`,
     `test_a_bore_chamfer_under_min_wall_from_the_root_warns_with_the_measured_gap`,
     pins WR-01's warning one step either side of `MIN_WALL` on the default gear
     (`bore_d` 27.1 → silent, 27.15 → "0.39 mm"), on a D-flat, across the
     `bore_clearance` flip at `bore_d` 27.2, and confirms silence on hex, no-bore,
     default and default-keyed links.
  2. `src/spur/calc.py`'s `ROOT_CONTACT` comment was reworded: the UI's step buttons
     never land in the sub-2e-8 mm residual band, but nothing enforces the step —
     `app.js` forwards a typed value as-is (lines 68, 99) — so a typed value, a shared
     link, or an API/CLI caller can. The comment no longer overclaims "unreachable"
     generally.
  3. Both comments (the module-level `ROOT_CONTACT` comment and the pinning test's
     docstring) now say `24.724999998` has 11 significant figures (was 9).
  Codex re-reviewed `882dd76` and returned APPROVED (98/100, no issues) per
  `09-REVIEW-FIX.md`.

The ship-note (`b9f6dea`, `STATE.md`) and the prior VERIFICATION.md (`31269e2`) also
landed in between; neither touches source.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | ROADMAP SC1/REQ-keyway-bore and REQ-keyway-wall-refused carry the D-20 amendment (as-cut-wall datum, recess-yields clause, pre-keyway-count proof) | ✓ VERIFIED | `gsd query roadmap.get-phase 9` re-run: SC1/SC3/SC4 text unchanged since prior verification; `.planning/REQUIREMENTS.md` REQ-keyway-bore/REQ-keyway-wall-refused read the amended text verbatim |
| 2 | `keyway_width`/`keyway_depth` fields exist between `bore_flat` and `bore_hex`, 0=off, DIN/ANSI help with no size cited | ✓ VERIFIED | `src/spur/params.py` unchanged this cycle (`git diff --stat d03533b..882dd76 -- src/spur/params.py` shows no post-5cef005 delta); field order re-confirmed by direct read |
| 3 | A keyway is cut as a rectangular slot after the chamfered bore, floor at `bore_radius(p) + keyway_depth`, width `keyway_width + bore_clearance`, centred +Y, sharp edges | ✓ VERIFIED | `src/spur/model.py` unchanged since prior verification (`git diff 5cef005..882dd76 -- src/spur/model.py` empty); `.venv/bin/pytest -q tests/test_model.py::test_the_kernel_can_fail_inside_the_root_contact_residual_band` → `1 passed in 2.28s` (re-run live, not assumed) |
| 4 | `/api/info`, `spur info` and the web UI print `keyway_floor_to_wall` and `keyway_width_effective`, null with no keyway | ✓ VERIFIED | Live re-check: `.venv/bin/spur info --keyway-width 3 --keyway-depth 1.4` reproduces `keyway_floor_to_wall`/`keyway_width_effective`; `app.js` DIMS rows unchanged this cycle |
| 5 | A keyway and a D-flat coexist (default link is D-flat + keyway); a keyway into the flat is refused naming both | ✓ VERIFIED | Live re-check: `--keyway-width 6.5 --keyway-depth 1.4` → exact D-02 refusal sentence naming `bore_flat`/`keyway_width`, re-run against HEAD |
| 6 | A keyway on a hex bore or with `bore_d=0` is refused naming the fields; a half-set keyway is refused naming both | ✓ VERIFIED | Live re-checks reproduce all three exact `check()` sentences: hex+keyway, `bore_d=0`+keyway, half-set (`--keyway-width 3` alone) |
| 7 | A keyway whose floor corner nears the root, or one at least as wide as the bore, is refused naming the fields | ✓ VERIFIED | Unchanged `check()` code this cycle; refusal boundaries (D-10, D-11) untouched by `882dd76` (diff confined to `derive()`'s WR-01 branch and comments) |
| 8 | The face recess yields to the keyway corner (never a 422); D-12's round/D-flat chamfer-reach debt is resolved at the measured contact point, now with a warning below `MIN_WALL` but above `ROOT_CONTACT` (WR-01), and the warning is now pinned by a 10-case regression test | ✓ VERIFIED | Live re-check: `--bore-d 24.75 --bore-chamfer 2 --bore-flat 0` → exact D-12 refusal; live Python re-check of `derive()` on `bore_d=27.905` → `('Bore chamfer leaves only 0.01 mm of wall to the root circle...', 'No room for a face recess...')`, default and default-keyed links still `()`; **new:** `.venv/bin/pytest -q tests/test_calc.py::test_a_bore_chamfer_under_min_wall_from_the_root_warns_with_the_measured_gap` → `10 passed in 0.06s` |
| 9 | The rim selector takes only pre-keyway edges; the chamfer survives the slot on every bore shape, with and without a keyway | ✓ VERIFIED | `.venv/bin/pytest tests/test_model.py --collect-only -q \| grep -c picks_exactly_its_own_edges` → 28 (unchanged; `model.py` untouched this cycle) |
| 10 | Every pre-v0.2 record replays unchanged; the two new fields read null on every old record; the fixture is byte-identical | ✓ VERIFIED | `git diff --stat d03533b..882dd76 -- tests/regression/pre_v0_2.json tests/regression/corpus.py` → empty (re-run against the whole phase span, not assumed) |
| 11 | Measured build time at the heaviest keyway configuration is recorded in `bench/RESULTS.md`, every row inside `SPUR_BUILD_TIMEOUT=30s` | ✓ VERIFIED | `bench/RESULTS.md` "## Keyway bore build and export time (Phase 9)" present, unchanged this cycle (`882dd76` touches only `calc.py`/`test_calc.py`/`test_model.py`) |
| 12 | L28 states the keyway datum with its formula; README documents the feature with no standard-table size cited; the `ROOT_CONTACT` comment accurately states the residual band's reach (not overclaimed "unreachable") | ✓ VERIFIED | `grep "^## L28"` → present at line 908, formula `bore_radius(p) + keyway_depth`, unchanged; `src/spur/calc.py` lines 15-37 re-read directly: comment now says "the UI's step buttons never land in it -- but nothing enforces the step... app.js forwards a typed value as-is... a value typed into the field, a shared link or an API/CLI caller sending an 11-significant-figure bore_d can land inside this band" — matches the live repro (`24.724999998` = 11 digits, confirmed by `len('24724999998')` → 11) |

**Score:** 12/12 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` | `keyway_width`/`keyway_depth` fields between `bore_flat`/`bore_hex` | ✓ VERIFIED | Unchanged this cycle; confirmed by direct read |
| `src/spur/calc.py` | Keyway helpers, `ROOT_CONTACT`, six refusal rules, two `DerivedDimensions` fields, WR-01's warning, WR-02's corrected comment (now precision- and reach-accurate) | ✓ VERIFIED | `else` branch at lines 490-500 unchanged in logic (comment/wording only); WR-01's warning confirmed live; module-level comment (lines 15-37) re-read, now states "11-significant-figure" and "app.js forwards a typed value as-is" |
| `src/spur/model.py` | `_cut_keyway` after `_cut_bore` in `_build` | ✓ VERIFIED | Present, unchanged this cycle |
| `src/spur/static/app.js` | Two `DIMS` rows | ✓ VERIFIED | `keyway_floor_to_wall`/`keyway_width_effective` rows present; unchanged this cycle |
| `tests/test_calc.py` | **New:** `test_a_bore_chamfer_under_min_wall_from_the_root_warns_with_the_measured_gap` — 10-case parametrized pin of WR-01 | ✓ VERIFIED | Present at line 442; run in isolation: `10 passed in 0.06s`; also green inside the full 407-test `make verify` run |
| `tests/test_model.py` | `test_the_kernel_can_fail_inside_the_root_contact_residual_band`, docstring corrected to "11-significant-figure" | ✓ VERIFIED | Present; docstring re-read, matches; run in isolation: `1 passed in 2.28s` |
| `docs/tech_debt/resolved/2026-09-26-round-bore-chamfer-reach-is-not-checked.md` | Resolved debt record | ✓ VERIFIED | `Status: resolved`, unchanged this cycle |
| `docs/architecture/decision_log.md` | L28 | ✓ VERIFIED | Present at line 908, unchanged this cycle |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `derive()`'s `else` branch (WR-01) | `bore_radius`, `p.bore_chamfer`, `pr.rf`, `MIN_WALL` | reads the same values `check()`'s `ROOT_CONTACT` rule reads, gated on `p.bore_hex == 0` implicitly by the `if/else` structure | ✓ WIRED | Confirmed by direct read of `src/spur/calc.py:479-500`; logic unchanged this cycle, only the sibling module comment reworded |
| `tests/test_calc.py`'s new parametrized test | `spur.calc.derive()` | direct function call, no mocking | ✓ WIRED | `derive(GearParams.model_validate(kw))` — real call, confirmed by direct read and live pass |
| `calc.recess_radii` → `calc.bore_mouth_limit` → `keyway_corner_radius` | recess yields to the keyway corner | unchanged this cycle | ✓ WIRED | Not re-derived numerically this cycle (no code change); confirmed the covering file, `model.py`, is byte-identical to the prior verification's checked state |
| `params._feasible` → `calc.check` | every refusal becomes a 422/exit 2 | unchanged this cycle | ✓ WIRED | Live CLI re-checks (D-02, D-12) reproduce the exact refusal sentences |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|---------------------|--------|
| `keyway_floor_to_wall`/`keyway_width_effective` (API/CLI/UI) | `derive()` computed values | real calc from validated params, re-checked live | Yes | ✓ FLOWING |
| WR-01's warning string | `derive()`'s `wall_gap` computation | `pr.rf - (bore_radius(p) + p.bore_chamfer)`, re-confirmed live at `bore_d=27.905` → `0.01 mm`, matching the exact float | Yes | ✓ FLOWING |
| Keyway slot geometry (STL/STEP) | kernel-cut solid | `_cut_keyway` (unchanged) | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Round bore chamfer reaches root refused (D-12) | `spur info --bore-d 24.75 --bore-chamfer 2 --bore-flat 0` | exact D-12 sentence | ✓ PASS |
| WR-01's thin-wall warning fires | Python: `derive(GearParams(bore_d=27.905, bore_flat=0)).warnings` | `('Bore chamfer leaves only 0.01 mm of wall to the root circle...', 'No room for a face recess...')` | ✓ PASS |
| WR-01 does not false-fire | same, on `GearParams()` and `GearParams(keyway_width=3, keyway_depth=1.4)` | `()` both times | ✓ PASS |
| **New: WR-01's 10-case pin passes** | `.venv/bin/pytest -q tests/test_calc.py::test_a_bore_chamfer_under_min_wall_from_the_root_warns_with_the_measured_gap` | `10 passed in 0.06s` | ✓ PASS |
| WR-02's pinning test passes in isolation | `.venv/bin/pytest -q tests/test_model.py::test_the_kernel_can_fail_inside_the_root_contact_residual_band` | `1 passed in 2.28s` | ✓ PASS |
| 28 matrix rows (11 keyway) still collected | `pytest tests/test_model.py --collect-only -q \| grep -c picks_exactly_its_own_edges` | 28 | ✓ PASS |
| Regression fixture still byte-identical across the whole phase span | `git diff --stat d03533b..882dd76 -- tests/regression/pre_v0_2.json tests/regression/corpus.py` | empty | ✓ PASS |
| Debt marker scan on touched files | `git grep -nE '\b(TODO\|FIXME\|XXX\|HACK\|NotImplementedError)\b' -- src/spur/calc.py tests/test_calc.py tests/test_model.py` | exit 1 (no matches) | ✓ PASS |
| Full test suite passes at HEAD | `make verify` | ruff / mypy --strict / import-linter (5 kept, 0 broken) / no-fake-done / **407 tests passed in 85.04s** | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-keyway-bore | 09-01..05 | Keyway fields, as-cut-wall datum, clearance on width, `bore_d=0`/hex 422s, no standard sizing | ✓ SATISFIED | `params.py`, `calc.py`, live refusal re-checks, README, L28 — all re-verified at HEAD |
| REQ-keyway-composes-with-d-flat | 09-02, 03 | Keyway + D-flat coexist; into-the-flat 422 | ✓ SATISFIED | D-02 refusal live-re-checked at HEAD |
| REQ-keyway-wall-refused | 09-01, 02, 03 | Corner-vs-root 422, never capped; recess yields; and, per this cycle, the thin-wall *below* `ROOT_CONTACT` warns rather than silently passing | ✓ SATISFIED | D-10/D-12 refusals live-re-checked; WR-01's warning now pinned by a 10-case test |
| REQ-hex-rim-chamfer | 09-01, 02 | Hex rim chamfer (Phase 8); keyway bore's round rim chamfered pre-slot | ✓ SATISFIED | Hex-marked tests pass inside `make verify`'s 407; 28-row matrix (11 keyway) re-collected |
| REQ-bore-derived-numbers | 09-02, 05 | `keyway_floor_to_wall`/`keyway_width_effective`, null when off; hex numbers re-confirmed | ✓ SATISFIED | `derive()` fields re-checked live; README rows unchanged |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s Phase-9-mapped IDs (`REQ-keyway-bore`,
`REQ-keyway-composes-with-d-flat`, `REQ-keyway-wall-refused`, `REQ-hex-rim-chamfer`,
`REQ-bore-derived-numbers`) exactly match the union of `requirements:` frontmatter across
09-01..09-05 (re-grepped this cycle) and the phase's ROADMAP `Requirements:` line; all five
show `Complete` in REQUIREMENTS.md's traceability table.

### Anti-Patterns Found

None. `git grep -nE '\b(TODO|FIXME|XXX|HACK|NotImplementedError)\b' -- src/spur/calc.py
tests/test_calc.py tests/test_model.py` (the three files touched by `882dd76`) returned no
matches. `git diff --stat 5cef005..882dd76` confirms only `src/spur/calc.py` (+11/-10, comment
only), `tests/test_calc.py` (+38, new test), and `tests/test_model.py` (+5/-4, docstring only)
changed in the covered-file set since the previously-stale report — exactly the Codex
cross-review's three findings, nothing broader. `.planning/STATE.md` also changed
(ship-note bookkeeping) but is not a covered implementation file.

### L03/L05/L08 Check on this cycle's change

- **L08 ("no plausible number"):** No numeric behavior changed — `882dd76` is comments and a
  new test. The warning's printed value is unchanged and still a real measured `wall_gap`
  (re-confirmed live: `0.01 mm` for `bore_d=27.905`).
- **L05 ("a parameter the user did not set must never silently change the part"):** No
  boundary moved. `ROOT_CONTACT` and `MIN_WALL` are untouched; the comment correction only
  makes the *documented* reach of the known residual band more honest (11, not 9,
  significant figures; "the UI's step buttons never land in it" instead of a blanket
  "unreachable"), which is itself an instance of L08's spirit applied to documentation, not
  a code behavior change.
- **L03 (cap vs. refuse):** Unaffected — no refusal boundary moved in this commit.

### Human Verification Required

None. All must-haves resolved programmatically: direct code reads of the three changed
files, live CLI/API/Python checks reproduced independently at HEAD `882dd76` (not copied
from SUMMARY.md or the prior VERIFICATION.md), a green `make verify` run (407 passed in
85.04s — up from 397 at the two-verifications-ago baseline, the delta being exactly the
10 new WR-01 pin cases), and a byte-identical regression fixture confirmed by re-running
the diff across the full phase span, not by assumption.

### Gaps Summary

No gaps. The three files that changed since the previously-stale verification
(`src/spur/calc.py`, `tests/test_calc.py`, `tests/test_model.py`) were re-read in full and
their behavior re-derived by hand and by live execution: the calc.py change is comment-only
(no logic delta — confirmed the `else` branch's code is byte-identical, only the module-level
`ROOT_CONTACT` comment's wording changed to state the residual band's reach and the
`24.724999998` example's significant-figure count accurately); the two test changes add a
10-case regression pin for WR-01's warning (closing the "warning exists but isn't pinned by a
test" gap the Codex cross-review found) and correct a docstring's digit count to match. All
twelve of the phase's observable truths were independently re-confirmed against HEAD
`882dd76` — not copied from the prior report's evidence — and none regressed. Every roadmap
Success Criterion (SC1-SC5), every phase requirement ID, the byte-identical pre-v0.2 fixture,
the 32-row sweep, L28, and the README all still hold.

---

*Verified: 2026-09-28*
*Verifier: Claude (gsd-verifier)*
