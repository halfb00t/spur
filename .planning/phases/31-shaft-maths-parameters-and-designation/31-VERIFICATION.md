---
phase: 31-shaft-maths-parameters-and-designation
verified: 2026-10-26T14:00:00Z
status: gaps_found
score: 4/5 must-haves verified
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
covered_digest: "v3:sha256:b33c97eded6f7a9ce23d86aa94771a143a8a8535ade4c601283acb5ad39f3a7b"
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "SC2 / REQ-shaft-basic-dims: d_B, tip, root and nominal thickness each agree with the independent oracle AND with at least two anchor rows from the copy"
    status: partial
    reason: "Oracle half holds. Copy half is not met: the only copy-anchored basic dimension is the tip diameter d_a1 of W 120x3x38x8f (one row, one of four quantities). Root diameter and nominal tooth thickness have no copy row at all; they rest on clause confirmation of the formula by the human (Table 3) plus two vendor reports. The human accepted a partial pass at 31-05 and the shortfall is filed as must-severity debt, but no override with a named acceptor exists in a VERIFICATION.md, and REQ-shaft-basic-dims is correctly left Pending."
    artifacts:
      - path: "tests/test_din5480_anchors.py"
        issue: "One basic-dimension row (tip, 119.40). The d_Ff1 limit and M1 rows are not basic dimensions. No root row, no nominal-thickness row, no second designation."
      - path: "docs/tech_debt/active/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md"
        issue: "Carries the shortfall (must). Trigger: DIN 5480 Part 2 or Part 15 pages become available. Not closable by a plan; needs external evidence."
    missing:
      - "A second cited basic-dimension row (ideally W25x1.25x18 or W30x2x14), and a root and a nominal-thickness row, from pages the human approves by name"
      - "Or: the human records the partial pass as an override (YAML below) so the phase can close with the shortfall carried by the debt item"
deferred: []
coincidental_reliance_items: []
human_verification: []
---

# Phase 31: Shaft Maths, Parameters and Designation Verification Report

**Phase Goal:** A user can ask the pure maths for a DIN 5480 external shaft from reference diameter, module, tooth count and tolerance field and get honest numbers: the profile shift the standard derives, tip and root diameters, nominal tooth thickness, measurement over pins at nominal thickness, each proved against an independent oracle and against rows of the copy, with the form diameter and odd-z M_Re `null` until proven, and a designation that prints and parses back to the same shaft. No solid, no route, no page yet.
**Verified:** 2026-10-26
**Status:** gaps_found
**Re-verification:** No, initial verification

## Verdict

The maths, the oracle, the codec, the null discipline and the gear-safety guard are all real and work. I ran the focused suites, ruff, `mypy --strict`, `lint-imports` and `gear.unchanged` myself, and I exercised the code with five shafts and the hostile designations. One clause of the goal is not met as written: "against rows of the copy". There is one copy designation, and only the tip diameter of it is a basic-dimension row. That is the single gap. It is a gap that no further plan can close; it needs evidence from outside the repo.

## Goal Achievement

### Observable Truths (ROADMAP success criteria; PLAN must-haves add detail, none subtract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: Frozen `ShaftParams` contract, shift from d_B, epsilon edge, range refusal naming the range, gear untouched | VERIFIED | `tests/test_shaft_params.py::test_the_shaft_field_names_and_defaults_are_frozen`, bound and edge tests; 986 passed in my run of the four shaft files. `ShaftParams(reference_d=25.5)` raises `infeasible` naming "-0.05 to +0.45". `git diff v0.6 -- calc.py params.py requirements.txt` empty. W30x2x14 prints x = -0.05 and validates. Red logs 31-01-red-*.log present. |
| 2 | SC2: d_B, tip, root, thickness agree with the independent oracle and with at least two copy anchor rows | PARTIAL (FAILED on the copy half) | Oracle half VERIFIED: `tests/shaft_oracle.py` imports only `math`, holds its own constants, rebuilds tip and thickness by a different road (base-thickness identity), 192-case grid plus vendor sets, red logs 31-02-red-*.log. Its docstring admits root is the same definition twice and proves transcription only. Copy half: one row (d_a1 119.40). Root and thickness have no copy row. |
| 3 | SC3: d_Ff `null` with a sentence, even-z M_Re and D_Re agree with oracle, contact guard or `null` with a warning, odd z `null` until an odd row | VERIFIED | Every output I produced has `form_d` None with the form sentence in `warnings`. Odd z (25/1.25/19) gives `pin_d` 2.36, `measure_over_pins` None. Even z prints M_Re. `pin_measurement` has both null branches, covered by direct calls (31-03-red-guard-swapped.log). Even-z M1 reproduces the copy's 125.956 at the row's own s and pin, within 0.00004. |
| 4 | SC4: Designation prints and parses back, `.` and `,`, refusal names the bad token, fit shape only | VERIFIED | I round-tripped five shafts through `format_designation`/`parse_designation`, with `,` as well. Refused: `W 25x1.25x18` (token `25x1.25x18`), `X ...` (token `X`), `18.5` (token `18.5`), `8F` (token `8F`). Red logs 31-04-red-*.log. |
| 5 | SC5: Gate delta recorded; Phase 30 check green | VERIFIED | `bench/RESULTS.md` "The gate delta (31-06)": 2355 passed, 243.23 s vs Phase 30's 233.18 s (+4.3 %, inside the ~8 % spread, under L43's 300 s). `python -m scripts.gear_unchanged`: "byte-equal to v0.6", run by me. Orchestrator gate: `make verify` exit 0, 2355 passed. |

**Score:** 4/5 truths verified (0 present, behavior-unverified). Truth 2 is split: oracle half passes, copy half fails.

### Judgement on the partial pass (the orchestrator's question)

The "proved against rows of the copy" clause is only partly met, and I count it as a **gap**, not as a satisfied clause and not as a silent pass.

- The roadmap says "at least two anchor rows" for the basic dimensions and "Without the rows the plan builds the maths and the oracle, then stops at a checkpoint: no number ships unproved (L08)". The checkpoint stopped, the human decided to proceed, and that decision is honest and recorded (31-05 SUMMARY, debt item, 31-06 close check 9 left reading FAIL with the reason beside it).
- But a human decision to proceed is not the same as the contract being met. The override mechanism requires a named acceptor and a timestamp in a VERIFICATION.md; none exists, and I will not invent one. So the strict reading stands: the truth is not VERIFIED.
- Mitigating, and why I do not call it a blocker for moving on: the formulas for shift, tip, root and thickness were confirmed by the human against the copy by clause (cl. 6 Table 3, cl. 7.1; 31-05 A1 to A4) and the tip number was reproduced at 119.40. Hexagon's d_f 113.40 for the same W120x3x38 matches our `root_d` 113.4 (a vendor report, not the copy). The numbers I generated look right. The weakness is evidence coverage, not a found wrong number.
- What the gap is not: it is not closable by `/gsd-plan-phase --gaps`, because the missing input is pages of DIN 5480 Part 2 or Part 15. The debt item carries the trigger.

**Suggested override, if the human wants the phase to close with this carried by debt** (fill `accepted_by`; the evidence for it is the 31-05 decision):

```yaml
overrides:
  - must_have: "d_B, tip, root and nominal thickness agree with at least two anchor rows from the copy"
    reason: "DIN 5480 Part 1 has no size tables; one designation (W 120x3x38x8f, cl. 9.1 Fig. 6) is anchored for the tip; the rest is filed as must-severity debt 2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing"
    accepted_by: "<the human's name>"
    accepted_at: "2026-10-26"
```

With that override, truth 2 becomes PASSED (override) and the phase reads `passed`, with REQ-shaft-basic-dims still Pending in REQUIREMENTS.md, which is the right place for it.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/din5480.py` | Formulas, constants, codec | VERIFIED | 259 lines, real maths, clause-cited, 5 ASSUMPTION markers named; no cadquery/logger/gear imports |
| `src/spur/shaft_calc.py` | `derive_shaft`, `check_shaft`, pin guard | VERIFIED | Wired to `din5480`; `form_d=None` always; odd gate present |
| `src/spur/shaft_params.py` | `ShaftParams` | VERIFIED | Frozen, validated once via `model_validator` -> `check_shaft` |
| `tests/shaft_oracle.py` | Independent oracle | VERIFIED | Imports `math` only |
| `tests/test_din5480_anchors.py` | Copy anchor rows | PARTIAL | 3 cited tests, 1 basic-dimension row |
| `src/spur/parts.py` | `Part = GearParams` | VERIFIED | Phase 32 widens it, by design |

### Key Link Verification

| From | To | Status | Details |
|------|----|--------|---------|
| `ShaftParams._feasible` | `shaft_calc.check_shaft` | WIRED | Local import; refusal reaches the caller as a validation error |
| `derive_shaft` | `din5480.*` | WIRED | All formulas called; designation from `format_designation` |
| `shaft_oracle` | `spur` | INTENTIONALLY ABSENT | The oracle must not import spur |
| shaft maths | gear maths | ABSENT (required) | `lint-imports`: 10 contracts kept, 0 broken |

### Data-Flow Trace (Level 4)

Not applicable: pure functions, no rendering, no data source. Values flow from arguments to returned model.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Shaft tests | `.venv/bin/python -m pytest` on 4 shaft files | `986 passed in 2.14s` | PASS |
| Lint, types | `ruff check src tests`; `mypy --strict` on 3 modules | clean | PASS |
| Import contracts | `lint-imports` | 10 kept, 0 broken | PASS |
| Gear unchanged | `python -m scripts.gear_unchanged` | byte-equal to v0.6 | PASS |
| Default shaft | `derive_shaft` | tip 24.75, root 22.25, s 2.613, form None, M_Re 27.999 | PASS |
| W120x3x38 | `derive_shaft` | tip 119.4, root 113.4 (Hexagon 113.40), M_Re 125.902 | PASS |
| Odd z | 25/1.25/19 | pin 2.36, M_Re None | PASS |

I did not re-run the full `make verify`; the orchestrator's run (exit 0, 2355 passed in 175.70 s) stands as the gate evidence.

### Probe Execution

SKIPPED: no probes declared by this phase.

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|-------------|-------------|--------|----------|
| REQ-shaft-params | 31-01, 31-04, 31-05, 31-06 | SATISFIED | Frozen-contract test, boundary validation |
| REQ-profile-shift-from-dB | 31-01, 31-02, 31-05, 31-06 | SATISFIED | Formula confirmed by clause; epsilon edges; range refusal. The range is narrower than the copy's exceptions (debt D3, errs honest) |
| REQ-shaft-basic-dims | 31-01, 31-02, 31-04, 31-05, 31-06 | **BLOCKED (partial)** | Oracle yes; "at least two anchor rows" no. Correctly Pending in REQUIREMENTS.md |
| REQ-form-diameter-honest | 31-03, 31-05, 31-06 | SATISFIED | `form_d` None everywhere with a reason; the copy's printed limit 113.91 checked as a limit |
| REQ-mre-nominal | 31-03, 31-05, 31-06 | SATISFIED | Even z at nominal with the guard; odd z null; see WR-02 note below |
| REQ-designation-codec | 31-04, 31-06 | SATISFIED | Round trip and refusals verified |

All six phase IDs appear in PLAN frontmatter and in REQUIREMENTS.md. No orphans: the Traceability table maps exactly these six to Phase 31. REQ-gate-cost-recorded is listed in the 31-06 plan but mapped to Phase 34 and is rightly open; the Phase 31 reading is recorded.

### Anti-Patterns Found

None blocking. `grep TBD|FIXME|XXX|TODO|HACK` over the phase's source and test files is empty. Five `ASSUMPTION` markers remain in `din5480.py` (`ALPHA`, `RHO_FP`, `theoretical_pin_diameter`, `measure_over_pins`, `form_diameter`), each names what is unconfirmed; this is honest labelling, not a stub. Of those, `ALPHA` = 30 degrees is still marked a clause slot even though the tip/shift formulas it feeds reproduce the copy.

### Code review (31-REVIEW.md): 0 critical, 5 warnings, all open

None is a goal blocker. My assessment of the one you asked about:

**WR-02 does not contradict the goal.** The goal says "measurement over pins at nominal thickness", and `measure_over_pins` is exactly that, and its field description says so. REQ-mre-nominal asks for the nominal measure; the fit-dependent limits are REQ-mre-limits in Phase 34. The review is right about the risk though: the printed warning (`THEORETICAL_PIN`) says "M_Re is for this pin" and never says "at nominal thickness, ignoring the fit", while the designation beside it ends in `8f`. For W120x3x38x8f the copy's own M1 minimum is taken 0.091 mm below nominal thickness. A front end that shows `warnings` but not field descriptions would let a user cut to the nominal M under an 8f label. I rate this a WARNING to fix before Phase 33 builds the shaft page and CLI, a one-sentence change plus a test pin. It is not a Phase 31 gap, because the number is correct for what it claims.

The others: WR-01 (refusal message prints "+0.450" outside "+0.45", reproduced by the reviewer at `reference_d=25.001`, and the default sits on the edge so the first stepper click hits it), WR-03 (root warning lists hobbing only), WR-04 (`DesignationError` unpicklable; matters once the pool or 422 path ships it across a process), WR-05 (leading zeros accepted in number tokens, refused in the fit; docstring overstates). These are quality warnings for the next phases, not Phase 31 truth failures. Disposition is still `open` for all ten findings.

### Out-of-plan changes

`ac34e6a` (root_d labelled as the theoretical/broaching root, with a hobbed-root warning) and `8e880c4` (debt and idea filed) landed after the checkpoint. Both are consistent with the goal: they make `root_d` more honest and alter no number. `root_d` still prints the broaching value; I checked the warning prints "hobbed: root_d - 0.1*m = 113.100 mm" for W120x3x38.

### Human Verification Required

None new. The one human decision this phase needs (accepting the anchor shortfall as an override) is stated in the gap above.

### Gaps Summary

One gap, and it is about evidence, not about wrong code. SC2 and REQ-shaft-basic-dims require at least two copy rows for the basic dimensions; the phase has one (tip of W 120x3x38x8f). Root and nominal thickness have no copy row, and no second designation or odd-z row exists. The human knowingly accepted this at 31-05, it is filed as a must-severity debt item with a named trigger, and the requirement is honestly left Pending. Everything else in the goal is verified by running code. To move on: either the human records the override above, or the missing pages arrive and the debt item is worked.

---

_Verified: 2026-10-26_
_Verifier: Claude (gsd-verifier)_
