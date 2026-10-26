---
phase: 31-shaft-maths-parameters-and-designation
reviewed: 2026-10-26T00:00:00Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - src/spur/din5480.py
  - src/spur/shaft_calc.py
  - tests/test_din5480_anchors.py
  - tests/test_shaft_calc.py
  - docs/architecture/decision_log.md
  - docs/tech_debt/resolved/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md
  - docs/tech_debt/active/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md
  - docs/tech_debt/active/2026-10-26-shaft-shift-range-narrower-than-din-5480-exceptions.md
  - docs/ideas/2026-10-26-print-odd-tooth-count-measure-over-pins.md
findings:
  critical: 0
  warning: 5
  info: 8
  total: 13
status: issues_found
---

# Phase 31: Code Review Report (DIN 5480-2 anchors follow-up)

**Reviewed:** 2026-10-26
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Scope: diff `a7a7df3..HEAD` (8ff9eca, 8daa87a, 45b6565, 87ca176) in the nine listed files. I also read the two INDEX rows and the five `31-part2-red-*.log` files as evidence for the prose.

Tests: `.venv/bin/python -m pytest tests/test_din5480_anchors.py tests/test_shaft_calc.py tests/test_din5480.py tests/test_shaft_params.py -q` gave `1018 passed in 2.22s`. That is the previous 1007, plus 3 W 120 anchors, plus 8 new parametrized cases. I did not run `make verify`.

Mutation probes, run in a scratch copy (`src/` and `tests/` copied out, repo untouched, `git status --porcelain` empty):
- `TIP_DIAMETER_OFFSET = 0.22`, the committed "tip" break, never reaches the `tip_d` line. Its first failures are at :106 (x*m), in `_params` (W 30x2x14 refused at x -0.0600) and at :109.
- `tip_diameter` returning `reference_d - 0.21 * m` goes red at :111, `assert 29.58 == 29.6 ± 0.005`.
- Deleting the odd gate in `pin_measurement` goes red at :134, `assert 35.299 is None`, for W 26x1.25x19 and W 30x2x13.
So the assertions can fail, but the committed red evidence does not show it (WR-08).

The checks you asked for:
- **T-31-13: holds.**
  - Every DIN 5480 value in the diff is one of the 24 approved numbers or an already committed one. `PART_2_ROWS` matches the approved table cell for cell.
  - The other numbers are derived statistics or tool output: 705/706, 470, 0.174*m, 11, x 0.617-0.879, -0.031, median +0.018, 33 rows at h_fP 0.60, 492/208, 16 of 700, "about 30 %", z >= 60, m 0.6-1.75, and the tool's 0.562.
  - My judgement: x 0.617 and 0.879 are each one unnamed row's x. They are not flagged, because x is a public function of the designation and not a table cell, and without the designation it maps back to no cell. "Tables 12/13, 18/19" and "Part 2 cl. 1" are citations, not clause text.
- **Tolerances: mostly as briefed.**
  - Every Part 2 assertion is at half a unit of the printed digit or tighter ("never wider" holds).
  - The m = 2 x*m check at the table's digit is ±0.05, so x can drift ±0.025 before it fails. The tip probe showed it passing 0.88 against 0.9. The tool-digit line :109 catches that drift, so it is not a finding.
  - The odd-row `measure_over_pins is None` assertion is there. It also runs for W 30x2x13, which is odd too (WR-07).
- **L05/L08: hold.**
  - No constant, default, bound or printed number moved. The only `src/` changes are the `ODD_Z_UNCONFIRMED` string and two docstrings.
  - `derive_shaft` on the four rows prints x*m 0.562/0.438/-0.1/0.9, tip 24.75/25.75/29.6/29.6, root 22.25/23.25/25.6/25.6 and s 2.613/2.469/3.026/4.181, as before.
- **Prose vs code: four mismatches.** WR-07 (two odd rows, not one), WR-09 (margin misquoted), WR-10 (schema still says "unconfirmed") and WR-11 (the printed pin sentence is now false).
- **L47 amendment: follows the convention on edits.** The diff to `decision_log.md` is additions only, and it ends "No existing sentence of this entry is edited." Its shape departs from the log's precedent (IN-15).

IN-10 and IN-11 are not touched by this diff, so they are carried forward verbatim.

## Warnings

### WR-07: Two of the four approved rows have an odd tooth count, but every new text says one

**File:** `src/spur/din5480.py:143-144`, `tests/test_din5480_anchors.py:12,124-125`, `docs/ideas/2026-10-26-print-odd-tooth-count-measure-over-pins.md:15`, `docs/architecture/decision_log.md:3183`, `docs/tech_debt/resolved/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md` (Resolution, first sentence)
**Issue:** W 30x2x13 has z = 13. Every new text names only W 26x1.25x19 as the odd row:
- `measure_over_pins`: "four approved rows, one odd".
- The M1 test docstring: "W 26x1.25x19 is an odd tooth count, so this is the first row behind the odd-count factor".
- The idea: "One odd row, W 26x1.25x19, is committed".
- The amendment and the resolution label W 26x1.25x19 alone as the odd row.

The committed evidence says otherwise. `31-part2-red-odd-factor.log` fails both `W 26x1.25x19x8f` and `W 30x2x13x8f`, and the test's `if p.teeth % 2:` branch runs for both. The text understates the evidence: the odd factor is anchored at two modules (1.25 and 2), and once at the upper shift edge. That matters to the human's open idea of printing the odd M_Re.
**Fix:** Say "two odd (W 26x1.25x19, z 19, and W 30x2x13, z 13)" in each place. For the test docstring:
```python
    print. W 26x1.25x19 and W 30x2x13 have odd tooth counts, so these are the first rows behind
    the odd-count factor cos(pi/(2*z)); the shaft still prints no M_Re for either
    (ODD_Z_UNCONFIRMED, D-13)."""
```
The decision-log line must not be edited. Correct it with a further amendment sentence, or leave it, since "an odd tooth count" alone is not false.

### WR-08: "Each assertion was seen red once" is false for da1, for the odd-row null, and for the oracle cross-check

**File:** `docs/tech_debt/resolved/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md` (Resolution: "each assertion was seen red once"), `docs/architecture/decision_log.md:3186`, `tests/test_din5480_anchors.py:111,132,134`
**Issue:** The amendment says each row's "x*m, s1, da1, df1, D_M and M1 ... was seen red once (`31-part2-red-*.log`)". The resolution says "each assertion". Three assertions were never seen red:
- **`tip_d` (:111).** `31-part2-red-tip.log` breaks `TIP_DIAMETER_OFFSET`, which also feeds `SHIFT_TERM`. The test stops at the shift line :106 first (W 30x2x14 is refused inside `_params`), so :111 is never executed. I reproduced this; the log's 6 "comparison failed" lines for 8 failures are the same effect. `bench/RESULTS.md` row 31-02 R1 records the same trap ("the tip is seen red by its own break") and fixed it with a break in `tip_diameter`'s body. This round repeats the trap.
- **`measure_over_pins is None` for odd rows (:134).** No log breaks the gate. The odd-factor break fails at the M1 line :131, before :134.
- **The oracle line (:132).** It always sits behind :131, so it is not seen red on its own either.

The new red runs are also not appended to `bench/RESULTS.md` `### Seen red once (Phase 31)`, whose preamble says "later plans append rows". The logs carry no first-failure line and no revert proof, unlike every row of that table. D_M is a test input, so "D_M ... seen red" means nothing.
**Fix:** Run and keep two more logs:
- `tip_diameter` returning `reference_d - 0.21 * m`. Expect :111 red, `assert 29.58 == 29.6 ± 0.005`.
- The odd gate removed in `pin_measurement`. Expect :134 red, `assert 35.299 is None`.

Then append all seven runs as `bench/RESULTS.md` rows, each with its first failure line and its revert. Alternatively, narrow the prose to what the logs show (x*m, s1, df1, M1), say why da1 and the odd null are not among them, and drop "D_M".

### WR-09: The amendment quotes the guard margin as 0.067*m; the margin is 0.1*m

**File:** `docs/architecture/decision_log.md:3194`
**Issue:** "by up to 0.174*m, against the margin's 0.067*m" is wrong. `GUARD_MARGIN_FACTOR = 0.1` (`src/spur/shaft_calc.py:36`), and L47 **The guard** says the window is form + `0.1*m`. 0.067*m is the larger observed gap that the margin was sized from (1.5 × 0.067 = 0.1). The debt file says it correctly: "L47's guard margin was sized from two gaps of at most 0.202 mm at m 3 (0.067*m)". Phase 34 will size the live guard from this log. A reader who takes 0.067*m as the margin under-reads the real margin by a third, and compares the 0.174*m gap with the wrong number.
**Fix:** Do not edit line 3194. Add one sentence to the amendment, for example: "Correction to this amendment: 0.067*m is the larger observed gap the margin was sized from, not the margin itself, which is 0.1*m (`GUARD_MARGIN_FACTOR`)."

### WR-10: The published `measure_over_pins` description still says an odd count is "unconfirmed"

**File:** `src/spur/shaft_calc.py:130-134` (also the constant name at `:58`)
**Issue:** 45b6565 removed "until a DIN 5480 row confirms the odd-tooth formula" from `ODD_Z_UNCONFIRMED`, because Part 2 now confirms it. The new docstrings say so too (`shaft_calc.py:191-193`, `din5480.py:142-145`). The schema text was left behind: the `ShaftDimensions.measure_over_pins` description, which goes into the JSON schema, still reads "Null for an odd tooth count (unconfirmed)". That is now the opposite of the decision log and the idea file: the formula is confirmed, and the null is the human's choice (D-13).

The new warning also gives no reason at all ("not given for an odd tooth count yet"), where every other null-sentence in this file says why. The constant name `ODD_Z_UNCONFIRMED` keeps the stale claim in code. No `/api/shaft` route exists yet (L47), so no published contract moves.
**Fix:**
```python
        description="Measurement over pins M_Re at nominal thickness, for the printed pin. "
                    "Null for an odd tooth count (not printed yet, D-13) and when the pin "
                    "does not touch the flanks within the contact window.",
```
Optionally give the warning its reason, e.g. "... is not given for an odd tooth count yet: it is held back until it can be printed at the standard's pin (D-13) ...", and rename the constant together with the idea's "retire `ODD_Z_UNCONFIRMED`" step.

### WR-11: The printed pin sentence says the pin "has not been compared with a tabulated D_Re"; this diff compares it, and it differs for the default shaft

**File:** `src/spur/shaft_calc.py:43-47`; pinned by `tests/test_shaft_calc.py:150`
**Issue:** Every shaft prints `THEORETICAL_PIN`: "The tool computes this pin; it has not been compared with a tabulated D_Re." The resolution identifies Part 2's per-row D_M as "Phase 34's tabulated pin", and L47's Phase 34 handoff calls it "the copy's tabulated D_Re". After this diff, the claim is false in the repo itself:
- `PART_2_ROWS` pins D_M 2.75 and M1 28.050 for W 25x1.25x18, the default shaft.
- For that same shaft `derive_shaft` prints pin 2.73 and M_Re 27.999 (checked).
- The idea file records that the theoretical pin matches Part 2's pin in only 16 of 700 rows.

A user who reads "not compared" may assume the printed pin is close to the standard's. It differs in 684 of 700 rows, and the M_Re differs with it. Every number is still honest, because M_Re is right for the printed pin, so L08 holds. But the warning that is supposed to set the user's expectation now says something the repo disproves.
**Fix:** This changes printed text, so ask the human first. Options:
1. Reword to "The tool computes this pin; DIN 5480-2 tabulates a different measuring pin D_M for most sizes, and M_Re here is for this pin, not the standard's." Update the `endswith` pin in `test_shaft_calc.py:150`.
2. Leave the text until Phase 34 replaces the pin, and file a debt item that names the stale sentence.

Recommend 1. It is a one-string change, and it removes a false statement users read today.

## Info

### IN-10: The null-pin test's docstring still gives the pre-IN-07 reason for withholding `THEORETICAL_PIN`

**File:** `tests/test_shaft_calc.py:155-166`
**Issue:** The docstring of `test_no_pin_sentence_is_printed_when_no_pin_is_given` still says the sentence is withheld because "M_Re is for this pin" beside "M_Re and D_Re not given" would contradict itself. After 4ee29af, `THEORETICAL_PIN` contains no "M_Re" at all; `test_the_pin_sentence_says_...` now asserts that. The real reason is that the sentence describes a D_Re that is not printed. 4ee29af updated the matching source comment at `src/spur/shaft_calc.py:225` to "THEORETICAL_PIN would contradict ... 'M_Re and D_Re not given'", but not this docstring. The test body is correct, so only the stated reason is wrong.
**Fix:** Reword the last sentence of the docstring. Optionally, also assert the M_Re sentence is absent, which covers both gates:
```python
    """... null reading is injected: it goes live in Phase 34. A sentence about the printed
    D_Re beside "M_Re and D_Re not given" would contradict itself."""
    ...
    assert THEORETICAL_PIN not in d.warnings
    assert MEASURE_AT_NOMINAL_THICKNESS not in d.warnings
```

### IN-11: `H_FP_HOBBING`'s comment says only the hobbed-root sentence reads it; the `root_d` field description reads it too

**File:** `src/spur/din5480.py:34-35`
**Issue:** The new comment says: "Only shaft_calc's hobbed-root sentence reads it; the root diameter itself uses H_FP." `HOBBED_ROOT_DROP` (`src/spur/shaft_calc.py:70`) feeds two places:
- `hobbed_root_warning`.
- The `ShaftDimensions.root_d` field description (`src/spur/shaft_calc.py:112-117`), which goes into the published JSON schema.

The `shaft_calc.py` comment at lines 64-69 and 31-REVIEW-FIX.md both name both readers. The constants-block comment names one. Someone who edits `H_FP_HOBBING` and trusts this comment will not expect the schema text to change.
**Fix:**
```python
# h_fP/m of hobbing, same source as H_FP above (DIN 5480-1:2006, cl. 6, Table 3 and cl. 7.1).
# Read only through shaft_calc.HOBBED_ROOT_DROP (the hobbed-root warning and the root_d field
# description); the root diameter itself uses H_FP.
```

### IN-12: The basic-dimensions docstring claims more about the shift range than the test proves

**File:** `tests/test_din5480_anchors.py:101-102`
**Issue:** "W 30x2x14 and W 30x2x13 sit on the two edges of the shift range ... so the range is the standard's at m = 2." The test shows that the tool accepts both edge rows. It does not show that the standard prints nothing past them at m = 2; only the scratch comparison does ("Eleven Part 2 rows lie outside it", all at m 0.6-1.75). The range constants themselves are pinned in `test_shaft_params.py`, not here.
**Fix:** "... sit on the two edges of the shift range, -0.05 and +0.45, and are accepted, so both edges reach rows the standard prints."

### IN-13: 706 nominal rows but 700 M1 rows, and the amendment says "all"

**File:** `docs/architecture/decision_log.md:3187-3188`; same counts in the resolved debt item and the idea file
**Issue:** x*m, s1, da1 and df1 are compared on 705 of 706 rows. M1 is compared on "all 492 even-count and 208 odd-count rows", which is 700. The resolution says the one inconsistent row's M1 fits its d_B, so it is among the 700. Six rows have no M1 comparison and no stated reason, and "all" reads as all 706.
**Fix:** State the reason in the next amendment sentence and in the idea file (for example "6 rows print no M1" or "6 rows excluded because ..."), or write "on all 700 rows that print M1".

### IN-14: The anchor module docstring's first paragraph is now stale, and `tables` is never read

**File:** `tests/test_din5480_anchors.py:1-7,80-91,93-97,115-120`
**Issue:**
- The summary line says the values were approved "at the 31-05 checkpoint". The unedited line 6-7 says "No other value of the standard is in this repository", but the new paragraph adds 24 Part 2 values. "Each test below carries its part, clause and figure" does not fit the Part 2 tests, which carry tables.
- The `tables` column of `PART_2_ROWS` is read by neither test, nor by the ids or any failure message. Each test also takes five or six parameters it never uses.
- `_params` duplicates `_row_params` with an argument.
**Fix:** Reword the summary line and line 6-7 to cover both approvals ("... of the W 120 row and the four Part 2 rows below"). Use `tables` in the ids, or drop it in favour of the comment. Optionally, parametrize over the row tuple, unpack only the fields each test needs, and let `_row_params` take the designation.

### IN-15: The L47 amendment spans five paragraphs, and one of them opens like an original section

**File:** `docs/architecture/decision_log.md:3181-3196`
**Issue:** Every earlier amendment in the log (lines 1658, 1799, 1889, 2598, 3023-3060) is one paragraph opening `**Amendment (date, source).**`, and several amendments in a row each repeat that prefix. This one runs through bullets and four more paragraphs. Its fourth paragraph opens `**The guard**'s premise ...`, which looks like L47's own `**The guard** (D-12, D-20)` heading. A later reader, or a later amendment that cites "**The guard**", cannot tell original text from amendment without counting paragraphs.
**Fix:** Keep the text, but make the boundary visible. Either merge it into one paragraph, or split it into separate `**Amendment (2026-10-26, DIN 5480-2 anchors, guard).**`-style paragraphs, and drop the bold on "The guard" in the body.

### IN-16: Resolving the anchor item drops the gauge-series bullet and leaves REQ-shaft-basic-dims "can close" untracked

**File:** `docs/tech_debt/resolved/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md` (Resolution), `docs/architecture/decision_log.md:3190`
**Issue:**
- The item's second next-step bullet is "the clause source of D_Re / M_Re ... and any gauge pin series". The resolution covers the clause, still unread and now tracked only as the `measure_over_pins` ASSUMPTION marker. It never mentions the gauge series. `PIN_DECIMALS` keeps its "no series in the copy" ASSUMPTION, and Part 2's D_M values (2.75, 4.0, 5.0) are the first evidence for or against a series.
- The amendment says "REQ-shaft-basic-dims can close", but `.planning/REQUIREMENTS.md:60,164` still reads `[ ]` / Pending, and no file records the step.

Both residues of a `must` item now live only in prose.
**Fix:** Add a fifth resolution bullet, "Gauge series: Part 2 tabulates D_M per row; `PIN_DECIMALS` keeps its marker until Phase 34 takes the tabulated pin." Close REQ-shaft-basic-dims at ship, or note in STATE.md who closes it.

### IN-17: The code that the new form-diameter debt item is about does not point to it

**File:** `src/spur/din5480.py:171-183` (`form_diameter` docstring), `src/spur/shaft_calc.py:30-36` (`GUARD_MARGIN_FACTOR` comment)
**Issue:** `X_MIN`/`X_MAX` cite their debt file in place (`din5480.py:37-39`). `form_diameter` and the margin comment still read as written before Part 2 ("no DIN 5480 row proves this construction yet"; the margin "costs nothing until Phase 34"). They do not mention that the construction now sits above Part 2's d_Ff1 maximum on 470 rows. Whoever makes the guard live in Phase 34 edits these lines first.
**Fix:** Append one line to each: "Above DIN 5480-2's d_Ff1 maximum on most rows: docs/tech_debt/active/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md."

---

_Reviewed: 2026-10-26_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
