# The tooling and the phase 34 plans expect 24 rows in Table 7's tolerance table; the printed page has 30

Severity: must
Status: resolved
Date: 2026-10-30
Resolved in: 072ddd2 fix(34-14): Table 7's tolerance table has 30 rows; the completeness check says so
Source: 34-12 (Table 7 read A): the 600 ppi crops of page 24 end on a 30th row, and the 8 tolerance classes by 9 columns of the diagonals reach exactly 30 rows (3 rows per class step, 1 row per column). 34-RESEARCH "Table structure" says 24.
Related files:
- scripts/din5480_tables_tool.py:47 (`EXPECTED_COUNTS["tolerance_rows"]`)
- tests/test_din5480_tables_tool.py:103 (`test_the_expected_counts_are_the_standards_shape`)
- .planning/phases/34-fit-tables-and-tolerance-window/34-13-PLAN.md and 34-14-PLAN.md (the "24 True" / "24 rows" checks)
- .planning/phases/34-fit-tables-and-tolerance-window/34-RESEARCH.md ("Table structure", block 4)

## Context
`make tables.check --complete` and `make tables.assemble` compare a table file with `EXPECTED_COUNTS`, which holds 24 tolerance rows. Read A holds 30 rows as printed, passes `make tables.check`, and is refused by `--complete` on that one count (the absent sizes and modules aside). Read B will meet the same page. Read A was not trimmed to 24 (L08, D-05).

## Why it matters
`tables.assemble` refuses the union while the constant says 24, so 34-14 cannot write the table file from two correct reads. The refusal is loud, not silent.

## Next step
At 34-14, before assembling: confirm the 30 against read B, change the constant to 30, the test at line 103, and the "24" checks in the 34-13 and 34-14 plans, and fix the RESEARCH sentence; then flip this item to resolved.

## Resolution
The human authorized 30 at 34-14 (2026-10-30) on the evidence of both reads: read A (34-12) and read B (34-13) each counted 30 rows on page 24, all 30 satisfy T_G = T_act + T_eff, and 8 classes stepping 3 rows plus the column diagonals reach row 30. `EXPECTED_COUNTS["tolerance_rows"]` and `test_the_expected_counts_are_the_standards_shape` now say 30. The 34-RESEARCH sentence and the 34-13 plan's "24" checks are history and stay as written; 34-14's acceptance reads 30.
