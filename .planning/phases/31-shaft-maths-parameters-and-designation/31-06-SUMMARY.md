---
phase: 31-shaft-maths-parameters-and-designation
plan: 06
subsystem: shaft-maths
tags: [din5480, anchors, citations, gate-delta, closing-decision, partial-pass]

requires:
  - phase: 31-shaft-maths-parameters-and-designation
    provides: the formulas, oracle, pins and guard, the codec (31-01 to 31-04), the checkpoint result (31-05)
provides:
  - tests/test_din5480_anchors.py, one cited test per approved row (d_a1, the d_Ff1 limit, M1)
  - DIN 5480-1:2006 citations in din5480.py for every item the copy confirmed; five markers left, named
  - the form-diameter sentence naming the copy's reason
  - the gate delta and the phase-close checks in bench/RESULTS.md
  - L47, the closing decision-log entry of Phase 31
affects: [phase-32, phase-33, phase-34]

plan_head_before: 8e880c4996b39a3f5feb04c4be180a0c955ab86f
plan_head_after: bf6de767dee32925d52f6c589ff5af5fefd556db

actuals:
  tokens: 5300    # chars/4 (21256 chars) over the lines added to src, tests, docs and bench since 8e880c4; the logs are evidence, not counted
  tasks: 3
  commits: 6      # measured: git rev-list --count 8e880c4..HEAD, before this SUMMARY's own commit

tech-stack:
  added: []
  patterns:
    - "an approved copy value is a test that cites part, clause and figure and compares to half a unit of the printed digit; a printed maximum is checked as a limit"
    - "a marker is replaced only by a clause the human confirmed; what the copy does not hold stays marked and is named in the closing entry"

key-files:
  created:
    - tests/test_din5480_anchors.py
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-06-red-anchor-tip.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-06-red-anchor-form-rho.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-06-red-anchor-measure-pin.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-06-verify.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-06-verify-meta.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-06-close-checks.log
  modified:
    - src/spur/din5480.py
    - src/spur/shaft_calc.py
    - bench/RESULTS.md
    - docs/architecture/decision_log.md

key-decisions:
  - "No constant or formula was edited: the checkpoint found no contradiction that changes a printed number (D1 was a label, fixed in ac34e6a; D3 and D5 are filed debt), so no D-09 entry was needed and the closing entry is L47"
  - "Even-count M_Re keeps printing: it reproduces the copy's M1 to 0.00004 and the warning says the pin is not the tabulated one; its clause (DIN 5480-15, 5.2.4.3) is unread and the marker says so rather than claiming Part 1"
  - "Check 9 of the phase-close checks reads FAIL and stays FAIL: only one basic-dimension row exists, the human accepted the partial pass at 31-05, and the log says so beside the word"
  - "REQ-shaft-basic-dims and REQ-gate-cost-recorded are not marked complete"

requirements-completed: [REQ-shaft-params, REQ-profile-shift-from-dB, REQ-form-diameter-honest, REQ-mre-nominal, REQ-designation-codec]

coverage:
  - id: D1
    description: "The three approved W 120x3x38x8f values are pinned as cited tests: d_a1 119.40, d_Ff1 maximum 113.91 as a limit, M1 minimum 125.956 at D_M 6.000 and s 6.180 (oracle at 1e-9)"
    requirement: "REQ-shaft-basic-dims"
    verification:
      - kind: unit
        ref: "tests/test_din5480_anchors.py#test_anchor_w120x3x38x8f_tip_diameter"
        status: pass
      - kind: unit
        ref: "tests/test_din5480_anchors.py#test_anchor_w120x3x38x8f_form_diameter_is_a_limit_not_a_construction"
        status: pass
      - kind: unit
        ref: "tests/test_din5480_anchors.py#test_anchor_w120x3x38x8f_measure_over_pins_at_the_rows_own_thickness_and_pin"
        status: pass
    human_judgment: true
    rationale: "The plan's minimum of two basic-dimension rows is not met (one exists); the human accepted a partial pass at 31-05 and the rest is filed as debt"
  - id: D2
    description: "Each confirmed formula and constant carries its DIN 5480-1:2006 clause in din5480.py; five markers stay for what the copy did not confirm, and none claims a Part 1 source for M_Re"
    requirement: "REQ-profile-shift-from-dB"
    verification:
      - kind: other
        ref: "grep -c ASSUMPTION src/spur/din5480.py prints 5; 31-06-close-checks.log check 8"
        status: pass
    human_judgment: true
    rationale: "Whether a clause citation matches the copy was judged by the human at 31-05; no test can check it"
  - id: D3
    description: "form_d stays null and its sentence names the copy's reason (a limit tied to the mating part, DIN 5480-1 Tables 3 and 4); odd-z M_Re stays null with ODD_Z_UNCONFIRMED and D_Re still prints"
    requirement: "REQ-form-diameter-honest"
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py (the form-null and odd-z tests) and tests/test_din5480_anchors.py#test_anchor_w120x3x38x8f_form_diameter_is_a_limit_not_a_construction"
        status: pass
    human_judgment: false
  - id: D4
    description: "Each anchor test seen red once against a deliberate perturbation, reverted, recorded in bench/RESULTS.md"
    requirement: "REQ-shaft-basic-dims"
    verification:
      - kind: other
        ref: "bench/RESULTS.md ### Seen red once (Phase 31), three 31-06 rows; investigation/31-06-red-anchor-*.log"
        status: pass
    human_judgment: false
  - id: D5
    description: "The phase's make verify is recorded against Phase 30's on the same host, eight of nine close checks pass, and L47 records the phase"
    requirement: "REQ-gate-cost-recorded"
    verification:
      - kind: other
        ref: "bench/RESULTS.md ### The gate delta (31-06) and ### Phase close checks (31-06); investigation/31-06-verify.log"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-10-26
status: complete
---

# Phase 31 Plan 06: The Anchors, the Gate Delta and the Closing Decision Summary

**The three copy values the human approved are pinned as cited tests and each was seen red once; every clause the copy confirmed replaced its marker, five markers stay for what it did not; `make verify` reads `2355 passed in 243.23s` (+4.3 % on Phase 30, inside the spread); and L47 closes the phase, which proved the maths on one designation and left d_Ff and odd-count M_Re null.**

## Performance

- **Duration:** 12 min (07:09 to 07:21 UTC, of which the gate run is 4 min 12 s)
- **Tasks:** 3 (the tracer, the remaining rows and markers, the gate delta and L47)
- **Files:** 4 modified, 7 created

## Accomplishments

- Task 1 (`0763238`): `test_anchor_w120x3x38x8f_tip_diameter` (d_a1 119.40, tolerance 0.005); the tip markers became DIN 5480-1:2006 cl. 6, Table 3.
- Task 2 (`e77b233`, `24a844e`, `5b7c473`): the `d_Ff1` limit row and the `M1` row (oracle agrees at 1e-9 once the row's thickness is written as a shift); the shift, root, `h_fP`, thickness, range and odd-factor markers became citations (cl. 4, cl. 6 Table 3, cl. 7.1); the form-diameter sentence now names the copy's reason; three anchors seen red once.
- Task 3 (`a97e1b8`, `bf6de76`): the gate delta, the close checks and L47.

## Checkpoint outcome, per item

| Item | Outcome |
|---|---|
| A1 shift, A2 tip and h_aP, A4 thickness | confirmed, cl. 6 Table 3, cited; d_a1 pinned |
| A3 root and h_fP | formula confirmed, cl. 6 Table 3 and cl. 7.1; `H_FP` 0.55 is the theoretical root, hobbing is 0.60; labelled in `ac34e6a`; no constant changed |
| A5 even M_Re | not in Part 1; the formula reproduces M1 (anchored), its clause (DIN 5480-15, 5.2.4.3) unread, marker kept |
| A6 odd M_Re | form consistent with cl. 4 eq. (1), cited; no odd-count row, so it stays null with `ODD_Z_UNCONFIRMED` |
| A7 shift range | matches for the shaft, cited; the copy's exceptions at larger tooth counts are debt (D3) |
| A8 fit | `8f` is the copy's spelling; `FIT_PATTERN` and `fit` unchanged; the pattern being wider is debt (D5) |
| A9 d_Ff | a limit tied to the mating part (Tables 3 and 4): `form_d` null, sentence updated, the printed 113.91 checked as a limit |
| A10 gauge series | none in Part 1; 0.01 mm stays, marker kept in `shaft_calc.py` |
| D2, D4 | labelling and naming only; D2 got a note on `form_diameter`'s validity, D4 is left (see Handoffs) |

## Shipped nulls

`form_d` (every shaft), M_Re for an odd tooth count (D_Re still prints). The pin diameter and even-count M_Re print from the computed theoretical pin, warned as not the tabulated one.

## Gate delta

`make verify`: `2355 passed in 243.23s (0:04:03)`, `real 244.14`, exit 0, at `5b7c473`, load 7.03 to 4.58, against Phase 30's `1369 passed`, `233.18 s`, `real 234.48 s`: +10.05 s (+4.31 %) and +9.66 s (+4.12 %), inside Phase 25's about 8 % spread, 56.77 s under L43's 300 s bar. 986 tests added by the phase. Coverage `98.23%`.

## Handoffs

Phase 32: widen `Part`, the three internals, the solid fields' bounds and cross-field rules. Phase 33: `DesignationError.token` and the infeasible error in its 422s, the twelve `ShaftDimensions` keys, the part switch. Phase 34: the copy's D_Re replaces the computed pin with a warning, the guard goes live, the fit tables, the anchor rows of the debt item. Open with the human, not changed here: `THEORETICAL_PIN` says "It is not the D_Re that DIN 5480 tabulates", which no page seen so far shows (D4); the debt item covers it.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] The form-diameter sentence and the `form_d` field description gave a reason the copy contradicts**
- **Found during:** Task 2, outcome A9
- **Issue:** both said the construction was "not yet proven" and that vendors print a limit; the copy (cl. 9.1, Tables 3 and 4) says the standard prints a limit tied to the mating part. The plan allows the sentence to gain the copy's reason.
- **Fix:** rewrote both in plain words; `form_d` stays null; no tests pinned the literal (they import the constant).
- **Files modified:** `src/spur/shaft_calc.py`
- **Commit:** `24a844e`

**2. [Rule 1 - Bug] Two pure-maths helpers (`inv`, `_involute_angle`) carried a "clause slot" marker for a clause that cannot exist**
- **Found during:** Task 2
- **Fix:** the markers now say "a mathematical definition, no clause" and "numerical, no clause". This is why five markers remain and not seven.
- **Files modified:** `src/spur/din5480.py`; **Commit:** `e77b233`

**3. The plan's anchor minimum and verify command are not met.** The phase-close check 9 (two basic-dimension rows) reads `FAIL`, so the plan's second Task 3 verify (`grep -c FAIL` is 0, `PASS` at least 9) reads 1 and 8. This is the partial pass the human accepted at 31-05, not a defect; the log carries that beside the word.

**Total deviations:** 2 auto-fixed, 1 accepted shortfall. **Impact:** no printed number changed in this plan.

Also: the first M1 perturbation (the sign of `s / d`) was discarded because the test failed on `None`, showing no number; the kept break moves the number (row recorded).

## Known Stubs

None.

## Threat Flags

None. No new route or trust boundary; only the three approved values, each cited, entered the repository (T-31-13, T-31-15); no tolerance was widened (T-31-14).

## Debt and ideas

Filed by earlier work and cited by L47, none new in this plan: the anchor rows (`2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md`, must), the shift range (`...shaft-shift-range-narrower-than-din-5480-exceptions.md`, must), the fit pattern (`...fit-pattern-accepts-fits-outside-the-standards-set.md`, nice) and the process-field idea (`docs/ideas/2026-10-26-shaft-manufacturing-process-field.md`).

## Requirements

Marked complete: REQ-shaft-params, REQ-profile-shift-from-dB (formula confirmed by clause; the range refuses the copy's exceptions, which is debt and errs on the honest side), REQ-form-diameter-honest, REQ-mre-nominal (odd count null as the requirement says; even count anchored by M1), REQ-designation-codec. **Left open:** REQ-shaft-basic-dims (one basic-dimension row, not two) and REQ-gate-cost-recorded (Phase 34's milestone reading).

## Next Phase Readiness

Phase 31 is complete for the plans; the phase verification will need to weigh the partial pass. Phase 32 can start.

## Self-Check: PASSED

- `tests/test_din5480_anchors.py`, the three red logs, `31-06-verify.log`, `31-06-verify-meta.log` and `31-06-close-checks.log` exist.
- `0763238`, `e77b233`, `24a844e`, `5b7c473`, `a97e1b8` and `bf6de76` are ancestors of HEAD.
- `git status --porcelain -- src tests` prints nothing; the L47 commit changes no line of `src` or `tests` and deletes no line of the log.
