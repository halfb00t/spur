---
status: complete
phase: 14-honest-record
source: [14-VERIFICATION.md]
started: 2026-10-03T12:00:00Z
updated: 2026-10-03T11:55:00Z
---

## Current Test

[testing complete]

## Tests

### 1. 14-02 deviation: shared cutout assertion gained opt-in volume_rel; 15 composed rows (12 tip-chamfer, 3 single-sided-recess) assert at rel=1e-6
expected: Accept as an override, or require the 15 literals re-pinned at full precision
result: pass
note: "override accepted by the human 2026-10-03 -- the 15 composed rows stay at rel=1e-6; SC3's four rows are at abs=1e-9"

### 2. WR-02: L33 says all three skip-the-cutout tripwire rows run at abs=1e-9, but holes/cells literals are 6 dp and the face-delta assert fires first on holes and spokes-filleted
expected: L33 states only what the rows prove, or the rows prove what L33 states (reword L33, or make the rows discriminating)
result: issue
reported: "the second recommended option"
severity: major
decision: "make the rows discriminating -- holes and cells take their d_volume from the closed forms, and the tripwire asserts the shared call passes on the unpatched build before the monkeypatch; L33 untouched"

### 3. WR-01: abs=1e-9 gaps measured on macOS arm64 only; CI is ubuntu-latest
expected: All four kernel-to-formula gaps stay far below 1e-9 mm3 on CI; record next to the arm64 ones
result: pass
note: "bound proven on CI run 37099687748 (PR #17, ubuntu-24.04): 927 passed in 297.20s, same count as local, 0 failures, so the four abs=1e-9 rows and the rim-corner tripwire ran and held. The values clause is unmet by human choice 2026-10-03: the suite asserts the bound and prints no gaps, so no ubuntu numbers exist to record next to the arm64 ones"

### 4. README number guard: no repo test enforces "no number in README the tests do not prove"
expected: Accept the verifier's manual check (1.188, 1.25, 0.125 only, each a test row value), or ask for a repo test guarding README numbers
result: pass
note: "manual check accepted by the human 2026-10-03: 1.188 is the default-gear test row, 1.25 is calc.py's dedendum coefficient (a definition), 0.125 and 'halfway up the tooth' are the three mid-tooth rows; no README-number test added"

### 5. WR-03: "no closed form exists after an arbitrary boolean" is false for 4 of the 15 composed rows; the claim sits in the debt file, L33 (twice) and three test_model.py docstrings
expected: Reword to "not derived" where it is false (tied to item 2's L33 decision: edit in place on the unlanded branch, or append an amendment), and decide whether the four web-formula rows move to abs=1e-9 now or stay with the debt
result: issue
reported: "reword all five, edit L33 in place, move the four rows"
severity: major
decision: "reword every 'no closed form exists after an arbitrary boolean' to 'not derived here' (debt file, L33 x2, three test_model.py docstrings); L33 edited in place because the branch is unlanded; the four hole-through-web rows take d_volume from 6*pi*(hole_d/2)**2*web and drop volume_rel, measured on the pinned kernel first and halted if any gap exceeds 1e-9"

## Summary

total: 5
passed: 3
issues: 2
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-14-2
  truth: "The skip-the-cutout tripwire's holes and cells rows prove the abs=1e-9 volume bar, so L33's sentence 'all three skip-the-cutout tripwire rows run at abs=1e-9' is true as written"
  status: failed
  reason: "User reported: 'the second recommended option' -- make the rows discriminating rather than reword L33: replace the holes and cells d_volume literals with the closed forms and add a control assertion that the shared call passes on the unpatched build before _cut_body is patched"
  severity: major
  test: 2
  root_cause: "test_the_cutout_proof_fails_when_the_cutout_step_is_skipped passes 6 dp literals (holes 565.486678 at line 1358, cells 1052.220866 at line 1365) into _assert_the_cutout_is_what_derive_prints, whose default became abs=1e-9 in 14-02. The literals sit +3.54e-7 and +4.02e-7 mm3 off the closed forms, so the volume line raises on an unpatched build too; pytest.raises(AssertionError) (lines 1379-1383) is satisfied by either branch and cannot tell the patched build from the correct one. Confirmed by gsd-code-reviewer building the solids (565.4866776461604, 1052.220865598084) and corroborated by the Codex lane (14-REVIEW.md WR-02)."
  artifacts:
    - path: "tests/test_model.py"
      issue: "holes and cells rows of the skip-the-cutout tripwire carry 6 dp volume literals that fail abs=1e-9 on a correct build"
  missing:
    - "holes row d_volume = 6 * pi * (hole_d/2)**2 * face_width (the closed form the proof test already uses near line 1314), cells row d_volume = the hex-cell formula at line 1348"
    - "a control assertion before the monkeypatch: the shared assertion passes on the unpatched build, so the pytest.raises below can only be satisfied by the patch"
    - "the docstring of the tripwire and L33 part two re-read against the new rows; L33 is expected to need no change"
  debug_session: ""

- gap_id: G-14-5
  truth: "Every statement of why the composed rows sit at rel=1e-6 says the closed form was not derived here, never that none exists; and the four hole-through-web rows (round, D-flat and keyed holes with both recesses; single-sided holes) assert abs=1e-9 against 6*pi*(hole_d/2)**2*web like the plain-solid rows"
  status: failed
  reason: "User reported: 'reword all five, edit L33 in place, move the four rows'"
  severity: major
  test: 5
  root_cause: "14-02 justified volume_rel=1e-6 on all 15 composed rows with 'no closed form exists after an arbitrary boolean' and wrote that sentence into the debt file (lines 16-17), L33 (decision_log.md lines 1580 and 1607) and three test_model.py docstrings (1245-1246, 1601-1602, 1657-1658). It is false for the hole-through-web rows: test_model.py:901-903 already derives recessed-hole volume as cylinder area times web thickness, and the reviewer measured that formula against the four rows' 6 dp literals -- 263.89378290 vs 263.893783 (d-flat, round, keyed holes, both recesses, web 3.5) and 414.69023027 vs 414.69023 (single-sided holes, web 5.5). hex-holes is excluded (the hex bore moves the recess outer wall to 11.994 mm and the holes reach 12 mm, crossing it); spokes and cells straddle the recess walls and their form is a polar/polygon-vs-circle integral split at the recess radii -- underived, not impossible. Found by the Codex lane, verified by gsd-code-reviewer (14-REVIEW.md WR-03)."
  artifacts:
    - path: "docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md"
      issue: "lines 16-17 state no closed form exists after an arbitrary boolean"
    - path: "docs/architecture/decision_log.md"
      issue: "L33 lines 1580 and 1607 repeat the claim; L33 is on the unlanded branch and is edited in place by the human's decision -- L33 did not exist at 5d9e907, so the phase's append-only check (no 5d9e907 line deleted) still holds"
    - path: "tests/test_model.py"
      issue: "docstrings at 1245-1246, 1601-1602, 1657-1658 repeat the claim; the four hole-through-web rows in test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore and test_the_recess_fillet_and_cutout_proofs_hold_with_a_single_sided_recess carry 6 dp literals at volume_rel=1e-6"
  missing:
    - "reword the five locations to say the closed form was not derived here (and that four hole rows now have one); grep the phase for any further copy of the sentence before closing"
    - "the four rows: d_volume = 6 * math.pi * (p.hole_d / 2) ** 2 * web, web = face_width - 2 * recess_depth for both-sided recesses and face_width - recess_depth for the single-sided row; drop volume_rel on those rows so the abs=1e-9 default applies; hex-holes, spokes and cells rows keep volume_rel=1e-6"
    - "before changing the bar, measure each of the four rows' kernel-vs-formula gap on the pinned kernel and record it in the test docstring; if any gap exceeds 1e-9 mm3 stop at a blocking-human checkpoint with the numbers (14-02's D-06 pattern), never loosen the bar"
    - "the debt file: 11 rows remain at rel=1e-6, the four moved rows named, the next step naming the recess-split integral for spokes and cells"
  debug_session: ""
  human_pre_decision: "2026-10-03, after the planner probe (tip rows 5.85e-10 / 5.94e-10 / 6.55e-10 mm3, single-sided 2.79e-12): noise-multiple 1e-8 -- the three tip rows at abs=1e-8, the single-sided row at abs=1e-9; applies only if the executor measurement reproduces those bands (14-04-PLAN.md Task 2)"
