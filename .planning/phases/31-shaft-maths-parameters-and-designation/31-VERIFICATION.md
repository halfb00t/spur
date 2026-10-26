---
phase: 31-shaft-maths-parameters-and-designation
verified: 2026-10-26T16:00:00Z
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
covered_digest: "v3:sha256:b33c97eded6f7a9ce23d86aa94771a143a8a8535ade4c601283acb5ad39f3a7b"
behavior_unverified: 0
overrides_applied: 1
overrides:
  - must_have: "d_B, tip, root and nominal thickness agree with at least two anchor rows from the copy"
    reason: "DIN 5480 Part 1 has no size tables; one designation (W 120x3x38x8f, cl. 9.1 Fig. 6) is anchored for the tip; the rest is filed as must-severity debt 2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing. Accepted at the 31-05 checkpoint (partial pass + debt); accepted_by entered by the agent on the human's explicit instruction."
    accepted_by: "Andrew S"
    accepted_at: "2026-10-26"
re_verification:
  previous_status: gaps_found
  previous_score: 4/5
  gaps_closed:
    - "SC2 / REQ-shaft-basic-dims: d_B, tip, root and nominal thickness agree with at least two anchor rows from the copy (closed by override, not by new evidence; the shortfall stays in the debt item)"
  gaps_remaining: []
  regressions: []
deferred: []
advisory: []
coincidental_reliance_items: []
human_verification: []
---

# Phase 31: Shaft Maths, Parameters and Designation Verification Report

**Phase Goal:** A user can ask the pure maths for a DIN 5480 external shaft from reference diameter, module, tooth count and tolerance field and get honest numbers: the profile shift the standard derives, tip and root diameters, nominal tooth thickness, measurement over pins at nominal thickness, each proved against an independent oracle and against rows of the copy, with the form diameter and odd-z M_Re `null` until proven, and a designation that prints and parses back to the same shaft. No solid, no route, no page yet.
**Verified:** 2026-10-26 (re-verification; initial 2026-10-26T14:00:00Z)
**Status:** passed
**Re-verification:** Yes, after the human recorded an override for the one gap

## Re-verification scope

No code changed. `git diff 68b95c0 --stat -- src tests` is empty, and the only file changed since 68b95c0 is this report (the added `overrides:` block). The fingerprint over the same implementation files gives the same digest as the initial report (`v3:sha256:b33c97ed...`). Regression check: the four shaft test files gave `986 passed in 2.19s`, the same count as the initial run. Every other finding below carries forward from the initial verification without being re-derived.

The one change is that truth 2 now reads PASSED (override). The override's `must_have` matches truth 2 on 14 of its 16 tokens (87.5 %), and the gap wording on all 16, so it clears the 80 % threshold. It names an acceptor (Andrew S) and a date (2026-10-26). The agent typed the name on the human's explicit instruction, and I treat that as the human's acceptance.

## Verdict

The maths, the oracle, the codec, the null discipline and the gear-safety guard are all real and work (initial run: focused suites, ruff, `mypy --strict`, `lint-imports`, `gear.unchanged`, five shafts and the hostile designations). The one clause not met as written, "against rows of the copy", is now covered by a recorded human override. The override accepts the shortfall but does not fill it. The evidence is unchanged: one copy designation, and only its tip diameter is a basic-dimension row.

## Goal Achievement

### Observable Truths (ROADMAP success criteria; PLAN must-haves add detail, none subtract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: Frozen `ShaftParams` contract, shift from d_B, epsilon edge, range refusal naming the range, gear untouched | VERIFIED | `tests/test_shaft_params.py::test_the_shaft_field_names_and_defaults_are_frozen`, bound and edge tests; 986 passed (re-run today, unchanged). `ShaftParams(reference_d=25.5)` raises `infeasible` naming "-0.05 to +0.45". `git diff v0.6 -- calc.py params.py requirements.txt` empty. W30x2x14 prints x = -0.05 and validates. Red logs 31-01-red-*.log present. |
| 2 | SC2: d_B, tip, root, thickness agree with the independent oracle and with at least two copy anchor rows | **PASSED (override)** | Override: "DIN 5480 Part 1 has no size tables; one designation (W 120x3x38x8f) is anchored for the tip; the rest is filed as must-severity debt", accepted by Andrew S on 2026-10-26. Underlying evidence unchanged. Oracle half VERIFIED: `tests/shaft_oracle.py` imports only `math` and rebuilds tip and thickness by a different route (base-thickness identity), over a 192-case grid plus vendor sets. Copy half: one row (d_a1 119.40); root and thickness have no copy row. |
| 3 | SC3: d_Ff `null` with a sentence, even-z M_Re and D_Re agree with oracle, contact guard or `null` with a warning, odd z `null` until an odd row | VERIFIED | `form_d` None with the form sentence in `warnings` everywhere. Odd z (25/1.25/19) gives `pin_d` 2.36 and `measure_over_pins` None. `pin_measurement` has both null branches, covered by direct calls (31-03-red-guard-swapped.log). Even-z M1 reproduces the copy's 125.956 at the row's own s and pin, within 0.00004. |
| 4 | SC4: Designation prints and parses back, `.` and `,`, refusal names the bad token, fit shape only | VERIFIED | Five shafts round-tripped through `format_designation`/`parse_designation`, with `,` as well. Refused: `W 25x1.25x18` (token `25x1.25x18`), `X ...` (token `X`), `18.5` (token `18.5`), `8F` (token `8F`). Red logs 31-04-red-*.log. |
| 5 | SC5: Gate delta recorded; Phase 30 check green | VERIFIED | `bench/RESULTS.md` "The gate delta (31-06)": 2355 passed, 243.23 s vs Phase 30's 233.18 s (+4.3 %, inside the ~8 % spread, under L43's 300 s). `python -m scripts.gear_unchanged`: "byte-equal to v0.6". Orchestrator gate: `make verify` exit 0, 2355 passed. |

**Score:** 5/5 truths (4 VERIFIED, 1 PASSED (override); 0 present, behavior-unverified).

### Override applied

The suggested override from the initial report has been recorded in the frontmatter by the human (accepted_by "Andrew S", accepted_at 2026-10-26) and is applied to truth 2. The override closes the verification gap only. **REQ-shaft-basic-dims stays Pending**: the requirement asks for at least two copy anchor rows, the phase has one, and an accepted shortfall is not a completed requirement. The debt item `docs/tech_debt/active/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md` (must) still carries the missing rows, with the trigger "DIN 5480 Part 2 or Part 15 pages become available". When those rows land, truth 2 can be re-verified as VERIFIED and the requirement marked complete.

### Deferred Items

None.

### Advisory (New Scope, Unevidenced)

None. Re-verification found no new findings, because no code changed.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/din5480.py` | Formulas, constants, codec | VERIFIED | 259 lines, real maths, clause-cited, 5 ASSUMPTION markers named; no cadquery/logger/gear imports |
| `src/spur/shaft_calc.py` | `derive_shaft`, `check_shaft`, pin guard | VERIFIED | Wired to `din5480`; `form_d=None` always; odd gate present |
| `src/spur/shaft_params.py` | `ShaftParams` | VERIFIED | Frozen, validated once via `model_validator` -> `check_shaft` |
| `tests/shaft_oracle.py` | Independent oracle | VERIFIED | Imports `math` only |
| `tests/test_din5480_anchors.py` | Copy anchor rows | PARTIAL (covered by override) | 3 cited tests, 1 basic-dimension row; shortfall accepted, carried by the debt item |
| `src/spur/parts.py` | `Part = GearParams` | VERIFIED | Phase 32 widens it, by design |

### Key Link Verification

| From | To | Status | Details |
|------|----|--------|---------|
| `ShaftParams._feasible` | `shaft_calc.check_shaft` | WIRED | Local import; refusal reaches the caller as a validation error |
| `derive_shaft` | `din5480.*` | WIRED | All formulas called; designation from `format_designation` |
| `shaft_oracle` | `spur` | INTENTIONALLY ABSENT | The oracle must not import spur |
| shaft maths | gear maths | ABSENT (required) | `lint-imports`: 10 contracts kept, 0 broken |

### Data-Flow Trace (Level 4)

Not applicable: pure functions, no rendering, no data source. Values flow from arguments to the returned model.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Code unchanged since initial report | `git diff 68b95c0 --stat -- src tests` | empty | PASS (re-verification) |
| Shaft tests | `.venv/bin/python -m pytest -q` on 4 shaft files | `986 passed in 2.19s` | PASS (re-run today) |
| Lint, types | `ruff check src tests`; `mypy --strict` on 3 modules | clean | PASS (carried forward) |
| Import contracts | `lint-imports` | 10 kept, 0 broken | PASS (carried forward) |
| Gear unchanged | `python -m scripts.gear_unchanged` | byte-equal to v0.6 | PASS (carried forward) |
| Default shaft | `derive_shaft` | tip 24.75, root 22.25, s 2.613, form None, M_Re 27.999 | PASS (carried forward) |
| W120x3x38 | `derive_shaft` | tip 119.4, root 113.4 (Hexagon 113.40), M_Re 125.902 | PASS (carried forward) |
| Odd z | 25/1.25/19 | pin 2.36, M_Re None | PASS (carried forward) |

I did not re-run the full `make verify`. The orchestrator's run (exit 0, 2355 passed in 175.70 s) stands as the gate evidence, and no code has changed since then.

### Probe Execution

SKIPPED: no probes declared by this phase.

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|-------------|-------------|--------|----------|
| REQ-shaft-params | 31-01, 31-04, 31-05, 31-06 | SATISFIED | Frozen-contract test, boundary validation |
| REQ-profile-shift-from-dB | 31-01, 31-02, 31-05, 31-06 | SATISFIED | Formula confirmed by clause; epsilon edges; range refusal. The accepted range is narrower than the copy's exceptions (debt D3; it errs toward refusing) |
| REQ-shaft-basic-dims | 31-01, 31-02, 31-04, 31-05, 31-06 | **PENDING (partial; phase gap overridden)** | Oracle yes; "at least two anchor rows" no. The override lets the phase close; it does not complete the requirement. Stays Pending in REQUIREMENTS.md until the debt item is worked |
| REQ-form-diameter-honest | 31-03, 31-05, 31-06 | SATISFIED | `form_d` None everywhere with a reason; the copy's printed limit 113.91 checked as a limit |
| REQ-mre-nominal | 31-03, 31-05, 31-06 | SATISFIED | Even z at nominal with the guard; odd z null; see WR-02 note below |
| REQ-designation-codec | 31-04, 31-06 | SATISFIED | Round trip and refusals verified |

All six phase IDs appear in PLAN frontmatter and in REQUIREMENTS.md. No orphans: the Traceability table maps exactly these six to Phase 31. REQ-gate-cost-recorded is listed in the 31-06 plan but mapped to Phase 34 and correctly stays open; the Phase 31 reading is recorded.

### Anti-Patterns Found

None blocking (carried forward; no files changed). `grep TBD|FIXME|XXX|TODO|HACK` over the phase's source and test files is empty. Five `ASSUMPTION` markers remain in `din5480.py` (`ALPHA`, `RHO_FP`, `theoretical_pin_diameter`, `measure_over_pins`, `form_diameter`). Each one names what is unconfirmed, so they are honest labels, not stubs. One loose end: `ALPHA` = 30 degrees is still marked as a clause slot, although the tip and shift formulas that use it reproduce the copy.

### Code review (31-REVIEW.md): 0 critical, 5 warnings, all open

None of the warnings blocks the goal.

**WR-02 (fix before Phase 33).** The goal asks for "measurement over pins at nominal thickness", and `measure_over_pins` delivers exactly that; its field description says so. Fit-dependent limits belong to REQ-mre-limits in Phase 34. The risk is real, though. The printed warning (`THEORETICAL_PIN`) says "M_Re is for this pin" but never says "at nominal thickness, ignoring the fit", and the designation printed beside it ends in `8f`. For W120x3x38x8f, the copy's own M1 minimum is taken 0.091 mm below nominal thickness. A front end that shows `warnings` but not field descriptions would let a user cut to the nominal M under an 8f label. Fix it before Phase 33 builds the shaft page and CLI: a one-sentence warning change plus a test that pins it. It is not a Phase 31 gap, because the number is correct for what it claims.

The other four: WR-01 (the refusal message prints "+0.450" against a range shown as "+0.45"; reproduced at `reference_d=25.001`; the default sits on the range edge, so the first stepper click hits it), WR-03 (the root warning lists hobbing only), WR-04 (`DesignationError` cannot be pickled; matters once the pool or 422 path sends it across a process), WR-05 (leading zeros accepted in number tokens but refused in the fit; the docstring overstates). These are quality warnings for the next phases, not Phase 31 truth failures. All ten findings are still `open`.

### Out-of-plan changes

`ac34e6a` (root_d labelled as the theoretical/broaching root, with a hobbed-root warning) and `8e880c4` (debt and idea filed) landed after the checkpoint. Both fit the goal: they make `root_d` more honest and change no number. `root_d` still prints the broaching value, and the warning prints "hobbed: root_d - 0.1*m = 113.100 mm" for W120x3x38.

### Human Verification Required

None. The human decision this phase needed, accepting the anchor shortfall, has been made and recorded as the override above.

### Gaps Summary

No open gaps. The single gap from the initial verification (SC2's "at least two copy anchor rows") is closed by a named human override, not by new evidence. The shortfall itself (one tip row; no root, nominal-thickness or second-designation row) still exists. It is carried by the must-severity debt item, and REQ-shaft-basic-dims stays Pending until those rows arrive. WR-02 should be fixed before Phase 33.

---

_Verified: 2026-10-26 (re-verification)_
_Verifier: Claude (gsd-verifier)_
