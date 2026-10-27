---
phase: 31-shaft-maths-parameters-and-designation
reviewed: 2026-10-26T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - src/spur/din5480.py
  - src/spur/shaft_calc.py
  - tests/test_din5480_anchors.py
  - tests/test_shaft_calc.py
  - bench/RESULTS.md
  - docs/architecture/decision_log.md
  - docs/tech_debt/resolved/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md
  - docs/ideas/2026-10-26-print-odd-tooth-count-measure-over-pins.md
findings:
  critical: 0
  warning: 0
  info: 5
  total: 5
status: issues_found
---

# Phase 31: Code Review Report (re-review of the WR-07..WR-11 and IN-10..IN-17 fixes)

**Reviewed:** 2026-10-26
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Scope: diff `0972c10..HEAD` (ee75aae, 3bedcc7, 8c77302, 195e38c, c4fc1ac) in the eight listed files. I also read the eight `investigation/31-part2-red-*.log` files and the form-diameter debt item as evidence.

**Tests:** `.venv/bin/python -m pytest tests/test_din5480_anchors.py tests/test_shaft_calc.py tests/test_din5480.py tests/test_shaft_params.py -q` gave `1018 passed in 2.21s`. I did not run `make verify`.

**WR-08 spot-check:** I ran two mutations in a scratch copy of `src/` and `tests/` (with `PYTHONPATH` pointed at the copy; I confirmed `spur.__file__` resolved there):
- Baseline: `8 passed, 3 deselected`.
- tip-only (`return reference_d - 0.21 * m`): `4 failed, 4 passed`. All four rows go red at `:113`, starting with `assert 24.738 == 24.75 ± 0.005`. This matches `31-part2-red-tip-only.log` and the RESULTS row.
- odd-gate (`if p.teeth % 2:` changed to `if False:`): `2 failed, 6 passed`, at `:137`, `assert 28.688 is None` and `assert 35.299 is None`. This matches the log.
- After the restore: `8 passed`. `diff -r` of the copy's `src` against the repo differs only in `.pyc` files. The repo's `git status --porcelain` is empty, and no mutation string is left in `src/` or `tests/`.

**WR-11 printed sentence: holds and does not overclaim.**
- Default shaft: D_M 2.75 against the printed pin 2.73, so "differs" is true for it. The other three approved rows differ too: 2.62/2.75, 3.83/4.0 and 4.72/5.0.
- "For most of them": 684 of 700 rows read differ. Even if every row the parser missed matched, 684 is still most of the total.
- "For the sizes it lists" does not say the current shaft is listed. That keeps the sentence true for an off-catalogue d_B.
- The "M_Re is for this pin" part sits in `MEASURE_AT_NOMINAL_THICKNESS`, under the M_Re gate. So option 1's tail is covered without breaking IN-07.
- L47 **The pin policy**'s "The warning says this is not the D_Re DIN 5480 tabulates" is true again.

**Fixes that hold (not re-listed):** WR-08, WR-09, WR-10, WR-11, IN-10, IN-11, IN-12, IN-13 (residue in IN-22), IN-14, IN-15, IN-16 and IN-17. WR-07 holds in every place the review named, with one pointer left behind (IN-21).
- WR-10: removing "unconfirmed" fixes the false claim. "(not given yet)" still gives no reason. That part was optional, so it is not re-listed.
- Decision log: both L47 amendments were rewritten in place, although the earlier review said to add sentences instead. This is acceptable: 87ca176 is not on `main`, the diff touches no sentence of L47's original body, and the two `**Amendment (...)**` labels now mark the boundary.

**T-31-13: holds.**
- Every DIN 5480 value in the diff is one of the 24 approved ones: the RESULTS rows' expected values, and "D_M 2.75" in the `test_shaft_calc.py` docstring.
- The other numbers are tool output (the logs' actuals, 2.73), derived statistics (470 of 705, 0.174*m, 684/700), or already committed (0.067*m, 0.202 mm).

**L05: holds.** No default, bound or constant changed in `src/`. The source diff is the two warning/description strings plus comments and docstrings.

**L08: holds.**
- No printed number moved. `derive_shaft` on the four rows still prints x*m 0.562/0.438/-0.1/0.9 and M_Re 27.999/None/33.685/None.
- The new sentence makes no numeric claim.

## Info

### IN-18: "A break that reaches it alone" is false for the shift and thickness runs

**File:** `docs/architecture/decision_log.md:3186`, `docs/tech_debt/resolved/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md:37`
**Issue:** Both texts say each value assertion "was seen red once against a break that reaches it alone".
- `31-part2-red-shift.log` (`ADDENDUM_FACTOR` 0.46) also reaches:
  - `:111` (W 30x2x13, whose `:108` passes at ±0.05);
  - `:134` (all four M1 rows);
  - `_params` (two ValidationErrors).
- `31-part2-red-thickness.log` (`tan` changed to `sin`) also reaches `:134` on all four rows.

What holds is narrower. Each assertion line is the first failure of its own test under one of the eight breaks. Six of the eight breaks (printed shift, tip, root, odd factor, oracle, odd gate) do reach one line only. The commit message of 8c77302 says it correctly: "each fails at its own line".
**Fix:** In the next amendment sentence, or in the resolved item, which is not append-only, write "each value assertion was seen red once as the first failure of its test". Do not edit 3186 if the branch is treated as published.

### IN-19: 8c77302's logs and RESULTS rows cite line numbers of a later commit, and no log carries revert proof

**File:** `bench/RESULTS.md:7005-7012`; `investigation/31-part2-red-*.log`
**Issue:**
- In 8c77302's own `tests/test_din5480_anchors.py`, the tip assertion is `:111`, `:113` is blank, the oracle is `:132`, and the file ends at `:134`.
- The logs committed in 8c77302 cite `:113` (tip), `:135` (oracle) and `:137` (odd null). Those lines exist only after c4fc1ac's docstring edits.
- So the red runs were taken against an uncommitted tree that already held c4fc1ac's docstring edits, which is a later commit's content. Checking out 8c77302 gives line citations that point at the wrong statements.
- The Revert column says "the file restored from a copy taken before the break; the 11 anchor tests pass after it". Every earlier row of that table records `git checkout -- …; git status --porcelain -- src tests empty`. The logs themselves still end at the red line, with no post-restore run.
- The table's preamble says every red ran with `PYTHONDONTWRITEBYTECODE=1` and the caches cleared. The root break (`0.55` changed to `0.60`) keeps the file size, the exact trap that preamble records. The new rows do not say they followed it.

My spot-check shows the HEAD citations are right, so no evidence is wrong at HEAD.
**Fix:** Append the post-restore pytest line (and `git status --porcelain -- src tests`) to each log, and say in the rows whether the bytecode rule was followed. Next time, run the reds after the last test-file edit is committed, so the commit that records them matches them.

### IN-20: `test_shaft_calc.py`'s module docstring still describes the anchor file before Part 2

**File:** `tests/test_shaft_calc.py:3-7`
**Issue:** The docstring says "the three values the 31-05 checkpoint approved are pinned in tests/test_din5480_anchors.py". That file now pins those three values plus four Part 2 rows. The docstring also lists M_Re as "still unconfirmed against the standard", but the M_Re formula now reproduces Part 2's M1 on all four rows at the tabulated pin. What stays unconfirmed is M_Re at the theoretical pin, which is the number this file pins. c4fc1ac updated the matching module docstring in the anchor file, but not this one. This file is in the diff (ee75aae, c4fc1ac).
**Fix:** "... the Part 1 values and the four DIN 5480-2 rows are pinned in tests/test_din5480_anchors.py. Unconfirmed are the theoretical pin D_Re, M_Re at that pin and the form diameter d_Ff, so those numbers here pin what the code does."

### IN-21: The idea's Related files still points to one odd anchor row (WR-07 residue)

**File:** `docs/ideas/2026-10-26-print-odd-tooth-count-measure-over-pins.md:8`
**Issue:** "`test_anchor_part_2_measure_over_pins_at_the_tabulated_pin`, the W 26x1.25x19 row". The body of the same file (line 15) now names both W 26x1.25x19 and W 30x2x13. Whoever removes the gate will look at the pointer first.
**Fix:** "... the W 26x1.25x19 and W 30x2x13 rows".

### IN-22: The cause given for the 706/700 gap ("misses a few rows at page breaks") has no evidence in the repo

**File:** `docs/architecture/decision_log.md:3188`; `docs/tech_debt/resolved/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md:37`; `docs/ideas/2026-10-26-print-odd-tooth-count-measure-over-pins.md:12`
**Issue:** The IN-13 fix explains the gap as a parser artifact at page breaks, in both tables. No log, scratch output or note in `.planning/` or `docs/` records which rows were missed or where. The only other mention is 31-REVIEW-FIX.md, which restates the claim. The scratch comparison is not committed. "A few" in both tables also means 706 is not the table's true row count, and the text does not say how many rows were unchecked. CLAUDE.md asks that a claim cite evidence or be marked `ASSUMPTION:`. This one is now written into the append-only log.
**Fix:** Write the parser's missed row count (or the page numbers) into the resolved item, which is still editable. Or mark the cause there as an assumption: "ASSUMPTION: the 6-row gap is parser loss at page breaks; not itemised." Leave line 3188 alone.

---

_Reviewed: 2026-10-26_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
