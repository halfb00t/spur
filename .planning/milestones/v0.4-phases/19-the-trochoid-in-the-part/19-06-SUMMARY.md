---
phase: 19-the-trochoid-in-the-part
plan: 06
subsystem: calc
tags: [trochoid, hob-root, derive, root_form_d, root_waist, undercut, warnings, gear-maths-docs]

requires:
  - phase: 19-the-trochoid-in-the-part
    provides: 19-02's adopted waist floor, field name and bars; 19-04's RootMode.curve, root_shape end to end and the silenced undercut sentence
provides:
  - "DerivedDimensions.root_form_d (round(2 * R_join, 3), the cutter-envelope junction, not an ISO 21771 form diameter) and DerivedDimensions.root_waist (round(2 * R_w * h_w, 3)), directly after root_fillet, mm, null unless the trochoid root applies"
  - "ROOT_WAIST_FLOOR = 0.4 mm absolute with the walk, the human's choice, the headroom and the small-module caveat beside it; the waist thin sentence below it, never a refusal"
  - "the undercut sentence restated from the cutter actually used (onset rounded up to 0.1 teeth, avoiding shift rounded up to 0.001, none printed above the field's 1.0); radial mode and a refused request keep the shipped sentence byte for byte"
  - "the cap sentence under root_fillet names root_fillet and says the printed radius is within 0.001 mm of the largest that keeps a tip land"
  - "two DIMS rows in the UI; the 31-name DerivedDimensions set; docs/architecture/gear-maths/ true for the hob root"
affects: [19-07, 19-08, 19-09, 19-10]

# Actuals (#2632): chars/4 over the added lines of src, tests and docs, 6754aaa..8504a92.
actuals:
  tokens: 10609
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "a bound printed in a warning is rounded the safe way after removing float residue (math.ceil(round(v * 10**k, 9)) / 10**k), and the test reads the cutter's own roll one step either side"
    - "a number compared at the resolution it prints (round(waist, 3) < floor), the lead-in warning's rule"
    - "a mutation run (change the code, watch the named test fail, restore) shows each new test has teeth"

key-files:
  created: []
  modified:
    - src/spur/calc.py
    - src/spur/static/app.js
    - tests/test_trochoid.py
    - tests/test_api.py
    - docs/architecture/gear-maths/implementation.md
    - docs/architecture/gear-maths/tests.md
    - docs/architecture/gear-maths/errors_and_logging.md

key-decisions:
  - "ROOT_WAIST_FLOOR is its own literal 0.4, equal to MIN_TIP_FDM by the human's choice (floor-print) but not bound to it, so a change to the tip warning does not move the waist floor without a new walk"
  - "The restated undercut sentence fires on rm.curve.join == crossing, not on the printed onset (the plan's flagged assumption): a join inside the 1e-4 rb band reads tangent and prints nothing, exactly as its part is built"
  - "PROFILE_SHIFT_MAX = 1.0 is written once in calc.py (it imports params for typing only); a test reads the schema's maximum to keep the two equal"
  - "The waist sentence names teeth, profile_shift and pressure_angle (D-06) and says thickens, not clears: 3,901 seeded random trochoid gears, one step up in each, none got thinner; on module 0.2 no change of the three reaches the floor, so it promises a direction only"

patterns-established:
  - "A test that separates two predicates for the same word picks rows where they disagree (sharp cutter at 18 teeth, 14.5 degrees at 30 and 31 teeth), and the mutation of the gate to the wrong predicate fails it"

requirements-completed: [REQ-derived-numbers-honest-under-trochoid, REQ-undercut-warning-restated, REQ-cutter-tip-radius-settable]  # declared by this plan; requirements.ready-ids (#2388) answered 1/3 ready after this SUMMARY: REQ-derived-numbers-honest-under-trochoid was marked complete, REQ-undercut-warning-restated and REQ-cutter-tip-radius-settable are also declared by a sibling with no SUMMARY yet and were left for its last declaring plan

coverage:
  - id: D1
    description: "root_form_d and root_waist are printed where the trochoid applies and null elsewhere: 30.558 and 3.303 on the default gear (the waist equal to the involute's thickness at the junction through Profile.half_angle and the file's own involute formula, not the curve), 9.451 and 1.473 on the 10-tooth crossing; null in radial mode, on a refused request and on all 44 fixture records"
    requirement: REQ-derived-numbers-honest-under-trochoid
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_root_form_d_is_twice_the_junction_radius_and_null_when_radial"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_root_waist_is_printed_where_the_trochoid_applies_and_null_elsewhere"
        status: pass
      - kind: unit
        ref: "tests/test_api.py#test_openapi_documents_the_typed_contracts"
        status: pass
      - kind: unit
        ref: "tests/regression (86 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The waist warning fires one 0.001 mm printed step under the 0.4 mm floor and not at it, on two series of the 19-02 walk, the gear valid either way; the comparison is round(waist, 3) < floor"
    requirement: REQ-derived-numbers-honest-under-trochoid
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_waist_warning_fires_one_print_step_below_the_floor_and_not_at_it"
        status: pass
    human_judgment: false
  - id: D3
    description: "The undercut sentence is restated from the cutter actually used: onset and avoiding shift rounded up, the cutter's roll non-negative at the printed shift and negative one step below, none printed above 1.0, the trimmed cutter's numbers for a trimmed tip radius, no radial-root wording; a tangent join, a gear nobody asked about and a refused request keep their shipped behaviour, the shipped sentence equal to the fixture's string"
    requirement: REQ-undercut-warning-restated
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_restated_undercut_sentence_fires_at_17_teeth_and_not_18"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_advised_shift_is_rounded_up_and_flips_the_gear_out_of_undercut"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_a_shift_above_the_field_s_range_is_never_advised"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_onset_is_the_trimmed_cutter_s"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_a_refused_trochoid_request_keeps_the_shipped_undercut_sentence"
        status: pass
    human_judgment: false
  - id: D4
    description: "The cap sentence a user reads under root_fillet in trochoid mode names root_fillet and says within 0.001 mm of the largest; 0.471 silent, 0.472 trimmed to 0.471 with the sentence, 0.4715 used as given and silent, 0 a legal sharp hob; the whole warnings tuple of a five-sentence gear is pinned in order and ASCII"
    requirement: REQ-cutter-tip-radius-settable
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_trimmed_tip_radius_is_printed_and_warned_one_step_either_side_of_the_cap"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_every_root_sentence_is_ascii_and_in_a_fixed_order"
        status: pass
    human_judgment: false
  - id: D5
    description: "root_form_d is never labelled an ISO form diameter where a user reads it (UI label, schema description, README)"
    requirement: REQ-derived-numbers-honest-under-trochoid
    verification:
      - kind: unit
        ref: "tests/test_api.py#test_root_form_d_is_never_labelled_an_iso_form_diameter_where_a_user_reads_it"
        status: pass
    human_judgment: false
  - id: D6
    description: "docs/architecture/gear-maths/ describes what calc now prints for the hob root: the fields, the floor and its caveat, RootMode.curve, the changed signatures, the sentences and the tests"
    requirement: REQ-derived-numbers-honest-under-trochoid
    verification:
      - kind: other
        ref: "the plan's docs check (prints 'gear-maths docs brought true')"
        status: pass
    human_judgment: true
    rationale: "Whether the prose is true and readable is a reviewer's judgment; the check only proves the named terms are present. Numbers were copied from bench/RESULTS.md and the code, and the sentences from derive()."

duration: "11 min"
completed: 2026-10-09
status: complete
plan_head_before: 6754aaa1d75005b41ae05fafb5be496a3c304b30
plan_head_after: 8504a92d13eaa66817171ef53924a3f11b887495
commits: 3
---

# Phase 19 Plan 06: Every number beside the hob root has a proof or a warning Summary

**`derive()` now prints the hob root's junction diameter (`root_form_d`, 30.558 on the default gear) and narrowest tooth (`root_waist`, 3.303, warned under a 0.4 mm floor), restates the undercut sentence from the cutter that cut the part with a shift that really avoids it (rounded up, never above the field's 1.0), and words the tip-radius cap honestly; the radial sentences and the fixture are byte-identical.**

## Performance

- **Duration:** 11 min of wall time (04:26:40Z to 04:38:04Z), of which the one `make verify` is 95 s
- **Started:** 2026-10-09T04:26:40Z
- **Completed:** 2026-10-09T04:38:04Z
- **Tasks:** 3
- **Files modified:** 7 (`src/spur/calc.py`, `src/spur/static/app.js`, `tests/test_trochoid.py`, `tests/test_api.py`, three gear-maths docs)

## Accomplishments

- **`root_form_d` and `root_waist` (D-04, D-06).** Two `float | None` fields directly after `root_fillet`, unit mm, no default, null in radial mode, on a refused request and on all 44 fixture records. `root_form_d = round(2 * curve.points[-1][0], 3)`: 30.558 on the default gear (checked against `2 * sqrt(rb^2 + xi^2)` written out in the test), 9.451 on the 10-tooth, module 1, 20 degree, backlash 0, tip radius 0.38 gear. `root_waist = round(2 * R_w * h_w, 3)`: 3.303 on the default gear, equal on that tangent join to the involute's own thickness at the junction through `Profile.half_angle` and through the test file's separately written involute (an independent check); 1.473 on the 10-tooth crossing, below the involute's 1.622 at its junction. The description calls `root_form_d` the cutter-envelope junction and "not an ISO 21771 form diameter"; the UI labels are "Hob root junction Ø" and "Narrowest tooth in the root"; a test keeps the phrase out of any label.
- **`ROOT_WAIST_FLOOR = 0.4` mm, absolute, with its provenance (D-07).** The comment carries the 19-02 walk (1,098 gears, 37 `tooth severed`, 1,061 all built, worst oracle reading 6.8995e-5 mm, thinnest built waist 3.2325e-3 mm), why that makes the floor a printability choice (no failure signature; 124x the thinnest built waist, 5.8e3x the worst reading), the human's `floor-print` adoption ("take the recommendations", ids mapped by the orchestrator), host and dates, the firing counts (294 of 1,061 walk gears, 771 of 10,326 product gears) and the **small-module caveat: 595 of the 616 module-0.2 gears warn, 195 of them on tangent joins with no undercut at all, against 176 of 9,710 at module 1 and above**. The same caveat is in `errors_and_logging.md` and `implementation.md`. The sentence never says "undercut" for that reason.
- **The undercut sentence restated (REQ-undercut-warning-restated, T-19-12).** Where the trochoid applies and `curve.join == "crossing"`, `_undercut_advice(rm.cutter)` prints the onset `ceil(round(undercut_teeth * 10, 9)) / 10` and the shift `ceil(round(undercut_shift * 1000, 9)) / 1000` of the cutter actually used. 10 teeth (module 1, 20 degrees, backlash 0, tip radius 0.38 mm) advises **0.416**: the cutter's roll is +2.7e-3 mm there and negative at 0.415 (to nearest it would have printed 0.415, still undercut at -7.9e-5 mm). 17 teeth print "Below 17.1 teeth ... 0.006 or more", 18 teeth print nothing. A request of 3.0 mm on 12 teeth is cut at 0.471 and the sentence is that cutter's (16.1 teeth, 0.239). 6 teeth at 14.5 degrees with a sharp cutter need 1.0619, above the field's 1.0, so the sentence says no shift in range avoids it and prints none; 8 teeth at 14.5 degrees (0.99924) print 1.000 and 7 teeth at 15.5 degrees (1.00004) print none. A mutation run (nearest instead of ceil, residue removal off, range guard off, waist compared unrounded, gate on the shipped `z_min`) failed the named tests each time; the last survived the first draft of the 17/18 test, which is why that test now carries the rows where the two predicates disagree (sharp cutter at 18 teeth; 14.5 degrees at 30 and 31 teeth).
- **Radial mode and a refused request untouched.** The shipped sentence is compared byte for byte against the string read from the fixture JSON (`Below 51.0 teeth a cut gear would be undercut; this model uses a radial root instead.`) beside the refusal sentence on the 6-tooth, 14.5 degree, shift -0.6 gear. `tests/regression`: 86 passed; the fixture and `cli.py` are byte-identical to the phase base (the SC1 check printed `SC1 holds`).
- **The cap sentence (REQ-cutter-tip-radius-settable).** "root_fillet is the hob's tip radius here, and it was reduced to 0.471 mm, within 0.001 mm of the largest that keeps the cutter a tip land at this pressure angle and backlash." Pinned one step either side at module 1, 20 degrees, backlash 0 (cap 0.47191 mm): 0.471 used and silent, 0.472 trimmed to 0.471 with the sentence, 0.4715 used as given, printed 0.471, silent, 0 a legal sharp hob. The 0.293 mm row of the older cap test was re-captured.
- **Docs.** `implementation.md` gains rows for `ROOT_WAIST_FLOOR`/`PROFILE_SHIFT_MAX`, `_undercut_advice`, `DerivedDimensions`, `derive()`'s warning order and the new `_ROOT_SENTENCES` keys, and the stale `spline_start`, `tip_chamfer_limit`/`tip_chamfer_effective` and `RootMode` rows are updated; `tests.md` lists the 19-04 and 19-06 calc-tier tests and corrects "21 tests" (70 functions, 405 collected cases); `errors_and_logging.md` has the new section "The hob-cut (trochoid) root". `ROOT_CURVE_POINTS`' comment now says where the bar lives. `strategy.md` is 19-10's and was left alone.

### Captured sentences (L33), from `derive()` on 2026-10-09 and typed into the tests after capture

- Undercut: "Below 17.1 teeth this cutter undercuts the gear, and the root is cut the way the hob cuts it; a profile shift of 0.006 or more avoids the undercut." (17 teeth); "... a profile shift of 0.416 or more avoids the undercut." (10 teeth); "Below 16.1 teeth ... 0.239 ..." (12 teeth, request 3.0).
- Out of range: "Below 39.9 teeth this cutter undercuts the gear, and the root is cut the way the hob cuts it; no profile shift up to 1 avoids the undercut at this pressure angle and tip radius."
- Cap: "root_fillet is the hob's tip radius here, and it was reduced to 0.471 mm, within 0.001 mm of the largest that keeps the cutter a tip land at this pressure angle and backlash." (0.293 and 0.661 mm in the other two tests)
- Waist: "The tooth is only 0.399 mm thick at its narrowest in the hob-cut root, under the 0.4 mm this design holds for a printable tooth; more teeth, a larger profile_shift or a larger pressure_angle thickens it."

### Floor and the tuned shifts the floor test landed on

`ROOT_WAIST_FLOOR` = **0.4 mm, absolute** (not a multiple of the module). Profile shifts found by 60 halvings (module 1, 14.5 degrees, default backlash 0.10, tip radius 0.38 mm):

| Gear | Waist 0.400 (silent) | Waist 0.399 (warns) |
|---|---|---|
| 8 teeth, bisected over [-0.6, 0] | -0.5135896205570665 | -0.5143215951869762 |
| 6 teeth, bisected over [-0.57, 0] | -0.31063950975425636 | -0.31129343996754943 |

## Task Commits

1. **Task 1: root_form_d, root_waist, the floor and the UI rows** - `6032926` (feat)
2. **Task 2: the restated undercut sentence, the cap sentence, the order test** - `fe8fed9` (feat)
3. **Task 3: gear-maths docs** - `8504a92` (docs)

**Plan metadata:** the docs commit that carries this SUMMARY, STATE.md, ROADMAP.md and `.planning/state.json`.

`commits: 3` is measured from the ledger: `git rev-list --count 6754aaa..HEAD` read 3 at SUMMARY write.

## Decisions Made

See `key-decisions`. In short: the floor is its own constant at 0.4 (not tied to `MIN_TIP_FDM`); the sentence fires on the join, not the printed onset; `PROFILE_SHIFT_MAX` is written once and pinned to the schema by a test; the waist sentence promises a direction, not a cure.

## Deviations from Plan

### Plan-literal items that did not apply as written

**1. The five-sentence ordering gear is 6 teeth, not 12.** The plan names 12 teeth, module 1, 20 degrees, backlash 0 and says to find the shift from the walk table. Measured 2026-10-09, that gear's waist is 0.941 mm at shift -0.6 and rises with the shift, so it never goes under 0.4 mm and cannot fire the waist sentence. The gear used is 6 teeth, module 1, 14.5 degrees, shift -0.5, backlash 0.10, `root_fillet` 3.0 (cut at 0.661), tip chamfer 3.0 (cut at 0.38), waist 0.262 mm: cap, thickness, tip-chamfer, undercut and waist, five of them, asserted as a whole tuple in order. The tip-FDM and the radial-only sentences cannot fire on a hob-root gear, so the order they hold relative to the rest is pinned by the radial tests that already exist, not by this one.

**2. A number written before it was measured.** Not a plan item: my own first draft of the waist test docstring said the involute's thickness at the 10-tooth junction was 1.560 mm; the run read 1.622 mm and the docstring and assertion were corrected before the commit (a draft number written before it was measured).

**3. [Rule 3 - Blocking] Line length.** The first commit attempt failed `ruff` (E501, two lines in the new test) at the pre-commit hook; shortened and recommitted. Nothing committed in the failed attempt.

**4. [Rule 2 - Missing Critical] Two tests the plan did not list.** `test_root_form_d_is_never_labelled_an_iso_form_diameter_where_a_user_reads_it` (the plan's `prohibitions` entry says `verification: test`, and none of the ten named tests covers the UI label, the schema description and README) in `tests/test_api.py`, which the plan already lists; and two extra rows in the 17/18 test (see Accomplishments) after the gate-on-the-wrong-predicate mutation survived. Both are in files the plan lists.

**5. Task 1 and Task 2 are `tdd="true"` but code-first in part.** The plan is `type: execute`, so the plan-level gate does not apply. Task 1's tests went in with the code in one commit (the first run of the form_d/waist test caught my wrong 1.560, a number, not behaviour); Task 2's tests were written after the code and shown to have teeth by the mutation run described above (5 mutations of `calc.py`, each restored and diffed against a copy), not by a RED commit.

**Total deviations:** 2 auto-fixed (1 Rule 2, 1 Rule 3) and 3 plan-literal items. **Impact on plan:** none on behaviour.

## Issues Encountered

- **Gate result:** `make verify` exit 0, **`1081 passed in 94.62s (0:01:34)`**, coverage **97.90 %** (floor 96); ruff, mypy `--strict` (43 source files), 5 import contracts kept, unfinished-work scan clean. Host load at the start was 3.08 (1-minute), 4.42 and 6.62 (5- and 15-minute). That is 95 s against 19-04's and 19-05's 117 to 131 s at loads 5.5 to 9: the gate cost is host-load dependent as 19-04 said, and L34's 66 s bar stays 19-09's question; nothing was done about it here. 12 tests were added by this plan to the 1069 of 19-05 (1081).
- **No `ReentrantCallError` or other flake appeared** in the full gate or in the three pre-commit hooks (one of them rejected for E501, which is lint, not the flake), so the resource-tracker debt item's trigger did not fire and no log was kept under `investigation/`.
- **Commit attribution line.** Commits end with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, the line the session's attribution reminder gives. The dispatch text named `Claude Fable 5.1` in its CLAUDE.md note; `CLAUDE.md` itself names neither, so the reminder was followed, as 19-05 did.
- **State file.** `.planning/state.json` changes with the state handlers and is committed with them, not left modified.

## Known Stubs

None. No placeholder values, empty data flows or TODO markers were added.

## Threat Flags

None. T-19-12 (advice that still undercuts, or a shift outside the field) is mitigated: both bounds rounded up after residue removal, nothing printed above 1.0, the tests read the cutter's roll at the printed shift and one step below. T-19-13 (a plausible number mislabelled, or one without proof) is mitigated: `root_form_d` is the Phase 18 curve's junction labelled as such in the description and the UI, the waist is checked independently through `Profile.half_angle` on a tangent join, and both are null wherever the trochoid does not apply. No new network, auth or file surface.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 19-07 and 19-08 compose the trochoid column with the other families. `tests/composition.py` `ALWAYS` still lists `root_thickness` and `root_gap` as always non-null, wrong for any `root_shape="trochoid"` row (19-04 said so), and now `root_form_d` and `root_waist` are non-null exactly on those rows.
- 19-09 still owns the gate cost (95 to 131 s on this host, host-load dependent, against L34's 66 s) and the bench swap of `trochoid_outline` for `spur.model._outline(pr, 0.0, curve=...)`.
- 19-10 should cite the floor's value, the small-module caveat (595 of 616 module-0.2 gears) and the bars from `bench/RESULTS.md` "Bars adopted (19-02)" when it writes L38, and `strategy.md` is its to update.
- The 19-04 gap (a trochoid request on an undercut gear printed no undercut sentence) is closed.
- Files filed: no debt or idea item was filed by this plan.

## Self-Check: PASSED

- Files: `src/spur/calc.py`, `src/spur/static/app.js`, `tests/test_trochoid.py`, `tests/test_api.py` and the three `docs/architecture/gear-maths/` files exist; this SUMMARY is at `.planning/phases/19-the-trochoid-in-the-part/19-06-SUMMARY.md`.
- Commits `6032926`, `fe8fed9` and `8504a92` are ancestors of HEAD; `git rev-list --count 6754aaa..HEAD` read 3.
- Acceptance: the `form_d and waist printed under the hob root` line, the `derived-number tests present` line, the `SC1 holds` line and the `gear-maths docs brought true` line all printed; `tests/regression` 86 passed; `root_form_d` and `root_waist` sit directly after `root_fillet` in `DerivedDimensions`, `ROOT_WAIST_FLOOR` exists with the walk and the human's choice in its comment, `app.js` has the two rows and no label contains "form diameter".

---
*Phase: 19-the-trochoid-in-the-part*
*Completed: 2026-10-09*
