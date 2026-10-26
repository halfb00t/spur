---
phase: 31
review: 31-REVIEW.md
titles: json
findings:
  - id: IN-18
    severity: info
    disposition: fixed
    title: "\"A break that reaches it alone\" is false for the shift and thickness runs"
  - id: IN-19
    severity: info
    disposition: fixed
    title: "8c77302's logs and RESULTS rows cite line numbers of a later commit, and no log carries revert proof"
  - id: IN-20
    severity: info
    disposition: fixed
    title: "`test_shaft_calc.py`'s module docstring still describes the anchor file before Part 2"
  - id: IN-21
    severity: info
    disposition: fixed
    title: "The idea's Related files still points to one odd anchor row (WR-07 residue)"
  - id: IN-22
    severity: info
    disposition: fixed
    title: "The cause given for the 706/700 gap (\"misses a few rows at page breaks\") has no evidence in the repo"
  - id: WR-07
    severity: warning
    disposition: fixed
    title: "Two of the four approved rows have an odd tooth count, but every new text says one"
  - id: WR-08
    severity: warning
    disposition: fixed
    title: "\"Each assertion was seen red once\" is false for da1, for the odd-row null, and for the oracle cross-check"
  - id: WR-09
    severity: warning
    disposition: fixed
    title: "The amendment quotes the guard margin as 0.067*m; the margin is 0.1*m"
  - id: WR-10
    severity: warning
    disposition: fixed
    title: "The published `measure_over_pins` description still says an odd count is \"unconfirmed\""
  - id: WR-11
    severity: warning
    disposition: fixed
    title: "The printed pin sentence says the pin \"has not been compared with a tabulated D_Re\"; this diff compares it, and it differs for the default shaft"
  - id: IN-10
    severity: info
    disposition: fixed
    title: "The null-pin test's docstring still gives the pre-IN-07 reason for withholding `THEORETICAL_PIN`"
  - id: IN-11
    severity: info
    disposition: fixed
    title: "`H_FP_HOBBING`'s comment says only the hobbed-root sentence reads it; the `root_d` field description reads it too"
  - id: IN-12
    severity: info
    disposition: fixed
    title: "The basic-dimensions docstring claims more about the shift range than the test proves"
  - id: IN-13
    severity: info
    disposition: fixed
    title: "706 nominal rows but 700 M1 rows, and the amendment says \"all\""
  - id: IN-14
    severity: info
    disposition: fixed
    title: "The anchor module docstring's first paragraph is now stale, and `tables` is never read"
  - id: IN-15
    severity: info
    disposition: fixed
    title: "The L47 amendment spans five paragraphs, and one of them opens like an original section"
  - id: IN-16
    severity: info
    disposition: fixed
    title: "Resolving the anchor item drops the gauge-series bullet and leaves REQ-shaft-basic-dims \"can close\" untracked"
  - id: IN-17
    severity: info
    disposition: fixed
    title: "The code that the new form-diameter debt item is about does not point to it"
  - id: IN-07
    severity: info
    disposition: fixed
    title: "`THEORETICAL_PIN` still says \"M_Re is for this pin\" for an odd tooth count, where no M_Re is printed"
  - id: IN-08
    severity: info
    disposition: fixed
    title: "The `module` branch of `_exact` has no test, and the hobbed-root test indexes `warnings[2]`"
  - id: IN-09
    severity: info
    disposition: fixed
    title: "`H_FP_HOBBING` is a second hand-copied 0.60, outside the constants block"
  - id: WR-06
    severity: warning
    disposition: fixed
    title: "The shift refusal still contradicts itself for an overshoot under 0.00005, and `{reference_d:g}` hides the nudge"
  - id: IN-01
    severity: info
    disposition: fixed
    title: "Debt items point at stale line numbers"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "Stale module docstring in `tests/test_shaft_calc.py`"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "`THEORETICAL_PIN` makes a claim no seen page supports, and stays when the pin is null"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "The 0.1*m drop is written twice and `HOBBED_ROOT_DROP` is not tied to `H_FP`"
  - id: IN-05
    severity: info
    disposition: fixed
    title: "The default shaft sits on the range edge, and `shaft_params` imports the gear's private helpers"
  - id: IN-06
    severity: info
    disposition: fixed
    title: "The leading-zero comment promises \"one spelling per shaft\", but five other spellings parse"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "The refusal message contradicts itself near the range edges"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`measure_over_pins` is printed next to a fit designation but is the nominal-thickness measure, and no warning says so"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "The `root_d` warning names only hobbing; the copy names more processes"
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "`DesignationError` cannot be pickled, copied or re-raised across a process boundary"
  - id: WR-05
    severity: warning
    disposition: fixed
    title: "`parse_designation` accepts leading zeros in the number tokens but refuses them in the fit; its docstring says otherwise"
open: 0
total: 33
recorded: 2026-10-26T16:24:43.015Z
---

# Phase 31: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| IN-18 | info | fixed | 31-REVIEW-FIX.md |
| IN-19 | info | fixed | 31-REVIEW-FIX.md |
| IN-20 | info | fixed | 31-REVIEW-FIX.md |
| IN-21 | info | fixed | 31-REVIEW-FIX.md |
| IN-22 | info | fixed | 31-REVIEW-FIX.md |
| WR-07 | warning | fixed | 31-REVIEW-FIX.md (not in the current review) |
| WR-08 | warning | fixed | 31-REVIEW-FIX.md (not in the current review) |
| WR-09 | warning | fixed | 31-REVIEW-FIX.md (not in the current review) |
| WR-10 | warning | fixed | 31-REVIEW-FIX.md (not in the current review) |
| WR-11 | warning | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-10 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-11 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-12 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-13 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-14 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-15 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-16 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-17 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-07 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-08 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-09 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| WR-06 | warning | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-01 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-02 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-03 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-04 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-05 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| IN-06 | info | fixed | 31-REVIEW-FIX.md (not in the current review) |
| WR-01 | warning | fixed | 31-REVIEW-FIX.md (not in the current review) |
| WR-02 | warning | fixed | 31-REVIEW-FIX.md (not in the current review) |
| WR-03 | warning | fixed | 31-REVIEW-FIX.md (not in the current review) |
| WR-04 | warning | fixed | 31-REVIEW-FIX.md (not in the current review) |
| WR-05 | warning | fixed | 31-REVIEW-FIX.md (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
