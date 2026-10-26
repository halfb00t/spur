---
phase: 31-shaft-maths-parameters-and-designation
verified: 2026-10-26T18:00:00Z
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
covered_digest: "v3:sha256:9d9ab127183446e9deae2545e1b145656d449aed3be3667fff36f585a476644d"
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
  - finding: "IN-07: THEORETICAL_PIN ends 'M_Re is for this pin' on an odd tooth count, where measure_over_pins is null and ODD_Z_UNCONFIRMED says M_Re is not given"
    category: other
    reason: "Wording inconsistency between two warnings; no number is printed, so it does not break the null-until-proven claim. Fix by gating the clause on reading.measure (review IN-07). IN-08 and IN-09 are test and constant hygiene."
    evidence_status: "reproduced: W 25x1.25x19x8f carries both sentences with measure_over_pins null"
coincidental_reliance_items: []
human_verification: []
---

# Phase 31: Shaft Maths, Parameters and Designation Verification Report

**Phase Goal:** A user can ask the pure maths for a DIN 5480 external shaft from reference diameter, module, tooth count and tolerance field and get honest numbers: the profile shift the standard derives, tip and root diameters, nominal tooth thickness, measurement over pins at nominal thickness, each proved against an independent oracle and against rows of the copy, with the form diameter and odd-z M_Re `null` until proven, and a designation that prints and parses back to the same shaft. No solid, no route, no page yet.
**Verified:** 2026-10-26T18:00:00Z
**Status:** passed
**Re-verification:** Yes. The prior report went stale because the code-review fixes (WR-01..WR-06, IN-01..IN-06) changed covered files.

## Re-verification scope

`git diff 68b95c0 --stat -- src tests` (the tree of the prior report) shows six changed files: `din5480.py`, `shaft_calc.py`, `shaft_params.py` and three test files, 239 insertions and 35 deletions. `calc.py`, `params.py` and `requirements.txt` are untouched against `v0.6`.

I read the full source diff and checked the three things that could have broken the goal.

1. **No printed number changed.** I loaded the shaft maths from `git archive 68b95c0` into a scratch directory and compared it with HEAD over a grid of 11011 shafts: 13 modules, 6 to 82 teeth, 11 reference diameters each. Every field except `warnings` is byte-identical between the two (`cmp` on the JSON dumps). The default shaft still prints tip 24.75, root 22.25, s 2.613, M_Re 27.999, pin 2.73.
2. **No default or bound changed (L05).** `ShaftParams()` is still reference_d 25.0, module 1.25, teeth 18, fit 8f, splined 30, chamfer 1, shank 25 x 20. `X_MIN` and `X_MAX` are untouched. The only schema change on the shaft fields is a sentence appended to three help strings. `make gear.unchanged` (re-run by me): "byte-equal to v0.6" (8723 bytes).
3. **Null discipline holds.** Over the same 11011 shafts, `form_d` is non-null in 0, odd-z `measure_over_pins` is non-null in 0 of 5434, and even-z `measure_over_pins` is null in 0 of 5577.

The codec fixes (WR-04 pickling, WR-05 leading zeros) changed parse behavior for malformed input only. The canonical designations and the refusals still hold (below). The override from the prior report is carried forward verbatim and applied to truth 2.

## Goal Achievement

### Observable Truths (ROADMAP success criteria; PLAN must-haves add detail, none subtract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: Frozen `ShaftParams` contract, shift from d_B, epsilon edge, range refusal naming the range, gear untouched | VERIFIED | Frozen-contract test passes (1009 passed across the four shaft test files, run by me). `ShaftParams(reference_d=25.5)` raises `infeasible`: "needs a profile shift of +0.6500, above the allowed range -0.05 to +0.45". W30x2x14 prints x = -0.05 and validates. `git diff v0.6 -- calc.py params.py requirements.txt` empty. Gear schema byte-equal. |
| 2 | SC2: d_B, tip, root, thickness agree with the independent oracle and with at least two copy anchor rows | **PASSED (override)** | Override: "DIN 5480 Part 1 has no size tables; one designation (W 120x3x38x8f) is anchored for the tip; the rest is filed as must-severity debt", accepted by Andrew S on 2026-10-26. Oracle half VERIFIED: `tests/shaft_oracle.py` imports only `math` (line 31) and passes over the grid. Copy half: one row (W120x3x38 tip 119.4, root 113.4). The shortfall is accepted, not filled. |
| 3 | SC3: d_Ff `null` with a sentence; even-z M_Re and D_Re agree with the oracle; contact guard or `null` with a warning; odd z `null` | VERIFIED | `form_d` None for all 11011 grid shafts, each with the form sentence in `warnings`. Even z prints M_Re (W120x3x38: pin 5.93, M_Re 125.902). Odd z (25/1.25/19) prints pin 2.36 and `measure_over_pins` None with the odd-z sentence. Guard branches covered by direct-call tests. |
| 4 | SC4: Designation prints and parses back, `.` and `,`, refusal names the bad token, fit shape only | VERIFIED | Four shafts (including W30x2x14 and the odd-z one) round-trip through `format_designation`/`parse_designation`, also with `,`. Refused with the token named: `W 25x1.25x18` (`25x1.25x18`), `X ...` (`X`), `18.5`, `8F`, and the new `025`. `DesignationError` now survives a pickle round trip with the same message and token (WR-04). |
| 5 | SC5: Gate delta recorded; Phase 30 check green | VERIFIED | `bench/RESULTS.md` records the gate delta (2355 passed, 243.23 s vs 233.18 s, inside L43's 300 s). Orchestrator gate on this tree: `make verify` exit 0, `2378 passed in 324.61s`. Phase 30 contracts: `lint-imports` 10 kept, 0 broken (run by me). |

**Score:** 5/5 truths (4 VERIFIED, 1 PASSED (override); 0 present, behavior-unverified).

### Override applied

The override in the frontmatter is the human's (accepted_by "Andrew S", accepted_at 2026-10-26), carried forward verbatim. It matches truth 2 on the same wording as before. It closes the verification gap only. **REQ-shaft-basic-dims stays Pending**: the requirement asks for at least two copy anchor rows and the phase has one. The must-severity debt item `docs/tech_debt/active/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md` carries the missing rows, triggered by DIN 5480 Part 2 or Part 15 pages becoming available.

### Deferred Items

None.

### Advisory (New Scope, Unevidenced)

| # | Finding | Category | Why Advisory |
|---|---------|----------|--------------|
| 1 | IN-07: on an odd tooth count `THEORETICAL_PIN` still ends "and M_Re is for this pin" next to `ODD_Z_UNCONFIRMED` ("M_Re is not given") | other | Judged: wording inconsistency, not a breach of the honesty claim. No M_Re number is printed (`measure_over_pins` is null in all 5434 odd-z grid cases) and the odd-z sentence states the reason. The goal says odd-z M_Re is `null` until proven, and it is. A reader sees one sentence that is moot and one that is correct. The pin diameter D_Re is printed for odd z and the sentence is true of it. Worth the one-line fix review IN-07 proposes, but it is not a gap. |

IN-08 (no test for the `module` branch of `_exact`; a test indexes `warnings[2]`) and IN-09 (`H_FP_HOBBING` is a second hand-copied 0.60) are test and constant hygiene. They change no number and are recorded open in `31-REVIEW-DISPOSITION.md`.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/din5480.py` | Formulas, constants, codec | VERIFIED | Real maths, clause-cited; no cadquery, logger or gear imports (contract kept) |
| `src/spur/shaft_calc.py` | `derive_shaft`, `check_shaft`, pin guard | VERIFIED | Wired to `din5480`; `form_d=None` always; odd gate present |
| `src/spur/shaft_params.py` | `ShaftParams` | VERIFIED | Frozen, validated once via `model_validator` to `check_shaft` |
| `tests/shaft_oracle.py` | Independent oracle | VERIFIED | Imports `math` only |
| `tests/test_din5480_anchors.py` | Copy anchor rows | PARTIAL (covered by override) | One basic-dimension row; shortfall carried by the debt item |
| `src/spur/parts.py` | `Part = GearParams` | VERIFIED | Unchanged |

### Key Link Verification

| From | To | Status | Details |
|------|----|--------|---------|
| `ShaftParams._feasible` | `shaft_calc.check_shaft` | WIRED | A refusal reaches the caller as a validation error (seen above) |
| `derive_shaft` | `din5480.*` | WIRED | All formulas called; designation from `format_designation` |
| `shaft_oracle` | `spur` | INTENTIONALLY ABSENT | The oracle must not import spur |
| shaft maths | gear maths | ABSENT (required) | `lint-imports`: 10 kept, 0 broken |

### Data-Flow Trace (Level 4)

Not applicable: pure functions, no rendering or data source.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Printed numbers unchanged vs the prior tree | scratch compare of `68b95c0` and HEAD over 11011 shafts, `cmp` on non-warning fields | identical | PASS |
| form_d and odd-z M_Re null | same grid | 0 non-null form_d; 0 of 5434 odd-z M_Re non-null | PASS |
| Shaft tests | `pytest` on `test_din5480`, `test_din5480_anchors`, `test_shaft_calc`, `test_shaft_params` | `1009 passed in 2.20s` | PASS |
| Lint, types | `ruff check src tests`; `mypy --strict` on the 3 modules | clean | PASS |
| Import contracts | `lint-imports` | 10 kept, 0 broken | PASS |
| Gear unchanged | `python -m scripts.gear_unchanged` | byte-equal to v0.6 (8723 bytes) | PASS |
| Codec | round trip of four shafts, five hostile strings, pickle of the error | as in truth 4 | PASS |
| Full gate | orchestrator: `make verify` | exit 0, `2378 passed in 324.61s` | PASS (cited, not re-run) |

### Probe Execution

SKIPPED: no probes declared by this phase.

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|-------------|-------------|--------|----------|
| REQ-shaft-params | 31-01, 31-04, 31-05, 31-06 | SATISFIED | Frozen-contract test; defaults unchanged; validation at the boundary |
| REQ-profile-shift-from-dB | 31-01, 31-02, 31-05, 31-06 | SATISFIED | Shift derived from d_B, m, z; epsilon edges; range refusal now reads correctly near the edges (WR-01, WR-06). The range is narrower than the copy's exceptions (debt; errs toward refusing) |
| REQ-shaft-basic-dims | 31-01, 31-02, 31-04, 31-05, 31-06 | **PENDING (partial; phase gap overridden)** | Oracle yes; "at least two anchor rows" no. Stays Pending in REQUIREMENTS.md |
| REQ-form-diameter-honest | 31-03, 31-05, 31-06 | SATISFIED | `form_d` None everywhere with a reason |
| REQ-mre-nominal | 31-03, 31-05, 31-06 | SATISFIED | Even z at nominal with the guard, and now a warning that M_Re carries no fit allowance (WR-02); odd z null |
| REQ-designation-codec | 31-04, 31-06 | SATISFIED | Round trip and refusals verified |

All six phase IDs appear in PLAN frontmatter and in REQUIREMENTS.md (lines 53 to 70 and the Traceability table, lines 162 to 167: five Complete, REQ-shaft-basic-dims Pending). No orphans. REQ-gate-cost-recorded appears in the 31-06 plan but is mapped to Phase 34 and correctly stays open.

### Anti-Patterns Found

None blocking. `grep TBD|FIXME|XXX|TODO|HACK` over the phase's source and test files is empty. The `ASSUMPTION` markers in `din5480.py` name what is unconfirmed and are honest labels, not stubs.

### Code review status

The first review's findings WR-01 to WR-05 and the second round's WR-06 and IN-01 to IN-06 are recorded fixed in `31-REVIEW-DISPOSITION.md`. The re-review of those fixes found 0 critical, 0 warnings and 3 info (IN-07 to IN-09, open, covered above). WR-02 from the prior report, the one I asked to be fixed before Phase 33, is fixed: `MEASURE_AT_NOMINAL_THICKNESS` is emitted whenever M_Re is non-null.

### Human Verification Required

None. The human decision this phase needed (accepting the anchor shortfall) is recorded as the override. The review-fix report asks for a human look at the wording of the WR-06 refusal and the IN-03 gating. Both are wording choices on text the tests pin, and neither changes a number, so I do not treat them as a verification blocker.

### Gaps Summary

No open gaps. The single shortfall (SC2's "at least two copy anchor rows") is covered by the carried-forward human override and stays in the must-severity debt item; REQ-shaft-basic-dims stays Pending until those rows arrive. The review fixes changed wording, error messages and codec strictness, and no printed number, default, or null.

---

_Verified: 2026-10-26T18:00:00Z_
_Verifier: Claude (gsd-verifier)_
