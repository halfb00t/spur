---
phase: 31-shaft-maths-parameters-and-designation
verified: 2026-10-26T20:00:00Z
status: passed
score: 5/5 must-haves verified (includes 1 override)
covered_files:
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-01-PLAN.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-01-SUMMARY.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-02-PLAN.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-02-SUMMARY.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-03-PLAN.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-03-SUMMARY.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-04-PLAN.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-04-SUMMARY.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-05-PLAN.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-05-SUMMARY.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-06-PLAN.md"
  - ".planning/phases/31-shaft-maths-parameters-and-designation/31-06-SUMMARY.md"
  - "bench/RESULTS.md"
  - "docs/tech_debt/active/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md"
  - "src/spur/din5480.py"
  - "src/spur/parts.py"
  - "src/spur/shaft_calc.py"
  - "src/spur/shaft_params.py"
  - "tests/shaft_oracle.py"
  - "tests/test_din5480.py"
  - "tests/test_din5480_anchors.py"
  - "tests/test_shaft_calc.py"
  - "tests/test_shaft_params.py"
covered_digest: "v3:sha256:89bf1943ab111792a8ff789bfd8a8394559813f6098dd3d9783a2a2d80a79d0f"
behavior_unverified: 0
overrides_applied: 1
overrides:
  - must_have: "d_B, tip, root and nominal thickness agree with at least two anchor rows from the copy"
    reason: "DIN 5480 Part 1 has no size tables; one designation (W 120x3x38x8f, cl. 9.1 Fig. 6) is anchored for the tip; the rest is filed as must-severity debt 2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing. Accepted at the 31-05 checkpoint (partial pass + debt); accepted_by entered by the agent on the human's explicit instruction."
    accepted_by: "Andrew S"
    accepted_at: "2026-10-26"
re_verification:
  previous_status: passed
  previous_score: 5/5
  gaps_closed: []
  gaps_remaining: []
  regressions: []
deferred: []
advisory:
  - finding: "IN-10: the docstring of test_no_pin_sentence_is_printed_when_no_pin_is_given (tests/test_shaft_calc.py:158-161) still gives the pre-IN-07 reason, 'M_Re is for this pin' beside 'M_Re and D_Re not given'. THEORETICAL_PIN no longer contains M_Re."
    category: other
    reason: "Stale comment. The test body asserts the right thing; only the stated reason is out of date. Reword the last sentence."
    evidence_status: "reproduced: read at the cited lines; assert 'M_Re' not in THEORETICAL_PIN passes"
  - finding: "IN-11: the H_FP_HOBBING comment (src/spur/din5480.py:34-35) says only the hobbed-root sentence reads it; HOBBED_ROOT_DROP also feeds the root_d field description in the published schema"
    category: other
    reason: "Stale comment. Someone editing H_FP_HOBBING on this comment's word would not expect the schema text to move. Name both readers, as the shaft_calc.py comment already does."
    evidence_status: "reproduced: read at the cited lines"
coincidental_reliance_items: []
human_verification: []
---

# Phase 31: Shaft Maths, Parameters and Designation Verification Report

**Phase Goal:** A user can ask the pure maths for a DIN 5480 external shaft from reference diameter, module, tooth count and tolerance field and get honest numbers: the profile shift the standard derives, tip and root diameters, nominal tooth thickness, measurement over pins at nominal thickness, each proved against an independent oracle and against rows of the copy, with the form diameter and odd-z M_Re `null` until proven, and a designation that prints and parses back to the same shaft. No solid, no route, no page yet.
**Verified:** 2026-10-26T20:00:00Z
**Status:** passed
**Re-verification:** Yes. The prior report went stale because the IN-07, IN-08 and IN-09 fixes (4ee29af, ae7bbfc, a2d125c) changed `din5480.py`, `shaft_calc.py`, `tests/test_shaft_calc.py` and `tests/test_shaft_params.py`.

## Re-verification scope

`git diff 63172e7..HEAD -- src tests` is four files: 3 added lines in `din5480.py`, 25 lines moved in `shaft_calc.py`, and test edits. I read the whole diff. It does three things.

1. **IN-07.** The clause "and M_Re is for this pin" leaves `THEORETICAL_PIN` and moves into `MEASURE_AT_NOMINAL_THICKNESS`, which is emitted only when `reading.measure` is non-null. On an odd tooth count, where `measure_over_pins` is null and `ODD_Z_UNCONFIRMED` says M_Re is not given, the pin sentence no longer mentions M_Re. The previous report's advisory is therefore closed, not carried.
2. **IN-08.** A test is added for the `module` branch of the refusal message, and the hobbed-root tests find their sentence by content (`"hobbed" in w`) instead of `warnings[2]`.
3. **IN-09.** `H_FP_HOBBING = 0.60` moves into the `din5480.py` constants block. `HOBBED_ROOT_DROP` is computed from it and `H_FP`. A test asserts the drop is above 0.

No formula, bound or default is touched. Only string literals and the constant's location moved.

## L08: no printed number changed

I extracted `63172e7` and `HEAD` with `git archive src` into two scratchpad directories, ran the same script against each in its own process (`python -I`, import path asserted to be the scratch tree), and compared the JSON dumps. The oracle `tests/shaft_oracle.py` supplied d_B, so the grid sits on and around the real feasible region.

Grid: 13 modules (0.5 to 10) x 77 tooth counts (6 to 82) x 3 fits (8f, 7h, 9g) x 19 reference diameters per cell (the oracle d_B at 16 profile shifts from -0.06 to +0.46, spanning both range edges, plus 25.0 and two nudged values). That is **57,057 evaluations, 54,489 distinct shafts**: 45,519 accepted and 8,970 refused.

| Check | Result |
|-------|--------|
| Every non-warning field of every accepted shaft (the whole `model_dump` less `warnings`) | 0 differences |
| Refusal text for the 8,970 refused shafts | 0 differences |
| `ShaftParams` and `ShaftDimensions` JSON schemas | equal |
| Warning count per shaft | equal everywhere (the sentences moved, none added or dropped) |
| Warning strings that differ | exactly four: the old and new `THEORETICAL_PIN`, and the old and new `MEASURE_AT_NOMINAL_THICKNESS` |
| Default shaft (25 / 1.25 / 18 / 8f) | tip 24.75, root 22.25, pin 2.73, M_Re 27.999, as before |
| `form_d` non-null | 0 of 45,519 |
| Odd z, `measure_over_pins` non-null | 0 of 22,464 |
| Even z, `measure_over_pins` null | 0 of 23,055 |

Only warning strings differ. L05 holds with them: no default, bound or schema field moved, and `git diff v0.6 --stat -- src/spur/calc.py src/spur/params.py requirements.txt` is empty. `make gear.unchanged` (run by me): "byte-equal to v0.6" (8723 bytes).

## Goal Achievement

### Observable Truths (ROADMAP success criteria; PLAN must-haves add detail, none subtract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: Frozen `ShaftParams` contract, shift from d_B, epsilon edge, range refusal naming the range, gear untouched | VERIFIED | 1010 passed across the four shaft test files (run by me), including the frozen-contract test. 8,970 grid cases refuse with the range named, and refusal text is identical to `63172e7`. `calc.py`, `params.py`, `requirements.txt` empty against `v0.6`; gear schema byte-equal. |
| 2 | SC2: d_B, tip, root, thickness agree with the independent oracle and with at least two copy anchor rows | **PASSED (override)** | Override: "DIN 5480 Part 1 has no size tables; one designation (W 120x3x38x8f) is anchored for the tip; the rest is filed as must-severity debt", accepted by Andrew S on 2026-10-26. Oracle half VERIFIED: `tests/shaft_oracle.py` imports `math` only and its test passes. Copy half: one row (W120x3x38 tip 119.4, root 113.4), in `test_din5480_anchors.py`, passing. The shortfall is accepted, not filled. |
| 3 | SC3: d_Ff `null` with a sentence; even-z M_Re and D_Re agree with the oracle; contact guard or `null` with a warning; odd z `null` | VERIFIED | Grid counts above: `form_d` null in all 45,519 accepted shafts, odd-z `measure_over_pins` null in all 22,464, even-z printed in all 23,055. The form sentence is in the warnings of every shaft. Guard branches covered by direct-call tests in `test_shaft_calc.py` (passing). |
| 4 | SC4: Designation prints and parses back, `.` and `,`, refusal names the bad token, fit shape only | VERIFIED | Codec code untouched by the three fix commits; the codec tests pass (round trip, `,` form, refusals naming the token, pickle round trip of `DesignationError`). Every accepted grid shaft carries a designation in `designation`, identical to `63172e7`. |
| 5 | SC5: Gate delta recorded; Phase 30 check green | VERIFIED | `bench/RESULTS.md` records the gate delta. Orchestrator gate on this tree (cited, not re-run): `make verify` exit 0, `2379 passed in 316.29s`. `lint-imports`: 10 kept, 0 broken (run by me). `make gear.unchanged` green (run by me). |

**Score:** 5/5 truths (4 VERIFIED, 1 PASSED (override); 0 present, behavior-unverified).

### Override applied

The override in the frontmatter is the human's (accepted_by "Andrew S", accepted_at 2026-10-26), carried forward verbatim and not re-asked. It matches truth 2 on the same wording as before and closes the verification gap only. **REQ-shaft-basic-dims stays Pending**: the requirement asks for at least two copy anchor rows and the phase has one. The must-severity debt item `docs/tech_debt/active/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md` exists and carries the missing rows.

### Deferred Items

None.

### Advisory (New Scope, Unevidenced)

| # | Finding | Category | Why Advisory |
|---|---------|----------|--------------|
| 1 | IN-10: stale docstring in `test_no_pin_sentence_is_printed_when_no_pin_is_given` | other | Comment only. Not a goal gap: the test body asserts `THEORETICAL_PIN not in d.warnings`, which is the right behavior, and `THEORETICAL_PIN` holds no "M_Re" (asserted by another test). The docstring gives a reason that was true before IN-07. |
| 2 | IN-11: `H_FP_HOBBING` comment names one reader of two | other | Comment only. Not a goal gap: the constant, its value (0.60) and the drop (0.1) are pinned by tests, and `shaft_calc.py` lines 64-69 name both readers correctly. It is a maintenance trap for the next editor, with no effect on any number or null. |

The previous report's IN-07 advisory is closed by 4ee29af (checked above). IN-10 and IN-11 stay `open` in `31-REVIEW-DISPOSITION.md`; the two one-line fixes can land with any later edit of these files.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/din5480.py` | Formulas, constants, codec | VERIFIED | Real maths, clause-cited; `H_FP_HOBBING` now in the constants block; no cadquery, logger or gear imports (contract kept) |
| `src/spur/shaft_calc.py` | `derive_shaft`, `check_shaft`, pin guard | VERIFIED | Wired to `din5480`; `form_d=None` always; odd gate present; measure sentence gated on a printed M_Re |
| `src/spur/shaft_params.py` | `ShaftParams` | VERIFIED | Frozen, validated once through `check_shaft`; unchanged in this round |
| `tests/shaft_oracle.py` | Independent oracle | VERIFIED | Imports `math` only |
| `tests/test_din5480_anchors.py` | Copy anchor rows | PARTIAL (covered by override) | One basic-dimension row; shortfall carried by the debt item |
| `src/spur/parts.py` | `Part = GearParams` | VERIFIED | Unchanged |

### Key Link Verification

| From | To | Status | Details |
|------|----|--------|---------|
| `ShaftParams._feasible` | `shaft_calc.check_shaft` | WIRED | 8,970 refused grid cases surface as validation errors |
| `derive_shaft` | `din5480.*` | WIRED | All formulas called; `HOBBED_ROOT_DROP` reads `din5480.H_FP_HOBBING` and `din5480.H_FP` |
| `shaft_oracle` | `spur` | INTENTIONALLY ABSENT | The oracle must not import spur |
| shaft maths | gear maths | ABSENT (required) | `lint-imports`: 10 kept, 0 broken |

### Data-Flow Trace (Level 4)

Not applicable: pure functions, no rendering or data source.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| No printed number or default changed vs `63172e7` | scratch compare of both trees over 57,057 evaluations (54,489 shafts) | 0 non-warning diffs, 0 refusal diffs, schemas equal | PASS |
| form_d and odd-z M_Re null | same grid | 0 non-null form_d; 0 of 22,464 odd-z M_Re non-null; 0 of 23,055 even-z null | PASS |
| Shaft tests | `pytest` on `test_din5480`, `test_din5480_anchors`, `test_shaft_calc`, `test_shaft_params` | `1010 passed in 2.15s` | PASS |
| Lint, types | `ruff check src tests`; `mypy --strict` on the 3 modules | clean | PASS |
| Import contracts | `lint-imports` | 10 kept, 0 broken | PASS |
| Gear unchanged | `make gear.unchanged` | byte-equal to v0.6 (8723 bytes) | PASS |
| Full gate | orchestrator: `make verify` | exit 0, `2379 passed in 316.29s` | PASS (cited, not re-run) |

### Probe Execution

SKIPPED: no probes declared by this phase.

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|-------------|-------------|--------|----------|
| REQ-shaft-params | 31-01, 31-04, 31-05, 31-06 | SATISFIED | Frozen-contract test; defaults unchanged; validation at the boundary |
| REQ-profile-shift-from-dB | 31-01, 31-02, 31-05, 31-06 | SATISFIED | Shift derived from d_B, m, z; epsilon edges; refusal names the range. The range is narrower than the copy's exceptions (debt; errs toward refusing) |
| REQ-shaft-basic-dims | 31-01, 31-02, 31-04, 31-05, 31-06 | **PENDING (partial; phase gap overridden)** | Oracle yes; "at least two anchor rows" no. Left Pending in REQUIREMENTS.md (line 60 unchecked, traceability line 164 Pending). Not marked complete. |
| REQ-form-diameter-honest | 31-03, 31-05, 31-06 | SATISFIED | `form_d` None in every grid shaft, with a reason |
| REQ-mre-nominal | 31-03, 31-05, 31-06 | SATISFIED | Even z at nominal with the guard and the no-fit-allowance sentence; odd z null |
| REQ-designation-codec | 31-04, 31-06 | SATISFIED | Round trip and refusals verified |

All six phase IDs appear in PLAN frontmatter and REQUIREMENTS.md (five Complete, REQ-shaft-basic-dims Pending). No orphans.

### Anti-Patterns Found

None. `grep TBD|FIXME|XXX|TODO|HACK` over the phase's source and test files is empty. The `ASSUMPTION` markers in `din5480.py` name what is unconfirmed; they are honest labels, not stubs.

### Human Verification Required

None. The one human decision this phase needed (accepting the anchor shortfall) is recorded as the override.

### Gaps Summary

No open gaps. The single shortfall (SC2's "at least two copy anchor rows") is covered by the carried-forward human override and stays in the must-severity debt item; REQ-shaft-basic-dims stays Pending until those rows arrive. The IN-07..IN-09 fixes moved warning text and one constant. A 57,057-evaluation comparison with `63172e7` shows no number, null, default, refusal or schema field changed. IN-10 and IN-11 are stale comments, recorded as advisory.

---

_Verified: 2026-10-26T20:00:00Z_
_Verifier: Claude (gsd-verifier)_
