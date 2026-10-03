---
phase: 14-honest-record
verified: 2026-10-03T14:30:00Z
status: passed
score: 8/8 must-haves verified
covered_files:
  - .planning/phases/14-honest-record/14-01-PLAN.md
  - .planning/phases/14-honest-record/14-01-SUMMARY.md
  - .planning/phases/14-honest-record/14-02-PLAN.md
  - .planning/phases/14-honest-record/14-02-SUMMARY.md
  - .planning/phases/14-honest-record/14-03-PLAN.md
  - .planning/phases/14-honest-record/14-03-SUMMARY.md
  - .planning/phases/14-honest-record/14-04-PLAN.md
  - .planning/phases/14-honest-record/14-04-SUMMARY.md
  - README.md
  - docs/architecture/decision_log.md
  - docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md
  - src/spur/calc.py
  - src/spur/model.py
  - tests/test_calc.py
  - tests/test_model.py
covered_digest: "v2:sha256:64901acc421ee529d2fd3e7f95329ab5243ad7e949d33ae7350cea51b83f62b4"
behavior_unverified: 0
overrides_applied: 1
overrides:
  - must_have: "_assert_the_cutout_is_what_derive_prints asserts the removed volume at abs=1e-9 on all four rows and nowhere at a relative tolerance"
    reason: "Eleven composed-solid rows carry 6 dp literals whose closed form is not derived here and cannot meet 1e-9; they keep their pre-phase rel=1e-6 via an explicit volume_rel argument, named in the active debt file. The four SC3 rows are at abs=1e-9. Accepted at 14-UAT.md Test 1 (15 rows at the time; four have since moved to formulas by 14-04)."
    accepted_by: "halfb00t (human, 14-UAT.md Test 1)"
    accepted_at: "2026-10-03"
re_verification:
  previous_status: human_needed
  previous_score: 4/5
  gaps_closed:
    - "G-14-2: skip-the-cutout tripwire holes and cells rows were non-discriminating (6 dp literals failed abs=1e-9 on a correct build)"
    - "G-14-5: 'no closed form exists after an arbitrary boolean' was false for four hole-through-web rows; debt file, L33 and three docstrings reworded; four rows moved onto the web formula"
  gaps_remaining: []
  regressions: []
gaps: []
---

# Phase 14: Honest Record Verification Report

**Phase Goal:** Every claim this tool or its docs make about geometry it already builds is either true or flagged: the root lead-in warns when it rises above the pitch circle, README states the real limit instead of the general "non-working root zone" claim, and the filleted-spoke removed-volume proof is checked against an independent closed form instead of a pinned literal.
**Verified:** 2026-10-03, against HEAD ff38fad
**Status:** passed
**Re-verification:** Yes. The earlier report went stale: 14-04 (gap_closure, G-14-2 and G-14-5) changed tests/test_model.py, L33, the debt file and its INDEX row. Every verdict below was re-derived from the code at HEAD, not copied.

## Gate and runs I did myself

- `make verify` was not re-run by me. The orchestrator reports `927 passed in 224.25s` on HEAD, and 14-04-SUMMARY records `927 passed in 212.90s` on the committed tree. I make no claim about that run beyond relaying it.
- Targeted pytest, run by me at HEAD:
  - `-k "every_feature_proof_holds_on_a_tip or proofs_hold_with_a_single_sided or each_cutout_is_exactly or cutout_proof_fails"`: `23 passed` (matches the plan's expected 23).
  - `tests/test_calc.py -k root_lead_in`: `15 passed`.
  - `tests/test_model.py -k rim_corner_tangent_root`: `1 passed`.
  - `tests/regression`: `86 passed`.
- Scope checks: `git diff --quiet 5d9e907 -- tests/regression/pre_v0_2.json src/spur/params.py` exits 0. `git diff --name-only 7cb0c7d..HEAD -- src README.md tests/regression` prints nothing, so 14-04 touched no src, README or fixture. `src/` differs from 5d9e907 only in calc.py and model.py (14-01's work).

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: `derive().warnings` names the lead-in height (3 dp) and that the chord deviates from the involute, at the three debt configs plus one step either side of the crossing; pure `calc.py`, no outline change | VERIFIED | `src/spur/calc.py:975-985`: `h = spline_start(pr, rfil) - pr.r`; `if round(h, 3) > 0` appends "...reaching {h:.3f} mm above the pitch circle, where it deviates from the involute: the root fillet is larger than half the dedendum." 15 rows pass. No kernel import in calc.py. No 14-04 change to src. The prior report's 3,930-point sweep covered this code, which is unchanged since. |
| 2 | SC2: README's root-fillets bullet states the real condition, cites `warnings`, no unmeasured number | VERIFIED | README.md:228-229 says "1.188 mm below the pitch circle on the default gear, but above it, where the chord deviates from the true involute, when the root fillet exceeds half the dedendum" and cites `warnings`. README is byte-unchanged since the prior report. Numbers are 1.188, 1.25, 0.125, each a test row value or a definition. |
| 3 | SC3: filleted-spoke row asserted against an independent closed form at abs=1e-9; literal demoted; tripwire goes red on a perturbed `inside=True` root | VERIFIED | `_filleted_spoke_volume` holds no `cq` or `_fillet_corner` name. The shared assertion's default is `pytest.approx(d_volume, abs=1e-9)` (verified by AST: present, and the literal `rel=1e-6` is absent from the function). The rim-corner tripwire passes (1 passed). The four proof rows pass inside the 23. |
| 4 | SC4: both debt files retired with sha; fixture byte-unchanged; new Lxx answers L30 without touching it | VERIFIED | Both files are in `docs/tech_debt/resolved/` and absent from `active/`. `git diff 5d9e907 -- decision_log.md` has 111 added lines and 0 deleted (`--numstat` `111 0`; `grep -c '^-[^-]'` gives 0), so L30 and everything before it is untouched. L33 is the last and only L33 heading, after L32. |
| 5 | Plan 14-02 must-have "abs=1e-9 on all four rows and nowhere at a relative tolerance" | PASSED (override) | Eleven composed rows still pass `volume_rel=1e-6`. Override accepted by the human at 14-UAT.md Test 1. See the frontmatter. Intent met: the four SC3 rows are at abs=1e-9, and the eleven are named in the active debt file. |
| 6 | G-14-2: the tripwire's holes and cells rows take closed-form `d_volume`; a control call passes on the unpatched build before the monkeypatch; L33's tripwire sentence stands verbatim and is true | VERIFIED | AST of `test_the_cutout_proof_fails_when_the_cutout_step_is_skipped`: two calls to the shared assertion, one outside `pytest.raises` on a line before the single `setattr`, one inside it. No float literal in the parametrize except the 0.0 angles. Rows use `_holes_volume(...)`, `_hex_cells_volume(_CELLS_NO_RECESS)` and `_filleted_spoke_volume(...)`. Both helpers hold no `cq` name. All three rows pass, so the control call passes on the correct build at abs=1e-9. L33's sentence `all three skip-the-cutout tripwire rows run at \`abs=1e-9\`` is present verbatim (decision_log.md:1595-1596). See Residual 1 below. |
| 7 | G-14-5: every "no closed form exists" reworded to "not derived here"; four hole-through-web rows assert the web formula, measured first, at the human's bar; record states it accurately | VERIFIED | Grep of docs/, tests/, src/, README.md for `closed form exists`, `arbitrary boolean`, `no closed form`: remaining hits are L33:1523 (paraphrase of L30, kept on purpose), L33:1580 ("no closed form has been derived for them here", accurate), the resolved filleted-spoke debt file (dated record), and tests/test_model.py:1522 (Phase 11 fragment-count docstring, not a volume). The shared assertion and both composed tests' docstrings contain "not derived". Bar and numbers: see the table below. |
| 8 | 14-04 prohibitions: no bar loosened without the human's answer; no src change; L33 only edited in place, tripwire sentence verbatim | VERIFIED | The human answered at Task 2 (`noise-multiple 1e-8`, recorded in 14-UAT.md `human_pre_decision` and 14-04-SUMMARY). src, params.py and the fixture unchanged by 14-04. decision_log numstat against 5d9e907 deletes 0 lines. |

**Score:** 8/8 truths verified (1 via accepted override, 0 behavior-unverified)

### The four hole-through-web rows: measured, not trusted

I rebuilt the solids on the pinned kernel (cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1, Python 3.12.13) and compared `reference.Volume() - cut.Volume()` with `_holes_volume`:

| Row | Kernel delta (mm3) | Formula (mm3) | Signed gap | Bar in the test | Margin |
|---|---|---|---|---|---|
| d-flat-holes (tip chamfer, both recesses) | 263.8937829021279 | 263.89378290154264 | +5.853e-10 | abs=1e-8 | about 17x |
| round-holes | 263.89378290213654 | 263.89378290154264 | +5.939e-10 | abs=1e-8 | about 17x |
| keyed-holes | 263.8937829021979 | 263.89378290154264 | +6.553e-10 | abs=1e-8 | about 15x |
| single-sided holes | 414.6902302738499 | 414.6902302738527 | -2.785e-12 | abs=1e-9 | about 360x |

These match 14-04-SUMMARY's table to every printed digit. The numbers in the test docstrings (5.85e-10, 5.94e-10, 6.55e-10, 2.79e-12, 1.36e-12), the debt file and L33 are all the measured ones.

Is the recorded bar accurate, and is any asserted number unmeasured (L08)?

- The human's `noise-multiple 1e-8` is recorded in four places and each agrees with the code. The tip test sets `volume_abs=1e-8` only on the `d_volume is None` branch. The single-sided test passes `volume_rel=None` and no `volume_abs`, so it runs at the default abs=1e-9. The `_assert_the_cutout_is_what_derive_prints` docstring says the 1e-8 bar is "one the human chose as a multiple of that measured offset (L33), not one the executor tuned". The tip-test docstring says the three rows do not run at 1e-9 because that "would leave them about 1.5x of headroom; 1e-8 is about 15x their largest gap". L33:1588-1592 says the human chose `abs=1e-8`, "about 15x their largest gap", and that it is "the one bar in this phase set from a measured gap". The debt file's Context says the same.
- L33:1573-1575 keeps its earlier sentence "no tolerance was loosened and none was set from a measured gap", but scoped to "these four rows" (holes, sharp spokes, filleted spokes, cells). That scoping keeps it true next to the 1e-8 admission.
- Every e-notation figure in L33 (`1.36e-12 2.39e-12 2.522e-4 2.73e-12 2.79e-12 2.9e-3 5.85e-10 5.94e-10 6.55e-10 8.59e-8 8.87e-12`) also appears in tests/test_model.py. None is unmeasured.
- Row counts add up: the tip test has 12 rows (3 formula, 9 literal) and the single-sided test has 3 (1 formula, 2 literal), so 4 + 11 = 15. The debt file's title "Eleven" and L33's "Eleven composed-solid rows (9 of the 12 ..., 2 of the 3 ...)" agree. The debt file's list (d-flat, round, hex and keyed spokes and cells, hex-holes, single-sided spokes and cells) is also 8 + 1 + 2 = 11.
- The debt file stays in `active/`. Its INDEX row link text is exactly the new H1, with the same trigger. The Next step names the recess-split integral.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/test_model.py` `_holes_volume`, `_hex_cells_volume` | pure-math oracles after `_filleted_spoke_volume` | VERIFIED | Present, no `cq` name, used by the proof, the tripwire and the composed rows. |
| Tripwire with control call | control before patch, no literal volumes | VERIFIED | AST-checked above. |
| `volume_abs` on the shared assertion | precedence `volume_rel`, then `volume_abs`, then default abs=1e-9 | VERIFIED | The branch at tests/test_model.py:1291-1296 matches. The default line is verbatim. |
| `docs/architecture/decision_log.md` L33 | edited in place, accurate | VERIFIED | See truths 4, 6 and 7. |
| Active debt file and INDEX row | narrowed to eleven | VERIFIED | See above. |
| `src/spur/calc.py` | lead-in warning | VERIFIED | Truth 1. |
| `README.md` | corrected bullet | VERIFIED | Truth 2. |

### Key Link Verification

| From | To | Status | Details |
|------|----|--------|---------|
| tripwire holes and cells rows | `_holes_volume` / `_hex_cells_volume` | WIRED | Called at collection time in the parametrize. |
| tip test d-flat, round, keyed holes | `_holes_volume(p, 2)` | WIRED | `None` row, formula in the body. Bar spy: 23 passed with the rows resolving. |
| single-sided holes | `_holes_volume(p, 1)` | WIRED | Same. |
| L33 | the composed tests' docstrings | WIRED | All L33 figures appear in the test file. |
| `derive()` | `spline_start`, `root_fillet`, `pr.r` | WIRED | calc.py:975. |

### Requirements Coverage

| Requirement | Source Plans | Status | Evidence |
|-------------|--------------|--------|----------|
| REQ-root-lead-in-warned | 14-01, 14-03 | SATISFIED | Truth 1. REQUIREMENTS.md marks it `[x]` and "Complete". |
| REQ-readme-root-zone-states-the-limit | 14-01, 14-03 | SATISFIED | Truth 2. Debt file retired. |
| REQ-filleted-spoke-closed-form | 14-02, 14-03, 14-04 | SATISFIED | Truths 3, 4, 6 and 7. REQUIREMENTS.md's wording that all four rows assert abs=1e-9 holds. |

All three IDs appear in PLAN frontmatter (14-04 declares `REQ-filleted-spoke-closed-form`) and in REQUIREMENTS.md and ROADMAP.md. REQUIREMENTS.md maps no other ID to Phase 14, so none is orphaned.

### Prohibitions (ADR-550 D3)

| Prohibition | Tier | Result |
|-------------|------|--------|
| No loosening or measured-gap bar without the human (D-06) | test | Held. The only measured-gap bar is the three tip rows' 1e-8, set by the human and logged in L33. |
| No src change by 14-04; fixture and params.py byte-identical to 5d9e907 | test | Held (git checks above). |
| Decision log: only L33 edited, no 5d9e907 line deleted, tripwire sentence verbatim | test | Held (numstat 0 deleted; sentence present). |
| No number in README the tests do not prove | test | No standing repo test enforces it. The human accepted the manual check at 14-UAT.md Test 4 (1.188, 1.25, 0.125 only). It stays flagged as a manual-only guard but is resolved by the human, not silently passed. |

### Anti-Patterns

No `TBD`, `FIXME` or `XXX` in files 14-04 touched; the gate's unfinished-work scan passed in the relayed `make verify`. No stub or empty-return pattern in the new helpers.

## Residuals (informational, no status impact)

1. **The skip-the-cutout tripwire is red for the face-delta reason, not the volume line.** I patched `_cut_body` to a no-op on the holes row and the first assertion to fire is `assert faces_delta == d_faces`. The control passes unpatched, so the tripwire now discriminates the patched build from the correct one, which is what G-14-2 asked for. L33 says the rows "run at `abs=1e-9`", and that is true: the control proves the expected volume agrees at 1e-9. L33 does not claim the volume line is what turns the tripwire red. The rim-corner tripwire is what proves the 1e-9 bar is load-bearing. No wording change needed.
2. **WR-01's CI claim is human-recorded, not something I re-ran.** 14-UAT.md Test 3 cites CI run 37099687748 (ubuntu-24.04, 927 passed) and the human chose not to record ubuntu gap values. I cannot see that run from here. Treat the CI point as human-accepted.
3. **Tangent left to the human (raised by 14-04):** `test_the_hole_link_cuts_six_holes_through_the_recessed_floor` (tests/test_model.py near line 901) asserts the same web formula at `rel=1e-6` on the default gear. It is outside G-14-5's four rows and was not changed.
4. **Housekeeping:** `.planning/ROADMAP.md` line 64 still reads `- [ ] **Phase 14: Honest Record**` although all four plans are `[x]`. The phase-complete step should flip it. The review disposition keeps WR-01, IN-01, IN-02 and IN-03 `open` (warning and info, none blocking).

## Human Verification Required

None outstanding. The four items the earlier report raised were each resolved by the human at 14-UAT.md (Tests 1, 3, 4 accepted or passed; Tests 2 and 5 became G-14-2 and G-14-5, closed and re-verified above).

## Gaps Summary

No gaps. All four ROADMAP success criteria hold in the code at HEAD ff38fad. Both UAT gaps are closed: the tripwire's three rows discriminate (control call first, no literals), and the four hole-through-web rows assert `6*pi*(hole_d/2)**2*web` at bars that match the kernel gaps I re-measured to every digit. The record (L33, the debt file, the docstrings) states the human's 1e-8 decision and the "not derived here" wording accurately.

---

_Verified: 2026-10-03_
_Verifier: Claude (gsd-verifier)_
