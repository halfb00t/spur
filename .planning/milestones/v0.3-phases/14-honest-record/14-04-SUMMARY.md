---
phase: 14-honest-record
plan: 04
subsystem: testing
tags: [pytest, cadquery, closed-form, tripwire, decision-log, tech-debt, gap-closure]
gap_closure: true
gap_ids: [G-14-2, G-14-5]

requires:
  - phase: 14-honest-record (14-02)
    provides: "the abs=1e-9 shared assertion, the filleted-spoke oracle, the plain-row gaps (61e1bea)"
  - phase: 14-honest-record (14-03)
    provides: "L33, the decision-log entry this plan corrects in place (9fb667d)"
provides:
  - "_holes_volume and _hex_cells_volume: pure-math oracles shared by the proof, the tripwire and the composed rows"
  - "a skip-the-cutout tripwire whose holes and cells rows are discriminating (control call passes on the unpatched build first)"
  - "the d-flat, round and keyed holes rows (tip chamfer, both recesses) on the web formula at abs=1e-8, the single-sided holes row at abs=1e-9"
  - "the debt file narrowed to eleven rows, L33 corrected in place, every 'no closed form exists' reworded to 'not derived here'"
affects: [phase-14-verification, 14-REVIEW WR-02 and WR-03]

actuals:
  tokens: 7467
  tasks: 3
  commits: 2
plan_head_before: 7cb0c7d86c49b115d5bfb5f9680a57376fb33ed3
commits: 2
plan_head_after: 48928533f6cd18fcdf58b475316ebd1326fed902

tech-stack:
  added: []
  patterns:
    - "one closed-form oracle per cutout pattern, shared by the proof, its tripwire and the composed rows"
    - "a tripwire runs the shared assertion on the unpatched build before the patch, so pytest.raises can only be satisfied by the patch"
    - "a None d_volume in a parametrize row is derived in the test body, not pinned"

key-files:
  created: []
  modified:
    - tests/test_model.py
    - docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md
    - docs/tech_debt/INDEX.md
    - docs/architecture/decision_log.md
    - .planning/phases/14-honest-record/14-REVIEW-DISPOSITION.md

key-decisions:
  - "Task 2 answer: noise-multiple 1e-8 -- the three tip-chamfer holes rows assert at abs=1e-8 (about 15x their largest measured gap), the single-sided holes row at abs=1e-9"
  - "A third bar keyword, volume_abs, on the shared assertion: volume_rel set uses the relative bar, else volume_abs, else the abs=1e-9 default kept verbatim"

patterns-established:
  - "A bar set from a measured gap is the human's choice, logged in L33, never the executor's (D-06)"

requirements-completed: [REQ-filleted-spoke-closed-form]

coverage:
  - id: D1
    description: "The skip-the-cutout tripwire's holes and cells rows take closed-form volumes and a control call passes on the unpatched build before the monkeypatch (G-14-2)"
    requirement: REQ-filleted-spoke-closed-form
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_the_cutout_proof_fails_when_the_cutout_step_is_skipped"
        status: pass
    human_judgment: false
  - id: D2
    description: "The four hole-through-web composed rows assert the web formula at the bar the human chose, hex-holes, spokes and cells unchanged at volume_rel=1e-6 (G-14-5)"
    requirement: REQ-filleted-spoke-closed-form
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_the_recess_fillet_and_cutout_proofs_hold_with_a_single_sided_recess"
        status: pass
    human_judgment: false
  - id: D3
    description: "The debt file, L33 and three docstrings say the closed form is not derived here, never that none exists (G-14-5)"
    verification: []
    human_judgment: true
    rationale: "Wording of the record: the claim scan proves the old phrases are gone, only a reader can judge that the new sentences are true and sufficient"

duration: 70min
completed: 2026-10-03
status: complete
---

# Phase 14 Plan 04: Gap closure for G-14-2 and G-14-5 Summary

**The skip-the-cutout tripwire's holes and cells rows now fail only when the cutout is skipped (closed-form volumes, control call before the patch), four hole-through-web composed rows assert the web formula (abs=1e-8 on the three tip-chamfer rows, abs=1e-9 on the single-sided row), and the debt file, L33 and three docstrings say "not derived here".**

## Performance

- **Duration:** about 70 min wall clock from the plan's base commit (12:27 to 13:37 +06:00), including the Task 2 checkpoint pause
- **Completed:** 2026-10-03
- **Tasks:** 3 (Task 1 tracer, Task 2 measurement checkpoint, Task 3)
- **Files modified:** 5 (tests/test_model.py, the debt file, its INDEX row, decision_log.md, 14-REVIEW-DISPOSITION.md)

## Accomplishments

- G-14-2: `_holes_volume(p, recesses)` and `_hex_cells_volume(p)` sit after `_filleted_spoke_volume`, pure math, bit-identical to the proof's old inline expressions (14-02's recorded gaps 2.39e-12 and 8.87e-12 mm3 still describe them). The tripwire's parametrize holds no float literal but the 0.0 angles.
- G-14-2: the tripwire calls the shared assertion on the unpatched build before `monkeypatch.setattr`, so `pytest.raises(AssertionError)` can only be satisfied by the skipped cutout. L33's sentence "all three skip-the-cutout tripwire rows run at `abs=1e-9`" needed no change and is now true.
- G-14-5: the d-flat, round and keyed holes rows and the single-sided holes row take `d_volume` from `_holes_volume` (2 recesses / 1 recess). hex-holes, every spokes row and every cells row keep their 6 dp literal at `volume_rel=1e-6`.
- G-14-5: debt narrowed to eleven rows (stays in `docs/tech_debt/active/`, INDEX link text equals the new title, Next step names the recess-split integral), L33 corrected in place, three docstrings reworded.

## Task 2: measurement and the human's answer

Measured 2026-10-03 on cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1, Python 3.12.13. Two byte-identical runs by the Task 2 executor, reproduced to every digit again by the continuation executor before Task 3. Kernel delta is `reference.Volume() - cut.Volume()`.

| Row | Kernel delta (mm3) | Formula (mm3) | Signed gap | Abs gap |
|---|---|---|---|---|
| d-flat-holes (tip chamfer, both recesses) | 263.8937829021279 | 263.89378290154264 | +5.853e-10 | 5.85e-10 |
| round-holes | 263.89378290213654 | 263.89378290154264 | +5.939e-10 | 5.94e-10 |
| keyed-holes | 263.8937829021979 | 263.89378290154264 | +6.553e-10 | 6.55e-10 |
| single-sided holes | 414.6902302738499 | 414.6902302738527 | -2.785e-12 | 2.79e-12 |
| diagnostic: d-flat-holes without tip_chamfer | 263.893782901544 | 263.89378290154264 | +1.364e-12 | 1.36e-12 |

Case B: every gap at or below 1e-9, the three tip rows above 1e-10 (about 1.5x headroom against the 1e-9 bar). The tip chamfer shifts the kernel's volume difference by about 6e-10 mm3, systematic and not noise; without it the same row's gap is 1.36e-12. The single-sided row is about 360x inside 1e-9.

The measurement reproduced the human's pre-recorded bands (tip rows between 5e-10 and 7e-10, single-sided at or below 1e-10), and the human confirmed the same answer at this checkpoint.

**Task 2 answer: noise-multiple 1e-8**

The three tip-chamfer holes rows assert at `abs=1e-8` (about 15x the largest measured gap, 6.55e-10) on `_holes_volume(p, 2)`; the single-sided holes row asserts at `abs=1e-9` on `_holes_volume(p, 1)`. Task 3 implemented this with a `volume_abs` keyword on the shared assertion and logged 1e-8 in L33.

## Task Commits

1. **Task 1 (G-14-2): closed forms for the tripwire's holes and cells rows, control call before the patch** - `a4347be` (test). `pytest -k "each_cutout_is_exactly or cutout_proof_fails_when_the_cutout_step"`: 7 passed; the pre-commit `make verify` hook passed.
2. **Task 2 (G-14-5 measurement checkpoint):** no commit by design; nothing under tests/ or docs/ moved before the human answered.
3. **Task 3 (G-14-5): the four rows on the web formula, wording, debt, L33** - `4892853` (test). Hook passed; targeted `pytest -k` gives 23 passed; `make verify` run once more on the committed tree, last line: `927 passed in 212.90s (0:03:32)`.

**Plan metadata:** the closing `docs(14-04)` commit that carries this SUMMARY, STATE.md, ROADMAP.md and 14-REVIEW-DISPOSITION.md.

_TDD note: Task 3 is `tdd="true"` but the plan prescribes one commit for the test change, debt narrowing and L33 correction. The RED step was run uncommitted: the bar spy failed on the unchanged tree (`d-flat-holes` reached the shared assertion as `(263.893783, 1e-06, None)`) and passed after the change (`bar ok`)._

## Files Created/Modified

- `tests/test_model.py` - `_holes_volume`, `_hex_cells_volume`, the discriminating tripwire with its control call, `volume_abs` on the shared assertion, the four hole-through-web rows, reworded docstrings
- `docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md` - retitled "Eleven ...", the four moved rows with their measured gaps and bars, the recess-split Next step
- `docs/tech_debt/INDEX.md` - the Active row's link text now equals the new title
- `docs/architecture/decision_log.md` - L33 edited in place: the composed-row passage, `Reason:` and `Kernel:`; the paraphrase of L30 and the tripwire sentence left as they were
- `.planning/phases/14-honest-record/14-REVIEW-DISPOSITION.md` - WR-02 and WR-03 set to `fixed` citing `a4347be` and `4892853`, `open: 4`

## Decisions Made

- The 1e-8 bar for the three tip rows is the human's (D-06): a bar set from a measured gap, chosen by the human at this checkpoint and logged in L33, not tuned by the executor.
- L33's one sentence "no tolerance was loosened and none was set from a measured gap" was scoped to "these four rows" (the plain formula rows it describes), since the tip rows' 1e-8 is a bar set from a measured gap by the human's choice.
- `volume_abs` precedence: `volume_rel` first, then `volume_abs`, then the existing `abs=1e-9` line verbatim, so no formula row changes.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The cells row of the tripwire failed its own control call on a correct build**
- **Found during:** Task 1 (the control call before the monkeypatch)
- **Issue:** the tripwire passed `rim_angle=0.0` for the cells row, but the proof probes the rim at the farthest honeycomb-cell vertex; the new control call failed on the correct, unpatched build. This is the discrimination gap G-14-2 describes, found by the new control.
- **Fix:** the tripwire's parametrize gains a `rim_angle` column (`angle` renamed `hub_angle`) and a module constant `_CELLS_NO_RECESS`, so the cells row uses `_honeycomb_farthest_vertex_angle`.
- **Files modified:** tests/test_model.py
- **Verification:** `pytest -k "each_cutout_is_exactly or cutout_proof_fails_when_the_cutout_step"` gave 7 passed
- **Committed in:** `a4347be`

---

**Total deviations:** 1 auto-fixed (1 bug, in Task 1). L33 needed no change for G-14-2.
**Impact on plan:** the fix is the control call doing its job; no scope creep.

## Issues Encountered

None beyond the deviation above.

## Verification

- `pytest -k "every_feature_proof_holds_on_a_tip or proofs_hold_with_a_single_sided or each_cutout_is_exactly or cutout_proof_fails"`: 23 passed.
- Bar spy (the plan's verify with the expected tuples edited to the `noise-multiple` answer): d-flat, round and keyed holes reach the shared assertion as `(_holes_volume(p, 2), None, 1e-08)`, single-sided as `(_holes_volume(p, 1), None, None)`, hex-holes as `(263.92552, 1e-06, None)`; prints `bar ok`.
- Claim scan, debt check and 14-03's L33 check: `claims ok`, `debt ok`, `L33 ok`. Decision-log numstat against 5d9e907 deletes 0 lines. `src scope ok`: no src/ change, `tests/regression/pre_v0_2.json` and `src/spur/params.py` byte-identical to 5d9e907.
- `make verify` on the committed tree: `927 passed in 212.90s (0:03:32)`.

## Kept on purpose (claim-scan exceptions)

- `_assert_the_recess_fillet_survives`'s Phase 11 docstring (tests/test_model.py): "no closed form gives the fragment count after an arbitrary boolean cut" is about a face-fragment count, not a volume, and stays true.
- L33's paraphrase of L30 (decision_log.md, "pinned because it has no closed form"): it quotes the claim in order to answer it.
- The resolved filleted-spoke debt file's Resolution (`docs/tech_debt/resolved/2026-09-29-filleted-spoke-volume-proof-pinned-not-derived.md`): a dated record of `61e1bea`'s state.

`.planning/` history files (REVIEW, UAT, VERIFICATION, earlier SUMMARYs) record what was said at the time and were not edited.

## Tangent, raised and not changed

`test_the_hole_link_cuts_six_holes_through_the_recessed_floor` (tests/test_model.py, the web formula around lines 901-903) asserts the same web formula at `rel=1e-6` on the default gear. It is outside G-14-5's four rows and the human decides whether it moves.

## Debt

One item updated in place (`docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md`, now eleven rows); none filed.

## Known Stubs

None.

## Threat Flags

None. No network endpoint, auth path, file access or schema change was added; only test code, docs and the decision log changed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both UAT gaps are closed in the working tree; `/gsd-verify-work 14` can re-check G-14-2 and G-14-5.
- WR-01 (CI-platform calibration of the abs bars) stays open in the review disposition; the three tip rows now sit about 15x inside their bar, which is the margin WR-01 asked for.

## Self-Check: PASSED

- Files found: tests/test_model.py, the debt file, docs/tech_debt/INDEX.md, docs/architecture/decision_log.md
- Commits found: a4347be, 4892853
- `commits:` measured from the on-disk ledger: `git rev-list --count 7cb0c7d86c49b115d5bfb5f9680a57376fb33ed3..HEAD` gave 2

---
*Phase: 14-honest-record*
*Completed: 2026-10-03*
