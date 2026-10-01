---
phase: 11-body-cutouts
verified: 2026-09-29T11:43:13Z
status: passed
score: 7/7 must-haves verified
covered_files: [".planning/phases/11-body-cutouts/11-01-PLAN.md", ".planning/phases/11-body-cutouts/11-01-SUMMARY.md", ".planning/phases/11-body-cutouts/11-02-PLAN.md", ".planning/phases/11-body-cutouts/11-02-SUMMARY.md", ".planning/phases/11-body-cutouts/11-03-PLAN.md", ".planning/phases/11-body-cutouts/11-03-SUMMARY.md", ".planning/phases/11-body-cutouts/11-04-PLAN.md", ".planning/phases/11-body-cutouts/11-04-SUMMARY.md", ".planning/phases/11-body-cutouts/11-05-PLAN.md", ".planning/phases/11-body-cutouts/11-05-SUMMARY.md", ".planning/phases/11-body-cutouts/11-06-PLAN.md", ".planning/phases/11-body-cutouts/11-06-SUMMARY.md", ".planning/phases/11-body-cutouts/11-07-PLAN.md", ".planning/phases/11-body-cutouts/11-07-SUMMARY.md", ".planning/phases/11-body-cutouts/11-08-PLAN.md", ".planning/phases/11-body-cutouts/11-08-SUMMARY.md", ".planning/phases/11-body-cutouts/11-09-PLAN.md", ".planning/phases/11-body-cutouts/11-09-SUMMARY.md", ".planning/phases/11-body-cutouts/11-CONTEXT.md", ".planning/phases/11-body-cutouts/11-REVIEW-DISPOSITION.md", ".planning/phases/11-body-cutouts/11-REVIEW.md", ".planning/phases/11-body-cutouts/11-SECURITY.md", ".planning/phases/11-body-cutouts/11-VALIDATION.md", "README.md", "bench/RESULTS.md", "bench/honeycomb_spike.py", "bench/sweeps/hole_cutout.json", "bench/sweeps/honeycomb.json", "bench/sweeps/spoke_cutout.json", "docs/architecture/decision_log.md", "docs/architecture/gear-maths/implementation.md", "docs/architecture/solid-model/tactics.md", "docs/ideas/2026-09-29-conditional-form-fields.md", "docs/ideas/2026-09-29-cutout-rotation-field.md", "docs/ideas/2026-09-29-teeth-dependent-honeycomb-cap.md", "docs/ideas/INDEX.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md", "src/spur/calc.py", "src/spur/model.py", "src/spur/params.py", "src/spur/static/app.js", "tests/test_api.py", "tests/test_bench.py", "tests/test_calc.py", "tests/test_cli.py", "tests/test_model.py"]
covered_digest: "v2:sha256:78a97f8d7cbd62a6bd76fd2da7196dde2c6519c43b064b5af9fb86d8e5288614"
behavior_unverified: 0
overrides_applied: 0
behavior_unverified_items: []
human_verification:
  - test: "Confirm the spoke-arm MIN_WALL rule (0 < spoke_width < MIN_WALL refused with a 422) matches what the human actually wanted at the 11-01 checkpoint."
    expected: "11-01-SUMMARY.md's transcription of the human's 'approved' answer (keep the rule) matches the human's intent; test_a_spoke_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly and the arm sentence in calc.check() implement it."
    why_human: "A policy decision transcribed from the human's own words at a checkpoint, not a property automation can verify — this project's own 11-VALIDATION.md lists it as manual-only."
  - test: "Confirm HEX_CELL_CAP = 120 and the star cut spelling are acceptable as measured, given (a) both readings were taken under a loaded host (8-9 and 5-10 on a 12-core machine, well above the project's 1.5 'quiet' bar) and (b) 11-REVIEW.md's WR-01 (open, unfixed) found that bench/honeycomb_spike.py's slower()/verdict logic can silently discard a failed build trial in favour of a successful one and never checks the confirmation or spelling rows for validity — a methodology gap in the exact script whose output produced HEX_CELL_CAP."
    expected: "Either accept 120 as-is (11-06's independent sweep at the cap re-confirms every honeycomb row builds, heaviest 8.65 s, inside the 30 s absolute budget) or require a re-run of the spike with WR-01's fix before trusting the cap further."
    why_human: "The number is read off one load-affected run on shared hardware, and a known, still-open methodology gap in the measuring script itself is a judgment call about acceptable evidence quality, not something a test can settle (L08)."
  - test: "Confirm the honeycomb's 8.65 s cap-row reading is acceptable against D-11's own 7.5 s quarter-share budget (a 1.15x overrun), accepted at 11-06's checkpoint as 'comparable to 11-02's own 7.25 s reading under similar load.'"
    expected: "The human's already-recorded acceptance (11-06-SUMMARY.md key-decisions) stands, or a quieter-host re-measurement is requested."
    why_human: "Same load-affected-measurement judgment as above; already decided once at an interactive checkpoint (11-06, autonomous: false) but worth a final confirmation since it is the honeycomb's only reading over its own D-11 budget line."
  - test: "Confirm the 33.39 s arithmetic total (heaviest spoke_count le-40 row, 18.52 s, plus Phase 10's 14.87 s tip-chamfer row, both single-feature readings, not a composed build) is acceptable to defer to Phase 12's real composed sweep rather than lowering spoke_count's le further now."
    expected: "docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md's must-severity filing with Phase 12 as its named trigger is the right call, or the le should be lowered again before Phase 12."
    why_human: "Whether one loaded-host arithmetic reading (load 32.17, the heaviest anywhere in this project's bench history) warrants revisiting the le now versus waiting for Phase 12's real measurement is a project-priority call, not a test (11-06-SUMMARY.md's own rationale)."
  - test: "Triage the five still-open code-review findings from 11-REVIEW.md (WR-01 through WR-05, IN-01; 11-REVIEW-DISPOSITION.md shows all six at disposition 'open', none fixed/skipped/deferred). Two were independently reproduced during this verification: WR-02 (docs/architecture/decision_log.md:1218-1221's L30 entry still says 'the boundary itself builds, one step past it does not', the opposite of what test_the_kernel_cuts_one_valid_solid_past_each_cutout_rule proves and ships) and WR-04 (README.md:151-152 still claims the reverse half-set case — a cutout dimension set with its count at 0 — is 'rejected'; confirmed live that it instead builds nothing and warns: `spur info --hole-d 4 --hole-circle-d 20` returns warnings=['No lightening holes with hole_count 0: ...'], not a 422)."
    expected: "Each finding gets a disposition (fixed/skipped/deferred) rather than sitting at 'open' indefinitely; WR-02 and WR-04 are confirmed real doc/prose inaccuracies (not code defects) and are inexpensive one-sentence fixes."
    why_human: "Severity/priority triage of a code-review finding is a project decision, and code review disposition is explicitly a human-owned gate (11-REVIEW-DISPOSITION.md), not something the verifier can resolve unilaterally."
---

# Phase 11: Body Cutouts Verification Report

**Phase Goal:** A user can lighten the gear body with exactly one of three explicit cutout
patterns — lightening holes, spoke arms, or a honeycomb web — each composing with any bore
profile and with face recesses.
**Verified:** 2026-09-29T11:43:13Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Setting `hole_count`/`hole_d`/`hole_circle_d` (0=off) cuts N equal round holes on a bolt circle through the full face width, in one `.cut(*cutters)` call (ROADMAP SC1) | ✓ VERIFIED | `src/spur/model.py:267` `_hole_cutters`, `:364` `_cut_body` (`solid.cut(*cutters)`, single call, no loop); live spot check `spur info --hole-count 6 --hole-d 4 --hole-circle-d 20` → `cutout_hub_wall 3.025`, `cutout_rim_wall 2.438` (matches 11-03-SUMMARY.md exactly); `tests/test_calc.py`/`tests/test_model.py` hole-scoped tests (36 collected) run clean |
| 2 | Setting `spoke_count`/`spoke_width`/`hub_d`/`rim_wall` (0=off) cuts N arms between a hub ring and a rim ring, corners rounded by `spoke_fillet` (0=sharp), capped to fit (ROADMAP SC2, 11-CONTEXT D-04/D-06/D-21) | ✓ VERIFIED | `src/spur/model.py:338` `_spoke_cutters`, `_fillet_corner(inside=)`; live spot check `spur info --spoke-count 4 --spoke-width 2 --hub-d 12 --rim-wall 1 --spoke-fillet 1` → `spoke_fillet_effective 1.0`, walls `1.025`/`1.0` (matches 11-04-SUMMARY.md exactly); REQUIREMENTS.md's REQ-spoke-cutout and ROADMAP SC2 both carry the `spoke_fillet` clause per 11-01's amendment |
| 3 | Setting `hex_cell`/`hex_wall` (0=off) cuts a honeycomb whose cell count is derived/reported; a sweep ran before any cap formula was written and is logged as `L30`; over-cap requests are raised, never dropped, and the cap is analytic/deterministic (ROADMAP SC3) | ✓ VERIFIED | `src/spur/calc.py:51` `HEX_CELL_CAP = 120` (matches `bench/RESULTS.md`'s `**Cap:**` line exactly, written before any `hex_cell` field existed — 11-02 predates 11-05); live spot check `spur info --hex-cell 3 --hex-wall 1` → `hex_cell_effective 3.0`, `hex_cell_count 18`, walls `1.525`/`2.149` (matches 11-05-SUMMARY.md exactly); `L30` present in `docs/architecture/decision_log.md:1140` |
| 4 | Exactly one of `spoke_count`/`hole_count`/`hex_cell` may be non-zero; two or more is a 422 naming the fields (REQ-one-cutout-pattern) | ✓ VERIFIED | `src/spur/calc.py:679-691` `chosen`/one-pattern rule; live spot check: `spur info --hole-count 6 --hole-d 4 --hole-circle-d 20 --spoke-count 4 --spoke-width 2 --hub-d 12 --rim-wall 1` → exit 2, `"Only one body cutout pattern per part: spoke_count (4) and hole_count (6) are both set..."` |
| 5 | A cutout that breaches the hub wall, rim wall, or overlaps itself is refused in `calc.py` before any CAD work, 422/exit 2, same message on both interfaces (REQ-cutout-conflicts-refused-early) | ✓ VERIFIED | Live spot check: `spur info --hole-count 6 --hole-d 4 --hole-circle-d 14.7` → exit 2, hub-breach sentence; `--hole-circle-d 14.75` (exactly `MIN_WALL`) → accepted, `cutout_hub_wall 0.4`; `tests/test_model.py::test_the_kernel_cuts_one_valid_solid_past_each_cutout_rule`/`test_the_largest_cutout_each_wall_rule_allows_builds` (18 rows, re-run, pass) prove the rules sit at the part's `MIN_WALL`, not a kernel limit |
| 6 | Any cutout composes with face recesses (cuts through the recessed floor, floor fillet intact on surviving edges) and with any bore profile; measured build time recorded; Phase 7's regression fixture still passes (ROADMAP SC5) | ✓ VERIFIED | Live spot check: hex bore + honeycomb (`--bore-hex 6 --hex-cell 3 --hex-wall 1`) → `hex_cell_count 24`, walls `1.184`/`2.149` (matches 11-05-SUMMARY.md's per-bore-shape table exactly); `tests/test_model.py::test_the_recess_floor_fillet_survives_every_cutout_on_every_bore` (13 rows: every pattern × D-flat/round/hex/keyed bore, both recesses) re-run, passes, zero sharp floor-to-wall circles; `git diff --exit-code tests/regression/pre_v0_2.json` → byte-unchanged; `bench/RESULTS.md` "Body cutout build and export time (Phase 11)" records 24 first-run + 16 re-run rows |
| 7 | `DerivedDimensions` reports the thinnest hub-side and rim-side wall, the honeycomb cell count actually cut, `null` when no cutout is set (REQ-cutout-derived-numbers) | ✓ VERIFIED | `src/spur/calc.py:911-935` five fields present (`cutout_hub_wall`, `cutout_rim_wall`, `spoke_fillet_effective`, `hex_cell_effective`, `hex_cell_count`); `src/spur/static/app.js:34-37` wired and rendered; `tests/test_model.py::test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid` (re-run, passes) reads the printed numbers back off the built solid per pattern with two tripwires proving the proof fails when the cut or the recess fillet is skipped |

**Score:** 7/7 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/params.py` | Spokes/Holes/Honeycomb groups, 10 fields, every default 0 | ✓ VERIFIED | `grep` confirms all 10 fields in the three named groups; `spoke_count`/`hole_count` `le` 40/60 (D-18's gate outcome, not the plan's provisional 200) |
| `src/spur/calc.py` | `HEX_CELL_CAP`, `cutout_walls`, `_under_min_wall`, `hole_gap`, `spoke_opening`, `spoke_fillet_limit`, `spoke_fillet_effective`, `whole_cells`, `cell_count_floor`, `cells_within`, `hex_cells`, 5 derived fields, cutout rules | ✓ VERIFIED | All functions present at the expected signatures (`grep -n "^def "` confirms every one) |
| `src/spur/model.py` | `_hole_cutters`, `_spoke_cutters`, `_cell_cutters`, `_cut_body` between `_cut_keyway` and `_chamfer_tips`, single `cut(*cutters)` | ✓ VERIFIED | Build order confirmed: `_cut_keyway` (514) → `_cut_body` (515) → `_chamfer_tips` (516); `_cut_body`'s docstring and code match the plan's `star` spelling exactly, no `tol=` |
| `src/spur/static/app.js` | 5 new `DIMS` rows | ✓ VERIFIED | All 5 rows present and rendered in the results table loop (line 138) |
| `bench/honeycomb_spike.py`, `bench/RESULTS.md`, `bench/sweeps/*.json` | Measurement spike, spike/sweep records, sweep files at the gated `le` | ✓ VERIFIED | `HEX_CELL_CAP = 120` line present; hole/spoke sweeps confirmed at 60/40 (post-gate); honeycomb sweep at the cap |
| `tests/test_api.py`, `tests/test_model.py`, `tests/test_calc.py`, `tests/test_cli.py`, `tests/test_bench.py` | Tracer, boundary, selector, built-solid and sweep-pin tests | ✓ VERIFIED | Targeted re-runs: 76 `tests/test_calc.py` cutout-scoped tests pass; 96 `tests/test_model.py` cutout-scoped tests pass (76.9s); 10 `tests/test_bench.py` tests pass; regression fixture byte-unchanged throughout |
| `README.md`, `docs/architecture/decision_log.md` (L30), `docs/architecture/gear-maths/implementation.md`, `docs/architecture/solid-model/tactics.md`, `docs/ideas/*` | Documentation, decision log, deferred ideas | ⚠️ VERIFIED WITH KNOWN GAPS | README/L30/architecture docs all present with the expected content; two prose inaccuracies confirmed still open (WR-02 in L30, WR-04 in README) — see Anti-Patterns and Human Verification |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `bench/RESULTS.md` (`**Cap:**` line) | `src/spur/calc.py` (`HEX_CELL_CAP`) | The constant is written from the measured line | ✓ WIRED | Both read `120`; `HEX_CELL_CAP`'s comment cites the measurement, date and host |
| `bench/RESULTS.md` (`**Spelling:**` line) | `src/spur/model.py` (`_cut_body`) | The measured spelling every cutter uses | ✓ WIRED | `_cut_body`'s docstring cites the same measurement; code uses `solid.cut(*cutters)` (`star`) |
| `src/spur/model.py` (`_cut_body`) | `src/spur/calc.py` (`cutout_walls`, `hex_cells`, `spoke_fillet_effective`) | Cutter geometry and printed walls share the same datum functions | ✓ WIRED | Confirmed by reading `_hole_cutters`/`_spoke_cutters`/`_cell_cutters` against `cutout_walls`'s hub/rim math |
| `README.md` (CLI examples) | `tests/test_cli.py` (`test_readme_export_examples_run`) | Every documented command runs in the gate | ✓ WIRED | Test present and asserts >1000-byte output, no warning, per 11-09-SUMMARY.md |
| `bench/RESULTS.md` (Body cutout build/export time) | `docs/architecture/decision_log.md` (L30) | L30 quotes the heaviest rows | ✓ WIRED | `grep -c "^\*\*Heaviest:\*\*"` → 8 in RESULTS.md; L30 present and cites SUMMARY shas/RESULTS sections per its own text |
| `.planning/REQUIREMENTS.md` | `.planning/ROADMAP.md` (Phase 11 SC2) | Both carry the same `spoke_fillet` clause | ✓ WIRED | Both texts confirmed to carry the D-04/D-06/D-21-cited clause |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|---------------------|--------|
| `app.js` DIMS row `cutout_hub_wall` | `d.cutout_hub_wall` | `/api/info` → `derive(p).cutout_hub_wall` → `calc.cutout_walls(p, rf)` | Yes — live spot check returns real, varying numbers per link (3.025 default holes, 1.025 spokes, 1.525/1.184 honeycomb per bore) | ✓ FLOWING |
| `app.js` DIMS row `hex_cell_effective` (label carries count) | `d.hex_cell_effective`, `d.hex_cell_count` | `derive(p).hex_cell_effective`/`hex_cell_count` → `calc.hex_cells(p, rf)` | Yes — count varies with bore shape (18/24/12/30 measured) | ✓ FLOWING |
| `model._cut_body` cutter lists | `_hole_cutters`/`_spoke_cutters`/`_cell_cutters(p, ...)` | Computed from `p` and `pr` each call, no cache/static list | Yes — same-link-same-part test and per-bore-shape counts confirm real computation | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Hole tracer link builds with correct walls | `spur info --hole-count 6 --hole-d 4 --hole-circle-d 20` | `cutout_hub_wall 3.025`, `cutout_rim_wall 2.438`, `warnings []` | ✓ PASS |
| Spoke tracer link builds with correct fillet/walls | `spur info --spoke-count 4 --spoke-width 2 --hub-d 12 --rim-wall 1 --spoke-fillet 1` | `spoke_fillet_effective 1.0`, walls `1.025`/`1.0` | ✓ PASS |
| Honeycomb tracer link builds with correct count/walls | `spur info --hex-cell 3 --hex-wall 1` | `hex_cell_effective 3.0`, `hex_cell_count 18`, walls `1.525`/`2.149` | ✓ PASS |
| Honeycomb composes with a hex bore | `spur info --bore-hex 6 --hex-cell 3 --hex-wall 1` | `hex_cell_count 24`, walls `1.184`/`2.149` | ✓ PASS |
| Two patterns refused before CAD | `spur info --hole-count 6 --hole-d 4 --hole-circle-d 20 --spoke-count 4 --spoke-width 2 --hub-d 12 --rim-wall 1` | exit 2, one-pattern sentence naming both | ✓ PASS |
| Hub-wall breach refused one step past MIN_WALL | `spur info --hole-count 6 --hole-d 4 --hole-circle-d 14.7` | exit 2, hub-breach sentence | ✓ PASS |
| Hub-wall boundary accepted exactly at MIN_WALL | `spur info --hole-count 6 --hole-d 4 --hole-circle-d 14.75` | `cutout_hub_wall 0.4` | ✓ PASS |
| Reverse half-set warns, does not reject (confirms WR-04) | `spur info --hole-d 4 --hole-circle-d 20` | `warnings: ['No lightening holes with hole_count 0: ...']`, exit 0 | ✓ PASS (confirms README.md:151-152 is inaccurate — see WR-04) |
| Regression fixture unchanged | `git diff --exit-code tests/regression/pre_v0_2.json` | clean | ✓ PASS |
| `tests/test_calc.py` cutout-scoped tests | `pytest tests/test_calc.py -k "cutout or spoke or hole or hex or honeycomb or one_pattern or two_cutout or three_cutout"` | 76 passed | ✓ PASS |
| `tests/test_model.py` cutout-scoped tests | `pytest tests/test_model.py -k "cutout or spoke or hole or hex or honeycomb or recess_floor_fillet_survives or selector_takes_only"` | 96 passed (76.9s) | ✓ PASS |
| `tests/test_bench.py` sweep-pin tests | `make test PYTEST_ARGS="tests/test_bench.py -q"` | 10 passed | ✓ PASS |

Full `make verify` was not re-run per the verification-context instruction (already proven green at HEAD `90154aa`: 621 passed, 177.62s pytest / 178.55s wall, ruff/mypy --strict/import-boundary contracts/unfinished-work scan all clean, per `bench/RESULTS.md` and `11-09-SUMMARY.md`).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| REQ-spoke-cutout | 11-01, 11-04 | Spoke arms with fillet, capped to fit | ✓ SATISFIED | Spot check + `_spoke_cutters`/`spoke_fillet_effective` code + tests |
| REQ-hole-cutout | 11-03 | N lightening holes on a bolt circle | ✓ SATISFIED | Spot check + `_hole_cutters` code + tests |
| REQ-honeycomb-cutout | 11-02, 11-05 | Honeycomb web, cell count derived, cap analytic | ✓ SATISFIED | Spot check + `HEX_CELL_CAP`/`hex_cells` code + tests; cap methodology has an open review caveat (WR-01, see Human Verification) |
| REQ-one-cutout-pattern | 11-04, 11-05 | Exactly one pattern, 422 naming both/all | ✓ SATISFIED | Spot check confirms 422 with two patterns set |
| REQ-cutout-conflicts-refused-early | 11-03, 11-04, 11-05, 11-07 | Wall/overlap breaches refused before CAD work | ✓ SATISFIED | Spot checks (hub breach refused, boundary accepted) + kernel-boundary tests |
| REQ-cutout-composes | 11-03, 11-07, 11-08 | Composes with recesses and bore profiles | ✓ SATISFIED | Spot check (hex bore + honeycomb) + 13-row recess-fillet-survival test |
| REQ-cutout-derived-numbers | 11-03, 11-04, 11-05, 11-08, 11-09 | 5 fields report thinnest walls/fillet/count, null when off | ✓ SATISFIED | Code + spot checks + built-solid proof tests |

All 7 phase requirement IDs cross-referenced against `.planning/REQUIREMENTS.md`'s traceability table — all marked `Complete`, all mapped to Phase 11, no orphans (REQUIREMENTS.md's own "Coverage: 20 total, 20 mapped, 0 unmapped" holds for the milestone as a whole).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `docs/architecture/decision_log.md` | 1218-1221 | L30 states "the boundary itself builds, one step past it does not" — the opposite of what's proven and shipped | ⚠️ Warning (already tracked: 11-REVIEW.md WR-02, disposition `open`) | Misleads a future reader of the decision log about whether cutout `MIN_WALL` rules are kernel limits or design choices; confirmed still present at verification time |
| `README.md` | 151-152 | Claims the "reverse half-set" case (a cutout dimension set, count 0) is rejected; it actually builds and warns | ⚠️ Warning (already tracked: 11-REVIEW.md WR-04, disposition `open`) | User-facing documentation contradicts actual API behavior; reproduced live during this verification (see Behavioral Spot-Checks) |
| `docs/architecture/gear-maths/implementation.md` | 32 | Documents `cell_count_floor(cap, cell, wall, inner, outer)`; actual signature has no `cap` | ℹ️ Info (already tracked: WR-03, disposition `open`) | A developer calling as documented gets a `TypeError`; low impact, not user-facing |
| `bench/honeycomb_spike.py` | 170-174, 298-304 | `slower()`/verdict logic can silently discard a failed build trial in favour of a successful one; never checks confirmation/spelling rows for validity | ⚠️ Warning (already tracked: WR-01, disposition `open`) | Methodology gap in the exact script whose output produced `HEX_CELL_CAP = 120`, a constant that caps every honeycomb request in production — see Human Verification |
| `tests/test_model.py` | 1224-1240 | Filleted-spoke removed-volume check has no closed-form cross-check (pinned literal only), unlike holes/sharp-spokes/honeycomb | ℹ️ Info (already tracked: WR-05, disposition `open`) | A systematic geometry error in the new `_fillet_corner(inside=True)` path would be invisible to `make verify` forever; reviewer independently re-derived the math and found no actual defect |
| `bench/RESULTS.md`, `tests/test_bench.py` | 971, 273 | Misstate `hex_cell`'s default/legal-minimum as 3mm; actual default is 0 | ℹ️ Info (already tracked: IN-01, disposition `open`) | Documentation-only inaccuracy, no behavioral impact |

No `TBD`/`FIXME`/`XXX` debt markers found in any phase-modified file. No `TODO`/`HACK`/`PLACEHOLDER` markers found. All six findings above were independently confirmed present in the codebase at HEAD `90154aa` during this verification (not merely taken from `11-REVIEW.md`'s word) — none are new discoveries, all were already surfaced by Phase 11's own code review and remain at disposition `open` (recorded, not yet triaged) in `11-REVIEW-DISPOSITION.md`.

### Human Verification Required

See frontmatter `human_verification` for the full structured list. Summary:

1. **Spoke-arm MIN_WALL rule intent** — confirm the human's `approved` answer at the 11-01
   checkpoint (kept, refuses `0 < spoke_width < MIN_WALL`) matches what was actually wanted.
2. **`HEX_CELL_CAP = 120` and the `star` spelling, given WR-01** — both numbers were read off
   a loaded host, and the spike script that produced them has an open, unfixed methodology
   gap (can silently discard a failed trial). 11-06's independent sweep at the cap re-confirms
   every honeycomb row builds inside 30 s, but the "is 120 the *true* tightest cap" question
   is not fully settled.
3. **Honeycomb's 8.65 s cap-row vs D-11's own 7.5 s quarter-share budget** (a 1.15x overrun,
   already accepted once at 11-06's interactive checkpoint under host-load reasoning) —
   worth a final confirmation.
4. **The 33.39 s arithmetic total** (heaviest spoke re-run + Phase 10's chamfer row, not a
   composed build, measured under this project's heaviest-ever recorded host load) — confirm
   deferring to Phase 12's real composed sweep, per the filed tech-debt item, is the right call.
5. **Triage the five open code-review findings** (WR-01 through WR-05, IN-01) — two (WR-02,
   WR-04) were independently reproduced during this verification as real, if low-severity,
   documentation inaccuracies; none are currently `fixed`/`skipped`/`deferred`.

### Gaps Summary

No must-have truth failed, no artifact is missing or stub, no key link is unwired, and no
blocking anti-pattern was found — every one of the 7 phase requirements (REQ-spoke-cutout,
REQ-hole-cutout, REQ-honeycomb-cutout, REQ-one-cutout-pattern,
REQ-cutout-conflicts-refused-early, REQ-cutout-composes, REQ-cutout-derived-numbers) is
implemented, tested, and independently reproduced live during this verification with numbers
that match the phase's own SUMMARYs to the last measured digit. `make verify` is green at
HEAD (621 passed), the regression fixture is byte-unchanged, and both the security and
Nyquist validation audits report zero open items.

What keeps this out of a plain `passed`: five items are load-affected measurements or
already-recorded human policy decisions that this project's own process (11-VALIDATION.md's
"Manual-Only Verifications") correctly routes to a human rather than a test, plus one item
(triaging the still-open code-review findings, two of which were independently confirmed
here) that is explicitly a human-owned gate per `11-REVIEW-DISPOSITION.md`. None of these
represent incomplete or incorrect implementation — they are judgment calls this project's own
workflow reserves for a human, now presented together for that decision.

---

_Verified: 2026-09-29T11:43:13Z_
_Verifier: Claude (gsd-verifier)_
